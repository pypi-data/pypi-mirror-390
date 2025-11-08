import os
import sys
from pathlib import Path

import pytest
from prefect import flow, task
from prefect.runtime import flow_run, task_run  # noqa: F401
from prefect.testing.utilities import prefect_test_harness

# Add the root directory to the sys.path so we can import from subflows.py
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from subflows import flow_run_all_groups  # noqa: E402


@pytest.fixture(autouse=True, scope="session")
def prefect_test_fixture():
    with prefect_test_harness():
        yield


def generate_task_run_name():
    return f"{task_run.task_name}-{task_run.parameters['combo']}"


@task(task_run_name=generate_task_run_name)
def my_task(
    scratch_dir: Path,
    year: int,
    external_dir: Path,
    combo: list,
) -> None:
    print(f"Running my_task {combo}")


@flow
def my_flow():
    # Call subflow
    flow_run_all_groups.with_options(flow_run_name=my_task.__name__)(
        scratch_dir=Path("/tmp"),
        external_mirror=Path("/tmp"),
        year=2025,
        task_function=my_task,
        combo_arg_name="combo",
        all_groups_file=Path(__file__).parent / "mock_groups.json",
        first_group=1,
    )


def test_flow_run_all_groups():
    assert my_flow() == 42
