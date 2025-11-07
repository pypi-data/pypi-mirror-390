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

        if not response.get('success') or 'data' not in response:
            raise Exception(response.get('message', 'Failed to create conversation'))

        return response['data']['conversation']

    def list(self, params: Optional[ListConversationsParams] = None) -> PaginatedResponse:
        response = self._client._http.get('/conversations', params=params or {})

        if 'conversations' not in response:
            raise Exception(response.get('error', 'Failed to list conversations'))

        return {
            'data': response['conversations'],
            'total': response['total'],
            'page': response['page'],
            'limit': response['limit'],
            'hasNext': response.get('hasNext', False)
        }

    def get(self, conversation_id: str) -> Conversation:
        response = self._client._http.get(f'/conversations/{conversation_id}')

        if not response.get('success') or 'data' not in response:
            raise Exception(response.get('message', 'Failed to get conversation'))

        return response['data']['conversation']

    def update(self, conversation_id: str, data: Dict[str, Any]) -> Conversation:
        response = self._client._http.patch(f'/conversations/{conversation_id}', data)

        if not response.get('success') or 'data' not in response:
            raise Exception(response.get('message', 'Failed to update conversation'))

        return response['data']['conversation']

    def delete(self, conversation_id: str) -> None:
        response = self._client._http.delete(f'/conversations/{conversation_id}')

        if not response.get('success'):
            raise Exception(response.get('message', 'Failed to delete conversation'))

    def get_tree(self, conversation_id: str) -> ConversationTree:
        response = self._client._http.get(f'/conversations/{conversation_id}/tree')

        if not response.get('success') or 'data' not in response:
            raise Exception(response.get('error', 'Failed to get conversation tree'))

        return response['data']
