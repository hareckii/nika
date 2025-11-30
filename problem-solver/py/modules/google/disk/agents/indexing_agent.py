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

from modules.google.disk.models.auth import authorize
from modules.google.disk.models.crawler import crawl_drive
from modules.google.disk.models.indexer import AIComponents, IndexerWithFiles



logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(message)s",
    datefmt="[%d-%b-%y %H:%M:%S]",
)


class IndexingAgent(ScAgentClassic):
    def __init__(self):
        super().__init__("action_index_documents")

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
            # message_addr = get_action_arguments(action_node, 1)[0]
            service = authorize()
            files = crawl_drive(service)

            self.logger.info(f"Всего файлов: {len(files)}")
            for f in files:
                self.logger.info(f"{f['name']}")
            files = files[:4]

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