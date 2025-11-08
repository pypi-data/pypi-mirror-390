import argparse
import asyncio
import os

from prefect import allow_failure, flow, task  # noqa: F401
from prefect.context import get_run_context
from prefect.futures import PrefectFuture, wait
from prefect_dask import DaskTaskRunner
from prefect_util import map_wrapper

from srs.all import (
    srs_block_imputation,
    srs_conversion,
    srs_conversion_bystate,
    srs_copula_imputation_step1,
    srs_copula_imputation_step2_imp,
    srs_copula_imputation_step2_stack,
    srs_copula_imputation_step3_01_template,
    srs_copula_imputation_step3_02_variance,
    srs_final_estimates,
    srs_final_estimates_merged,
    srs_get_copula_part2_combos,
    srs_get_final_estimation_permutation_list,
    srs_indicator_estimation_get_table_combinations,
    srs_indicator_estimation_setup_clean_frame,
    srs_indicator_estimation_setup_raw_frame,
    srs_indicator_estimation_setup_weights,
    srs_indicator_estimation_tables_part1_preprocessing,
    srs_indicator_estimation_tables_part2_generate_est,
    srs_indicator_estimation_tables_part3_finalize,
    srs_qc_conversion_reports,
    srs_weighting,
)
from subflows import flow_run_all_groups, flow_variance, flow_variance_srs
from tasks.all import (
    block_imputation,
    block_imputation_group_b,
    collect_task_metrics,
    combine_logs,
    copula_imputation_step1,
    copula_imputation_step2_imp,
    copula_imputation_step2_stack,
    copula_imputation_step2_summary,
    copula_imputation_step3_01_template,
    copy_external_file_json,
    create_copula_groups,
    create_estimates_database,
    create_estimates_index,
    create_general_groups,
    create_initial_estimate_lookup_files,
    create_msa_provider,
    create_run_metadata,
    create_scratch_dir,
    define_db_task_tag,
    fetch_external_files,
    fill_variance_skipped_demos,
    final_estimates_merged,
    final_estimates_momentum,
    final_estimates_suppression,
    get_copula_combinations,
    get_demo_perm_fill_list,
    get_final_estimation_permutation_list,
    get_specific_group,
    get_state_dependency_list,
    get_states_in_database,
    get_ten_years_in_database,
    get_vic_off_rel_state_dependency_split,
    get_years_in_database,
    impute_officers,
    indicator_estimation_demo_skips,
    indicator_estimation_get_table_combinations,
    indicator_estimation_part4_gv_combine_tables,
    indicator_estimation_setup,
    indicator_estimation_setup_gv_dataset,
    indicator_estimation_setup_part2_00a,
    indicator_estimation_setup_part2_00b,
    indicator_estimation_setup_part2_00b_weights,
    indicator_estimation_setup_part2_00c_clean_main,
    indicator_estimation_setup_part2_00d_agency_ori,
    indicator_estimation_tables_part1_preprocessing,
    indicator_estimation_tables_part2_create_additional_columns,
    indicator_estimation_tables_part2_generate_est,
    indicator_estimation_tables_part3_finalize,
    indicator_estimation_tables_part4_select_tables,
    indicator_estimation_tables_part5_select_tables,
    item_imputation_part1,
    item_imputation_part2_nonperson,
    item_imputation_part2_person,
    item_imputation_part3_5_ethnicity,
    item_imputation_part3_5_ethnicity_combine,
    item_imputation_part3_finalize,
    item_imputation_part4_victim_offender_relationship,
    item_imputation_part4_vor_property,
    item_imputation_part5_groupb_arrestee,
    item_imputation_part5_groupb_arrestee_combine,
    missing_months,
    nibrs_extract_one_state,
    optional_final_estimates_blank_momentum,
    outlier_detection,
    partial_reporters,
    qc_for_input_data,
    qc_for_input_data_missingness,
    qc_for_input_data_missingness_bystate,
    qc_for_input_data_missingness_bystate_merge,
    qc_for_input_data_partial_reporters,
    queries_by_data_year,
    queries_by_state,
    queries_by_state_qc,
    run_smoketest_part1a,
    run_smoketest_part1b,
    run_smoketest_part2,
    srs_retamm_file,
    universe_file,
    update_pop_totals,
    update_universe,
    validation_block_imputation,
    validation_copula_imputation_aggregate,
    validation_copula_imputation_step2,
    validation_data_quality,
    validation_extract_bystate,
    validation_extract_merge,
    validation_item_imputation,
    validation_population,
    weighting,
)
from tasks.settings import load_custom_flow_params, ESTIMATES_DB_NAME
from tasks.store import FileStore
from tasks_grant.all import (
    bjs_grant_combine,
    bjs_grant_conversion,
    bjs_grant_conversion_bystate,
    bjs_grant_conversion_bystate_combinations,
)

store = FileStore(
    external_location=os.environ["EXTERNAL_STORE"],
    artifact_location=os.environ["ARTIFACT_STORE"],
)
custom_flow_params = load_custom_flow_params()


@flow(
    name="Smoketest",
    description="Simple flow to test infrastructure",
    **custom_flow_params,
)
def flow_smoketest(run_id: str):
    flow_name = "smoketest"
    year = 2021
    
    scratch_dir = create_scratch_dir.submit(run_id=run_id, flow_name=flow_name)

    tag_definition = define_db_task_tag()
    asyncio.run(tag_definition)

    create_run_metadata.submit(
        scratch_dir=scratch_dir,
        run_id=run_id,
        flow_name=flow_name,
        wait_for=[scratch_dir],
    )

    external_config = copy_external_file_json.submit(
        scratch_dir, wait_for=[scratch_dir]
    )
    external_mirror = fetch_external_files.submit(
        store=store,
        external_config=external_config,
        scratch_dir=scratch_dir,
        wait_for=[scratch_dir, external_config],
    )

    part1a = run_smoketest_part1a.submit(
        scratch_dir=scratch_dir,
        year=year,
        wait_for=[scratch_dir, external_config, external_mirror],
    )

    year_list = get_years_in_database.submit(year)

    universe_created = map_wrapper.submit(
        universe_file,
        scratch_dir=scratch_dir,
        year=year_list,
        external_dir=external_mirror,
        wait_for=[external_mirror, year_list],
    )

    part1b = run_smoketest_part1b.submit(
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        wait_for=[scratch_dir, external_config, external_mirror, universe_created],
    )
    part2 = run_smoketest_part2.submit(
        scratch_dir=scratch_dir,
        year=year,
        wait_for=[part1a, part1b],
    )

    logs_combined = combine_logs.submit(
        scratch_dir=scratch_dir,
        wait_for=[allow_failure(part2), allow_failure(universe_created)],
    )
    for maybe_future in locals().values():
        if isinstance(maybe_future, PrefectFuture):
            maybe_future.wait()
        elif isinstance(maybe_future, list) and all(
            isinstance(f, PrefectFuture) for f in maybe_future
        ):
            wait(maybe_future)

    return logs_combined


