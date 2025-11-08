# Data Quality

This directory allow us to verify the data in the database is what we think it is:

- Expected column names
- Expected column types
- Expected column values for columns that have a limited set of values (200 or under)

Checks are written in [SodaCL](https://docs.soda.io/soda-cl/soda-cl-overview.html), human-readable YAML that the library `soda` can parse and run test cases from.

## Running

Pre-req: a `.env` file in project root with database credentials

### with Docker

```bash
./bin/run-docker.sh [all|schema|sodacl_file]
```

```bash
Usage: python soda_nibrs_scan.py [all|schema|sodacl_file]

# Example: Use all the checks in the soda/checks directory
  python soda_nibrs_scan.py all

# Example: Use all the checks in the soda/checks/ucr_prd directory
  python soda_nibrs_scan.py ucr_prd

# Example: Specify a checks file to use
  python soda_nibrs_scan.py checks/ucr_prd/ref_agency.yml
```

### with Python

If using a virtualenv, `pip install soda-core-postgres python-dotenv "typer[all]"`, then

```bash
python soda_nibrs_scan.py [all|schema|sodacl_file]
```

## Understanding Results

Soda compares the baseline data in the `checks` directory with the data in the database. If there are differences, it will report them in the terminal. To get a better understanding of the results, you can view the data causing check failures in the `output` directory.

Current baselines are based on `ucr-prd-stats-2022` db.

## Addendum A: soda-core API override

Note: Soda's CLI cannot be used at this time because it queries `information_schema.columns` to determine column types. Instead, we use Soda as a Python package and override the query for columns to use `pg_attributes`, which is where Postgres stores info for materialized views.

## Addendum B: Programmatically generating check files

Pre-req: `psycopg`

NOTE: Checks are already created and should be manually edited for updates. If you need to programmatically regenerate the checks, read on.

Edit the table list in the `analyze_db.py` script and run to generate or update a table's check file

```bash
python soda/analyze_db.py
```

NOTE: There's a bug where array values in the outputed check file that have a single quote. When Soda reads this, it errors. The band-aid fix is to manually edit the check file, replacing `"` with `'`, and replacing `'` with `''''`. For example: `['A', 'B', "Cat's"]` should be edited to `['A', 'B', 'Cat''''s']`. Four single quotes are used to escape two times: once in YAML and once in SQL.
