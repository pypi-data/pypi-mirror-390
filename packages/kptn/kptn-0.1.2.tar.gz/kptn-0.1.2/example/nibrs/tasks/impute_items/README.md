# NIBRS Estimation Pipeline

## Running item imputation scripts outside of Docker

The item imputation scripts all rely on the same additional environment variable, `INPUT_STATE`, outside of the environment variables described in the main README, EXCEPT for the VOR property imputations (see below). The expected values for `INPUT_STATE` are dependent on which states are in the agency table for a given data year. The working directory is set to the sub-folder for the specific part of item imputation, i.e. `./nibrs-estimation-pipeline/tasks/impute_items/part2_person_victims`.

To run a single state through item imputation, you'd add the following line to your environment script:

`INPUT_STATE = "AL"`

and then after setting the appropriate working directory run the 100 run program in the folder.

To run all or a subset of the states through any part of item imputation, you'd run code similar to the following:

```
source(here::here("tasks/logging.R"))

con <- dbConnect(RPostgres::Postgres())

query2 <- paste0("
SELECT  state_abbr,
            agency_status,
            covered_flag,
            dormant_flag,
            agency_type_name
    FROM agencies agn
    where data_year=",year,"
")

states_df <- time_query(con,query2) %>% 
  filter(agency_status == "A") %>%
  filter(covered_flag == "N") %>%
  filter(dormant_flag == "N") %>%
  filter(str_to_upper(agency_type_name) != "FEDERAL")

state_list <- as.list(unique(states_df['state_abbr']))

final_list <- state_list[1]$state_abbr

for (st in final_list) {
    Sys.setenv(INPUT_STATE = st)

    source("100_Run_Logical_Edits.R")
}
```

## Running Hispanic Ethnicity item imputation script outside of Docker.

The Hispanic ethnicity item imputation script relies on the additional environment variable, `ETHNICITY_INPUT_NUM`, outside of the environment variables described in the main README. The expected values for `ETHNICITY_INPUT_NUM` are 1-3, which correspond to groups of states. The working directory is set to the sub-folder for Hispanic ethnicity imputation, `./nibrs-estimation-pipeline/tasks/impute_items/part3_5_ethnicity`. 

## Running VOR property item imputation script outside of Docker.

The VOR property item imputation script relies on the additional environment variable, `INPUT_NUM`, outside of the environment variables described in the main README. The expected values for `INPUT_NUM` are 1-12, which corresponds to groups of states or a single state. The working directory is set to the sub-folder for VOR imputation `./nibrs-estimation-pipeline/tasks/impute_items/part4_victim_offender`.


## Running Group B Arrestee item imputation scripts outside of Docker.

There are two Group B Arrestee scripts, part1 and part2. Part 1 runs by state, and therefore requires the environment variable `INPUT_STATE`. To run the part1 script for all states, follow the directions listed above to obtain a full list of states and run the script. Part 2 does not require any additional environment variables. The working directory is set to the sub-folder for Group B arrestee imputation `./nibrs-estimation-pipeline/tasks/impute_items/part5_groupb_arrestee`.