@flow(
    name="Run All Flow", description="Flow to run entire pipeline", **custom_flow_params
)
def flow_all(run_id: str):
    # PIPELINE SETUP
    year = 2021
    flow_name = "runall"

    if os.getenv("IS_PROD", False):
        # For the child flows, we need to re-use the current task runner created
        # for the parent flow. Otherwise Prefect tries to create a new task
        # runner for each child flow and throws an error saying a task runner has
        # already been started.
        child_task_runner = DaskTaskRunner(
            address=get_run_context().task_runner._client.scheduler_info()["address"]
        )
        options = {
            "task_runner": child_task_runner,
        }
    else:
        options = {}

    subflow_options = {**options}

    scratch_dir = create_scratch_dir.submit(run_id=run_id, flow_name=flow_name)

    tag_definition = define_db_task_tag()
    asyncio.run(tag_definition)

    run_metadata = create_run_metadata.submit(
        scratch_dir=scratch_dir,
        run_id=run_id,
        flow_name=flow_name,
    )

    external_config = copy_external_file_json.submit(scratch_dir)

    external_mirror = fetch_external_files.submit(
        store=store, external_config=external_config, scratch_dir=scratch_dir
    )

    year_list = get_years_in_database.submit(year)

    estimates_db = create_estimates_database.submit(
        wait_for=[scratch_dir]
    )

    # INITIAL TASKS
    # tasks related to generating previously external files
    # required for both SRS and NIBRS
    universe_created = map_wrapper.submit(
        universe_file,
        scratch_dir=scratch_dir,
        year=year_list,
        external_dir=external_mirror,
        wait_for=[external_mirror],
    )

    msa_provider = create_msa_provider.submit(
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        wait_for=[external_mirror],
    )

    srs_retamm_created = map_wrapper.submit(
        srs_retamm_file,
        scratch_dir=scratch_dir,
        year=list(range(2022, year + 1)),
        external_dir=external_mirror,
        wait_for=[external_mirror, universe_created],
    )

    officers_imputed = impute_officers.submit(
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        wait_for=[srs_retamm_created],
    )

    universe_updated = update_universe.submit(
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        wait_for=[officers_imputed],
    )

    pop_totals_updated = update_pop_totals.submit(
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        pipeline="NIBRS",
        wait_for=[universe_updated],
    )

    year_queried = queries_by_data_year.submit(
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        wait_for=[external_mirror],
    )

    states_in_database = get_states_in_database.submit(
        scratch_dir=scratch_dir,
        year=year,
    )

    states_queried = map_wrapper.submit(
        queries_by_state,
        scratch_dir=scratch_dir,
        year=year,
        state_abbr=states_in_database,
        external_dir=external_mirror,
        wait_for=[external_mirror, states_in_database],
    )

    states_queried_qc = map_wrapper.submit(
        queries_by_state_qc,
        scratch_dir=scratch_dir,
        year=year,
        state_abbr=states_in_database,
        external_dir=external_mirror,
        wait_for=[external_mirror, states_in_database],
    )

    missed_months = map_wrapper.submit(
        missing_months,
        scratch_dir=scratch_dir,
        year=year_list,
        external_dir=external_mirror,
        wait_for=[external_mirror, year_list, universe_updated, year_queried],
    )

    # PIPELINE TASKS
    # tasks to generate shared data files for downstream tasks
    partial_reporters_calculated = partial_reporters.submit(
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        wait_for=[missed_months, year_queried],
    )

    nibrs_extract_one_state_created = map_wrapper.submit(
        nibrs_extract_one_state,
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        state_abbr=states_in_database,
        wait_for=[states_in_database, states_queried],
    )

    # tasks to generate block imputation results
    outliers_detected = outlier_detection.submit(
        scratch_dir=scratch_dir,
        year=year,
        wait_for=[partial_reporters_calculated],
    )

    blocks_imputed = block_imputation.submit(
        scratch_dir=scratch_dir,
        year=year,
        wait_for=[outliers_detected, year_queried],
    )

    blocks_imputed_group_b = block_imputation_group_b.submit(
        scratch_dir=scratch_dir,
        year=year,
        wait_for=[states_queried, blocks_imputed],
    )

    # tasks to generate item imputation results
    items_imputed_part1 = map_wrapper.submit(
        item_imputation_part1,
        scratch_dir=scratch_dir,
        year=year,
        state_abbr=states_in_database,
        wait_for=[
            states_in_database,
            states_queried,
            year_queried,
            nibrs_extract_one_state_created,
        ],
    )

    items_imputed_part2_nonperson = map_wrapper.submit(
        item_imputation_part2_nonperson,
        scratch_dir=scratch_dir,
        year=year,
        state_abbr=states_in_database,
        wait_for=[states_in_database, items_imputed_part1],
    )

    items_imputed_part2_person = map_wrapper.submit(
        item_imputation_part2_person,
        scratch_dir=scratch_dir,
        year=year,
        state_abbr=states_in_database,
        wait_for=[states_in_database, items_imputed_part1],
    )

    items_imputed_part3 = map_wrapper.submit(
        item_imputation_part3_finalize,
        scratch_dir=scratch_dir,
        year=year,
        state_abbr=states_in_database,
        wait_for=[
            states_in_database,
            items_imputed_part2_nonperson,
            items_imputed_part2_person,
        ],
    )

    items_imputed_part3_5_ethnicity = map_wrapper.submit(
        item_imputation_part3_5_ethnicity,
        scratch_dir=scratch_dir,
        year=year,
        ethnicity_num=list(range(1, 4)),
        wait_for=[
            items_imputed_part2_nonperson,
            items_imputed_part2_person,
            items_imputed_part3,
        ],
    )

    items_imputed_part3_5_ethnicity_combined = (
        map_wrapper.submit(
            item_imputation_part3_5_ethnicity_combine,
            scratch_dir=scratch_dir,
            year=year,
            state_abbr=states_in_database,
            wait_for=[
                states_in_database,
                items_imputed_part3_5_ethnicity,
            ],
        )
    )

    possible_dependent_states = get_state_dependency_list.submit(year=year)
    (
        independent_states,
        dependent_states,
    ) = get_vic_off_rel_state_dependency_split.submit(
        scratch_dir,
        states_in_database,
        possible_dependent_states,
        wait_for=[possible_dependent_states, possible_dependent_states],
    ).result()

    items_imputed_part4 = map_wrapper.submit(
        item_imputation_part4_victim_offender_relationship,
        scratch_dir=scratch_dir,
        year=year,
        state_abbr=independent_states,
        wait_for=[items_imputed_part3_5_ethnicity_combined, independent_states],
    )

    items_imputed_part4_dep = map_wrapper.submit(
        item_imputation_part4_victim_offender_relationship,
        scratch_dir=scratch_dir,
        year=year,
        state_abbr=dependent_states,
        wait_for=[items_imputed_part4, dependent_states],
    )

    items_imputed_part4_vor = map_wrapper.submit(
        item_imputation_part4_vor_property,
        scratch_dir=scratch_dir,
        year=year,
        vor_num=list(range(1, 13)),
        wait_for=[states_queried, items_imputed_part4_dep],
    )

    items_imputed_part5 = map_wrapper.submit(
        item_imputation_part5_groupb_arrestee,
        scratch_dir=scratch_dir,
        external_dir=external_mirror,
        year=year,
        state_abbr=states_in_database,
        wait_for=[states_queried, universe_updated],
    )

    items_imputed_part5_combined = item_imputation_part5_groupb_arrestee_combine.submit(
        scratch_dir=scratch_dir,
        external_dir=external_mirror,
        year=year,
        wait_for=[items_imputed_part5, states_queried, universe_updated], 
    )

    # tasks to generate weighting results
    weights_computed = weighting.submit(
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        wait_for=[
            outliers_detected,
            srs_retamm_created,
            pop_totals_updated,
            year_queried,
        ],
    )

    indicators_estimated_setup = map_wrapper.submit(
        indicator_estimation_setup,
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        state_abbr=states_in_database,
        wait_for=[states_in_database, states_queried, nibrs_extract_one_state_created],
    )

    indicators_estimated_setup_part2_00a = indicator_estimation_setup_part2_00a.submit(
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        wait_for=[states_queried, indicators_estimated_setup],
    )

    indicators_estimated_setup_part2_00b = map_wrapper.submit(
        indicator_estimation_setup_part2_00b,
        scratch_dir=scratch_dir,
        year=year,
        dataset=["VICTIM", "OFFENDER", "ARRESTEE", "OFFENDERYOUTHTABLE", "GROUPBARRESTEE"],
        external_dir=external_mirror,
        wait_for=[
            indicators_estimated_setup_part2_00a,
            items_imputed_part4_vor,
            items_imputed_part5_combined,
            weights_computed,
            blocks_imputed,
            blocks_imputed_group_b,
        ],
    )

    indicator_estimated_setup_part2_weights = (
        indicator_estimation_setup_part2_00b_weights.submit(
            scratch_dir=scratch_dir,
            year=year,
            external_dir=external_mirror,
            wait_for=[
                indicators_estimated_setup_part2_00a,
                weights_computed,
                year_queried,
            ],
        )
    )

    indicator_estimated_setup_part2_00c_clean_main = (
        map_wrapper.submit(
            indicator_estimation_setup_part2_00c_clean_main,
            scratch_dir=scratch_dir,
            year=year,
            main_to_run=["incident", "offenses", "arrestee", "LEOKA", "arrest_code", "group_b_arrestee"],
            external_dir=external_mirror,
            wait_for=[
                indicator_estimated_setup_part2_weights,
                indicators_estimated_setup_part2_00b,
            ],
        )
    )

    indicator_estimated_setup_part2_00d_agency_ori = (
        indicator_estimation_setup_part2_00d_agency_ori.submit(
            scratch_dir=scratch_dir,
            year=year,
            external_dir=external_mirror,
            wait_for=[
                indicator_estimated_setup_part2_00c_clean_main,
                msa_provider,
                year_queried,
            ],
        )
    )

    indicator_estimated_setup_part2_00c_gv_main = (
        indicator_estimation_setup_gv_dataset.submit(
            scratch_dir=scratch_dir,
            year=year,
            external_dir=external_mirror,
            wait_for=[indicator_estimated_setup_part2_00c_clean_main],
        )
    )

    (
        tables,
        estimate_combos,
        add_col_combos,
    ) = indicator_estimation_get_table_combinations.submit(
        scratch_dir,
    ).result()

    # tasks to create final estimates
    indicators_estimated_tables_part1_preprocessing = (
        map_wrapper.submit(
            indicator_estimation_tables_part1_preprocessing,
            scratch_dir=scratch_dir,
            year=year,
            external_dir=external_mirror,
            table_name=tables,
            wait_for=[
                tables,
                indicator_estimated_setup_part2_00d_agency_ori,
                indicator_estimated_setup_part2_00c_gv_main,
            ],
        )
    )

    indicators_estimated_tables_part2_generate_est = (
        map_wrapper.submit(
            indicator_estimation_tables_part2_generate_est,
            scratch_dir=scratch_dir,
            year=year,
            external_dir=external_mirror,
            table_est_combo=estimate_combos,
            wait_for=[estimate_combos, indicators_estimated_tables_part1_preprocessing],
        )
    )

    add_cols_grps = create_general_groups.submit(
        scratch_dir=scratch_dir,
        perm_list=add_col_combos,
        group_name="indicator_est_add",
        wait_for=[add_col_combos],
    )

    subflow_options["flow_run_name"] = (
        indicator_estimation_tables_part2_create_additional_columns.__name__
    )
    created_additional_columns_flow = flow_run_all_groups.with_options(
        **subflow_options
    )(
        scratch_dir=scratch_dir,
        external_mirror=external_mirror,
        year=year,
        task_function=indicator_estimation_tables_part2_create_additional_columns,
        combo_arg_name="add_col_combo",
        all_groups_file=add_cols_grps,
        wait_for=[add_cols_grps, indicators_estimated_tables_part2_generate_est],
    )

    # tasks to create final estimates
    indicators_estimated_tables_part3_finalize = (
        map_wrapper.submit(
            indicator_estimation_tables_part3_finalize,
            scratch_dir=scratch_dir,
            year=year,
            external_dir=external_mirror,
            table_name=tables,
            wait_for=[
                tables,
                indicators_estimated_tables_part2_generate_est,
                created_additional_columns_flow,
            ],
        )
    )

    # Two tables have additional steps
    indicators_estimated_tables_part4_finalize = (
        map_wrapper.submit(
            indicator_estimation_tables_part4_select_tables,
            scratch_dir=scratch_dir,
            year=year,
            external_dir=external_mirror,
            table_name=[
                "2a",
                "2b",
                "GV1a",
            ],
            wait_for=[indicators_estimated_tables_part3_finalize],
        )
    )

    indicators_estimated_tables_part5_finalize = (
        map_wrapper.submit(
            indicator_estimation_tables_part5_select_tables,
            scratch_dir=scratch_dir,
            year=year,
            external_dir=external_mirror,
            table_name=[
                "2a",
                "GV1a",
            ],
            wait_for=[indicators_estimated_tables_part4_finalize],
        )
    )

    indicators_estimated_tables_part4_gv_combo = (
        indicator_estimation_part4_gv_combine_tables.submit(
            scratch_dir=scratch_dir,
            year=year,
            external_dir=external_mirror,
            wait_for=[indicators_estimated_tables_part3_finalize],
        )
    )

    est_db_lookups_created = create_initial_estimate_lookup_files.submit(
            scratch_dir=scratch_dir,
            year=year,
            external_dir=external_mirror,
            wait_for=[indicators_estimated_tables_part4_gv_combo, estimates_db],
    )

    demo_skips_collected = indicator_estimation_demo_skips.submit(
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        wait_for=[
            indicators_estimated_tables_part5_finalize,
            indicators_estimated_tables_part4_gv_combo,
        ],
    )

    (copula_combo_list, copula_stack_list) = get_copula_combinations.submit(
        scratch_dir=scratch_dir,
        external_config=external_config,
        external_dir=external_mirror,
        year=year,
        wait_for=[external_mirror, created_additional_columns_flow],
    ).result()

    cop_stacked_grps_file = create_general_groups.submit(
        scratch_dir=scratch_dir,
        perm_list=copula_stack_list,
        group_name="copula_pt1_stack",
        wait_for=[copula_stack_list, demo_skips_collected],
    ).result()

    subflow_options["flow_run_name"] = copula_imputation_step1.__name__
    copula_part_1_flow = flow_run_all_groups.with_options(**subflow_options)(
        scratch_dir=scratch_dir,
        external_mirror=external_mirror,
        year=year,
        task_function=copula_imputation_step1,
        combo_arg_name="permutation_table",
        all_groups_file=cop_stacked_grps_file,
        wait_for=[cop_stacked_grps_file, demo_skips_collected],
    )

    cop_part2_grps_file = create_copula_groups.submit(
        scratch_dir=scratch_dir,
        full_copula_combo_list=copula_combo_list,
        wait_for=[
            copula_combo_list,
            copula_part_1_flow,
        ],
    ).result()

    subflow_options["flow_run_name"] = copula_imputation_step2_imp.__name__
    copula_part_2_flow = flow_run_all_groups.with_options(**subflow_options)(
        scratch_dir=scratch_dir,
        external_mirror=external_mirror,
        year=year,
        task_function=copula_imputation_step2_imp,
        combo_arg_name="combo",
        all_groups_file=cop_part2_grps_file,
        wait_for=[cop_part2_grps_file, copula_part_1_flow],
    )

    subflow_options["flow_run_name"] = validation_copula_imputation_step2.__name__
    copula_part_2_validated_flow = flow_run_all_groups.with_options(**subflow_options)(
        scratch_dir=scratch_dir,
        external_mirror=external_mirror,
        year=year,
        task_function=validation_copula_imputation_step2,
        combo_arg_name="permutation_table",
        all_groups_file=cop_stacked_grps_file,
        wait_for=[cop_part2_grps_file, copula_part_2_flow],
    )

    subflow_options["flow_run_name"] = copula_imputation_step2_stack.__name__
    copula_stacked_flow = flow_run_all_groups.with_options(**subflow_options)(
        scratch_dir=scratch_dir,
        external_mirror=external_mirror,
        year=year,
        task_function=copula_imputation_step2_stack,
        combo_arg_name="permutation_table",
        all_groups_file=cop_stacked_grps_file,
        wait_for=[cop_part2_grps_file, copula_part_2_flow],
    )

    copula_imputed_summary = map_wrapper.submit(
        copula_imputation_step2_summary,
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        table=tables,
        wait_for=[copula_stacked_flow, tables],
    )

    copula_imputed_step3_01 = copula_imputation_step3_01_template.submit(
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        wait_for=[copula_stacked_flow],
    )

    variance_flow = flow_variance.with_options(**options)(
        scratch_dir=scratch_dir,
        external_mirror=external_mirror,
        external_config=external_config,
        year=year,
        wait_for=[copula_imputed_step3_01],
    )

    skipped_demo_list = get_demo_perm_fill_list.submit(
        scratch_dir=scratch_dir,
        year=year,
        wait_for=[variance_flow],
    )

    variance_filled = map_wrapper.submit(
        fill_variance_skipped_demos,
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        combo=skipped_demo_list,
        wait_for=[skipped_demo_list],
    )

    (
        final_perm_momentum_list,
        final_perm_suppression_groups_file,
    ) = get_final_estimation_permutation_list.submit(
        scratch_dir=scratch_dir,
        external_dir=external_mirror,
        external_config=external_config,
        year=year,
        wait_for=[variance_filled],
    ).result()

    final_estimates_momentum_calculated = map_wrapper.submit(
        final_estimates_momentum,
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        combo=final_perm_momentum_list,
        wait_for=[
            final_perm_momentum_list,
        ],
    )

    """optional_final_estimates_momentum_blanked = optional_final_estimates_blank_momentum.submit(
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        wait_for=[final_estimates_momentum_calculated], 
    )"""

    subflow_options["flow_run_name"] = final_estimates_suppression.__name__
    final_estimates_suppression_flow = flow_run_all_groups.with_options(
        **subflow_options
    )(
        scratch_dir=scratch_dir,
        external_mirror=external_mirror,
        year=year,
        task_function=final_estimates_suppression,
        combo_arg_name="combo",
        all_groups_file=final_perm_suppression_groups_file,
        wait_for=[
            final_perm_suppression_groups_file,
            final_estimates_momentum_calculated,
            est_db_lookups_created,
            estimates_db,
            #optional_final_estimates_momentum_blanked
        ],
    )

    final_estimated_merged = final_estimates_merged.submit(
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        wait_for=[final_estimates_suppression_flow],
    )

    estimates_index_created = create_estimates_index.submit(
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        wait_for=[final_estimates_suppression_flow],
    )

    # PIPELINE VALIDATION
    # tasks to run QC on the input files
    input_data_qcd = qc_for_input_data.submit(
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        wait_for=[missed_months],
    )

    partial_reporters_qcd = qc_for_input_data_partial_reporters.submit(
        scratch_dir=scratch_dir,
        year=year,
        wait_for=partial_reporters_calculated,
    )

    qc_missingness = qc_for_input_data_missingness.submit(
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        wait_for=[indicators_estimated_setup, states_queried_qc],
    )

    qc_missingness_bystate = map_wrapper.submit(
        qc_for_input_data_missingness_bystate,
        scratch_dir=scratch_dir,
        year=year,
        state_abbr=states_in_database,
        external_dir=external_mirror,
        wait_for=[states_in_database, states_queried_qc],
    )

    missingness_qcd = qc_for_input_data_missingness_bystate_merge.submit(
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        wait_for=[states_queried_qc, qc_missingness_bystate],
    )

    validated_population = validation_population.submit(
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        wait_for=[external_mirror, universe_created],
    )

    validate_extracts_bystate = map_wrapper.submit(
        validation_extract_bystate,
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        state_abbr=states_in_database,
        wait_for=[states_in_database],
    )

    validate_extracts_merge = validation_extract_merge.submit(
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        wait_for=[validate_extracts_bystate],
    )

    item_imputation_validated = validation_item_imputation.submit(
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        wait_for=[indicators_estimated_setup_part2_00b],
    )

    validate_data_quality = validation_data_quality.submit(
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        wait_for=[validate_extracts_merge],
    )

    block_imputation_validated = validation_block_imputation.submit(
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        wait_for=[blocks_imputed, pop_totals_updated],
    )
    copula_imputed_validation_summary = validation_copula_imputation_aggregate.submit(
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        wait_for=[copula_part_2_validated_flow],
    )

    # This task should wait for all parallel tasks to finish and possibly fail before running
    # Thus it waits for all tasks that don't rely on each other
    logs_combined = combine_logs.submit(
        scratch_dir=scratch_dir,
        wait_for=[
            allow_failure(created_additional_columns_flow),
            allow_failure(copula_part_1_flow),
            allow_failure(copula_part_2_flow),
            allow_failure(copula_part_2_validated_flow),
            allow_failure(copula_stacked_flow),
            allow_failure(copula_imputed_summary),
            allow_failure(final_estimates_suppression_flow),
            allow_failure(final_estimated_merged),
            allow_failure(estimates_index_created),
            allow_failure(input_data_qcd),
            allow_failure(partial_reporters_qcd),
            allow_failure(missingness_qcd),
            allow_failure(qc_missingness),
            allow_failure(qc_missingness_bystate),
            allow_failure(validated_population),
            allow_failure(item_imputation_validated),
            allow_failure(validate_data_quality),
            allow_failure(block_imputation_validated),
            allow_failure(copula_imputed_validation_summary),
        ],
    )

    """ The comment below is based on Prefect 1 & 2. For Prefect 3, see https://docs.prefect.io/v3/resources/upgrade-to-prefect-3#flow-final-states """
    # The success/failure of the overall flow is determined by the
    # success/failure of the reference tasks. By default, all leaf node tasks
    # are reference tasks. But that would be the save_scratch task in this case,
    # which actually has the opposite success/failure state than what we want
    # because of its any_failed trigger:
    #   - When an earlier task fails, the save_scratch task runs. When that task
    #     succeeds, prefect thinks the flow succeeded.
    #   - When all earlier tasks succeed, save_scratch fails because its trigger
    #     failed. This makes prefect think the flow failed.
    # Really, we want to know if the final_estimates task succeeded.

    # Ensure all tasks have completed before returning, otherwise they're simply garbage collected
    # https://docs.prefect.io/v3/develop/task-runners#submit-tasks-to-a-task-runner
    for maybe_future in locals().values():
        if isinstance(maybe_future, PrefectFuture):
            maybe_future.wait()
        elif isinstance(maybe_future, list) and all(
            isinstance(f, PrefectFuture) for f in maybe_future
        ):
            wait(maybe_future)

    return logs_combined


