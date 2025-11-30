from sc_kpm import ScModule

from auth.agents import CreateContactAgent, FindContactAgent


class ContactModule(ScModule):
    def __init__(self):
        super().__init__(
            CreateContactAgent(),
            FindContactAgent(),
        )
