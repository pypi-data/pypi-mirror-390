import { Construct } from 'constructs';
import * as ecs from "aws-cdk-lib/aws-ecs";
import * as iam from "aws-cdk-lib/aws-iam";
import * as logs from "aws-cdk-lib/aws-logs";


type PrefectWorkerTaskDefinitionProps = {
  prefectEndpoint: string,
  taskRole: iam.IRole,
  taskExecutionRole: iam.IRole,
  logGroup: logs.ILogGroup,
}

export function PrefectWorkerTaskDefinition(scope: Construct, props: PrefectWorkerTaskDefinitionProps) {
  const env = {
    WORKER_CPU: process.env.WORKER_CPU || "256",
    WORKER_MEMORY: process.env.WORKER_MEMORY || "512",
    WORK_POOL_NAME: process.env.WORK_POOL_NAME || "ecs-pool",
    WORKER_IMAGE: process.env.PREFECT_IMAGE!,
    EXTRA_PIP_PACKAGES: process.env.EXTRA_PIP_PACKAGES || "prefect[aws]==3.2.12"
  }
  const taskDefinition = new ecs.FargateTaskDefinition(scope, "PrefectWorkerTaskDefinition", {
    cpu: parseInt(env.WORKER_CPU!),
    memoryLimitMiB: parseInt(env.WORKER_MEMORY!),
    taskRole: props.taskRole,
    executionRole: props.taskExecutionRole,
  })

  const container = taskDefinition.addContainer("PrefectWorker", {
    image: ecs.ContainerImage.fromRegistry(env.WORKER_IMAGE),
    command: ["prefect", "worker", "start", "-p", env.WORK_POOL_NAME!, "--type", "ecs"],
    environment: {
      PREFECT_API_URL: `http://${props.prefectEndpoint}/api`,
      EXTRA_PIP_PACKAGES: env.EXTRA_PIP_PACKAGES!,
      AWS_MAX_ATTEMPTS: "10",
      AWS_RETRY_MODE: "adaptive",
    },
    logging: ecs.LogDrivers.awsLogs({
      logGroup: props.logGroup,
      streamPrefix: "prefect-worker",
    }),
  })

  return taskDefinition
}