@flow(name="SRS Flow", description="Flow to run srs pipeline", **custom_flow_params)
def flow_srs(run_id: str):
    # PIPELINE SETUP
    year = 2021
    flow_name = "srs"

    if os.getenv("IS_PROD", False):
        # For the child flows, we need to re-use the current task runner created
        # for the parent flow. Otherwise Prefect tries to create a new task
        # runner for each child flow and throws an error saying a task runner has
        # already been started.
        child_task_runner = DaskTaskRunner(
            address=get_run_context().task_runner._client.scheduler_info()["address"]
        )
        options = {
            "task_runner": child_task_runner,
        }
    else:
        options = {}

    scratch_dir = create_scratch_dir.submit(run_id=run_id, flow_name=flow_name)

    create_run_metadata.submit(
        scratch_dir=scratch_dir,
        run_id=run_id,
        flow_name=flow_name,
        wait_for=[scratch_dir],
    )

    external_config = copy_external_file_json.submit(
        scratch_dir, wait_for=[scratch_dir]
    )

    external_mirror = fetch_external_files.submit(
        store=store,
        external_config=external_config,
        scratch_dir=scratch_dir,
        wait_for=[scratch_dir, external_config],
    )

    states_in_database = get_states_in_database.submit(
        scratch_dir=scratch_dir,
        year=year,
    )

    year_list = get_years_in_database.submit(year)

    universe_created = map_wrapper.submit(
        universe_file,
        scratch_dir=scratch_dir,
        year=year_list,
        external_dir=external_mirror,
        wait_for=[external_mirror, year_list],
    )

    srs_retamm_created = srs_retamm_file.submit(
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        wait_for=[external_mirror, universe_created],
    )

    officers_imputed = impute_officers.submit(
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        wait_for=[srs_retamm_created],
    )

    universe_updated = update_universe.submit(
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        wait_for=[officers_imputed],
    )

    pop_totals_updated = update_pop_totals.submit(
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        pipeline="SRS",
        wait_for=[universe_updated],
    )

    year_queried = queries_by_data_year.submit(
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        wait_for=[external_mirror],
    )

    # IN PRODUCTION USE THE all OUTPUT OF THIS TASK
    missed_months = map_wrapper.submit(
        missing_months,
        scratch_dir=scratch_dir,
        year=year_list,
        external_dir=external_mirror,
        wait_for=[external_mirror, year_list, universe_updated, year_queried],
    )

    # IN PRODUCTION USE THE all OUTPUT OF THIS TASK
    partial_reporters_calculated = partial_reporters.submit(
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        wait_for=[missed_months],
    )

    # IN PRODUCTION USE THE all OUTPUT OF THIS TASK
    outliers_detected = outlier_detection.submit(
        scratch_dir=scratch_dir,
        year=year,
        wait_for=[partial_reporters_calculated],
    )

    srs_weights_created = srs_weighting.submit(
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        wait_for=[outliers_detected, srs_retamm_created, pop_totals_updated],
    )

    # IN PRODUCTION USE THE all OUTPUT OF THIS TASK
    # also now depends on NIBRS setup having been run
    blocks_imputed = block_imputation.submit(
        scratch_dir=scratch_dir,
        year=year,
        wait_for=[outliers_detected, srs_retamm_created],
    )

    srs_bystate_converted = map_wrapper.submit(
        srs_conversion_bystate,
        scratch_dir=scratch_dir,
        year=year,
        state_abbr=states_in_database,
        external_dir=external_mirror,
        wait_for=[external_mirror, states_in_database],
    )

    srs_qc_converted = map_wrapper.submit(
        srs_qc_conversion_reports,
        scratch_dir=scratch_dir,
        year=year,
        state=states_in_database,
        external_dir=external_mirror,
        wait_for=[states_in_database, srs_bystate_converted],
    )

    srs_conversion_finalized = srs_conversion.submit(
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        wait_for=[srs_bystate_converted, blocks_imputed],
    )

    # USER WARNING: this runs the first two programs from NIBRS weighting
    srs_blocks_imputed = srs_block_imputation.submit(
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        wait_for=[outliers_detected, srs_qc_converted, srs_conversion_finalized],
    )

    srs_weights_setup = srs_indicator_estimation_setup_weights.submit(
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        wait_for=[srs_weights_created],
    )

    srs_cleanframe_setup = srs_indicator_estimation_setup_clean_frame.submit(
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        wait_for=[srs_weights_created, srs_blocks_imputed],
    )

    srs_rawframe_setup = srs_indicator_estimation_setup_raw_frame.submit(
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        wait_for=[srs_weights_created, srs_blocks_imputed],
    )

    (
        srs_tables,
        srs_estimate_combos,
    ) = srs_indicator_estimation_get_table_combinations.submit(
        scratch_dir,
    ).result()

    srs_indicators_estimated_tables_part1_preprocessing = (
        map_wrapper.submit(
            srs_indicator_estimation_tables_part1_preprocessing,
            scratch_dir=scratch_dir,
            year=year,
            external_dir=external_mirror,
            table_name=srs_tables,
            wait_for=[
                srs_tables,
                srs_rawframe_setup,
                srs_cleanframe_setup,
                srs_weights_setup,
            ],
        )
    )

    srs_indicators_estimated_tables_part2_generate_est = (
        map_wrapper.submit(
            srs_indicator_estimation_tables_part2_generate_est,
            scratch_dir=scratch_dir,
            year=year,
            external_dir=external_mirror,
            table_est_combo=srs_estimate_combos,
            wait_for=[
                srs_estimate_combos,
                srs_indicators_estimated_tables_part1_preprocessing,
            ],
        )
    )

    srs_indicators_estimated_tables_part3_finalize = (
        map_wrapper.submit(
            srs_indicator_estimation_tables_part3_finalize,
            scratch_dir=scratch_dir,
            year=year,
            external_dir=external_mirror,
            table_name=srs_tables,
            wait_for=[
                srs_tables,
                srs_indicators_estimated_tables_part2_generate_est,
            ],
        )
    )

    srs_part1_computed = map_wrapper.submit(
        srs_copula_imputation_step1,
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        table=[
            "SRS1a",
            "SRS2a",
        ],
        wait_for=[
            srs_indicators_estimated_tables_part3_finalize,
        ],
    )

    srs_part2_groups = srs_get_copula_part2_combos.submit(
        tables=srs_tables,
        wait_for=[srs_tables, srs_indicators_estimated_tables_part3_finalize],
    )
    srs_part2_imputed = map_wrapper.submit(
        srs_copula_imputation_step2_imp,
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        combo=srs_part2_groups,
        wait_for=[
            srs_part1_computed,
            srs_part2_groups,
        ],
    )

    srs_part2_stacked = map_wrapper.submit(
        srs_copula_imputation_step2_stack,
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        table=[
            "SRS1a",
            "SRS2a",
        ],
        wait_for=[
            srs_part2_imputed,
        ],
    )

    srs_copula_imputed_step3_01 = srs_copula_imputation_step3_01_template.submit(
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        wait_for=[srs_part2_stacked],
    )

    variance_flow = flow_variance_srs.with_options(**options)(
        scratch_dir=scratch_dir,
        external_mirror=external_mirror,
        external_config=external_config,
        year=year,
        wait_for=[srs_copula_imputed_step3_01],
    )

    srs_final_permutations_list = srs_get_final_estimation_permutation_list.submit(
        scratch_dir=scratch_dir,
        external_config=external_config,
        external_dir=external_mirror,
        year=year,
        wait_for=[variance_flow],
    )

    srs_final_permutations_grps = create_general_groups.submit(
        scratch_dir=scratch_dir,
        perm_list=srs_final_permutations_list,
        group_name="srs_final_permutations",
        wait_for=[srs_final_permutations_list],
    ).result()

    srs_final_permutations_grp_1 = get_specific_group.submit(
        scratch_dir=scratch_dir,
        groups=srs_final_permutations_grps,
        group_num=1,
        task_list_name="srs_final_permutations_list",
        wait_for=[srs_final_permutations_grps],
    )

    srs_final_estimates_calculated_1 = map_wrapper.submit( # noqa: F841
        srs_final_estimates,  
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        permutation_name=srs_final_permutations_grp_1,
        wait_for=[
            srs_final_permutations_grp_1,
        ],
    )

    srs_final_permutations_grp_2 = get_specific_group.submit(
        scratch_dir=scratch_dir,
        groups=srs_final_permutations_grps,
        group_num=2,
        task_list_name="srs_final_permutations_list",
        wait_for=[srs_final_estimates_calculated_1],
    )

    srs_final_estimates_calculated_2 = map_wrapper.submit( # noqa: F841
        srs_final_estimates,
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        permutation_name=srs_final_permutations_grp_2,
        wait_for=[
            srs_final_permutations_grp_2,
        ],
    )

    srs_final_estimated_merged = srs_final_estimates_merged.submit(
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        wait_for=[srs_final_estimates_calculated_2],
    )

    combined_logs = combine_logs.submit(
        scratch_dir=scratch_dir,
        wait_for=[
            allow_failure(srs_final_estimates_calculated_1),
            allow_failure(srs_final_permutations_list),
            allow_failure(srs_final_estimated_merged),
        ],
    )
    for maybe_future in locals().values():
        if isinstance(maybe_future, PrefectFuture):
            maybe_future.wait()
        elif isinstance(maybe_future, list) and all(
            isinstance(f, PrefectFuture) for f in maybe_future
        ):
            wait(maybe_future)

    return combined_logs


