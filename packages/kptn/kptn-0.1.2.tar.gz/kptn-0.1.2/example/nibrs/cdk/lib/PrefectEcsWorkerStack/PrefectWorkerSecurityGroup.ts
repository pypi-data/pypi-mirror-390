import { Construct } from 'constructs';
import * as ec2 from "aws-cdk-lib/aws-ec2";


/**
 * Creates a security group for the Prefect worker in ECS.
 * @param scope The construct scope.
 * @param props The properties for the security group.
 * @returns The created security group.
 */
export function PrefectWorkerSecurityGroup(scope: Construct, vpc: ec2.IVpc) {
  const securityGroup = new ec2.SecurityGroup(scope, "PrefectWorkerSecurityGroup", {
    vpc,
    description: "ECS Prefect worker",
  })

  // Allow outbound traffic to the internet and Prefect server
  securityGroup.addEgressRule(ec2.Peer.anyIpv4(), ec2.Port.tcp(443), "HTTPS outbound")
  securityGroup.addEgressRule(ec2.Peer.anyIpv4(), ec2.Port.tcp(4200), "Prefect outbound")

  return securityGroup
}
  