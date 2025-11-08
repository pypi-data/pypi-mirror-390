# NIBRS Estimation Pipeline

## Running copula data preparation scripts outside of Docker

The copula imputation part 1 data preparation scripts require 2 additional environment variables. Each variable is described below:

 - `TABLE_NAME`: Expected values are 1a - 1c, 2a - 2c, 3a - 3c, 4a - 4b, LEOKA, DM1 - DM10, 5a - 5b, GV1a, GV2a, YT1, YT2, 
                 3aclear, 3aunclear, 3bclear, & 3bunclear
 - `DER_CURRENT_PERMUTATION_NUM`: The national or demographic national permutation: 1, 1001, 2001, etc.
 
The working directly also needs to be set to `./nibrs-estimation-pipeline/tasks/copula_imputation/part1_prep_data`

The example below uses all of the arguments to run DM6 in it's entirety for the national permutation.

```
source('../../logging.R')

Sys.setenv(TABLE_NAME = "DM6",
           DER_CURRENT_PERMUTATION_NUM = 1)

for (i in c(1:5)) {
    source(paste0("100_Run_Copula_Data_Prep_Step",i,".R"))
}
```