@flow(
    name="SRS 30 year Flow",
    description="Flow to run srs 30yr pipeline",
    **custom_flow_params,
)
def flow_srs_30(run_id: str):
    # PIPELINE SETUP
    year = 2021
    flow_name = "srs_30"
    method30_flag = True

    scratch_dir = create_scratch_dir.submit(run_id=run_id, flow_name=flow_name)

    tag_definition = define_db_task_tag()
    asyncio.run(tag_definition)

    scratch_dir = create_scratch_dir.submit(run_id=run_id, flow_name=flow_name)

    create_run_metadata.submit(
        scratch_dir=scratch_dir,
        run_id=run_id,
        flow_name=flow_name,
        wait_for=[scratch_dir],
    )

    external_config = copy_external_file_json.submit(
        scratch_dir, method30=method30_flag, wait_for=[scratch_dir]
    )

    external_mirror = fetch_external_files.submit(
        store=store,
        external_config=external_config,
        scratch_dir=scratch_dir,
        wait_for=[scratch_dir, external_config],
    )

    states_in_database = get_states_in_database.submit(
        scratch_dir=scratch_dir,
        year=year,
    )

    year_list = get_years_in_database.submit(year)

    universe_created = map_wrapper.submit(
        universe_file,
        scratch_dir=scratch_dir,
        year=list(range(year - 4, year + 1)),
        external_dir=external_mirror,
        wait_for=[external_mirror, year_list],
    )

    srs_retamm_created = map_wrapper.submit(
        srs_retamm_file,
        scratch_dir=scratch_dir,
        year=list(range(year - 4, year + 1)),
        external_dir=external_mirror,
        wait_for=[external_mirror, universe_created],
    )

    officers_imputed = impute_officers.submit(
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        method30=method30_flag,
        wait_for=[srs_retamm_created],
    )

    universe_updated = update_universe.submit(
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        wait_for=[officers_imputed],
    )

    pop_totals_updated = update_pop_totals.submit(
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        pipeline="SRS_30yr",
        wait_for=[universe_updated],
    )

    year_queried = queries_by_data_year.submit(
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        wait_for=[external_mirror],
    )

    # IN PRODUCTION USE THE all OUTPUT OF THIS TASK
    missed_months = map_wrapper.submit(
        missing_months,
        scratch_dir=scratch_dir,
        year=year_list,
        external_dir=external_mirror,
        wait_for=[external_mirror, year_list, universe_updated, year_queried],
    )

    # IN PRODUCTION USE THE all OUTPUT OF THIS TASK
    partial_reporters_calculated = partial_reporters.submit(
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        wait_for=[missed_months],
    )

    # IN PRODUCTION USE THE all OUTPUT OF THIS TASK
    outliers_detected = outlier_detection.submit(
        scratch_dir=scratch_dir,
        year=year,
        wait_for=[partial_reporters_calculated],
    )

    srs_weights_created = srs_weighting.submit(
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        method30=method30_flag,
        wait_for=[outliers_detected, srs_retamm_created, pop_totals_updated],
    )

    # IN PRODUCTION USE THE all OUTPUT OF THIS TASK
    # also now depends on NIBRS setup having been run
    blocks_imputed = block_imputation.submit(
        scratch_dir=scratch_dir,
        year=year,
        wait_for=[outliers_detected, srs_retamm_created],
    )

    srs_bystate_converted = map_wrapper.submit(
        srs_conversion_bystate,
        scratch_dir=scratch_dir,
        year=year,
        state_abbr=states_in_database,
        external_dir=external_mirror,
        wait_for=[external_mirror, states_in_database],
    )

    srs_conversion_finalized = srs_conversion.submit(
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        wait_for=[srs_bystate_converted, blocks_imputed],
    )

    # USER WARNING: this runs the first two programs from NIBRS weighting
    srs_blocks_imputed = srs_block_imputation.submit(
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        method30=method30_flag,
        wait_for=[outliers_detected, srs_conversion_finalized],
    )

    srs_weights_setup = srs_indicator_estimation_setup_weights.submit(
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        method30=method30_flag,
        wait_for=[srs_weights_created],
    )

    srs_cleanframe_setup = srs_indicator_estimation_setup_clean_frame.submit(
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        method30=method30_flag,
        wait_for=[srs_weights_created, srs_blocks_imputed],
    )

    srs_rawframe_setup = srs_indicator_estimation_setup_raw_frame.submit(
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        method30=method30_flag,
        wait_for=[srs_weights_created, srs_blocks_imputed],
    )

    (
        srs_tables,
        srs_estimate_combos,
    ) = srs_indicator_estimation_get_table_combinations.submit(
        scratch_dir,
        method30_flag,
    ).result()

    srs_indicators_estimated_tables_part1_preprocessing = (
        map_wrapper.submit(
            srs_indicator_estimation_tables_part1_preprocessing,
            scratch_dir=scratch_dir,
            year=year,
            external_dir=external_mirror,
            table_name=srs_tables,
            method30=method30_flag,
            wait_for=[
                srs_tables,
                srs_rawframe_setup,
                srs_cleanframe_setup,
                srs_weights_setup,
            ],
        )
    )

    srs_indicators_estimated_tables_part2_generate_est = (
        map_wrapper.submit(
            srs_indicator_estimation_tables_part2_generate_est,
            scratch_dir=scratch_dir,
            year=year,
            external_dir=external_mirror,
            table_est_combo=srs_estimate_combos,
            method30=method30_flag,
            wait_for=[
                srs_estimate_combos,
                srs_indicators_estimated_tables_part1_preprocessing,
            ],
        )
    )

    srs_indicators_estimated_tables_part3_finalize = (
        map_wrapper.submit(
            srs_indicator_estimation_tables_part3_finalize,
            scratch_dir=scratch_dir,
            year=year,
            external_dir=external_mirror,
            table_name=srs_tables,
            method30=method30_flag,
            wait_for=[
                srs_tables,
                srs_indicators_estimated_tables_part2_generate_est,
            ],
        )
    )

    srs_part1_computed = map_wrapper.submit(
        srs_copula_imputation_step1,
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        table=[
            "SRS1a",
        ],
        method30=method30_flag,
        wait_for=[
            srs_indicators_estimated_tables_part3_finalize,
        ],
    )

    srs_part2_groups = srs_get_copula_part2_combos.submit(
        tables=srs_tables,
        method30=method30_flag,
        wait_for=[srs_tables, srs_indicators_estimated_tables_part3_finalize],
    )
    srs_part2_imputed = map_wrapper.submit(
        srs_copula_imputation_step2_imp,
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        combo=srs_part2_groups,
        method30=method30_flag,
        wait_for=[
            srs_part1_computed,
            srs_part2_groups,
        ],
    )

    srs_part2_stacked = map_wrapper.submit(
        srs_copula_imputation_step2_stack,
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        method30=method30_flag,
        table=[
            "SRS1a",
        ],
        wait_for=[
            srs_part2_imputed,
        ],
    )

    srs_copula_imputed_step3_01 = srs_copula_imputation_step3_01_template.submit(
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        method30=method30_flag,
        wait_for=[srs_part2_stacked],
    )

    variance_1 = map_wrapper.submit(
        srs_copula_imputation_step3_02_variance,
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        combo=[("SRS1a", 1), ("SRS1araw", 1)],
        method30=method30_flag,
        wait_for=[srs_copula_imputed_step3_01],
    )

    srs_final_estimates_calculated = map_wrapper.submit( # noqa: F841
        srs_final_estimates,
        scratch_dir=scratch_dir,
        year=year,
        external_dir=external_mirror,
        permutation_name=[1],
        wait_for=[
            variance_1,
        ],
    )

    combined_logs = combine_logs.submit(
        scratch_dir=scratch_dir,
        wait_for=[
            allow_failure(srs_final_estimates_calculated),
        ],
    )
    for maybe_future in locals().values():
        if isinstance(maybe_future, PrefectFuture):
            maybe_future.wait()
        elif isinstance(maybe_future, list) and all(
            isinstance(f, PrefectFuture) for f in maybe_future
        ):
            wait(maybe_future)

    return combined_logs


