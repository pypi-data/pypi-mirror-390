import os
from pathlib import Path
from typing import Tuple

from prefect import task

from tasks.all import run_script, write_mapped_task_list
from tasks.constants import RSCRIPT_ENV
from tasks.task_run_name import (
    bjs_grant_conversion_bystate_tr_name,
    bjs_grant_conversion_tr_name,
)


# flow tasks for BJS grant
@task
def bjs_grant_conversion_bystate_combinations(
    scratch_dir: Path,
    year_list: list,
    states_list: list,
) -> list:
    """Generates state-year combinations for BJS grant by state conversion."""
    state_year_combos = [
        (state, data_year) for state in states_list for data_year in year_list
    ]

    write_mapped_task_list(
        scratch_dir, state_year_combos, "bjs_grant_state_year_combos.txt"
    )

    return state_year_combos


@task(task_run_name=bjs_grant_conversion_bystate_tr_name, tags=["db_task"])
def bjs_grant_conversion_bystate(
    scratch_dir: Path,
    state_year: Tuple[str, int],
    external_dir: Path,
) -> None:
    """Generates database extracts for each state and applies SRS rules."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)
    state_abbr, year = state_year
    os.environ["DATA_YEAR"] = str(year)
    os.environ["INPUT_STATE"] = str(state_abbr)

    run_script(
        scratch_dir=scratch_dir,
        script=f"{RSCRIPT_ENV} Rscript 1001_Run_SRS_byState_Partial.R",
        cwd=Path("tasks_grant/conversion"),
        log_file=f"bjs_grant/conversion_{year}/bjs_extract_implement_rule_{state_abbr}.log",
        shell=True,
    )


@task(task_run_name=bjs_grant_conversion_tr_name)
def bjs_grant_conversion(
    scratch_dir: Path,
    year: int,
    external_dir: Path,
) -> None:
    """NIBRS to SRS conversion for BJS grant."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)
    os.environ["DATA_YEAR"] = str(year)

    run_script(
        scratch_dir=scratch_dir,
        script=f"{RSCRIPT_ENV} Rscript 1002_Run_SRS_Block_Combine_Partial.R",
        cwd=Path("tasks_grant/conversion"),
        log_file=f"bjs_grant/bjs_grant_totals_combine_{year}.log",
        shell=True,
    )


@task
def bjs_grant_combine(
    scratch_dir: Path,
    year_list: list,
    external_dir: Path,
) -> None:
    """Creates final BJS_Grant.csv file."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)
    os.environ["DATA_YEAR"] = str(max(year_list))
    os.environ["DATA_YEAR_MIN"] = str(min(year_list))

    run_script(
        scratch_dir=scratch_dir,
        script=f"{RSCRIPT_ENV} Rscript 1003_Run_Combine_Years_Partial.R",
        cwd=Path("tasks_grant/conversion"),
        log_file="bjs_grant/bjs_grant_final_combine.log",
        shell=True,
    )
