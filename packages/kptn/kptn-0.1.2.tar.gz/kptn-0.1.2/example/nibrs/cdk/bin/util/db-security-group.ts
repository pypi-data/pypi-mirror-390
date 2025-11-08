import { EC2Client, DescribeSecurityGroupsCommand, AuthorizeSecurityGroupIngressCommand } from "@aws-sdk/client-ec2";

// Given an IP address and security group ID, update the security group to
// allow ingress from that IP address, unless it is already allowed.
export async function addIngressRuleToSecurityGroup(
  region: string,
  ip: string,
  securityGroupId: string
) {
  const ec2Client = new EC2Client({ region });
  // get the security group
  const describeSecurityGroupsCommand = new DescribeSecurityGroupsCommand({
    GroupIds: [securityGroupId],
  });
  const securityGroup = await ec2Client
    .send(describeSecurityGroupsCommand)
    .then((data) => {
      return data.SecurityGroups?.[0];
    });
  if (!securityGroup) {
    throw new Error(`Security group ${securityGroupId} not found`);
  }

  // console.log(`Found security group`)
  // console.log(securityGroup);
  // console.log(securityGroup.IpPermissions![0].IpRanges);

  // check if the ingress rule already exists
  const existingIngressRule = securityGroup.IpPermissions?.find((ipPermission) => {
    return (
      ipPermission.IpRanges?.find((ipRange) => {
        return ipRange.CidrIp === `${ip}/32`;
      }) !== undefined
    );
  });
  if (existingIngressRule) {
    console.log(`Ingress rule already exists for ${ip}`);
    return;
  }
  // add the ingress rule for port 5432
  const params = {
    GroupId: securityGroupId,
    IpPermissions: [{
      IpProtocol: "tcp",
      FromPort: 5432,
      ToPort: 5432,
      IpRanges: [
        {
          CidrIp: `${ip}/32`,
          Description: `${process.env.STACK_NAME} public subnet (${process.env.AWS_DEFAULT_REGION})`,
        },
      ],
    }],
  };
  await ec2Client.send(new AuthorizeSecurityGroupIngressCommand(params));
  console.log(`Added ingress rule for ${ip}`);
}