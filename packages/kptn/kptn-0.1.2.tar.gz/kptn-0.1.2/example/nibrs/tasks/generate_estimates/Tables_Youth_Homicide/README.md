# NIBRS Estimation Pipeline

## Running single estimation YT scripts outside of Docker

The working directory should be set to the subfolder for the table of interest and the environment variables described in the main README should be set, for the purposes of the README we'll be describing Table YT1: `./nibrs-estimation-pipeline/tasks/generate_estimates/Single_Youth_Homicide/36_TableYT1`

All steps rely on one additional environment variable `DER_TABLE_NAME`. This is the value after the "Table" in the folder name for the table being run. Valid options are `YT1` and `YT2`.

### Data prep

Takes no additional environment variables, just run `Part1_prepare_datasets.R`

### Generate est

Takes one additional argument variable, which is the column. The `collist` variable in the Part 1 program for each table contains the list of columns being referenced. The script takes a number between 1 and the length of `collist`, indicating which item in the list to process. The following could be added to a script to run YT1 in it's entirety:

```
source(here::here("tasks/logging.R"))

columns <- c(1:2)

for (c in columns) {
    # NOTE: the working directory should still be within the 36_TableYT1 folder, as the generate_estimates.R file relies on the Table-specific files.
    system(paste0("Rscript ../../Tables_Shared_Scripts/generate_estimates.R", c))
}
```


### Finalize

Takes no additional environment variables, just run `Part3_finalize.R`

