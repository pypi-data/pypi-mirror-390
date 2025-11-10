import { CloudFormationClient, DescribeOrganizationsAccessCommand, } from "@aws-sdk/client-cloudformation";
async function getOrgCloudFormation(region) {
    let orgCfnStatus = {
        status: "disabled"
    };
    const cloudFormationClient = new CloudFormationClient({ region });
    try {
        const describeOrgAccessInput = {};
        const command = new DescribeOrganizationsAccessCommand(describeOrgAccessInput);
        const cloudFormationOrgAccess = await cloudFormationClient.send(command);
        //console.log("CloudFormation activation status: ", cloudFormationOrgAccess.Status)
        orgCfnStatus.status = cloudFormationOrgAccess.Status ?? "disabled";
    }
    catch (error) {
        console.log(`Error: ${error}`);
        //throw new Error(`Error: ${error}`);
    }
    finally {
        cloudFormationClient.destroy();
        return orgCfnStatus;
    }
}
;
export default getOrgCloudFormation;
