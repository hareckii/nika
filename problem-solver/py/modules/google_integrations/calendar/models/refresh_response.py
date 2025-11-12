from pydantic import BaseModel


class RefreshResponse(BaseModel):
    success: bool
    access_token: str | None
    error: str | None
    error_description: str | None
