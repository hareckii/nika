from sc_kpm import ScModule

from modules.google.mail.agents import SendMessageAgent


class GoogleMailModule(ScModule):
    def __init__(self):
        super().__init__(
            SendMessageAgent(),
        )
