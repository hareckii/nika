from sc_kpm import ScModule

from modules.google.auth.agents import (
    CreateContactAgent,
    CreateGoogleUser,
)


class GoogleAuthModule(ScModule):
    def __init__(self):
        super().__init__(
            CreateGoogleUser(),
            CreateContactAgent(),
        )
