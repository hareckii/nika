import requests

from auth.models import User
from auth.services import OauthUserService


USER_URL = "https://login.yandex.ru/info"


class YandexOauthUserService(OauthUserService):
    def __init__(self):
        super().__init__(USER_URL)

    def get_user(self, token: str) -> User:
        headers = {
            "Authorization": f"OAuth {token}",
            "Accept": "application/json",
        }
        response = requests.get(
            self.user_url,
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()

        user_data = response.json()

        return User(
            name=user_data.get("real_name"),
            email=user_data.get("default_email") or "email_is_none@gmail.com",
        )
