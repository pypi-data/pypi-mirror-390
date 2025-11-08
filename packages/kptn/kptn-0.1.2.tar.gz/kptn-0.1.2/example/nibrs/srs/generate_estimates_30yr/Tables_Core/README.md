# SRS Estimation Pipeline

## Running single estimation scripts outside of Docker

The working directory should be set to the subfolder for the table of interest and the environment variables described in the main README should be set, for the purposes of the README we'll be describing Table SRS1a: `./nibrs-estimation-pipeline/srs/generate_estimates/Tables_Core/01_TableSRS1a`

### Data prep

Takes no additional environment variables, just run `Part1_prepare_datasets.R`

### Generate est

Takes one additional argument variable, which is the column. The `collist` variable in the Part 1 program for each table contains the list of columns being referenced. The script takes a number between 1 and the length of `collist`, indicating which item in the list to process. The following could be added to a script to run SRS1a in it's entirety:

```
source("../../../logging.R")

columns <- as.list(1:9)

for (c in columns) {
    system(paste0("Rscript Part2_generate_est.R", c))
}
```

### Finalize

Takes no additional environment variables, just run `Part3_finalize.R`
