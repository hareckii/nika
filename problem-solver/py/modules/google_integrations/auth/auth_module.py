from sc_kpm import ScModule
from .create_user import CreateGoogleUser



class GoogleAuthModule(ScModule):
    def __init__(self):
        super().__init__(
            CreateGoogleUser(),
        )
