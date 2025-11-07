from typing import TYPE_CHECKING, List, Optional, Callable
from ..types import (
    Message,
    SendMessageRequest,
    SendMessageResponse,
    StreamChunk
)

if TYPE_CHECKING:
    from ..client import ChatRoutes


class MessagesResource:
    def __init__(self, client: 'ChatRoutes'):
        self._client = client

    def send(self, conversation_id: str, data: SendMessageRequest) -> SendMessageResponse:
        response = self._client._http.post(f'/conversations/{conversation_id}/messages', data)

        if not response.get('success') or 'data' not in response:
            raise Exception(response.get('message', 'Failed to send message'))

        return response['data']

    def stream(
        self,
        conversation_id: str,
        data: SendMessageRequest,
        on_chunk: Callable[[StreamChunk], None],
        on_complete: Optional[Callable[[dict], None]] = None
    ) -> None:
        def handle_chunk(chunk: StreamChunk):
            on_chunk(chunk)

        complete_message = self._client._http.stream(
            f'/conversations/{conversation_id}/messages/stream',
            data,
            handle_chunk
        )

        if on_complete and complete_message:
            on_complete(complete_message)

    def list(self, conversation_id: str, branch_id: Optional[str] = None) -> List[Message]:
        params = {}
        if branch_id:
            params['branchId'] = branch_id

        response = self._client._http.get(f'/conversations/{conversation_id}/messages', params=params)

        if not response.get('success') or 'data' not in response:
            raise Exception(response.get('message', 'Failed to list messages'))

        return response['data']['messages']

    def update(self, message_id: str, content: str) -> Message:
        response = self._client._http.patch(f'/messages/{message_id}', {'content': content})

        if not response.get('success') or 'data' not in response:
            raise Exception(response.get('message', 'Failed to update message'))

        return response['data']['message']

    def delete(self, message_id: str) -> None:
        response = self._client._http.delete(f'/messages/{message_id}')

        if not response.get('success'):
            raise Exception(response.get('message', 'Failed to delete message'))
