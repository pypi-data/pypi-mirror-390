import boto3
import requests
import schedule
import time

# Hard-coded mapping of region-suffix to aws region
# Derived from ~/cdk/envs/
REGIONS = {
    "east": "us-east-1",
    "west": "us-west-1",
}
# Slack token for posting to `nibrs-bot` channel
SLACK_WEBHOOK_URL = (
    ""
)
# AWS Access & Secret with permissions set needed to list task in a cluster
# Currently using a service account `nibrs-bot` keys
AWS_ACCESS_KEY_ID = ""
AWS_SECRET_ACCESS_KEY = ""


def get_running_tasks_count(region: str, cluster_suffix: str) -> int:
    """Get the count of running ECS tasks in the given cluster.

    Args:
        region (str): AWS region where the ECS cluster is located.
        cluster_suffix (str): Suffix used to identify the cluster.

    Returns:
        int: Number of running ECS tasks in the cluster.
    """
    cluster_name = f"nibrsep-{cluster_suffix}"
    ecs_client = boto3.client(
        "ecs",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=region,
    )
    response = ecs_client.list_tasks(
        cluster=cluster_name,
        desiredStatus="RUNNING",
    )
    return len(response.get("taskArns", []))


def post_to_slack(region: str, cluster_suffix: str, task_count: int) -> None:
    """Post ECS cluster information to Slack.

    Args:
        region (str): AWS region of the cluster.
        cluster_suffix (str): Cluster suffix used to identify the ECS cluster.
        task_count (int): Number of running tasks to report.

    Raises:
        RuntimeError: If Slack API returns a non-200 response.
    """
    cluster_name = f"nibrsep-{cluster_suffix}"
    message = f"*Region*: {region}\n*Cluster*: {cluster_name}\n*# of Tasks*: {task_count}"

    resp = requests.post(SLACK_WEBHOOK_URL, json={"text": message})
    if resp.status_code != 200:
        raise RuntimeError(f"Slack API error: {resp.status_code} {resp.text}")


def main() -> None:
    """Main script execution.

    Uses hard-coded values to: for each AWS region and cluster suffix,
    retrieve the number of running ECS tasks, and post the results to Slack.
    """
    for suffix, region in REGIONS.items():
        print(f"{suffix} in {region}")

        try:
            task_count = get_running_tasks_count(region, suffix)
            post_to_slack(region, suffix, task_count)
            print(f"Posted for {region} / nibrsep-{suffix}: {task_count} tasks")
        except Exception as e:
            print(f"Error processing {suffix}: {e}")


if __name__ == "__main__":
    # Run immediately on start
    main()

    # Schedule to run every day at noon
    schedule.every().day.at("00:00").do(main)
    schedule.every().day.at("12:00").do(main)

    while True:
        schedule.run_pending()
        time.sleep(1800)
