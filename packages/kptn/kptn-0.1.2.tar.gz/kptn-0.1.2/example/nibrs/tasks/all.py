import json
import os
import re
import shutil
import subprocess
from datetime import datetime, timezone
from itertools import product
from pathlib import Path
from typing import Any, Dict, Tuple
from tasks.generate_estimates_database.utils.database_manager import DatabaseManager

import pandas as pd
from prefect import get_run_logger, task
from prefect.client.orchestration import get_client
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from .constants import (
    DEMOGRAPHICS_TABLE_LIST,
    NON_DEMOGRAPHICS_TABLE_LIST,
    RSCRIPT_ENV,
    STATES,
    TABLE_LIST,
    DEMOGRAPHIC_COLUMN_NUMBERS
)
from .settings import (
    GROUP_SIZE,
    MAX_WORKERS,
    OVERWRITE_SUCCESS,
    STOP_COPULA_AFTER_PART1,
    ESTIMATES_DB_NAME
)
from .store import FileStore
from .task_run_name import (
    copula_imputation_step2_summary_tr_name,
    fill_variance_skipped_demos_tr_name,
    final_estimates_momentum_tr_name,
    indicator_estimation_setup_part2_00b_tr_name,
    indicator_estimation_setup_part2_00c_clean_main_tr_name,
    indicator_estimation_setup_tr_name,
    indicator_estimation_tables_part1_preprocessing_tr_name,
    indicator_estimation_tables_part2_generate_est_tr_name,
    indicator_estimation_tables_part3_finalize_tr_name,
    indicator_estimation_tables_part4_select_tables_tr_name,
    indicator_estimation_tables_part5_select_tables_tr_name,
    item_imputation_part1_tr_name,
    item_imputation_part2_nonperson_tr_name,
    item_imputation_part2_person_tr_name,
    item_imputation_part3_5_ethnicity_combine_tr_name,
    item_imputation_part3_5_ethnicity_tr_name,
    item_imputation_part3_finalize_tr_name,
    item_imputation_part4_victim_offender_relationship_tr_name,
    item_imputation_part4_vor_property_tr_name,
    item_imputation_part5_groupb_arrestee_tr_name,
    missing_months_tr_name,
    nibrs_extract_one_state_tr_name,
    qc_for_input_data_missingness_bystate_tr_name,
    queries_by_state_tr_name,
    srs_retamm_file_tr_name,
    universe_file_tr_name,
    validation_extract_bystate_tr_name,
)
# set a concurrency limit of 10 on the 'db_task' tag
async def define_db_task_tag() -> None:
    await get_client().create_concurrency_limit(tag="db_task", concurrency_limit=10)


# worker functions
def create_db_engine() -> Engine:
    """Return an engine for connecting to the database."""
    return create_engine(
        f'postgresql://{os.getenv("PGUSER")}:{os.getenv("PGPASSWORD")}'
        + f'@{os.getenv("PGHOST")}:{os.getenv("PGPORT")}/{os.getenv("PGDATABASE")}'
    )


def run_script(
    scratch_dir: Path,
    script: str,
    cwd: Path,
    log_file: str,
    shell: bool = False,
    add_timings: bool = True,
) -> None:
    """Run a given script and save the output in log files."""
    scratch_log_file = scratch_dir / "log_files" / log_file
    scratch_log_file.parent.mkdir(exist_ok=True, parents=True)
    os.environ["LOG_FILE"] = str(scratch_log_file)

    """save failures as well"""
    scratch_fail_log_file = scratch_dir / "fail_logs" / log_file
    scratch_fail_log_file.parent.mkdir(exist_ok=True, parents=True)

    if add_timings:
        script = f"/usr/bin/time -v {script}"
        # shell must be True when the script's command has spaces in it
        shell = True

    scratch_success_log_file = scratch_dir / "success_logs" / log_file
    scratch_success_log_file.parent.mkdir(exist_ok=True, parents=True)

    if scratch_success_log_file.exists() and not OVERWRITE_SUCCESS:
        # this task has already succeeded so skip it
        pass

    else:
        if OVERWRITE_SUCCESS:
            # we are overwriting this success so remove the success log if it exists
            scratch_success_log_file.unlink(missing_ok=True)

        result = subprocess.run(
            script,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            shell=shell,
        )

        # If the subprocess writes anything to LOG_FILE, then beware that this next
        # step will overwrite it. Some assumptions:
        #
        # - The subprocess will write messages to LOG_FILE when it wants those
        #   messages to be preserved if the subprocess hangs.
        # - Everything the subprocess writes to LOG_FILE, it also writes to stdout.
        # - The subprocess may write additional messages to stdout that it doesn't
        #   write to LOG_FILE.
        #
        # If the subprocess hangs, execution will never reach this point, so
        # LOG_FILE will contain only the messages written there by the subprocess.
        #
        # If the subprocess completes, execution reaches this point, and we
        # overwrite LOG_FILE with everything the subprocess wrote to stdout. That
        # will contain everything the subprocess wrote to LOG_FILE (because we
        # assume it also wrote that to stdout) plus any additional messages the
        # subprocess wrote only to stdout.
        with open(scratch_log_file, mode="w") as fh:
            fh.write(result.stdout)

        try:
            result.check_returncode()
            # add success file
            with open(scratch_success_log_file, mode="w") as fw:  # noqa: F841
                pass

        except subprocess.CalledProcessError as e:
            with open(scratch_fail_log_file, mode="w") as fw:  # noqa: F841
                pass
            with open(scratch_log_file, mode="a") as fw:  # noqa: F841
                fw.write("\n" + str(e))
            raise ValueError(f"Task failed. Logs can be found at {log_file}")


@task()
def combine_logs(scratch_dir: Path) -> None:
    """Take failure logs and combine them into one file for each topic."""
    file_type_dict = {
        "fail_logs": "all_failures.txt",
    }
    for log_type, file_name in file_type_dict.items():
        # Scrape the names of all the log files for failing tasks combine.
        scratch_log_file = scratch_dir / log_type / file_name
        scratch_log_file.parent.mkdir(exist_ok=True, parents=True)

        # check if the combined file already exists and if so delete
        if scratch_log_file.is_file():
            scratch_log_file.unlink()

        # print the log names for all failing tasks to a single txt file
        for root, dirs, files in os.walk(scratch_dir / log_type):
            for file in files:
                if file.endswith(".log"):
                    with open(scratch_log_file, mode="a") as fw:
                        fw.write(file)
                        fw.write("\n")

        # clean-up the folders
        for item in os.listdir(scratch_dir / log_type):
            if item != file_name and (scratch_dir / log_type / item).is_file():
                (scratch_dir / log_type / item).unlink()
            elif item != file_name:
                shutil.rmtree(scratch_dir / log_type / item)


# mapped task lists
def write_mapped_task_list(scratch_dir: Path, task_list: list, task_name: str) -> None:
    """Write a mapped list to a file to save for later."""
    scratch_mapped_file = scratch_dir / "mapped_tasks"
    scratch_mapped_file.mkdir(exist_ok=True, parents=True)
    with open(scratch_dir / "mapped_tasks" / task_name, "w") as task_id_file:
        for i in range(len(task_list)):
            task_id_file.write(f"MAPPED ID: {i}, {str(task_list[i])}\n")


def write_mapped_group_reference(
    scratch_dir: Path,
    group_list: list,
    reference_file_name: str,
) -> None:
    """Write a mapped list to a file to save for later."""
    scratch_mapped_file = scratch_dir / "mapped_tasks"
    scratch_mapped_file.mkdir(exist_ok=True, parents=True)
    with open(scratch_dir / "mapped_tasks" / reference_file_name, "w") as task_id_file:
        counter = 1
        for group in group_list:
            if len(group) == 0:
                task_id_file.write(f"Group: {counter}, Length: 0\n")
                counter += 1
                continue
            first_item = group[0]
            if isinstance(first_item, list):
                first_item = first_item[0]

            last_item = group[-1]
            if isinstance(last_item, list):
                last_item = last_item[-1]

            task_id_file.write(
                f"Group: {counter}, Length: {len(group)}, First Item: {first_item}, Last Item: {last_item}\n"
            )
            counter += 1


@task
def get_years_in_database(data_year: int) -> list:
    """Gets the set of years available in the database."""
    engine = create_db_engine()
    year_list = (
        pd.read_sql(
            sql="SELECT DISTINCT EXTRACT(year FROM incident_date) AS data_year FROM ucr_prd.nibrs_incident",
            con=engine,
        )["data_year"]
        .astype(int)
        .tolist()
    )
    return [y for y in year_list if y >= (data_year - 4) and y <= data_year]


@task
def get_ten_years_in_database(data_year: int) -> list:
    """Gets the 10 years prior to the current year in the database."""
    engine = create_db_engine()
    year_list = (
        pd.read_sql(
            sql="SELECT DISTINCT EXTRACT(year FROM incident_date) AS data_year FROM ucr_prd.nibrs_incident",
            con=engine,
        )["data_year"]
        .astype(int)
        .tolist()
    )
    return [y for y in year_list if y > (data_year - 10) and y <= data_year]


@task
def get_states_in_database(
    scratch_dir: Path,
    data_year: int,
) -> list:
    """Gets the set of states available from the connected database for future tasks."""
    engine = create_db_engine()

    state_df = pd.read_sql(
        f"""
    SELECT
        ref_state.abbr as state_abbr,
        ref_agency_status.agency_status,
        CASE
            WHEN ref_agency_yearly.is_covered IS TRUE THEN 'Y'::text
            WHEN ref_agency_yearly.is_covered IS FALSE THEN 'N'::text
            ELSE ' '::text
        END AS covered_flag,
        CASE
            WHEN ref_agency_yearly.agency_status = 'D'::bpchar THEN 'Y'::text
            ELSE 'N'::text
        END AS dormant_flag,
        ref_agency_type.name as agency_type_name
    FROM ucr_prd.ref_agency_yearly ref_agency_yearly
        LEFT JOIN ucr_prd.ref_agency ref_agency USING (agency_id)
        LEFT JOIN ucr_prd.ref_state USING (state_id)
        LEFT JOIN ucr_prd.ref_agency_status ref_agency_status USING (agency_id, data_year)
        LEFT JOIN ucr_prd.ref_agency_type USING (agency_type_id)
    WHERE ref_agency_status.data_year IS NOT NULL AND
          ref_agency_yearly.is_nibrs IS TRUE AND
          ref_agency_status.data_year = {data_year}
    """,
        con=engine,
    )

    state_df = state_df.loc[
        (state_df["agency_status"] == "A")
        & (state_df["covered_flag"] == "N")
        & (state_df["dormant_flag"] == "N")
        & (state_df["agency_type_name"].str.upper() != "FEDERAL")
    ]
    state_list = state_df["state_abbr"].unique().tolist()

    # drop any entries not in the states list (i.e. territories)
    state_list = [s for s in state_list if s in STATES]

    write_mapped_task_list(scratch_dir, state_list, "states_in_database_list.txt")

    return state_list


