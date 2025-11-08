from typing import TYPE_CHECKING, Optional, Dict, Any
from ..types import (
    Conversation,
    CreateConversationRequest,
    ListConversationsParams,
    PaginatedResponse,
    ConversationTree
)

if TYPE_CHECKING:
    from ..client import ChatRoutes


class ConversationsResource:
    def __init__(self, client: 'ChatRoutes'):
        self._client = client

    def create(self, data: CreateConversationRequest) -> Conversation:
        response = self._client._http.post('/conversations', data)
        return response.get('data', {}).get('conversation', response)

    def list(self, params: Optional[ListConversationsParams] = None) -> PaginatedResponse:
        response = self._client._http.get('/conversations', params=params or {})
        return {
            'data': response.get('conversations', []),
            'total': response.get('total', 0),
            'page': response.get('page', 1),
            'limit': response.get('limit', 10),
            'hasNext': response.get('hasNext', False)
        }

    def get(self, conversation_id: str) -> Conversation:
        response = self._client._http.get(f'/conversations/{conversation_id}')
        return response.get('data', {}).get('conversation', response)

    def update(self, conversation_id: str, data: Dict[str, Any]) -> Conversation:
        response = self._client._http.patch(f'/conversations/{conversation_id}', data)
        return response.get('data', {}).get('conversation', response)

    def delete(self, conversation_id: str) -> None:
        self._client._http.delete(f'/conversations/{conversation_id}')

    def get_tree(self, conversation_id: str) -> ConversationTree:
        response = self._client._http.get(f'/conversations/{conversation_id}/tree')
        return response.get('data', response)
