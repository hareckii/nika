import logging

from datetime import UTC, datetime

import requests

from sc_client.models import ScAddr
from sc_kpm import ScKeynodes, ScResult
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
from modules.google.calendar.models import (
    CalendarDateTime,
    EventBase,
    UpdateEvent,
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(message)s",
    datefmt="[%d-%b-%y %H:%M:%S]",
)


class UpdateEventAgent(GoogleCalendarAgent):
    def __init__(self):
        super().__init__("action_update_calendar_event")
        self.rrel_new_event_summary = ScKeynodes.get(
            "rrel_new_event_summary",
        )

    def on_event(
        self,
        event_element: ScAddr,  # noqa: ARG002
        event_edge: ScAddr,  # noqa: ARG002
        action_element: ScAddr,
    ) -> ScResult:
        try:
            result = self.run(action_element)
            is_successful = result != ScResult.ERROR
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
        new_event = self.get_new_event(message_addr)
        old_event = self.search_event(token, event)
        if old_event is None:
            self.logger.info("Event hasn't been found in Google Calendar")
            return ScResult.ERROR
        self.logger.info(f"Found event: {old_event.summary}")

        res = self.update_event(
            token,
            old_event,
            new_event,
        )
        if res is None:
            self.logger.error("Do not update event!")
            return ScResult.ERROR
        self.logger.error("New event %s", res)
        # check other parameters

        summary_addr = search_element_by_role_relation(
            message_addr,
            self.rrel_event_summary,
        )
        generate_action_result(action_node, summary_addr)
        return ScResult.OK

    def search_event(
        self,
        access_token: str,
        event: EventBase,
    ) -> UpdateEvent | None:
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
                return UpdateEvent(**item)
            self.logger.info(
                f"Search error: {response.status_code} - {response.text}",
            )
            return None
        except requests.exceptions.ConnectionError:
            self.logger.info("Finished with connection error")
            return None

    def update_event(
        self,
        access_token: str,
        old_event: UpdateEvent,
        new_event: UpdateEvent,
    ):
        self.logger.info("NEW EVENT %s", new_event)
        self.logger.info("OLD EVENT %s", old_event)
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        url = (
            "https://www.googleapis.com/calendar/"
            f"v3/calendars/{self.calendar_id}"
            f"/events/{old_event.id}"
        )

        try:
            if new_event.summary is None:
                new_event.summary = old_event.summary

            if new_event.end.dateTime is None:
                new_event.end = old_event.end

            if new_event.start.dateTime is None:
                new_event.start = old_event.start

            response = requests.patch(
                url,
                headers=headers,
                json=new_event.model_dump(),
            )

            if response.status_code == 200:
                return UpdateEvent(**response.json())
            self.logger.error(
                f"Update error: {response.status_code} - {response.text}",
            )
            return None

        except requests.exceptions.ConnectionError:
            self.logger.error("Finished with connection error")
            return None
        except Exception as e:
            self.logger.error("Update failed with error: %s", e)
            return None

    def get_event(self, message_addr: ScAddr) -> EventBase:
        summary_link = search_element_by_role_relation(
            message_addr,
            self.rrel_event_summary,
        )
        self.logger.info("Find event summary link")

        summary = get_link_content_data(summary_link)
        event = EventBase(summary=summary)
        return event

    def get_new_event(self, message_addr: ScAddr) -> UpdateEvent:
        summary = None
        start: CalendarDateTime | None = None
        end: CalendarDateTime | None = None
        # find links
        new_summary_link = search_element_by_role_relation(
            message_addr,
            self.rrel_new_event_summary,
        )
        start_time_link = search_element_by_role_relation(
            message_addr,
            self.rrel_start_time,
        )
        end_time_link = search_element_by_role_relation(
            message_addr,
            self.rrel_end_time,
        )
        # find link_content
        if new_summary_link:
            summary = get_link_content_data(new_summary_link)
        if start_time_link:
            start_time = get_link_content_data(start_time_link)
            start = CalendarDateTime(dateTime=start_time)
        if end_time_link:
            end_time = get_link_content_data(end_time_link)
            end = CalendarDateTime(dateTime=end_time)

        event = UpdateEvent(
            summary=summary,
            start=start,
            end=end,
        )

        return event
