# SRS Estimation Pipeline

## Running copula data preparation script outside of Docker

The copula imputation part 1 data preparation script requires 1 additional environment variable. The expected options are below:

 - `TABLE_NAME`: SRS1a, SRS2a
 
The working directly also needs to be set to `./nibrs-estimation-pipeline/srs/copula_imputation/part1_prep_data`

The example below uses all of the arguments to run SRS1a.

```
source('../../logging.R')

Sys.setenv(TABLE_NAME = "SRS1a")


source("100_run_copula_part1_prep_data.R")

```
