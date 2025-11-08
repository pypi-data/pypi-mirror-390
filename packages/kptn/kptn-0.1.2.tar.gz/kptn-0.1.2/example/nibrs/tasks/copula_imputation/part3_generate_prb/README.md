# NIBRS Estimation Pipeline

## Running generate PRB scripts outside of Docker

The environment variables from the main README should be set and the working directory should be set to: `./nibrs-estimation-pipeline/tasks/copula_imputation/part3_generate_prb`

### Template

Takes no additional environment variables, just run `01_Create_Template_Indicator_Tabel_Rel_Bias.R`.

### Generate PRB and Generate PRB part 2

These scripts require 2 additional environment variables. Each variable is described below:

 - `TABLE_NAME`: Expected values are 1a - 1c, 2a - 2c, 3a - 3c, 4a - 4b, LEOKA, DM1 - DM10, 5a - 5b, GV1a, GV2a, YT1, YT2, 
                 3aclear, 3aunclear, 3bclear, & 3bunclear
 - `DER_CURRENT_PERMUTATION_NUM`: The geographic or demographic permutation, see `POP_TOTALS_PERM_XXXX.csv` for a full list

The example below uses all of the arguments to run DM6 in it's entirety for the national permutation.

```
source('../../logging.R')

Sys.setenv(TABLE_NAME = "DM6",
           DER_CURRENT_PERMUTATION_NUM = 1)

source('02_Generate_PRB_Copula.R')
source('03_Generate_PRB_Copula_2.R')
```