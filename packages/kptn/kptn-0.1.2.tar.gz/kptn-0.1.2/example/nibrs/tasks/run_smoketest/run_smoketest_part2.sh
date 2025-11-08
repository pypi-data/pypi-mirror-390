#!/bin/bash
set -e
jupyter nbconvert \
    --ExecutePreprocessor.timeout=-1 \
    --execute \
    --to html \
    --no-input \
    --output-dir "${OUTPUT_PIPELINE_DIR}/smoketest" \
    --output report \
    run_smoketest_part2.ipynb