@task
def get_state_dependency_list(
    year: int,
) -> list:
    """Gets the list of dependent states based on year."""
    if year == 2020:
        dependent_state = ["NY"]
    elif year == 2021:
        dependent_state = ["FL"]
    elif year == 2023:
        dependent_state = ["WV"]
    else:
        dependent_state = []
    return dependent_state


@task
def get_vic_off_rel_state_dependency_split(
    scratch_dir: Path,
    states_in_database: list,
    dependent_states: list,
) -> tuple:
    """Splits up the states into two steps. Some states in vic-off-rel imputation depend on others."""
    independent_states = list(set(states_in_database) - set(dependent_states))
    dependent_states = list(set(states_in_database) & set(dependent_states))
    write_mapped_task_list(
        scratch_dir,
        independent_states,
        "independent_state_item_imp_list.txt",
    )
    write_mapped_task_list(
        scratch_dir,
        dependent_states,
        "dependent_state_item_imp_list.txt",
    )

    return (independent_states, dependent_states)


@task
def indicator_estimation_get_table_combinations(
    scratch_dir: Path,
) -> Tuple[list, list, list]:
    """Get lists needed for each step of the table estimation."""
    base_tables = TABLE_LIST + ["GV2b"]
    est_table_ranges = {
        "1a": list(range(1, 21)),
        "1b": list(range(1, 16)),
        "1c": list(range(1, 28)),
        "2a": list(range(1, 21)),
        "2b": list(range(1, 19)),
        "2c": list(range(1, 28)),
        "3a": list(range(1, 34)),
        "3b": list(range(1, 34)),
        "3c": list(range(1, 16)),
        "4a": list(range(1, 62)),
        "4b": list(range(1, 62)),
        "LEOKA": list(range(1, 2)),
        "DM1": list(range(1, 2)),
        "DM2": list(range(1, 2)),
        "DM3": list(range(1, 2)),
        "DM4": list(range(1, 2)),
        "DM5": list(range(1, 2)),
        "DM6": list(range(1, 55)),
        "DM7": list(range(1, 55)),
        "DM8": list(range(1, 55)),
        "DM9": list(range(1, 55)),
        "DM10": list(range(1, 5)),
        "5a": list(range(1, 72)),
        "5b": list(range(1, 72)),
        "GV1a": list(range(1, 14)),
        "GV2a": list(range(1, 14)),
        "GV2b": list(range(1, 14)),
        "3aunclear": list(range(1, 34)),
        "3aclear": list(range(1, 34)),
        "3bunclear": list(range(1, 34)),
        "3bclear": list(range(1, 34)),
        "YT1": list(range(1, 2)),
        "YT2": list(range(1, 2)),
        "GV3a": list(range(1, 14)),
    }
    generate_est_combos = []
    for table, cols in est_table_ranges.items():
        generate_est_combos += list(product([table], cols))

    add_col_ranges = {
        "3a": list(range(1000, 261000, 1000)),
        "3b": list(range(1000, 261000, 1000)),
        "4a": list(range(1000, 261000, 1000)),
        "4b": list(range(1000, 261000, 1000)),
        "DM7": list(range(1000, 261000, 1000)),
        "DM9": list(range(1000, 261000, 1000)),
        "DM10": list(range(1000, 261000, 1000)),
        "5a": list(range(1000, 261000, 1000)),
        "5b": list(range(1000, 261000, 1000)),
        "GV2a": list(range(1000, 261000, 1000)),
        "3aunclear": list(range(1000, 261000, 1000)),
        "3aclear": list(range(1000, 261000, 1000)),
        "3bunclear": list(range(1000, 261000, 1000)),
        "3bclear": list(range(1000, 261000, 1000)),
    }
    col_ranges = []
    for table, cols in add_col_ranges.items():
        col_ranges += list(product([table], cols))

    write_mapped_task_list(scratch_dir, base_tables, "est_base_tables_list.txt")
    write_mapped_task_list(
        scratch_dir,
        generate_est_combos,
        "table_est_generate_est_list.txt",
    )
    write_mapped_task_list(
        scratch_dir,
        col_ranges,
        "table_est_create_additional_columns_list.txt",
    )

    return base_tables, generate_est_combos, col_ranges


