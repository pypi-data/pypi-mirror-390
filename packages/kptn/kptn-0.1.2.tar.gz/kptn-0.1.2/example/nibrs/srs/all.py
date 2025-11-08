import json
import os
from itertools import product
from pathlib import Path
from typing import Tuple

import pandas as pd
from prefect import task

from tasks.all import run_script, write_mapped_task_list
from tasks.constants import RSCRIPT_ENV
from tasks.task_run_name import (
    srs_conversion_bystate_tr_name,
    srs_copula_imputation_step1_tr_name,
    srs_copula_imputation_step2_imp_tr_name,
    srs_copula_imputation_step2_stack_tr_name,
    srs_indicators_estimated_tables_part1_preprocessing_tr_name,
    srs_indicators_estimated_tables_part2_generate_est_tr_name,
    srs_indicators_estimated_tables_part3_finalize_tr_name,
    srs_qc_conversion_reports_tr_name,
)


@task
def srs_indicator_estimation_get_table_combinations(
    scratch_dir: Path,
    method30: bool = False,
) -> Tuple[list, list]:
    """Get lists needed for each step of the table estimation for SRS."""
    if method30:
        base_tables = ["SRS1a", "SRS1araw"]
        est_table_ranges = {
            "SRS1a": list(range(1, 10)),
            "SRS1araw": list(range(1, 10)),
        }
    else:
        base_tables = ["SRS1a", "SRS2a", "SRS1araw"]
        est_table_ranges = {
            "SRS1a": list(range(1, 10)),
            "SRS2a": list(range(1, 10)),
            "SRS1araw": list(range(1, 10)),
        }
    generate_est_combos = []
    for table, cols in est_table_ranges.items():
        generate_est_combos += list(product([table], cols))

    write_mapped_task_list(scratch_dir, base_tables, "SRS_est_base_tables_list.txt")
    write_mapped_task_list(
        scratch_dir,
        generate_est_combos,
        "SRS_table_est_generate_est_list.txt",
    )

    return base_tables, generate_est_combos


@task
def srs_tables_list(
    scratch_dir: Path,
    method30: bool = False,
) -> list:
    """Return the list of base tables used for SRS estimation."""
    base_tables, _ = srs_indicator_estimation_get_table_combinations.fn(  # type: ignore[attr-defined]
        scratch_dir=scratch_dir,
        method30=method30,
    )
    write_mapped_task_list(scratch_dir, base_tables, "srs_tables_list.txt")
    return base_tables


@task
def srs_estimate_combos_list(
    scratch_dir: Path,
    method30: bool = False,
) -> list:
    """Return the table/estimate combinations used for SRS estimation."""
    _, generate_est_combos = srs_indicator_estimation_get_table_combinations.fn(  # type: ignore[attr-defined]
        scratch_dir=scratch_dir,
        method30=method30,
    )
    write_mapped_task_list(
        scratch_dir,
        generate_est_combos,
        "srs_estimate_combos_list.txt",
    )
    return generate_est_combos


@task
def srs_copula_step1_tables_list(
    scratch_dir: Path,
    method30: bool = False,
) -> list:
    """Return the tables processed during the first step of the copula pipeline."""
    if method30:
        tables = ["SRS1a"]
    else:
        tables = ["SRS1a", "SRS2a"]
    write_mapped_task_list(
        scratch_dir,
        tables,
        "srs_copula_imputation_step1_tables_list.txt",
    )
    return tables


@task
def srs_get_variance_table_list(
    scratch_dir: Path,
    external_config: Path,
    external_dir: Path,
    year: int,
    method30: bool = False,
) -> list:
    """Read in the population file to get the set of permutations."""
    if method30:
        permutation_list = [1]
        all_combinations = list(product(["SRS1a"], permutation_list)) + list(
            product(["SRS1araw"], permutation_list)
        )
    else:
        with open(external_config, "r") as ex_path_f:
            path_dict = json.load(ex_path_f)[str(year)]
            population_path = path_dict["population_srs"]
            exclude_path = path_dict["exclusion_srs"]

            population_df = pd.read_csv(
                external_dir / population_path, usecols=["PERMUTATION_NUMBER"]
            )
            permutation_list = population_df["PERMUTATION_NUMBER"].astype(int).tolist()

            exclude = pd.read_csv(
                external_dir / exclude_path, usecols=["PERMUTATION_NUMBER"]
            )
            exclude_list = exclude["PERMUTATION_NUMBER"].astype(int).tolist()

            permutation_list = [x for x in permutation_list if x not in exclude_list]

            # table 1 is crossed with everything while table 2 is only for national
            all_combinations = (
                list(product(["SRS1a"], permutation_list))
                + [("SRS2a", 1)]
                + list(product(["SRS1araw"], permutation_list))
            )

    write_mapped_task_list(scratch_dir, all_combinations, "srs_variance_table_list.txt")

    return all_combinations


