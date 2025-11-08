import { Construct } from 'constructs';
import * as iam from "aws-cdk-lib/aws-iam";

export function PrefectFlowTaskRole(scope: Construct) {  
  const prefectFlowTaskRole = new iam.Role(scope, "PrefectFlowTaskRole", {
    assumedBy: new iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
    inlinePolicies: {
        "dask-policy": new iam.PolicyDocument({
          statements: [
            new iam.PolicyStatement({
              actions: [
                "ec2:CreateTags",
                "ec2:DescribeInstances",
                "ec2:DescribeNetworkInterfaces",
                "ec2:DescribeSecurityGroups",
                "ec2:DescribeVpcs",
                "ecs:DescribeTasks",
                "ecs:ListAccountSettings",
                "ecs:RegisterTaskDefinition",
                "ecs:RunTask",
                "ecs:StopTask",
                "ecs:ListClusters",
                "ecs:DescribeClusters",
                "ecs:ListTaskDefinitions",
                "ecs:DescribeTaskDefinition",
                "ecs:DeregisterTaskDefinition",
                "ecs:TagResource",
                "iam:PassRole",
                "iam:ListRoles",
                "iam:ListRoleTags",
                "logs:DescribeLogGroups",
                "logs:GetLogEvents"
              ],
              effect: iam.Effect.ALLOW,
              resources: ["*"],
            }),
          ],
        }),
      },
  })

  return prefectFlowTaskRole
}
