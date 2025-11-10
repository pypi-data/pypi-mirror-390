import { OrganizationsClient, DescribeOrganizationCommand, ListRootsCommand } from "@aws-sdk/client-organizations";
async function getOrgDetails(region) {
    const orgClient = new OrganizationsClient({ region });
    let orgDetails = {};
    try {
        const orgDescribeCommand = new DescribeOrganizationCommand({});
        const orgData = await orgClient.send(orgDescribeCommand);
        if (orgData.Organization) {
            orgDetails.id = orgData.Organization.Id ?? "";
            // console.log(`Organization ID: ${orgDetails.id}` );
            orgDetails.arn = orgData.Organization.Arn ?? "";
            // console.log(`Organization ARN: ${orgDetails.arn}`);
        }
        const command = new ListRootsCommand({});
        const roots = await orgClient.send(command);
        if (roots.Roots) {
            orgDetails.rootOuId = roots.Roots[0].Id;
            // console.log(`AWS Org root ou id: ${orgDetails.rootOuId}`)
        }
        else {
            console.log('No info found for your AWS Organization.');
        }
    }
    catch (error) {
        console.error(`An error occurred: ${error}`);
    }
    finally {
        orgClient.destroy();
        return orgDetails;
    }
}
export default getOrgDetails;
