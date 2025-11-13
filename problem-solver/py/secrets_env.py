from __future__ import annotations

from os import getenv

from dotenv import load_dotenv


load_dotenv()

GOOGLE_CLIENT_ID = getenv("GOOGLE_CLIENT_ID")
GOOGLE_API_KEY = getenv("GOOGLE_API_KEY")
GOOGLE_CLIENT_SECRET = getenv("GOOGLE_CLIENT_SECRET")
