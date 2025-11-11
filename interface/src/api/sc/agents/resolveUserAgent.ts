import {ScTemplate, ScType} from 'ts-sc-client';
import { client } from '@api/sc';
import { getCookie } from '@hooks/useGoogleAuth';

const conceptUser = 'concept_user';
const conceptDialog = 'concept_dialogue';
const rrelDialogParticipant = 'rrel_dialog_participant';
const nrelGoogleSession = 'nrel_google_session';

const baseKeynodes = [
    { id: conceptUser, type: ScType.ConstNodeClass },
    { id: conceptDialog, type: ScType.ConstNodeClass },
    { id: rrelDialogParticipant, type: ScType.ConstNodeRole },
    { id: nrelGoogleSession, type: ScType.ConstNodeNonRole },
];

const getUser = async () => {
    const session = getCookie('google_session')
    if(!session) return null;
    
    const res = await client.searchLinksByContents([session])
    const session_link = res[0][0]
    if(!session_link) return null;

    const keynodes = await client.resolveKeynodes(baseKeynodes);
    const user = '_user';
    const template = new ScTemplate();

    template.triple(
        keynodes[conceptUser],
        ScType.VarPermPosArc,
        [ScType.VarNode, user],
    );

    template.quintuple(
        user, ScType.VarCommonArc, session_link,
        ScType.VarPermPosArc, keynodes[nrelGoogleSession]
    )

    const result = await client.searchByTemplate(template);
    
    if (result.length === 1) {
        console.log("Successfully find user node!")
        return result[0].get(user);
    }
    return null;
}

const createUser = async () => {
    const keynodes = await client.resolveKeynodes(baseKeynodes);
    const user = '_user';
    const dialog = '_dialog';

    const template = new ScTemplate();
    template.triple(
        keynodes[conceptUser],
        ScType.VarPermPosArc,
        [ScType.VarNode, user],
    );
    template.triple(
        keynodes[conceptDialog],
        ScType.VarPermPosArc,
        [ScType.VarNode, dialog],
    );
    template.quintuple(
        dialog,
        ScType.VarPermPosArc,
        user,
        ScType.VarPermPosArc,
        keynodes[rrelDialogParticipant],
    );
    const result = await client.generateByTemplate(template, {});
    return result?.get(user);
}

export const resolveUserAgent = async () => {
    const user = await getUser();
    if (user !== null) {
        return user;
    }
    return await createUser();
};
