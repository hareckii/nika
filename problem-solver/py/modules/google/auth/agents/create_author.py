import logging

import requests

from sc_client.client import generate_by_template
from sc_client.constants import sc_type
from sc_client.models import ScAddr, ScTemplate
from sc_kpm import ScAgentClassic, ScKeynodes, ScResult
from sc_kpm.utils import (
    generate_link,
    get_link_content_data,
)
from sc_kpm.utils.action_utils import (
    finish_action_with_status,
    get_action_arguments,
)

from modules.google.auth.models import Author
from secrets_env import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(message)s",
    datefmt="[%d-%b-%y %H:%M:%S]",
)


class CreateGoogleUser(ScAgentClassic):
    def __init__(self):
        super().__init__("action_create_google_user")
        self.nrel_name: ScAddr = ScKeynodes.resolve(
            "nrel_name", sc_type.CONST_NODE_NON_ROLE,
        )
        self.nrel_email: ScAddr = ScKeynodes.resolve(
            "nrel_email", sc_type.CONST_NODE_NON_ROLE,
        )
        self.nrel_access_token: ScAddr = ScKeynodes.resolve(
            "nrel_access_token", sc_type.CONST_NODE_NON_ROLE,
        )
        self.nrel_refresh_token: ScAddr = ScKeynodes.resolve(
            "nrel_refresh_token", sc_type.CONST_NODE_NON_ROLE,
        )
        self.nrel_google_session: ScAddr = ScKeynodes.resolve(
            "nrel_google_session", sc_type.CONST_NODE_NON_ROLE,
        )
        self.concept_user: ScAddr = ScKeynodes.resolve(
            "concept_user", sc_type.CONST_NODE_CLASS,
        )
        self.lang_en: ScAddr = ScKeynodes.resolve("lang_en", sc_type.CONST_NODE_CLASS)

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
        self.logger.info("Started!")
        args = get_action_arguments(action_node, 2)

        google_session_link = args[0]
        google_code_link = args[1]

        google_code = get_link_content_data(google_code_link)
        access_token, refresh_token = self.get_tokens(google_code)

        author = self.get_author(access_token)
        author.refresh_token = refresh_token
        self.logger.info("%s", author)
        self.save_author(author, google_session_link)

        return ScResult.OK

    def get_tokens(self, code: str) -> tuple[str]:
        # get access and refresh tokens by credentials
        base_url = "https://oauth2.googleapis.com/token"

        try:
            response = requests.post(
                url=base_url,
                data={
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": "http://localhost:3033",
                },
            )
            response.raise_for_status()
            res = response.json()
            return (res["access_token"], res["refresh_token"])

        except requests.exceptions.HTTPError as e:
            self.logger.error("HTTP Error: %s", e)
            self.logger.error("Status Code: %s", response.status_code)
            raise

        except requests.exceptions.RequestException as e:
            self.logger.error("Request Error: %s", e)
            raise

        except KeyError as e:
            self.logger.error("Key Error in response: %s", e)
            self.logger.error("Full response: %s", res)
            raise

    def save_author(
        self,
        author: Author,
        session_link: str,
        ):
        template = ScTemplate()
        user_alias = "_user"
        self.generate_base_keynodes(author)

        # generate new user node
        template.triple(
            self.concept_user,
            sc_type.VAR_PERM_POS_ARC,
            sc_type.VAR_NODE >> user_alias,
        )
        template.triple(
            self.lang_en,
            sc_type.VAR_PERM_POS_ARC,
            session_link,
            )
        # generate all links connected with this user
        template.quintuple(
            user_alias,
            sc_type.VAR_COMMON_ARC,
            self.name_link,
            sc_type.VAR_PERM_POS_ARC,
            self.nrel_name,
        )
        template.quintuple(
            user_alias,
            sc_type.VAR_COMMON_ARC,
            self.email_link,
            sc_type.VAR_PERM_POS_ARC,
            self.nrel_email,
        )
        template.quintuple(
            user_alias,
            sc_type.VAR_COMMON_ARC,
            self.acs_tkn_link,
            sc_type.VAR_PERM_POS_ARC,
            self.nrel_access_token,
        )
        template.quintuple(
            user_alias,
            sc_type.VAR_COMMON_ARC,
            self.ref_token_link,
            sc_type.VAR_PERM_POS_ARC,
            self.nrel_refresh_token,
        )
        template.quintuple(
            user_alias,
            sc_type.VAR_COMMON_ARC,
            session_link,
            sc_type.VAR_PERM_POS_ARC,
            self.nrel_google_session,
        )
        generate_by_template(template)

    def get_author(self, token: str) -> Author:
        # get base user info(name and email)
        url = "https://www.googleapis.com/oauth2/v2/userinfo"

        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }

        try:
            response = requests.get(url, headers=headers, timeout=30)

            if not response.ok:
                self.logger.error("User Info Error Details:")
                self.logger.error(f"Status Code: {response.status_code}")
                self.logger.error(f"URL: {response.url}")

            response.raise_for_status()

            user_data = response.json()

            return Author(
                name=user_data["name"],
                email=user_data["email"],
                access_token=token,
                )

        except requests.exceptions.HTTPError as e:
            self.logger.error("HTTP Error in get_user_info: %s", e)
            self.logger.error(f"Response Text: {response.text}")
            raise

        except requests.exceptions.RequestException as e:
            self.logger.error("Request Error in get_user_info: %s", e)
            raise

        except KeyError as e:
            self.logger.error("Missing expected field in user data: %s", e)
            self.logger.error(f"Available fields: {list(user_data.keys())}")
            raise

    def generate_base_keynodes(self, author):
        # generate base user info links
        self.name_link = generate_link(author.name)
        self.acs_tkn_link = generate_link(author.access_token)
        self.ref_token_link = generate_link(author.refresh_token)

        self.email_link = generate_link(author.email)
