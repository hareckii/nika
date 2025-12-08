import logging

from auth.agents.user.create_author import CreateAuthorAgent
from modules.yandex.yandex_auth.services.yandex_oauth_user_service import YandexOauthUserService


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(message)s",
    datefmt="[%d-%b-%y %H:%M:%S]",
)


class CreateYandexAuthorAgent(CreateAuthorAgent):
    def __init__(self):
        super().__init__("action_create_yandex_author")

    @property
    def service(self) -> YandexOauthUserService:
        return YandexOauthUserService()

    @property
    def token_agent_action(self) -> str:
        return "action_create_yandex_tokens"
