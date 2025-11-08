import os
import pandas as pd
from tasks.generate_estimates_database.utils.database_manager import DatabaseManager
from tasks.generate_estimates_database.utils.load_functions import (
    select_and_convert_columns,
    load_into_database,
)
from tasks.generate_estimates_database.utils.config import columns_and_types, data_dict, logger
from pathlib import Path


def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """Filter and transform dataframe."""

    # CHECK IF WE STILL WANT THIS FILTER
    df = df[df["estimate"] != -9].copy()

    # add rate specific domain column
    df.loc[:, "rate_specific_domain"] = (df["full_table"].str.contains("GV2a")) & (
        df["estimate_type"] == "rate"
    )

    # add any missing columns
    for col in columns_and_types.keys():
        if col not in df.columns:
            df[col] = None

    # coerce columns to the correct data types
    df = select_and_convert_columns(df, columns_and_types)

    df = df.where(pd.notnull(df), None)
    return [tuple(row) for row in df.to_numpy()]


if __name__ == "__main__":
    estimates_db = DatabaseManager(
        os.getenv("PGHOST"),
        os.getenv("PGPORT"),
        os.getenv("ESTIMATES_DB_NAME"),
        os.getenv("PGUSER"),
        os.getenv("PGPASSWORD"),
    )

    # make sure the estimates table exists
    logger.info("Generating estimates db table")
    estimates_db.run_sql(
        sql="""
        CREATE TABLE If NOT EXISTS estimates (
                time_series_start_year integer,
                PERMUTATION_NUMBER integer,
                der_variable_name text,
                rate_specific_domain bool,
                estimate float,
                estimate_unweighted float,
                estimate_type text,
                estimate_type_num integer,
                estimate_type_detail_percentage text,
                estimate_type_detail_rate text,
                estimate_standard_error float,
                estimate_upper_bound float,
                estimate_lower_bound float,
                relative_standard_error float,
                estimate_prb float,
                estimate_bias float,
                estimate_rmse float,
                relative_rmse float,
                suppression_flag_indicator bool,
                der_elig_suppression bool,
                agency_counts float,
                der_rrmse_30 text,
                der_rrmse_gt_30_se_estimate_0_2_cond bool,
                der_rrmse_gt_30_se_estimate_0_2_cond_top float,
                der_perm_group_unsuppression_flag bool,
                der_perm_group_suppression_flag bool,
                population_estimate float,
                PRB_ACTUAL float,
                CORRELATION_WITH_PRIOR_YEAR float,
                PROP_ELIG_ORIS_NONZERO_COUNT float,
                estimate_copula float
            )
    """
    )

    # read in the specific estimates file
    table_path = (
        Path(os.getenv("OUTPUT_PIPELINE_DIR"))
        / "final-estimates"
        / "Indicator_Tables"
        / os.getenv("TOP_FOLDER")
        / os.getenv("MID_FOLDER")
    )
    file_name = f"Indicator_Tables_{os.getenv('PERMUTATION_NAME')}_{os.getenv('TABLE_NAME')}.csv"
    logger.debug(f"Reading in file {file_name}")
    path = table_path / file_name
    if not path.exists():
        raise ValueError(f"ERROR: {path} does not exist.")

    df = pd.read_csv(path, dtype=data_dict)
    df_selected = transform_data(df)
    results, total_time = load_into_database(
        df_selected, estimates_db, "estimates", list(columns_and_types.keys())
    )
    logger.debug(f"Completed in time: {total_time}")
    logger.debug(results)
