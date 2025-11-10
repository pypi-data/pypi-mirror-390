import { OrganizationsClient, ListRootsCommand } from "@aws-sdk/client-organizations";
async function getEnabledOrgPolicyTypes(region) {
    const orgClient = new OrganizationsClient({ region });
    let policyTypesEnabled = {
        scpEnabled: false,
        tagPolicyEnabled: false,
        backupPolicyEnabled: false
    };
    try {
        const input = {};
        const command = new ListRootsCommand(input);
        const roots = await orgClient.send(command);
        if (roots.Roots) {
            if (roots.Roots[0].PolicyTypes) {
                for (const enabledPolicy of roots.Roots[0].PolicyTypes) {
                    if (enabledPolicy.Type == 'SERVICE_CONTROL_POLICY' && enabledPolicy.Status == 'ENABLED') {
                        policyTypesEnabled.scpEnabled = true;
                    }
                    if (enabledPolicy.Type == 'TAG_POLICY' && enabledPolicy.Status == 'ENABLED') {
                        policyTypesEnabled.tagPolicyEnabled = true;
                    }
                    if (enabledPolicy.Type == 'BACKUP_POLICY' && enabledPolicy.Status == 'ENABLED') {
                        policyTypesEnabled.backupPolicyEnabled = true;
                    }
                } // end for
            } // end if
        } // end if
    }
    catch (error) {
        console.error(`An error occurred: ${error}`);
    }
    finally {
        orgClient.destroy();
        return policyTypesEnabled;
    }
}
export default getEnabledOrgPolicyTypes;
