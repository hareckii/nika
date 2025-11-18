import logging

import requests

from sc_client.client import set_link_contents
from sc_client.models import ScAddr, ScLinkContent, ScLinkContentType
from sc_kpm import ScAgentClassic, ScKeynodes, ScResult
from sc_kpm.utils import (
    get_link_content_data,
    search_element_by_non_role_relation,
)
from sc_kpm.utils.action_utils import (
    finish_action_with_status,
    generate_action_result,
    get_action_arguments,
)

from modules.google.calendar.models import RefreshResponse
from secrets_env import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET


TOKEN_URL = "https://oauth2.googleapis.com/token"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(message)s",
    datefmt="[%d-%b-%y %H:%M:%S]",
)


class CheckGoogleTokenAgent(ScAgentClassic):
    def __init__(self):
        super().__init__("action_google_auth")
        self.nrel_refresh_token = ScKeynodes.get("nrel_refresh_token")
        self.nrel_access_token = ScKeynodes.get("nrel_access_token")

    def on_event(
        self,
        event_element: ScAddr,  # noqa: ARG002
        event_connector: ScAddr,  # noqa: ARG002
        action_element: ScAddr,
    ) -> ScResult:
        if not (GOOGLE_CLIENT_SECRET and GOOGLE_CLIENT_SECRET):
            return ScResult.ERROR

        self.author_node = get_action_arguments(action_element, 1)[0]
        self.logger.error("%s", self.author_node)
        if not self.author_node.is_valid():
            return ScResult.ERROR

        access_token_link = search_element_by_non_role_relation(
            self.author_node,
            self.nrel_access_token,
        )
        refresh_token_link = search_element_by_non_role_relation(
            self.author_node,
            self.nrel_refresh_token,
        )

        if not (access_token_link and refresh_token_link):
            return ScResult.ERROR

        self.logger.info("Found necessary auth nodes")
        access_token = get_link_content_data(access_token_link)
        refresh_token = get_link_content_data(refresh_token_link)

        if not self.is_valid(access_token):
            response = self.refresh_access_token(refresh_token)
            if response.success is not True:
                self.logger.error(
                    f"Get {response.error}",
                    f"{response.error_description}",
                )
                return ScResult.ERROR
            new_access_token = response.access_token
            new_link_content = ScLinkContent(
                new_access_token,
                ScLinkContentType.STRING,
                access_token_link,
            )
            set_link_contents([new_link_content])

        generate_action_result(action_element, (access_token_link))
        self.logger.info("Finished successfully!")
        finish_action_with_status(action_element)

        return ScResult.OK

    def is_valid(self, access_token: str) -> bool:
        """
        Check is access_token valid
        """
        try:
            response = requests.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
            )

            if response.status_code == 200:
                return True
            return False

        except requests.exceptions.RequestException as e:
            self.logger.error("%s", e)
            return False

    def refresh_access_token(self, refresh_token: str) -> RefreshResponse:
        try:
            payload = {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
            }

            response = requests.post(
                TOKEN_URL,
                data=payload,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                timeout=30,
            )

            if response.status_code == 200:
                token_data = response.json()
                return RefreshResponse(
                    success=True,
                    access_token=token_data["access_token"],
                )
            error_data = response.json()
            return RefreshResponse(
                success=False,
                error=f"HTTP {response.status_code}",
                error_description=error_data.get(
                    "error_description",
                    "Unknown error",
                ),
            )

        except requests.exceptions.Timeout:
            return RefreshResponse(success=False, error="Request timeout")
        except requests.exceptions.RequestException as e:
            return RefreshResponse(
                success=False,
                error=f"Request failed: {e!s}",
            )
        except KeyError:
            return RefreshResponse(
                success=False,
                error="Invalid response format",
            )
