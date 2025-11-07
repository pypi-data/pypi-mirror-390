from typing import TYPE_CHECKING, List, Optional
from ..types import Checkpoint, CheckpointCreateRequest

if TYPE_CHECKING:
    from ..client import ChatRoutes


class CheckpointsResource:
    def __init__(self, client: 'ChatRoutes'):
        self._client = client

    def list(self, conversation_id: str, branch_id: Optional[str] = None) -> List[Checkpoint]:
        params = {}
        if branch_id:
            params['branchId'] = branch_id

        response = self._client._http.get(
            f'/conversations/{conversation_id}/checkpoints',
            params=params
        )

        if not response.get('success') or 'data' not in response:
            raise Exception(response.get('message', 'Failed to list checkpoints'))

        return response['data']['checkpoints']

    def create(self, conversation_id: str, branch_id: str, anchor_message_id: str) -> Checkpoint:
        data: CheckpointCreateRequest = {
            'branchId': branch_id,
            'anchorMessageId': anchor_message_id
        }

        response = self._client._http.post(
            f'/conversations/{conversation_id}/checkpoints',
            data
        )

        if not response.get('success') or 'data' not in response:
            raise Exception(response.get('message', 'Failed to create checkpoint'))

        return response['data']['checkpoint']

    def delete(self, checkpoint_id: str) -> None:
        response = self._client._http.delete(f'/checkpoints/{checkpoint_id}')

        if not response.get('success'):
            raise Exception(response.get('message', 'Failed to delete checkpoint'))

    def recreate(self, checkpoint_id: str) -> Checkpoint:
        response = self._client._http.post(f'/checkpoints/{checkpoint_id}/recreate', {})

        if not response.get('success') or 'data' not in response:
            raise Exception(response.get('message', 'Failed to recreate checkpoint'))

        return response['data']['checkpoint']
