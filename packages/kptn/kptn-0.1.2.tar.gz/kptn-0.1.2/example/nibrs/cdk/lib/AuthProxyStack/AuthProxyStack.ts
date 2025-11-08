import * as cdk from 'aws-cdk-lib';
import * as ecs from "aws-cdk-lib/aws-ecs";
import * as ssm from "aws-cdk-lib/aws-ssm";
import { LogGroup, RetentionDays } from "aws-cdk-lib/aws-logs"
import { type NibrsepFoundationStack } from '../nibrsep-foundation-stack';
import { AuthProxyExecutionRole } from './AuthProxyExecutionRole';
import { AuthProxyTaskRole } from './AuthProxyTaskRole';
import { __dirname } from '../util/node'
import { getSsmParameterNames } from '../util/crossStackSsmParameterNames';

type StackProps = {
  foundation: NibrsepFoundationStack,
} & cdk.StackProps

/**
 * Represents a stack for the AuthProxy ECS service.
 */
export class AuthProxyStack extends cdk.Stack {
  constructor(scope: cdk.App, id: string, props: StackProps) {
    super(scope, id, props);

    const ssmIPS = getSsmParameterNames(process.env.STACK_NAME, process.env.RSRC_SUFFIX)
    const prefectEndpoint = ssm.StringParameter.valueForStringParameter(
      this,
      ssmIPS["ALB_DNS_NAME"]
    )
    const taskRole = AuthProxyTaskRole(this)
    const executionRole = AuthProxyExecutionRole(this)

    const authProxyTaskDefinition = new ecs.Ec2TaskDefinition(this, "AuthProxyTaskDefinition", {
      networkMode: ecs.NetworkMode.HOST,
      taskRole,
      executionRole
    })

    authProxyTaskDefinition.addContainer("nginx", {
      memoryReservationMiB: 1024,
      image: ecs.ContainerImage.fromEcrRepository(props.foundation.authProxyRepo, "latest"),
      environment: {
        // AWS_CONTAINER_CREDENTIALS_RELATIVE_URI: "/get-credentials",
        S3_ARTIFACTS_BUCKET_NAME: props.foundation.bucketArtifacts.bucketName,
        S3_EXTERNALS_BUCKET_NAME: props.foundation.bucketExternals.bucketName,
        ECR_FLOW_RUNNER_REPO: props.foundation.flowRunnerRepo.repositoryUri,
        AWS_REGION: process.env.AWS_DEFAULT_REGION!,
        PREFECT_ENDPOINT: prefectEndpoint,
      },
      logging: ecs.LogDrivers.awsLogs({
        logGroup: new LogGroup(this, "AuthProxyLogGroup", {
          retention: RetentionDays.ONE_MONTH,
        }),
        streamPrefix: "authproxy",
      }),
    })

    const authProxyService = new ecs.Ec2Service(this, "AuthProxyService", {
      cluster: props.foundation.ecsCluster,
      desiredCount: 1,
      taskDefinition: authProxyTaskDefinition,
      minHealthyPercent: 0,
      maxHealthyPercent: 100,
      enableExecuteCommand: true,
    })
  }
}
