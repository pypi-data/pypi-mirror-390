import { EC2Client, DescribeVpcsCommand } from "@aws-sdk/client-ec2";
async function checkVpcExists(regions) {
    let vpcValidation = [];
    for (const region of regions) {
        const ec2Client = new EC2Client({ region });
        const command = new DescribeVpcsCommand({});
        try {
            const response = await ec2Client.send(command);
            if (response.Vpcs) {
                if (response.Vpcs.length > 0) {
                    const vpcFound = {
                        region: region,
                        vpcFound: true
                    };
                    vpcValidation.push(vpcFound);
                }
                else {
                    const vpcFound = {
                        region: region,
                        vpcFound: false
                    };
                    vpcValidation.push(vpcFound);
                }
            }
            else {
                const vpcFound = {
                    region: region,
                    vpcFound: false
                };
                vpcValidation.push(vpcFound);
            }
        }
        catch (error) {
            console.log(`Error: ${error}`);
        }
        finally {
            ec2Client.destroy();
        }
    } // end for
    return vpcValidation;
}
;
export default checkVpcExists;
