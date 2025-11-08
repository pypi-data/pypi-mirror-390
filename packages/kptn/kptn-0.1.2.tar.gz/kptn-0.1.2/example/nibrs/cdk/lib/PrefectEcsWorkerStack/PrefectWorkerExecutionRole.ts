import { Construct } from 'constructs';
import * as iam from "aws-cdk-lib/aws-iam";

/**
 * Creates an IAM role for Prefect worker execution.
 * 
 * This function creates an IAM role that can be used by Prefect workers to execute tasks in an ECS cluster.
 * The role is assumed by the `ecs-tasks.amazonaws.com` service principal and includes the `AmazonECSTaskExecutionRolePolicy`
 * managed policy. Additionally, it allows the role to create log groups in CloudWatch Logs.
 * 
 * @param scope - The construct scope.
 * @returns The created IAM role for Prefect worker execution.
 */
export function PrefectWorkerExecutionRole(scope: Construct) {  
  const prefectWorkerExecutionRole = new iam.Role(scope, "PrefectWorkerExecutionRole", {
    assumedBy: new iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
    managedPolicies: [
      iam.ManagedPolicy.fromAwsManagedPolicyName("service-role/AmazonECSTaskExecutionRolePolicy"),
    ],
    inlinePolicies: {
      "logs-allow-create-log-group": new iam.PolicyDocument({
        statements: [
          new iam.PolicyStatement({
            actions: ["logs:CreateLogGroup"],
            effect: iam.Effect.ALLOW,
            resources: ["*"],
          }),
        ],
      }),
    },
  })

  return prefectWorkerExecutionRole
}