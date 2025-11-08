import { Construct } from "constructs";
import * as ecs from "aws-cdk-lib/aws-ecs";
import * as ecr from "aws-cdk-lib/aws-ecr";
import * as iam from "aws-cdk-lib/aws-iam";
import * as logs from "aws-cdk-lib/aws-logs";
import * as rds from "aws-cdk-lib/aws-rds";
import * as s3 from "aws-cdk-lib/aws-s3";
import * as sm from "aws-cdk-lib/aws-secretsmanager"
import { __dirname } from "../util/node"

/**
 * This file contains the task definition for the Prefect Web Server.
 * which is a custom Dockerfile that creates a work pool with a JSON template.
 * This file sets environment variables used by the template.
 */

type PrefectWebServerTaskDefinitionProps = {
  externalPrefectEndpoint: string,
  internalPrefectEndpoint: string,
  image: ecs.ContainerImage,
  taskExecutionRole: iam.IRole,
  logGroup: logs.ILogGroup,
  vpcId: string,
  flowRunSecurityGroupId: string,
  privateSubnetId: string,
  flowTaskRole: iam.IRole,
  flowExecutionRole: iam.IRole,
  flowImage: ecr.IRepository,
  flowCluster: ecs.ICluster,
  efsFileSystemId: string,
  existingDbSecret: sm.ISecret,
  rdsCluster: rds.DatabaseCluster,
  rdsProxy: rds.DatabaseProxy,
  artifactBucket: s3.IBucket;
  externalsBucket: s3.IBucket;
}

export function PrefectWebServerTaskDefinition(scope: Construct, props: PrefectWebServerTaskDefinitionProps) {
  const taskDefinition = new ecs.FargateTaskDefinition(scope, "PrefectWebServerTaskDefinition", {
    cpu: 1024,
    memoryLimitMiB: 2048,
    taskRole: props.flowTaskRole,
    executionRole: props.taskExecutionRole,
  })

  const webServerContainer = taskDefinition.addContainer("PrefectWebServer", {
    image: props.image,
    portMappings: [{ containerPort: 4200 }],
    secrets: {
      PREFECT_DB_USER: ecs.Secret.fromSecretsManager(props.rdsCluster.secret!, "username"),
      PREFECT_DB_PASS: ecs.Secret.fromSecretsManager(props.rdsCluster.secret!, "password"),
      // PREFECT_DB_HOST: ecs.Secret.fromSecretsManager(props.rdsCluster.secret!, "host"),
      PREFECT_DB_PORT: ecs.Secret.fromSecretsManager(props.rdsCluster.secret!, "port"),
      PREFECT_DB_DBNAME: ecs.Secret.fromSecretsManager(props.rdsCluster.secret!, "dbname"),
    },
    environment: {
      AWS_EC2_EIP: props.externalPrefectEndpoint,
      AWS_CONTAINER_CREDENTIALS_FULL_URI: "http://localhost:51678",
      PREFECT_API_MAX_FLOW_RUN_GRAPH_NODES: "1",
      PREFECT_API_MAX_FLOW_RUN_GRAPH_ARTIFACTS: "1",
      PREFECT_SQLALCHEMY_POOL_SIZE: "10",
      PREFECT_SQLALCHEMY_MAX_OVERFLOW: "500",
      PREFECT_API_DATABASE_TIMEOUT: "60",
      PREFECT_API_DATABASE_CONNECTION_TIMEOUT: "60",
      PREFECT_API_REQUEST_TIMEOUT: "300",
      PREFECT_API_ENABLE_HTTP2: "false",
      PREFECT_DB_HOST: props.rdsProxy.endpoint,
      // All below are for the work pool, what the flow run will use
      PREFECT_TASK_START_TIMEOUT_SECONDS: "300",
      PREFECT_TASK_WATCH_POLL_INTERVAL: "30",
      DASK_DISTRIBUTED__COMM__TIMEOUTS__CONNECT: "60s",
      DASK_DISTRIBUTED__COMM__RETRY__COUNT: "3",
      PREFECT_TASK_MEMORY: "30720",
      PREFECT_TASK_CPU: "4096",
      WORK_POOL_NAME: "ecs-pool",
      FLOW_VPC_ID: props.vpcId,
      FLOW_SECURITY_GROUP_ID: props.flowRunSecurityGroupId,
      FLOW_PRIVATE_SUBNET_ID: props.privateSubnetId,
      FLOW_TASK_ROLE_ARN: props.flowTaskRole.roleArn,
      FLOW_EXECUTION_ROLE_ARN: props.flowExecutionRole.roleArn,
      FLOW_IMAGE: props.flowImage.repositoryUri,
      FLOW_VOLUMES: JSON.stringify([
        {
          "name": "efs-nibrs",
          "efsVolumeConfiguration": {
            "fileSystemId": props.efsFileSystemId,
          }
        },
      ]),
      FLOW_MOUNTPOINTS: JSON.stringify([
        {
          "sourceVolume": "efs-nibrs",
          "containerPath": "/data",
          "readOnly": false
        }
      ]),
      FLOW_ENV: JSON.stringify([
        { name: "IS_NEW_CDK", value: "1" },
        { name: "IS_PROD", value: "1" },
        { name: "CHARGE_CODE", value: process.env.PROJECT_NUMBER },
        { name: "SCRATCH_DIR", value: "/data" },
        { name: "EXTERNAL_STORE", value: `s3://${props.externalsBucket.bucketName}` },
        { name: "ARTIFACT_STORE", value: `s3://${props.artifactBucket.bucketName}` },
        { name: "WORKING_DIR", value: "~/nibrs-estimation" },
        { name: "PGDATABASE", value: "ucr_prd" },
        { name: "AWS_REGION", value: process.env.AWS_DEFAULT_REGION },
        { name: "EXECUTION_ROLE_ARN", value: props.flowExecutionRole.roleArn },
        { name: "TASK_ROLE_ARN", value: props.flowTaskRole.roleArn },
        { name: "AWS_EFS_ID", value: props.efsFileSystemId },
        { name: "AWS_LOGGROUP", value: props.logGroup.logGroupName },
        { name: "AWS_VPC", value: props.vpcId },
        { name: "AWS_SUBNET", value: props.privateSubnetId },
        { name: "AWS_SECURITY_GROUP", value: props.flowRunSecurityGroupId },
        { name: "ECS_CLUSTER", value: props.flowCluster.clusterName },
        { name: "AWS_CLUSTER_ARN", value: props.flowCluster.clusterArn },
        { name: "AWS_EC2_EIP", value: props.internalPrefectEndpoint },
        { name: "REGISTRY_URI", value: props.flowImage.repositoryUri }
      ]),
      FLOW_SECRETS: JSON.stringify([{
        name: "PGUSER",
        valueFrom: `${props.existingDbSecret.secretArn}:username::`,
      }, {
        name: "PGPASSWORD",
        valueFrom: `${props.existingDbSecret.secretArn}:password::`,
      }, {
        name: "PGHOST",
        valueFrom: `${props.existingDbSecret.secretArn}:host::`,
      }, {
        name: "PGPORT",
        valueFrom: `${props.existingDbSecret.secretArn}:port::`,
      }]),
      FLOW_CLUSTER: props.flowCluster.clusterName,
    },
    logging: ecs.LogDrivers.awsLogs({
      logGroup: props.logGroup,
      streamPrefix: "prefect-server",
    }),
  })

  return taskDefinition
}