# SRS Estimation Pipeline

## Running setup merging scripts outside of Docker

The environment variables from the main README should be set and the working directory should be set to: `./nibrs-estimation-pipeline/srs/generate_estimates/Setup`

### Setup SRS

Takes no additional environment variables, just run `100_Create_Clean_SRS.R` & `100_Create_Raw_SRS.R`.

### Add weights

Takes no additional environment variables, just run `100_Run_Process_Weights_and_Permutation.R`