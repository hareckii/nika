from sc_client.constants import sc_type
from sc_client.models import ScAddr
from sc_kpm import ScAgentClassic, ScKeynodes
from sc_kpm.identifiers import CommonIdentifiers
from sc_kpm.sc_sets import ScStructure
from sc_kpm.utils import (
    get_link_content_data,
    search_element_by_non_role_relation,
)
from sc_kpm.utils.action_utils import (
    execute_agent,
    get_action_result,
)

from modules.google.auth.models import Author


class IntegrationAgent(ScAgentClassic):
    def __init__(self, action: str):
        super().__init__(action)
        self.nrel_name: ScAddr = ScKeynodes.resolve(
            "nrel_name",
            sc_type.CONST_NODE_NON_ROLE,
        )
        self.nrel_email: ScAddr = ScKeynodes.resolve(
            "nrel_email",
            sc_type.CONST_NODE_NON_ROLE,
        )
        self.author_node: ScAddr | None = None

    def _get_authenticated_token(self) -> str | None:
        action_class_name = "action_google_auth"
        action, is_successful = execute_agent(
            arguments={self.author_node: False},
            concepts=[CommonIdentifiers.ACTION, action_class_name],
        )
        if is_successful:
            result_struct = get_action_result(action)
            token_link = ScStructure(
                set_node=result_struct,
            ).elements_set.pop()
            access_token = get_link_content_data(token_link)
            return access_token
        return None

    def get_author(self) -> Author:
        access_token = self._get_authenticated_token()
        name = search_element_by_non_role_relation(
            self.author_node,
            self.nrel_name,
        )
        email = search_element_by_non_role_relation(
            self.author_node,
            self.nrel_email,
        )
        try:
            return Author(
                name=get_link_content_data(name),
                email=get_link_content_data(email),
                access_token=access_token,
            )
        except ValueError:
            self.logger.info(
                "Got error with author params: "
                f"{access_token=}, {name=}, {email=}",
            )
            return None
