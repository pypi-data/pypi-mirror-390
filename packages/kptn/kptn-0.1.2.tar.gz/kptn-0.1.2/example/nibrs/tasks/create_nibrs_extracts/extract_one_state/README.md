# NIBRS Estimation Pipeline

## Running extract one state scripts outside of Docker

The extract one state script relies on the additional environment variable, `INPUT_STATE`, outside of those described in the main README. The expected values for `INPUT_STATE` are dependent on which states are in the agency table for a given data year. The working directory is set to the sub-folder for the extract one state task, i.e. `./nibrs-estimation-pipeline/tasks/create_nibrs_extracts/extract_one_state`.

To run a single state through extract one state, you'd add the following line to your environment script:

`INPUT_STATE = "AL"`

and then after setting the appropriate working directory run `100-Run_Program.R`.

To run all or a subset of the states through any part of extract one state, you'd run code similar to the following:

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

    source("100-Run_Program.R")
}
```
