echo "Waiting for the Prefect server to be ready..."
while ! prefect work-pool ls; do
    sleep 1
done
echo "Prefect server is ready"

# Check if work pool exists
if [[ -z "$(prefect work-pool ls | grep $WORK_POOL_NAME)" ]]; then
    echo "Creating work pool $WORK_POOL_NAME"
    prefect work-pool create --type ecs --base-job-template /opt/prefect/ecs-work-pool-template.json $WORK_POOL_NAME
else
    echo "Updating work pool $WORK_POOL_NAME"
    prefect work-pool update --base-job-template /opt/prefect/ecs-work-pool-template.json $WORK_POOL_NAME
fi