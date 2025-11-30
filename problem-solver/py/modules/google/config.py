from auth.models import OauthClient
from secrets_env import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET


client = OauthClient(
    id=GOOGLE_CLIENT_ID,
    secret=GOOGLE_CLIENT_SECRET,
)
