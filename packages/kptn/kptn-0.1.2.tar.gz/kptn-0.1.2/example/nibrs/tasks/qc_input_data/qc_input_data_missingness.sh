#!/bin/bash
set -e
jupyter nbconvert --ExecutePreprocessor.timeout=-1 --execute --to html --no-input "Part 6 - Missing Variables.ipynb"
mv *.html ${OUTPUT_PIPELINE_DIR}/"QC_output_files"/
