# NIBRS - SRS Estimation Pipeline

## Running BJS Grant SRS conversion scripts outside of Docker

The environment variables from the main README should be set and the working directory should be set to `./nibrs-estimation-pipeline/srs/bjs_grant/conversion`

### Create Extracts and Implement SRS

The first two parts of the BJS Grant SRS conversion task requires one additional environment variable, `INPUT_STATE`.

To run a single state, you'd add the following line to your environment script:

`INPUT_STATE = "AL"`

and then after setting the appropriate working directory run `1001_Run_SRS_byState_Parial.R`.

To run all or a subset of the states for a single year, you'd run code similar to the following:

```
source("../../../logging.R")

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

    source("1001_Run_SRS_byState_Partial.R")
}
```