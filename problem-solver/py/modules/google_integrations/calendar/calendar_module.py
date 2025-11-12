from sc_kpm import ScModule

from .add_event import AddEventAgent
from .delete_event import DeleteEventAgent
from .check_token import CheckGoogleTokenAgent


class GoogleCalendarModule(ScModule):
    def __init__(self):
        super().__init__(
            AddEventAgent(),
            CheckGoogleTokenAgent(),
            DeleteEventAgent(),
            # UpdateEventAgent()
        )