@flow(
    name="Run BJS Grant Flow",
    description="Flow to create BJS grant files",
    **custom_flow_params,
)
def flow_bjs_grant(run_id: str):
    # PIPELINE SETUP
    year = 2022
    flow_name = "bjs_grant"

    scratch_dir = create_scratch_dir.submit(run_id=run_id, flow_name=flow_name)

    tag_definition = define_db_task_tag()
    asyncio.run(tag_definition)

    create_run_metadata.submit(
        scratch_dir=scratch_dir,
        run_id=run_id,
        flow_name=flow_name,
    )

    external_config = copy_external_file_json.submit(scratch_dir)

    external_mirror = fetch_external_files.submit(
        store=store, external_config=external_config, scratch_dir=scratch_dir
    )

    year_list = get_ten_years_in_database.submit(year, wait_for=[external_mirror])

    states_in_database = get_states_in_database.submit(
        scratch_dir=scratch_dir,
        year=year,
    )

    bjs_state_year_list = bjs_grant_conversion_bystate_combinations.submit(
        scratch_dir=scratch_dir,
        year_list=year_list,
        states_list=states_in_database,
        wait_for=[year_list, states_in_database],
    )

    # INITIAL TASKS
    # tasks related to generating previously external files
    universe_created = map_wrapper.submit(
        universe_file,
        scratch_dir=scratch_dir,
        year=year_list,
        external_dir=external_mirror,
        wait_for=[external_mirror],
    )

    srs_retamm_created = map_wrapper.submit(
        srs_retamm_file,
        scratch_dir=scratch_dir,
        year=year_list,
        external_dir=external_mirror,
        wait_for=[universe_created],
    )

    # BJS Grant tasks
    bjs_grant_bystate_converted = map_wrapper.submit(
        bjs_grant_conversion_bystate,
        scratch_dir=scratch_dir,
        state_year=bjs_state_year_list,
        external_dir=external_mirror,
        wait_for=[bjs_state_year_list],
    )

    bjs_grant_conversion_finalized = map_wrapper.submit(
        bjs_grant_conversion,
        scratch_dir=scratch_dir,
        year=year_list,
        external_dir=external_mirror,
        wait_for=[srs_retamm_created, bjs_grant_bystate_converted],
    )

    bjs_grant_combined = bjs_grant_combine.submit(
        scratch_dir=scratch_dir,
        year_list=year_list,
        external_dir=external_mirror,
        wait_for=[bjs_grant_conversion_finalized],
    )

    combined_logs = combine_logs.submit(
        scratch_dir=scratch_dir,
        wait_for=[
            allow_failure(bjs_grant_conversion_finalized),
            allow_failure(bjs_grant_combined),
        ],
    )
    for maybe_future in locals().values():
        if isinstance(maybe_future, PrefectFuture):
            maybe_future.wait()
        elif isinstance(maybe_future, list) and all(
            isinstance(f, PrefectFuture) for f in maybe_future
        ):
            wait(maybe_future)

    return combined_logs


