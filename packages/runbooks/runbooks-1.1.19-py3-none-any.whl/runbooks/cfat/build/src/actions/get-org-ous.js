import { OrganizationsClient, ListOrganizationalUnitsForParentCommand, ListAccountsForParentCommand } from "@aws-sdk/client-organizations";
async function getOrgTopLevelOus(region, rootOuId) {
    const orgClient = new OrganizationsClient({ region });
    let topLevelOus = [];
    try {
        const listOUsCommand = new ListOrganizationalUnitsForParentCommand({
            ParentId: rootOuId,
        });
        const listOUsResponse = await orgClient.send(listOUsCommand);
        if (listOUsResponse.OrganizationalUnits) {
            for (const ou of listOUsResponse.OrganizationalUnits) {
                let topLevelOu = {
                    id: ou.Id,
                    name: ou.Name
                };
                const accountResponse = await orgClient.send(new ListAccountsForParentCommand({ ParentId: ou.Id }));
                if (accountResponse.Accounts && accountResponse.Accounts.length > 0) {
                    topLevelOu.accounts = accountResponse.Accounts;
                }
                topLevelOus.push(topLevelOu);
            }
        }
    }
    catch (error) {
        console.error('Error checking service access:', error);
        return [];
    }
    finally {
        orgClient.destroy();
    }
    return topLevelOus;
}
;
export default getOrgTopLevelOus;
