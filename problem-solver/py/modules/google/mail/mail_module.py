from sc_kpm import ScModule

from modules.google.mail.agents import (
    MailAgent,
)


class GmailModule(ScModule):
    def __init__(self):
        super().__init__(
            MailAgent(),
        )
