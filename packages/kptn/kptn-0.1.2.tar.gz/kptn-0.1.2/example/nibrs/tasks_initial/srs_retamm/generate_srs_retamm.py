import os
from pathlib import Path

import pandas as pd
from dictionaries import col_list, col_start_index, month_dict, srs_column_names
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


def get_srs_column_name(row: dict) -> str:
    month = int(row["data_month"])
    variable = row["variable"]
    return "v" + str(col_list.index(variable) + col_start_index[month - 1])


def get_cleaned_universe_files(univ_path: Path, year: str) -> pd.DataFrame:
    """This function reads in the Universe file and renames some columns."""
    universe_raw = pd.read_csv(Path(univ_path) / f"orig_ref_agency_{year}.csv")
    universe_raw.rename(
        columns={c: f"{c}_UNIV" for c in universe_raw.columns if c != "ORI"},
        inplace=True,
    )
    universe_raw = universe_raw.rename(
        columns={
            "ORI": "ORI_UNIV",
            "FEMALE_OFFICER+FEMALE_CIVILIAN_UNIV": "FEMALE_OFFICER_FEMALE_CIVIL_UNIV",
            "LEGACY_ORI_UNIV": "ORI",
            "MALE_OFFICER+MALE_CIVILIAN_UNIV": "MALE_OFFICER_MALE_CIVILIAN_UNIV",
            "MSA_NAME_UNIV": "MSA_UNIV",
            "PE_FEMALE_CIVILIAN_COUNT_UNIV": "FEMALE_CIVILIAN_UNIV",
            "PE_FEMALE_OFFICER_COUNT_UNIV": "FEMALE_OFFICER_UNIV",
            "PE_MALE_CIVILIAN_COUNT_UNIV": "MALE_CIVILIAN_UNIV",
            "PE_MALE_OFFICER_COUNT_UNIV": "MALE_OFFICER_UNIV",
        }
    ).drop(columns=["UCR_AGENCY_NAME_UNIV"])

    return universe_raw


def get_srs_missing_month(engine_database: Engine, year: str) -> pd.DataFrame:
    """This function prepares in the missing month table for all NIBRS/Return A reporters."""
    missing_month_query = f"""
        SELECT nm.data_year,
            nm.data_month,
            a.legacy_ori
        FROM ucr_prd.form_month nm
        LEFT JOIN ucr_prd.ref_agency a on a.agency_id = nm.agency_id
        WHERE
        nm.form_code IN ('N','R')
        AND nm.data_year = {year}
    """

    db_reta_mm = pd.read_sql(missing_month_query, engine_database).drop_duplicates()

    # cast numeric months to strings and then transform them into one binary column per month
    db_reta_mm["data_month"] = db_reta_mm["data_month"].apply(lambda x: month_dict[x])
    db_reta_mm = pd.get_dummies(db_reta_mm, columns=["data_month"]).fillna(0)
    for month in month_dict.values():
        db_reta_mm.rename(
            columns={f"data_month_{month}": f"{month}_mm_flag"}, inplace=True
        )

    # for each agency, sum up the binary month columns to get one row per agency
    db_reta_mm = (
        db_reta_mm.groupby(["legacy_ori", "data_year"])
        .sum()
        .reset_index()
        .rename(columns={"legacy_ori": "ORI"})
    )

    # for those few agencies that were reported as both N and R, cast those 2's back to 1's
    for month in month_dict.values():
        db_reta_mm[f"{month}_mm_flag"] = db_reta_mm[f"{month}_mm_flag"].apply(
            lambda x: 1 if x >= 1 else 0
        )

    return db_reta_mm


