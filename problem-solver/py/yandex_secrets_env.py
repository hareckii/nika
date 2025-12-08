from os import getenv

from dotenv import load_dotenv


load_dotenv()

YANDEX_CLIENT_ID = getenv("YANDEX_CLIENT_ID")
YANDEX_CLIENT_SECRET = getenv("YANDEX_CLIENT_SECRET")

GMAIL_PASS = getenv("GMAIL_PASSWORD")

CRYPTO_KEY = getenv("CRYPTO_KEY")
