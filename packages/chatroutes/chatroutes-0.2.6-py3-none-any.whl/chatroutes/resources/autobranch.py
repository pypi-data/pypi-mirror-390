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

        response = self._client._http.post('/autobranch/suggest-branches', data)
        return response.get('data', response)

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
        response = self._client._http.get('/autobranch/health')
        return response.get('data', response)
