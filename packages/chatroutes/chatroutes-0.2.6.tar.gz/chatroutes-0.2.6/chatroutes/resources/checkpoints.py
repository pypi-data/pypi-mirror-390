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
        return response.get('data', {}).get('checkpoints', response.get('checkpoints', []))

    def create(self, conversation_id: str, branch_id: str, anchor_message_id: str) -> Checkpoint:
        data: CheckpointCreateRequest = {
            'branchId': branch_id,
            'anchorMessageId': anchor_message_id
        }

        response = self._client._http.post(
            f'/conversations/{conversation_id}/checkpoints',
            data
        )
        return response.get('data', {}).get('checkpoint', response)

    def delete(self, checkpoint_id: str) -> None:
        self._client._http.delete(f'/checkpoints/{checkpoint_id}')

    def recreate(self, checkpoint_id: str) -> Checkpoint:
        response = self._client._http.post(f'/checkpoints/{checkpoint_id}/recreate', {})
        return response.get('data', {}).get('checkpoint', response)
