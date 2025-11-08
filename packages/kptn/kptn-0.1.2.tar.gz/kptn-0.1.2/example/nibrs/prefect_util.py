from prefect import task
from tasks.task_run_name import map_wrapper_tr_name


def check_futures_success(futures) -> str:
    """Determines if all, some, or no elements in a list of futures are successful"""
    total = len(futures)
    success = sum(future.state.is_completed() for future in futures)
    if success == total:
        return "SUCCESS"
    elif success == 0:
        return "FAILURE"
    else:
        return "INCOMPLETE"

def raise_if_not_successful(futures, task_name: str):
    """Raises an error if any future in the list is not successful."""
    status = check_futures_success(futures)
    if status != "SUCCESS":
        raise RuntimeError(f"Subtasks failed for {task_name}")

@task(task_run_name=map_wrapper_tr_name)
def map_wrapper(task, group_num=0, **kwargs):
    """
    A workaround for `wait_for` not waiting
    https://github.com/PrefectHQ/prefect/issues/17772
    """
    futures = task.map(**kwargs)
    print(f"Waiting for {len(futures)} subtasks for group {group_num}")
    for future in futures:
        future.wait()
    raise_if_not_successful(futures, task_name=task.__name__)
    return futures