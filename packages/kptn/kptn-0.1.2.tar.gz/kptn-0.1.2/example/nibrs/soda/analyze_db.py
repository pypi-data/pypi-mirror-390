import os
from decimal import Decimal

import psycopg
from dotenv import load_dotenv

# Path to this file's directory
soda_dir = os.path.dirname(os.path.realpath(__file__))

# Load .env file one directory up relative to this Python file
load_dotenv(os.path.join(soda_dir, "..", ".env"))

columns_excluded_from_value_scan = [
    "pub_agency_unit",
    "ori",
    "legacy_ori",
    "ncic_agency_name",
    "pub_agency_name",
    "city_id",
    "population",
    "campus_id",
    "tribe_id",
    "agency_id",
    "submitting_agency_id",
    "ucr_agency_name",
    "judicial_district_code",
    "county_id",
    "fips_code",
    "metro_div_id",
    "legacy_county_code",
    "legacy_msa_code",
    "incident_number",
    "arrest_number",
    "added_date",
    "metro_div_name",
    "msa_name",
    "county_name",
    "property_value",
    "est_drug_qty",
    "data_year",
]

# I comment out the tables that I don't want to analyze
tables_to_analyze = [
    # ucr_prd schema:
    # "sum_month_offense",
    "lkup_srs_offense",
    # "est_12mc_reta_counts",
    "ref_metro_division",
    # "supp_month_offense",
    "ref_agency",
    "ref_agency_yearly",
    "ref_state",
    "ref_county",
    "ref_agency_type",
    "ref_division",
    "nibrs_incident",
    "form_month",
    "nibrs_offender",
    "nibrs_offense",
    "nibrs_arrestee",
    "nibrs_arrestee_weapon",
    "lkup_nibrs_weapon",
    "lkup_nibrs_arrest_type",
    "nibrs_criminal_activity",
    "lkup_nibrs_criminal_activity",
    "nibrs_victim",
    "nibrs_victim_offense",
    "nibrs_victim_offender_relationship",
    "lkup_nibrs_offense",
    "nibrs_property",
    "nibrs_property_description",
    "lkup_nibrs_property_description",
    "lkup_nibrs_property_loss",
    "nibrs_suspected_drug",
    "lkup_nibrs_drug",
    "lkup_nibrs_cleared_exceptionally",
    "lkup_nibrs_relationship",
    "nibrs_bias_motivation",
    "lkup_bias",
    "nibrs_offense_weapon",
    "nibrs_victim_injury",
    "lkup_nibrs_injury",
    "lkup_nibrs_location",
    "lkup_nibrs_activity",
    "lkup_assignment",
    "nibrs_victim_circumstance",
]

MAX_NUM_VALUES_TO_SAVE = 200


def analyze_table(cur, table_name, table_schema, output_dir):
    print("\n" + ("-" * 48))
    print(
        f"Analyzing table: {table_name}, schema: {table_schema}, output_dir: {output_dir}"
    )
    schema_table_name = f"{table_schema}.{table_name}"
    cur.execute(
        "SELECT attname AS column_name, format_type(atttypid, atttypmod) AS data_type \n"
        "FROM   pg_attribute \n"
        f"WHERE  attrelid = '{schema_table_name}'::regclass \n"
        "AND NOT attisdropped \n"
        "AND attnum > 0 \n"
        "ORDER BY attnum;"
    )
    column_name_list = []
    column_type_list = []
    for column_name, column_type in cur.fetchall():
        if column_name not in column_name_list:
            column_name_list.append(column_name)
        if (column_name, column_type) not in column_type_list:
            column_type_list.append((column_name, column_type))

    filepath = os.path.join(soda_dir, output_dir, table_schema, f"{table_name}.yml")
    with open(filepath, "w") as f:
        f.write(f"checks for {table_name}:\n")
        f.write("- row_count > 0\n")
        f.write("- schema:\n")
        f.write("    fail:\n")
        f.write(f"      when required column missing: {column_name_list}\n")
        f.write("      when wrong column type:\n")
        for column_name, column_type in column_type_list:
            f.write(f"        {column_name}: {column_type}\n")

        f.write("\n")
        too_many_values = []
        for column_name, column_type in column_type_list:
            if (
                column_type == "date"
                or column_type == "timestamp without time zone"
                or column_type == "timestamp with time zone"
                or column_type == "bigint"
                or column_name in columns_excluded_from_value_scan
            ):
                print("Skipping column", column_name)
                continue

            query = f"SELECT DISTINCT {column_name} from {table_schema}.{table_name}"
            print(query)
            cur.execute(query)
            values = [v[0] for v in cur.fetchall()]
            if len(values) <= MAX_NUM_VALUES_TO_SAVE:
                # Sort
                sorted_vals = sorted(values, key=lambda x: (x is None, x))

                # If the last value is None, remove it
                if sorted_vals[-1] is None:
                    sorted_vals = sorted_vals[:-1]

                # If any values are Decimal, convert them to float
                if any(isinstance(v, Decimal) for v in sorted_vals):
                    sorted_vals = [float(v) for v in sorted_vals]

                if len(sorted_vals) == 0:
                    continue

                # Write
                f.write(f"- invalid_count({column_name}) = 0:\n")
                f.write(f"    valid values: {sorted_vals}\n")
            else:
                too_many_values.append((column_name, len(values), values[:10]))

    # Pretty print too_many_values
    if len(too_many_values) > 0:
        print(f"Columns with {MAX_NUM_VALUES_TO_SAVE}+ values for {table_name}:")
        for column_name, num_values, values in too_many_values:
            print(f"{column_name} has {num_values} values. First 10 values: {values}")


with psycopg.connect() as conn:
    with conn.cursor() as cur:
        for table_name in tables_to_analyze:
            analyze_table(cur, table_name, "ucr_prd", "checks")
