#!/bin/bash

usage() {
    echo "usage: seed-prefect-deployments.sh <stack-suffix> <deployment-name> <flow-entrypoint>"
    echo -e "    suffix: string, cdk-stack suffix - corresponds to envs/.env.<suffix>"
    echo -e "    deployment-name: string, name to give deployment in prefect-ui"
    echo -e "    flow-entrypoint: string, (eg. flows.py:flow_smoketest)\n"
    echo "This script will start a docker container in the prefect container and create a"
    echo "deployment in the prefect-ui for the supplied flow."
    echo "NOTE: This script assumes you have \$HOME/.aws/credentials with nibrs profile"
    echo "NOTE: This script is expected to be run from the ./cdk/ directory. There are hardcoded paths in this script"
}

# Import utils file
source ./bin/util/bash-utils.sh

# Validate correct number of arguments
if [ "$#" -ne 3 ]; then
    echo -e "Please provide exactly three arguments.\n"
    usage
    exit 1
fi

# Grab the arguements
SUFFIX_IDENTIFIER="$1"
DEPLOYMENT_NAME="$2"
FLOW_ENTRYPOINT="$3"

# Load environment based on provided stack-suffix
if [ ! -f "envs/.env.$SUFFIX_IDENTIFIER" ]; then
    echo "Unable to find envs/.env.$SUFFIX_IDENTIFIER, check provided stack-suffix $SUFFIX_IDENTIFIER"
    usage
    exit 1
else
    echo "Using envs/.env.$SUFFIX_IDENTIFIER"
    source envs/.env.base
    source envs/.env.$SUFFIX_IDENTIFIER
fi

# Get the EIP to set PREFECT_API_URL
FOUNDATION_STACK_NAME="${STACK_NAME}Foundation-${RSRC_SUFFIX}"
EIP=$(get_stack_output $FOUNDATION_STACK_NAME "ec2publicIp" $AWS_DEFAULT_REGION)
PREFECT_API_URL="http://$EIP/api"
REGISTRY_URL="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com"

# Get the image_uri so we can run a command in a flowRunner container
FLOW_RUNNER_URI=$(get_stack_output $FOUNDATION_STACK_NAME "flowRunnerRepo" $AWS_DEFAULT_REGION)

# Build the artifact & external store paths assuming we are using s3
ARTIFACT_STORE="s3://$ARTIFACTS_BUCKET_NAME"
EXTERNAL_STORE="s3://$EXTERNALS_BUCKET_NAME"

auth_docker $REGISTRY_URL $AWS_DEFAULT_REGION

echo "Starting docker container: $FLOW_RUNNER_URI"

# The stores here are required due to the way deployments work in prefect.
# We must have the source of the flow and prefect attempts to import the flow entrypoint file.
# Our flow entrypoint file sets our store at the top-level so it gets executed on import.
# I do not think that the values here actually matter since the values are
# loaded at run time in the workers using the worker's environment variables
docker run --rm \
    -e PREFECT_API_URL=$PREFECT_API_URL \
    -e EXTERNAL_STORE=$EXTERNAL_STORE \
    -e ARTIFACT_STORE=$ARTIFACT_STORE \
    $FLOW_RUNNER_URI \
    prefect deploy -n $DEPLOYMENT_NAME --pool ecs-pool $FLOW_ENTRYPOINT
