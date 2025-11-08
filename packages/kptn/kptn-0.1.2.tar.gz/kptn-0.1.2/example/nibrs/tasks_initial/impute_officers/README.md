# NIBRS/SRS Estimation Pipeline

## Running officer imputation scripts outside of Docker

### Part 1 - Officer imputation

No additional environment variables are needed to run the officer imputation script outside of Docker. Once the environment variables from the main README have been defined and the working directory is set to `./nibrs-estimation-pipeline/tasks_initial/impute_officers`, all that is required is running `100_Run_01_Impute_Officers.R`.

### Part 2 - Update universe

No additional environment variables are needed to run the universe update script outside of Docker. Once the environment variables from the main README have been defined and the working directory is set to `./nibrs-estimation-pipeline/tasks_initial/impute_officers`, all that is required is running `02_Update_Universe.R`.

### Part 3 - Update POP_TOTALS

No additional environment variables are needed to run the POP_TOTALS scripts outside of Docker. Once the environment variables from the main README have been defined and the working directory is set to `./nibrs-estimation-pipeline/tasks_initial/impute_officers`, all that is required is running `103_Update_POP_TOTALS_PERM_YEAA.R` OR `104_Update_POP_TOTALS_YEAR_SRS.R`.
