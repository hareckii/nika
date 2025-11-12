from datetime import datetime, timedelta

from pydantic import BaseModel, model_validator


class Event(BaseModel):
    summary: str
    start_time: datetime
    end_time: datetime | None = None

    # set end_time = start_time + 1 hour if end_time is none
    @model_validator(mode='after')
    def set_end_time(self) -> 'Event':
        if self.end_time is None:
            self.end_time = self.start_time + timedelta(hours=1)
        return self