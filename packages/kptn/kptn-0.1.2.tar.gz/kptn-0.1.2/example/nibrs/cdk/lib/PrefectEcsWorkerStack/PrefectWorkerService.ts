import { Construct } from 'constructs';
import * as ecs from "aws-cdk-lib/aws-ecs";
import * as ec2 from "aws-cdk-lib/aws-ec2";


type PrefectWorkerServiceProps = {
  cluster: ecs.ICluster,
  taskDefinition: ecs.FargateTaskDefinition,
  securityGroup: ec2.ISecurityGroup,
  subnets: ec2.ISubnet[],
  desiredCount: number,
}

export function PrefectWorkerService(scope: Construct, props: PrefectWorkerServiceProps) {
  const service = new ecs.FargateService(scope, "PrefectWorkerService", {
    cluster: props.cluster,
    desiredCount: props.desiredCount,
    taskDefinition: props.taskDefinition,
    securityGroups: [props.securityGroup],
    assignPublicIp: true,
    vpcSubnets: { subnets: props.subnets },
    minHealthyPercent: 0,
    enableExecuteCommand: true,
  })

  return service
}