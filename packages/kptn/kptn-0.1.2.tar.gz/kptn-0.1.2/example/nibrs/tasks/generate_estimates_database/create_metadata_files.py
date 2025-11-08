import pandas as pd
import os
from pathlib import Path
import json
from tasks.generate_estimates_database.utils.database_manager import DatabaseManager
from tasks.generate_estimates_database.utils.load_functions import load_into_database
from tasks.generate_estimates_database.utils.config import logger

def create_estimates_lookup(base_dir, year, output_dir, estimates_db):
    """Creates Estimates Lookup Table:
    - Processes Reporting Database files
    - Generates unique identifiers for estimates
    - Creates derived variable names
    - Maps estimate domains and relationships
    """
    logger.info("Running create_estimates_lookup")
    tables_folder = base_dir / "indicator_table_estimates"
    estimates_file_list = [
        pd.read_csv(tables_folder / f)
        for f in os.listdir(tables_folder)
        if f.endswith("Reporting_Database.csv")
    ]
    print("Processing", len(estimates_file_list), "tables.")
    reporting_db_df = pd.concat(estimates_file_list)
    der_variable_name = reporting_db_df[
        [
            "full_table",
            "table",
            "section",
            "row",
            "column",
            "estimate_domain",
            "estimate_type",
            "indicator_name",
        ]
    ].drop_duplicates()
    der_variable_name["der_variable_name"] = (
        "t_"
        + der_variable_name["table"]
        + "_"
        + der_variable_name["section"].astype(str)
        + "_"
        + der_variable_name["row"].astype(str)
        + "_"
        + der_variable_name["column"].astype(str)
    )
    der_variable_name["rate_specific_domain"] = (
        der_variable_name["table"] == "GV2a"
    ) & (der_variable_name["estimate_type"] == "rate")
    der_variable_name = der_variable_name.drop(
        columns=["estimate_type", "section", "row", "column"]
    ).drop_duplicates()
    der_variable_name["unique_id"] = der_variable_name[
        "der_variable_name"
    ] + der_variable_name["rate_specific_domain"].astype(str)
    der_variable_name["estimate_domain_1"] = der_variable_name["estimate_domain"].apply(
        lambda x: x if ":" not in x else x.split(":")[0].strip()
    )
    der_variable_name["estimate_domain_2"] = der_variable_name["estimate_domain"].apply(
        lambda x: None if ":" not in x else x.split(":")[1].strip()
    )
    der_variable_name = (
        der_variable_name[
            [
                "der_variable_name",
                "rate_specific_domain",
                "full_table",
                "indicator_name",
                "estimate_domain_1",
                "estimate_domain_2",
            ]
        ]
        .reset_index(drop=True)
        .reset_index()
        .rename(columns={"index": "estimate_pk"})
    )
    logger.debug(f"Lookup file dim: {der_variable_name.shape}")
    logger.debug("Writing estimates lookup to table")
    estimates_db.run_sql(sql="DROP TABLE IF EXISTS der_variable_name_lookup")
    estimates_db.run_sql(
        sql="""
        CREATE TABLE If NOT EXISTS der_variable_name_lookup (
            estimate_pk integer, 
            der_variable_name text, 
            rate_specific_domain bool, 
            full_table text, 
            indicator_name text, 
            estimate_domain_1 text, 
            estimate_domain_2 text
        )
    """
    )

    der_variable_name.to_csv(output_dir / f"DY{year}_estimate_lookup.csv", index=False)
    results, total_time = load_into_database(
        [tuple(row) for row in der_variable_name.to_numpy()],
        estimates_db,
        "der_variable_name_lookup",
        der_variable_name.columns.values.tolist(),
    )
    logger.debug(f"Completed in time: {total_time}")
    logger.debug(results)


