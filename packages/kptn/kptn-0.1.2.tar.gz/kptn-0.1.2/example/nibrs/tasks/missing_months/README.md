# NIBRS Estimation Pipeline

## Running missing months script outside of Docker

Missing months is the one task where `DATA_YEAR` should not be set once because the partial reporters task requires missing months files for all data years. The task is written to iterate over the 5 most recent years based on the `DATA_YEAR`. So once all other environment variables from the main README have been defined and the working directory is set to `./nibrs-estimation-pipeline/tasks/missing months` there are two options: running a single year or running all years.

To run a single year through missing months simply set the `DATA_YEAR` environment variables and run `100-Run_Program.R`.

For example if DATA_YEAR = 2023, you'd run a script similar to the following:

```
source(here::here("tasks/logging.R"))

year_list <- seq(2023-4, 2023)


for (year in year_list) {
    Sys.setenv(DATA_YEAR = year)

    source('100-Run_Program.R')
}
```
