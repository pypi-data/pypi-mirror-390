from typing import TypedDict, List, Optional


class Checkpoint(TypedDict, total=False):
    id: str
    conversation_id: str
    branch_id: str
    anchor_message_id: str
    summary: str
    token_count: int
    created_at: str


class CheckpointCreateRequest(TypedDict, total=False):
    branchId: str
    anchorMessageId: str


class CheckpointListResponse(TypedDict):
    checkpoints: List[Checkpoint]
