# NIBRS Estimation Pipeline

## Running setup merging scripts outside of Docker

The environment variables from the main README should be set and the working directory should be set to: `./nibrs-estimation-pipeline/tasks/generate_estimates/Setup_part2_merged`

### Merge outputs

Takes no additional environment variables, just run `00a_Merge_Setup_Outputs_pt1.R` & `00a_Merge_Setup_Outputs_pt2.R`.

### Combine outputs with imputation

Takes one additional environment variable, `DATASET_TO_GENERATE`. The potential values of `DATASET_TO_GENERATE` are "VICTIM", "OFFENDER", "OFFENDERYOUTHTABLE", and "ARRESTEE".

To run all you'd need a script similar to the following:
```
source('../../logging.R')

dset_list <- c("VICTIM", "OFFENDER", "ARRESTEE", "OFFENDERYOUTHTABLE")

for (d in dset_list) {
    Sys.setenv(DATASET_TO_GENERATE = d)

    source("100_Run_00b_Create_Datasets.R")
}
```

### Add weights

Takes no additional environment variables, just run `100_Run_Process_Weights_and_Permutation.R`

### Clean main

Takes an argument variable with the potential values "incident", "offenses", "arrestee", "LEOKA", "arrest_code", and "group_b_arrestee".

To run all you'd need a script similar to the following:
```
source('../../logging.R')

dset_list <- c("incident", "offenses", "arrestee", "LEOKA", "arrest_code", "group_b_arrestee")

for (d in dset_list) {
    system(paste0("Rscript clean_main.R ", d))
    system(paste0("Rscript clean_main_2.R ", d))
}

```

### MSA indicator

Takes no additional environment variables, just run `101_Run_Setup_Agency_ORI.R`

### Firearms

Takes no additional environment variables, just run `00c_Create_Firearm_Datasets.R`