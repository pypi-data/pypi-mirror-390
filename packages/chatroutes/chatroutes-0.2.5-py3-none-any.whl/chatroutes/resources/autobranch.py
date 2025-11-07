from typing import TYPE_CHECKING, Optional
from ..types.autobranch import (
    SuggestBranchesRequest,
    SuggestBranchesResponse,
    HealthResponse
)

if TYPE_CHECKING:
    from ..client import ChatRoutes


class AutoBranchResource:
    def __init__(self, client: 'ChatRoutes', autobranch_base_url: Optional[str] = None):
        self._client = client
        self._base_url = autobranch_base_url or f"{client.base_url}/autobranch"

    def suggest_branches(
        self,
        text: str,
        suggestions_count: int = 3,
        hybrid_detection: bool = False,
        threshold: float = 0.7,
        llm_model: Optional[str] = None,
        llm_provider: Optional[str] = None,
        llm_api_key: Optional[str] = None
    ) -> SuggestBranchesResponse:
        data: SuggestBranchesRequest = {
            'text': text,
            'suggestionsCount': suggestions_count,
            'hybridDetection': hybrid_detection,
            'threshold': threshold
        }

        if llm_model:
            data['llmModel'] = llm_model
        if llm_provider:
            data['llmProvider'] = llm_provider
        if llm_api_key:
            data['llmApiKey'] = llm_api_key

        import requests
        try:
            response = requests.post(
                f"{self._base_url}/suggest-branches",
                json=data,
                headers=self._client._get_headers(),
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            if 'data' in result:
                return result['data']
            return result
        except requests.exceptions.RequestException as e:
            raise Exception(f"AutoBranch request failed: {str(e)}")

    def analyze_text(
        self,
        text: str,
        suggestions_count: int = 3,
        hybrid_detection: bool = False,
        threshold: float = 0.7,
        llm_model: Optional[str] = None
    ) -> SuggestBranchesResponse:
        return self.suggest_branches(
            text=text,
            suggestions_count=suggestions_count,
            hybrid_detection=hybrid_detection,
            threshold=threshold,
            llm_model=llm_model
        )

    def health(self) -> HealthResponse:
        import requests
        try:
            response = requests.get(
                f"{self._base_url}/health",
                timeout=5
            )
            response.raise_for_status()
            result = response.json()
            if 'data' in result:
                return result['data']
            return result
        except requests.exceptions.RequestException as e:
            raise Exception(f"AutoBranch health check failed: {str(e)}")
