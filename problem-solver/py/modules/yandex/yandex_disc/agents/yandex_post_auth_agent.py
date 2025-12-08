import logging
import time
from typing import Optional

from sc_client.models import ScAddr, ScTemplate
from sc_client.constants import sc_type
from sc_client.client import search_by_template

from sc_kpm import ScAgentClassic, ScResult, ScKeynodes
from sc_kpm.utils import get_link_content_data
from sc_kpm.utils.action_utils import get_action_arguments

from modules.yandex.yandex_disc.agents.yandex_disc_info_agent import YandexDiscInfoAgent
from modules.yandex.yandex_disc.agents.yandex_disc_resources_agent import YandexDiscResourcesAgent


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(message)s",
    datefmt="[%d-%b-%y %H:%M:%S]"
)


class YandexPostAuthAgent(ScAgentClassic):
    def __init__(self):
        super().__init__("action_create_yandex_author")
        self.disc_info_updater = YandexDiscInfoAgent()
        self.disc_resources_updater = YandexDiscResourcesAgent()

    def on_event(self, event_element: ScAddr, event_edge: ScAddr, action_node: ScAddr) -> ScResult:
        try:
            args = get_action_arguments(action_node, 1)
            if not args:
                return ScResult.OK
            session_node = args[0]
            
            user_node = self._wait_for_user(session_node)
            if not user_node:
                self.logger.warning(f"User not found for session {session_node.value}")
                return ScResult.OK

            token = self._get_user_token(user_node)
            if not token or not isinstance(token, str):
                self.logger.error(f"Access token not found for user {user_node.value}")
                return ScResult.OK

            self.disc_info_updater.run(user_node, token)
            self.disc_resources_updater.run(user_node, token)

            self.logger.info("Disk info for user updated")

        except Exception as e:
            self.logger.error(f"Error in PostAuthAgent: {e}")
            return ScResult.ERROR

        return ScResult.OK

    def _wait_for_user(self, session_node: ScAddr, attempts: int = 20, delay: float = 0.5) -> Optional[ScAddr]:
        for _ in range(attempts):
            user_node = self._find_user_by_session(session_node)
            if user_node:
                return user_node
            time.sleep(delay)
        return None

    def _find_user_by_session(self, session_node: ScAddr) -> Optional[ScAddr]:
        nrel_auth_session = ScKeynodes.resolve("nrel_auth_session", sc_type.CONST_NODE_NON_ROLE)
        if not nrel_auth_session.is_valid():
            return None

        template = ScTemplate()
        template.quintuple(
            sc_type.VAR_NODE,
            sc_type.VAR_COMMON_ARC,
            session_node,
            sc_type.VAR_PERM_POS_ARC,
            nrel_auth_session
        )
        res = search_by_template(template)
        return res[0][0] if res else None

    def _get_user_token(self, user_node: ScAddr) -> Optional[str]:
        nrel_access_token = ScKeynodes.resolve("nrel_access_token", sc_type.CONST_NODE_NON_ROLE)
        
        template = ScTemplate()
        template.quintuple(
            user_node,
            sc_type.VAR_COMMON_ARC,
            sc_type.VAR_NODE_LINK,
            sc_type.VAR_PERM_POS_ARC,
            nrel_access_token
        )
        res = search_by_template(template)
        
        if res:
            token_link = res[0][2]
            return get_link_content_data(token_link)
        return None