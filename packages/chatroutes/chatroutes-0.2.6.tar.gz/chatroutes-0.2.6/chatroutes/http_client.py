import time
from typing import Any, Dict, Optional
import requests
from .exceptions import (
    ChatRoutesError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    NotFoundError,
    ServerError,
    NetworkError
)


class HttpClient:
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.chatroutes.com/api/v1",
        timeout: int = 30,
        retry_attempts: int = 3,
        retry_delay: float = 1.0
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        self.session = requests.Session()
        self._set_default_headers()

    def _set_default_headers(self):
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Authorization': f'ApiKey {self.api_key}'
        })

    def _handle_error_response(self, status_code: int, response_data: Dict[str, Any]) -> ChatRoutesError:
        message = response_data.get('message') or response_data.get('error', 'An error occurred')
        details = response_data.get('details')

        if status_code == 400:
            return ValidationError(message, details)
        elif status_code == 401:
            return AuthenticationError(message, details)
        elif status_code == 404:
            return NotFoundError(message, details)
        elif status_code == 429:
            retry_after = response_data.get('retryAfter')
            return RateLimitError(message, retry_after, details)
        elif status_code >= 500:
            return ServerError(message, details)
        else:
            return ChatRoutesError(message, status_code, response_data.get('error'), details)

    def request(
        self,
        method: str,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        skip_auth: bool = False
    ) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        request_headers = self.session.headers.copy()

        if headers:
            request_headers.update(headers)

        if skip_auth:
            request_headers.pop('Authorization', None)

        last_error = None

        for attempt in range(self.retry_attempts + 1):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    json=data if data else None,
                    params=params,
                    headers=request_headers,
                    timeout=self.timeout
                )

                try:
                    response_data = response.json()
                except requests.exceptions.JSONDecodeError:
                    response_data = {'error': 'Invalid JSON response'}

                if not response.ok:
                    error = self._handle_error_response(response.status_code, response_data)

                    if response.status_code < 500:
                        raise error

                    last_error = error
                    if attempt < self.retry_attempts:
                        delay = self.retry_delay * (2 ** attempt)
                        time.sleep(delay)
                        continue
                    raise error

                return response_data

            except requests.exceptions.RequestException as e:
                last_error = NetworkError(f"Request failed: {str(e)}", {'error': str(e)})

                if attempt < self.retry_attempts:
                    delay = self.retry_delay * (2 ** attempt)
                    time.sleep(delay)
                    continue

                raise last_error

        if last_error:
            raise last_error

        raise NetworkError("Request failed after retries")

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self.request('GET', path, params=params)

    def post(
        self,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        skip_auth: bool = False
    ) -> Dict[str, Any]:
        return self.request('POST', path, data=data, headers=headers, skip_auth=skip_auth)

    def patch(self, path: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self.request('PATCH', path, data=data)

    def delete(self, path: str) -> Dict[str, Any]:
        return self.request('DELETE', path)

    def stream(self, path: str, data: Dict[str, Any], on_chunk):
        url = f"{self.base_url}{path}"
        headers = self.session.headers.copy()
        headers['Accept'] = 'text/event-stream'

        try:
            response = self.session.post(
                url,
                json=data,
                headers=headers,
                stream=True,
                timeout=self.timeout
            )

            if not response.ok:
                try:
                    error_data = response.json()
                except requests.exceptions.JSONDecodeError:
                    error_data = {'error': 'Invalid JSON response'}
                raise self._handle_error_response(response.status_code, error_data)

            complete_message = None

            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith('data: '):
                        data_str = decoded_line[6:]
                        if data_str == '[DONE]':
                            return complete_message

                        try:
                            import json
                            chunk_data = json.loads(data_str)

                            if chunk_data.get('type') == 'complete':
                                complete_message = chunk_data.get('message')

                            on_chunk(chunk_data)
                        except json.JSONDecodeError:
                            pass

            return complete_message

        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Stream request failed: {str(e)}", {'error': str(e)})
