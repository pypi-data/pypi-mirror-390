import os
import shutil
import sys

import typer
from dotenv import load_dotenv
from lib.custom_sampler import CustomSampler
from lib.sql_columns_override import sql_get_table_columns
from lib.util import output_dir, parse_out_schema_name, soda_dir
from typing_extensions import Annotated

from soda.execution.data_source import DataSource
from soda.scan import Scan

# Fix soda's column query
DataSource.sql_get_table_columns = sql_get_table_columns
app = typer.Typer()

# Load .env file one directory up relative to this Python file
load_dotenv(os.path.join(soda_dir, "..", ".env"))


def create_scan(schema_name, sample_format, all_cols):
    scan = Scan()
    scan.sampler = CustomSampler(sample_format, all_cols)
    scan.set_scan_definition_name("test_scan")
    # scan.add_configuration_yaml_file("./configuration.yml")

    scan.add_configuration_yaml_str(
        f"""
    data_source nibrs:
      type: postgres
      schema: {schema_name}
      connection:
        host: {os.getenv("PGHOST")}
        port: {os.getenv("PGPORT")}
        username: {os.getenv("PGUSER")}
        password: {os.getenv("PGPASSWORD")}
        database: {os.getenv("PGDATABASE")}
    """
    )
    scan.set_data_source_name("nibrs")
    return scan


def execute(scan):
    scan.execute()
    print(scan.get_logs_text())


def main(
    checks: Annotated[
        str,
        typer.Argument(
            help='Either "all", a subdirectory of checks/, or a soda_cl file like "checks/ucr_prd/ref_agency.yml"'
        ),
    ],
    sample_format: Annotated[
        str, typer.Option(help="The file format of the output samples")
    ] = "csv",
    all_cols: Annotated[
        bool, typer.Option(help="Whether to output all columns for the samples")
    ] = False,
    schema_name: Annotated[str, typer.Option(help="The database schema to use")] = "",
    auto_clean: Annotated[
        bool, typer.Option(help="Whether to delete output before each run")
    ] = False,
):
    """Run a soda scan on the NIBRS database."""
    if auto_clean:
        # Delete any directories in output_dir
        for filename in os.listdir(output_dir):
            file_path = os.path.join(output_dir, filename)
            try:
                if os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(e)

    checks_dir = os.path.join(soda_dir, "checks")
    schema_names = os.listdir(checks_dir)

    if checks == "all":
        for schema_name in schema_names:
            scan = create_scan(schema_name, sample_format, all_cols)
            scan.add_sodacl_yaml_files(os.path.join(checks_dir, schema_name))
            execute(scan)
    elif checks in schema_names:
        scan = create_scan(checks, sample_format, all_cols)
        scan.add_sodacl_yaml_files(os.path.join(checks_dir, checks))
        execute(scan)
    else:
        # Verify the checks file exists
        if not os.path.exists(os.path.join(soda_dir, checks)):
            print(f"ERROR: File {checks} does not exist")
            sys.exit(1)
        # If schema_name is not set as an arg, try to parse it from the supplied checks filepath
        if schema_name == "":
            schema_name = parse_out_schema_name(checks)
            if schema_name not in schema_names:
                print(
                    f"ERROR: Schema name must be set to one of {schema_names} or be passed as an argument"
                )
                sys.exit(1)
        # Use a single checks file
        scan = create_scan(schema_name, sample_format, all_cols)
        scan.add_sodacl_yaml_file(os.path.join(soda_dir, checks))
        execute(scan)


if __name__ == "__main__":
    typer.run(main)
