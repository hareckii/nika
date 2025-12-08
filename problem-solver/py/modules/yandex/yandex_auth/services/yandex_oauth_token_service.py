import requests
from auth.models import OauthClient
from auth.services import OauthTokenService


TOKEN_URL = "https://oauth.yandex.ru/token"


class YandexOauthTokenService(OauthTokenService):
    def __init__(self, client: OauthClient):
        super().__init__(client, TOKEN_URL)

    def get_tokens(self, code: str) -> dict[str, str]:
        response = requests.post(
            url=self.token_url,
            data={
                "client_id": self.client.id,
                "client_secret": self.client.secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": "http://localhost:3033/auth/yandex/callback",
            },
            timeout=30,
        )
        response.raise_for_status()
        res = response.json()
        return {
            "access_token": res["access_token"],
            "refresh_token": res.get("refresh_token"),
        }

    def is_token_valid(self, token: str) -> bool:
        response = requests.get(
            "https://login.yandex.ru/info",
            headers={"Authorization": f"OAuth {token}"},
            timeout=30,
        )
        return response.status_code == 200

    def get_new_token(self, refresh_token: str) -> str:
        payload = {
            "client_id": self.client.id,
            "client_secret": self.client.secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }
        response = requests.post(
            self.token_url,
            data=payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=30,
        )
        response.raise_for_status()
        token_data = response.json()
        return token_data["access_token"]
