# NIBRS Estimation Pipeline

## Running weighting scripts outside of Docker

No additional environment variables are needed to run the weighting scripts outside of Docker. Once the environment variables from the main README have been defined and the working directory is set to `./nibrs-estimation-pipeline/tasks/compute_weights`, all that is required is running `00a_Weights_Creation_Main_subSt.R` or `Add_on_Calibration_Variables.R`.

**NOTE**: If you want to work on only part of the weighting task the beginning of `01_Create_Clean_Frame.R` still needs to be run because it sets up the data folders and the data year.
