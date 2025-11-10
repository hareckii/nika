from sc_kpm import ScModule
from .add_event import AddEventAgent
from .auth_google import GoogleAuthAgent
from .delete_event import DeleteEventAgent
from .update_event import UpdateEventAgent

class GoogleCalendarModule(ScModule):
    def __init__(self):
        super().__init__(
            AddEventAgent(),
            GoogleAuthAgent(),
            DeleteEventAgent(),
            UpdateEventAgent()
            )