@flow(
    name="metrics",
    description="Collect performance metrics for a flow's tasks",
    **custom_flow_params,
)
def flow_metrics(target_run_id: str, target_flow_name: str):
    scratch_dir = create_scratch_dir.submit(
        run_id=target_run_id, flow_name=target_flow_name
    )
    collect_task_metrics.submit(scratch_dir=scratch_dir)


FLOWS = {
    "smoketest": flow_smoketest,
    "all": flow_all,
    "srs": flow_srs,
    "metrics": flow_metrics,
    "bjs_grant": flow_bjs_grant,
    "srs_30": flow_srs_30,
}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    register_parser = subparsers.add_parser(
        "register",
        help="Register the flows with a Prefect server",
    )
    register_parser.add_argument(
        "--flow-name",
        type=str,
        choices=FLOWS.keys(),
        nargs="+",
        default=None,
        help="Name of the flow(s) to register. Default: Register every flow.",
    )
    run_parser = subparsers.add_parser("run", help="Run a flow")
    run_parser.add_argument(
        "flow_name",
        type=str,
        choices=FLOWS.keys(),
        help="Name of the flow to run",
    )
    run_parser.add_argument(
        "run_id",
        type=str,
        help="ID to assign to the flow run",
    )
    args = parser.parse_args()

    if args.command == "register":
        if args.flow_name is None:
            flow_names_to_register = FLOWS.keys()
        else:
            flow_names_to_register = args.flow_name
        for flow_name in flow_names_to_register:
            FLOWS[flow_name].register(project_name="nibrs-estimation")
    elif args.command == "run":
        if os.getenv("IS_PROD", False):
            raise ValueError(
                "Script is not designed to be run in 'run' mode "
                "with production (IS_PROD) settings."
            )
        FLOWS[args.flow_name](run_id=args.run_id)
        
