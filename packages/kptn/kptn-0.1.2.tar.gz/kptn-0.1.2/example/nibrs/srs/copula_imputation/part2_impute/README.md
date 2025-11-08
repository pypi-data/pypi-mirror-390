# SRS Estimation Pipeline

## Running copula imputation part 2 scripts outside of Docker

The environment variables from the main README should be set and the working directory should be set to `./nibrs-estimation-pipeline/srs/copula_imputation/part2_impute`

### Part 2 Impute

The copula imputation part 2 impute script requires 2 additional environment variables and an argument variable. Each variable is described below:

 - `TABLE_NAME`: SRS1a, SRS2a
 - `STRAT_VAR`: For all tables this is 1-8.
 - `subset`: These are "popResidAgcyCounty_cbi>0 & nDemoMissing==0", "popResidAgcyCounty_cbi>0 & nDemoMissing>0", and "popResidAgcyCounty_cbi==0"

The example below uses all of the arguments to run SRS1a.

```
source('../../logging.R')

Sys.setenv(TABLE_NAME = "SRS1a")

strat <- c(1:8)

subsets <- c(
  "popResidAgcyCounty_cbi>0 & nDemoMissing==0",
  "popResidAgcyCounty_cbi>0 & nDemoMissing>0",
  "popResidAgcyCounty_cbi==0"
)

for (st in strat) {
    Sys.setenv(STRAT_VAR = st)
    for (s in subsets) {
        system(paste0("Rscript 100_Run_Copula_Stack.R '", s,"'"))
            
    }       
}

```

### Part 2 Stack

The copula imputation part 2 stack script requires 1 additional environment variable described below:

 - `TABLE_NAME`: SRS1a, SRS2a

The example below uses all of the arguments to run SRS1a.

```
source('../../logging.R')

Sys.setenv(TABLE_NAME = "SRS1a")

source('100_Run_Copula_Stack.R')
```