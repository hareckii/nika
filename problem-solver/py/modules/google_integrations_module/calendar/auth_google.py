import json
import logging

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from sc_client.client import set_link_contents
from sc_client.models import ScAddr, ScLinkContent, ScLinkContentType
from sc_kpm import ScAgentClassic, ScKeynodes, ScResult
from sc_kpm.utils import get_link_content_data, search_element_by_non_role_relation
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


class GoogleAuthAgent(ScAgentClassic):
    def __init__(self):
        super().__init__("action_google_auth")

    def on_event(
        self, event_element: ScAddr, event_connector: ScAddr, action_element: ScAddr
    ) -> ScResult:
        self.logger.info("Started")
        concept_nika_user = get_action_arguments(action_element, 1)[0]
        nrel_google_access_token = ScKeynodes.get("nrel_google_access_token")
        # nrel_google_refresh_token = ScKeynodes.get("nrel_google_access_token")
        access_token_link = search_element_by_non_role_relation(
            concept_nika_user, nrel_google_access_token
        )

        if nrel_google_access_token and concept_nika_user:
            self.logger.info("Found necessary auth nodes")
            self.logger.info(f"{access_token_link=}")
            creds_dict = json.loads(get_link_content_data(access_token_link))
            creds = Credentials.from_authorized_user_info(creds_dict)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                self.logger.warning("Need to authorize user")
                finish_action_with_status(action_element, False)
                return ScResult.ERROR

            new_link_content = ScLinkContent(
                creds.to_json(), ScLinkContentType.STRING, access_token_link
            )
            set_link_contents(new_link_content)
        generate_action_result(action_element, (access_token_link))
        self.logger.info("Finished successfully!")
        finish_action_with_status(action_element, True)
        return ScResult.OK
