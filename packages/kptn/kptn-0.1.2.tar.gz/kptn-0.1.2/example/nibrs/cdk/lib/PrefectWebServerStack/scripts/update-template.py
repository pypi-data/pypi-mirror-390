# Update "variables" field in JSON file with environment variables
import json
import os

JSON_FILE = "/opt/prefect/ecs-work-pool-template.json"
with open(JSON_FILE, "r") as f:
    data = json.load(f)
    data["variables"]["properties"]["vpc_id"]["default"] = os.environ["FLOW_VPC_ID"]
    data["variables"]["properties"]["network_configuration"]["default"] = {
        "assignPublicIp": "DISABLED",
        "subnets": [os.environ["FLOW_PRIVATE_SUBNET_ID"]],
        "securityGroups": [os.environ["FLOW_SECURITY_GROUP_ID"]],
    }
    data["variables"]["properties"]["task_role_arn"]["default"] = os.environ[
        "FLOW_TASK_ROLE_ARN"
    ]
    data["variables"]["properties"]["execution_role_arn"]["default"] = os.environ[
        "FLOW_EXECUTION_ROLE_ARN"
    ]
    data["variables"]["properties"]["image"]["default"] = os.environ["FLOW_IMAGE"]
    data["variables"]["properties"]["container_env"]["default"] = json.loads(
        os.environ["FLOW_ENV"]
    )
    data["variables"]["properties"]["secrets"]["default"] = json.loads(
        os.environ["FLOW_SECRETS"]
    )
    data["variables"]["properties"]["volumes"]["default"] = json.loads(
        os.environ["FLOW_VOLUMES"]
    )
    data["variables"]["properties"]["mountPoints"]["default"] = json.loads(
        os.environ["FLOW_MOUNTPOINTS"]
    )
    data["variables"]["properties"]["cluster"]["default"] = os.environ["FLOW_CLUSTER"]
    data["variables"]["properties"]["task_start_timeout_seconds"]["default"] = (
        os.environ["PREFECT_TASK_START_TIMEOUT_SECONDS"]
    )
    data["variables"]["properties"]["task_watch_poll_interval"]["default"] = os.environ[
        "PREFECT_TASK_WATCH_POLL_INTERVAL"
    ]
    data["variables"]["properties"]["memory"]["default"] = int(
        os.environ["PREFECT_TASK_MEMORY"]
    )
    data["variables"]["properties"]["cpu"]["default"] = int(
        os.environ["PREFECT_TASK_CPU"]
    )

with open(JSON_FILE, "w") as f:
    json.dump(data, f, indent=4)
