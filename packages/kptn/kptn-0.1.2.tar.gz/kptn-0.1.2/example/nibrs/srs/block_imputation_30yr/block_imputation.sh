#!/bin/bash
set -e
Rscript 100_Run_00_Raw_SRS_Using_NIBRS.R
Rscript 100_Run_SRS_Block_Imputation.R