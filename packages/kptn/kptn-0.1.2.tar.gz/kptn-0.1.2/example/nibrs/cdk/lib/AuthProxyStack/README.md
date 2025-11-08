# AuthProxyStack

This stack exposes an HTTP endpoint for retrieving AWS credentials for a single task role. These credentials allow Prefect users to upload code to S3. Prior to this solution, full access IAM user credentials were used.
