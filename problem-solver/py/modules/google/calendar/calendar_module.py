from sc_kpm import ScModule

from modules.google.calendar.agents import (
    AddEventAgent,
    DeleteEventAgent,
    UpdateEventAgent,
    CheckGoogleTokenAgent,
)


class GoogleCalendarModule(ScModule):
    def __init__(self):
        super().__init__(
            AddEventAgent(),
            CheckGoogleTokenAgent(),
            DeleteEventAgent(),
            UpdateEventAgent()
        )
