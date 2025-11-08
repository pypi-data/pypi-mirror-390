#!/bin/bash

PREFECT_API_DATABASE_CONNECTION_URL="postgresql+asyncpg://${PREFECT_DB_USER}:${PREFECT_DB_PASS}@${PREFECT_DB_HOST}:${PREFECT_DB_PORT}/${PREFECT_DB_DBNAME}"

export PREFECT_API_DATABASE_CONNECTION_URL

python /opt/prefect/update-template.py
bash /opt/prefect/apply-work-pool.sh
PREFECT_API_URL="http://${AWS_EC2_EIP}/api" prefect server start --host 0.0.0.0