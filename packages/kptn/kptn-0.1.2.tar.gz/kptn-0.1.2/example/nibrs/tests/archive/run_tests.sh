#!/bin/bash
set -e
export PYTHONPATH=../nibrs-estimation-pipeline:$PYTHONPATH
Rscript tests/run_r_tests.R "SETUP" "all"
python tests/prepare_test_environment.py "$@"
Rscript tests/run_r_tests.R "TEST" "$@"

while test $# -gt 0; do
    #skip the first argument
    shift
    case "$1" in
        -d|--delete)
            shift
            echo "Deleting test_output_files and gold_standard_output_full folders"
            rm -r tests/test_output_files
            rm -r tests/gold_standard_output_full
            ;;
        "")
            shift
            ;;
        --full)
            echo "--full flag has been deprecated. See README for details."
            break
            ;;
        *)
            echo "Unknown argument $1"
            break
            ;;
    esac
done