@task
def srs_get_final_estimation_permutation_list(
    scratch_dir: Path,
    external_config: Path,
    external_dir: Path,
    year: int,
) -> list:
    """Returns the list of basic permutations we want final estimate files for."""
    with open(external_config, "r") as ex_path_f:
        path_dict = json.load(ex_path_f)[str(year)]
        population_path = path_dict["population_srs"]
        exclude_path = path_dict["exclusion_srs"]

    population_df = pd.read_csv(
        external_dir / population_path, usecols=["PERMUTATION_NUMBER"]
    )
    permutation_list = population_df["PERMUTATION_NUMBER"].astype(int).tolist()

    exclude = pd.read_csv(external_dir / exclude_path, usecols=["PERMUTATION_NUMBER"])
    exclude_list = exclude["PERMUTATION_NUMBER"].astype(int).tolist()

    permutation_list = [x for x in permutation_list if x not in exclude_list]

    write_mapped_task_list(
        scratch_dir, permutation_list, "srs_final_permutations_list.txt"
    )

    return permutation_list


@task
def srs_get_copula_part2_combos(tables: list | None = None, method30: bool = False) -> list:
    """Generates table by stratifications."""
    if method30:
        selected_tables = ["SRS1a"]
    elif tables:
        selected_tables = list(tables)
    else:
        selected_tables = ["SRS1a", "SRS2a"]

    all_combos = []
    for t in selected_tables:
        all_combos += [[t, i] for i in range(1, 9)]
    return all_combos


# flow tasks for SRS
@task(task_run_name=srs_conversion_bystate_tr_name, tags=["db_task"])
def srs_conversion_bystate(
    scratch_dir: Path,
    year: int,
    external_dir: Path,
    state_abbr: str,
) -> None:
    """Generates database extracts for each state and applies SRS rules."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)
    os.environ["DATA_YEAR"] = str(year)
    os.environ["INPUT_STATE"] = str(state_abbr)

    run_script(
        scratch_dir=scratch_dir,
        script=f"{RSCRIPT_ENV} Rscript 1001_Run_SRS_byState.R",
        cwd=Path("srs/conversion"),
        log_file=f"srs/conversion/srs_extract_implement_rule_{state_abbr}.log",
        shell=True,
    )


@task
def srs_conversion(
    scratch_dir: Path,
    year: int,
    external_dir: Path,
) -> None:
    """Adds block imputation of NIBRS reporters to SRS."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)
    os.environ["DATA_YEAR"] = str(year)

    run_script(
        scratch_dir=scratch_dir,
        script=f"{RSCRIPT_ENV} Rscript 1002_Run_SRS_Block_Combine.R",
        cwd=Path("srs/conversion"),
        log_file="srs/srs_add_blockimp_combine.log",
        shell=True,
    )


@task
def srs_weighting(
    scratch_dir: Path,
    year: int,
    external_dir: Path,
    method30: bool = False,
) -> None:
    """Generates weights for SRS. It has no dependencies."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["DATA_YEAR"] = str(year)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)

    if method30:
        run_script(
            scratch_dir=scratch_dir,
            script=f"{RSCRIPT_ENV} Rscript 00_Weights_Creation_Master_National_SRS.R",
            cwd=Path("srs/compute_weights"),
            log_file="srs/weighting_srs.log",
            shell=True,
        )

        run_script(
            scratch_dir=scratch_dir,
            script=f"{RSCRIPT_ENV} Rscript Add_on_Calibration_Variables_National_SRS.R",
            cwd=Path("srs/compute_weights"),
            log_file="srs/Add_on_Calibration_Variables_SRS.log",
            shell=True,
        )
    else:
        run_script(
            scratch_dir=scratch_dir,
            script=f"{RSCRIPT_ENV} Rscript 00_Weights_Creation_Master_SRS.R",
            cwd=Path("srs/compute_weights"),
            log_file="srs/weighting_srs.log",
            shell=True,
        )

        run_script(
            scratch_dir=scratch_dir,
            script=f"{RSCRIPT_ENV} Rscript Add_on_Calibration_Variables_SRS.R",
            cwd=Path("srs/compute_weights"),
            log_file="srs/Add_on_Calibration_Variables_SRS.log",
            shell=True,
        )


@task
def srs_block_imputation(
    scratch_dir: Path,
    year: int,
    external_dir: Path,
    method30: bool = False,
) -> None:
    """Adds block imputation of SRS reporters."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)
    os.environ["DATA_YEAR"] = str(year)

    if method30:
        run_script(
            scratch_dir=scratch_dir,
            script="./block_imputation.sh",
            cwd=Path("srs/block_imputation_30yr"),
            log_file="srs/srs_block_imputation.log",
        )
    else:
        run_script(
            scratch_dir=scratch_dir,
            script="./block_imputation.sh",
            cwd=Path("srs/block_imputation"),
            log_file="srs/srs_block_imputation.log",
        )


