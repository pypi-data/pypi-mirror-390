import { Construct } from 'constructs';
import * as iam from "aws-cdk-lib/aws-iam";


/**
 * Creates an IAM role for the Prefect web server.
 * 
 * This function creates an IAM role, granting the Prefect web server
 * task (application) permissions to perform actions in AWS such as
 * 
 * @param scope - The construct scope.
 * @returns The IAM role for the Prefect web server task.
 */
export function AuthProxyTaskRole(scope: Construct) {
  const authProxyTaskRole = new iam.Role(scope, "AuthProxyTaskRole", {
    assumedBy: new iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
    inlinePolicies: {
      "authproxy-allow-s3": new iam.PolicyDocument({
        statements: [
          new iam.PolicyStatement({
            actions: [
              // S3
              "s3:GetObject",
              "s3:ListBucket",
              "s3:PutObject",
              "s3:DeleteObject",
            ],
            effect: iam.Effect.ALLOW,
            // TODO: Replace with the ARN of the S3 bucket created by FoundationStack
            // Also, 2nd policy statement, read-access for EXTERNALS_BUCKET_NAME
            resources: ["arn:aws:s3:::*"],
          }),
        ],
      }),
      "authproxy-allow-ecr": new iam.PolicyDocument({
        statements: [
          new iam.PolicyStatement({
            actions: [
              // ECR
              "ecr:GetAuthorizationToken",
              "ecr:BatchCheckLayerAvailability",
              "ecr:GetDownloadUrlForLayer",
              "ecr:BatchGetImage",
              "ecr:InitiateLayerUpload",
              "ecr:UploadLayerPart",
              "ecr:CompleteLayerUpload",
              "ecr:PutImage",
            ],
            effect: iam.Effect.ALLOW,
            // TODO: Replace with the ARN of the FlowRunner ECR repository created by FoundationStack
            resources: ["*"],
          }),
        ],
      }),
    },
  })

  return authProxyTaskRole
}