def get_combo_lists(
    skip_dict: dict,
    demographic_perms: list,
    permutations: list,
    demographics: list,
    items_per_worker: int,
    table_list: list = TABLE_LIST,
) -> list:
    """Get combinations for a list of geographic permutations."""
    combos = list(product(table_list, permutations))
    all_combos = [
        combos[i : i + items_per_worker]
        for i in range(0, len(combos), items_per_worker)
    ]

    all_dems_for_group = [
        p  # type: ignore
        for p in demographic_perms  # type: ignore
        if (p // 1000 in demographics and p % 1000 in permutations)  # type: ignore
    ]  # type:ignore

    dem_combos = []
    for d in all_dems_for_group:  # type:ignore
        for table in [t for t in DEMOGRAPHICS_TABLE_LIST if t in table_list]:
            # only add if this specific table + demographic combination is not skipped
            if table not in skip_dict.keys() or d // 1000 not in skip_dict[table]:
                dem_combos.append((table, d))

    all_combos += [
        dem_combos[i : i + items_per_worker]
        for i in range(0, len(dem_combos), items_per_worker)
    ]
    return all_combos


@task
def get_variance_table_list(
    scratch_dir: Path,
    external_config: Path,
    external_dir: Path,
    year: int,
) -> list:
    """Read in the population file to get the set of permutations."""
    with open(external_config, "r") as ex_path_f:
        path_dict = json.load(ex_path_f)[str(year)]
        population_path = path_dict["population"]
        exclude_path = path_dict["exclusion"]

    population_df = pd.read_csv(
        external_dir / population_path, usecols=["PERMUTATION_NUMBER"]
    )
    permutation_list = population_df["PERMUTATION_NUMBER"].astype(int).tolist()

    exclude = pd.read_csv(external_dir / exclude_path, usecols=["PERMUTATION_NUMBER"])
    exclude_list = exclude["PERMUTATION_NUMBER"].astype(int).tolist()

    permutation_list = [x for x in permutation_list if x % 1000 not in exclude_list]

    old_race_demo = (
        [12, 13, 14, 15, 16, 20, 26]
        + list(range(28, 84))
        + list(range(106, 136))
        + [142, 143, 144]
    )

    # we need to remove the old version of the race demographics
    permutation_list = [p for p in permutation_list if not (p // 1000 in old_race_demo)]
    all_return_lists = []

    # tasks to create final estimates

    # before we get into the weeds, just drop 108 + all demographics and drop 107 for 1 through 27
    permutation_list = [
        p
        for p in permutation_list
        if (
            (not (p % 1000 == 108 and p // 1000 > 0))
            and (
                not (
                    (p % 1000 == 107)
                    and (
                        p // 1000
                        in [
                            1,
                            2,
                            3,
                            4,
                            5,
                            6,
                            7,
                            8,
                            9,
                            17,
                            18,
                            19,
                            21,
                            22,
                            23,
                            24,
                            25,
                            27,
                            136,
                            139,
                        ]
                    )
                )
            )
        )
    ]
    skip_df = pd.read_csv(
        scratch_dir
        / f"indicator_demo_missing/demographic_permutation_skipped_{year}.csv"
    )
    skip_dict = {}
    for table, table_group in skip_df.groupby("Table"):  # type: ignore
        skip_dict[table] = (table_group["Demographic_Permutation"] // 1000).tolist()  # type: ignore

    geographic_perms = [p for p in permutation_list if p < 1000]
    demographic_perms = [p for p in permutation_list if p > 1000]

    # first, we get all of the national permutations
    national_perm = [1]
    region_permutations = [g for g in geographic_perms if g in [12, 23, 34, 45]]
    state_permutations = [g for g in geographic_perms if g in range(56, 107)]
    msa_permutations = [
        g for g in geographic_perms if (g in range(109, 493)) | (g in range(638, 710))
    ]
    jd_permutations = [g for g in geographic_perms if g in range(493, 583)]
    fo_permutations = [g for g in geographic_perms if g in range(583, 638)]
    remaining_permutations = [
        g
        for g in geographic_perms
        if g
        not in (
            jd_permutations
            + fo_permutations
            + state_permutations
            + region_permutations
            + national_perm
            + msa_permutations
        )
    ]

    national_demographics = (
        list(range(1, 12))
        + [17, 18, 19, 21, 22, 23, 24, 25, 27]
        + list(range(84, 106))
        + list(range(136, 142))
        + list(range(145, 261))
    )
    region_demographics = (
        list(range(1, 12))
        + [17, 18, 19, 21, 22, 23, 24, 25, 27]
        + list(range(136, 142))
        + list(range(146, 170))
    )
    all_demographics = (
        list(range(1, 12))
        + [17, 18, 19, 21, 22, 23, 24, 25, 27, 136, 139]
        + list(range(145, 154))
        + [258]
    )

    all_national_combos = get_combo_lists(
        skip_dict,
        demographic_perms,
        national_perm,
        national_demographics,
        2,
    )
    all_national_combos_part1 = all_national_combos[:GROUP_SIZE]
    all_return_lists.append(all_national_combos_part1)

    all_national_combos_part2 = all_national_combos[GROUP_SIZE:]
    all_return_lists.append(all_national_combos_part2)

    all_region_combos = get_combo_lists(
        skip_dict,
        demographic_perms,
        region_permutations,
        region_demographics,
        4,
    )
    all_return_lists.append(all_region_combos)

    all_state_combos = get_combo_lists(
        skip_dict,
        demographic_perms,
        state_permutations,
        all_demographics,
        3,
    )
    list_counter = 4
    for i in range(0, len(all_state_combos), GROUP_SIZE):
        temp_list = all_state_combos[i : min(len(all_state_combos), i + GROUP_SIZE)]
        all_return_lists.append(temp_list)
        list_counter += 1

    all_msa_combos = get_combo_lists(
        skip_dict,
        demographic_perms,
        msa_permutations,
        all_demographics,
        10,
    )
    for i in range(0, len(all_msa_combos), GROUP_SIZE):
        temp_list = all_msa_combos[i : min(len(all_msa_combos), i + GROUP_SIZE)]
        all_return_lists.append(temp_list)
        list_counter += 1

    all_fo_combos = get_combo_lists(
        skip_dict,
        demographic_perms,
        fo_permutations,
        all_demographics,
        10,
    )
    for i in range(0, len(all_fo_combos), GROUP_SIZE):
        temp_list = all_fo_combos[i : min(len(all_fo_combos), i + GROUP_SIZE)]
        all_return_lists.append(temp_list)
        list_counter += 1

    all_jd_combos = get_combo_lists(
        skip_dict,
        demographic_perms,
        jd_permutations,
        all_demographics,
        10,
    )
    for i in range(0, len(all_jd_combos), GROUP_SIZE):
        temp_list = all_jd_combos[i : min(len(all_jd_combos), i + GROUP_SIZE)]
        all_return_lists.append(temp_list)
        list_counter += 1

    all_remaining_combos = get_combo_lists(
        skip_dict,
        demographic_perms,
        remaining_permutations,
        all_demographics,
        10,
    )
    for i in range(0, len(all_remaining_combos), GROUP_SIZE):
        temp_list = all_remaining_combos[
            i : min(len(all_remaining_combos), i + GROUP_SIZE)
        ]
        all_return_lists.append(temp_list)
        list_counter += 1

    write_mapped_group_reference(
        scratch_dir,
        all_return_lists,
        "variance_table_list_reference.txt",
    )

    return all_return_lists


@task
def verify_variance_runs(scratch_dir: Path, all_perm_groups: list) -> list:
    """Check the output folders and verify that all combination ran."""
    skip_variance_files = (scratch_dir / "variance_skip").iterdir()

    skip_variance_combos = []
    for file in skip_variance_files:
        file = str(file).split("/")[-1]  # type: ignore
        split = str(file).find("_")
        permutation = int(str(file)[:split])
        table = str(file)[split + 1 :].replace(".csv", "")
        skip_variance_combos.append([table, permutation])

    output_dir = scratch_dir / "indicator_table_estimates_after_variance"
    missing_list = []
    missing_inner_list = []
    for group in all_perm_groups:
        for inner_set in group:
            for combo in inner_set:
                table, perm = combo
                if [table, int(perm)] in skip_variance_combos:
                    continue

                file_name = (
                    f"Table {table}_Reporting_Database_After_Variance_{perm}.csv"
                )

                # check if this output file exists. If not then save
                if not (output_dir / file_name).exists():
                    missing_inner_list.append([combo])
                    if len(missing_inner_list) > GROUP_SIZE:
                        missing_list.append(missing_inner_list)
                        missing_inner_list = []

    missing_list.append(missing_inner_list)

    write_mapped_task_list(
        scratch_dir,
        missing_list,
        "variance_table_list_missing.txt",
    )
    write_mapped_group_reference(
        scratch_dir,
        missing_list,
        "missing_permutation_table_groups_reference.txt",
    )

    return missing_list


@task
def get_specific_group(
    scratch_dir: Path,
    groups: list,
    group_num: int,
    task_list_name: str,
) -> list:
    """A simple task that returns the specific group needed. Making this a task helps prevent Prefect from making a bunch of tasks ahead of time."""
    group = groups[group_num - 1]
    write_mapped_task_list(
        scratch_dir,
        group,
        f"{task_list_name}_{group_num}.txt",
    )
    return group


@task
def get_copula_combinations(
    scratch_dir: Path,
    external_config: Path,
    external_dir: Path,
    year: int,
) -> Tuple[list, list]:
    """Take the permutations and cross them with copula column numbers."""
    with open(external_config, "r") as ex_path_f:
        population_path = json.load(ex_path_f)[str(year)]["population"]

    population_df = pd.read_csv(
        external_dir / population_path, usecols=["PERMUTATION_NUMBER"]
    )
    permutation_list = population_df["PERMUTATION_NUMBER"].astype(int).tolist()

    # remove demographics based on the prior race definitions
    old_race_demo = (
        [12, 13, 14, 15, 16, 20, 26]
        + list(range(28, 84))
        + list(range(106, 136))
        + [142, 143, 144]
    )
    permutation_list = [p for p in permutation_list if not (p // 1000 in old_race_demo)]

    national_perm_list = [p for p in permutation_list if (p % 1000 == 1)]
    national_nodemo_list = [p for p in permutation_list if p == 1]

    all_copula_combinations_nodemo = list(
        product(NON_DEMOGRAPHICS_TABLE_LIST, national_nodemo_list)
    )
    add_copula_combo_demolist = list(
        product(DEMOGRAPHICS_TABLE_LIST, national_perm_list)
    )

    all_copula_stack_combos = all_copula_combinations_nodemo + add_copula_combo_demolist

    # remove any demographic permutations identified to not exist for specific tables
    skip_df = pd.read_csv(
        scratch_dir
        / f"indicator_demo_missing/demographic_permutation_skipped_{year}.csv"
    )

    final_all_copula_stack_combos = all_copula_stack_combos
    for index, row in skip_df.iterrows():
        final_all_copula_stack_combos = [
            x
            for x in final_all_copula_stack_combos
            if not (x[0] == row["Table"] and x[1] == row["Demographic_Permutation"] + 1)
        ]

    # add column set
    combo_tables = [
        "DM6",
        "DM7",
        "DM8",
        "DM9",
    ]
    combo_perms = [p for p in final_all_copula_stack_combos if p[0] in combo_tables]
    no_combo_perms = [
        p for p in final_all_copula_stack_combos if p[0] not in combo_tables
    ]

    all_copula_combinations = list(product(no_combo_perms, [1])) + list(
        product(combo_perms, list(range(1, 10)))
    )

    # finally add stratification var
    all_copula_combinations_final = list(
        product(all_copula_combinations, list(range(1, 9)))
    )

    write_mapped_task_list(
        scratch_dir,
        final_all_copula_stack_combos,
        "copula_combinations_stack_list.txt",
    )

    write_mapped_task_list(
        scratch_dir,
        all_copula_combinations_final,
        "copula_combinations_list.txt",
    )

    return all_copula_combinations_final, final_all_copula_stack_combos


@task
def get_demo_perm_fill_list(
    scratch_dir: Path,
    year: int,
) -> list:
    """Returns the list of table/demographic permutation pairs that we want to fill."""
    # read in the dataset with what was skipped
    skip_df = pd.read_csv(
        scratch_dir
        / f"indicator_demo_missing/demographic_permutation_skipped_{year}.csv"
    )

    # create a list to return
    skip_combo_list = []
    for index, row in skip_df.iterrows():
        add = (row["Table"], row["Demographic_Permutation"])
        skip_combo_list.append(add)

    write_mapped_task_list(
        scratch_dir,
        skip_combo_list,
        "skipped_demographics_list.txt",
    )

    return skip_combo_list


@task
def create_copula_groups(
    scratch_dir: Path,
    full_copula_combo_list: list,
) -> Path:
    split_tables = [
        "DM7",
        "DM9",
    ]

    nodemo_list = [
        x for x in full_copula_combo_list if x[0][0][0] in NON_DEMOGRAPHICS_TABLE_LIST
    ]

    solo_table_list = []
    non_split_demo_tables = [
        t for t in DEMOGRAPHICS_TABLE_LIST if t not in split_tables
    ]
    for t in non_split_demo_tables:
        current_list = [x for x in full_copula_combo_list if x[0][0][0] == t]
        solo_table_list.append(current_list[:GROUP_SIZE])
        solo_table_list.append(current_list[GROUP_SIZE:])

    solo_colset_list = []
    for t in split_tables:
        for c in range(1, 10):
            current_list = [
                x for x in full_copula_combo_list if x[0][0][0] == t and x[0][1] == c
            ]
            solo_colset_list.append(current_list[:GROUP_SIZE])
            solo_colset_list.append(current_list[GROUP_SIZE:])

    all_groups = [nodemo_list] + solo_table_list + solo_colset_list
    write_mapped_group_reference(
        scratch_dir,
        all_groups,
        "copula_group_reference.txt",
    )
    out_list_file = "copula_part2_allgroups.json"
    out_list_path = Path(scratch_dir / "mapped_tasks" / out_list_file)
    with open(out_list_path, "w") as out_file:
        json.dump(all_groups, out_file)

    return out_list_path


@task
def get_final_estimation_permutation_list(
    scratch_dir: Path,
    external_config: Path,
    external_dir: Path,
    year: int,
) -> Tuple[list, Path]:
    """Returns the list of basic permutations we want final estimate files for."""
    with open(external_config, "r") as ex_path_f:
        path_dict = json.load(ex_path_f)[str(year)]
        population_path = path_dict["population"]
        exclude_path = path_dict["exclusion"]

    population_df = pd.read_csv(
        external_dir / population_path,
        usecols=["PERMUTATION_NUMBER", "WEIGHT_VAR", "PERMUTATION_DESCRIPTION"],
    )

    exclude = pd.read_csv(external_dir / exclude_path, usecols=["PERMUTATION_NUMBER"])
    exclude_list = exclude["PERMUTATION_NUMBER"].astype(int).tolist()
    population_df = population_df.loc[population_df["PERMUTATION_NUMBER"] < 1000]

    population_df = population_df.loc[
        ~population_df["PERMUTATION_NUMBER"].isin(exclude_list)
    ]

    population_df["Folder"] = population_df["WEIGHT_VAR"].apply(
        lambda x: x.replace("Wgt", "")
    )
    population_df["Sub_Folder"] = population_df["PERMUTATION_DESCRIPTION"].apply(
        lambda x: x.replace(" ", "_").replace(",", "").replace("-", "_")
    )

    momentum_set = population_df[
        ["PERMUTATION_NUMBER", "Folder", "Sub_Folder"]
    ].values.tolist()

    write_mapped_task_list(
        scratch_dir, momentum_set, "final_permutation_momentum_list.txt"
    )

    suppression_list = [list(product([t], momentum_set)) for t in TABLE_LIST]
    suppression_list = [list(product([t], momentum_set)) for t in TABLE_LIST]
    final_list_set = []
    for group in suppression_list:
        for i in range(0, len(group), GROUP_SIZE):
            final_list_set.append(group[i : min(i + GROUP_SIZE, len(group))])

    write_mapped_task_list(
        scratch_dir,
        momentum_set,
        "final_permutation_suppression_groups.txt",
    )

    write_mapped_group_reference(
        scratch_dir,
        final_list_set,
        "final_permutation_suppression_group_reference.txt",
    )
    out_list_file = "final_permutation_suppression_allgroups.json"
    out_list_path = Path(scratch_dir / "mapped_tasks" / out_list_file)
    with open(out_list_path, "w") as out_file:
        json.dump(final_list_set, out_file)

    return (momentum_set, out_list_path)


@task
def create_general_groups(
    scratch_dir: Path,
    perm_list: list,
    group_name: str,
) -> Path:
    """A simple task that returns the specified list split into sets of GROUP_SIZE."""
    return_list = []
    for i in range(0, len(perm_list), GROUP_SIZE):
        temp_list = perm_list[i : min(len(perm_list), i + GROUP_SIZE)]
        return_list.append(temp_list)

    write_mapped_group_reference(
        scratch_dir,
        return_list,
        f"{group_name}_list_reference.txt",
    )

    out_list_file = f"{group_name}_allgroups.json"
    out_list_path = Path(scratch_dir / "mapped_tasks" / out_list_file)
    with open(out_list_path, "w") as out_file:
        json.dump(return_list, out_file)

    return out_list_path


# flow NIBRS task functions - non-validation
@task
def create_scratch_dir(run_id: str, flow_name: str) -> Path:
    """Create a directory for holding a flow's scratch files."""
    scratch_dir = Path(f"{os.environ['SCRATCH_DIR']}/{run_id}/flow_{flow_name}")
    scratch_dir.mkdir(exist_ok=True, parents=True)
    return scratch_dir


@task
def create_run_metadata(
    scratch_dir: Path,
    run_id: str,
    flow_name: str,
) -> None:
    """Create an artifact containing metadata about the run."""
    metadata_path = scratch_dir / "run_metadata.json"

    metadata = {
        "run_id": run_id,
        "flow_name": flow_name,
        "PGHOST": os.getenv("PGHOST"),
        "PGDATABASE": os.getenv("PGDATABASE"),
        "git_branch": os.getenv("GIT_BRANCH"),
        "git_hash": os.getenv("GIT_HASH"),
        "max_workers": MAX_WORKERS,
    }

    with open(metadata_path, mode="w") as fh:
        json.dump(metadata, fh, indent=2)


@task
def copy_external_file_json(scratch_dir: Path, method30: bool = False) -> Path:
    """Copies the external_file_locations file to the scratch dir.

    The external_file_locations file contains the file paths to specific versions
    of external files like reta-mm and universe which are needed for each year.
    This step copies the local repository version of this file into the pipeline
    folder so that there is a record of what versions of these files were used in
    the pipeline run.

    """
    # copy the input file ref into the pipeline directory so we can
    # record which dates were used
    if method30:
        fromfile = "data/external_file_locations_30_year.json"
    else:
        fromfile = "data/external_file_locations.json"

    to_file = scratch_dir / "external_file_locations.json"
    shutil.copyfile(
        fromfile,
        to_file,
    )

    return to_file


@task
def fetch_external_files(
    store: FileStore, external_config: Path, scratch_dir: Path
) -> Path:
    """Copy all requested external files from the file store into the scratch space.

    Return the path to the directory where the external files are stored.
    """
    is_failure = False
    to_dir = scratch_dir / "externals"

    if to_dir == store.external_location:
        return to_dir

    with open(external_config, mode="r") as fh:
        config = json.load(fh)

    for vintage_year in config:
        for code_name in config[vintage_year]:
            file = config[vintage_year][code_name]
            try:
                store.fetch_external(
                    store_file=file,
                    to_file=to_dir / file,
                )
            except FileNotFoundError as e:
                print(e)
                is_failure = True

    if is_failure:
        raise FileNotFoundError(
            "There was an error fetching one or more external files."
        )

    return to_dir


@task(task_run_name=universe_file_tr_name)
def universe_file(
    scratch_dir: Path,
    year: int,
    external_dir: Path,
) -> None:
    """Calls the DB function that generates the universe file and saves it to csv."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["DATA_YEAR"] = str(year)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)

    run_script(
        scratch_dir=scratch_dir,
        script="python create_universe_file.py",
        cwd=Path("tasks_initial/universe"),
        log_file=f"initial/universe_{year}.log",
        shell=True,
    )


@task(task_run_name=queries_by_state_tr_name)
def queries_by_state(
    scratch_dir: Path,
    external_dir: Path,
    year: int,
    state_abbr: str,
) -> None:
    """Calls R script that runs queries for a single state against the database and saves query outputs to csvs."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)
    os.environ["DATA_YEAR"] = str(year)
    os.environ["INPUT_STATE"] = str(state_abbr)

    run_script(
        scratch_dir=scratch_dir,
        script=f"{RSCRIPT_ENV} Rscript queries_by_state.R",
        cwd=Path("tasks_initial/database_queries"),
        log_file=f"initial/database_queries_state/queries_{state_abbr}.log",
        shell=True,
    )


@task(task_run_name=queries_by_state_tr_name)
def queries_by_state_qc(
    scratch_dir: Path,
    external_dir: Path,
    year: int,
    state_abbr: str,
) -> None:
    """Calls R script that runs queries for a single state against the database and saves query outputs to csvs."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)
    os.environ["DATA_YEAR"] = str(year)
    os.environ["INPUT_STATE"] = str(state_abbr)

    run_script(
        scratch_dir=scratch_dir,
        script=f"{RSCRIPT_ENV} Rscript queries_by_state_qc_missingness.R",
        cwd=Path("tasks_initial/database_queries"),
        log_file=f"initial/database_queries_state/queries_qc_missingness_{state_abbr}.log",
        shell=True,
    )


@task
def queries_by_data_year(
    scratch_dir: Path,
    external_dir: Path,
    year: int,
) -> None:
    """Calls R script that runs queries for the selected data year against the database and saves query outputs to csvs."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)
    os.environ["DATA_YEAR"] = str(year)

    run_script(
        scratch_dir=scratch_dir,
        script=f"{RSCRIPT_ENV} Rscript queries_by_data_year.R",
        cwd=Path("tasks_initial/database_queries"),
        log_file=f"initial/database_queries_{year}.log",
        shell=True,
    )


@task(task_run_name=missing_months_tr_name)
def missing_months(
    scratch_dir: Path,
    year: int,
    external_dir: Path,
) -> None:
    """Generate a new reta-mm file from the nibrs_month table and universe file."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["DATA_YEAR"] = str(year)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)

    run_script(
        scratch_dir=scratch_dir,
        script=f"{RSCRIPT_ENV} Rscript 100-Run_Program.R",
        cwd=Path("tasks/missing_months"),
        log_file=f"nibrs/missing_months_creation_{year}.log",
        shell=True,
    )


@task
def create_msa_provider(
    scratch_dir: Path,
    year: int,
    external_dir: Path,
) -> None:
    """Generate the MSA by provider file from the database."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["DATA_YEAR"] = str(year)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)

    run_script(
        scratch_dir=scratch_dir,
        script=f"{RSCRIPT_ENV} Rscript 100_Create_MSA_provider_file.R",
        cwd=Path("tasks_initial/MSA_by_provider"),
        log_file=f"initial/MSA_by_provider_{year}.log",
        shell=True,
    )


@task(task_run_name=srs_retamm_file_tr_name)
def srs_retamm_file(
    scratch_dir: Path,
    year: int,
    external_dir: Path,
) -> None:
    """Generate the SRS file including SRS-only reporters from the database and universe file."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["DATA_YEAR"] = str(year)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)

    run_script(
        scratch_dir=scratch_dir,
        script="python generate_srs_retamm.py",
        cwd=Path("tasks_initial/srs_retamm"),
        log_file=f"initial/srs_retamm_{year}.log",
        shell=True,
    )


@task
def impute_officers(
    scratch_dir: Path,
    year: int,
    external_dir: Path,
    method30: bool = False,
) -> None:
    """Impute the missing officer counts in the universe file."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["DATA_YEAR"] = str(year)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)

    if method30:
        run_script(
            scratch_dir=scratch_dir,
            script=f"{RSCRIPT_ENV} Rscript 100_Run_01_Impute_Officers_30yr.R",
            cwd=Path("tasks_initial/impute_officers"),
            log_file=f"initial/impute_officers_{year}.log",
            shell=True,
        )
    else:
        run_script(
            scratch_dir=scratch_dir,
            script=f"{RSCRIPT_ENV} Rscript 100_Run_01_Impute_Officers.R",
            cwd=Path("tasks_initial/impute_officers"),
            log_file=f"initial/impute_officers_{year}.log",
            shell=True,
        )


@task
def update_universe(
    scratch_dir: Path,
    year: int,
    external_dir: Path,
) -> None:
    """Update the universe file with the new officer imputations."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["DATA_YEAR"] = str(year)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)

    run_script(
        scratch_dir=scratch_dir,
        script=f"{RSCRIPT_ENV} Rscript 02_Update_Universe.R",
        cwd=Path("tasks_initial/impute_officers"),
        log_file=f"initial/update_universe_{year}.log",
        shell=True,
    )


@task
def update_pop_totals(
    scratch_dir: Path,
    year: int,
    external_dir: Path,
    pipeline: str,
) -> None:
    """Update the POP_TOTALS FILES with the new officer imputations."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["DATA_YEAR"] = str(year)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)

    if pipeline == "NIBRS":
        run_script(
            scratch_dir=scratch_dir,
            script=f"{RSCRIPT_ENV} Rscript 103_Update_POP_TOTALS_PERM_YEAR.R",
            cwd=Path("tasks_initial/impute_officers"),
            log_file=f"initial/update_NIBRS_POP_TOTALS_{year}.log",
            shell=True,
        )
    elif pipeline == "SRS":
        run_script(
            scratch_dir=scratch_dir,
            script=f"{RSCRIPT_ENV} Rscript 104_Update_POP_TOTALS_PERM_YEAR_SRS.R",
            cwd=Path("tasks_initial/impute_officers"),
            log_file=f"initial/update_SRS_POP_TOTALS_{year}.log",
            shell=True,
        )
    else:
        run_script(
            scratch_dir=scratch_dir,
            script=f"{RSCRIPT_ENV} Rscript 104_Update_POP_TOTALS_PERM_YEAR_SRS_30yr.R",
            cwd=Path("tasks_initial/impute_officers"),
            log_file=f"initial/update_SRS_POP_TOTALS_{year}.log",
            shell=True,
        )


@task
def partial_reporters(
    scratch_dir: Path,
    year: int,
    external_dir: Path,
) -> None:
    """Runs the partial reporting R scripts.

    Runs part 1 which uses the NIBRS database to identify which months agencies reported.
    Then runs part 2 which takes the output of part 1 and adds information from the
    reta-mm and universe files.

    """
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)
    os.environ["DATA_YEAR"] = str(year)

    run_script(
        scratch_dir=scratch_dir,
        script="./generate_partial_reporters.sh",
        cwd=Path("tasks/create_partial_reporters"),
        log_file="nibrs/partial_reporters.log",
    )


@task(task_run_name=nibrs_extract_one_state_tr_name, tags=["db_task"])
def nibrs_extract_one_state(
    scratch_dir: Path,
    year: int,
    external_dir: Path,
    state_abbr: str,
) -> None:
    """Runs the NIBRS extract creation R scripts."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["DATA_YEAR"] = str(year)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)
    os.environ["INPUT_STATE"] = str(state_abbr)

    run_script(
        scratch_dir=scratch_dir,
        script=f"{RSCRIPT_ENV} Rscript 100-Run_Program.R",
        cwd=Path("tasks/create_nibrs_extracts/extract_one_state"),
        log_file=f"nibrs/nibrs_extract/nibrs_extract_{state_abbr}.log",
        shell=True,
    )


@task
def outlier_detection(
    scratch_dir: Path,
    year: int,
) -> None:
    """Runs the outlier detection step which depends on partial reporters."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["DATA_YEAR"] = str(year)

    run_script(
        scratch_dir=scratch_dir,
        script=f"{RSCRIPT_ENV} Rscript 100_run_outlier_detection_scripts_v5.R",
        cwd=Path("tasks/detect_outliers"),
        log_file="nibrs/outlier_detection.log",
        shell=True,
    )


@task
def block_imputation(
    scratch_dir: Path,
    year: int,
) -> None:
    """Runs the block imputation step which depends on outlier detection."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["DATA_YEAR"] = str(year)

    run_script(
        scratch_dir=scratch_dir,
        script=f"{RSCRIPT_ENV} Rscript 100_Run_Block_Imputation.R",
        cwd=Path("tasks/impute_blocks"),
        log_file="nibrs/block_imputation.log",
        shell=True,
    )


@task
def block_imputation_group_b(
    scratch_dir: Path,
    year: int,
) -> None:
    """Runs the block imputation step which depends on outlier detection."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["DATA_YEAR"] = str(year)

    run_script(
        scratch_dir=scratch_dir,
        script=f"{RSCRIPT_ENV} Rscript 100_Run_Block_Imputation_group_b.R",
        cwd=Path("tasks/impute_blocks"),
        log_file="nibrs/block_imputation_group_b.log",
        shell=True,
    )


@task(task_run_name=item_imputation_part1_tr_name)
def item_imputation_part1(scratch_dir: Path, year: int, state_abbr: str) -> None:
    """Runs the item imputation step which sets up logical edits.

    It depends on NIBRS Extracts.
    """
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["DATA_YEAR"] = str(year)
    os.environ["INPUT_STATE"] = str(state_abbr)

    run_script(
        scratch_dir=scratch_dir,
        script=f"{RSCRIPT_ENV} Rscript 100_Run_Logical_Edits.R",
        cwd=Path("tasks/impute_items/part1_setup_logical_edits"),
        log_file=f"nibrs/item_imputation/item_imp_part1/item_imp_part1_{state_abbr}.log",
        shell=True,
    )


@task(task_run_name=item_imputation_part2_nonperson_tr_name)
def item_imputation_part2_nonperson(
    scratch_dir: Path, year: int, state_abbr: str
) -> None:
    """Runs item imputation for nonperson victims. It depends on part 1."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["DATA_YEAR"] = str(year)
    os.environ["INPUT_STATE"] = str(state_abbr)

    run_script(
        scratch_dir=scratch_dir,
        script=f"{RSCRIPT_ENV} Rscript 100_Run_Nonperson_Victims.R",
        cwd=Path("tasks/impute_items/part2_nonperson_victims"),
        log_file=f"nibrs/item_imputation/item_imp_part2_nonperson/item_imp_part2_nonperson_{state_abbr}.log",
        shell=True,
    )


@task(task_run_name=item_imputation_part2_person_tr_name)
def item_imputation_part2_person(scratch_dir: Path, year: int, state_abbr: str) -> None:
    """Runs item imputation for person victims. It depends on part 1."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["DATA_YEAR"] = str(year)
    os.environ["INPUT_STATE"] = str(state_abbr)

    run_script(
        scratch_dir=scratch_dir,
        script=f"{RSCRIPT_ENV} Rscript 100_Run_Impute_Person_victims.R",
        cwd=Path("tasks/impute_items/part2_person_victims"),
        log_file=f"nibrs/item_imputation/item_imp_part2_person/item_imp_part2_person_{state_abbr}.log",
        shell=True,
    )


@task(task_run_name=item_imputation_part3_finalize_tr_name)
def item_imputation_part3_finalize(
    scratch_dir: Path, year: int, state_abbr: str
) -> None:
    """Finalizes item imputations. It depends on both parts of part 2."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["DATA_YEAR"] = str(year)
    os.environ["INPUT_STATE"] = str(state_abbr)

    run_script(
        scratch_dir=scratch_dir,
        script=f"{RSCRIPT_ENV} Rscript 100_Run_Impute_Final_Steps.R",
        cwd=Path("tasks/impute_items/part3_finalize"),
        log_file=f"nibrs/item_imputation/item_imp_part3_finalize/item_imp_part3_finalize_{state_abbr}.log",
        shell=True,
    )


@task(task_run_name=item_imputation_part3_5_ethnicity_tr_name)
def item_imputation_part3_5_ethnicity(
    scratch_dir: Path, year: int, ethnicity_num: int
) -> None:
    """Runs item imputation for ethnicity which depends on part 2 person and nonperson and part 3."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["DATA_YEAR"] = str(year)
    os.environ["ETHNICITY_INPUT_NUM"] = str(ethnicity_num)

    run_script(
        scratch_dir=scratch_dir,
        script=f"{RSCRIPT_ENV} Rscript 100_Run_Ethnicity.R",
        cwd=Path("tasks/impute_items/part3_5_ethnicity"),
        log_file=f"nibrs/item_imputation/item_imp_part3_5_ethnicity/item_imp_part3_5_ethnicity_{ethnicity_num}.log",
        shell=True,
    )


@task(task_run_name=item_imputation_part3_5_ethnicity_combine_tr_name)
def item_imputation_part3_5_ethnicity_combine(
    scratch_dir: Path, year: int, state_abbr: str
) -> None:
    """Combines ethnicity imputation by state. Depends on part 3_5."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["DATA_YEAR"] = str(year)
    os.environ["INPUT_STATE"] = str(state_abbr)

    run_script(
        scratch_dir=scratch_dir,
        script=f"{RSCRIPT_ENV} Rscript 100_Run_Ethnicity_Compile.R",
        cwd=Path("tasks/impute_items/part3_5_ethnicity"),
        log_file=f"nibrs/item_imputation/item_imp_part3_5_ethnicity/combined/item_imp_part3_5_ethnicity_combined_{state_abbr}.log",
        shell=True,
    )


@task(task_run_name=item_imputation_part4_victim_offender_relationship_tr_name)
def item_imputation_part4_victim_offender_relationship(
    scratch_dir: Path, year: int, state_abbr: str
) -> None:
    """Adds victim offender relationship imputation which depends on part 3."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["DATA_YEAR"] = str(year)
    os.environ["INPUT_STATE"] = str(state_abbr)

    run_script(
        scratch_dir=scratch_dir,
        script=f"{RSCRIPT_ENV} Rscript 100-Run_Programs_relationship_code.R",
        cwd=Path("tasks/impute_items/part4_victim_offender"),
        log_file=f"nibrs/item_imputation/item_imp_part4_vo_rel/item_imp_part4_vo_rel_{state_abbr}.log",
        shell=True,
    )


@task(task_run_name=item_imputation_part4_vor_property_tr_name)
def item_imputation_part4_vor_property(
    scratch_dir: Path, year: int, vor_num: str
) -> None:
    """Adds victim offender relationship imputation for property offenses which depends on part 3 and the earlier part 4."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["DATA_YEAR"] = str(year)
    os.environ["INPUT_NUM"] = str(vor_num)

    run_script(
        scratch_dir=scratch_dir,
        script=f"{RSCRIPT_ENV} Rscript 100-Run_Programs_relationship_code_Property.R",
        cwd=Path("tasks/impute_items/part4_victim_offender"),
        log_file=f"nibrs/item_imputation/item_imp_part4_vor_prop/item_imp_part4_vor_prop_{vor_num}.log",
        shell=True,
    )


@task(task_run_name=item_imputation_part5_groupb_arrestee_tr_name)
def item_imputation_part5_groupb_arrestee(scratch_dir: Path, external_dir: Path, year: int, state_abbr: str) -> None:
    """Adds arrestee imputation for group B offenses Does NOT depend on earlier item imputation tasks."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)
    os.environ["DATA_YEAR"] = str(year)
    os.environ["INPUT_STATE"] = str(state_abbr)

    run_script(
        scratch_dir=scratch_dir,
        script=f"{RSCRIPT_ENV} Rscript 100_Run_GroupB_part1.R",
        cwd=Path("tasks/impute_items/part5_groupb_arrestee"),
        log_file=f"nibrs/item_imputation/part5_groupb_arrestee/item_imp_part5_groupb_part1_{state_abbr}.log",
        shell=True,
    )


@task
def item_imputation_part5_groupb_arrestee_combine(scratch_dir: Path, external_dir: Path, year: int) -> None:
    """Imputation by ethnicity permutation group and combines group B arrestee imputation, depends on part 5."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)
    os.environ["DATA_YEAR"] = str(year)

    run_script(
        scratch_dir=scratch_dir,
        script=f"{RSCRIPT_ENV} Rscript 100_Run_GroupB_part2.R",
        cwd=Path("tasks/impute_items/part5_groupb_arrestee"),
        log_file=f"nibrs/item_imputation/part5_groupb_arrestee/item_imp_part5_groupb_part2.log",
        shell=True,
    )


@task
def weighting(
    scratch_dir: Path,
    year: int,
    external_dir: Path,
) -> None:
    """Generates weights. It depends on the partial reporter step."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["DATA_YEAR"] = str(year)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)

    if year == 2020:
        weighting_file = "00a_Weights_Creation_Main.R"
    else:
        weighting_file = "00a_Weights_Creation_Main_subSt.R"

    run_script(
        scratch_dir=scratch_dir,
        script=f"{RSCRIPT_ENV} Rscript {weighting_file}",
        cwd=Path("tasks/compute_weights"),
        log_file="nibrs/weighting.log",
        shell=True,
    )

    run_script(
        scratch_dir=scratch_dir,
        script=f"{RSCRIPT_ENV} Rscript Add_on_Calibration_Variables.R",
        cwd=Path("tasks/compute_weights"),
        log_file="nibrs/Add_on_Calibration_Variables.log",
        shell=True,
    )


@task(task_run_name=indicator_estimation_setup_tr_name, tags=["db_task"])
def indicator_estimation_setup(
    scratch_dir: Path,
    year: int,
    external_dir: Path,
    state_abbr: str,
) -> None:
    """Generates database extracts for each state which are needed for the Single tables."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)
    os.environ["DATA_YEAR"] = str(year)
    os.environ["INPUT_STATE"] = str(state_abbr)

    run_script(
        scratch_dir=scratch_dir,
        script=f"{RSCRIPT_ENV} Rscript 100_Run_Create_Datasets.R",
        cwd=Path("tasks/generate_estimates/Setup_part1_bystate"),
        log_file=f"nibrs/estimation_setup/indicator_estimation_setup_extract/indicator_setup_part1_{state_abbr}.log",
        shell=True,
    )


@task
def indicator_estimation_setup_part2_00a(
    scratch_dir: Path,
    year: int,
    external_dir: Path,
) -> None:
    """Merges the output of the previous step and runs additional preprocessing for all Tables."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)
    os.environ["DATA_YEAR"] = str(year)

    run_script(
        scratch_dir=scratch_dir,
        script="./00a_merge_setup_outputs.sh",
        cwd=Path("tasks/generate_estimates/Setup_part2_merged"),
        log_file="nibrs/estimation_setup/indicator_estimation_setup_merge/00a_Merge_Setup_Outputs.log",
    )


@task(task_run_name=indicator_estimation_setup_part2_00b_tr_name)
def indicator_estimation_setup_part2_00b(
    scratch_dir: Path,
    year: int,
    dataset: str,
    external_dir: Path,
) -> None:
    """Merges the output of the previous step and runs additional preprocessing for all Tables."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)
    os.environ["DATA_YEAR"] = str(year)
    os.environ["DATASET_TO_GENERATE"] = dataset

    run_script(
        scratch_dir=scratch_dir,
        script=f"{RSCRIPT_ENV} Rscript 100_Run_00b_Create_Datasets.R",
        cwd=Path("tasks/generate_estimates/Setup_part2_merged"),
        log_file=f"nibrs/estimation_setup/indicator_estimation_setup_merge/00b_Create_Datasets_{dataset}.log",
        shell=True,
    )


@task
def indicator_estimation_setup_part2_00b_weights(
    scratch_dir: Path,
    year: int,
    external_dir: Path,
) -> None:
    """Merges the output of the previous step and runs additional preprocessing for all Tables."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)
    os.environ["DATA_YEAR"] = str(year)

    run_script(
        scratch_dir=scratch_dir,
        script=f"{RSCRIPT_ENV} Rscript 100_Run_Process_Weights_and_Permutation.R",
        cwd=Path("tasks/generate_estimates/Setup_part2_merged"),
        log_file="nibrs/estimation_setup/indicator_estimation_setup_merge/100_Run_Create_Datasets_weighting.log",
        shell=True,
    )


@task(task_run_name=indicator_estimation_setup_part2_00c_clean_main_tr_name)
def indicator_estimation_setup_part2_00c_clean_main(
    scratch_dir: Path,
    year: int,
    main_to_run: str,
    external_dir: Path,
) -> None:
    """Merges the output of the previous step and runs additional preprocessing for all Tables."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)
    os.environ["DATA_YEAR"] = str(year)
    os.environ["SOURCE_TYPE"] = str(main_to_run)

    run_script(
        scratch_dir=scratch_dir,
        script="./00c_clean_main.sh",
        cwd=Path("tasks/generate_estimates/Setup_part2_merged"),
        log_file=f"nibrs/estimation_setup/indicator_estimation_setup_merge/clean_main_{main_to_run}.log",
    )


@task
def indicator_estimation_setup_part2_00d_agency_ori(
    scratch_dir: Path,
    year: int,
    external_dir: Path,
) -> None:
    """Merges the output of the previous step and runs additional preprocessing for all Tables."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)
    os.environ["DATA_YEAR"] = str(year)

    run_script(
        scratch_dir=scratch_dir,
        script=f"{RSCRIPT_ENV} Rscript 101_Run_Setup_Agency_ORI.R",
        cwd=Path("tasks/generate_estimates/Setup_part2_merged"),
        log_file="nibrs/estimation_setup/indicator_estimation_setup_merge/101_Run_Setup_Agency_ORI.log",
        shell=True,
    )


@task
def indicator_estimation_setup_gv_dataset(
    scratch_dir: Path,
    year: int,
    external_dir: Path,
) -> None:
    """Does some processing to create the main datasets for the new firearm tables."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)
    os.environ["DATA_YEAR"] = str(year)

    run_script(
        scratch_dir=scratch_dir,
        script=f"{RSCRIPT_ENV} Rscript 00c_Create_Firearm_Datasets.R",
        cwd=Path("tasks/generate_estimates/Setup_part2_merged"),
        log_file="nibrs/estimation_setup/indicator_estimation_setup_merge/00c_Create_Firearm_Datasets.log",
        shell=True,
    )


@task(task_run_name=indicator_estimation_tables_part1_preprocessing_tr_name)
def indicator_estimation_tables_part1_preprocessing(
    scratch_dir: Path,
    year: int,
    external_dir: Path,
    table_name: str,
) -> None:
    """Runs the preprocessing script for the given table."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)
    os.environ["DATA_YEAR"] = str(year)
    os.environ["DER_TABLE_NAME"] = str(table_name)

    if "DM" in table_name:
        folder_name = "Tables_Drug_Modules"
    elif "GV" in table_name:
        folder_name = "Tables_Firearms"
    elif "YT" in table_name:
        folder_name = "Tables_Youth_Homicide"
    else:
        folder_name = "Tables_Core"

    run_script(
        scratch_dir=scratch_dir,
        script=f"{RSCRIPT_ENV} Rscript Part1_prepare_datasets.R",
        cwd=Path(f"tasks/generate_estimates/{folder_name}/Table{table_name}"),
        log_file=f"nibrs/table_creation/indicator_estimation_part1_preprocessing/indicator_table_part1_{table_name}.log",
        shell=True,
    )


@task(task_run_name=indicator_estimation_tables_part2_generate_est_tr_name)
def indicator_estimation_tables_part2_generate_est(
    scratch_dir: Path,
    year: int,
    external_dir: Path,
    table_est_combo: tuple,
) -> None:
    """Runs the generate_est script for the given table."""
    table_name, est_num = table_est_combo

    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)
    os.environ["DATA_YEAR"] = str(year)
    os.environ["DER_TABLE_NAME"] = str(table_name)

    if "DM" in table_name:
        folder_name = "Tables_Drug_Modules"
    elif "GV" in table_name:
        folder_name = "Tables_Firearms"
    elif "YT" in table_name:
        folder_name = "Tables_Youth_Homicide"
    else:
        folder_name = "Tables_Core"

    run_script(
        scratch_dir=scratch_dir,
        script=f"{RSCRIPT_ENV} Rscript ../../Tables_Shared_Scripts/generate_estimates.R {est_num}",
        cwd=Path(f"tasks/generate_estimates/{folder_name}/Table{table_name}"),
        log_file=f"nibrs/table_creation/indicator_estimation_part2_generate_est/indicator_table_gen_est_{table_name}_{est_num}.log",
        shell=True,
    )


@task
def indicator_estimation_tables_part2_create_additional_columns(
    scratch_dir: Path,
    year: int,
    external_dir: Path,
    add_col_combo: tuple,
) -> None:
    """Runs the create_additional_columns script for the given table."""
    table_name, column_num = add_col_combo

    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)
    os.environ["DATA_YEAR"] = str(year)
    os.environ["DER_TABLE_NAME"] = str(table_name)

    if "DM" in table_name:
        folder_name = "Tables_Drug_Modules"
    elif "GV" in table_name:
        folder_name = "Tables_Firearms"
    else:
        folder_name = "Tables_Core"

    for i in range(1,DEMOGRAPHIC_COLUMN_NUMBERS[table_name]+1):
        run_script(
            scratch_dir=scratch_dir,
            script=f"{RSCRIPT_ENV} Rscript ../../Tables_Shared_Scripts/create_additional_columns.R {column_num} {i}",
            cwd=Path(f"tasks/generate_estimates/{folder_name}/Table{table_name}"),
            log_file=f"nibrs/table_creation/indicator_estimation_part2_create_additional_columns/indicator_table_addcols_{table_name}_{column_num}_{i}.log",
            shell=True,
        )


@task(task_run_name=indicator_estimation_tables_part3_finalize_tr_name)
def indicator_estimation_tables_part3_finalize(
    scratch_dir: Path,
    year: int,
    external_dir: Path,
    table_name: str,
) -> None:
    """Runs the finalize script for the given table."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)
    os.environ["DATA_YEAR"] = str(year)
    os.environ["DER_TABLE_NAME"] = str(table_name)

    if "DM" in table_name:
        folder_name = "Tables_Drug_Modules"
    elif "GV" in table_name:
        folder_name = "Tables_Firearms"
    elif "YT" in table_name:
        folder_name = "Tables_Youth_Homicide"
    else:
        folder_name = "Tables_Core"

    run_script(
        scratch_dir=scratch_dir,
        script=f"{RSCRIPT_ENV} Rscript Part3_finalize.R",
        cwd=Path(f"tasks/generate_estimates/{folder_name}/Table{table_name}"),
        log_file=f"nibrs/table_creation/indicator_estimation_part3_finalize/indicator_table_part3_{table_name}.log",
        shell=True,
    )


@task(task_run_name=indicator_estimation_tables_part4_select_tables_tr_name)
def indicator_estimation_tables_part4_select_tables(
    scratch_dir: Path,
    year: int,
    external_dir: Path,
    table_name: str,
) -> None:
    """Runs the part B script for the given table."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)
    os.environ["DATA_YEAR"] = str(year)
    os.environ["DER_TABLE_NAME"] = str(table_name)

    if "GV" in table_name:
        folder_name = "Tables_Firearms"
    else:
        folder_name = "Tables_Core"

    run_script(
        scratch_dir=scratch_dir,
        script=f"{RSCRIPT_ENV} Rscript Part4_B.R",
        cwd=Path(f"tasks/generate_estimates/{folder_name}/Table{table_name}"),
        log_file=f"nibrs/table_creation/indicator_estimation_part4_and_5/indicator_table_part4_B_{table_name}.log",
        shell=True,
    )


@task(task_run_name=indicator_estimation_tables_part5_select_tables_tr_name)
def indicator_estimation_tables_part5_select_tables(
    scratch_dir: Path,
    year: int,
    external_dir: Path,
    table_name: str,
) -> None:
    """Runs the part C script for the given table."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)
    os.environ["DATA_YEAR"] = str(year)
    os.environ["DER_TABLE_NAME"] = str(table_name)

    if "GV" in table_name:
        folder_name = "Tables_Firearms"
    else:
        folder_name = "Tables_Core"

    run_script(
        scratch_dir=scratch_dir,
        script=f"{RSCRIPT_ENV} Rscript Part5_C.R",
        cwd=Path(f"tasks/generate_estimates/{folder_name}/Table{table_name}"),
        log_file=f"nibrs/table_creation/indicator_estimation_part4_and_5/indicator_table_part5_C_{table_name}.log",
        shell=True,
    )


@task
def indicator_estimation_part4_gv_combine_tables(
    scratch_dir: Path,
    year: int,
    external_dir: Path,
) -> None:
    """Runs the part C script for the given table."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)
    os.environ["DATA_YEAR"] = str(year)

    run_script(
        scratch_dir=scratch_dir,
        script=f"{RSCRIPT_ENV} Rscript Part4_update_GV2a_RD.R",
        cwd=Path("tasks/generate_estimates/Tables_Firearms/TableGV2b"),
        log_file="nibrs/table_creation/indicator_estimation_part4_and_5/indicator_table_part4_gv_combine_GV2.log",
        shell=True,
    )


@task
def indicator_estimation_demo_skips(
    scratch_dir: Path,
    year: int,
    external_dir: Path,
) -> None:
    """Merges the output of the previous step and runs additional preprocessing for all Tables."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)
    os.environ["DATA_YEAR"] = str(year)

    run_script(
        scratch_dir=scratch_dir,
        script=f"{RSCRIPT_ENV} Rscript 100_Find_Demo_Skips.R",
        cwd=Path("tasks/generate_estimates/demo_skips"),
        log_file="nibrs/table_creation/indicator_estimation_demo_skips/100_Find_Demo_Skips.log",
        shell=True,
    )


@task
def copula_imputation_step1(
    scratch_dir: Path,
    year: int,
    external_dir: Path,
    permutation_table: list,
) -> None:
    """Runs preprocessing step for copula imputation. Depends on the tables estimation."""
    table, permutation = permutation_table
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)
    os.environ["DATA_YEAR"] = str(year)
    os.environ["TABLE_NAME"] = str(table)
    os.environ["DER_CURRENT_PERMUTATION_NUM"] = str(permutation)

    run_script(
        scratch_dir=scratch_dir,
        script="./part1_prep_data.sh",
        cwd=Path("tasks/copula_imputation/part1_prep_data"),
        log_file=f"nibrs/copula/copula_imp_part1_{table}/copula_part1_prep_{table}_{permutation}.log",
    )


@task
def copula_imputation_step2_imp(
    scratch_dir: Path,
    year: int,
    external_dir: Path,
    combo: list,
) -> None:
    """Generates copula imputation for a specific table, permutation, and sometimes column set."""
    table_perm_column, strat = combo
    table_perm, column = table_perm_column
    table, permutation = table_perm

    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)
    os.environ["DATA_YEAR"] = str(year)
    os.environ["TABLE_NAME"] = str(table)
    os.environ["DER_CURRENT_PERMUTATION_NUM"] = str(permutation)
    os.environ["COLUMN_INDEX"] = str(column)
    os.environ["STRAT_VAR"] = str(strat)

    log_file_name = f"nibrs/copula/copula_imputation_part2imp_{table}/copula_imp_part2_{table}_{permutation}_part{column}_strat{strat}"
    if STOP_COPULA_AFTER_PART1:
        os.environ["STOP_AFTER_PART1"] = "1"
        log_file_name += "_part1only.log"
    else:
        os.environ["STOP_AFTER_PART1"] = "0"
        log_file_name += ".log"

    run_script(
        scratch_dir=scratch_dir,
        script="./part2_impute.sh",
        cwd=Path("tasks/copula_imputation/part2_impute"),
        log_file=log_file_name,
    )


@task
def copula_imputation_step2_stack(
    scratch_dir: Path,
    year: int,
    external_dir: Path,
    permutation_table: list,
) -> None:
    """Merges the output from the copula imputation step."""
    table, permutation = permutation_table

    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)
    os.environ["DATA_YEAR"] = str(year)
    os.environ["TABLE_NAME"] = str(table)
    os.environ["DER_CURRENT_PERMUTATION_NUM"] = str(permutation)

    run_script(
        scratch_dir=scratch_dir,
        script=f"timeout --verbose 2h {RSCRIPT_ENV} Rscript 100_Run_Copula_Stack.R",
        cwd=Path("tasks/copula_imputation/part2_impute"),
        log_file=f"nibrs/copula/copula_imputation_part2stack_{table}/copula_imp_part2_stack_{table}_{permutation}.log",
    )


@task(task_run_name=copula_imputation_step2_summary_tr_name)
def copula_imputation_step2_summary(
    scratch_dir: Path, year: int, external_dir: Path, table: str
) -> None:
    """Fills in the table shell from the copula outputs. Depends on part 2."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)
    os.environ["TABLE_NAME"] = str(table)
    os.environ["DATA_YEAR"] = str(year)

    run_script(
        scratch_dir=scratch_dir,
        script=f"{RSCRIPT_ENV} Rscript Stack_Copula_Summary_Tables.R",
        cwd=Path("tasks/copula_imputation/part2_impute"),
        log_file=f"nibrs/copula/copula_summary/copula_imputation_stack_summary_{table}.log",
        shell=True,
    )


@task
def validation_copula_imputation_step2(
    scratch_dir: Path,
    year: int,
    external_dir: Path,
    permutation_table: list,
) -> None:
    """Runs validation on copula section 2."""
    table, permutation = permutation_table

    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)
    os.environ["DATA_YEAR"] = str(year)
    os.environ["TABLE_NAME"] = str(table)
    os.environ["DER_CURRENT_PERMUTATION_NUM"] = str(permutation)

    run_script(
        scratch_dir=scratch_dir,
        script=f"{RSCRIPT_ENV} Rscript 100_Run_Copula_Imputation_Validation_Instance.R",
        cwd=Path("tasks/validation/copula_imputation"),
        log_file=f"nibrs/validation/copula/copula_imputation_part2_{table}/copula_imp_part2_{table}_{permutation}.log",
        shell=True,
    )


@task
def copula_imputation_step3_01_template(
    scratch_dir: Path,
    year: int,
    external_dir: Path,
) -> None:
    """Fills in the table shell from the copula outputs. Depends on part 2."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)
    os.environ["DATA_YEAR"] = str(year)

    run_script(
        scratch_dir=scratch_dir,
        script=f"{RSCRIPT_ENV} Rscript 01_Create_Template_Indicator_Tabel_Rel_Bias.R",
        cwd=Path("tasks/copula_imputation/part3_generate_prb"),
        log_file="nibrs/copula/copula_imp_part3_01_create_template.log",
        shell=True,
    )


@task()
def copula_part_3_2_and_indicator_estimation_variance(
    scratch_dir: Path,
    year: int,
    external_dir: Path,
    permutation_tables: tuple,
) -> None:
    """Generates indicator estimates. It depends on imputation and weighting."""
    for permutation_table in permutation_tables:
        table, permutation_num = permutation_table

        os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
        os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
        os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)
        os.environ["DATA_YEAR"] = str(year)
        os.environ["DER_CURRENT_PERMUTATION_NUM"] = str(permutation_num)
        os.environ["TABLE_NAME"] = str(table)

        run_script(
            scratch_dir=scratch_dir,
            script="./generate_prb.sh",
            cwd=Path("tasks/copula_imputation/part3_generate_prb"),
            log_file=f"nibrs/copula/copula_imputation_part3_{table}/copula_imp_part3_02_{table}_perm_{permutation_num}.log",
            shell=True,
        )

        run_script(
            scratch_dir=scratch_dir,
            script=f"{RSCRIPT_ENV} Rscript -e \"source('100_Run_Table_Programs.R', keep.source=TRUE)\"",
            cwd=Path("tasks/generate_estimates/Variance"),
            log_file=f"nibrs/variance/variance_{table}/variance_table_{table}_perm_{permutation_num}.log",
            shell=True,
        )


@task(task_run_name=fill_variance_skipped_demos_tr_name)
def fill_variance_skipped_demos(
    scratch_dir: Path,
    external_dir: Path,
    year: int,
    combo: list,
) -> None:
    """Generates zero filled post-variance files for skipped demographic/table combinations."""
    table, demo_perm = combo

    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)
    os.environ["DATA_YEAR"] = str(year)
    os.environ["TABLE_NAME"] = str(table)
    os.environ["DEMO_PERM"] = str(demo_perm)

    run_script(
        scratch_dir=scratch_dir,
        script=f"{RSCRIPT_ENV} Rscript 200_Fill_Demo_Skips.R",
        cwd=Path("tasks/generate_estimates/demo_skips"),
        log_file=f"nibrs/variance/indicator_estimation_demo_skips/variance_fill_table{table}_demo_{demo_perm}.log",
        shell=True,
    )


@task
def optional_final_estimates_blank_momentum(
    scratch_dir: Path,
    year: int,
    external_dir: Path,
) -> None:
    """Creates a blank momentum rule file for the geographies specified in the program."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)
    os.environ["DATA_YEAR"] = str(year)

    run_script(
        scratch_dir=scratch_dir,
        script=f"{RSCRIPT_ENV} Rscript Optional_Make_Blank_Momentum_Rule.R",
        cwd=Path("tasks/make_final_dataset"),
        log_file="nibrs/final_estimates/final_estimates_blank_momentum.log",
        shell=True,
    )


@task(task_run_name=final_estimates_momentum_tr_name)
def final_estimates_momentum(
    scratch_dir: Path,
    year: int,
    external_dir: Path,
    combo: list,
) -> None:
    """Generates final estimates. It depends on the variance step."""
    permutation_name, top_level_folder, mid_level_folder = combo

    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["DATA_YEAR"] = str(year)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)
    os.environ["PERMUTATION_NAME"] = str(permutation_name)
    os.environ["TOP_FOLDER"] = str(top_level_folder)
    os.environ["MID_FOLDER"] = str(mid_level_folder)

    run_script(
        scratch_dir=scratch_dir,
        script=f"{RSCRIPT_ENV} Rscript 10000_Make_Momentum_Rule.R",
        cwd=Path("tasks/make_final_dataset"),
        log_file=f"nibrs/final_estimates/final_estimates_momentum/final_estimates_momentum_{permutation_name}.log",
        shell=True,
    )


@task
def final_estimates_suppression(
    scratch_dir: Path,
    year: int,
    external_dir: Path,
    combo: list,
) -> None:
    """Generates final estimates. It depends on the variance step."""
    table, perm_folders = combo
    permutation_name, top_level_folder, mid_level_folder = perm_folders

    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["DATA_YEAR"] = str(year)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)
    os.environ["PERMUTATION_NAME"] = str(permutation_name)
    os.environ["TOP_FOLDER"] = str(top_level_folder)
    os.environ["MID_FOLDER"] = str(mid_level_folder)
    os.environ["TABLE_NAME"] = str(table)
    os.environ["ESTIMATES_DB_NAME"] = ESTIMATES_DB_NAME

    run_script(
        scratch_dir=scratch_dir,
        script=f"{RSCRIPT_ENV} Rscript 10001_Make_Final_Database.R",
        cwd=Path("tasks/make_final_dataset"),
        log_file=f"nibrs/final_estimates/final_estimates_suppression_{table}/final_estimates_suppression_{table}_{permutation_name}.log",
        shell=True,
    )

    run_script(
        scratch_dir=scratch_dir,
        script="python upload_estimates.py",
        cwd=Path("tasks/generate_estimates_database"),
        log_file=f"nibrs/generate_estimate_db/final_estimates_database_{table}/final_estimates_db_{table}_{permutation_name}.log",
        shell=True,
    )


@task
def final_estimates_merged(
    scratch_dir: Path,
    year: int,
    external_dir: Path,
) -> None:
    """Generates final estimates. It depends on the permutation step."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["DATA_YEAR"] = str(year)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)

    run_script(
        scratch_dir=scratch_dir,
        script="python 10001_Combine_Final_Database.py",
        cwd=Path("tasks/make_final_dataset"),
        log_file="nibrs/final_estimates/final_estimates_merged.log",
        shell=True,
    )


# functions for NIBRS flow tasks - validation
@task
def qc_for_input_data(
    scratch_dir: Path,
    year: int,
    external_dir: Path,
) -> None:
    """Generates first set of input data QC reports."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["DATA_YEAR"] = str(year)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)

    run_script(
        scratch_dir=scratch_dir,
        script="./qc_input_data.sh",
        cwd=Path("tasks/qc_input_data"),
        log_file="nibrs/validation/qc_for_input_data.log",
    )


@task
def qc_for_input_data_missingness(
    scratch_dir: Path,
    year: int,
    external_dir: Path,
) -> None:
    """Generates the data missingness QC reports."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["DATA_YEAR"] = str(year)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)

    run_script(
        scratch_dir=scratch_dir,
        script="./qc_input_data_missingness.sh",
        cwd=Path("tasks/qc_input_data"),
        log_file="nibrs/validation/qc_for_input_data_missingness.log",
    )


@task(task_run_name=qc_for_input_data_missingness_bystate_tr_name, tags=["db_task"])
def qc_for_input_data_missingness_bystate(
    scratch_dir: Path,
    year: int,
    state_abbr: str,
    external_dir: Path,
) -> None:
    """Generates the data missingness QC reports."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["DATA_YEAR"] = str(year)
    os.environ["INPUT_STATE"] = str(state_abbr)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)

    run_script(
        scratch_dir=scratch_dir,
        script="./qc_input_data_missingness_bystate.sh",
        cwd=Path("tasks/qc_input_data"),
        log_file=f"nibrs/validation/qc_for_input_data_missingness_bystate/qc_for_input_data_missingness_{state_abbr}.log",
    )


@task
def qc_for_input_data_missingness_bystate_merge(
    scratch_dir: Path,
    year: int,
    external_dir: Path,
) -> None:
    """Generates the data missingness QC report with all states."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["DATA_YEAR"] = str(year)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)

    run_script(
        scratch_dir=scratch_dir,
        script="python qc_for_missingness_merge.py",
        cwd=Path("tasks/qc_input_data"),
        log_file="nibrs/validation/qc_for_input_data_missingness_merged.log",
        shell=True,
    )


@task
def qc_for_input_data_partial_reporters(
    scratch_dir: Path,
    year: int,
) -> None:
    """Generates the partial reporters QC reports."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["DATA_YEAR"] = str(year)

    run_script(
        scratch_dir=scratch_dir,
        script="./qc_input_data_partial_reporters.sh",
        cwd=Path("tasks/qc_input_data"),
        log_file="nibrs/validation/qc_for_input_data_partial_reporters.log",
    )


@task
def validation_population(
    scratch_dir: Path,
    year: int,
    external_dir: Path,
) -> None:
    """Runs validation tables on the population inputs. Does not depend on pipeline tasks."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)
    os.environ["DATA_YEAR"] = str(year)

    run_script(
        scratch_dir=scratch_dir,
        script=f"{RSCRIPT_ENV} Rscript 100_Run_Pop_Validation.R",
        cwd=Path("tasks/validation/population"),
        log_file="nibrs/validation/population_validation_with_tables.log",
        shell=True,
    )


@task(task_run_name=validation_extract_bystate_tr_name)
def validation_extract_bystate(
    scratch_dir: Path,
    year: int,
    external_dir: Path,
    state_abbr: str,
) -> None:
    """Generates database extracts for each state which are needed for validation."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)
    os.environ["DATA_YEAR"] = str(year)
    os.environ["INPUT_STATE"] = str(state_abbr)

    run_script(
        scratch_dir=scratch_dir,
        script=f"{RSCRIPT_ENV} Rscript 1000-Run_Table_Programs.R",
        cwd=Path("tasks/validation/extracts"),
        log_file=f"nibrs/validation/extract_bystate/validation_extracts_{state_abbr}.log",
        shell=True,
    )


@task
def validation_extract_merge(
    scratch_dir: Path,
    year: int,
    external_dir: Path,
) -> None:
    """Merges the output of the previous step for validation."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)
    os.environ["DATA_YEAR"] = str(year)

    run_script(
        scratch_dir=scratch_dir,
        script=f"{RSCRIPT_ENV} Rscript 01_Merge_Extracts.R",
        cwd=Path("tasks/validation/extracts"),
        log_file="nibrs/validation/validation_extracts_merged.log",
        shell=True,
    )


@task
def validation_item_imputation(
    scratch_dir: Path,
    year: int,
    external_dir: Path,
) -> None:
    """Runs validation tables on the item imputation outputs. Does not depend on pipeline tasks."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)
    os.environ["DATA_YEAR"] = str(year)

    run_script(
        scratch_dir=scratch_dir,
        script=f"{RSCRIPT_ENV} Rscript 1000_Run_Table_Programs.R",
        cwd=Path("tasks/validation/impute_items"),
        log_file="nibrs/validation/item_imputation_validation_with_tables.log",
        shell=True,
    )


@task
def validation_block_imputation(
    scratch_dir: Path,
    year: int,
    external_dir: Path,
) -> None:
    """Runs validation tables on the block imputation outputs. Does not depend on pipeline tasks."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)
    os.environ["DATA_YEAR"] = str(year)

    run_script(
        scratch_dir=scratch_dir,
        script=f"{RSCRIPT_ENV} Rscript 1000_Run_Table_Programs.R",
        cwd=Path("tasks/validation/impute_blocks"),
        log_file="nibrs/validation/block_imputation_validation_with_tables.log",
        shell=True,
    )


@task
def validation_copula_imputation_aggregate(
    scratch_dir: Path,
    year: int,
    external_dir: Path,
) -> None:
    """Runs validation tables on the block imputation outputs. Does not depend on pipeline tasks."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)
    os.environ["DATA_YEAR"] = str(year)

    run_script(
        scratch_dir=scratch_dir,
        script=f"{RSCRIPT_ENV} Rscript 100_Run_Copula_Imputation_Validation_Aggregate.R",
        cwd=Path("tasks/validation/copula_imputation"),
        log_file="nibrs/validation/copula_imputation/copula_imp_step1_aggregate.log",
        shell=True,
    )


@task
def validation_data_quality(
    scratch_dir: Path,
    year: int,
    external_dir: Path,
) -> None:
    """Runs validation tables for data quality of the database."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)
    os.environ["DATA_YEAR"] = str(year)

    run_script(
        scratch_dir=scratch_dir,
        script=f"{RSCRIPT_ENV} Rscript 100_Run_DQ_Validation.R",
        cwd=Path("tasks/validation/data_quality"),
        log_file="nibrs/validation/data_quality_validation.log",
        shell=True,
    )


# smoketest functions
@task
def run_smoketest_part1a(
    scratch_dir: Path,
    year: int,
) -> None:
    """Runs part 1a of the "smoketest" tasks, which exercise various components of the pipeline."""
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["DATA_YEAR"] = str(year)

    run_script(
        scratch_dir=scratch_dir,
        script=f"{RSCRIPT_ENV} Rscript run_smoketest_part1a.R",
        cwd=Path("tasks/run_smoketest"),
        log_file="smoketest/smoketest_part1/run_smoketest_part1a.log",
        shell=True,
    )


@task
def run_smoketest_part1b(
    scratch_dir: Path,
    year: int,
    external_dir: Path,
) -> None:
    """Runs part 1b of the "smoketest" tasks, which exercise various components of the pipeline."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["DATA_YEAR"] = str(year)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)

    run_script(
        scratch_dir=scratch_dir,
        script=f"{RSCRIPT_ENV} Rscript run_smoketest_part1b.R",
        cwd=Path("tasks/run_smoketest"),
        log_file="smoketest/smoketest_part1/run_smoketest_part1b.log",
        shell=True,
    )


@task
def run_smoketest_part2(
    scratch_dir: Path,
    year: int,
) -> None:
    """Runs part 2 of the "smoketest" tasks, which exercise various components of the pipeline."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["DATA_YEAR"] = str(year)

    run_script(
        scratch_dir=scratch_dir,
        script="./run_smoketest_part2.sh",
        cwd=Path("tasks/run_smoketest"),
        log_file="smoketest/run_smoketest_part2.log",
    )


@task
def collect_task_metrics(scratch_dir: Path) -> None:
    """Collects performance metrics for a flow's tasks."""
    logs_dir = scratch_dir / "log_files"

    all_metrics = []

    for log_file in logs_dir.glob("**/*.log"):
        task_metrics: Dict[str, Any] = {"log_file": log_file.relative_to(logs_dir)}

        mod_time = datetime.fromtimestamp(log_file.stat().st_mtime, tz=timezone.utc)
        task_metrics["mod_time"] = mod_time

        result = subprocess.run(
            f"tail -30 {log_file}",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            shell=True,
        )
        for line in result.stdout.split("\n"):
            # Example line from the log file:
            #   Maximum resident set size (kbytes): 87388
            pattern = r"^\s*Maximum resident set size \(kbytes\): (\d+)$"
            m = re.match(pattern, line)
            if m:
                task_metrics["mem_gb"] = round(int(m.group(1)) / 1024 / 1024, 3)
                continue

            # Example line from the log file:
            #   Percent of CPU this job got: 87%
            pattern = r"^\s*Percent of CPU this job got: (\d+)%$"
            m = re.match(pattern, line)
            if m:
                task_metrics["cpu_pct"] = int(m.group(1))
                continue

            # Example line from the log file:
            #   Elapsed (wall clock) time (h:mm:ss or m:ss): 0:02.79
            pattern = r"^\s*Elapsed \(wall clock\) time \(h:mm:ss or m:ss\): (?:(?P<hours>\d+):)?(?P<minutes>\d+):(?P<seconds>\d+)\.\d+$"
            m = re.match(pattern, line)
            if m:
                minutes: float = 0
                if m.group("hours"):
                    minutes += int(m.group("hours")) * 60
                minutes += int(m.group("minutes"))
                minutes += int(m.group("seconds")) / 60
                task_metrics["minutes"] = round(minutes, 2)
                continue

            # Example line from the log file:
            #   Exit status: 0
            pattern = r"^\s*Exit status: (\d+)$"
            m = re.match(pattern, line)
            if m:
                task_metrics["exit_status"] = int(m.group(1))
                continue

        all_metrics.append(task_metrics)

    metrics_file = scratch_dir / "task_metrics.csv"
    logger = get_run_logger()
    logger.info(f"Saving task metrics to {metrics_file}")
    pd.DataFrame(all_metrics).to_csv(metrics_file, index=False)


@task
def create_estimates_database() -> None:
    """Initializes the estimates database. This can run any time."""
    existing_db = DatabaseManager(
        os.getenv("PGHOST"),
        os.getenv("PGPORT"),
        os.getenv("PGDATABASE"),
        os.getenv("PGUSER"),
        os.getenv("PGPASSWORD"),
    )
    if not existing_db.db_exists(ESTIMATES_DB_NAME):
        existing_db.create_database(ESTIMATES_DB_NAME)


@task
def create_initial_estimate_lookup_files(
    scratch_dir: Path,
    year: int,
    external_dir: Path,
) -> None:
    """Initializes the population and estimate lookups. This can run any time."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["DATA_YEAR"] = str(year)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)
    os.environ["ESTIMATES_DB_NAME"] = ESTIMATES_DB_NAME

    run_script(
        scratch_dir=scratch_dir,
        script="python create_metadata_files.py",
        cwd=Path("tasks/generate_estimates_database"),
        log_file="nibrs/generate_estimate_db/create_initial_lookup_files.log",
        shell=True,
    )


@task
def create_estimates_index() -> None:
    """Adds index to estimates database."""
    estimates_db = DatabaseManager(
        os.getenv("PGHOST"),
        os.getenv("PGPORT"),
        ESTIMATES_DB_NAME,
        os.getenv("PGUSER"),
        os.getenv("PGPASSWORD"),
    )
    estimates_db.run_sql(f"""
        ALTER TABLE estimates ADD CONSTRAINT estimates_varname_permnum_ratedomain_estimatetype_ix UNIQUE (
                         der_variable_name,
                         permutation_number,
                         rate_specific_domain,
                         estimate_type_num
                         );
    """)
