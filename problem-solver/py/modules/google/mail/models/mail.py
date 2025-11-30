from pydantic import BaseModel

from auth.models import User


class Mail(BaseModel):
    sender: User
    receiver: User
    body: str
    subject: str | None = None
