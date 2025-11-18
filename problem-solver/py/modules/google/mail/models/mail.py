from pydantic import BaseModel

from modules.google.auth.models import Author, User


class Mail(BaseModel):
    sender: Author
    receiver: User
    body: str
    subject: str | None = None
