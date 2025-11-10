from dataclasses import dataclass


@dataclass
class GoogleResponse:
    access_token: str
    refresh_token: str
    