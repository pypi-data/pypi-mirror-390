from prefect.runtime import task_run

def map_wrapper_tr_name():
    return f"{task_run.parameters['task'].__name__}-{task_run.parameters['group_num']}-wrapper"

def universe_file_tr_name():
    return f"{task_run.task_name}-{task_run.parameters['year']}"


def srs_retamm_file_tr_name():
    return f"{task_run.task_name}-{task_run.parameters['year']}"


def queries_by_state_tr_name():
    return f"{task_run.task_name}-{task_run.parameters['state_abbr']}"


def missing_months_tr_name():
    return f"{task_run.task_name}-{task_run.parameters['year']}"


def nibrs_extract_one_state_tr_name():
    return f"{task_run.task_name}-{task_run.parameters['state_abbr']}"


def item_imputation_part1_tr_name():
    return f"{task_run.task_name}-{task_run.parameters['state_abbr']}"


def item_imputation_part2_nonperson_tr_name():
    return f"{task_run.task_name}-{task_run.parameters['state_abbr']}"


def item_imputation_part2_person_tr_name():
    return f"{task_run.task_name}-{task_run.parameters['state_abbr']}"


def item_imputation_part3_finalize_tr_name():
    return f"{task_run.task_name}-{task_run.parameters['state_abbr']}"


def item_imputation_part3_5_ethnicity_tr_name():
    return f"{task_run.task_name}-{task_run.parameters['ethnicity_num']}"


def item_imputation_part3_5_ethnicity_combine_tr_name():
    return f"{task_run.task_name}-{task_run.parameters['state_abbr']}"


def item_imputation_part4_victim_offender_relationship_tr_name():
    return f"{task_run.task_name}-{task_run.parameters['state_abbr']}"


def item_imputation_part4_vor_property_tr_name():
    return f"{task_run.task_name}-{task_run.parameters['vor_num']}"


def item_imputation_part5_groupb_arrestee_tr_name():
    return f"{task_run.task_name}-{task_run.parameters['state_abbr']}"


def indicator_estimation_setup_tr_name():
    return f"{task_run.task_name}-{task_run.parameters['state_abbr']}"


def indicator_estimation_setup_part2_00b_tr_name():
    return f"{task_run.task_name}-{task_run.parameters['dataset']}"


def indicator_estimation_setup_part2_00c_clean_main_tr_name():
    return f"{task_run.task_name}-{task_run.parameters['main_to_run']}"


def indicator_estimation_tables_part1_preprocessing_tr_name():
    return f"{task_run.task_name}-{task_run.parameters['table_name']}"


def indicator_estimation_tables_part2_generate_est_tr_name():
    return f"{task_run.task_name}-{task_run.parameters['table_est_combo']}"


def indicator_estimation_tables_part3_finalize_tr_name():
    return f"{task_run.task_name}-{task_run.parameters['table_name']}"


def indicator_estimation_tables_part4_select_tables_tr_name():
    return f"{task_run.task_name}-{task_run.parameters['table_name']}"


def indicator_estimation_tables_part5_select_tables_tr_name():
    return f"{task_run.task_name}-{task_run.parameters['table_name']}"


def copula_imputation_step2_summary_tr_name():
    return f"{task_run.task_name}-{task_run.parameters['table']}"


def fill_variance_skipped_demos_tr_name():
    return f"{task_run.task_name}-{task_run.parameters['combo']}"


def final_estimates_momentum_tr_name():
    return f"{task_run.task_name}-{task_run.parameters['combo']}"


def qc_for_input_data_missingness_bystate_tr_name():
    return f"{task_run.task_name}-{task_run.parameters['state_abbr']}"


def validation_extract_bystate_tr_name():
    return f"{task_run.task_name}-{task_run.parameters['state_abbr']}"


def srs_conversion_bystate_tr_name():
    return f"{task_run.task_name}-{task_run.parameters['state_abbr']}"


def srs_qc_conversion_reports_tr_name():
    return f"{task_run.task_name}-{task_run.parameters['state_abbr']}"


def srs_indicators_estimated_tables_part1_preprocessing_tr_name():
    return f"{task_run.task_name}-{task_run.parameters['table_name']}"


def srs_indicators_estimated_tables_part2_generate_est_tr_name():
    return f"{task_run.task_name}-{task_run.parameters['table_est_combo']}"


def srs_indicators_estimated_tables_part3_finalize_tr_name():
    return f"{task_run.task_name}-{task_run.parameters['table_name']}"


def srs_copula_imputation_step1_tr_name():
    return f"{task_run.task_name}-{task_run.parameters['table']}"


def srs_copula_imputation_step2_imp_tr_name():
    return f"{task_run.task_name}-{task_run.parameters['combo']}"


def srs_copula_imputation_step2_stack_tr_name():
    return f"{task_run.task_name}-{task_run.parameters['table']}"


def bjs_grant_conversion_bystate_tr_name():
    return f"{task_run.task_name}-{task_run.parameters['state_year']}"


def bjs_grant_conversion_tr_name():
    return f"{task_run.task_name}-{task_run.parameters['year']}"
