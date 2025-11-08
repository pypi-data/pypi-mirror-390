import * as s3 from "aws-cdk-lib/aws-s3";
import { Construct } from 'constructs';

export function getOrCreateS3Bucket(scope: Construct, CDK_RESOURCE_NAME: string, BUCKET_NAME: string, RSRC_SUFFIX?: string): s3.IBucket {

  const existingBucket = s3.Bucket.fromBucketName(scope, CDK_RESOURCE_NAME, BUCKET_NAME)

  if (!existingBucket.bucketName) {
    return new s3.Bucket(scope, CDK_RESOURCE_NAME, {
      bucketName: `${BUCKET_NAME}${RSRC_SUFFIX}`,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
    })
  } else {
    return existingBucket
  }
}