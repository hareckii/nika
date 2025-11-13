from sc_kpm import ScModule

from modules.google.calendar.agents import (
    AddEventAgent,
    CheckGoogleTokenAgent,
    DeleteEventAgent,
    UpdateEventAgent,
)


class GoogleCalendarModule(ScModule):
    def __init__(self):
        super().__init__(
            AddEventAgent(),
            CheckGoogleTokenAgent(),
            DeleteEventAgent(),
            UpdateEventAgent(),
        )
