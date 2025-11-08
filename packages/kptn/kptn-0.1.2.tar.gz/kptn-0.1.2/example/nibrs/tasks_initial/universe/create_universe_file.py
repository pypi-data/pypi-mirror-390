import os
from pathlib import Path

import pandas as pd
import psycopg2

if __name__ == "__main__":
    external_path = Path(str(os.getenv("EXTERNAL_FILE_PATH")))
    year = os.getenv("DATA_YEAR")
    output_dir = Path(str(os.getenv("OUTPUT_PIPELINE_DIR"))) / "initial_tasks_output"
    output_dir.mkdir(exist_ok=True)

    conn = psycopg2.connect(
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

    # Define your SQL query
    sql_query = f"set schema 'ucr_prd'; SELECT * FROM rpt_rti_universe_file({year})"

    # Execute the query and fetch the data into a pandas DataFrame
    df = pd.read_sql_query(sql_query, conn)
    df.columns = df.columns.str.upper()
    # Save the DataFrame to a CSV file
    df.to_csv(output_dir / f"orig_ref_agency_{year}.csv", index=False)
