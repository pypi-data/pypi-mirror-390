import { Construct } from 'constructs';
import * as iam from "aws-cdk-lib/aws-iam";

export function PrefectWebServerExecutionRole(scope: Construct) {  
  const prefectWebServerExecutionRole = new iam.Role(scope, "PrefectWebServerExecutionRole", {
    assumedBy: new iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
    managedPolicies: [
      iam.ManagedPolicy.fromAwsManagedPolicyName("service-role/AmazonECSTaskExecutionRolePolicy"),
    ]
  })

  return prefectWebServerExecutionRole
}