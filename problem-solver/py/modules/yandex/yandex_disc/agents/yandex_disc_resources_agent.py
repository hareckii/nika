import logging

from sc_client.models import ScAddr, ScLinkContentType, ScTemplate, ScConstruction, ScLinkContent
from sc_client.constants import sc_type
from sc_client.client import search_by_template, create_elements, delete_elements

from sc_kpm import ScKeynodes
from sc_kpm.utils import generate_connector

from modules.yandex.yandex_disc.services import YandexDisсResourcesService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(message)s",
    datefmt="[%d-%b-%y %H:%M:%S]"
)


class YandexDiscResourcesAgent:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def run(self, user_node: ScAddr, token: str) -> bool:
        try:
            info_text = YandexDisсResourcesService.get_file_list(token)
            self._save_to_kb(user_node, info_text)
            return True
        except Exception as e:
            self.logger.error(f"Failed to update disk resources: {e}")
            return False

    def _save_to_kb(self, user_node: ScAddr, text: str):
        nrel_target = ScKeynodes.resolve("nrel_yandex_disc_resources", sc_type.CONST_NODE_NON_ROLE)
        
        template = ScTemplate()
        template.quintuple(
            user_node,
            sc_type.VAR_COMMON_ARC,
            sc_type.VAR_NODE_LINK,
            sc_type.VAR_PERM_POS_ARC,
            nrel_target
        )
        old_res = search_by_template(template)
        for item in old_res:
            delete_elements([item[2]])

        link_content = ScLinkContent(text, ScLinkContentType.STRING)
        const = ScConstruction()
        const.create_link(sc_type.CONST_NODE_LINK, link_content)
        link_node = create_elements(const)[0]
        
        edge = generate_connector(sc_type.CONST_COMMON_ARC, user_node, link_node)
        generate_connector(sc_type.CONST_PERM_POS_ARC, nrel_target, edge)