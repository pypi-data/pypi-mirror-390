import json
from pathlib import Path

from prefect import allow_failure, flow  # noqa: F401
from prefect_util import map_wrapper

from srs.all import (  # noqa: F401
    srs_copula_imputation_step3_02_variance,
    srs_get_variance_table_list,
)
from tasks.all import copula_imputation_step1  # noqa: F401
from tasks.all import copula_imputation_step2_imp  # noqa: F401
from tasks.all import copula_imputation_step2_stack  # noqa: F401
from tasks.all import final_estimates_suppression  # noqa: F401
from tasks.all import validation_copula_imputation_step2  # noqa: F401
from tasks.all import (  # noqa: F401
    copula_part_3_2_and_indicator_estimation_variance,
    create_general_groups,
    get_specific_group,
    get_variance_table_list,
    indicator_estimation_tables_part2_create_additional_columns,
    verify_variance_runs,
)
from tasks.settings import load_custom_flow_params

custom_flow_params = load_custom_flow_params()


@flow(
    name="Copula Part 3 and Variance",
    description="Sub-flow to run copula part 3 and variance steps, split out into smaller parts for run-ability.",
    **custom_flow_params,
)
def flow_variance(
    scratch_dir: Path,
    external_mirror: Path,
    external_config: Path,
    year: int,
    first_group: int = 1,
):
    all_groups = get_variance_table_list.submit(
        scratch_dir=scratch_dir,
        external_config=external_config,
        external_dir=external_mirror,
        year=year,
        wait_for=[external_mirror],
    ).result()

    grp_1 = get_specific_group.submit(  # noqa: F841
        scratch_dir=scratch_dir,
        groups=all_groups,
        group_num=first_group,
        task_list_name="variance_table_list",
        wait_for=[all_groups],
    )

    variance_group_1 = map_wrapper.submit(
        copula_part_3_2_and_indicator_estimation_variance,
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        permutation_tables=grp_1,
        group_num=first_group,
        wait_for=[grp_1],
    )
    variance_group_1.wait()

    for i in range(first_group + 1, len(all_groups) + 1):
        grp_i = get_specific_group(
            scratch_dir=scratch_dir,
            groups=all_groups,
            group_num=i,
            task_list_name="variance_table_list",
        )
        variance_group_i = map_wrapper.submit(
            copula_part_3_2_and_indicator_estimation_variance,
            scratch_dir=scratch_dir,
            year=year,
            external_dir=external_mirror,
            permutation_tables=grp_i,
            group_num=i,
            wait_for=[grp_i],
        )
        variance_group_i.wait()

    remaining_variance_groups = verify_variance_runs.submit(
        scratch_dir=scratch_dir,
        all_perm_groups=all_groups,
    ).result()

    first_remaining_group = get_specific_group.submit(
        scratch_dir=scratch_dir,
        groups=remaining_variance_groups,
        group_num=1,
        wait_for=[remaining_variance_groups],
        task_list_name="remaining_variance_table_list",
    )

    variance_group_1 = map_wrapper.submit(
        copula_part_3_2_and_indicator_estimation_variance,
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        permutation_tables=first_remaining_group,
        group_num=1,
        wait_for=[first_remaining_group],
    )
    variance_group_1.wait()

    for i in range(2, len(remaining_variance_groups) + 1):
        remaining_group = get_specific_group.submit(
            scratch_dir=scratch_dir,
            groups=remaining_variance_groups,
            group_num=i,
            task_list_name="remaining_variance_table_list",
        )
        variance_group = map_wrapper.submit(
            copula_part_3_2_and_indicator_estimation_variance,
            scratch_dir=scratch_dir,
            year=year,
            external_dir=external_mirror,
            permutation_tables=remaining_group,
            group_num=i,
            wait_for=[remaining_group],
        )
        variance_group.wait()

    return


@flow(
    name="SRS Copula Part 3 and Variance",
    description="Sub-flow to run copula part 3 and variance steps for srs, split out into smaller parts for run-ability.",
    **custom_flow_params,
)
def flow_variance_srs(
    scratch_dir: Path,
    external_mirror: Path,
    external_config: Path,
    year: int,
    method30: bool = False,
    first_group: int = 1,
):
    srs_variance_table_list = srs_get_variance_table_list.submit(
        scratch_dir=scratch_dir,
        external_config=external_config,
        external_dir=external_mirror,
        year=year,
        method30=method30,
        wait_for=[external_mirror],
    )

    all_groups = create_general_groups.submit(
        scratch_dir=scratch_dir,
        perm_list=srs_variance_table_list,
        group_name="srs_variance",
        wait_for=[srs_variance_table_list],
    ).result()

    grp_1 = get_specific_group.submit(  # noqa: F841
        scratch_dir=scratch_dir,
        groups=all_groups,
        group_num=first_group,
        task_list_name="srs_variance_list",
        wait_for=[all_groups],
    )

    future = map_wrapper.submit(
        srs_copula_imputation_step3_02_variance,
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        combo=grp_1,
        group_num=first_group,
        wait_for=[
            grp_1,
        ],
    )
    future.wait()

    for i in range(first_group + 1, len(all_groups) + 1):
        grp_i = get_specific_group(
            scratch_dir=scratch_dir,
            groups=all_groups,
            group_num=i,
            task_list_name="srs_variance_list",
        )
        future = map_wrapper.submit(
            srs_copula_imputation_step3_02_variance,
            scratch_dir=scratch_dir,
            year=year,
            external_dir=external_mirror,
            combo=grp_i,
            group_num=i,
            wait_for=[grp_i],
        )
        future.wait()

    return


@flow(
    description="Sub-flow to run a list of groups.",
    **custom_flow_params,
)
def flow_run_all_groups(
    scratch_dir: Path,
    external_mirror: Path,
    year: int,
    task_function: callable,
    combo_arg_name: str,
    all_groups_file: Path,
    first_group: int = 1,
):
    with open(scratch_dir / "mapped_tasks" / all_groups_file, "r") as group_file:
        all_groups = json.load(group_file)

    grp_1 = get_specific_group.submit(  # noqa: F841
        scratch_dir=scratch_dir,
        groups=all_groups,
        group_num=first_group,
        task_list_name=task_function,
        wait_for=[all_groups],
    )

    kwargs = {combo_arg_name: grp_1}
    future = map_wrapper.submit(
        task_function,
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        wait_for=[grp_1],
        group_num=first_group,
        **kwargs,
    )
    future.wait()

    for i in range(first_group + 1, len(all_groups) + 1):
        grp_i = get_specific_group(
            scratch_dir=scratch_dir,
            groups=all_groups,
            group_num=i,
            task_list_name=task_function,
        )
        kwargs = {combo_arg_name: grp_i}
        future = map_wrapper.submit(
            task_function,
            scratch_dir=scratch_dir,
            year=year,
            external_dir=external_mirror,
            wait_for=[grp_i],
            group_num=i,
            **kwargs,
        )
        future.wait()

    return
