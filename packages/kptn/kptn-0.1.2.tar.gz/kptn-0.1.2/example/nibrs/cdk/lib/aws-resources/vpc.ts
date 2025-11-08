import * as ec2 from "aws-cdk-lib/aws-ec2";
import { Construct } from 'constructs';

export function getOrCreateVpc(scope: Construct, STACK_NAME: string, VPC_ID?: string): ec2.IVpc {

  if (VPC_ID) {
    return ec2.Vpc.fromLookup(scope, "VPC", {
      vpcId: VPC_ID,
    })
  } else {
    return new ec2.Vpc(scope, "VPC", {
        vpcName: `${STACK_NAME}-VPC`,
        natGateways: 1,
        subnetConfiguration: [{
          name: "public",
          subnetType: ec2.SubnetType.PUBLIC
        }, {
          name: "private",
          subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS
        }],
        maxAzs: 2,
      }
    )
  }
}
