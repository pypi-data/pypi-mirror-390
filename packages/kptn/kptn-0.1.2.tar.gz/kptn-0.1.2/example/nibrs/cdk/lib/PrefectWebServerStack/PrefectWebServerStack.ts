import * as cdk from 'aws-cdk-lib';
import * as ec2 from "aws-cdk-lib/aws-ec2";
import * as ecs from "aws-cdk-lib/aws-ecs";
import * as sm from "aws-cdk-lib/aws-secretsmanager"
import * as ssm from "aws-cdk-lib/aws-ssm";
import { LogGroup, RetentionDays } from "aws-cdk-lib/aws-logs"
import { type NibrsepFoundationStack } from '../nibrsep-foundation-stack';
import {
  PrefectWebServerExecutionRole,
  PrefectWebServerTaskDefinition,
  PrefectFlowSecurityGroup,
  PrefectFlowExecutionRole,
  PrefectFlowTaskRole,
} from '.';
import { getSsmParameterNames } from '../util/crossStackSsmParameterNames';
import * as elbv2 from 'aws-cdk-lib/aws-elasticloadbalancingv2';
import { Duration } from 'aws-cdk-lib';

type StackProps = {
  foundation: NibrsepFoundationStack,
  devIpAllowlist: string,
} & cdk.StackProps

/**
 * Represents a stack for Prefect UI web server on ECS.
 */
export class PrefectWebServerStack extends cdk.Stack {
  public readonly prefectFlowSecurityGroup: ec2.ISecurityGroup;

  constructor(scope: cdk.App, id: string, props: StackProps) {
    super(scope, id, props);

    const ssmParams = getSsmParameterNames(process.env.STACK_NAME, process.env.RSRC_SUFFIX)
    const prefectServerSecurityGroupId = ssm.StringParameter.valueForStringParameter(
      this,
      ssmParams["PREFECT_SERVER_SG_ID"]
    )
    const ec2publicIp = ssm.StringParameter.valueForStringParameter(
      this,
      ssmParams["EC2_PUBLIC_IP"]
    )
    const prefectServerSecurityGroup = ec2.SecurityGroup.fromSecurityGroupId(
      this,
      "PrefectServerSecurityGroup",
      prefectServerSecurityGroupId
    )
    const prefectFlowSecurityGroup = PrefectFlowSecurityGroup(
      this,
      props.foundation.vpc,
      props.foundation.nibrsEfs,
      props.foundation.ecsCluster
    )
    const prefectFlowExecutionRole = PrefectFlowExecutionRole(this)
    const existingDbSecret = sm.Secret.fromSecretNameV2(
      this,
      "NibrsEstimationRdsCreds",
      "nibrs-ucr-prod"
    )
    existingDbSecret.grantRead(prefectFlowExecutionRole) // allow flow to get db access creds
    const prefectFlowTaskRole = PrefectFlowTaskRole(this)
    props.foundation.bucketExternals.grantRead(prefectFlowTaskRole)
    props.foundation.bucketArtifacts.grantReadWrite(prefectFlowTaskRole)

    const albSecurityGroup = new ec2.SecurityGroup(this, "ALBSecurityGroup", {
      vpc: props.foundation.vpc,
      allowAllOutbound: true,
    })
    new ssm.StringParameter(this, "ALBSecurityGroupId", {
      parameterName: ssmParams["ALB_SG_ID"],
      stringValue: albSecurityGroup.securityGroupId,
    })

    // Allow from any IP in the VPC
    albSecurityGroup.addIngressRule(
      ec2.Peer.ipv4(props.foundation.vpc.vpcCidrBlock),
      ec2.Port.tcp(80),
      "Allow HTTP traffic from VPC"
    )

    const lb = new elbv2.ApplicationLoadBalancer(this, 'LB', {
      vpc: props.foundation.vpc,
      internetFacing: false,
      securityGroup: albSecurityGroup,
    });
    new ssm.StringParameter(this, "ALBDnsName", {
      parameterName: ssmParams["ALB_DNS_NAME"],
      stringValue: lb.loadBalancerDnsName,
    })

    const prefectWebServerExecutionRole = PrefectWebServerExecutionRole(this)
    const prefectWebServerTaskDefinition = PrefectWebServerTaskDefinition(this, {
      externalPrefectEndpoint: ec2publicIp,
      internalPrefectEndpoint: lb.loadBalancerDnsName,
      image: ecs.ContainerImage.fromEcrRepository(props.foundation.prefectWebServerRepo, "latest"),
      taskExecutionRole: prefectWebServerExecutionRole,
      logGroup: new LogGroup(this, "PrefectWebServerLogGroup", {
        retention: RetentionDays.ONE_MONTH,
      }),
      vpcId: props.foundation.vpc.vpcId,
      flowRunSecurityGroupId: prefectFlowSecurityGroup.securityGroupId,
      privateSubnetId: props.foundation.vpc.privateSubnets[0].subnetId,
      flowTaskRole: prefectFlowTaskRole,
      flowExecutionRole: prefectFlowExecutionRole,
      flowImage: props.foundation.flowRunnerRepo,
      flowCluster: props.foundation.ecsCluster,
      efsFileSystemId: props.foundation.nibrsEfs.fileSystemId,
      existingDbSecret,
      rdsCluster: props.foundation.prefectDb,
      rdsProxy: props.foundation.prefectDbProxy,
      externalsBucket: props.foundation.bucketExternals,
      artifactBucket: props.foundation.bucketArtifacts,
    })

    const prefectService = new ecs.FargateService(this, "PrefectWebServerService", {
      cluster: props.foundation.ecsCluster,
      desiredCount: 1,
      taskDefinition: prefectWebServerTaskDefinition,
      minHealthyPercent: 0,
      maxHealthyPercent: 200,
      enableExecuteCommand: true,
      securityGroups: [prefectServerSecurityGroup],
    })
    
    const port80HttpListener = new elbv2.ApplicationListener(this, 'ALBport80HttpListener', {
      loadBalancer: lb,
      port: 80,
      protocol: elbv2.ApplicationProtocol.HTTP,
      open: false,
    });

    const target = port80HttpListener.addTargets('PrefectWebServerService', {
      port: 80,
      targets: [prefectService],
      healthCheck: {
        path: '/api/health',
        interval: Duration.seconds(30),
        timeout: Duration.seconds(10),
        unhealthyThresholdCount: 3,
      },
      deregistrationDelay: Duration.seconds(5),
    });

    const scaling = prefectService.autoScaleTaskCount({ maxCapacity: 3, minCapacity: 1 });
    scaling.scaleOnRequestCount('ScaleOnRequestCount', {
      requestsPerTarget: 30,
      targetGroup: target,
    });
  }
}
