from datetime import datetime, timedelta

from pydantic import BaseModel, model_validator


class CalendarDateTime(BaseModel):
    dateTime: str | None = None  # iso format
    timeZone: str = "Europe/Moscow"


class EventBase(BaseModel):
    id: str | None = None
    summary: str

    class Config:
        extra = "ignore"


class Event(EventBase):
    start: CalendarDateTime
    end: CalendarDateTime | None = None

    # set end_time = start_time + 1 hour if end_time is none
    @model_validator(mode="after")
    def set_end_time(self) -> "Event":
        if self.end is None:
            end_time: datetime = datetime.fromisoformat(self.start.dateTime)
            +timedelta(hours=1)
            iso_end_time: str = datetime.isoformat(end_time)
            self.end = CalendarDateTime(dateTime=iso_end_time)
        return self


class UpdateEvent(EventBase):
    summary: str | None = None
    start: CalendarDateTime | None = None
    end: CalendarDateTime | None = None
