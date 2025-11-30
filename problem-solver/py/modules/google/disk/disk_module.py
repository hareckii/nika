from sc_kpm import ScModule

from modules.google.disk.agents import (
    IndexingAgent
)


class GoogleDiskModule(ScModule):
    def __init__(self):
        super().__init__(
            IndexingAgent(),
        )
