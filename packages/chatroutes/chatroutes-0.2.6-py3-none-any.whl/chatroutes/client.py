from typing import Optional
from .http_client import HttpClient
from .resources import (
    ConversationsResource,
    MessagesResource,
    BranchesResource,
    CheckpointsResource,
    AutoBranchResource
)


class ChatRoutes:
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.chatroutes.com/api/v1",
        timeout: int = 30,
        retry_attempts: int = 3,
        retry_delay: float = 1.0,
        autobranch_base_url: Optional[str] = None
    ):
        self._http = HttpClient(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            retry_attempts=retry_attempts,
            retry_delay=retry_delay
        )

        self.conversations = ConversationsResource(self)
        self.messages = MessagesResource(self)
        self.branches = BranchesResource(self)
        self.checkpoints = CheckpointsResource(self)
        self.autobranch = AutoBranchResource(self, autobranch_base_url)

    @property
    def api_key(self) -> str:
        return self._http.api_key

    @property
    def base_url(self) -> str:
        return self._http.base_url

    def _get_headers(self) -> dict:
        return self._http.session.headers.copy()
