#!/bin/bash

get_stack_output() {
    # Attempt to fetch CDK output keys from a cloudformation stack
    # and return its value. It expects three arguments: stack_name, output_key, region
    #
    # Args:
    #     stack_name: name of the CDK stack to search for an output_key
    #     output_key: key to search for and return its value
    #     region: aws region where stack exists
    # Returns:
    #     output_value: output value of the output_key

    local stack_name="$1"
    local output_key="$2"
    local region="$3"

    # Use AWS CLI to describe the stack
    local output=$(aws cloudformation describe-stacks \
        --region "$region" \
        --profile "nibrs" \
        --stack-name "$stack_name" \
        --query "Stacks[0].Outputs[?OutputKey=='$output_key'].OutputValue" \
        --output text)

    # Check if output is empty
    if [ -z "$output" ]; then
        echo "Error: Output key '$output_key' not found in stack '$stack_name' in region '$region'."
        exit 1
    else
        echo "$output"
    fi
}

auth_docker() {
    # Authenticates with an ECR repository.
    # This function expects AWS_ACCESS_KEY_ID & AWS_SECRET_ACCESS_KEY to be set in the environment
    #
    # Args:
    #     registry_url: The url of the registry to authenticate with
    #     ecr_region: aws region where ecr exists
    local registry_url="$1"
    local ecr_region="$2"

    echo "Authenticating: $registry_url"
    aws ecr get-login-password --profile nibrs --region $ecr_region | docker login --username AWS --password-stdin $registry_url
}