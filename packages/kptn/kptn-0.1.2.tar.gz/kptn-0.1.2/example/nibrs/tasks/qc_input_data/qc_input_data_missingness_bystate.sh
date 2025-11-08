#!/bin/bash
set -e
jupyter nbconvert --ExecutePreprocessor.timeout=-1 --execute --to html --no-input "Part 6 - Missing Variables-One State.ipynb"
mv "Part 6 - Missing Variables-One State.html" ${OUTPUT_PIPELINE_DIR}/"QC_output_files"/"Part 6 - Missing Variables-${INPUT_STATE}.html"
