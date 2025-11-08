#!/bin/bash
set -e
jupyter nbconvert --ExecutePreprocessor.timeout=-1 --execute --to html --no-input "Part 1 - High Level State Checks.ipynb"
jupyter nbconvert --ExecutePreprocessor.timeout=-1 --execute --to html --no-input "Part 2 - Coverage by State.ipynb"
jupyter nbconvert --ExecutePreprocessor.timeout=-1 --execute --to html --no-input "Part 3 - Agency Coverage by NIBRS Start Year.ipynb"
jupyter nbconvert --ExecutePreprocessor.timeout=-1 --execute --to html --no-input "Part 4 - NIBRS vs SRS.ipynb"

mv *.html ${OUTPUT_PIPELINE_DIR}/"QC_output_files"/
