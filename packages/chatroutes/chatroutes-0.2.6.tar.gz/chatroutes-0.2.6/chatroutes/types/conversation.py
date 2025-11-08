from typing import TypedDict, List, Optional, Literal, Any
from datetime import datetime


class MessageMetadata(TypedDict, total=False):
    model: str
    temperature: float
    maxTokens: int
    responseTime: float
    finishReason: str
    cost: float
    context_truncated: Optional[bool]
    checkpoint_used: Optional[bool]
    prompt_tokens: Optional[int]
    context_message_count: Optional[int]


class Message(TypedDict, total=False):
    id: str
    conversationId: str
    branchId: Optional[str]
    role: Literal['user', 'assistant', 'system']
    content: str
    tokenCount: Optional[int]
    createdAt: str
    metadata: Optional[MessageMetadata]


class Branch(TypedDict, total=False):
    id: str
    conversationId: str
    parentBranchId: Optional[str]
    forkPointMessageId: Optional[str]
    title: str
    contextMode: Optional[Literal['FULL', 'PARTIAL', 'MINIMAL']]
    isMain: bool
    isActive: bool
    createdAt: str
    updatedAt: Optional[str]
    messageCount: Optional[int]


class Conversation(TypedDict, total=False):
    id: str
    userId: str
    title: str
    createdAt: str
    updatedAt: str
    messages: Optional[List[Message]]
    branches: Optional[List[Branch]]


class CreateConversationRequest(TypedDict, total=False):
    title: str
    model: Optional[str]


class SendMessageRequest(TypedDict, total=False):
    content: str
    model: Optional[str]
    temperature: Optional[float]
    maxTokens: Optional[int]
    branchId: Optional[str]


class SendMessageResponse(TypedDict):
    message: Message
    usage: dict
    model: str


class CreateBranchRequest(TypedDict, total=False):
    title: str
    baseNodeId: Optional[str]
    description: Optional[str]
    contextMode: Optional[Literal['FULL', 'PARTIAL', 'MINIMAL']]


class ForkConversationRequest(TypedDict, total=False):
    forkPointMessageId: str
    title: str
    contextMode: Optional[Literal['FULL', 'PARTIAL', 'MINIMAL']]


class TreeNode(TypedDict, total=False):
    id: str
    content: str
    role: str
    children: List['TreeNode']
    branchInfo: Optional[dict]


class ConversationTreeMetadata(TypedDict):
    totalNodes: int
    totalBranches: int
    maxDepth: int


class ConversationTree(TypedDict):
    conversation: Conversation
    tree: TreeNode
    metadata: ConversationTreeMetadata


class ListConversationsParams(TypedDict, total=False):
    page: Optional[int]
    limit: Optional[int]
    filter: Optional[Literal['all', 'owned', 'shared']]


class PaginatedResponse(TypedDict):
    data: List[Any]
    total: int
    page: int
    limit: int
    hasNext: Optional[bool]


class StreamChunk(TypedDict, total=False):
    type: str
    content: Optional[str]
    model: Optional[str]
    message: Optional[dict]
    created: int