@task
def srs_indicator_estimation_setup_weights(
    scratch_dir: Path,
    year: int,
    external_dir: Path,
    method30: bool = False,
) -> None:
    """Merges the output of the previous step and runs additional preprocessing for all Tables."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)
    os.environ["DATA_YEAR"] = str(year)

    if method30:
        file_path = "srs/generate_estimates_30yr/Setup/"
    else:
        file_path = "srs/generate_estimates/Setup/"

    run_script(
        scratch_dir=scratch_dir,
        script=f"{RSCRIPT_ENV} Rscript 100_Run_Process_Weights_and_Permutation.R",
        cwd=Path(file_path),
        log_file="srs/estimation_setup/Run_Process_Weights_and_Permutation.log",
        shell=True,
    )


@task
def srs_indicator_estimation_setup_clean_frame(
    scratch_dir: Path,
    year: int,
    external_dir: Path,
    method30: bool = False,
) -> None:
    """Merges the output of the previous step and runs additional preprocessing for all Tables."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)
    os.environ["DATA_YEAR"] = str(year)

    if method30:
        file_path = "srs/generate_estimates_30yr/Setup/"
    else:
        file_path = "srs/generate_estimates/Setup/"

    run_script(
        scratch_dir=scratch_dir,
        script=f"{RSCRIPT_ENV} Rscript 100_Create_Clean_SRS.R",
        cwd=Path(file_path),
        log_file="srs/estimation_setup/Create_Clean_SRS.log",
        shell=True,
    )


@task
def srs_indicator_estimation_setup_raw_frame(
    scratch_dir: Path,
    year: int,
    external_dir: Path,
    method30: bool = False,
) -> None:
    """Creates the raw SRS file for single estimation."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)
    os.environ["DATA_YEAR"] = str(year)

    if method30:
        file_path = "srs/generate_estimates_30yr/Setup/"
    else:
        file_path = "srs/generate_estimates/Setup/"

    run_script(
        scratch_dir=scratch_dir,
        script=f"{RSCRIPT_ENV} Rscript 100_Create_Raw_SRS.R",
        cwd=Path(file_path),
        log_file="srs/estimation_setup/Create_Raw_SRS.log",
        shell=True,
    )


@task(task_run_name=srs_indicators_estimated_tables_part1_preprocessing_tr_name)
def srs_indicator_estimation_tables_part1_preprocessing(
    scratch_dir: Path,
    year: int,
    external_dir: Path,
    table_name: str,
    method30: bool = False,
) -> None:
    """Runs the preprocessing script for the given table."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)
    os.environ["DATA_YEAR"] = str(year)

    if method30:
        file_path = f"srs/generate_estimates_30yr/Tables_Core/Table{table_name}"
    else:
        file_path = f"srs/generate_estimates/Tables_Core/Table{table_name}"

    run_script(
        scratch_dir=scratch_dir,
        script=f"{RSCRIPT_ENV} Rscript Part1_prepare_datasets.R",
        cwd=Path(file_path),
        log_file=f"srs/table_creation/indicator_estimation_part1_preprocessing/indicator_table_part1_{table_name}.log",
        shell=True,
    )


