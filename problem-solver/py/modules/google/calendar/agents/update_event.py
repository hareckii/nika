import logging
from datetime import datetime, timezone

import requests
from modules.google.calendar.agents.event_agent import EventAgent
from modules.google.calendar.models import CalendarDateTime, EventBase, UpdateEvent
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

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(message)s",
    datefmt="[%d-%b-%y %H:%M:%S]",
)


class UpdateEventAgent(EventAgent):
    def __init__(self):
        super().__init__("action_update_calendar_event")
        self.rrel_new_event_summary = ScKeynodes.get("rrel_new_event_summary")

    def on_event(
        self, event_element: ScAddr, event_edge: ScAddr, action_element: ScAddr
    ) -> ScResult:
        result = self.run(action_element)
        is_successful = result != ScResult.ERROR
        finish_action_with_status(action_element, is_successful)
        self.logger.info(
            "Finished %s", "successfully" if is_successful else "unsuccessfully"
        )
        return result

    def run(self, action_node: ScAddr) -> ScResult:
        try:
            self.logger.info("Started")
            message_addr, author_node = get_action_arguments(action_node, 2)
            access_token = self.get_authenticated_token(author_node)
            if not access_token:
                self.logger.error("Do not get access token")
                return ScResult.ERROR

            old_event = self.get_event(message_addr)
            new_event = self.get_new_event(message_addr)
            event_with_id = self.search_event(access_token, old_event)
            if event_with_id is None:
                self.logger.info("Event hasn't been found in Google Calendar")
                return ScResult.ERROR
            self.logger.info(f"Found event: {event_with_id.summary}")

            res = self.update_event(access_token, event_with_id, new_event)
            if res is None:
                self.logger.error("Do not update event!")
                return ScResult.ERROR
            else:
                self.logger.error(f"New event {res=}")
            # check other parameters

        except Exception as e:
            self.logger.info(f"Finished with an error {e}")
            return ScResult.ERROR

        summary_addr = search_element_by_role_relation(
            message_addr, self.rrel_event_summary
        )
        generate_action_result(action_node, summary_addr)
        return ScResult.OK

    def search_event(self, access_token: str, event: EventBase) -> EventBase | None:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        }
        params = {
            "q": event.summary,
            "maxResults": 1,
            "timeMin": datetime.now(timezone.utc).replace(tzinfo=None).isoformat()
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
            else:
                self.logger.info(
                    f"Search error: {response.status_code} - {response.text}"
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
        self.logger.info(f"{new_event=}")
        self.logger.info(f"{old_event=}")
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
            if new_event.end.dateTime is None:
                new_event.end = old_event.end
                
            if new_event.start.dateTime is None:
                new_event.start = old_event.start
                
            response = requests.patch(url, headers=headers, json=new_event.model_dump())

            if response.status_code == 200:
                return UpdateEvent(**response.json())
            else:
                self.logger.error(
                    f"Update error: {response.status_code} - {response.text}"
                )
                return None

        except requests.exceptions.ConnectionError:
            self.logger.error("Finished with connection error")
            return None
        except Exception as e:
            self.logger.error(f"Update failed with error: {e}")
            return None

    def get_event(self, message_addr: ScAddr) -> EventBase:
        summary_link = search_element_by_role_relation(
            message_addr, self.rrel_event_summary
        )
        self.logger.info("Find event summary link")

        summary = get_link_content_data(summary_link)
        event = EventBase(summary=summary)
        return event

    def get_new_event(self, message_addr: ScAddr) -> UpdateEvent:
        summary = None
        start_time = None
        end_time = None
        # find links
        new_summary_link = search_element_by_role_relation(
            message_addr, self.rrel_new_event_summary
        )
        start_time_link = search_element_by_role_relation(
            message_addr, self.rrel_start_time
        )
        end_time_link = search_element_by_role_relation(
            message_addr, self.rrel_end_time
        )
        # find link_content
        if new_summary_link:
            summary = get_link_content_data(new_summary_link)
        if start_time_link:
            start_time = get_link_content_data(start_time_link)
        if end_time_link:
            end_time = get_link_content_data(end_time_link)

        event = UpdateEvent(
            summary=summary,
            start=CalendarDateTime(dateTime=start_time if start_time else None),
            end=CalendarDateTime(dateTime=end_time if end_time else None),
        )

        return event
