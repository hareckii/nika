from sc_kpm import ScModule

from modules.google.auth.agents import CreateGoogleUser


class GoogleAuthModule(ScModule):
    def __init__(self):
        super().__init__(
            CreateGoogleUser(),
        )
