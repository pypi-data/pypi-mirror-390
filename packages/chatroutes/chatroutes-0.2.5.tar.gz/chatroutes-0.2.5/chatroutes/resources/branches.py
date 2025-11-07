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

        if not response.get('success') or 'data' not in response:
            raise Exception(response.get('message', 'Failed to list branches'))

        return response['data']['branches']

    def create(self, conversation_id: str, data: CreateBranchRequest) -> Branch:
        response = self._client._http.post(f'/conversations/{conversation_id}/branches', data)

        if not response.get('success') or 'data' not in response:
            raise Exception(response.get('message', 'Failed to create branch'))

        return response['data']['branch']

    def fork(self, conversation_id: str, data: ForkConversationRequest) -> Branch:
        response = self._client._http.post(f'/conversations/{conversation_id}/fork', data)

        if not response.get('success') or 'data' not in response:
            raise Exception(response.get('message', 'Failed to fork conversation'))

        return response['data']['branch']

    def update(self, conversation_id: str, branch_id: str, data: Dict[str, Any]) -> Branch:
        response = self._client._http.patch(
            f'/conversations/{conversation_id}/branches/{branch_id}',
            data
        )

        if not response.get('success') or 'data' not in response:
            raise Exception(response.get('message', 'Failed to update branch'))

        return response['data']['branch']

    def delete(self, conversation_id: str, branch_id: str) -> None:
        response = self._client._http.delete(f'/conversations/{conversation_id}/branches/{branch_id}')

        if not response.get('success'):
            raise Exception(response.get('message', 'Failed to delete branch'))

    def get_messages(self, conversation_id: str, branch_id: str) -> List[Message]:
        response = self._client._http.get(
            f'/conversations/{conversation_id}/branches/{branch_id}/messages'
        )

        if not response.get('success') or 'data' not in response:
            raise Exception(response.get('message', 'Failed to get branch messages'))

        return response['data']['messages']

    def send_message(self, conversation_id: str, branch_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        response = self._client._http.post(
            f'/conversations/{conversation_id}/branches/{branch_id}/messages',
            data
        )

        if not response.get('success') or 'data' not in response:
            raise Exception(response.get('message', 'Failed to send message to branch'))

        return response['data']

    def merge(self, conversation_id: str, branch_id: str) -> Branch:
        response = self._client._http.post(
            f'/conversations/{conversation_id}/branches/{branch_id}/merge',
            {}
        )

        if not response.get('success') or 'data' not in response:
            raise Exception(response.get('message', 'Failed to merge branch'))

        return response['data']['branch']
