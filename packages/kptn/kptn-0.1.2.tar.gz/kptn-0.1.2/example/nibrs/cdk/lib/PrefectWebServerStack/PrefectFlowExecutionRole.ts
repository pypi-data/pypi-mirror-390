import { Construct } from 'constructs';
import * as iam from "aws-cdk-lib/aws-iam";

export function PrefectFlowExecutionRole(scope: Construct) {  
  const prefectFlowExecutionRole = new iam.Role(scope, "PrefectFlowExecutionRole", {
    assumedBy: new iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
    managedPolicies: [
      iam.ManagedPolicy.fromAwsManagedPolicyName("service-role/AmazonECSTaskExecutionRolePolicy"),
    ]
  })

  return prefectFlowExecutionRole
}