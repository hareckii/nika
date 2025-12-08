import logging

from auth.agents.token.create_tokens import CreateTokensAgent
from auth.models import OauthClient
from modules.yandex.yandex_auth.services.yandex_oauth_token_service import YandexOauthTokenService
from yandex_secrets_env import YANDEX_CLIENT_ID, YANDEX_CLIENT_SECRET


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(message)s",
    datefmt="[%d-%b-%y %H:%M:%S]",
)


class YandexCreateTokensAgent(CreateTokensAgent):
    def __init__(self):
        super().__init__("action_create_yandex_tokens")

    @property
    def service(self) -> YandexOauthTokenService:
        client = OauthClient(
            secret=YANDEX_CLIENT_SECRET,
            id=YANDEX_CLIENT_ID,
            )
        return YandexOauthTokenService(client)
