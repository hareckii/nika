import { 
    ScEventSubscriptionParams, 
    ScEventType, 
    ScTemplate, 
    ScType 
} from "ts-sc-client";
import { client } from "@api";


export async function fetchColorValue(funcChange) {
    
    const conceptHeader = 'concept_header';
    const conceptFooter = 'concept_footer';
    const conceptMainPart = 'concept_main_part';
    const componentColor = 'nrel_component_color';

    const baseKeynodes = [
        { id: conceptHeader, type: ScType.ConstNodeClass },
        { id: conceptMainPart, type: ScType.ConstNodeClass },
        { id: conceptFooter, type: ScType.ConstNodeClass },
    ];

    const helpKeynodes = [
        { id: componentColor, type: ScType.ConstNodeNonRole },
    ];

    const colorAlias = '_color';
    const componentAlias = '_component'
        
    const keynodes = await client.resolveKeynodes(baseKeynodes);
    const hKeynodes = await client.resolveKeynodes(helpKeynodes);

    for (var i = 0; i < baseKeynodes.length; i++) {
        const template = new ScTemplate();
        template.triple(
            keynodes[baseKeynodes[i].id],
            ScType.VarPermPosArc,
            [ScType.VarNode, componentAlias],
        );
        template.quintuple(
            componentAlias,
            ScType.VarCommonArc,
            [ScType.VarNodeLink, colorAlias],
            ScType.VarPermPosArc,
            hKeynodes[componentColor],
        );
        const resultColorLink = await client.searchByTemplate(template);
        
        if (resultColorLink.length) {
            const colorLink = resultColorLink[0].get(colorAlias);
            const resultColor = await client.getLinkContents([colorLink]);
            if (resultColor.length) {
                let color = resultColor[0].data;
                funcChange[i](color as any);
                const eventParams = new ScEventSubscriptionParams(colorLink, ScEventType.BeforeChangeLinkContent, fetchColorValue);
                await client.createElementaryEventSubscriptions([eventParams]); 
            }
        }    
    }
}