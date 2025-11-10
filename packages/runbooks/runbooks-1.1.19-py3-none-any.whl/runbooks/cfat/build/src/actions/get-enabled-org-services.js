import { OrganizationsClient, ListAWSServiceAccessForOrganizationCommand } from "@aws-sdk/client-organizations";
async function getEnabledOrgServices(region) {
    const discoveredOrgServices = [];
    const orgClient = new OrganizationsClient({ region });
    try {
        const orgServiceAccessCommand = new ListAWSServiceAccessForOrganizationCommand({});
        const orgServiceAccessResponse = await orgClient.send(orgServiceAccessCommand);
        if (orgServiceAccessResponse.EnabledServicePrincipals && orgServiceAccessResponse.EnabledServicePrincipals.length > 0) {
            orgServiceAccessResponse.EnabledServicePrincipals;
            for (const orgService of orgServiceAccessResponse.EnabledServicePrincipals) {
                const foundOrgService = { service: orgService.ServicePrincipal ?? "" };
                discoveredOrgServices.push(foundOrgService);
            }
        }
    }
    catch (error) {
        console.error('Error checking service access:', error);
    }
    finally {
        orgClient.destroy();
        return discoveredOrgServices;
    }
}
;
export default getEnabledOrgServices;
