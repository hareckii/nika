from sc_kpm import ScModule

from modules.google.google_auth.agents import (
    CheckGoogleTokenAgent,
    CreateGoogleAuthorAgent,
    GoogleCreateTokensAgent,
)


class GoogleAuthModule(ScModule):
    def __init__(self):
        super().__init__(
            CheckGoogleTokenAgent(),
            CreateGoogleAuthorAgent(),
            GoogleCreateTokensAgent(),
        )
