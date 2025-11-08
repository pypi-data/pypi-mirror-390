from typing import TYPE_CHECKING, List, Dict, Any
from ..types import (
    Branch,
    CreateBranchRequest,
    ForkConversationRequest,
    Message
)

if TYPE_CHECKING:
    from ..client import ChatRoutes


class BranchesResource:
    def __init__(self, client: 'ChatRoutes'):
        self._client = client

    def list(self, conversation_id: str) -> List[Branch]:
        response = self._client._http.get(f'/conversations/{conversation_id}/branches')
        return response.get('data', {}).get('branches', response.get('branches', []))

    def create(self, conversation_id: str, data: CreateBranchRequest) -> Branch:
        response = self._client._http.post(f'/conversations/{conversation_id}/branches', data)
        return response.get('data', {}).get('branch', response)

    def fork(self, conversation_id: str, data: ForkConversationRequest) -> Branch:
        response = self._client._http.post(f'/conversations/{conversation_id}/fork', data)
        return response.get('data', {}).get('branch', response)

    def update(self, conversation_id: str, branch_id: str, data: Dict[str, Any]) -> Branch:
        response = self._client._http.patch(
            f'/conversations/{conversation_id}/branches/{branch_id}',
            data
        )
        return response.get('data', {}).get('branch', response)

    def delete(self, conversation_id: str, branch_id: str) -> None:
        self._client._http.delete(f'/conversations/{conversation_id}/branches/{branch_id}')

    def get_messages(self, conversation_id: str, branch_id: str) -> List[Message]:
        response = self._client._http.get(
            f'/conversations/{conversation_id}/branches/{branch_id}/messages'
        )
        return response.get('data', {}).get('messages', response.get('messages', []))

    def send_message(self, conversation_id: str, branch_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        response = self._client._http.post(
            f'/conversations/{conversation_id}/branches/{branch_id}/messages',
            data
        )
        return response.get('data', response)

    def merge(self, conversation_id: str, branch_id: str) -> Branch:
        response = self._client._http.post(
            f'/conversations/{conversation_id}/branches/{branch_id}/merge',
            {}
        )
        return response.get('data', {}).get('branch', response)
