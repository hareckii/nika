from sc_kpm import ScModule

from modules.google.auth.agents import (
    CheckGoogleTokenAgent,
    CreateContactAgent,
    CreateGoogleUser,
    FindContactAgent,
)


class GoogleAuthModule(ScModule):
    def __init__(self):
        super().__init__(
            CreateGoogleUser(),
            CreateContactAgent(),
            CheckGoogleTokenAgent(),
            FindContactAgent(),
        )
