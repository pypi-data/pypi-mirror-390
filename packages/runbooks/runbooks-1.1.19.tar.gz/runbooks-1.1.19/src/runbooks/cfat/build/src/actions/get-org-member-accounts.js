import { OrganizationsClient, ListAccountsCommand } from '@aws-sdk/client-organizations';
async function getOrgMemberAccounts(region = 'us-east-1') {
    let orgMemberAccountInfo = [];
    const orgsClient = new OrganizationsClient({ region });
    const input = {
        MaxResults: Number("200"),
    };
    try {
        let response = await orgsClient.send(new ListAccountsCommand({}));
        if (response.Accounts && response.Accounts.length > 0) {
            for (const account of response.Accounts) {
                let orgMemberAccount = {
                    accountName: account.Name,
                    accountEmail: account.Email,
                };
                orgMemberAccountInfo.push(orgMemberAccount);
            }
            do {
                if (response.NextToken) {
                    response = await orgsClient.send(new ListAccountsCommand({ NextToken: response.NextToken }));
                    if (response.Accounts && response.Accounts.length > 0) {
                        for (const account of response.Accounts) {
                            let orgMemberAccount = {
                                accountName: account.Name,
                                accountEmail: account.Email,
                            };
                            orgMemberAccountInfo.push(orgMemberAccount);
                        }
                    }
                }
            } while (response.NextToken);
        }
    }
    catch (error) {
        console.error('Error listing AWS accounts:', error);
    }
    finally {
        orgsClient.destroy();
    }
    return orgMemberAccountInfo;
}
export default getOrgMemberAccounts;