def get_srs_actual_counts(engine_database: Engine, year: str) -> pd.DataFrame:
    """This function prepares the v columns of the Return A SRS file."""
    srs_count_query = f"""
        select
            ra.legacy_ori,
            lso.offense_name,
            lso.breakdown_name,
            data_month,
            sum(smo.actual_count) from ucr_prd.form_month fm
        join ucr_prd.sum_month_offense smo using(form_month_id)
        join ucr_prd.ref_agency ra using (agency_id)
        join ucr_prd.lkup_srs_offense lso using (breakdown_id)
        where
        data_year = {year}
        group by ra.legacy_ori, lso.offense_name,lso.breakdown_name, data_month
    """
    srs_frame_raw = pd.read_sql(srs_count_query, engine_database).drop_duplicates()
    srs_frame_raw.rename(columns={"legacy_ori": "ORI"}, inplace=True)

    # recode so simple and aggravated assault have the same broad category
    srs_frame_raw["offense_name"] = srs_frame_raw["offense_name"].apply(
        lambda x: "Assault" if x in ["Aggravated Assault", "Simple Assault"] else x
    )
    srs_frame_raw["offense_name"] = srs_frame_raw["offense_name"].apply(
        lambda x: (
            "Rape (Legacy)" if x in ["Rape (Legacy)", "Attempted Rape (Legacy)"] else x
        )
    )

    # get the total sums for each broad offense type
    srs_frame_totals = (
        srs_frame_raw.groupby(["ORI", "offense_name", "data_month"])["sum"]
        .sum()
        .reset_index()
    )
    srs_frame_totals["variable"] = "Total " + srs_frame_totals["offense_name"]
    srs_frame_totals.drop(columns=["offense_name"], inplace=True)

    # merge the offense totals together with the detailed groups since the final
    # variables include both
    srs_frame_clean = pd.concat(
        [
            srs_frame_totals,
            srs_frame_raw.rename(columns={"breakdown_name": "variable"})[
                ["ORI", "variable", "data_month", "sum"]
            ],
        ]
    ).reset_index(drop=True)

    # subset to the list of variables in the v columns of interest
    srs_frame_converted = srs_frame_clean.loc[
        srs_frame_clean["variable"].isin(srs_column_names.keys())
    ].copy()

    # calculate the overall total for the month for each agency
    # note that this uses all detailed groups along with "Total Larceny"
    srs_frame_converted_total = (
        srs_frame_converted.loc[
            srs_frame_converted["variable"].isin(
                [
                    "Assault - Firearm",
                    "Assault - Hands, Fists, Feet",
                    "Assault - Knife or Cutting Instrument",
                    "Assault - Other Dangerous Weapon",
                    "Burglary - Attempted Forcible Entry",
                    "Burglary - Forcible Entry",
                    "Burglary - No Force",
                    "Auto Theft",
                    "Other Vehicle Theft",
                    "Truck and Bus Theft",
                    "Murder and Nonnegligent Homicide",
                    "Attempted Rape",
                    "Rape",
                    "Robbery - Firearm",
                    "Robbery - Hands, Fists, Feet",
                    "Robbery - Knife or Cutting Instrument",
                    "Robbery - Other Dangerous Weapon",
                    "Simple Assault",
                    "Manslaughter by Negligence",
                    "Total Larceny",
                ]
            )
        ]
        .groupby(["ORI", "data_month"])["sum"]
        .sum()
        .reset_index()
    )
    srs_frame_converted_total["variable"] = "Grand Total"

    # concatenate on the monthly totals and covert variable names to v variables
    srs_frame_converted = pd.concat(
        [srs_frame_converted, srs_frame_converted_total]
    ).reset_index(drop=True)
    srs_frame_converted["variable"] = srs_frame_converted["variable"].apply(
        lambda x: srs_column_names[x]
    )
    srs_frame_converted["SRS_col"] = srs_frame_converted.apply(
        get_srs_column_name, axis=1
    )

    # pivot the dataframe so we have one column per variable and fill nulls with 0's
    srs_frame_converted = (
        srs_frame_converted.pivot(index="ORI", columns="SRS_col", values="sum")
        .fillna(0)
        .astype(int)
        .reset_index()
    )
    return srs_frame_converted


if __name__ == "__main__":
    external_path = Path(str(os.getenv("EXTERNAL_FILE_PATH")))
    year = os.getenv("DATA_YEAR")
    output_dir = Path(str(os.getenv("OUTPUT_PIPELINE_DIR"))) / "initial_tasks_output"
    output_dir.mkdir(exist_ok=True)

    engine_database = create_engine(
        "postgresql://"
        + str(os.getenv("PGUSER"))
        + ":"
        + str(os.getenv("PGPASSWORD"))
        + "@"
        + str(os.getenv("PGHOST"))
        + ":"
        + str(os.getenv("PGPORT"))
        + "/"
        + str(os.getenv("PGDATABASE"))
    )

    universe_raw = get_cleaned_universe_files(output_dir, str(year))
    db_reta_mm = get_srs_missing_month(engine_database, str(year))
    db_srs_counts = get_srs_actual_counts(engine_database, str(year))

    full_db_reta = db_reta_mm.merge(db_srs_counts, on=["ORI"], how="outer").fillna(0)
    full_db_reta = universe_raw.merge(full_db_reta, on=["ORI"], how="left")

    # for the agencies that were in universe but not in the database, fill the months
    # with 9's if the agency is covered and 0's if not
    fill_na = full_db_reta["COVERED_FLAG_UNIV"].apply(lambda x: 9 if x == "Y" else 0)
    for missing_month_field in [f"{m}_mm_flag" for m in month_dict.values()]:
        full_db_reta[missing_month_field] = (
            full_db_reta[missing_month_field].fillna(fill_na).astype(int)
        )

    if int(year) == 2024:
        lapd_df = pd.read_csv("./data/UCR_SRS_2024_LAPD.csv")
        full_db_reta = full_db_reta.loc[full_db_reta["ORI"] != "CA0194200"]
        full_db_reta = (
            pd.concat([full_db_reta, lapd_df], ignore_index=True)
            .sort_values(by=["AGENCY_ID_UNIV"])
            .reset_index(drop=True)
        )

    # for those same agencies missing from the database, fill all v variables with 0's
    for v_col in [c for c in full_db_reta.columns if c.startswith("v")]:
        full_db_reta[v_col] = full_db_reta[v_col].fillna(0).astype(int)

    # fill some missing data_year values
    full_db_reta["data_year"] = full_db_reta["data_year"].fillna(year)

    full_db_reta.to_csv(
        output_dir / f"UCR_SRS_{year}_clean_reta_mm_selected_vars.csv", index=False
    )
