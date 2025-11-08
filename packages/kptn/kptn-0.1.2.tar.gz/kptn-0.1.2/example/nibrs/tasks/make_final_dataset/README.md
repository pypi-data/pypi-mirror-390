# NIBRS Estimation Pipeline

## Running suppression scripts outside of Docker

### Momentum

The suppression script for calculating the momentum rule requires three additional environment variables, `PERMUTATION_NAME`, `TOP_FOLDER`, and `MID_FOLDER`, outside of the environment variables set in the main README. The working directly also needs to be set to `./nibrs-estimation-pipeline/tasks/make_final_dataset`. The expected values are described below:

- `PERMUTATION_NAME`: 1-709
- `TOP_FOLDER`: National, Region, State, Tribal, University, MSA, JD, & FO
- `MID_FOLDER`: State_Alabama, Regional_Midwest_Size_Non_MSA_Counties. This the the `POPULATION_DESCRIPTION` from `POP_TOTALS_{year}.csv` where all blank space, commas, and dashes(-) are replaced with an underscore.

The example below runs the momentum run for the State of Alabama:

```
source('../../logging.R')

Sys.setenv(PERMUTATION_NAME = 56,
           TOP_FOLDER = "State",
           MID_FOLDER = "State_Alabama")

source('1000_Make_Momentum_Rule.R')
```

### Suppression

The suppression script the same additional environment variables as the momentum rule PLUS `TABLE_NAME`, outside of the environment variables set in the main README. The working directly also needs to be set to `./nibrs-estimation-pipeline/tasks/make_final_dataset`. The expected values are described below:

To run a single permutation through the make final dataset script, you'd add the following line to your environment script:
The final database script requires one additional environment variable, `PERMUTATION_NAME`, outside of the environment variables set in the main README. The expected values for `PERMUTATION_NAME` are 1-108. The working directly also needs to be set to `./nibrs-estimation-pipeline/tasks/make_final_dataset`

- `PERMUTATION_NAME`: 1-709
- `TOP_FOLDER`: National, Region, State, Tribal, University, MSA, JD, & FO
- `MID_FOLDER`: State_Alabama, Regional_Midwest_Size_Non_MSA_Counties. This the the `POPULATION_DESCRIPTION` from `POP_TOTALS_{year}.csv` where all blank space, commas, and dashes(-) are replaced with an underscore.
- `TABLE_NAME`: 1a - 1c, 2a - 2c, 3a - 3c, 4a - 4b, LEOKA, DM1 - DM10, 5a - 5b, GV1a, GV2a, YT1, YT2, 3aclear, 3aunclear, 3bclear, & 3bunclear

The example below runs the suppression for the State of Alabama Table 1a:

```
source('../../logging.R')

Sys.setenv(PERMUTATION_NAME = 56,
           TOP_FOLDER = "State",
           MID_FOLDER = "State_Alabama",
           TABLE_NAME = "1a")

source('10001_Make_Final_Database.R')
```
