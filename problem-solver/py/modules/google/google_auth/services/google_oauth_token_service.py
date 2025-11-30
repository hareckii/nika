import requests

from auth.models import OauthClient
from auth.services import OauthTokenService


TOKEN_URL = "https://oauth2.googleapis.com/token"


class GoogleOauthTokenService(OauthTokenService):
    def __init__(self, client: OauthClient):
        super().__init__(client, TOKEN_URL)

    def get_tokens(self, code) -> dict[str, str]:
        response = requests.post(
            url=self.token_url,
            data={
                "client_id": self.client.id,
                "client_secret": self.client.secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": "http://localhost:3033",
            },
        )
        response.raise_for_status()
        res = response.json()
        return {
            'access_token': res["access_token"],
            'refresh_token': res["refresh_token"],
        }

    def is_token_valid(self, token: str):
        response = requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {token}"},
        )

        if response.status_code == 200:
            return True
        return False

    def get_new_token(
        self,
        refresh_token: str,
        ) -> str:
        payload = {
            "client_id": self.client.id,
            "client_secret": self.client.secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }

        response = requests.post(
            self.token_url,
            data=payload,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
            },
            timeout=30,
        )

        if response.status_code == 200:
            token_data = response.json()
            return token_data["access_token"]
