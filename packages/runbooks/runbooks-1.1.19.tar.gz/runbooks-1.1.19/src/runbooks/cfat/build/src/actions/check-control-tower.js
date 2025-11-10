import { ControlTowerClient, ListLandingZonesCommand, GetLandingZoneCommand } from "@aws-sdk/client-controltower";
async function getControlTower(region) {
    let controlTowerInfo = {};
    const controlTowerClient = new ControlTowerClient({ region });
    try {
        const command = new ListLandingZonesCommand({});
        const response = await controlTowerClient.send(command);
        if (response.landingZones && response.landingZones.length > 0) {
            const input = {
                landingZoneIdentifier: response.landingZones[0].arn,
            };
            const lzRegion = response.landingZones[0].arn?.toString().split(':')[3] ?? "";
            if (lzRegion) {
                controlTowerInfo.controlTowerRegion = lzRegion;
                const controlTowerClientRegion = new ControlTowerClient({ region: lzRegion });
                const command = new GetLandingZoneCommand(input);
                const lzResponse = await controlTowerClientRegion.send(command);
                if (lzResponse.landingZone) {
                    controlTowerInfo.status = lzResponse.landingZone.status;
                    controlTowerInfo.latestAvailableVersion = lzResponse.landingZone.latestAvailableVersion;
                    controlTowerInfo.deployedVersion = lzResponse.landingZone.version;
                    controlTowerInfo.driftStatus = lzResponse.landingZone.driftStatus?.status;
                }
            }
        }
    }
    catch (error) {
        console.error(`Error checking Control Tower in ${region}:`, error);
    }
    finally {
        controlTowerClient.destroy();
    }
    return controlTowerInfo;
}
export default getControlTower;
