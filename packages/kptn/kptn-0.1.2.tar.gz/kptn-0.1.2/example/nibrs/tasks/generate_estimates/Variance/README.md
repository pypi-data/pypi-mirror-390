# NIBRS Estimation Pipeline

## Running variance estimation (permutation) scripts outside of Docker

The variance estimation scripts require 2 additional environment variables outside of those described in the main README. 

 - `TABLE_PROGRAM`: Expected values are the full names of the programs found in the `Variance` folder.
 - `DER_CURRENT_PERMUTATION_NUM`: The geographic or demographic permutation, see `POP_TOTALS_PERM_XXXX.csv` for a full list

The working directory should be set to `./nibrs-estimation-pipeline/tasks/generate_estimates/Variance`.

The example below uses all of the arguments to run DM6 in it's entirety for the national permutation.

```
source('../../logging.R')

Sys.setenv(DER_CURRENT_PERMUTATION_NUM = 1,
           TABLE_PROGRAM = "122_TableDM6_Variance.R")

source('100_Run_Table_Programs.R')
```