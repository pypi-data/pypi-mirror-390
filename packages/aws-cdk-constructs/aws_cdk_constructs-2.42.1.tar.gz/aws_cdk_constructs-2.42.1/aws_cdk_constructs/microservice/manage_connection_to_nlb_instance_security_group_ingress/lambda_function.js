const { 
  EC2Client, 
  DescribeInstancesCommand, 
  AuthorizeSecurityGroupIngressCommand, 
  DescribeSecurityGroupsCommand, 
  RevokeSecurityGroupIngressCommand 
} = require("@aws-sdk/client-ec2");

exports.handler = async (event) => {
    console.log(JSON.stringify(event));

    const sns = event.Records[0].Sns;
    const message = JSON.parse(sns.Message);
    
    const shouldAdd = message.LifecycleTransition === "autoscaling:EC2_INSTANCE_LAUNCHING";

    const ec2 = new EC2Client({});

    const instanceId = message.EC2InstanceId;
    console.log(instanceId);

    const params = { InstanceIds: [instanceId] };
    console.log(shouldAdd ? "ADDING" : "REMOVING", instanceId);

    const securityGroupId = process.env["SECURITY_GROUP"];
    const port = parseInt(process.env["PORT"], 10);

    if (shouldAdd) {
        // Get private IP of the instance
        const data = await ec2.send(new DescribeInstancesCommand(params));
        const instanceIp = data.Reservations[0].Instances[0].PrivateIpAddress;

        const manageParams = {
            GroupId: securityGroupId,
            IpPermissions: [
                {
                    FromPort: port,
                    ToPort: port,
                    IpProtocol: "tcp",
                    IpRanges: [
                        {
                            CidrIp: instanceIp + "/32",
                            Description: instanceId,
                        },
                    ],
                },
            ],
        };

        return await ec2.send(new AuthorizeSecurityGroupIngressCommand(manageParams));
    }

    // Remove ingress rule if it exists
    const group = await ec2.send(
        new DescribeSecurityGroupsCommand({ GroupIds: [securityGroupId] })
    );

    // Find the matching ingress rule by Description
    const ingress = group.SecurityGroups[0].IpPermissions
        .flatMap((p) =>
            p.IpRanges.map((r) => ({
                ...r,
                FromPort: p.FromPort,
                ToPort: p.ToPort,
                IpProtocol: p.IpProtocol,
            }))
        )
        .find((r) => r.Description === instanceId);

    if (!ingress) {
        console.log("No matching ingress rule found for", instanceId);
        return;
    }

    const manageParams = {
        GroupId: securityGroupId,
        IpPermissions: [
            {
                FromPort: port,
                ToPort: port,
                IpProtocol: "tcp",
                IpRanges: [
                    {
                        CidrIp: ingress.CidrIp,
                        Description: instanceId,
                    },
                ],
            },
        ],
    };

    return await ec2.send(new RevokeSecurityGroupIngressCommand(manageParams));
};
