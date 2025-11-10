import logging
from os import getenv

from dotenv import load_dotenv
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
from modules.google_integrations_module.auth.google_response import GoogleResponse
from modules.google_integrations_module.auth.user import User

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(message)s",
    datefmt="[%d-%b-%y %H:%M:%S]",
)


class CreateGoogleUser(ScAgentClassic):
    def __init__(self):
        super().__init__("action_create_google_user")
        self.nrel_name: ScAddr = ScKeynodes.resolve(
            "nrel_name", sc_type.CONST_NODE_NON_ROLE
        )
        self.nrel_email: ScAddr = ScKeynodes.resolve(
            "nrel_email", sc_type.CONST_NODE_NON_ROLE
        )
        self.nrel_access_token: ScAddr = ScKeynodes.resolve(
            "nrel_access_token", sc_type.CONST_NODE_NON_ROLE
        )
        self.nrel_refresh_token: ScAddr = ScKeynodes.resolve(
            "nrel_refresh_token", sc_type.CONST_NODE_NON_ROLE
        )
        self.nrel_google_session: ScAddr = ScKeynodes.resolve(
            "nrel_google_session", sc_type.CONST_NODE_NON_ROLE
        )
        self.concept_user: ScAddr = ScKeynodes.resolve(
            "concept_user", sc_type.CONST_NODE_CLASS
        )

    def on_event(
        self, event_element: ScAddr, event_edge: ScAddr, action_element: ScAddr
    ) -> ScResult:
        result = self.run(action_element)
        is_successful = result == ScResult.OK
        finish_action_with_status(action_element, is_successful)
        self.logger.info(
            "Finished %s", "successfully" if is_successful else "unsuccessfully"
        )
        return result

    def run(self, action_node: ScAddr) -> ScResult:
        self.logger.info("Started create user agent")

        try:
            self.logger.info("BEFORE GETTING")
            args = get_action_arguments(action_node, 2)
            
            google_session_link = args[0]
            google_code_link = args[1]
            
            google_session = get_link_content_data(google_session_link)
            self.logger.info(f"{google_session=}")
            google_code = get_link_content_data(google_code_link)
            self.logger.info(f"{google_code=}")
            response = self.get_response(google_code)
            
            self.logger.info(
                f"{response.access_token=},\n {response.refresh_token=}"
            )

            user = self.get_user_info(response.access_token)
            self.logger.info(
                f"{user.name=}, {user.email=}"
            )
            self.logger.info("BEFORE SAVING")
            self.save_user(response, user, google_session_link)
            
        except Exception as e:
            self.logger.info(f"AddEventAgent: finished with an error {e}")
            return ScResult.ERROR

        return ScResult.OK
    
    @staticmethod
    def get_response(self, code: str) -> GoogleResponse:
        # get access and refresh tokens by credentials
        base_url = "https://oauth2.googleapis.com/token"

        try:
            response = requests.post(
                url=base_url,
                data={
                    "client_id": getenv("GOOGLE_CLIENT_ID"),
                    "client_secret": getenv("GOOGLE_CLIENT_SECRET"),
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": "http://localhost:3033",
                },
            )
            response.raise_for_status()
            res = response.json()
            return GoogleResponse(
                access_token=res["access_token"], refresh_token=res["refresh_token"]
            )

        except requests.exceptions.HTTPError as e:
            self.logger.error(f"HTTP Error: {e}")
            self.logger.error(f"Status Code: {response.status_code}")
            self.logger.error(f"Response Text: {response.text}")
            raise

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request Error: {e}")
            raise

        except KeyError as e:
            self.logger.error(f"Key Error in response: {e}")
            self.logger.error(f"Full response: {res}")
            raise
        
    def save_user(self, response: GoogleResponse, user: User, session_link: str):
        template = ScTemplate()
        user_alias = '_user'
        self.generate_base_keynodes(user, response)
        
        #generate new user node
        template.triple(
            self.concept_user,
            sc_type.VAR_PERM_POS_ARC,
            sc_type.VAR_NODE >> user_alias
        )
        #generate all links connected with this user
        template.quintuple(
            user_alias, sc_type.VAR_COMMON_ARC, self.name_link,
            sc_type.VAR_PERM_POS_ARC, self.nrel_name
        )
        template.quintuple(
            user_alias, sc_type.VAR_COMMON_ARC, self.email_link,
            sc_type.VAR_PERM_POS_ARC, self.nrel_email,
        )
        template.quintuple(
            user_alias, sc_type.VAR_COMMON_ARC, self.acs_tkn_link,
            sc_type.VAR_PERM_POS_ARC, self.nrel_access_token
        )
        template.quintuple(
            user_alias, sc_type.VAR_COMMON_ARC, self.ref_token_link,
            sc_type.VAR_PERM_POS_ARC, self.nrel_refresh_token
        )
        template.quintuple(
            user_alias, sc_type.VAR_COMMON_ARC, session_link,
            sc_type.VAR_PERM_POS_ARC, self.nrel_google_session,
        )
        generate_by_template(template)
    
    @staticmethod    
    def get_user_info(self, token: str) -> User:
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
                self.logger.error(f"Response Headers: {dict(response.headers)}")
                self.logger.error(f"Response Body: {response.text}")
            
            response.raise_for_status()

            user_data = response.json()
            self.logger.info(f"Received user data: {user_data}")
            
            return User(
                name=user_data['name'],
                email=user_data['email']
            )
        
        except requests.exceptions.HTTPError as e:
            self.logger.error(f"HTTP Error in get_user_info: {e}")
            self.logger.error(f"Response Text: {response.text}")
            raise
        
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request Error in get_user_info: {e}")
            raise
        
        except KeyError as e:
            self.logger.error(f"Missing expected field in user data: {e}")
            self.logger.error(f"Available fields: {list(user_data.keys())}")
            raise
        
    def generate_base_keynodes(self, user, response):
        # generate base user info links
        self.name_link = generate_link(user.name)
        self.acs_tkn_link = generate_link(response.access_token)
        self.ref_token_link = generate_link(response.refresh_token)

        self.email_link = generate_link(user.email)
