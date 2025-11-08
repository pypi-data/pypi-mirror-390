# SRS Estimation Pipeline

## Running weighting scripts outside of Docker

No additional environment variables are needed to run the weighting scripts outside of Docker. Once the environment variables from the main README have been defined and the working directory is set to `./nibrs-estimation-pipeline/srs/compute_weights`, all that is required is running `00_Weights_Creation_Master_SRS.R` or `Add_on_Calibration_Variables_SRS.R`.

**NOTE**: If you want to work on only part of the weighting task the beginning of `01_Create_Clean_Frame_SRS.R` still needs to be run because it sets up the data folders and the data year.
