import { Construct } from 'constructs';
import * as iam from "aws-cdk-lib/aws-iam";

export function AuthProxyExecutionRole(scope: Construct) {  
  const authProxyExecutionRole = new iam.Role(scope, "authProxyTaskRoleExecutionRole", {
    assumedBy: new iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
    managedPolicies: [
      iam.ManagedPolicy.fromAwsManagedPolicyName("service-role/AmazonECSTaskExecutionRolePolicy"),
    ]
  })

  return authProxyExecutionRole
}