@task(task_run_name=srs_indicators_estimated_tables_part2_generate_est_tr_name)
def srs_indicator_estimation_tables_part2_generate_est(
    scratch_dir: Path,
    year: int,
    external_dir: Path,
    table_est_combo: tuple,
    method30: bool = False,
) -> None:
    """Runs the generate_est script for the given table."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)
    os.environ["DATA_YEAR"] = str(year)

    table_name, est_num = table_est_combo
    if method30:
        file_path = f"srs/generate_estimates_30yr/Tables_Core/Table{table_name}"
    else:
        file_path = f"srs/generate_estimates/Tables_Core/Table{table_name}"

    run_script(
        scratch_dir=scratch_dir,
        script=f"env LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libjemalloc.so.2 Rscript Part2_generate_est.R {est_num}",
        cwd=Path(file_path),
        log_file=f"srs/table_creation/indicator_estimation_part2_generate_est/indicator_table_gen_est_{table_name}_{est_num}.log",
        shell=True,
    )


@task(task_run_name=srs_indicators_estimated_tables_part3_finalize_tr_name)
def srs_indicator_estimation_tables_part3_finalize(
    scratch_dir: Path,
    year: int,
    external_dir: Path,
    table_name: str,
    method30: bool = False,
) -> None:
    """Runs the finalize script for the given table."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)
    os.environ["DATA_YEAR"] = str(year)

    if method30:
        file_path = f"srs/generate_estimates_30yr/Tables_Core/Table{table_name}"
    else:
        file_path = f"srs/generate_estimates/Tables_Core/Table{table_name}"

    run_script(
        scratch_dir=scratch_dir,
        script=f"{RSCRIPT_ENV} Rscript Part3_finalize.R",
        cwd=Path(file_path),
        log_file=f"srs/table_creation/indicator_estimation_part3_finalize/indicator_table_part3_{table_name}.log",
        shell=True,
    )


@task(task_run_name=srs_copula_imputation_step1_tr_name)
def srs_copula_imputation_step1(
    scratch_dir: Path,
    year: int,
    external_dir: Path,
    table: str,
    method30: bool = False,
) -> None:
    """Runs preprocessing step for copula imputation. Depends on tables estimation."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)
    os.environ["DATA_YEAR"] = str(year)
    os.environ["TABLE_NAME"] = str(table)

    if method30:
        run_script(
            scratch_dir=scratch_dir,
            script=f"{RSCRIPT_ENV} Rscript 100_run_copula_part1_prep_data_national.R",
            cwd=Path("srs/copula_imputation/part1_prep_data"),
            log_file=f"srs/copula/copula_imputation_part1/copula_imp_part1_prep_{table}.log",
            shell=True,
        )
    else:
        run_script(
            scratch_dir=scratch_dir,
            script=f"{RSCRIPT_ENV} Rscript 100_run_copula_part1_prep_data.R",
            cwd=Path("srs/copula_imputation/part1_prep_data"),
            log_file=f"srs/copula/copula_imputation_part1/copula_imp_part1_prep_{table}.log",
            shell=True,
        )


@task(task_run_name=srs_copula_imputation_step2_imp_tr_name)
def srs_copula_imputation_step2_imp(
    scratch_dir: Path,
    year: int,
    external_dir: Path,
    combo: list,
    method30: bool = False,
) -> None:
    """Generates copula imputation for a specific table, permutation, and sometimes column set."""
    table, strat = combo

    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)
    os.environ["DATA_YEAR"] = str(year)
    os.environ["TABLE_NAME"] = str(table)
    os.environ["STRAT_VAR"] = str(strat)

    if method30:
        run_script(
            scratch_dir=scratch_dir,
            script="./part2_impute_30yr.sh",
            cwd=Path("srs/copula_imputation/part2_impute"),
            log_file=f"srs/copula/copula_imputation_part2imp_{table}/copula_imp_part2_{table}_strat{strat}.log",
        )
    else:
        run_script(
            scratch_dir=scratch_dir,
            script="./part2_impute.sh",
            cwd=Path("srs/copula_imputation/part2_impute"),
            log_file=f"srs/copula/copula_imputation_part2imp_{table}/copula_imp_part2_{table}_strat{strat}.log",
        )


@task(task_run_name=srs_copula_imputation_step2_stack_tr_name)
def srs_copula_imputation_step2_stack(
    scratch_dir: Path,
    year: int,
    external_dir: Path,
    table: str,
    method30: bool = False,
) -> None:
    """Merges the output from the copula imputation step."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)
    os.environ["DATA_YEAR"] = str(year)
    os.environ["TABLE_NAME"] = str(table)

    if method30:
        run_script(
            scratch_dir=scratch_dir,
            script=f"timeout --verbose 30m {RSCRIPT_ENV} Rscript 100_Run_Copula_Stack_National.R",
            cwd=Path("srs/copula_imputation/part2_impute"),
            log_file=f"srs/copula/copula_imputation_part2stack_{table}/copula_imp_part2_stack_{table}.log",
            shell=True,
        )
    else:
        run_script(
            scratch_dir=scratch_dir,
            script=f"timeout --verbose 30m {RSCRIPT_ENV} Rscript 100_Run_Copula_Stack.R",
            cwd=Path("srs/copula_imputation/part2_impute"),
            log_file=f"srs/copula/copula_imputation_part2stack_{table}/copula_imp_part2_stack_{table}.log",
            shell=True,
        )