def create_population_lookup(base_dir, year, external_path, output_dir, estimates_db):
    """Creates Population Lookup Table:
    - Processes population external files
    - Standardizes age range formatting
    - Maps permutation numbers to geographic locations
    - Handles population coverage metrics
    """
    logger.info("Running create_population_lookup")

    with open(base_dir / "external_file_locations.json", "r") as json_file:
        locations = json.load(json_file)
    pop_file_path = locations[year]["population"]
    population_file = (
        pd.read_csv(
            external_path / pop_file_path,
            usecols=[
                "PERMUTATION_NUMBER",
                "WEIGHT_VAR",
                "UNIV_POP_COV",
                "ORIG_UNIV_ELIG_PERM_AGENCY_MISSING_OVER_10_PERCENT",
                "ORIG_ELIG_PERM_AGENCY_MISSING_PRINCIPAL_CITY",
            ],
        )
        .drop_duplicates()
        .rename(
            columns={
                "WEIGHT_VAR": "analysis_weight_name",
                "UNIV_POP_COV": "pop_cov",
                "ORIG_UNIV_ELIG_PERM_AGENCY_MISSING_OVER_10_PERCENT": "POPTOTAL_ORIG_UNIV_ELIG_PERM_AGENCY_MISSING_OVER_10_PERCENT",
                "ORIG_ELIG_PERM_AGENCY_MISSING_PRINCIPAL_CITY": "POPTOTAL_ORIG_ELIG_PERM_AGENCY_MISSING_PRINCIPAL_CITY",
            }
        )
        .reset_index()
        .rename(columns={"index": "population_pk"})
    )
    population_file["GEOGRAPHIC_PERMUTATION"] = (
        population_file["PERMUTATION_NUMBER"] % 1000
    )
    population_file["DEMOGRAPHIC_PERMUTATION"] = (
        1000 * (population_file["PERMUTATION_NUMBER"] // 1000)
    ).replace({0: None})

    df_geography = pd.read_excel(
        "../copula_imputation/part3_generate_prb/Data/Permutation for Indicator Tables.xlsx",
        usecols=["permutation_number", "permutation_number_desc"],
    ).rename(
        columns={
            "permutation_number": "GEOGRAPHIC_PERMUTATION",
            "permutation_number_desc": "GEOGRAPHIC_DESCRIPTION",
        }
    )
    df_demographics = pd.read_excel(
        "../copula_imputation/part3_generate_prb/Data/Demo Permutation for Indicator Tables.xlsx",
        usecols=["permutation_series_add", "permutation_series_add_desc"],
    ).rename(
        columns={
            "permutation_series_add": "DEMOGRAPHIC_PERMUTATION",
            "permutation_series_add_desc": "DEMOGRAPHIC_DESCRIPTION",
        }
    )

    population_file = population_file.merge(
        df_geography, on=["GEOGRAPHIC_PERMUTATION"], how="left"
    ).merge(df_demographics, on=["DEMOGRAPHIC_PERMUTATION"], how="left")[
        [
            "population_pk",
            "PERMUTATION_NUMBER",
            "DEMOGRAPHIC_PERMUTATION",
            "GEOGRAPHIC_PERMUTATION",
            "DEMOGRAPHIC_DESCRIPTION",
            "GEOGRAPHIC_DESCRIPTION",
            "analysis_weight_name",
            "pop_cov",
            "POPTOTAL_ORIG_UNIV_ELIG_PERM_AGENCY_MISSING_OVER_10_PERCENT",
            "POPTOTAL_ORIG_ELIG_PERM_AGENCY_MISSING_PRINCIPAL_CITY",
        ]
    ]

    logger.debug(f"Lookup file dim: {population_file.shape}")
    logger.debug("Writing population lookup to table")
    estimates_db.run_sql(sql="DROP TABLE IF EXISTS population_lookup")
    estimates_db.run_sql(
        sql="""
        CREATE TABLE If NOT EXISTS population_lookup (
            population_pk integer,
            PERMUTATION_NUMBER integer,
            DEMOGRAPHIC_PERMUTATION integer,
            GEOGRAPHIC_PERMUTATION integer,
            DEMOGRAPHIC_DESCRIPTION text,
            GEOGRAPHIC_DESCRIPTION text,
            analysis_weight_name text,
            pop_cov float,
            POPTOTAL_ORIG_UNIV_ELIG_PERM_AGENCY_MISSING_OVER_10_PERCENT bool,
            POPTOTAL_ORIG_ELIG_PERM_AGENCY_MISSING_PRINCIPAL_CITY bool
        )
    """
    )

    population_file.to_csv(output_dir / f"DY{year}_population_lookup.csv", index=False)
    results, total_time = load_into_database(
        [tuple(row) for row in population_file.to_numpy()],
        estimates_db,
        "population_lookup",
        population_file.columns.values.tolist(),
    )
    logger.debug(f"Completed in time: {total_time}")
    logger.debug(results)


if __name__ == "__main__":
    base_dir = Path(os.getenv("OUTPUT_PIPELINE_DIR"))
    external_path = Path(os.getenv("EXTERNAL_FILE_PATH"))
    estimates_db_name = Path(os.getenv("ESTIMATES_DB_NAME"))
    year = str(os.getenv("DATA_YEAR"))

    estimates_db = DatabaseManager(
        os.getenv("PGHOST"),
        os.getenv("PGPORT"),
        estimates_db_name,
        os.getenv("PGUSER"),
        os.getenv("PGPASSWORD"),
    )

    output_dir = base_dir / "estimates_db"

    output_dir.mkdir(exist_ok=True)

    logger.info("Generating estimates lookup file")
    create_estimates_lookup(base_dir, year, output_dir, estimates_db)
    logger.info("Generating population lookup file")
    create_population_lookup(base_dir, year, external_path, output_dir, estimates_db)
