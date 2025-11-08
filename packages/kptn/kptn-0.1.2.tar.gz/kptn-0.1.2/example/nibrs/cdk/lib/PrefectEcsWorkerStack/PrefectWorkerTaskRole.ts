import { Construct } from 'constructs';
import * as iam from "aws-cdk-lib/aws-iam";


/**
 * Creates an IAM role for the Prefect worker task.
 * 
 * This function creates an IAM role, granting the Prefect worker task
 * (application) permissions to perform actions in AWS such as
 * creating log groups, running tasks, and stopping tasks.
 * 
 * @param scope - The construct scope.
 * @returns The IAM role for the Prefect worker task.
 */
export function PrefectWorkerTaskRole(scope: Construct) {
  const prefectWorkerTaskRole = new iam.Role(scope, "PrefectWorkerTaskRole", {
    assumedBy: new iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
    inlinePolicies: {
      "prefect-worker-allow-ecs-task": new iam.PolicyDocument({
        statements: [
          new iam.PolicyStatement({
            actions: [
              "ec2:DescribeSubnets",
              "ec2:DescribeVpcs",
              "ecr:BatchCheckLayerAvailability",
              "ecr:BatchGetImage",
              "ecr:GetAuthorizationToken",
              "ecr:GetDownloadUrlForLayer",
              "ecs:DeregisterTaskDefinition",
              "ecs:DescribeTaskDefinition",
              "ecs:DescribeTasks",
              "ecs:RegisterTaskDefinition",
              "ecs:RunTask",
              "ecs:StopTask",
              "ecs:TagResource",
              "iam:PassRole",
              "logs:CreateLogGroup",
              "logs:CreateLogStream",
              "logs:GetLogEvents",
              "logs:PutLogEvents",
            ],
            effect: iam.Effect.ALLOW,
            resources: ["*"],
          }),
        ],
      }),
    },
  })

  return prefectWorkerTaskRole
}