import logging

from datetime import UTC, datetime

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

from modules.google.calendar.agents.event_agent import CalendarAgent
from modules.google.calendar.models import EventBase


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(message)s",
    datefmt="[%d-%b-%y %H:%M:%S]",
)


class DeleteEventAgent(CalendarAgent):
    def __init__(self):
        super().__init__("action_delete_calendar_event")

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
            self.logger.info("Finished with an error %s", e)
            return ScResult.ERROR

    def run(self, action_node: ScAddr) -> ScResult:
        self.logger.info("Started")
        message_addr, self.author_node = get_action_arguments(
            action_node,
            2,
        )
        author = self.get_author()
        if author is None:
            self.logger.error("Did not get author")
            return ScResult.ERROR
        if not message_addr:
            self.logger.error("Did not have message address")
            return ScResult.ERROR

        event = self.get_event(message_addr)

        if event is None:
            self.logger.error("Did not get event")
            return ScResult.ERROR

        event_with_id = self.search_event(author.access_token, event)
        if not event_with_id:
            self.logger.info("Did not find event in Google Calendar")
            return ScResult.UNKNOWN

        self.logger.info(f"Find event: {event_with_id.summary}")

        deletion_result = self.delete_event(
            author.access_token,
            event_with_id,
        )
        if deletion_result is not True:
            self.logger.info("Did not delete event in Google Calendar")
            return ScResult.ERROR

        self.logger.info("Delete event")

        summary_addr = search_element_by_role_relation(
            message_addr,
            self.rrel_event_summary,
        )
        generate_action_result(action_node, summary_addr)
        return ScResult.OK

    def search_event(self, access_token: str, event: EventBase):
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        }
        params = {
            "q": event.summary,
            "maxResults": 1,
            "timeMin": datetime.now(UTC).replace(tzinfo=None).isoformat()
            + "Z",
            "singleEvents": "true",
            "orderBy": "startTime",
        }
        url = (
            "https://www.googleapis.com/calendar/"
            f"v3/calendars/{self.calendar_id}/events"
        )
        try:
            response = requests.get(
                url,
                headers=headers,
                params=params,
            )
            if response.status_code == 200:
                item = response.json()["items"][0]
                return EventBase(**item)
            self.logger.info(
                f"Search error: {response.status_code} - {response.text}",
            )
            return None
        except requests.exceptions.ConnectionError:
            self.logger.info("Finished with connection error")
            return None

    def delete_event(self, access_token: str, event: EventBase) -> bool:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        }
        url = (
            f"https://www.googleapis.com/calendar/v3/"
            f"calendars/{self.calendar_id}/"
            f"events/{event.id}"
        )
        try:
            response = requests.delete(url, headers=headers)

            if response.status_code == 204:
                return True
            raise Exception(
                f"Deletion error: {response.status_code} - {response.text}",
            )
        except requests.exceptions.ConnectionError:
            self.logger.info("Finished with connection error")
            return False

    def get_event(self, message_addr: ScAddr) -> EventBase:
        summary_link = search_element_by_role_relation(
            message_addr,
            self.rrel_event_summary,
        )
        self.logger.info("Find event summary link")

        summary = get_link_content_data(summary_link)
        event = EventBase(summary=summary)
        return event
