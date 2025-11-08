import * as cdk from 'aws-cdk-lib';
import * as ecs from "aws-cdk-lib/aws-ecs";
import * as ec2 from "aws-cdk-lib/aws-ec2";
import * as ssm from "aws-cdk-lib/aws-ssm";
import { type NibrsepFoundationStack } from '../nibrsep-foundation-stack';
import {
  PrefectWorkerExecutionRole,
  PrefectWorkerTaskRole,
  PrefectWorkerLogGroup,
  PrefectWorkerTaskDefinition,
} from '.';
import { getSsmParameterNames } from '../util/crossStackSsmParameterNames';

type StackProps = {
  foundation: NibrsepFoundationStack,
} & cdk.StackProps

/**
 * Represents a stack for Prefect ECS worker.
 */
export class PrefectEcsWorkerStack extends cdk.Stack {
  constructor(scope: cdk.App, id: string, props: StackProps) {
    super(scope, id, props);
    const securityGroup = new ec2.SecurityGroup(this, "PrefectWorkerSecurityGroup", {
      vpc: props.foundation.vpc,
      allowAllOutbound: true,
    })
    securityGroup.connections.allowTo(props.foundation.ecsCluster, ec2.Port.tcp(4200), "Allow access to Prefect Web Server")
    const prefectWorkerExecutionRole = PrefectWorkerExecutionRole(this)
    const prefectWorkerTaskRole = PrefectWorkerTaskRole(this)
    const prefectWorkerLogGroup = PrefectWorkerLogGroup(this)
    // Retrieve private IP address of the EC2 instance
    let ssmIPS = getSsmParameterNames(process.env.STACK_NAME, process.env.RSRC_SUFFIX)
    const prefectEndpoint = ssm.StringParameter.valueForStringParameter(
      this,
      ssmIPS["ALB_DNS_NAME"]
    )
    const prefectWorkerTaskDefinition = PrefectWorkerTaskDefinition(this, {
      prefectEndpoint,
      taskRole: prefectWorkerTaskRole,
      taskExecutionRole: prefectWorkerExecutionRole,
      logGroup: prefectWorkerLogGroup,
    })
    new ecs.FargateService(this, "PrefectWorkerService", {
      cluster: props.foundation.ecsCluster,
      desiredCount: 1,
      securityGroups: [securityGroup],
      taskDefinition: prefectWorkerTaskDefinition,
      assignPublicIp: false,
      vpcSubnets: { subnets: props.foundation.vpc.privateSubnets },
      minHealthyPercent: 0,
      enableExecuteCommand: true,
    })

    const albSecurityGroupId = ssm.StringParameter.valueForStringParameter(
      this,
      ssmIPS["ALB_SG_ID"]
    )
    const albSecurityGroup = ec2.SecurityGroup.fromSecurityGroupId(
      this,
      "albSecurityGroup",
      albSecurityGroupId
    )
    // Allow Worker to access the ALB
    albSecurityGroup.addIngressRule(
      securityGroup,
      ec2.Port.tcp(80),
      "Allow HTTP traffic from the Worker"
    )
  }
}
