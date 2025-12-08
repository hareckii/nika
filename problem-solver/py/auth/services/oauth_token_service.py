from abc import abstractmethod

from auth.models import OauthClient
from auth.services import OauthService


class OauthTokenService(OauthService):
    def __init__(self, client: OauthClient, token_url: str):
        self.client = client
        self.token_url = token_url

    @abstractmethod
    def get_tokens(self, code: str) -> dict[str, str]:
        pass

    @abstractmethod
    def is_token_valid(self, token: str) -> bool:
        pass

    @abstractmethod
    def get_new_token(self, refresh_token: str) -> str:
        pass
