import * as ec2 from "aws-cdk-lib/aws-ec2"
import * as efs from "aws-cdk-lib/aws-efs";
import { Construct } from 'constructs';

export function getOrCreateEfs(scope: Construct, EFS_VPC: ec2.IVpc, EFS_ID?: string): efs.IFileSystem {

  if (EFS_ID) {
    //If you import an EFS you will need to create an AccessPoint
    //AWS->EFS->Network->Manage
    //Then you must ssh into the instance and mount manually
    const securityGroup = new ec2.SecurityGroup(scope, "NibrsEfsSecurityGroup", {
      vpc: EFS_VPC,
      description: "Nibrs EFS",
    })
    return efs.FileSystem.fromFileSystemAttributes(scope, 'existingFS', {
      fileSystemId: EFS_ID,
      securityGroup: securityGroup,
    });      
  } else {
    return new efs.FileSystem(scope, "NIBRS_EFS", {
      vpc: EFS_VPC,
      lifecyclePolicy: efs.LifecyclePolicy.AFTER_7_DAYS,
      performanceMode: efs.PerformanceMode.GENERAL_PURPOSE,
      throughputMode: efs.ThroughputMode.ELASTIC,
      encrypted: false,
    })
  }
}
