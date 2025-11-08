// The security group for ECS Tasks that execute flow runs

import { Construct } from 'constructs';
import * as ec2 from "aws-cdk-lib/aws-ec2";
import * as ecs from "aws-cdk-lib/aws-ecs";
import { FileSystem, IFileSystem } from 'aws-cdk-lib/aws-efs';


/**
 * Creates a security group for the Prefect worker in ECS.
 * @param scope The construct scope.
 * @param props The properties for the security group.
 * @returns The created security group.
 */
export function PrefectFlowSecurityGroup(
  scope: Construct,
  vpc: ec2.IVpc,
  nibrsEfs: IFileSystem,
  ecsCluster: ecs.ICluster) {
  const securityGroup = new ec2.SecurityGroup(scope, "PrefectFlowSecurityGroup", {
    vpc,
    description: "Prefect ECS-Task Flow Runs",
  })

  // Allow access to/from the EFS file system
  securityGroup.connections.allowFrom(nibrsEfs, ec2.Port.tcp(FileSystem.DEFAULT_PORT))
  securityGroup.connections.allowTo(nibrsEfs, ec2.Port.tcp(FileSystem.DEFAULT_PORT))

  // Allow self-referential ingress
  // Specifically we need to allow Dask Scheduler, Dask Workers, and Nanny ports
  // Dask Scheduler is set to 8786-8787. However workers & nanny both use random ports
  securityGroup.connections.allowFrom(securityGroup, ec2.Port.allTcp(), "Self-referencing Rule.")
  
  securityGroup.connections.allowTo(ecsCluster, ec2.Port.tcp(4200), "Allow Prefect Web Server access from flow runner")

  return securityGroup
}
