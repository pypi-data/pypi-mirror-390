import os
from typing import Any, Dict

from prefect.task_runners import ConcurrentTaskRunner
from prefect_dask.task_runners import DaskTaskRunner  # type: ignore

# Define this variable globally so that it can be imported by other files.
# (For example, we import it in a task that saves its value to the log.)
MAX_WORKERS = 50
OVERWRITE_SUCCESS = False
GROUP_SIZE = 500
ESTIMATES_DB_NAME = "temp_test_estimates_db"

# If this is true then copula step2 will pause after the first section (of step 2) so the validation reports can be reviewed
# NOTE: if this is run with stop_after_part1=True then you will need to rerun these combinations
STOP_COPULA_AFTER_PART1 = False


def load_custom_flow_params() -> Dict[str, Any]:
    # In DEV/CI 'IS_PROD' is not set so this will evaluate to False
    # In production we can set this environment variable to anything
    # to trigger our production settings

    if os.getenv("IS_PROD", False):
        EFS_MOUNT_POINT = {
            "sourceVolume": "efs-nibrs",
            "containerPath": "/data",
            "readOnly": False,
        }
        EFS_VOLUME = {
            "name": "efs-nibrs",
            "efsVolumeConfiguration": {
                "fileSystemId": os.environ["AWS_EFS_ID"],
            },
        }

        PROD_ENVS = {
            "IS_PROD": "1",
            "AWS_EFS_ID": os.environ["AWS_EFS_ID"],
            "AWS_LOGGROUP": os.environ["AWS_LOGGROUP"],
            "AWS_REGION": os.environ["AWS_REGION"],
            "ECS_CLUSTER": os.environ["ECS_CLUSTER"],
            "AWS_VPC": os.environ["AWS_VPC"],
            "AWS_SUBNET": os.environ["AWS_SUBNET"],
            "AWS_SECURITY_GROUP": os.environ["AWS_SECURITY_GROUP"],
            "AWS_CLUSTER_ARN": os.environ["AWS_CLUSTER_ARN"],
            "CHARGE_CODE": os.environ["CHARGE_CODE"],
            "PGHOST": os.environ["PGHOST"],
            "PGPORT": os.environ["PGPORT"],
            "PGUSER": os.environ["PGUSER"],
            "PGPASSWORD": os.environ["PGPASSWORD"],
            "PGDATABASE": os.environ["PGDATABASE"],
            "AWS_EC2_EIP": os.environ["AWS_EC2_EIP"],
            "EXTERNAL_STORE": os.environ["EXTERNAL_STORE"],
            "ARTIFACT_STORE": os.environ["ARTIFACT_STORE"],
            "SCRATCH_DIR": os.environ["SCRATCH_DIR"],
            "WORKING_DIR": os.environ["WORKING_DIR"],
            "PREFECT__CLOUD__HEARTBEAT_MODE": "thread",
            "DASK_DISTRIBUTED__COMM__TIMEOUTS__CONNECT": "60s",
            "DASK_DISTRIBUTED__COMM__RETRY__COUNT": "3",
            "GIT_BRANCH": os.getenv(
                "GIT_BRANCH", ""
            ),  # optional, used only for logging
            "GIT_HASH": os.getenv("GIT_HASH", ""),  # optional, used only for logging
        }

        TASK_ROLE_ARN = os.environ["TASK_ROLE_ARN"]
        EXECUTION_ROLE_ARN = os.environ["EXECUTION_ROLE_ARN"]
        REGISTRY_URI = os.environ["REGISTRY_URI"]

        PROD_ENVS.update(
            {
                "EXECUTION_ROLE_ARN": EXECUTION_ROLE_ARN,
                "TASK_ROLE_ARN": TASK_ROLE_ARN,
                "REGISTRY_URI": REGISTRY_URI,
            }
        )

        task_runner = DaskTaskRunner(
            cluster_class="dask_cloudprovider.aws.FargateCluster",
            cluster_kwargs={
                "image": f"{REGISTRY_URI}:latest",
                "vpc": os.environ["AWS_VPC"],
                "subnets": [os.environ["AWS_SUBNET"]],
                "security_groups": [os.environ["AWS_SECURITY_GROUP"]],
                "execution_role_arn": EXECUTION_ROLE_ARN,
                "task_role_arn": TASK_ROLE_ARN,
                "cluster_arn": os.environ["AWS_CLUSTER_ARN"],
                "fargate_use_private_ip": True,
                "environment": PROD_ENVS,
                "mount_points": [EFS_MOUNT_POINT],
                "volumes": [EFS_VOLUME],
                "cloudwatch_logs_group": os.environ["AWS_LOGGROUP"],
                "worker_nthreads": 1,
                "worker_cpu": 4096,
                "worker_mem": 30720,
                "scheduler_mem": 30720,
                "scheduler_cpu": 4096,
                "scheduler_timeout": "15 minutes",
                "tags": {"project-number": os.environ.get("CHARGE_CODE", "")},
            },
            adapt_kwargs={"maximum": MAX_WORKERS},
        )

        return {"task_runner": task_runner}

    return {"task_runner": ConcurrentTaskRunner}
