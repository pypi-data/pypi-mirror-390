
# Get .env variables to authenticate with Postgres
project_root="$( dirname "${BASH_SOURCE[0]}" )/../.."
source $project_root/.env

cd $project_root/soda

docker build -t soda-nibrs .

# Pass the command line arguments to the python script
docker run -it --rm \
  -e PGHOST=$PGHOST \
  -e PGPORT=$PGPORT \
  -e PGUSER=$PGUSER \
  -e PGPASSWORD=$PGPASSWORD \
  -e PGDATABASE=$PGDATABASE \
  --mount type=bind,source="$(pwd)"/output,target=/usr/src/app/output \
  soda-nibrs \
  python "./soda_nibrs_scan.py" $@

# To mount the checks directory if writing new checks:
# --mount type=bind,source="$(pwd)"/checks,target=/usr/src/app/checks \
