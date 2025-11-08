# NIBRS Estimation Pipeline

## Running copula imputation part 2 scripts outside of Docker

The environment variables from the main README should be set and the working directory should be set to `./nibrs-estimation-pipeline/tasks/copula_imputation/part2_impute`

### Part 2 Impute

The copula imputation part 2 impute scripts require 4 additional environment variables and an argument variable. Each variable is described below:

 - `TABLE_NAME`: 1a - 1c, 2a - 2c, 3a - 3c, 4a - 4b, LEOKA, DM1 - DM10, 5a - 5b, GV1a, GV2a, YT1, YT2, 
                 3aclear, 3aunclear, 3bclear, & 3bunclear
 - `DER_CURRENT_PERMUTATION_NUM`: The national or demographic national permutation: 1, 1001, 2001, etc.
 - `COLUMN_INDEX`: For DM6-9, these are 1-9. For all other tables this is 1.
 - `STRAT_VAR`: For all tables this is 1-8.
 - `subset`: These are "popResidAgcyCounty_cbi>0 & nDemoMissing==0", "popResidAgcyCounty_cbi>0 & nDemoMissing>0", and "popResidAgcyCounty_cbi==0"

The example below uses all of the arguments to run DM6 in it's entirety for the national permutation.

```
source('../../logging.R')

Sys.setenv(TABLE_NAME = "DM6",
           DER_CURRENT_PERMUTATION_NUM = 1)

column_index <- c(1:9)
strat <- c(1:8)

subsets <- c(
  "popResidAgcyCounty_cbi>0 & nDemoMissing==0",
  "popResidAgcyCounty_cbi>0 & nDemoMissing>0",
  "popResidAgcyCounty_cbi==0"
)

copula_parts <- c(
    "100_Run_Copula_Imputation_Step1.R",
    "100_Run_Copula_Imputation_Step2_Alt.R",
    "100_Run_Copula_Imputation_Step3_Alt.R",
    "100_Run_Copula_Imputation_Step4.R"
)

for (c in column_index) {
    Sys.setenv(COLUMN_INDEX = c)
    for (st in strat) {
        Sys.setenv(STRAT_VAR = st)
        for (s in subsets) {
            for (p in copula_parts) {
                system(paste0("Rscript ", p," '", s,"'"))
            }
        }       
    }
}
```

### Part 2 Stack

The copula imputation part 2 stack scripts require 2 additional environment variables. Each variable is described below:

 - `TABLE_NAME`: Expected values are 1a - 1c, 2a - 2c, 3a - 3c, 4a - 4b, LEOKA, DM1 - DM10, 5a - 5b, GV1a, GV2a, YT1, YT2, 
                 3aclear, 3aunclear, 3bclear, & 3bunclear
 - `DER_CURRENT_PERMUTATION_NUM`: The national or demographic national permutation: 1, 1001, 2001, etc.

The example below uses all of the arguments to run DM6 in it's entirety for the national permutation.

```
source('../../logging.R')

Sys.setenv(TABLE_NAME = "DM6",
           DER_CURRENT_PERMUTATION_NUM = 1)

source('100_Run_Copula_Stack.R')
```