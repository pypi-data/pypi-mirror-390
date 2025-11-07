from typing import TypedDict, List, Optional, Literal


class BranchPoint(TypedDict):
    start: int
    end: int


class BranchSuggestion(TypedDict):
    id: str
    title: str
    description: str
    triggerText: str
    branchPoint: BranchPoint
    confidence: float
    reasoning: str
    estimatedDivergence: Literal["low", "medium", "high"]


class SuggestionMetadata(TypedDict):
    detectionMethod: Literal["pattern", "hybrid", "llm"]
    totalBranchPointsFound: int
    modelUsed: Optional[str]


class SuggestBranchesRequest(TypedDict, total=False):
    text: str
    suggestionsCount: int
    hybridDetection: bool
    threshold: float
    llmModel: Optional[str]
    llmProvider: Optional[str]
    llmApiKey: Optional[str]


class SuggestBranchesResponse(TypedDict):
    suggestions: List[BranchSuggestion]
    metadata: SuggestionMetadata


class HealthResponse(TypedDict):
    status: str
    version: str
    service: str
