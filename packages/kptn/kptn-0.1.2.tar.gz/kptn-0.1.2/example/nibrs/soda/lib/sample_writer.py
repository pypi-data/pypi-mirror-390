import csv
import json
import os
from datetime import date, datetime

from .util import output_dir


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code."""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


def get_file_name(table_name, filename, extension):
    # Create a directory $table_name in the output directory
    table_dir = os.path.join(output_dir, table_name)
    if not os.path.exists(table_dir):
        os.mkdir(table_dir)

    # Create a file $table_name/$col_name.$extension
    col_file = os.path.join(table_dir, f"{filename}.{extension}")
    return col_file


def write_samples_json(row_dicts, data_file):
    with open(data_file, "w") as f:
        json.dump(row_dicts, f, indent=2, default=json_serial)


def write_samples_csv(row_dicts, data_file):
    with open(data_file, "w") as f:
        writer = csv.DictWriter(f, fieldnames=row_dicts[0].keys())
        writer.writeheader()
        writer.writerows(row_dicts)


def write_samples(table_name, col_name, row_dicts, extension="json", all_cols=False):
    if extension == "json":
        # Write all columns to a file
        if all_cols:
            all_cols_file = get_file_name(table_name, f"{col_name}_all_cols", "json")
            write_samples_json(row_dicts, all_cols_file)

        # Write the 1 problem column to a file
        one_col_file = get_file_name(table_name, col_name, "json")
        row_dicts = list(
            map(lambda row_dict: {col_name: row_dict[col_name]}, row_dicts)
        )
        write_samples_json(row_dicts, one_col_file)

    elif extension == "csv":
        # Write all columns to a file
        if all_cols:
            all_cols_file = get_file_name(table_name, f"{col_name}_all_cols", "csv")
            write_samples_csv(row_dicts, all_cols_file)

        # Write the 1 problem column to a file
        row_dicts = list(
            map(lambda row_dict: {col_name: row_dict[col_name]}, row_dicts)
        )
        one_col_file = get_file_name(table_name, col_name, "csv")
        write_samples_csv(row_dicts, one_col_file)
