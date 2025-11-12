from datetime import datetime
import logging

import requests
from sc_client.models import ScAddr
from sc_kpm import ScResult
from sc_kpm.utils import (
    get_link_content_data,
    search_element_by_role_relation,
)
from sc_kpm.utils.action_utils import (
    finish_action_with_status,
    generate_action_result,
    get_action_arguments,
)

from modules.google_integrations.calendar.models import CalendarDateTime, Event
from modules.google_integrations.calendar.event_agent import EventAgent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(message)s",
    datefmt="[%d-%b-%y %H:%M:%S]",
)


class AddEventAgent(EventAgent):
    def __init__(self):
        super().__init__("action_add_calendar_event")
        
        self.logger.info("Found all necessary rrels")
        
        

    def on_event(
        self, event_element: ScAddr, event_edge: ScAddr, action_element: ScAddr
    ) -> ScResult:
        try:
            result = self.run(action_element)
            is_successful = result == ScResult.OK
            finish_action_with_status(action_element, is_successful)
            self.logger.info(
                "Finished %s", "successfully" if is_successful else "unsuccessfully"
            )
            return result
        except Exception as e:
            self.logger.error(f"End with error: {e}")

    def run(self, action_node: ScAddr) -> ScResult:
        self.logger.info("Started")
        message_addr, author_node = get_action_arguments(action_node, 2)
        self.logger.info(f"{message_addr=}, {author_node=}")
        access_token = self.get_authenticated_token(author_node)
        if not access_token:
            self.logger.error("Do not get access token")
            return ScResult.ERROR

        event = self.get_event_params(message_addr)

        if event is None:
            return ScResult.ERROR

        response = self.add_event_in_calendar(access_token, event)
        
        if not response:
            self.logger.info("Event wasn't generated in Google Calendar")
            return ScResult.ERROR

        summary_addr = search_element_by_role_relation(
            message_addr, self.rrel_event_summary
            )
        generate_action_result(action_node, summary_addr)
        return ScResult.OK

    def get_event_params(
        self,
        message_addr: ScAddr,
    ) -> Event:
        # search link addresses
        summary_link = search_element_by_role_relation(
            message_addr, self.rrel_event_summary
            )
        start_time_link = search_element_by_role_relation(
            message_addr, self.rrel_start_time
            )
        end_time_link = search_element_by_role_relation(
            message_addr, self.rrel_end_time
            )
        self.logger.info("Found rrel nodes")
        
        # search links content
        summary = get_link_content_data(summary_link)
        iso_start_time: str = get_link_content_data(start_time_link)
        
        event = Event(
            summary=summary, 
            start=CalendarDateTime(dateTime=iso_start_time)
        )
        
        if end_time_link:
            iso_end_time: str = get_link_content_data(end_time_link)
            
            if (datetime.fromisoformat(iso_start_time) 
                > datetime.fromisoformat(iso_end_time)):
                self.logger.info("Invalid end date detected")
                return None
            event.end = CalendarDateTime(dateTime=iso_end_time)
        return event

    def add_event_in_calendar(
        self,
        access_token: str,
        event: Event
    ) -> bool:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        }
        try:
            response = requests.post(
                "https://www.googleapis.com/calendar/v3/calendars/"
                f"{self.calendar_id}/events",
                headers=headers,
                json=event.model_dump(),
            )
            if response.status_code == 200:
                return True
            else:
                return False
        except requests.exceptions.ConnectionError:
            self.logger.info("Finished with connection error")
            return False

    
