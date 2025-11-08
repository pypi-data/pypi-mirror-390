# image is alpine
# This script uses sed to swap in the environment variables into the nginx.conf file
# env: ECS_CREDS_PATH
# env: S3_ARTIFACTS_BUCKET_NAME
# env: S3_EXTERNALS_BUCKET_NAME

# Set the ECS credentials path
sed -i "s|ECS_CREDS_PATH|${AWS_CONTAINER_CREDENTIALS_RELATIVE_URI}|g" /etc/nginx/nginx.conf

# Set the S3 bucket name
sed -i "s|S3_ARTIFACTS_BUCKET_NAME|${S3_ARTIFACTS_BUCKET_NAME}|g" /etc/nginx/nginx.conf
sed -i "s|S3_EXTERNALS_BUCKET_NAME|${S3_EXTERNALS_BUCKET_NAME}|g" /etc/nginx/nginx.conf

# Set the ECR repository name and region
sed -i "s|ECR_FLOW_RUNNER_REPO|${ECR_FLOW_RUNNER_REPO}|g" /etc/nginx/nginx.conf
sed -i "s|AWS_REGION|${AWS_REGION}|g" /etc/nginx/nginx.conf

# Set the Prefect endpoint (load balancer)
sed -i "s|PREFECT_ENDPOINT|${PREFECT_ENDPOINT}|g" /etc/nginx/nginx.conf