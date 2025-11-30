import logging

from datetime import datetime

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

from modules.google.calendar.agents.calendar_agent import (
    GoogleCalendarAgent,
)
from modules.google.calendar.models import CalendarDateTime, Event


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(message)s",
    datefmt="[%d-%b-%y %H:%M:%S]",
)


class AddEventAgent(GoogleCalendarAgent):
    def __init__(self):
        super().__init__("action_add_calendar_event")

        self.logger.info("Found all necessary rrels")

    def on_event(
        self,
        event_element: ScAddr,  # noqa: ARG002
        event_edge: ScAddr,  # noqa: ARG002
        action_element: ScAddr,
    ) -> ScResult:
        try:
            result = self.run(action_element)
            is_successful = result == ScResult.OK
            finish_action_with_status(action_element, is_successful)
            self.logger.info(
                "Finished %s",
                "successfully" if is_successful else "unsuccessfully",
            )
            return result
        except Exception as e:
            self.logger.error("%s", e)

    def run(self, action_node: ScAddr) -> ScResult:
        message_addr, self.author_node = get_action_arguments(
            action_node,
            2,
        )
        token = self.get_token()
        if token is None:
            self.logger.error("Did not get token")
            return ScResult.ERROR
        if not message_addr:
            self.logger.error("Did not have message address")
            return ScResult.ERROR

        event = self.get_event(message_addr)

        if event is None:
            self.logger.error("Did not get event")
            return ScResult.ERROR

        response = self.add_event_in_calendar(token, event)

        if not response:
            self.logger.info("Event wasn't generated in Google Calendar")
            return ScResult.ERROR

        summary_addr = search_element_by_role_relation(
            message_addr,
            self.rrel_event_summary,
        )
        generate_action_result(action_node, summary_addr)
        return ScResult.OK

    def get_event(
        self,
        message_addr: ScAddr,
    ) -> Event:
        # search link addresses
        summary_link = search_element_by_role_relation(
            message_addr,
            self.rrel_event_summary,
        )
        start_time_link = search_element_by_role_relation(
            message_addr,
            self.rrel_start_time,
        )
        end_time_link = search_element_by_role_relation(
            message_addr,
            self.rrel_end_time,
        )
        self.logger.info("Found rrel nodes")

        # search links content
        summary = get_link_content_data(summary_link)
        iso_start_time: str = get_link_content_data(start_time_link)

        event = Event(
            summary=summary,
            start=CalendarDateTime(dateTime=iso_start_time),
        )

        if end_time_link:
            iso_end_time: str = get_link_content_data(end_time_link)

            if datetime.fromisoformat(
                iso_start_time,
            ) > datetime.fromisoformat(
                iso_end_time,
            ):
                self.logger.info("Invalid end date detected")
                return None
            event.end = CalendarDateTime(dateTime=iso_end_time)
        return event

    def add_event_in_calendar(
        self,
        access_token: str,
        event: Event,
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
            return False
        except requests.exceptions.ConnectionError:
            self.logger.info("Finished with connection error")
            return False
