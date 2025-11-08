# SRS Estimation Pipeline

## Running SRS conversion scripts outside of Docker

The environment variables from the main README should be set and the working directory should be set to `./nibrs-estimation-pipeline/srs/conversion`

### Create Extracts and Implement SRS

The first two parts of the SRS conversion task requires one addition environment variable, `INPUT_STATE`.

To run a single state, you'd add the following line to your environment script:

`INPUT_STATE = "AL"`

and then after setting the appropriate working directory run `1001_Run_SRS_byState.R`.

To run all or a subset of the states, you'd run code similar to the following:

```
source(here::here("tasks/logging.R"))

con <- dbConnect(RPostgres::Postgres())

query2 <- paste0("
 SELECT
  ref_state.abbr AS state_abbr,
  ref_agency_status.agency_status,
  CASE
      WHEN ref_agency_yearly.is_covered IS TRUE THEN 'Y'::text
      WHEN ref_agency_yearly.is_covered IS FALSE THEN 'N'::text
      ELSE ' '::text
  END AS covered_flag,
  CASE
      WHEN ref_agency_yearly.agency_status = 'D'::bpchar THEN 'Y'::text
      ELSE 'N'::text
  END AS dormant_flag,
  ref_agency_type.name AS agency_type_name
 FROM ucr_prd.ref_agency_yearly ref_agency_yearly
	  LEFT JOIN ucr_prd.ref_agency ref_agency USING (agency_id)
	  LEFT JOIN ucr_prd.ref_state USING (state_id)
	  LEFT JOIN ucr_prd.ref_agency_status ref_agency_status USING (agency_id, data_year)
	  LEFT JOIN ucr_prd.ref_agency_type USING (agency_type_id)
 WHERE ref_agency_status.data_year = ",year," AND
       ref_agency_yearly.is_nibrs IS TRUE")
  

states_df <- time_query(con,query2) %>% 
  filter(agency_status == "A") %>%
  filter(covered_flag == "N") %>%
  filter(dormant_flag == "N") %>%
  filter(str_to_upper(agency_type_name) != "FEDERAL")

state_list <- as.list(unique(states_df['state_abbr']))

final_list <- state_list[1]$state_abbr

for (st in final_list) {
    Sys.setenv(INPUT_STATE = st)

    source("1001_Run_SRS_byState.R")
}
```

### Combine and Finalize the SRS Conversion

No additional environment variables are needed to run the second part of the SRS Conversion. Simply set the working directory to `./nibrs_estimation_pipeline/srs/conversion` and run `1002_Run_SRS_Block_Combine.R`.