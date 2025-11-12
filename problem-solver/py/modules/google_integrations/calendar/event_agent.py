
from sc_client.models import ScAddr
from sc_kpm import ScAgentClassic
from sc_kpm.identifiers import CommonIdentifiers
from sc_kpm.sc_sets import ScStructure
from sc_kpm.utils import (
    get_link_content_data,
)
from sc_kpm.utils.action_utils import (
    execute_agent,
    get_action_result,
)


class EventAgent(ScAgentClassic):
    def __init__(self, action: str):
        super().__init__(action)
        self.calendar_id = 'primary'        
        
    def get_authenticated_token(self, author_node: ScAddr) -> str | None:
        action_class_name = "action_google_auth"
        action, is_successful = execute_agent(
            arguments={author_node: False},
            concepts=[CommonIdentifiers.ACTION, action_class_name],
        )
        if is_successful:
            result_struct = get_action_result(action)
            token_link = ScStructure(set_node=result_struct).elements_set.pop()
            token = get_link_content_data(token_link)
            return token
        else:
            return None