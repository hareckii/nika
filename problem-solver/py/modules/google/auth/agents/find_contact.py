import logging

from sc_client.client import search_by_template
from sc_client.constants import sc_type
from sc_client.models import ScAddr, ScTemplate
from sc_kpm import ScKeynodes, ScResult
from sc_kpm.utils import (
    generate_link,
    get_link_content_data,
)
from sc_kpm.utils.action_utils import (
    finish_action_with_status,
    generate_action_result,
    get_action_arguments,
)

from modules.google.integration_agent import IntegrationAgent


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(message)s",
    datefmt="[%d-%b-%y %H:%M:%S]",
)


class FindContactAgent(IntegrationAgent):
    def __init__(self):
        super().__init__("action_find_contact")
        self.nrel_contacts = ScKeynodes.resolve(
            "nrel_contacts",
            sc_type.CONST_NODE_NON_ROLE,
        )

    def on_event(
        self,
        event_element: ScAddr,  # noqa: ARG002
        event_edge: ScAddr,  # noqa: ARG002
        action_element: ScAddr,
    ) -> ScResult:
        try:
            self.logger.info("Started")
            result = self.run(action_element)
            is_successful = result != ScResult.ERROR
            finish_action_with_status(action_element, is_successful)
            self.logger.info(
                "Finished %s",
                "successfully" if is_successful else "unsuccessfully",
            )
            return result
        except Exception as e:
            self.logger.error("%s", e)

    def run(self, action_node: ScAddr) -> ScResult:
        name_link, self.author_node = get_action_arguments(action_node, 2)
        contact_node = self.get_contact(name_link)
        generate_action_result(action_node, contact_node)
        self.logger.info("Finished successfully!")
        finish_action_with_status(action_node)

        return ScResult.OK

    def get_contact(self, name_link: ScAddr) -> ScAddr:
        template = ScTemplate()

        tuple_alias = "_contacts_tuple"
        contact_alias = "_contact"

        template.quintuple(
            self.author_node,
            sc_type.VAR_COMMON_ARC,
            sc_type.VAR_NODE_TUPLE >> tuple_alias,
            sc_type.VAR_PERM_POS_ARC,
            self.nrel_contacts,
        )
        template.triple(
            tuple_alias,
            sc_type.VAR_PERM_POS_ARC,
            sc_type.VAR_NODE >> contact_alias,
        )
        template.quintuple(
            contact_alias,
            sc_type.VAR_COMMON_ARC,
            generate_link(name_link),
            sc_type.VAR_PERM_POS_ARC,
            self.nrel_name,
        )

        res = search_by_template(template)
        if res:
            contact_node = res[0].get(contact_alias)
            return contact_node
        else:
            self.logger.error(
                "Did ot find contact with name %s",
                get_link_content_data(name_link),
            )
