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
    search_connector,
    search_element_by_non_role_relation,
)
from sc_kpm.utils.action_utils import (
    finish_action_with_status,
    generate_action_result,
    get_action_arguments,
)

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


class IndexingAgent(IntegrationAgent):
    def __init__(self):
        super().__init__("action_index_documents")

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
            "IndexingAgent finished %s",
            "successfully" if is_successful else "unsuccessfully",
        )
        return result

    def run(self, action_node: ScAddr) -> ScResult:
        self.logger.info("IndexingAgent started")

        try:
            message_addr = get_action_arguments(action_node, 1)[0]
            service = self.authorize(message_addr)            
            files = crawl_drive(service)

            self.logger.info(f"Всего файлов: {len(files)}")
            for f in files:
                self.logger.info(f"{f['name']}")

            if len(files) == 0:
                return ScResult.OK
            
            ai = AIComponents('ru_core_news_sm')
            indexer = IndexerWithFiles(ai)
            indexer.index_files(service, files)
            indexer.save_info_in_KB()

        except Exception as e:
            self.logger.info("IndexingAgent: finished with an error %s", e)
            return ScResult.ERROR

        return ScResult.OK
    
    def authorize(self, message_addr):
        nrel_authors = ScKeynodes.resolve("nrel_authors", sc_type.CONST_NODE_CLASS)
        author = search_element_by_non_role_relation(message_addr, nrel_authors)
        if author:
            self.author_node = author
        else:
            return ScResult.OK

        print(type(self.author_node))

        tokens_dict = self._get_tokens(self.author_node)
        if tokens_dict is None:
            self.logger.error("Did not find tokens!!!")

        access_token_link = tokens_dict.get('access_token')
        refresh_token_link = tokens_dict.get('refresh_token')

        access_token = get_link_content_data(access_token_link)
        refresh_token = get_link_content_data(refresh_token_link)
        
        try:
            # Создаём объект Credentials из токена
            creds = Credentials(
                token=access_token,
                refresh_token=refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=GOOGLE_CLIENT_ID,
                client_secret=GOOGLE_CLIENT_SECRET
            )
            if creds is not None:
                if creds.valid:
                    self.logger.info("Credentials object is GOOD")
            else:
                self.logger.info("Credentials object is None")
            # Создаём сервис Google Drive
            service = build('drive', 'v3', credentials=creds)
            return service
        except Exception as e:
            self.logger.info(f"Error creating service: {e}")
            return ScResult.ERROR
        
    def _get_tokens(self, author_node: ScAddr) -> dict[str, ScAddr]:
        nrel_refresh_token = ScKeynodes.resolve(
            "nrel_refresh_token",
            sc_type.CONST_NODE_NON_ROLE,
            )
        nrel_access_token = ScKeynodes.resolve(
            "nrel_access_token",
            sc_type.CONST_NODE_NON_ROLE,
            )
        template = ScTemplate()

        acs_alias = 'acs'
        ref_alias = 'ref'

        template.quintuple(
            author_node,
            sc_type.VAR_COMMON_ARC,
            sc_type.VAR_NODE_LINK >> acs_alias,
            sc_type.VAR_PERM_POS_ARC,
            nrel_access_token,
        )
        template.quintuple(
            author_node,
            sc_type.VAR_COMMON_ARC,
            sc_type.VAR_NODE_LINK >> ref_alias,
            sc_type.VAR_PERM_POS_ARC,
            nrel_refresh_token,
        )

        res = search_by_template(template)
        if res:
            return {
                'access_token': res[0].get(acs_alias),
                'refresh_token': res[0].get(ref_alias),
            }