@task
def srs_copula_imputation_step3_01_template(
    scratch_dir: Path,
    year: int,
    external_dir: Path,
    method30: bool = False,
) -> None:
    """Fills in the table shell from the copula outputs. Depends on part 2."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)
    os.environ["DATA_YEAR"] = str(year)

    if method30:
        file_path = "srs/copula_imputation/part3_generate_prb_30yr"
    else:
        file_path = "srs/copula_imputation/part3_generate_prb"

    run_script(
        scratch_dir=scratch_dir,
        script=f"{RSCRIPT_ENV} Rscript 01_Create_Template_Indicator_Tabel_Rel_Bias.R",
        cwd=Path(file_path),
        log_file="srs/copula/copula_imp_part3_01_create_template.log",
        shell=True,
    )


@task
def srs_copula_imputation_step3_02_variance(
    scratch_dir: Path,
    year: int,
    external_dir: Path,
    combo: list,
    method30: bool = False,
) -> None:
    """Processes the copula output for each permutation."""
    table, permutation = combo

    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)
    os.environ["DATA_YEAR"] = str(year)
    os.environ["TABLE_NAME"] = str(table)
    os.environ["DER_CURRENT_PERMUTATION_NUM"] = str(permutation)

    if method30:
        prb_path = "srs/copula_imputation/part3_generate_prb_30yr"
        variance_path = "srs/generate_estimates_30yr/Variance"
    else:
        prb_path = "srs/copula_imputation/part3_generate_prb"
        variance_path = "srs/generate_estimates/Variance"

    if table == "SRS1araw":
        # skip copula for the raw table
        pass
    else:
        run_script(
            scratch_dir=scratch_dir,
            script="./generate_prb.sh",
            cwd=Path(prb_path),
            log_file=f"srs/copula/copula_imputation_part3_{table}/copula_imp_part3_02_{table}_perm_{permutation}.log",
            shell=True,
        )

    run_script(
        scratch_dir=scratch_dir,
        script=f"{RSCRIPT_ENV} Rscript 100_Run_Table_Programs.R",
        cwd=Path(variance_path),
        log_file=f"srs/variance/indicator_estimation_variance/variance_table_{table}_perm_{permutation}.log",
        shell=True,
    )


@task
def srs_final_estimates(
    scratch_dir: Path,
    year: int,
    external_dir: Path,
    permutation_name: str,
) -> None:
    """Generates final estimates. It depends on the permutation step."""
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["DATA_YEAR"] = str(year)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)
    os.environ["PERMUTATION_NAME"] = str(permutation_name)

    run_script(
        scratch_dir=scratch_dir,
        script='env LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libjemalloc.so.2 Rscript "10000 - Make Final Database.R"',
        cwd=Path("srs/make_final_dataset"),
        log_file=f"srs/final_estimates/final_estimates_{permutation_name}.log",
        shell=True,
    )


@task
def srs_final_estimates_merged(
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
        cwd=Path("srs/make_final_dataset"),
        log_file="srs/final_estimates/final_estimates_merged.log",
        shell=True,
    )


@task(task_run_name=srs_qc_conversion_reports_tr_name)
def srs_qc_conversion_reports(
    scratch_dir: Path,
    year: int,
    external_dir: Path,
    state_abbr: str | None = None,
    INPUT_STATE: str | None = None,
) -> None:
    """Generates state-level comparison with DB for conversion."""
    state = state_abbr or INPUT_STATE
    if not state:
        raise ValueError("srs_qc_conversion_reports requires a state abbreviation")
    os.environ["INPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["OUTPUT_PIPELINE_DIR"] = str(scratch_dir)
    os.environ["DATA_YEAR"] = str(year)
    os.environ["INPUT_STATE"] = str(state)
    os.environ["EXTERNAL_FILE_PATH"] = str(external_dir)

    run_script(
        scratch_dir=scratch_dir,
        script="./generate_report.sh",
        cwd=Path("srs/qc_reports"),
        log_file=f"srs/validation/qc_conversion_reports_{state}.log",
    )
