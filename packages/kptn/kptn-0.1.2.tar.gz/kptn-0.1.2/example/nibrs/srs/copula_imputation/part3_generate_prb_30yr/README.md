# SRS Estimation Pipeline

## Running generate PRB scripts outside of Docker

The environment variables from the main README should be set and the working directory should be set to: `./nibrs-estimation-pipeline/srs/copula_imputation/part3_generate_prb`

### Template

Takes no additional environment variables, just run `01_Create_Template_Indicator_Tabel_Rel_Bias.R`. This is going to create quite a few files, so just be aware.

### Generate PRB and Generate PRB part 2

These scripts require 2 additional environment variables. Each variable is described below:

 - `TABLE_NAME`: SRS1a, SRS2a
 - `DER_CURRENT_PERMUTATION_NUM`: The geographic permutation, see `POP_TOTALS_PERM_XXXX_SRS.csv` for a full list

The example below uses all of the arguments to run SRS1a for the national permutation.

```
source('../../logging.R')

Sys.setenv(TABLE_NAME = "SRS1a",
           DER_CURRENT_PERMUTATION_NUM = 1)

source('02_Generate_PRB_Copula.R')
source('03_Generate_PRB_Copula_2.R')
```