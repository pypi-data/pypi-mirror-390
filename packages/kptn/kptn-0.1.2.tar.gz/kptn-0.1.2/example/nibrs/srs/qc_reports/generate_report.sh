#!/bin/bash
set -e
jupyter nbconvert --ExecutePreprocessor.timeout=-1 --execute --to html --no-input "Report_SRS_Conversion_versus_DB.ipynb" --output="Report_SRS_Conversion_versus_DB_${INPUT_STATE}.html"
mv Report_SRS_Conversion_versus_DB_${INPUT_STATE}.html ${OUTPUT_PIPELINE_DIR}/srs/QC_output_files/Report_SRS_Conversion_versus_DB_${INPUT_STATE}.html