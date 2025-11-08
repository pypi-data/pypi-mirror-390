#!/bin/bash

usage() {
    echo "usage: deploy_image_ecr.sh <stack-suffix> <imageType>"
    echo -e "    suffix: string, cdk-stack suffix - corresponds to envs/.env.<suffix>"
    echo -e "    imageType: 'authProxy', 'prefectWebServer', 'flowRunner', 'all'\n"
    echo "This script will build, tag, and upload a local image to ECR."
    echo "NOTE: This script assumes you have \$HOME/.aws/credentials with nibrs profile"
    echo "NOTE: This script is expected to be run from the ./cdk/ directory. There are hardcoded paths in this script"
}

build_and_push() {
    # Build docker image and push to an ECR.
    # This function expects the ECR registry to already be authenticated and
    # for $HOME/.aws/credentials to have a nibrs profile
    #
    # Args:
    #     uri: URI of the registry/image to push
    #     docker_dir: The directory of the Dockerfile needed to build the image
    echo "Build and pushing '$IMAGE_TYPE'"
    local uri="$1"
    local docker_dir="$2"

    if [ $IMAGE_TYPE = "prefectWebServer" ]; then
        docker build --build-arg PREFECT_IMAGE=$PREFECT_IMAGE -t $uri "$PWD/$docker_dir"
    else
        docker build -t $uri "$PWD/$docker_dir"
    fi

    docker push $uri:latest
}

# Import utils file
source ./bin/util/bash-utils.sh

# Validate correct number of arguments
if [ "$#" -ne 2 ]; then
    echo -e "Please provide exactly two arguments.\n"
    usage
    exit 1
fi

# Grab the arguements
IMAGE_TYPE="$2"
SUFFIX_IDENTIFIER="$1"

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

GIT_BRANCH=$(git branch --show-current)
GIT_HASH=$(git rev-parse HEAD)
FULL_STACK_NAME="${STACK_NAME}Foundation-${RSRC_SUFFIX}"
REGISTRY_URL="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com"

# Query Cloudformation for repository URIs
AUTH_PROXY_URI=$(get_stack_output $FULL_STACK_NAME "authProxyRepo" $AWS_DEFAULT_REGION)
PREFECT_WEB_SERVER_URI=$(get_stack_output $FULL_STACK_NAME "prefectWebServerRepo" $AWS_DEFAULT_REGION)
FLOW_RUNNER_URI=$(get_stack_output $FULL_STACK_NAME "flowRunnerRepo" $AWS_DEFAULT_REGION)

# Hardcode Docker Directories
AUTH_PROXY_DOCKER_DIR="lib/AuthProxyStack/"
PREFECT_WEB_SERVER_DOCKER_DIR="lib/PrefectWebServerStack/"
FLOW_RUNNER_DOCKER_DIR="../"

case $IMAGE_TYPE in

    "authProxy")
        echo "Building and Pushing authProxy"
        auth_docker $REGISTRY_URL $AWS_DEFAULT_REGION
        build_and_push $AUTH_PROXY_URI $AUTH_PROXY_DOCKER_DIR
        ;;

    "prefectWebServer")
        echo "Building and Pushing prefectWebServer"
        auth_docker $REGISTRY_URL $AWS_DEFAULT_REGION
        build_and_push $PREFECT_WEB_SERVER_URI $PREFECT_WEB_SERVER_DOCKER_DIR
        ;;
    
    "flowRunner")
        echo "Building and Pushing flowRunner"
        auth_docker $REGISTRY_URL $AWS_DEFAULT_REGION
        build_and_push $FLOW_RUNNER_URI $FLOW_RUNNER_DOCKER_DIR
        ;;
    
    "all")
        echo "Building and Pushing all images."
        auth_docker $REGISTRY_URL $AWS_DEFAULT_REGION
        IMAGE_TYPE="authProxy"
        build_and_push $AUTH_PROXY_URI $AUTH_PROXY_DOCKER_DIR
        IMAGE_TYPE="prefectWebServer"
        build_and_push $PREFECT_WEB_SERVER_URI $PREFECT_WEB_SERVER_DOCKER_DIR
        IMAGE_TYPE="flowRunner"
        build_and_push $FLOW_RUNNER_URI $FLOW_RUNNER_DOCKER_DIR
        ;;

    *)
        echo -e "Error: Invalid argument value for 'Image Type': $IMAGE_TYPE\n"
        usage
        exit 1
        ;;
esac
