"""
This code creates some test agent and registers until the user stops the process.
For this we wait for SIGINT.
"""

import logging

import requests

from sc_client.client import search_by_template
from sc_client.constants import sc_type
from sc_client.models import ScAddr, ScLinkContentType, ScTemplate
from sc_kpm import ScAgentClassic, ScKeynodes, ScResult
from sc_kpm.sc_sets import ScSet
from sc_kpm.utils import (
    check_connector,
    erase_connectors,
    generate_connector,
    generate_link,
    get_element_system_identifier,
    get_link_content_data,
    generate_role_relation,
    search_connector,
    search_element_by_non_role_relation,
)
from sc_kpm.utils.action_utils import (
    finish_action_with_status,
    generate_action_result,
    get_action_arguments,
)

from modules.google.disk.models.search_processor import SearchEngine
from modules.google.disk.models.crawler import crawl_drive
from modules.google.disk.models.indexer import AIComponents, IndexerWithFiles
from auth.base.agents.integration_agent import IntegrationAgent

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

from secrets_env import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(message)s",
    datefmt="[%d-%b-%y %H:%M:%S]",
)


class SearchDocumentsAgent(IntegrationAgent):
    def __init__(self):
        super().__init__("action_search_documents")

    @property
    def check_token_agent_action(self) -> str:
        return 'action_check_google_token'

    def on_event(
        self,
        event_element: ScAddr,  # noqa: ARG002
        event_edge: ScAddr,  # noqa: ARG002
        action_element: ScAddr,
    ) -> ScResult:
        result = self.run(action_element)
        is_successful = result == ScResult.OK
        finish_action_with_status(action_element, is_successful)
        self.logger.info(
            "SearchDocumentsAgent finished %s",
            "successfully" if is_successful else "unsuccessfully",
        )
        return result

    def run(self, action_node: ScAddr) -> ScResult:
        self.logger.info("SearchDocumentsAgent started")

        try:
            message_addr = get_action_arguments(action_node, 1)[0]

            request = self.extract_request(message_addr)

            ai = AIComponents('ru_core_news_sm')
            engine = SearchEngine(ai)
            results = engine.search(request)
            engine.save_info_in_KB(results, request)

        except Exception as e:
            self.logger.info("SearchDocumentsAgent: finished with an error %s", e)
            return ScResult.ERROR

        return ScResult.OK
    
    def extract_request(self, message_addr: ScAddr) -> str:
        rrel_request = ScKeynodes.resolve("rrel_request", sc_type.CONST_NODE_CLASS)
        template = ScTemplate()
        template.quintuple(
            message_addr,
            sc_type.VAR_PERM_POS_ARC,
            sc_type.VAR_NODE_LINK,
            sc_type.VAR_PERM_POS_ARC,
            rrel_request,
        )
        search_results = search_by_template(template)
        request_link = search_results[0][2]
        return get_link_content_data(request_link)
