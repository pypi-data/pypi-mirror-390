# NIBRS Estimation Pipeline

## Running single estimation scripts outside of Docker

The working directory should be set to the subfolder for the table of interest and the environment variables described in the main README should be set, for the purposes of the README we'll be describing Table 3a: `./nibrs-estimation-pipeline/tasks/generate_estimates/Single/09_Table3a`

All steps rely on one additional environment variable `DER_TABLE_NAME`. This is the value after the "Table" in the folder name for the table being run. Examples are `3a`, `LEOKA`, `3aunclear`, etc.

### Data prep

Takes no additional environment variables, just run `Part1_prepare_datasets.R`

### Generate est

Takes one additional argument variable, which is the column. The `collist` variable in the Part 1 program for each table contains the list of columns being referenced. The script takes a number between 1 and the length of `collist`, indicating which item in the list to process. The following could be added to a script to run 3a in it's entirety:

```
source(here::here("tasks/logging.R"))

columns <- as.list(1:17)

for (c in columns) {
    # NOTE: the working directory should still be within the 09_Table3a folder, as the generate_estimates.R file relies on the Table-specific files.
    system(paste0("Rscript ../../Tables_Shared_Scripts/generate_estimates.R", c))
}
```

### Additional columns (demographic tables only)

Takes one additional argument variable, which is the demographic series. The create_additional_columns.R file has the available values of series. The following could be added to a script to run 3a in it's entirety:

```
source(here::here("tasks/logging.R"))

series <- seq(1000,20000,1000)

for (s in series) {
    # NOTE: the working directory should still be within the 09_Table3a folder, as the create_additional_columns.R file relies on the Table-specific files.
    system(paste0("Rscript ../../Tables_Shared_Scripts/create_additional_columns.R ", s))
}
```

### Finalize

Takes no additional environment variables, just run `Part3_finalize.R`

### Parts B & C

Applies only to 2a and 2b, takes no additional environment variables just run the script.