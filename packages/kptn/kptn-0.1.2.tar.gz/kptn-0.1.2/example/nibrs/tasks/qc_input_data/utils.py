import json
import os
from pathlib import Path

import pandas as pd
from dictionaries import srs_col_type_dict  # type: ignore
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


def connect_to_database() -> Engine:
    """This function opens a connection to the database."""
    user = os.getenv("PGUSER")
    password = os.getenv("PGPASSWORD")
    host = os.getenv("PGHOST")
    port = os.getenv("PGPORT")
    dbname = os.getenv("PGDATABASE")
    # --- Create connection
    engine_database = create_engine(
        f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
    )
    return engine_database


def get_file_locations() -> dict:
    """This function loads in the file locations using the external_file_locations json."""
    output_dir = os.getenv("OUTPUT_PIPELINE_DIR")

    with open(f"{output_dir}/external_file_locations.json", "r") as json_file:
        locations = json.load(json_file)
        return locations


def get_available_years() -> list:
    """Get the years we have files for using the external_file_locations."""
    output_dir = os.getenv("OUTPUT_PIPELINE_DIR")

    with open(f"{output_dir}/external_file_locations.json", "r") as json_file:
        locations = json.load(json_file)
        return list(locations.keys())


def get_data_frame(source: str, year: int) -> pd.DataFrame:
    """A helper function to read the necessary file into a pandas dataframe."""
    external_path = os.getenv("EXTERNAL_FILE_PATH")
    remote_files = get_file_locations()
    fl = remote_files[year][source]
    # need this for mypy
    assert fl is not None
    assert external_path is not None

    if source == "srs":
        columns = srs_col_type_dict.keys()
        dtype = srs_col_type_dict
    else:
        columns = None
        dtype = None

    if fl.endswith("csv"):
        return pd.read_csv(Path(external_path) / fl, usecols=columns, dtype=dtype)
    else:
        return pd.read_excel(Path(external_path) / fl, usecols=columns, dtype=dtype)


def get_elegible_agency_list(reta_frame: pd.DataFrame) -> list:
    """This function subsets the universe frame by agencies that are eligible."""
    reta_frame = reta_frame.rename(
        columns={col: col.upper() for col in reta_frame.columns}
    )
    # AGENCY_STATUS is “Active”,
    active_fr = reta_frame.loc[reta_frame["AGENCY_STATUS"].isin(["Active"])]
    # COVERED_FLAG and DORMANT_FLAG are set to “N”,
    uncovered_fr = active_fr.loc[active_fr["COVERED_FLAG"] == "N"]
    nondormant_fr = uncovered_fr.loc[uncovered_fr["DORMANT_FLAG"] == "N"]
    return list(nondormant_fr["ORI"].unique())
