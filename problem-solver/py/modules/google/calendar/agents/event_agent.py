from abc import abstractmethod

from sc_client.models import ScAddr
from sc_kpm import ScKeynodes

from modules.google.calendar.models import EventBase
from modules.google.integration_agent import IntegrationAgent


class CalendarAgent(IntegrationAgent):
    def __init__(self, action: str):
        super().__init__(action)
        self.calendar_id = "primary"
        self.rrel_event_summary = ScKeynodes.get("rrel_event_summary")
        self.rrel_start_time = ScKeynodes.get("rrel_start_time")
        self.rrel_end_time = ScKeynodes.get("rrel_end_time")

    @abstractmethod
    def get_event(self, message_addr: ScAddr) -> EventBase:
        pass
