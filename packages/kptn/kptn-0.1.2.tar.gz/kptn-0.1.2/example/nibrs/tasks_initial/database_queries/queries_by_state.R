library(tidyverse)
library(DBI)
library(DT)
library(lubridate)
library(data.table)

#Read in the common functions to be used in R
source(here::here("tasks/logging.R"))

#input/output directories for pipeline artifacts
outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")
inputPipelineDir <- Sys.getenv("INPUT_PIPELINE_DIR")
external_path <- Sys.getenv("EXTERNAL_FILE_PATH")

#output path for all the data extracts
queried_data_path = paste0(outputPipelineDir, "/initial_tasks_output/database_queries/")
if (! dir.exists(queried_data_path)) {
  dir.create(queried_data_path, recursive = TRUE)
}

#output path for data extracts previously created in generate_estimates/Setup_part1_bystate
der_bystate_file_path = paste0(outputPipelineDir, "/indicator_table_extracts_bystate/") #output path for all the data extracts
if (! dir.exists(der_bystate_file_path)) {
  dir.create(der_bystate_file_path, recursive = TRUE)
}

#output path for data needing to be saved in artifacts
artifacts_path <- paste0(outputPipelineDir,"/artifacts/")
if (! dir.exists(artifacts_path)) {
  dir.create(artifacts_path, recursive = TRUE)
}

CONST_YEAR <- Sys.getenv("DATA_YEAR")
INPUT_STATE <- Sys.getenv("INPUT_STATE")

con <- dbConnect(RPostgres::Postgres())

state_year_where <- paste0("EXTRACT(YEAR FROM incident_date) = ", CONST_YEAR," AND agencies.state_abbr = '", INPUT_STATE,"'")

### tasks/create_nibrs_extracts/extract_one_state/01_Extract_All.Rmd ####
query_victim_offense_month <- paste0("
 SELECT 
   EXTRACT(year FROM nibrs_incident.incident_date) AS data_year,
   nibrs_incident.incident_id,
   CASE
       WHEN nibrs_incident.is_cargo_theft IS TRUE THEN 'Y'::bpchar
       WHEN nibrs_incident.is_cargo_theft IS FALSE THEN 'N'::bpchar
       ELSE NULL::bpchar
   END AS cargo_theft_flag,
   nibrs_incident.incident_date,
   nibrs_incident.cleared_exceptionally_code AS cleared_except_code,
   agencies.ori AS ori,
   agencies.dormant_flag,
   agencies.agency_status,
   agencies.state_id,
   agencies.state_abbr,
   agencies.division_code,
   agencies.region_code,
   agencies.agency_type_name,
   agencies.population,
   agencies.suburban_area_flag,
   agencies.population_group_id,
   agencies.covered_flag,
   nibrs_victim.victim_id,
   nibrs_victim.sequence_number AS victim_seq_num,
   nibrs_victim.victim_type_code,
   nibrs_victim.age_code as age_code_victim,
   CASE
       WHEN nibrs_victim.age_code = ANY (ARRAY['NN'::bpchar, 'NB'::bpchar, 'BB'::bpchar, '00'::bpchar, 'NS'::bpchar, '99'::bpchar]) THEN NULL::bpchar
       ELSE nibrs_victim.age_code
   END AS age_num_victim,
   CASE
       WHEN nibrs_victim.sex_code = 'X'::bpchar THEN ' '::bpchar
       ELSE nibrs_victim.sex_code
   END AS sex_code_victim,
   CASE 
       WHEN nibrs_victim.race_code = '' THEN 'NA'
       ELSE nibrs_victim.race_code
   END AS race_code_victim,
   CASE
       WHEN nibrs_victim.ethnicity_code = 'X'::bpchar THEN ' '::bpchar
       ELSE nibrs_victim.ethnicity_code
   END AS ethnicity_code_victim,
   CASE
       WHEN nibrs_victim.resident_status_code = 'None'::bpchar THEN ' '::bpchar
       WHEN nibrs_victim.resident_status_code = '-1'::bpchar THEN ' '::bpchar
       WHEN nibrs_victim.resident_status_code IS NULL THEN ' '::bpchar
       ELSE nibrs_victim.resident_status_code
   END AS resident_status_code_victim,
   nibrs_victim_offense.offense_id,
   lkup_nibrs_offense.offense_code,
   CASE
       WHEN nibrs_offense.method_of_entry_code IS NULL THEN ' '::bpchar
       ELSE nibrs_offense.method_of_entry_code
   END AS method_entry_code,
   lkup_nibrs_offense.name AS offense_name,
   lkup_nibrs_offense.crime_against,
   lkup_nibrs_offense.category_name AS offense_category_name,
   form_month.data_month AS month_num
 FROM ucr_prd.nibrs_incident
	LEFT JOIN (
	  SELECT
	   ref_agency.ori,
	   ref_agency.agency_id,
	   ref_agency.legacy_ori,
	   ref_agency.nibrs_start_date,
	   ref_agency_type.name AS agency_type_name,
	   ref_agency_status.data_year,
	   ref_agency_status.agency_status,
	   ref_agency_yearly.is_nibrs,
	   ref_agency_yearly.population,
	   ref_agency_yearly.population_group_id,
	   ref_state.state_id,
     ref_state.name AS state_name,
     ref_state.abbr AS state_abbr,
     ref_state.postal_abbr AS state_postal_abbr,
     ref_division.code AS division_code,
     ref_region.code AS region_code,
     CASE
         WHEN ref_agency_yearly.is_suburban_area IS TRUE THEN 'Y'::text
         WHEN ref_agency_yearly.is_suburban_area IS FALSE THEN 'N'::text
         ELSE ' '::text
     END AS suburban_area_flag,
     CASE
         WHEN ref_agency_yearly.agency_status = 'D'::bpchar THEN 'Y'::text
         ELSE 'N'::text
     END AS dormant_flag,
     CASE
         WHEN ref_agency_yearly.is_covered IS TRUE THEN 'Y'::text
         WHEN ref_agency_yearly.is_covered IS FALSE THEN 'N'::text
         ELSE ' '::text
     END AS covered_flag
	  FROM ucr_prd.ref_agency_yearly ref_agency_yearly
	   LEFT JOIN ucr_prd.ref_agency ref_agency USING (agency_id)
	   LEFT JOIN ucr_prd.ref_state USING (state_id)
	   LEFT JOIN ucr_prd.ref_agency_status ref_agency_status USING (agency_id, data_year)
	   LEFT JOIN ucr_prd.ref_division USING (division_id)
     LEFT JOIN ucr_prd.ref_region USING (region_id)
     LEFT JOIN ucr_prd.ref_agency_type USING (agency_type_id)
	  WHERE ref_agency_status.data_year IS NOT NULL AND ref_agency_yearly.is_nibrs IS TRUE
	) agencies 
         ON ((nibrs_incident.agency_id = agencies.agency_id) AND (EXTRACT(year FROM nibrs_incident.incident_date) = agencies.data_year))
  LEFT JOIN ucr_prd.nibrs_victim nibrs_victim USING (incident_id)
  LEFT JOIN ucr_prd.nibrs_victim_offense ON (nibrs_victim.victim_id = nibrs_victim_offense.victim_id)
  LEFT JOIN ucr_prd.nibrs_offense ON ((nibrs_incident.incident_id = nibrs_offense.incident_id) AND (nibrs_victim_offense.offense_id = nibrs_offense.offense_id))
  LEFT JOIN ucr_prd.lkup_nibrs_offense USING (offense_code)
  LEFT JOIN ucr_prd.form_month ON (nibrs_incident.form_month_id = form_month.form_month_id AND agencies.agency_id = form_month.agency_id AND agencies.data_year = form_month.data_year)
 WHERE ", state_year_where, " AND form_month.form_code = 'N'"
)
victim_offense_month_df <- time_query(con, query_victim_offense_month)
victim_offense_month_df %>% write_csv(gzfile(paste0(queried_data_path,"victim_offense_form_code_N_",INPUT_STATE,".csv.gz")), na="")

### tasks/generate_estimates/Setup_part1_bystate/00a_Create_Datasets_full.Rmd ####
query_offenses_incidents <- paste0("
 SELECT
  agencies.ori AS ori,
  agencies.legacy_ori AS legacy_ori,
  extract(year FROM incident_date) as data_year,
  nibrs_incident.incident_id AS incident_id,
  agencies.agency_status,
  agencies.covered_flag,
  agencies.dormant_flag,
  agencies.agency_type_name,
  agencies.state_id AS state_id,
  agencies.state_name AS state_name,
  agencies.state_abbr AS state_abbr,
  agencies.state_postal_abbr AS state_postal_abbr, 
  nibrs_offense_type.offense_code AS offense_code,
  nibrs_offense_type.name AS offense_name,
  nibrs_offense_type.crime_against AS crime_against,
  nibrs_offense_type.category_name AS offense_category_name,
  nibrs_offense_type.offense_group AS offense_group,
  nibrs_offense.offense_id,
  nibrs_location_type.location_code as location_code,
  nibrs_location_type.name as location_name
 FROM ucr_prd.nibrs_incident nibrs_incident
  LEFT JOIN (
	SELECT
	  ref_agency.ori,
	  ref_agency.legacy_ori,
	  ref_agency_type.name as agency_type_name,
	  ref_agency.agency_id,
	  ref_agency.nibrs_start_date,
	  ref_agency_status.data_year,
	  ref_agency_status.agency_status,
	  ref_agency_yearly.is_nibrs,
	  ref_agency.state_id,
	  ref_state.name as state_name,
	  ref_state.abbr as state_abbr,
	  ref_state.postal_abbr as state_postal_abbr,
	  CASE
            WHEN ref_agency_yearly.is_covered IS TRUE THEN 'Y'::text
            WHEN ref_agency_yearly.is_covered IS FALSE THEN 'N'::text
            ELSE ' '::text
        END AS covered_flag,
      CASE
            WHEN ref_agency_yearly.agency_status = 'D'::bpchar THEN 'Y'::text
            ELSE 'N'::text
        END AS dormant_flag
	FROM ucr_prd.ref_agency_yearly ref_agency_yearly
	LEFT JOIN ucr_prd.ref_agency ref_agency USING (agency_id)
	LEFT JOIN ucr_prd.ref_state USING (state_id)
	LEFT JOIN ucr_prd.ref_agency_status ref_agency_status USING (agency_id, data_year)
	LEFT JOIN ucr_prd.ref_agency_type USING (agency_type_id)
	WHERE ref_agency_status.data_year IS NOT NULL AND ref_agency_yearly.is_nibrs IS TRUE
) agencies 
 	ON ((nibrs_incident.agency_id = agencies.agency_id) AND (EXTRACT(year FROM nibrs_incident.incident_date) = agencies.data_year))
LEFT JOIN ucr_prd.nibrs_offense using (incident_id)
LEFT JOIN ucr_prd.lkup_nibrs_offense nibrs_offense_type using (offense_code)
LEFT JOIN ucr_prd.lkup_nibrs_location nibrs_location_type using (location_code) 
 WHERE ", state_year_where)
offenses_incidents_df <- time_query(con, query_offenses_incidents)
offenses_incidents_df %>% write_csv(gzfile(paste0(der_bystate_file_path,"raw_all_Offenses_incident_",INPUT_STATE,".csv.gz")), na="")

query_incidents_pop_group <- paste0("
 SELECT 
   EXTRACT(year FROM nibrs_incident.incident_date) as data_year,
   agencies.ori,
   agencies.legacy_ori,
   nibrs_incident.incident_id AS incident_id,
   agencies.state_id,
   agencies.state_name,
   agencies.state_abbr,
   agencies.state_postal_abbr,
   nibrs_incident.incident_hour,
   CASE
       WHEN nibrs_incident.is_reported_date IS TRUE THEN 'R'::bpchar
       WHEN nibrs_incident.is_reported_date IS FALSE THEN ''::bpchar
       ELSE NULL::bpchar
   END AS report_date_flag,
   agencies.population_group_id,
   agencies.population_group_code,
   agencies.population_group_desc,
   agencies.parent_pop_group_code,
   agencies.parent_pop_group_desc,
   agencies.agency_type_name
 FROM ucr_prd.nibrs_incident
	LEFT JOIN (
	  SELECT
	   ref_agency.ori,
	   ref_agency.agency_id,
	   ref_agency.legacy_ori,
	   ref_agency_status.data_year,
	   ref_agency_status.agency_status,
	   ref_agency_yearly.is_nibrs,
	   ref_state.state_id,
     ref_state.name AS state_name,
     ref_state.abbr AS state_abbr,
     ref_state.postal_abbr AS state_postal_abbr,
     ref_agency_yearly.population_group_id,
     ref_population_group.code AS population_group_code,
     ref_population_group.description AS population_group_desc,
     ref_parent_population_group.code AS parent_pop_group_code,
     ref_parent_population_group.description AS parent_pop_group_desc,
     ref_agency_type.name as agency_type_name
	  FROM ucr_prd.ref_agency_yearly ref_agency_yearly
	   LEFT JOIN ucr_prd.ref_agency ref_agency USING (agency_id)
	   LEFT JOIN ucr_prd.ref_state USING (state_id)
	   LEFT JOIN ucr_prd.ref_agency_status ref_agency_status USING (agency_id, data_year)
	   LEFT JOIN ucr_prd.ref_agency_type USING (agency_type_id)
	   LEFT JOIN ucr_prd.ref_population_group USING (population_group_id)
     LEFT JOIN ucr_prd.ref_parent_population_group USING (parent_pop_group_id)
	  WHERE ref_agency_status.data_year IS NOT NULL AND ref_agency_yearly.is_nibrs IS TRUE
	) agencies 
         ON ((nibrs_incident.agency_id = agencies.agency_id) AND (EXTRACT(year FROM nibrs_incident.incident_date) = agencies.data_year))
 WHERE ", state_year_where)
incidents_pop_group_df <- time_query(con, query_incidents_pop_group)
incidents_pop_group_df %>% write_csv(gzfile(paste0(der_bystate_file_path,"raw_Time_of_day_population_agency_",INPUT_STATE,".csv.gz")), na="")

query_property_loss <- paste0("
 SELECT 
  agencies.ori,
  EXTRACT(year FROM nibrs_incident.incident_date) as data_year,
  nibrs_incident.incident_id,
  agencies.state_id,
  agencies.state_name,
  agencies.state_abbr,
  agencies.state_postal_abbr,
  nibrs_property.prop_loss_code,
  lkup_nibrs_property_loss.name AS prop_loss_name,
  lkup_nibrs_property_loss.description AS prop_loss_desc
 FROM ucr_prd.nibrs_incident
	LEFT JOIN (
	  SELECT
	   ref_agency.ori,
	   ref_agency.agency_id,
	   ref_agency.legacy_ori,
	   ref_agency_status.data_year,
	   ref_agency_status.agency_status,
	   ref_agency_yearly.is_nibrs,
	   ref_state.state_id,
     ref_state.name AS state_name,
     ref_state.abbr AS state_abbr,
     ref_state.postal_abbr AS state_postal_abbr
	  FROM ucr_prd.ref_agency_yearly ref_agency_yearly
	   LEFT JOIN ucr_prd.ref_agency ref_agency USING (agency_id)
	   LEFT JOIN ucr_prd.ref_state USING (state_id)
	   LEFT JOIN ucr_prd.ref_agency_status ref_agency_status USING (agency_id, data_year)
	  WHERE ref_agency_status.data_year IS NOT NULL AND ref_agency_yearly.is_nibrs IS TRUE
	) agencies 
         ON ((nibrs_incident.agency_id = agencies.agency_id) AND (EXTRACT(year FROM nibrs_incident.incident_date) = agencies.data_year))
  LEFT JOIN ucr_prd.nibrs_property USING (incident_id)
  LEFT JOIN ucr_prd.lkup_nibrs_property_loss USING (prop_loss_code)
 WHERE ", state_year_where)  
property_loss_df <- time_query(con, query_property_loss)
property_loss_df %>% write_csv(gzfile(paste0(der_bystate_file_path,"raw_property_loss_", INPUT_STATE, ".csv.gz")), na="")

query_offense_attempt_complete <- paste0("
 SELECT 
  agencies.ori AS ori,
  agencies.legacy_ori AS legacy_ori,
  extract(year FROM incident_date) as data_year,
  nibrs_incident.incident_id AS incident_id,
  agencies.agency_status,
  agencies.covered_flag,
  agencies.dormant_flag,
  agencies.agency_type_name,
  agencies.state_id AS state_id,
  agencies.state_name AS state_name,
  agencies.state_abbr AS state_abbr,
  agencies.state_postal_abbr AS state_postal_abbr,
  agencies.nibrs_start_date as nibrs_start_date,
  nibrs_offense_type.offense_code AS offense_code,
  nibrs_offense_type.name AS offense_name,
  nibrs_offense_type.crime_against AS crime_against,
  nibrs_offense_type.category_name AS offense_category_name,
  nibrs_offense_type.offense_group AS offense_group,
  nibrs_offense.offense_id,
  nibrs_offense.attempt_complete_code AS attempt_complete_code,
  nibrs_incident.incident_date AS incident_date,
  extract(year  FROM incident_date) as incident_year,
  extract(month  FROM incident_date) as incident_month,
  nibrs_offense.location_code AS location_code,
  nibrs_location.name AS location_name,
  nibrs_offense.method_of_entry_code AS method_entry_code,
  nibrs_offense.method_of_entry_code AS method_of_entry_code,
  nibrs_offense.num_premises_entered AS num_premises_entered
 FROM ucr_prd.nibrs_incident nibrs_incident
  LEFT JOIN (
	 SELECT
	  ref_agency.ori,
	  ref_agency.legacy_ori,
	  ref_agency_type.name as agency_type_name,
	  ref_agency.agency_id,
	  ref_agency.nibrs_start_date,
	  ref_agency_status.data_year,
	  ref_agency_status.agency_status,
	  ref_agency_yearly.is_nibrs,
	  ref_agency.state_id,
	  ref_state.name as state_name,
	  ref_state.abbr as state_abbr,
	  ref_state.postal_abbr as state_postal_abbr,
	  CASE
            WHEN ref_agency_yearly.is_covered IS TRUE THEN 'Y'::text
            WHEN ref_agency_yearly.is_covered IS FALSE THEN 'N'::text
            ELSE ' '::text
        END AS covered_flag,
      CASE
            WHEN ref_agency_yearly.agency_status = 'D'::bpchar THEN 'Y'::text
            ELSE 'N'::text
        END AS dormant_flag
	 FROM ucr_prd.ref_agency_yearly ref_agency_yearly
	  LEFT JOIN ucr_prd.ref_agency ref_agency USING (agency_id)
	  LEFT JOIN ucr_prd.ref_state USING (state_id)
	  LEFT JOIN ucr_prd.ref_agency_status ref_agency_status USING (agency_id, data_year)
	  LEFT JOIN ucr_prd.ref_agency_type USING (agency_type_id)
	 WHERE ref_agency_status.data_year IS NOT NULL AND ref_agency_yearly.is_nibrs IS TRUE
   ) agencies 
 	   ON ((nibrs_incident.agency_id = agencies.agency_id) AND (EXTRACT(year FROM nibrs_incident.incident_date) = agencies.data_year))
  LEFT JOIN ucr_prd.nibrs_offense using (incident_id)
  LEFT JOIN ucr_prd.lkup_nibrs_offense nibrs_offense_type using (offense_code)
  LEFT JOIN ucr_prd.lkup_nibrs_location nibrs_location using (location_code) 
 WHERE ", state_year_where)
offense_attempt_complete_df <- time_query(con, query_offense_attempt_complete)
offense_attempt_complete_df %>% write_csv(gzfile(paste0(queried_data_path,"offense_attempt_complete_",INPUT_STATE,".csv.gz")), na="")

query_bias_victim <- paste0("
 SELECT 
  agencies.ori,
  agencies.legacy_ori,
  EXTRACT(year FROM nibrs_incident.incident_date) as data_year,
  nibrs_incident.incident_id AS incident_id,
  agencies.agency_status,
  agencies.covered_flag,
  agencies.dormant_flag,
  agencies.agency_type_name,
  nibrs_victim.victim_id,
  nibrs_victim.victim_type_code,
  agencies.state_id,
  agencies.state_name,
  agencies.state_abbr,
  agencies.state_postal_abbr,
  nibrs_bias_motivation.bias_code,
  lkup_bias.category AS bias_name,
  lkup_bias.description AS bias_desc
 FROM ucr_prd.nibrs_incident
	LEFT JOIN (
	 SELECT
    ref_agency.ori,
    ref_agency.legacy_ori,
    ref_agency_status.data_year,
    ref_agency.agency_id,
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
    ref_agency_type.name AS agency_type_name,
    ref_agency.state_id,
    ref_state.name AS state_name,
    ref_state.abbr AS state_abbr,
    ref_state.postal_abbr AS state_postal_abbr,
    ref_agency_yearly.population 
	 FROM ucr_prd.ref_agency_yearly ref_agency_yearly
	   LEFT JOIN ucr_prd.ref_agency ref_agency USING (agency_id)
	   LEFT JOIN ucr_prd.ref_state USING (state_id)
	   LEFT JOIN ucr_prd.ref_agency_status ref_agency_status USING (agency_id, data_year)
	   LEFT JOIN ucr_prd.ref_submitting_agency USING (agency_id)
     LEFT JOIN ucr_prd.ref_agency_type USING (agency_type_id)
	  WHERE ref_agency_status.data_year IS NOT NULL AND ref_agency_yearly.is_nibrs IS TRUE
  ) agencies 
      ON ((nibrs_incident.agency_id = agencies.agency_id) AND (EXTRACT(year FROM nibrs_incident.incident_date) = agencies.data_year))
  LEFT JOIN ucr_prd.nibrs_victim USING (incident_id)
  LEFT JOIN ucr_prd.nibrs_offense USING (incident_id)
  LEFT JOIN ucr_prd.nibrs_bias_motivation USING (offense_id)
  LEFT JOIN ucr_prd.lkup_bias USING (bias_code)
 WHERE ", state_year_where)
bias_victim_df <- time_query(con, query_bias_victim)
bias_victim_df %>% write_csv(gzfile(paste0(der_bystate_file_path,"raw_bias_hate_crime_victim_",INPUT_STATE,".csv.gz")), na="")

query_bias_offense <- paste0("
 SELECT 
  agencies.ori,
  agencies.legacy_ori,
  EXTRACT(year FROM nibrs_incident.incident_date) as data_year,
  nibrs_incident.incident_id AS incident_id,
  agencies.agency_status,
  agencies.covered_flag,
  agencies.dormant_flag,
  agencies.agency_type_name,
  nibrs_victim.victim_id,
  nibrs_victim.victim_type_code,
  nibrs_offense.offense_id,
  agencies.state_id,
  agencies.state_name,
  agencies.state_abbr,
  agencies.state_postal_abbr,
  nibrs_bias_motivation.bias_code,
  lkup_bias.category AS bias_name,
  lkup_bias.description AS bias_desc
 FROM ucr_prd.nibrs_incident
	LEFT JOIN (
	 SELECT
    ref_agency.ori,
    ref_agency.legacy_ori,
    ref_agency_status.data_year,
    ref_agency.agency_id,
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
    ref_agency_type.name AS agency_type_name,
    ref_agency.state_id,
    ref_state.name AS state_name,
    ref_state.abbr AS state_abbr,
    ref_state.postal_abbr AS state_postal_abbr,
    ref_agency_yearly.population 
	 FROM ucr_prd.ref_agency_yearly ref_agency_yearly
	   LEFT JOIN ucr_prd.ref_agency ref_agency USING (agency_id)
	   LEFT JOIN ucr_prd.ref_state USING (state_id)
	   LEFT JOIN ucr_prd.ref_agency_status ref_agency_status USING (agency_id, data_year)
	   LEFT JOIN ucr_prd.ref_submitting_agency USING (agency_id)
     LEFT JOIN ucr_prd.ref_agency_type USING (agency_type_id)
	  WHERE ref_agency_status.data_year IS NOT NULL AND ref_agency_yearly.is_nibrs IS TRUE
  ) agencies 
      ON ((nibrs_incident.agency_id = agencies.agency_id) AND (EXTRACT(year FROM nibrs_incident.incident_date) = agencies.data_year))
  LEFT JOIN ucr_prd.nibrs_victim USING (incident_id)
  LEFT JOIN ucr_prd.nibrs_victim_offense USING (victim_id)
  LEFT JOIN ucr_prd.nibrs_offense USING (offense_id)
  LEFT JOIN ucr_prd.nibrs_bias_motivation USING (offense_id)
  LEFT JOIN ucr_prd.lkup_bias USING (bias_code)
 WHERE ", state_year_where)
bias_offense_df <- time_query(con, query_bias_offense)
bias_offense_df %>% write_csv(gzfile(paste0(der_bystate_file_path,"raw_bias_hate_crime_offenses_",INPUT_STATE,".csv.gz")), na="")

query_weapon_offense <- paste0("
 SELECT
  agencies.ori AS ori,
  extract(year FROM incident_date) as data_year,
  nibrs_incident.incident_id AS incident_id,
  nibrs_victim.victim_id,
  nibrs_offense.offense_id,
  agencies.state_id AS state_id,
  agencies.state_name AS state_name,
  agencies.state_abbr AS state_abbr,
  agencies.state_postal_abbr AS state_postal_abbr,
  nibrs_weapon_type.weapon_code,
  lkup_nibrs_weapon.name as weapon_name 
 FROM ucr_prd.nibrs_incident nibrs_incident
  LEFT JOIN (
	 SELECT
	  ref_agency.ori,
	  ref_agency.legacy_ori,
	  ref_agency_type.name as agency_type_name,
	  ref_agency.agency_id,
	  ref_agency.nibrs_start_date,
	  ref_agency_status.data_year,
	  ref_agency_status.agency_status,
	  ref_agency_yearly.is_nibrs,
	  ref_agency.state_id,
	  ref_state.name as state_name,
	  ref_state.abbr as state_abbr,
	  ref_state.postal_abbr as state_postal_abbr,
	  CASE
            WHEN ref_agency_yearly.is_covered IS TRUE THEN 'Y'::text
            WHEN ref_agency_yearly.is_covered IS FALSE THEN 'N'::text
            ELSE ' '::text
        END AS covered_flag,
      CASE
            WHEN ref_agency_yearly.agency_status = 'D'::bpchar THEN 'Y'::text
            ELSE 'N'::text
        END AS dormant_flag
	FROM ucr_prd.ref_agency_yearly ref_agency_yearly
	 LEFT JOIN ucr_prd.ref_agency ref_agency USING (agency_id)
	 LEFT JOIN ucr_prd.ref_state USING (state_id)
	 LEFT JOIN ucr_prd.ref_agency_status ref_agency_status USING (agency_id, data_year)
	 LEFT JOIN ucr_prd.ref_agency_type USING (agency_type_id)
	WHERE ref_agency_status.data_year IS NOT NULL AND ref_agency_yearly.is_nibrs IS TRUE
   ) agencies 
 	   ON ((nibrs_incident.agency_id = agencies.agency_id) AND (EXTRACT(year FROM nibrs_incident.incident_date) = agencies.data_year))
  LEFT JOIN ucr_prd.nibrs_victim nibrs_victim ON (nibrs_incident.incident_id = nibrs_victim.incident_id)
  LEFT JOIN ucr_prd.nibrs_victim_offense nibrs_victim_offense ON (nibrs_victim.victim_id = nibrs_victim_offense.victim_id)
  LEFT JOIN ucr_prd.nibrs_offense nibrs_offense ON (nibrs_victim_offense.offense_id = nibrs_offense.offense_id)
  LEFT JOIN ucr_prd.nibrs_offense_weapon nibrs_weapon_type ON (nibrs_offense.offense_id = nibrs_weapon_type.offense_id)
  LEFT JOIN ucr_prd.lkup_weapon lkup_nibrs_weapon ON (lkup_nibrs_weapon.weapon_code = nibrs_weapon_type.weapon_code)
 WHERE ", state_year_where)
weapon_offense_df <- time_query(con, query_weapon_offense)
weapon_offense_df %>% write_csv(gzfile(paste0(der_bystate_file_path,"raw_weapon_offense_",INPUT_STATE,".csv.gz")), na="")

query_arrestee_offense_location <- paste0("
 SELECT
  agencies.ori AS ori,
  agencies.legacy_ori AS legacy_ori,
  extract(year FROM incident_date) as data_year,
  nibrs_incident.incident_id AS incident_id,
  agencies.agency_status,
  agencies.covered_flag,
  agencies.dormant_flag,
  agencies.agency_type_name,
  nibrs_arrestee.arrestee_id,
  agencies.state_id AS state_id,
  agencies.state_name AS state_name,
  agencies.state_abbr AS state_abbr,
  agencies.state_postal_abbr AS state_postal_abbr,
  nibrs_offense_type.offense_code AS offense_code,
  nibrs_offense_type.name AS offense_name,
  nibrs_offense_type.crime_against AS crime_against,
  nibrs_offense_type.category_name AS offense_category_name,
  nibrs_offense_type.offense_group AS offense_group,
  nibrs_location_type.location_code,
  nibrs_location_type.name as location_name
 FROM ucr_prd.nibrs_incident nibrs_incident
  LEFT JOIN (
	SELECT
	  ref_agency.ori,
	  ref_agency.legacy_ori,
	  ref_agency_type.name as agency_type_name,
	  ref_agency.agency_id,
	  ref_agency.nibrs_start_date,
	  ref_agency_status.data_year,
	  ref_agency_status.agency_status,
	  ref_agency_yearly.is_nibrs,
	  ref_agency.state_id,
	  ref_state.name as state_name,
	  ref_state.abbr as state_abbr,
	  ref_state.postal_abbr as state_postal_abbr,
	  CASE
            WHEN ref_agency_yearly.is_covered IS TRUE THEN 'Y'::text
            WHEN ref_agency_yearly.is_covered IS FALSE THEN 'N'::text
            ELSE ' '::text
        END AS covered_flag,
      CASE
            WHEN ref_agency_yearly.agency_status = 'D'::bpchar THEN 'Y'::text
            ELSE 'N'::text
        END AS dormant_flag
	FROM ucr_prd.ref_agency_yearly ref_agency_yearly
	LEFT JOIN ucr_prd.ref_agency ref_agency USING (agency_id)
	LEFT JOIN ucr_prd.ref_state USING (state_id)
	LEFT JOIN ucr_prd.ref_agency_status ref_agency_status USING (agency_id, data_year)
	LEFT JOIN ucr_prd.ref_agency_type USING (agency_type_id)
	WHERE ref_agency_status.data_year IS NOT NULL AND ref_agency_yearly.is_nibrs IS TRUE
) agencies 
 	ON ((nibrs_incident.agency_id = agencies.agency_id) AND (EXTRACT(year FROM nibrs_incident.incident_date) = agencies.data_year))
  LEFT JOIN ucr_prd.nibrs_arrestee nibrs_arrestee ON (nibrs_incident.incident_id = nibrs_arrestee.incident_id)
  LEFT JOIN ucr_prd.nibrs_offense nibrs_offense ON (nibrs_arrestee.incident_id = nibrs_offense.incident_id)
  LEFT JOIN ucr_prd.lkup_nibrs_offense nibrs_offense_type ON (nibrs_offense.offense_code = nibrs_offense_type.offense_code)
  LEFT JOIN ucr_prd.lkup_nibrs_location nibrs_location_type ON (nibrs_location_type.location_code = nibrs_offense.location_code)
 WHERE ", state_year_where)
arrestee_offense_location_df <- time_query(con, query_arrestee_offense_location)
arrestee_offense_location_df %>% write_csv(gzfile(paste0(der_bystate_file_path,"raw_all_Offenses_arrestee_",INPUT_STATE,".csv.gz")), na="")

query_arrestee_offense <- paste0("
 SELECT 
  agencies.ori AS ori,
  agencies.legacy_ori AS legacy_ori,
  extract(year FROM incident_date) as data_year,
  nibrs_incident.incident_id AS incident_id,
  agencies.agency_status,
  agencies.covered_flag,
  agencies.dormant_flag,
  agencies.agency_type_name,
  nibrs_arrestee.arrestee_id,
  agencies.state_id AS state_id,
  agencies.state_name AS state_name,
  agencies.state_abbr AS state_abbr,
  agencies.state_postal_abbr AS state_postal_abbr,
  nibrs_offense_type.offense_code AS offense_code,
  nibrs_offense_type.name AS offense_name,
  nibrs_offense_type.crime_against AS crime_against,
  nibrs_offense_type.category_name AS offense_category_name,
  nibrs_offense_type.offense_group AS offense_group
 FROM ucr_prd.nibrs_incident nibrs_incident
  LEFT JOIN (
	SELECT
	  ref_agency.ori,
	  ref_agency.legacy_ori,
	  ref_agency_type.name as agency_type_name,
	  ref_agency.agency_id,
	  ref_agency.nibrs_start_date,
	  ref_agency_status.data_year,
	  ref_agency_status.agency_status,
	  ref_agency_yearly.is_nibrs,
	  ref_agency.state_id,
	  ref_state.name as state_name,
	  ref_state.abbr as state_abbr,
	  ref_state.postal_abbr as state_postal_abbr,
	  CASE
            WHEN ref_agency_yearly.is_covered IS TRUE THEN 'Y'::text
            WHEN ref_agency_yearly.is_covered IS FALSE THEN 'N'::text
            ELSE ' '::text
        END AS covered_flag,
      CASE
            WHEN ref_agency_yearly.agency_status = 'D'::bpchar THEN 'Y'::text
            ELSE 'N'::text
        END AS dormant_flag
	FROM ucr_prd.ref_agency_yearly ref_agency_yearly
	LEFT JOIN ucr_prd.ref_agency ref_agency USING (agency_id)
	LEFT JOIN ucr_prd.ref_state USING (state_id)
	LEFT JOIN ucr_prd.ref_agency_status ref_agency_status USING (agency_id, data_year)
	LEFT JOIN ucr_prd.ref_agency_type USING (agency_type_id)
	WHERE ref_agency_status.data_year IS NOT NULL AND ref_agency_yearly.is_nibrs IS TRUE
) agencies 
 	ON ((nibrs_incident.agency_id = agencies.agency_id) AND (EXTRACT(year FROM nibrs_incident.incident_date) = agencies.data_year))
  LEFT JOIN ucr_prd.nibrs_arrestee nibrs_arrestee ON (nibrs_incident.incident_id = nibrs_arrestee.incident_id)
  LEFT JOIN ucr_prd.lkup_nibrs_offense nibrs_offense_type ON (nibrs_arrestee.offense_code = nibrs_offense_type.offense_code)
 WHERE ", state_year_where)
arrestee_offense_df <- time_query(con, query_arrestee_offense)
arrestee_offense_df %>% write_csv(gzfile(paste0(der_bystate_file_path,"raw_all_arrestee_arrest_code_",INPUT_STATE,".csv.gz")), na="")

query_arrestee_bias_motivation <- paste0("
 SELECT 
  agencies.ori,
  agencies.legacy_ori,
  EXTRACT(year FROM nibrs_incident.incident_date) as data_year,
  nibrs_incident.incident_id AS incident_id,
  agencies.agency_status,
  agencies.covered_flag,
  agencies.dormant_flag,
  agencies.agency_type_name,
  agencies.state_id,
  agencies.state_name,
  agencies.state_abbr,
  agencies.state_postal_abbr,
  nibrs_arrestee.arrestee_id,
  nibrs_bias_motivation.bias_code,
  lkup_bias.category AS bias_name,
  lkup_bias.description AS bias_desc
 FROM ucr_prd.nibrs_incident
	LEFT JOIN (
	 SELECT
    ref_agency.ori,
    ref_agency.legacy_ori,
    ref_agency_status.data_year,
    ref_agency.agency_id,
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
    ref_agency_type.name AS agency_type_name,
    ref_agency.state_id,
    ref_state.name AS state_name,
    ref_state.abbr AS state_abbr,
    ref_state.postal_abbr AS state_postal_abbr,
    ref_agency_yearly.population 
	 FROM ucr_prd.ref_agency_yearly ref_agency_yearly
	   LEFT JOIN ucr_prd.ref_agency ref_agency USING (agency_id)
	   LEFT JOIN ucr_prd.ref_state USING (state_id)
	   LEFT JOIN ucr_prd.ref_agency_status ref_agency_status USING (agency_id, data_year)
	   LEFT JOIN ucr_prd.ref_submitting_agency USING (agency_id)
     LEFT JOIN ucr_prd.ref_agency_type USING (agency_type_id)
	 WHERE ref_agency_status.data_year IS NOT NULL AND ref_agency_yearly.is_nibrs IS TRUE
  ) agencies 
      ON ((nibrs_incident.agency_id = agencies.agency_id) AND (EXTRACT(year FROM nibrs_incident.incident_date) = agencies.data_year))
  LEFT JOIN ucr_prd.nibrs_arrestee ON (nibrs_incident.incident_id = nibrs_arrestee.incident_id)
  LEFT JOIN ucr_prd.nibrs_offense ON (nibrs_arrestee.incident_id = nibrs_offense.incident_id)
  LEFT JOIN ucr_prd.nibrs_bias_motivation ON (nibrs_bias_motivation.offense_id = nibrs_offense.offense_id)
  LEFT JOIN ucr_prd.lkup_bias USING (bias_code)
 WHERE ", state_year_where)
arrestee_bias_motivation_df <- time_query(con, query_arrestee_bias_motivation)
arrestee_bias_motivation_df %>% 
  select(ori, legacy_ori, data_year, incident_id, agency_status,
         covered_flag, dormant_flag, agency_type_name, arrestee_id, state_id,
         state_name, state_abbr, state_postal_abbr, bias_code, bias_name, bias_desc) %>% 
  write_csv(gzfile(paste0(der_bystate_file_path,"raw_bias_hate_crime_arrestee_",INPUT_STATE,".csv.gz")), na="")

query_arrestee_drug_offense <- paste0("
 SELECT
  agencies.ori AS ori,
  agencies.legacy_ori AS legacy_ori,
  extract(year FROM nibrs_incident.incident_date) AS data_year,
  nibrs_incident.incident_id AS incident_id,
  agencies.agency_status,
  agencies.covered_flag,
  agencies.dormant_flag,
  agencies.agency_type_name,
  agencies.state_id AS state_id,
  agencies.state_name AS state_name,
  agencies.state_abbr AS state_abbr,
  agencies.state_postal_abbr AS state_postal_abbr,
  nibrs_offense_type.offense_code AS offense_code,
  nibrs_offense_type.name AS offense_name,
  nibrs_offense_type.crime_against AS crime_against,
  nibrs_offense_type.category_name AS offense_category_name,
  nibrs_offense_type.offense_group AS offense_group,
  nibrs_suspected_drug_type.drug_code AS suspected_drug_code,
  nibrs_suspected_drug_type.name AS suspected_drug_name,
  nibrs_criminal_act_type.criminal_activity_code AS criminal_act_code,
  nibrs_criminal_act_type_lkup.name AS criminal_act_name,
  nibrs_criminal_act_type_lkup.description AS criminal_act_desc,
  nibrs_arrestee.arrestee_id AS arrestee_id,
  nibrs_arrestee.sequence_number AS arrestee_seq_num
 FROM ucr_prd.nibrs_incident nibrs_incident
    LEFT JOIN (
  	SELECT
  	  ref_agency.ori,
  	  ref_agency.legacy_ori,
  	  ref_agency_type.name as agency_type_name,
  	  ref_agency.agency_id,
  	  ref_agency.nibrs_start_date,
  	  ref_agency_status.data_year,
  	  ref_agency_status.agency_status,
  	  ref_agency_yearly.is_nibrs,
  	  ref_agency.state_id,
  	  ref_state.name as state_name,
  	  ref_state.abbr as state_abbr,
  	  ref_state.postal_abbr as state_postal_abbr,
  	  CASE
              WHEN ref_agency_yearly.is_covered IS TRUE THEN 'Y'::text
              WHEN ref_agency_yearly.is_covered IS FALSE THEN 'N'::text
              ELSE ' '::text
          END AS covered_flag,
        CASE
              WHEN ref_agency_yearly.agency_status = 'D'::bpchar THEN 'Y'::text
              ELSE 'N'::text
          END AS dormant_flag
  	FROM ucr_prd.ref_agency_yearly ref_agency_yearly
     LEFT JOIN ucr_prd.ref_agency ref_agency USING (agency_id)
     LEFT JOIN ucr_prd.ref_state USING (state_id)
     LEFT JOIN ucr_prd.ref_agency_status ref_agency_status USING (agency_id, data_year)
     LEFT JOIN ucr_prd.ref_agency_type USING (agency_type_id)
  	WHERE ref_agency_status.data_year IS NOT NULL AND ref_agency_yearly.is_nibrs IS TRUE
    ) agencies 
   	  ON ((nibrs_incident.agency_id = agencies.agency_id) AND (EXTRACT(year FROM nibrs_incident.incident_date) = agencies.data_year))
  LEFT JOIN ucr_prd.nibrs_offense nibrs_offense ON (nibrs_incident.incident_id = nibrs_offense.incident_id)
  LEFT JOIN ucr_prd.lkup_nibrs_offense nibrs_offense_type ON (nibrs_offense.offense_code = nibrs_offense_type.offense_code)
  LEFT JOIN ucr_prd.nibrs_arrestee nibrs_arrestee on (nibrs_incident.incident_id = nibrs_arrestee.incident_id and nibrs_offense_type.offense_code = nibrs_arrestee.offense_code)
  LEFT JOIN ucr_prd.nibrs_property nibrs_property ON (nibrs_incident.incident_id = nibrs_property.incident_id)
  LEFT JOIN ucr_prd.nibrs_property_description nibrs_property_desc ON (nibrs_property.property_id = nibrs_property_desc.property_id)
  LEFT JOIN ucr_prd.lkup_nibrs_property_description nibrs_prop_desc_type ON (nibrs_property_desc.prop_desc_code = nibrs_prop_desc_type.prop_desc_code)
  LEFT JOIN ucr_prd.lkup_nibrs_property_loss nibrs_prop_loss_type ON (nibrs_property.prop_loss_code = nibrs_prop_loss_type.prop_loss_code)
  LEFT JOIN ucr_prd.nibrs_suspected_drug nibrs_suspected_drug ON (nibrs_property.property_id = nibrs_suspected_drug.property_id)
  LEFT JOIN ucr_prd.lkup_nibrs_drug nibrs_suspected_drug_type ON (nibrs_suspected_drug.drug_code = nibrs_suspected_drug_type.drug_code)
  LEFT JOIN ucr_prd.nibrs_criminal_activity nibrs_criminal_act_type ON (nibrs_offense.offense_id = nibrs_criminal_act_type.offense_id)
  LEFT JOIN ucr_prd.lkup_nibrs_criminal_activity nibrs_criminal_act_type_lkup ON (nibrs_criminal_act_type.criminal_activity_code = nibrs_criminal_act_type_lkup.criminal_activity_code)
 WHERE nibrs_arrestee.arrestee_id IS NOT NULL and trim(upper(nibrs_offense_type.offense_code)) in ('35A', '35B') and ", state_year_where)
arrestee_drug_offense_df <- time_query(con, query_arrestee_drug_offense)
arrestee_drug_offense_df %>% write_csv(gzfile(paste0(der_bystate_file_path,"recoded_all_Offenses_recoded_arrestee_drug_activity_",INPUT_STATE,".csv.gz")), na="")

query_victim <- paste0("
 SELECT 
  agencies.ori,
  EXTRACT(year FROM nibrs_incident.incident_date) as data_year,
  nibrs_incident.incident_id,
  agencies.state_id,
  agencies.state_name,
  agencies.state_abbr,
  agencies.state_postal_abbr,
  nibrs_victim.victim_id,
  nibrs_victim.sequence_number AS victim_seq_num,
  nibrs_victim.victim_type_code AS victim_type_code,
  lkup_nibrs_victim_type.name AS victim_type_name,
  nibrs_victim.age_code AS victim_age_code,
  lkup_age.name AS victim_age_name,
  CASE
      WHEN nibrs_victim.age_code = ANY (ARRAY['NN'::bpchar, 'NB'::bpchar, 'BB'::bpchar, '00'::bpchar, 'NS'::bpchar, '99'::bpchar]) THEN NULL::bpchar
      ELSE nibrs_victim.age_code
  END AS victim_age_num,
  CASE
      WHEN nibrs_victim.sex_code = 'X'::bpchar THEN ' '::bpchar
      ELSE nibrs_victim.sex_code
  END AS victim_sex_code,
  nibrs_victim.race_code AS victim_race_code,
  CAST(lkup_race.description AS TEXT) AS victim_race_desc, 
  nibrs_victim.ethnicity_code AS victim_ethnicity_code,
  lkup_ethnicity.description AS victim_ethnicity_name
 FROM ucr_prd.nibrs_incident
	LEFT JOIN (
	 SELECT
    ref_agency.ori,
    ref_agency.legacy_ori,
    ref_agency_status.data_year,
    ref_agency.agency_id,
    ref_agency_status.agency_status,
    ref_agency.state_id,
    ref_state.name AS state_name,
    ref_state.abbr AS state_abbr,
    ref_state.postal_abbr AS state_postal_abbr,
    ref_agency_yearly.population 
	 FROM ucr_prd.ref_agency_yearly ref_agency_yearly
	   LEFT JOIN ucr_prd.ref_agency ref_agency USING (agency_id)
	   LEFT JOIN ucr_prd.ref_state USING (state_id)
	   LEFT JOIN ucr_prd.ref_agency_status ref_agency_status USING (agency_id, data_year)
	   LEFT JOIN ucr_prd.ref_submitting_agency USING (agency_id)
     LEFT JOIN ucr_prd.ref_agency_type USING (agency_type_id)
	 WHERE ref_agency_status.data_year IS NOT NULL AND ref_agency_yearly.is_nibrs IS TRUE
  ) agencies 
      ON ((nibrs_incident.agency_id = agencies.agency_id) AND (EXTRACT(year FROM nibrs_incident.incident_date) = agencies.data_year))
  LEFT JOIN ucr_prd.nibrs_victim nibrs_victim USING (incident_id)
  LEFT JOIN ucr_prd.lkup_age USING (age_code)
  LEFT JOIN ucr_prd.lkup_ethnicity USING (ethnicity_code)
  LEFT JOIN ucr_prd.lkup_nibrs_victim_type USING (victim_type_code)
  LEFT JOIN ucr_prd.lkup_race USING (race_code)
 WHERE ", state_year_where)
victim_df <- time_query(con, query_victim)
victim_df %>% write_csv(gzfile(paste0(der_bystate_file_path,"raw_victim_",INPUT_STATE,".csv.gz")), na="")

query_victim_offender_rel <- paste0("
 SELECT 
  agencies.ori AS ori,
  EXTRACT(year FROM nibrs_incident.incident_date) as data_year,
  nibrs_incident.incident_id AS incident_id,
  nibrs_victim.victim_id,
  nibrs_victim.sequence_number AS victim_seq_num,
  nibrs_victim.victim_type_code AS victim_type_code,
  nibrs_victim.age_code AS victim_age_code,
  CASE
      WHEN nibrs_victim.age_code = ANY (ARRAY['NN'::bpchar, 'NB'::bpchar, 'BB'::bpchar, '00'::bpchar, 'NS'::bpchar, '99'::bpchar]) THEN NULL::bpchar
      ELSE nibrs_victim.age_code
  END AS victim_age_num,
  CASE
      WHEN nibrs_victim.sex_code = 'X'::bpchar THEN ' '::bpchar
      ELSE nibrs_victim.sex_code
  END AS victim_sex_code,
  nibrs_victim.race_code AS victim_race_code,
  nibrs_offender.offender_id,
  nibrs_offender.sequence_number AS offender_seq_num,
  nibrs_offender.age_code as offender_age_code,
  CASE
      WHEN nibrs_offender.age_code = ANY (ARRAY['NN'::bpchar, 'NB'::bpchar, 'BB'::bpchar, '00'::bpchar, 'NS'::bpchar, '99'::bpchar]) THEN NULL::bpchar
      ELSE nibrs_offender.age_code
  END AS offender_age_num,
  CASE
      WHEN nibrs_offender.sex_code = 'X'::bpchar THEN ' '::bpchar
      ELSE nibrs_offender.sex_code
  END AS offender_sex_code,
  nibrs_offender.race_code as offender_race_code,
  agencies.state_id AS state_id,
  agencies.state_name AS state_name,
  agencies.state_abbr AS state_abbr,
  agencies.state_postal_abbr AS state_postal_abbr,
  nibrs_victim_offender_relationship.relationship_code AS relationship_code,
  lkup_nibrs_relationship.name AS relationship_name
 FROM ucr_prd.nibrs_incident
	LEFT JOIN (
	 SELECT
    ref_agency.ori,
    ref_agency.legacy_ori,
    ref_agency_status.data_year,
    ref_agency.agency_id,
    ref_agency_status.agency_status,
    ref_agency.state_id,
    ref_state.name AS state_name,
    ref_state.abbr AS state_abbr,
    ref_state.postal_abbr AS state_postal_abbr,
    ref_agency_yearly.population 
	 FROM ucr_prd.ref_agency_yearly ref_agency_yearly
	   LEFT JOIN ucr_prd.ref_agency ref_agency USING (agency_id)
	   LEFT JOIN ucr_prd.ref_state USING (state_id)
	   LEFT JOIN ucr_prd.ref_agency_status ref_agency_status USING (agency_id, data_year)
	   LEFT JOIN ucr_prd.ref_submitting_agency USING (agency_id)
     LEFT JOIN ucr_prd.ref_agency_type USING (agency_type_id)
	 WHERE ref_agency_status.data_year IS NOT NULL AND ref_agency_yearly.is_nibrs IS TRUE
  ) agencies 
      ON ((nibrs_incident.agency_id = agencies.agency_id) AND (EXTRACT(year FROM nibrs_incident.incident_date) = agencies.data_year))
  LEFT JOIN ucr_prd.nibrs_offender USING (incident_id)
  LEFT JOIN ucr_prd.nibrs_victim USING (incident_id)
  LEFT JOIN ucr_prd.nibrs_victim_offender_relationship USING (victim_id, offender_id)
  LEFT JOIN ucr_prd.lkup_nibrs_relationship USING (relationship_code)
 WHERE ", state_year_where)
victim_offender_rel_df <- time_query(con, query_victim_offender_rel)
victim_offender_rel_df %>% write_csv(gzfile(paste0(der_bystate_file_path,"raw_victim_offender_rel_",INPUT_STATE,".csv.gz")), na="")

query_leoka_activity <- paste0("
 SELECT 
  EXTRACT(year FROM nibrs_incident.incident_date) as data_year,
  nibrs_incident.incident_id,
  nibrs_victim.victim_id,
  nibrs_victim.sequence_number AS victim_seq_num,
  nibrs_victim.victim_type_code AS victim_type_code,
  nibrs_victim.assignment_code AS assignment_code,
  lkup_assignment.name AS assignment_name,
  nibrs_victim.activity_code AS activity_code,
  lkup_nibrs_activity.name AS activity_name
 FROM ucr_prd.nibrs_incident
	LEFT JOIN (
	 SELECT
    ref_agency.ori,
    ref_agency.legacy_ori,
    ref_agency_status.data_year,
    ref_agency.agency_id,
    ref_agency_status.agency_status,
    ref_agency.state_id,
    ref_state.name AS state_name,
    ref_state.abbr AS state_abbr,
    ref_state.postal_abbr AS state_postal_abbr,
    ref_agency_yearly.population 
	 FROM ucr_prd.ref_agency_yearly ref_agency_yearly
	   LEFT JOIN ucr_prd.ref_agency ref_agency USING (agency_id)
	   LEFT JOIN ucr_prd.ref_state USING (state_id)
	   LEFT JOIN ucr_prd.ref_agency_status ref_agency_status USING (agency_id, data_year)
	 WHERE ref_agency_status.data_year IS NOT NULL AND ref_agency_yearly.is_nibrs IS TRUE
  ) agencies 
      ON ((nibrs_incident.agency_id = agencies.agency_id) AND (EXTRACT(year FROM nibrs_incident.incident_date) = agencies.data_year))
  LEFT JOIN ucr_prd.nibrs_victim USING (incident_id)
  LEFT JOIN ucr_prd.lkup_assignment USING (assignment_code)
  LEFT JOIN ucr_prd.lkup_nibrs_activity USING (activity_code)
 WHERE nibrs_victim.victim_type_code = 'L' AND ", state_year_where)
leoka_activity_df <- time_query(con, query_leoka_activity)
leoka_activity_df %>% write_csv(gzfile(paste0(queried_data_path,"raw_leoka_activity_",INPUT_STATE,".csv.gz")), na="")

query_leoka_offense <- paste0("
 SELECT 
  agencies.agency_id,
  agencies.data_year,
  agencies.ori,
  agencies.legacy_ori,
  agencies.direct_contributor_flag,
  agencies.dormant_flag,
  agencies.dormant_year,
  agencies.ucr_agency_name,
  agencies.agency_status,
  agencies.covered_flag,
  agencies.ncic_agency_name,
  agencies.pub_agency_name,
  agencies.pub_agency_unit,
  agencies.state_id,
  agencies.state_name,
  agencies.state_abbr,
  agencies.state_postal_abbr,
  agencies.division_code,
  agencies.division_name,
  agencies.region_code,
  agencies.region_name,
  agencies.region_desc,
  agencies.agency_type_name,
  agencies.population,
  agencies.submitting_agency_id,
  agencies.sai,
  agencies.suburban_area_flag,
  agencies.population_group_id,
  agencies.population_group_code,
  agencies.population_group_desc,
  agencies.parent_pop_group_code,
  agencies.parent_pop_group_desc,
  agencies.nibrs_cert_date,
  agencies.nibrs_start_date,
  agencies.nibrs_leoka_start_date,
  agencies.nibrs_ct_start_date,
  agencies.nibrs_multi_bias_start_date,
  agencies.nibrs_off_eth_start_date,
  agencies.county_name,
  agencies.msa_name,
  agencies.publishable_flag,
  agencies.nibrs_participated,
  EXTRACT(year FROM nibrs_incident.incident_date) AS data_year_nibrs_incident,
  nibrs_incident.incident_id AS incident_id,
  nibrs_incident.form_month_id AS nibrs_month_id,
  CASE
      WHEN nibrs_incident.is_cargo_theft IS TRUE THEN 'Y'::bpchar
      WHEN nibrs_incident.is_cargo_theft IS FALSE THEN 'N'::bpchar
      ELSE NULL::bpchar
  END AS cargo_theft_flag,
  nibrs_incident.incident_date AS incident_date,
  CASE
      WHEN nibrs_incident.is_reported_date IS TRUE THEN 'R'::bpchar
      WHEN nibrs_incident.is_reported_date IS FALSE THEN ''::bpchar
      ELSE NULL::bpchar
  END AS report_date_flag,
  nibrs_incident.incident_hour AS incident_hour,
  nibrs_incident.cleared_exceptionally_code AS cleared_except_code,
  nibrs_incident.cleared_exceptionally_date,
  nibrs_incident.did,
  nibrs_victim.victim_id,
  nibrs_victim.incident_id AS incident_id_nibrs_victim,
  nibrs_victim.sequence_number AS victim_seq_num,
  nibrs_victim.victim_type_code,
  nibrs_victim.assignment_code,
  nibrs_victim.activity_code,
  nibrs_victim.outside_agency_id,
  nibrs_victim.age_code,
  CASE
      WHEN nibrs_victim.age_code = ANY (ARRAY['NN'::bpchar, 'NB'::bpchar, 'BB'::bpchar, '00'::bpchar, 'NS'::bpchar, '99'::bpchar]) THEN NULL::bpchar
      ELSE nibrs_victim.age_code
  END AS age_num,
  CASE
      WHEN nibrs_victim.sex_code = 'X'::bpchar THEN ' '::bpchar
      ELSE nibrs_victim.sex_code
  END AS sex_code,
  nibrs_victim.race_code,
  nibrs_victim.ethnicity_code,
  CASE
      WHEN nibrs_victim.resident_status_code = 'None'::bpchar THEN ' '::bpchar
      WHEN nibrs_victim.resident_status_code = '-1'::bpchar THEN ' '::bpchar
      WHEN nibrs_victim.resident_status_code IS NULL THEN ' '::bpchar
      ELSE nibrs_victim.resident_status_code
  END AS resident_status_code,
  nibrs_victim_offense.victim_id AS victim_id_nibrs_victim_offense,
  nibrs_victim_offense.offense_id AS offense_id,
  nibrs_offense.offense_id AS offense_id_nibrs_offense,
  nibrs_offense.incident_id AS incident_id_nibrs_offense,
  nibrs_offense.offense_code,
  nibrs_offense.attempt_complete_code AS attempt_complete_flag,
  nibrs_offense.location_code,
  nibrs_offense.num_premises_entered,
  CASE
      WHEN nibrs_offense.method_of_entry_code IS NULL THEN ' '::bpchar
      ELSE nibrs_offense.method_of_entry_code
  END AS method_entry_code,
  lkup_nibrs_offense.name AS offense_name,
  lkup_nibrs_offense.crime_against,
  CASE
      WHEN lkup_nibrs_offense.used_for_ct = true THEN 'Y'
      ELSE 'N'
  END AS ct_flag,
  CASE
      WHEN lkup_nibrs_offense.used_for_hc = true THEN 'Y'
      ELSE 'N'
  END,
  lkup_nibrs_offense.hc_code AS hc_code,
  lkup_nibrs_offense.category_name AS offense_category_name,
  lkup_nibrs_offense.offense_group
 FROM ucr_prd.nibrs_incident
	LEFT JOIN (
	 SELECT DISTINCT
    ref_agency.ori,
    ref_agency.legacy_ori,
    ref_agency_status.data_year,
    ref_agency.agency_id,
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
    CASE
        WHEN ref_agency_yearly.agency_status = 'D'::bpchar THEN ref_agency_yearly.data_year
        ELSE NULL::smallint
    END AS dormant_year,
    ref_agency.ucr_agency_name,
    ref_agency.ncic_agency_name,
    ref_agency.pub_agency_name,
    ref_agency.pub_agency_unit,
    ref_agency_yearly.is_direct_contributor AS direct_contributor_flag,
    ref_agency_type.name AS agency_type_name,
    ref_agency.state_id,
    ref_state.name AS state_name,
    ref_state.abbr AS state_abbr,
    ref_state.postal_abbr AS state_postal_abbr,
    ref_agency_yearly.population,
    ref_division.code AS division_code,
    ref_division.name AS division_name,
    ref_region.code AS region_code,
    ref_region.name AS region_name,
    ref_region.description AS region_desc,
    ref_agency.submitting_agency_id,
    ref_submitting_agency.sai,
    CASE
        WHEN ref_agency_yearly.is_suburban_area IS TRUE THEN 'Y'::text
        WHEN ref_agency_yearly.is_suburban_area IS FALSE THEN 'N'::text
        ELSE ' '::text
    END AS suburban_area_flag,
    ref_agency_yearly.population_group_id,
    ref_population_group.code AS population_group_code,
    ref_population_group.description AS population_group_desc,
    ref_parent_population_group.code AS parent_pop_group_code,
    ref_parent_population_group.description AS parent_pop_group_desc,
    ref_submitting_agency.nibrs_cert_date,
    ref_agency.nibrs_start_date,
    ref_agency.nibrs_leoka_start_date,
    ref_agency.nibrs_ct_start_date,
    ref_agency.nibrs_multi_bias_start_date,
    ref_agency.nibrs_off_eth_start_date,
    string_agg(ref_county.name::text, '; '::text ORDER BY (ref_county.name::text)) AS county_name,
    string_agg(ref_msa.name::text, '; '::text ORDER BY (ref_msa.name::text)) AS msa_name,
    CASE
        WHEN ref_agency_yearly.is_publishable IS TRUE THEN 'Y'::text
        WHEN ref_agency_yearly.is_publishable IS FALSE THEN 'N'::text
        ELSE ' '::text
    END AS publishable_flag,
    CASE
        WHEN ref_agency_yearly.is_nibrs IS TRUE THEN 'Y'::text
        WHEN ref_agency_yearly.is_nibrs IS FALSE THEN 'N'::text
        ELSE ' '::text
    END AS nibrs_participated
	 FROM ucr_prd.ref_agency_yearly ref_agency_yearly
	   LEFT JOIN ucr_prd.ref_agency ref_agency USING (agency_id)
	   LEFT JOIN ucr_prd.ref_state USING (state_id)
     LEFT JOIN ucr_prd.ref_division USING (division_id)
     LEFT JOIN ucr_prd.ref_region USING (region_id)
	   LEFT JOIN ucr_prd.ref_agency_status ref_agency_status USING (agency_id, data_year)
	   LEFT JOIN ucr_prd.ref_submitting_agency USING (agency_id)
     LEFT JOIN ucr_prd.ref_agency_type USING (agency_type_id)
     LEFT JOIN ucr_prd.ref_population_group USING (population_group_id)
     LEFT JOIN ucr_prd.ref_parent_population_group USING (parent_pop_group_id)
     LEFT JOIN ucr_prd.ref_agency_county USING (agency_id, data_year)
     LEFT JOIN ucr_prd.ref_county USING (county_id)
     LEFT JOIN ucr_prd.ref_metro_division USING (metro_div_id)
     LEFT JOIN ucr_prd.ref_msa USING (msa_id)
	 WHERE ref_agency_status.data_year IS NOT NULL AND ref_agency_yearly.is_nibrs IS TRUE
	 GROUP BY ref_agency_type.name, ref_agency.agency_type_id, ref_agency.pub_agency_unit, ref_agency.nibrs_ct_start_date, ref_agency.ori, ref_agency.agency_id, ref_agency.nibrs_off_eth_start_date, ref_agency.submitting_agency_id, ref_agency.ucr_agency_name, ref_agency.legacy_ori, ref_agency.nibrs_multi_bias_start_date, ref_agency.ncic_agency_name, ref_agency.nibrs_leoka_start_date, ref_agency.pub_agency_name, ref_agency.state_id, ref_agency.nibrs_start_date, ref_agency.judicial_district_code, ref_agency.tribe_id, ref_agency.department_id, ref_agency.legacy_notify_agency, ref_agency.city_id, ref_agency.special_mailing_group, ref_agency.population_family_id, ref_agency.campus_id, ref_agency.nibrs_leoka_except_flag, ref_agency.fid_code, ref_agency.field_office_id, ref_agency.tribal_district_id, ref_agency.added_date, ref_agency.special_mailing_address, ref_state.postal_abbr, ref_state.abbr, ref_state.name, ref_agency_status.agency_status, ref_agency_status.data_year, ref_submitting_agency.sai, ref_submitting_agency.nibrs_cert_date, ref_agency_yearly.is_direct_contributor, ref_agency_yearly.is_nibrs, ref_agency_yearly.agency_status, ref_agency_yearly.population_group_id, (
        CASE
            WHEN ref_agency_yearly.is_publishable IS TRUE THEN 'Y'::text
            WHEN ref_agency_yearly.is_publishable IS FALSE THEN 'N'::text
            ELSE ' '::text
        END), (
        CASE
            WHEN ref_agency_yearly.is_nibrs IS TRUE THEN 'Y'::text
            WHEN ref_agency_yearly.is_nibrs IS FALSE THEN 'N'::text
            ELSE ' '::text
        END), ref_population_group.code, ref_population_group.description, ref_parent_population_group.code, ref_parent_population_group.description, (
        CASE
            WHEN ref_agency_yearly.is_covered IS TRUE THEN 'Y'::text
            WHEN ref_agency_yearly.is_covered IS FALSE THEN 'N'::text
            ELSE ' '::text
        END), ref_agency_yearly.population, (
        CASE
            WHEN ref_agency_yearly.agency_status = 'D'::bpchar THEN 'Y'::text
            ELSE 'N'::text
        END), (
        CASE
            WHEN ref_agency_yearly.agency_status = 'D'::bpchar THEN ref_agency_yearly.data_year
            ELSE NULL::smallint
        END), ref_division.code, ref_division.name, ref_region.code, ref_region.name, ref_region.description, (
        CASE
            WHEN ref_agency_yearly.is_suburban_area IS TRUE THEN 'Y'::text
            WHEN ref_agency_yearly.is_suburban_area IS FALSE THEN 'N'::text
            ELSE ' '::text
        END)
  ) agencies 
      ON ((nibrs_incident.agency_id = agencies.agency_id) AND (EXTRACT(year FROM nibrs_incident.incident_date) = agencies.data_year))
  LEFT JOIN ucr_prd.nibrs_victim USING (incident_id)
  LEFT JOIN ucr_prd.nibrs_victim_offense USING (victim_id)
  LEFT JOIN ucr_prd.nibrs_offense USING (incident_id, offense_id)
  LEFT JOIN ucr_prd.lkup_nibrs_offense USING (offense_code)
 WHERE nibrs_victim.victim_type_code = 'L' AND ",  state_year_where)
leoka_offense_df <- time_query(con, query_leoka_offense)
leoka_offense_df %>% write_csv(gzfile(paste0(queried_data_path,"raw_leoka_offense_",INPUT_STATE,".csv.gz")), na="")

query_clearance <- paste0("
 SELECT
  agencies.ori AS ori,
  EXTRACT(year FROM nibrs_incident.incident_date) as data_year,
  nibrs_incident.incident_id AS incident_id,
  agencies.state_id AS state_id,
  agencies.state_name AS state_name,
  agencies.state_abbr AS state_abbr,
  agencies.state_postal_abbr AS state_postal_abbr,
  nibrs_incident.cleared_exceptionally_code AS cleared_except_code,
  nibrs_cleared_except.name as cleared_except_name,
  nibrs_cleared_except.description as cleared_except_desc
 FROM ucr_prd.nibrs_incident
	LEFT JOIN (
	 SELECT
    ref_agency.ori,
    ref_agency.legacy_ori,
    ref_agency_status.data_year,
    ref_agency.agency_id,
    ref_agency_status.agency_status,
    ref_agency.state_id,
    ref_state.name AS state_name,
    ref_state.abbr AS state_abbr,
    ref_state.postal_abbr AS state_postal_abbr,
    ref_agency_yearly.population 
	 FROM ucr_prd.ref_agency_yearly ref_agency_yearly
	   LEFT JOIN ucr_prd.ref_agency ref_agency USING (agency_id)
	   LEFT JOIN ucr_prd.ref_state USING (state_id)
	   LEFT JOIN ucr_prd.ref_agency_status ref_agency_status USING (agency_id, data_year)
	   LEFT JOIN ucr_prd.ref_submitting_agency USING (agency_id)
     LEFT JOIN ucr_prd.ref_agency_type USING (agency_type_id)
	 WHERE ref_agency_status.data_year IS NOT NULL AND ref_agency_yearly.is_nibrs IS TRUE
  ) agencies 
      ON ((nibrs_incident.agency_id = agencies.agency_id) AND (EXTRACT(year FROM nibrs_incident.incident_date) = agencies.data_year))
  LEFT JOIN ucr_prd.lkup_nibrs_cleared_exceptionally nibrs_cleared_except ON (nibrs_incident.cleared_exceptionally_code = nibrs_cleared_except.cleared_exceptionally_code)
 WHERE ", state_year_where)
clearance_df <- time_query(con, query_clearance)
clearance_df %>% write_csv(gzfile(paste0(der_bystate_file_path,"raw_clearance_",INPUT_STATE,".csv.gz")), na="")

query_gang <- paste0("
SELECT
  agencies.ori AS ori,
  EXTRACT(year FROM nibrs_incident.incident_date) as data_year,
  nibrs_incident.incident_id AS incident_id,
  agencies.state_id AS state_id,
  agencies.state_name AS state_name,
  agencies.state_abbr AS state_abbr,
  agencies.state_postal_abbr AS state_postal_abbr,
  nibrs_criminal_act.criminal_activity_code as criminal_act_code,
  nibrs_criminal_act_type.name as criminal_act_name,
  nibrs_criminal_act_type.description as criminal_act_desc,
  nibrs_offense.offense_id
FROM ucr_prd.nibrs_incident
	LEFT JOIN (
	 SELECT
    ref_agency.ori,
    ref_agency.legacy_ori,
    ref_agency_status.data_year,
    ref_agency.agency_id,
    ref_agency_status.agency_status,
    ref_agency.state_id,
    ref_state.name AS state_name,
    ref_state.abbr AS state_abbr,
    ref_state.postal_abbr AS state_postal_abbr,
    ref_agency_yearly.population 
	 FROM ucr_prd.ref_agency_yearly ref_agency_yearly
	   LEFT JOIN ucr_prd.ref_agency ref_agency USING (agency_id)
	   LEFT JOIN ucr_prd.ref_state USING (state_id)
	   LEFT JOIN ucr_prd.ref_agency_status ref_agency_status USING (agency_id, data_year)
	   LEFT JOIN ucr_prd.ref_submitting_agency USING (agency_id)
     LEFT JOIN ucr_prd.ref_agency_type USING (agency_type_id)
	 WHERE ref_agency_status.data_year IS NOT NULL AND ref_agency_yearly.is_nibrs IS TRUE
  ) agencies 
      ON ((nibrs_incident.agency_id = agencies.agency_id) AND (EXTRACT(year FROM nibrs_incident.incident_date) = agencies.data_year))
  LEFT JOIN ucr_prd.nibrs_offense nibrs_offense ON (nibrs_incident.incident_id = nibrs_offense.incident_id)
  LEFT JOIN ucr_prd.nibrs_criminal_activity nibrs_criminal_act ON (nibrs_criminal_act.offense_id = nibrs_offense.offense_id)
  LEFT JOIN ucr_prd.lkup_nibrs_criminal_activity nibrs_criminal_act_type ON (nibrs_criminal_act_type.criminal_activity_code = nibrs_criminal_act.criminal_activity_code)
 WHERE ", state_year_where)
gang_df <- time_query(con, query_gang)
gang_df %>% write_csv(gzfile(paste0(der_bystate_file_path,"raw_gang_",INPUT_STATE,".csv.gz")), na="")

query_gang_offense <- paste0("
SELECT
  agencies.ori AS ori,
  EXTRACT(year FROM nibrs_incident.incident_date) as data_year,
  nibrs_incident.incident_id AS incident_id,
  nibrs_victim.victim_id,
  nibrs_offense.offense_id,
  agencies.state_id AS state_id,
  agencies.state_name AS state_name,
  agencies.state_abbr AS state_abbr,
  agencies.state_postal_abbr AS state_postal_abbr,
  nibrs_criminal_act.criminal_activity_code as criminal_act_code,
  nibrs_criminal_act_type.name as criminal_act_name,
  nibrs_criminal_act_type.description as criminal_act_desc
FROM ucr_prd.nibrs_incident
	LEFT JOIN (
	 SELECT
    ref_agency.ori,
    ref_agency.legacy_ori,
    ref_agency_status.data_year,
    ref_agency.agency_id,
    ref_agency_status.agency_status,
    ref_agency.state_id,
    ref_state.name AS state_name,
    ref_state.abbr AS state_abbr,
    ref_state.postal_abbr AS state_postal_abbr,
    ref_agency_yearly.population 
	 FROM ucr_prd.ref_agency_yearly ref_agency_yearly
	   LEFT JOIN ucr_prd.ref_agency ref_agency USING (agency_id)
	   LEFT JOIN ucr_prd.ref_state USING (state_id)
	   LEFT JOIN ucr_prd.ref_agency_status ref_agency_status USING (agency_id, data_year)
	   LEFT JOIN ucr_prd.ref_submitting_agency USING (agency_id)
     LEFT JOIN ucr_prd.ref_agency_type USING (agency_type_id)
	 WHERE ref_agency_status.data_year IS NOT NULL AND ref_agency_yearly.is_nibrs IS TRUE
  ) agencies 
      ON ((nibrs_incident.agency_id = agencies.agency_id) AND (EXTRACT(year FROM nibrs_incident.incident_date) = agencies.data_year))
  LEFT JOIN ucr_prd.nibrs_victim nibrs_victim ON (nibrs_incident.incident_id = nibrs_victim.incident_id)
  LEFT JOIN ucr_prd.nibrs_victim_offense nibrs_victim_offense ON (nibrs_victim.victim_id = nibrs_victim_offense.victim_id)
  LEFT JOIN ucr_prd.nibrs_offense nibrs_offense ON (nibrs_victim_offense.offense_id = nibrs_offense.offense_id)
  LEFT JOIN ucr_prd.nibrs_criminal_activity nibrs_criminal_act ON (nibrs_criminal_act.offense_id = nibrs_offense.offense_id)
  LEFT JOIN ucr_prd.lkup_nibrs_criminal_activity nibrs_criminal_act_type ON (nibrs_criminal_act_type.criminal_activity_code = nibrs_criminal_act.criminal_activity_code)
  WHERE ", state_year_where)
gang_offense_df <- time_query(con, query_gang_offense)
gang_offense_df %>% write_csv(gzfile(paste0(der_bystate_file_path,"raw_gang_offense_",INPUT_STATE,".csv.gz")), na="")


query_location <- paste0("
 SELECT
  agencies.ori AS ori,
  extract(year FROM nibrs_incident.incident_date) AS data_year,
  nibrs_incident.incident_id AS incident_id, 
  agencies.state_id AS state_id,
  agencies.state_name AS state_name,
  agencies.state_abbr AS state_abbr,
  agencies.state_postal_abbr AS state_postal_abbr,
  nibrs_offense.location_code,
  nibrs_location_type.name as location_name,
  nibrs_offense.offense_id
FROM ucr_prd.nibrs_incident nibrs_incident
  LEFT JOIN (
	SELECT
	  ref_agency.ori,
	  ref_agency.legacy_ori,
	  ref_agency_type.name as agency_type_name,
	  ref_agency.agency_id,
	  ref_agency.nibrs_start_date,
	  ref_agency_status.data_year,
	  ref_agency_status.agency_status,
	  ref_agency_yearly.is_nibrs,
	  ref_agency.state_id,
	  ref_state.name as state_name,
	  ref_state.abbr as state_abbr,
	  ref_state.postal_abbr as state_postal_abbr,
	  CASE
            WHEN ref_agency_yearly.is_covered IS TRUE THEN 'Y'::text
            WHEN ref_agency_yearly.is_covered IS FALSE THEN 'N'::text
            ELSE ' '::text
        END AS covered_flag,
      CASE
            WHEN ref_agency_yearly.agency_status = 'D'::bpchar THEN 'Y'::text
            ELSE 'N'::text
        END AS dormant_flag
	FROM ucr_prd.ref_agency_yearly ref_agency_yearly
	LEFT JOIN ucr_prd.ref_agency ref_agency USING (agency_id)
	LEFT JOIN ucr_prd.ref_state USING (state_id)
	LEFT JOIN ucr_prd.ref_agency_status ref_agency_status USING (agency_id, data_year)
	LEFT JOIN ucr_prd.ref_agency_type USING (agency_type_id)
	WHERE ref_agency_status.data_year IS NOT NULL AND ref_agency_yearly.is_nibrs IS TRUE
) agencies 
 	ON ((nibrs_incident.agency_id = agencies.agency_id) AND (EXTRACT(year FROM nibrs_incident.incident_date) = agencies.data_year))
  LEFT JOIN ucr_prd.nibrs_offense nibrs_offense ON (nibrs_incident.incident_id = nibrs_offense.incident_id)
  LEFT JOIN ucr_prd.lkup_nibrs_location nibrs_location_type ON (nibrs_location_type.location_code = nibrs_offense.location_code)
 WHERE ", state_year_where)
location_df <- time_query(con, query_location)
location_df %>% write_csv(gzfile(paste0(der_bystate_file_path,"raw_location_",INPUT_STATE,".csv.gz")), na="")


query_drug_by_drug_type_and_activity <- paste0("
 SELECT
  agencies.ori AS ori,
  agencies.legacy_ori AS legacy_ori,
  extract(year FROM incident_date) as data_year,
  nibrs_incident.incident_id AS incident_id,
  agencies.agency_status,
  agencies.covered_flag,
  agencies.dormant_flag,
  agencies.agency_type_name,
  agencies.state_id AS state_id,
  agencies.state_name AS state_name,
  agencies.state_abbr AS state_abbr,
  agencies.state_postal_abbr AS state_postal_abbr,
  nibrs_offense_type.offense_code AS offense_code,
  nibrs_offense_type.name AS offense_name,
  nibrs_offense_type.crime_against AS crime_against,
  nibrs_offense_type.category_name AS offense_category_name,
  nibrs_offense_type.offense_group AS offense_group,
  nibrs_suspected_drug.drug_code AS suspected_drug_code,
  nibrs_suspected_drug_type.name AS suspected_drug_name,
  nibrs_criminal_act.criminal_activity_code AS criminal_act_code,
  nibrs_criminal_act_type_lkup.name AS criminal_act_name,
  nibrs_criminal_act_type_lkup.description AS criminal_act_desc
FROM ucr_prd.nibrs_incident nibrs_incident
  LEFT JOIN (
	SELECT
	  ref_agency.ori,
	  ref_agency.legacy_ori,
	  ref_agency_type.name as agency_type_name,
	  ref_agency.agency_id,
	  ref_agency.nibrs_start_date,
	  ref_agency_status.data_year,
	  ref_agency_status.agency_status,
	  ref_agency_yearly.is_nibrs,
	  ref_agency.state_id,
	  ref_state.name as state_name,
	  ref_state.abbr as state_abbr,
	  ref_state.postal_abbr as state_postal_abbr,
	  CASE
            WHEN ref_agency_yearly.is_covered IS TRUE THEN 'Y'::text
            WHEN ref_agency_yearly.is_covered IS FALSE THEN 'N'::text
            ELSE ' '::text
        END AS covered_flag,
      CASE
            WHEN ref_agency_yearly.agency_status = 'D'::bpchar THEN 'Y'::text
            ELSE 'N'::text
        END AS dormant_flag
	FROM ucr_prd.ref_agency_yearly ref_agency_yearly
	LEFT JOIN ucr_prd.ref_agency ref_agency USING (agency_id)
	LEFT JOIN ucr_prd.ref_state USING (state_id)
	LEFT JOIN ucr_prd.ref_agency_status ref_agency_status USING (agency_id, data_year)
	LEFT JOIN ucr_prd.ref_agency_type USING (agency_type_id)
	WHERE ref_agency_status.data_year IS NOT NULL AND ref_agency_yearly.is_nibrs IS TRUE
) agencies 
 	ON ((nibrs_incident.agency_id = agencies.agency_id) AND (EXTRACT(year FROM nibrs_incident.incident_date) = agencies.data_year))
  LEFT JOIN ucr_prd.nibrs_offense nibrs_offense ON (nibrs_incident.incident_id = nibrs_offense.incident_id)
  LEFT JOIN ucr_prd.lkup_nibrs_offense nibrs_offense_type ON (nibrs_offense.offense_code = nibrs_offense_type.offense_code)
  LEFT JOIN ucr_prd.nibrs_property nibrs_property ON (nibrs_incident.incident_id = nibrs_property.incident_id)
  LEFT JOIN ucr_prd.nibrs_property_description nibrs_property_desc ON (nibrs_property.property_id = nibrs_property_desc.property_id)
  LEFT JOIN ucr_prd.lkup_nibrs_property_description nibrs_prop_desc_type ON (nibrs_property_desc.prop_desc_code = nibrs_prop_desc_type.prop_desc_code)
  LEFT JOIN ucr_prd.lkup_nibrs_property_loss nibrs_prop_loss_type ON (nibrs_property.prop_loss_code = nibrs_prop_loss_type.prop_loss_code)
  LEFT JOIN ucr_prd.nibrs_suspected_drug nibrs_suspected_drug ON (nibrs_property.property_id = nibrs_suspected_drug.property_id)
  LEFT JOIN ucr_prd.lkup_nibrs_drug nibrs_suspected_drug_type ON (nibrs_suspected_drug.drug_code = nibrs_suspected_drug_type.drug_code)
  LEFT JOIN ucr_prd.nibrs_criminal_activity nibrs_criminal_act ON (nibrs_offense.offense_id = nibrs_criminal_act.offense_id)
  LEFT JOIN ucr_prd.lkup_nibrs_criminal_activity nibrs_criminal_act_type_lkup ON (nibrs_criminal_act.criminal_activity_code = nibrs_criminal_act_type_lkup.criminal_activity_code)
 WHERE trim(upper(nibrs_offense_type.offense_code)) in ('35A', '35B') and ", state_year_where)
drug_by_drug_type_and_activity_df <- time_query(con, query_drug_by_drug_type_and_activity)
drug_by_drug_type_and_activity_df %>% 
  write_csv(gzfile(paste0(der_bystate_file_path,"raw_all_Offenses_recoded_incident_drug_activity_",INPUT_STATE,".csv.gz")), na="")

query_injury <- paste0("
 SELECT
  agencies.ori AS ori,
  extract(year FROM incident_date) as data_year,
  nibrs_incident.incident_id AS incident_id,
  nibrs_victim.victim_id,
  agencies.state_id AS state_id,
  agencies.state_name AS state_name,
  agencies.state_abbr AS state_abbr,
  agencies.state_postal_abbr AS state_postal_abbr,
  nibrs_injury.injury_code,
  lkup_nibrs_injury.name as injury_name
 FROM ucr_prd.nibrs_incident
	LEFT JOIN (
	  SELECT
	   ref_agency.ori,
	   ref_agency.agency_id,
	   ref_agency_status.data_year,
	   ref_agency_status.agency_status,
	   ref_agency_yearly.is_nibrs,
	   ref_state.state_id,
     ref_state.name AS state_name,
     ref_state.abbr AS state_abbr,
     ref_state.postal_abbr AS state_postal_abbr
	  FROM ucr_prd.ref_agency_yearly ref_agency_yearly
	   LEFT JOIN ucr_prd.ref_agency ref_agency USING (agency_id)
	   LEFT JOIN ucr_prd.ref_state USING (state_id)
	   LEFT JOIN ucr_prd.ref_agency_status ref_agency_status USING (agency_id, data_year)
	  WHERE ref_agency_status.data_year IS NOT NULL AND ref_agency_yearly.is_nibrs IS TRUE
	) agencies 
         ON ((nibrs_incident.agency_id = agencies.agency_id) AND (EXTRACT(year FROM nibrs_incident.incident_date) = agencies.data_year))
  LEFT JOIN ucr_prd.nibrs_victim nibrs_victim ON (nibrs_incident.incident_id = nibrs_victim.incident_id)
  LEFT JOIN ucr_prd.nibrs_victim_injury nibrs_injury ON (nibrs_victim.victim_id = nibrs_injury.victim_id)
  LEFT JOIN ucr_prd.lkup_nibrs_injury lkup_nibrs_injury ON (nibrs_injury.injury_code = lkup_nibrs_injury.injury_code)
 WHERE ", state_year_where)
injury_df <- time_query(con, query_injury)
injury_df %>% write_csv(gzfile(paste0(der_bystate_file_path,"raw_Injury_",INPUT_STATE,".csv.gz")), na="")

### tasks/generate_estimates/Setup_part1_bystate/00_Create_Datasets_full_Drug_Module.Rmd ####
query_incidents <- paste0("
 SELECT 
  agencies.ori,
  agencies.legacy_ori,
  EXTRACT(year FROM nibrs_incident.incident_date) AS data_year,
  nibrs_incident.incident_id,
  nibrs_offense.offense_id,
  agencies.agency_status,
  agencies.covered_flag,
  agencies.dormant_flag,
  agencies.agency_type_name,
  agencies.state_id AS state_id,
  agencies.state_name AS state_name,
  agencies.state_abbr AS state_abbr,
  agencies.state_postal_abbr AS state_postal_abbr,
  nibrs_offense.offense_code,
  lkup_nibrs_offense.name AS offense_name,
  lkup_nibrs_offense.crime_against,
  lkup_nibrs_offense.category_name AS offense_category_name,
  lkup_nibrs_offense.offense_group,
  nibrs_offense.attempt_complete_code AS attempt_complete_flag
 FROM ucr_prd.nibrs_incident
	LEFT JOIN (
   SELECT
    ref_agency.ori,
    ref_agency.legacy_ori,
    ref_agency_status.data_year,
    ref_agency.agency_id,
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
    ref_agency_type.name AS agency_type_name,
    ref_agency.state_id,
    ref_state.name AS state_name,
    ref_state.abbr AS state_abbr,
    ref_state.postal_abbr AS state_postal_abbr,
    ref_agency_yearly.population 
	 FROM ucr_prd.ref_agency_yearly ref_agency_yearly
	   LEFT JOIN ucr_prd.ref_agency ref_agency USING (agency_id)
	   LEFT JOIN ucr_prd.ref_state USING (state_id)
	   LEFT JOIN ucr_prd.ref_agency_status ref_agency_status USING (agency_id, data_year)
	   LEFT JOIN ucr_prd.ref_submitting_agency USING (agency_id)
     LEFT JOIN ucr_prd.ref_agency_type USING (agency_type_id)
	  WHERE ref_agency_status.data_year IS NOT NULL AND ref_agency_yearly.is_nibrs IS TRUE
  ) agencies 
      ON ((nibrs_incident.agency_id = agencies.agency_id) AND (EXTRACT(year FROM nibrs_incident.incident_date) = agencies.data_year))
  LEFT JOIN ucr_prd.nibrs_offense USING (incident_id)
  LEFT JOIN ucr_prd.lkup_nibrs_offense USING (offense_code)
 WHERE ", state_year_where)
incidents_df <- time_query(con, query_incidents)
incidents_df %>% write_csv(gzfile(paste0(queried_data_path,"incidents_",INPUT_STATE,".csv.gz")), na="")

query_criminal_activity <- paste0("
 SELECT 
  agencies.ori,
  agencies.state_abbr,
  nibrs_incident.incident_id,
  nibrs_offense.attempt_complete_code AS attempt_complete_flag,
  lkup_nibrs_offense.name AS offense_name,
  nibrs_offense.offense_code,
  nibrs_criminal_activity.criminal_activity_code AS criminal_act_code,
  lkup_nibrs_criminal_activity.name AS criminal_act_name,
  EXTRACT(year FROM nibrs_incident.incident_date) AS data_year,
  nibrs_offense.offense_id AS offense_id
 FROM ucr_prd.nibrs_incident
	LEFT JOIN (
   SELECT
    ref_agency.ori,
    ref_agency.legacy_ori,
    ref_agency_status.data_year,
    ref_agency.agency_id,
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
    ref_agency_type.name AS agency_type_name,
    ref_agency.state_id,
    ref_state.name AS state_name,
    ref_state.abbr AS state_abbr,
    ref_state.postal_abbr AS state_postal_abbr,
    ref_agency_yearly.population 
	 FROM ucr_prd.ref_agency_yearly ref_agency_yearly
	   LEFT JOIN ucr_prd.ref_agency ref_agency USING (agency_id)
	   LEFT JOIN ucr_prd.ref_state USING (state_id)
	   LEFT JOIN ucr_prd.ref_agency_status ref_agency_status USING (agency_id, data_year)
	   LEFT JOIN ucr_prd.ref_submitting_agency USING (agency_id)
     LEFT JOIN ucr_prd.ref_agency_type USING (agency_type_id)
	  WHERE ref_agency_status.data_year IS NOT NULL AND ref_agency_yearly.is_nibrs IS TRUE
  ) agencies 
      ON ((nibrs_incident.agency_id = agencies.agency_id) AND (EXTRACT(year FROM nibrs_incident.incident_date) = agencies.data_year))
  LEFT JOIN ucr_prd.nibrs_offense USING (incident_id)
  LEFT JOIN ucr_prd.lkup_nibrs_offense USING (offense_code)
  LEFT JOIN ucr_prd.nibrs_criminal_activity USING (offense_id)
  LEFT JOIN ucr_prd.lkup_nibrs_criminal_activity USING (criminal_activity_code)
  WHERE ", state_year_where)
criminal_activity_df <- time_query(con, query_criminal_activity)
criminal_activity_df %>% write_csv(gzfile(paste0(queried_data_path,"criminal_activity_",INPUT_STATE,".csv.gz")), na="")

query_drug_by_drug_type <- paste0("
 SELECT
  agencies.ori AS ori,
  agencies.state_abbr as state_abbr,
  nibrs_incident.incident_id AS incident_id,
  nibrs_prop_loss_type.description AS prop_loss_desc,
  nibrs_prop_loss_type.name AS prop_loss_name,
  nibrs_property_desc.prop_desc_code,
  nibrs_property_desc_lkup.name as prop_desc_name,
  nibrs_suspected_drug.drug_measure_code AS drug_measure_code,
  nibrs_suspected_drug.est_drug_qty AS est_drug_qty,
  nibrs_suspected_drug.drug_code AS suspected_drug_code,
  lkup_nibrs_drug.name AS suspected_drug_name
 FROM ucr_prd.nibrs_incident
	LEFT JOIN (
	 SELECT
    ref_agency.ori,
    ref_agency.legacy_ori,
    ref_agency_status.data_year,
    ref_agency.agency_id,
    ref_agency_status.agency_status,
    ref_agency.state_id,
    ref_state.name AS state_name,
    ref_state.abbr AS state_abbr,
    ref_state.postal_abbr AS state_postal_abbr,
    ref_agency_yearly.population 
	 FROM ucr_prd.ref_agency_yearly ref_agency_yearly
	   LEFT JOIN ucr_prd.ref_agency ref_agency USING (agency_id)
	   LEFT JOIN ucr_prd.ref_state USING (state_id)
	   LEFT JOIN ucr_prd.ref_agency_status ref_agency_status USING (agency_id, data_year)
	   LEFT JOIN ucr_prd.ref_submitting_agency USING (agency_id)
     LEFT JOIN ucr_prd.ref_agency_type USING (agency_type_id)
	 WHERE ref_agency_status.data_year IS NOT NULL AND ref_agency_yearly.is_nibrs IS TRUE
  ) agencies 
      ON ((nibrs_incident.agency_id = agencies.agency_id) AND (EXTRACT(year FROM nibrs_incident.incident_date) = agencies.data_year))
  LEFT JOIN ucr_prd.nibrs_property nibrs_property ON (nibrs_incident.incident_id = nibrs_property.incident_id)
  LEFT JOIN ucr_prd.nibrs_property_description nibrs_property_desc ON (nibrs_property.property_id = nibrs_property_desc.property_id)
  LEFT JOIN ucr_prd.lkup_nibrs_property_description nibrs_property_desc_lkup ON (nibrs_property_desc.prop_desc_code = nibrs_property_desc_lkup.prop_desc_code)
  LEFT JOIN ucr_prd.lkup_nibrs_property_loss nibrs_prop_loss_type ON (nibrs_property.prop_loss_code = nibrs_prop_loss_type.prop_loss_code)
  LEFT JOIN ucr_prd.nibrs_suspected_drug nibrs_suspected_drug ON (nibrs_property.property_id = nibrs_suspected_drug.property_id)
  LEFT JOIN ucr_prd.lkup_nibrs_drug ON (nibrs_suspected_drug.drug_code = lkup_nibrs_drug.drug_code)
 WHERE ", state_year_where)
drug_by_drug_type_df <- time_query(con, query_drug_by_drug_type)
drug_by_drug_type_df %>% write_csv(gzfile(paste0(queried_data_path,"drug_incidents_by_drug_type_",INPUT_STATE,".csv.gz")), na="")

query_drug_offense <- paste0("
 SELECT
  agencies.ori,
	agencies.state_abbr,
	nibrs_incident.incident_id,
	nibrs_offense.attempt_complete_code AS attempt_complete_flag,
	nibrs_offense.offense_code AS offense_code,
	nibrs_criminal_activity.criminal_activity_code AS criminal_act_code,
  lkup_nibrs_criminal_activity.name AS criminal_act_name,
	EXTRACT(year FROM nibrs_incident.incident_date) AS data_year,
 	nibrs_offense.offense_id,
  lkup_nibrs_offense.name AS offense_name,
  lkup_nibrs_offense.crime_against,
  lkup_nibrs_offense.category_name AS offense_category_name,
  lkup_nibrs_offense.offense_group,
  nibrs_suspected_drug.drug_measure_code,
	nibrs_suspected_drug.est_drug_qty,
	nibrs_suspected_drug.drug_code AS suspected_drug_code,
  lkup_nibrs_drug.name AS suspected_drug_name
 FROM ucr_prd.nibrs_incident
	LEFT JOIN (
	 SELECT
    ref_agency.ori,
    ref_agency.legacy_ori,
    ref_agency_status.data_year,
    ref_agency.agency_id,
    ref_agency_status.agency_status,
    ref_agency.state_id,
    ref_state.name AS state_name,
    ref_state.abbr AS state_abbr,
    ref_state.postal_abbr AS state_postal_abbr,
    ref_agency_yearly.population 
	 FROM ucr_prd.ref_agency_yearly ref_agency_yearly
	   LEFT JOIN ucr_prd.ref_agency ref_agency USING (agency_id)
	   LEFT JOIN ucr_prd.ref_state USING (state_id)
	   LEFT JOIN ucr_prd.ref_agency_status ref_agency_status USING (agency_id, data_year)
	   LEFT JOIN ucr_prd.ref_submitting_agency USING (agency_id)
     LEFT JOIN ucr_prd.ref_agency_type USING (agency_type_id)
	 WHERE ref_agency_status.data_year IS NOT NULL AND ref_agency_yearly.is_nibrs IS TRUE
  ) agencies 
      ON ((nibrs_incident.agency_id = agencies.agency_id) AND (EXTRACT(year FROM nibrs_incident.incident_date) = agencies.data_year))
  LEFT JOIN ucr_prd.nibrs_offense USING (incident_id)
  LEFT JOIN ucr_prd.lkup_nibrs_offense USING (offense_code)
  LEFT JOIN ucr_prd.nibrs_criminal_activity USING (offense_id)
  LEFT JOIN ucr_prd.lkup_nibrs_criminal_activity USING (criminal_activity_code)
  LEFT JOIN ucr_prd.nibrs_property ON (nibrs_incident.incident_id = nibrs_property.incident_id)
  LEFT JOIN ucr_prd.nibrs_property_description ON (nibrs_property.property_id = nibrs_property_description.property_id)
  LEFT JOIN ucr_prd.nibrs_suspected_drug ON (nibrs_property.property_id = nibrs_suspected_drug.property_id)
  LEFT JOIN ucr_prd.lkup_nibrs_drug USING (drug_code)
 WHERE ", state_year_where)
drug_offense_df <- time_query(con, query_drug_offense)
drug_offense_df %>% write_csv(gzfile(paste0(queried_data_path,"drug_offense_by_drug_and_activity_",INPUT_STATE,".csv.gz")), na="")

### create_nibrs_extracts/extract_one_state/01_Extract_All.Rmd & generate_estimates/Setup_part1_bystate/00a_Create_Datasets_full.Rmd ####
query_arrestee <- paste0("
 SELECT 
  agencies.ori AS ori,
  EXTRACT(year FROM nibrs_incident.incident_date) AS data_year,
  nibrs_incident.incident_id AS incident_id,
  agencies.state_id,
  agencies.state_name,
  agencies.state_abbr,
  agencies.state_postal_abbr,
  nibrs_arrestee.arrestee_id AS arrestee_id,
  nibrs_arrestee.incident_id AS incident_id_arrestee,
  nibrs_arrestee.sequence_number AS arrestee_seq_num,
  nibrs_arrestee.arrest_date,
  nibrs_arrestee.multiple_indicator_code AS multiple_indicator,
  nibrs_arrestee.offense_code AS offense_type_code_arrestee,
  nibrs_arrestee.age_code AS age_code_arrestee,
  CASE
      WHEN nibrs_arrestee.age_code = ANY (ARRAY['NN'::bpchar, 'NB'::bpchar, 'BB'::bpchar, '00'::bpchar, 'NS'::bpchar, '99'::bpchar]) THEN NULL::bpchar
      ELSE nibrs_arrestee.age_code
  END AS age_num_arrestee,
  CASE
      WHEN nibrs_arrestee.sex_code = 'X'::bpchar THEN ' '::bpchar
      ELSE nibrs_arrestee.sex_code
  END AS sex_code_arrestee,
  CASE 
      WHEN nibrs_arrestee.race_code = '' THEN 'NA'
      ELSE nibrs_arrestee.race_code
  END AS race_code_arrestee,
  CASE
     WHEN nibrs_arrestee.ethnicity_code = 'X'::bpchar THEN ' '::bpchar
     ELSE nibrs_arrestee.ethnicity_code
  END AS ethnicity_code_arrestee,
  CASE
      WHEN nibrs_arrestee.resident_status_code IS NULL THEN ' '::bpchar
      ELSE nibrs_arrestee.resident_status_code
  END AS resident_code,
  CASE
      WHEN nibrs_arrestee.under_18_disposition_code IS NULL THEN ' '::bpchar
      ELSE nibrs_arrestee.under_18_disposition_code
  END AS under_18_disposition_code,
  nibrs_arrestee.age_code_range_low AS age_range_low_num_arrestee,
  nibrs_arrestee.age_code_range_high AS age_range_high_num_arrestee,
  nibrs_arrestee.arrest_type_code,
  lkup_nibrs_arrest_type.name as arrest_type_name
 FROM ucr_prd.nibrs_incident
	LEFT JOIN (
	  SELECT
	   ref_agency.ori,
	   ref_agency.agency_id,
	   ref_agency_status.data_year,
	   ref_agency_status.agency_status,
	   ref_agency_yearly.is_nibrs,
	   ref_state.state_id,
     ref_state.name AS state_name,
     ref_state.abbr AS state_abbr,
     ref_state.postal_abbr AS state_postal_abbr
	  FROM ucr_prd.ref_agency_yearly ref_agency_yearly
	   LEFT JOIN ucr_prd.ref_agency ref_agency USING (agency_id)
	   LEFT JOIN ucr_prd.ref_state USING (state_id)
	   LEFT JOIN ucr_prd.ref_agency_status ref_agency_status USING (agency_id, data_year)
	  WHERE ref_agency_status.data_year IS NOT NULL AND ref_agency_yearly.is_nibrs IS TRUE
	) agencies 
         ON ((nibrs_incident.agency_id = agencies.agency_id) AND (EXTRACT(year FROM nibrs_incident.incident_date) = agencies.data_year))
  LEFT JOIN ucr_prd.nibrs_arrestee nibrs_arrestee USING (incident_id)
  LEFT JOIN ucr_prd.lkup_nibrs_arrest_type USING (arrest_type_code)
 WHERE ", state_year_where)
arrestee_df <- time_query(con, query_arrestee)

arrestee_df %>% write_csv(gzfile(paste0(queried_data_path,"raw_arrestee_all_cols_",INPUT_STATE,".csv.gz")), na="")

arrestee_df %>% 
  select(ori, data_year, incident_id, state_id, state_name, state_abbr,
         state_postal_abbr, arrestee_id, arrestee_seq_num, age_code_arrestee,
         age_num_arrestee, sex_code_arrestee, race_code_arrestee,
         under_18_disposition_code, multiple_indicator) %>% 
  # rename to match original
  rename(arrestee_age_code=age_code_arrestee,
         arrestee_age_num=age_num_arrestee,
         arrestee_sex_code=sex_code_arrestee,
         arrestee_race_code=race_code_arrestee) %>% 
  write_csv(gzfile(paste0(der_bystate_file_path,"raw_arrestee_",INPUT_STATE,".csv.gz")), na="")

arrestee_df %>% 
  select(ori, data_year, incident_id, state_id, state_name, state_abbr, state_postal_abbr,
         arrestee_id, arrestee_seq_num, arrest_type_code, arrest_type_name) %>% 
  write_csv(gzfile(paste0(der_bystate_file_path,"raw_arrest_type_",INPUT_STATE,".csv.gz")), na="")

query_arrestee_weapon <- paste0("
 SELECT
  agencies.ori AS ori,
  EXTRACT(year FROM inc.incident_date) AS data_year,
  inc.incident_id AS incident_id,
  agencies.state_id AS state_id,
  agencies.state_name AS state_name,
  agencies.state_abbr AS state_abbr,
  agencies.state_postal_abbr AS state_postal_abbr,
  nibrs_arrestee_weapon.arrestee_id AS arrestee_id,
  lkup_weapon.weapon_code,
  lkup_weapon.name as weapon_name,
  CASE 
        WHEN lkup_weapon.used_for_shr = true THEN 'Y'
        WHEN lkup_weapon.used_for_shr = false THEN 'N'
        ELSE 'N'
  END AS shr_flag
 FROM ucr_prd.nibrs_incident inc
	LEFT JOIN (
	  SELECT
	   ref_agency.ori,
	   ref_agency.agency_id,
	   ref_agency.legacy_ori,
	   ref_agency.nibrs_start_date,
	   ref_agency_status.data_year,
	   ref_agency_yearly.is_nibrs,
	   ref_state.state_id,
     ref_state.name AS state_name,
     ref_state.abbr AS state_abbr,
     ref_state.postal_abbr AS state_postal_abbr
	  FROM ucr_prd.ref_agency_yearly ref_agency_yearly
	   LEFT JOIN ucr_prd.ref_agency ref_agency USING (agency_id)
	   LEFT JOIN ucr_prd.ref_state USING (state_id)
	   LEFT JOIN ucr_prd.ref_agency_status ref_agency_status USING (agency_id, data_year)
	  WHERE ref_agency_status.data_year IS NOT NULL AND ref_agency_yearly.is_nibrs IS TRUE
	) agencies 
         ON ((inc.agency_id = agencies.agency_id) AND (EXTRACT(year FROM inc.incident_date) = agencies.data_year))
 LEFT JOIN ucr_prd.nibrs_arrestee USING (incident_id)
 LEFT JOIN ucr_prd.nibrs_arrestee_weapon USING (arrestee_id)
 LEFT JOIN ucr_prd.lkup_weapon USING (weapon_code)
 WHERE ", state_year_where
)
arrestee_weapon_df <- time_query(con, query_arrestee_weapon)

arrestee_weapon_df %>% 
  select(data_year, incident_id, state_abbr, arrestee_id,
         weapon_code, weapon_name, shr_flag) %>% 
  mutate(shr_flag = ifelse(is.na(weapon_code), NA, shr_flag)) %>% 
  write_csv(gzfile(paste0(queried_data_path,"raw_arrestee_weapon_all_cols_",INPUT_STATE,".csv.gz")), na="")

arrestee_weapon_df %>% 
  select(ori, data_year, incident_id, state_id, state_name, state_abbr, 
         state_postal_abbr, arrestee_id, weapon_code, weapon_name) %>% 
  write_csv(gzfile(paste0(der_bystate_file_path,"raw_arrestee_weapon_",INPUT_STATE,".csv.gz")), na="")

query_bias <- paste0("
 SELECT
  agencies.ori AS ori,
  agencies.legacy_ori AS legacy_ori,
  EXTRACT(year FROM nibrs_incident.incident_date) AS data_year,
  nibrs_incident.incident_id AS incident_id,
  agencies.agency_status,
  agencies.covered_flag,
  agencies.dormant_flag,
  agencies.agency_type_name,
  agencies.state_id AS state_id,
  agencies.state_name AS state_name,
  agencies.state_abbr AS state_abbr,
  agencies.state_postal_abbr AS state_postal_abbr,
  nibrs_bias_motivation.offense_id AS offense_id,
  nibrs_bias_motivation.bias_code AS bias_code,
  lkup_bias.category AS bias_name,
  lkup_bias.description AS bias_desc
 FROM ucr_prd.nibrs_incident
	LEFT JOIN (
	 SELECT
    ref_agency.ori,
    ref_agency.legacy_ori,
    ref_agency_status.data_year,
    ref_agency.agency_id,
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
    ref_agency_type.name AS agency_type_name,
    ref_agency.state_id,
    ref_state.name AS state_name,
    ref_state.abbr AS state_abbr,
    ref_state.postal_abbr AS state_postal_abbr,
    ref_agency_yearly.population 
	 FROM ucr_prd.ref_agency_yearly ref_agency_yearly
	   LEFT JOIN ucr_prd.ref_agency ref_agency USING (agency_id)
	   LEFT JOIN ucr_prd.ref_state USING (state_id)
	   LEFT JOIN ucr_prd.ref_agency_status ref_agency_status USING (agency_id, data_year)
	   LEFT JOIN ucr_prd.ref_submitting_agency USING (agency_id)
     LEFT JOIN ucr_prd.ref_agency_type USING (agency_type_id)
	  WHERE ref_agency_status.data_year IS NOT NULL AND ref_agency_yearly.is_nibrs IS TRUE
  ) agencies 
      ON ((nibrs_incident.agency_id = agencies.agency_id) AND (EXTRACT(year FROM nibrs_incident.incident_date) = agencies.data_year))
  LEFT JOIN ucr_prd.nibrs_offense USING (incident_id)
  LEFT JOIN ucr_prd.nibrs_bias_motivation USING (offense_id)
  LEFT JOIN ucr_prd.lkup_bias USING (bias_code)
 WHERE ", state_year_where)
bias_df <- time_query(con, query_bias)

bias_df %>% 
  write_csv(gzfile(paste0(queried_data_path,"raw_bias_hate_crime_all_cols_",INPUT_STATE,".csv.gz")), na="")

bias_df %>% 
  select(-c(offense_id)) %>% 
  write_csv(gzfile(paste0(der_bystate_file_path,"raw_bias_hate_crime_",INPUT_STATE,".csv.gz")), na="")

query_offender <- paste0("
 SELECT 
  agencies.ori,
  EXTRACT(year FROM nibrs_incident.incident_date) AS data_year,
  nibrs_incident.incident_id AS incident_id,
  agencies.state_id,
  agencies.state_name,
  agencies.state_abbr,
  agencies.state_postal_abbr,
  nibrs_offender.offender_id,
  nibrs_offender.sequence_number AS offender_seq_num,
  nibrs_offender.incident_id AS incident_id_offender,
  nibrs_offender.age_code as offender_age_code,
  CASE
      WHEN nibrs_offender.age_code = ANY (ARRAY['NN'::bpchar, 'NB'::bpchar, 'BB'::bpchar, '00'::bpchar, 'NS'::bpchar, '99'::bpchar]) THEN NULL::bpchar
      ELSE nibrs_offender.age_code
  END AS offender_age_num,
  nibrs_offender.age_code_range_low AS age_range_low_num_offender,
  nibrs_offender.age_code_range_high AS age_range_high_num_offender,
  CASE
     WHEN nibrs_offender.sex_code = 'X'::bpchar THEN ' '::bpchar
     ELSE nibrs_offender.sex_code
  END AS sex_code_offender,
  CASE 
      WHEN nibrs_offender.race_code = '' THEN 'NA'
      ELSE nibrs_offender.race_code
  END AS race_code_offender,
  CASE
     WHEN nibrs_offender.ethnicity_code = 'X'::bpchar THEN ' '::bpchar
     ELSE nibrs_offender.ethnicity_code
  END AS ethnicity_code_offender
 FROM ucr_prd.nibrs_incident
	LEFT JOIN (
	  SELECT
	   ref_agency.ori,
	   ref_agency.agency_id,
	   ref_agency_status.data_year,
	   ref_agency_status.agency_status,
	   ref_agency_yearly.is_nibrs,
	   ref_state.state_id,
     ref_state.name AS state_name,
     ref_state.abbr AS state_abbr,
     ref_state.postal_abbr AS state_postal_abbr
	  FROM ucr_prd.ref_agency_yearly ref_agency_yearly
	   LEFT JOIN ucr_prd.ref_agency ref_agency USING (agency_id)
	   LEFT JOIN ucr_prd.ref_state USING (state_id)
	   LEFT JOIN ucr_prd.ref_agency_status ref_agency_status USING (agency_id, data_year)
	  WHERE ref_agency_status.data_year IS NOT NULL AND ref_agency_yearly.is_nibrs IS TRUE
	) agencies 
         ON ((nibrs_incident.agency_id = agencies.agency_id) AND (EXTRACT(year FROM nibrs_incident.incident_date) = agencies.data_year))
  LEFT JOIN ucr_prd.nibrs_offender nibrs_offender USING (incident_id)
 WHERE ", state_year_where)
offender_df <- time_query(con, query_offender)
offender_df %>% write_csv(gzfile(paste0(queried_data_path,"raw_offender_all_cols_",INPUT_STATE,".csv.gz")), na="")

offender_df %>% 
  select(ori, data_year, incident_id, state_id, state_name, state_abbr, state_postal_abbr,
         offender_id, offender_seq_num, offender_age_code, offender_age_num) %>% 
  write_csv(gzfile(paste0(der_bystate_file_path,"raw_offender_",INPUT_STATE,".csv.gz")), na="")

query_weapons <- paste0("
 SELECT
  agencies.ori AS ori,
  EXTRACT(year FROM nibrs_incident.incident_date) AS data_year,
  nibrs_incident.incident_id AS incident_id,
  nibrs_offense.offense_id AS offense_id,
  agencies.state_id,
  agencies.state_name,
  agencies.state_abbr,
  agencies.state_postal_abbr,
  nibrs_offense_weapon.offense_id AS nibrs_weapon_offense_id,
  lkup_weapon.weapon_code,
  lkup_weapon.name as weapon_name,
  CASE 
      WHEN used_for_shr = true THEN 'Y'
      WHEN used_for_shr = false THEN 'N'
      ELSE 'NA'
  END AS shr_flag
 FROM ucr_prd.nibrs_incident
	LEFT JOIN (
	  SELECT
	   ref_agency.ori,
	   ref_agency.agency_id,
	   ref_agency_status.data_year,
	   ref_agency_status.agency_status,
	   ref_agency_yearly.is_nibrs,
	   ref_state.state_id,
     ref_state.name AS state_name,
     ref_state.abbr AS state_abbr,
     ref_state.postal_abbr AS state_postal_abbr
	  FROM ucr_prd.ref_agency_yearly ref_agency_yearly
	   LEFT JOIN ucr_prd.ref_agency ref_agency USING (agency_id)
	   LEFT JOIN ucr_prd.ref_state USING (state_id)
	   LEFT JOIN ucr_prd.ref_agency_status ref_agency_status USING (agency_id, data_year)
	  WHERE ref_agency_status.data_year IS NOT NULL AND ref_agency_yearly.is_nibrs IS TRUE
	) agencies 
         ON ((nibrs_incident.agency_id = agencies.agency_id) AND (EXTRACT(year FROM nibrs_incident.incident_date) = agencies.data_year))
  LEFT JOIN ucr_prd.nibrs_offense USING (incident_id)
  LEFT JOIN ucr_prd.nibrs_offense_weapon USING (offense_id)
  LEFT JOIN ucr_prd.lkup_weapon USING (weapon_code)
 WHERE ", state_year_where)
weapons_df <- time_query(con, query_weapons)
weapons_df %>%
  mutate(shr_flag = ifelse(is.na(weapon_code), NA, shr_flag)) %>% 
  write_csv(gzfile(paste0(queried_data_path,"raw_weapon_all_cols_",INPUT_STATE,".csv.gz")), na="")

weapons_df %>%
  select(ori, data_year, incident_id, state_id, state_name, state_abbr, state_postal_abbr,
         weapon_code, weapon_name, offense_id) %>% 
  write_csv(gzfile(paste0(der_bystate_file_path,"raw_weapon_",INPUT_STATE,".csv.gz")), na="")

### generate_estimates/Setup_part1_bystate/00a_Create_Datasets_full.Rmd & 000a_Create_Extracts_Carjacking.Rmd ####
query_offenses <- paste0("
 SELECT 
  agencies.ori AS ori,
  agencies.legacy_ori AS legacy_ori,
  extract(year FROM incident_date) as data_year,
  nibrs_incident.incident_id AS incident_id,
  nibrs_victim.victim_id,
  nibrs_victim.victim_type_code,
  nibrs_offense.offense_id,
  agencies.state_id AS state_id,
  agencies.state_name AS state_name,
  agencies.state_abbr AS state_abbr,
  agencies.state_postal_abbr AS state_postal_abbr,
  agencies.agency_status,
  agencies.covered_flag,
  agencies.dormant_flag,
  agencies.agency_type_name,
  nibrs_victim_type.name AS victim_type_name,
  nibrs_victim.sex_code AS sex_code,
  nibrs_offense_type.offense_code AS offense_code,
  nibrs_offense_type.name AS offense_name,
  nibrs_offense_type.crime_against AS crime_against,
  nibrs_offense_type.category_name AS offense_category_name,
  nibrs_offense_type.offense_group AS offense_group,
  nibrs_offense.attempt_complete_code AS attempt_complete_code,
  nibrs_location.location_code,
  nibrs_location.name as location_name
 FROM ucr_prd.nibrs_incident nibrs_incident
  LEFT JOIN (
  	SELECT
  	  ref_agency.ori,
  	  ref_agency.legacy_ori,
  	  ref_agency_type.name as agency_type_name,
  	  ref_agency.agency_id,
  	  ref_agency.nibrs_start_date,
  	  ref_agency_status.data_year,
  	  ref_agency_status.agency_status,
  	  ref_agency_yearly.is_nibrs,
  	  ref_agency.state_id,
  	  ref_state.name as state_name,
  	  ref_state.abbr as state_abbr,
  	  ref_state.postal_abbr as state_postal_abbr,
  	  CASE
              WHEN ref_agency_yearly.is_covered IS TRUE THEN 'Y'::text
              WHEN ref_agency_yearly.is_covered IS FALSE THEN 'N'::text
              ELSE ' '::text
          END AS covered_flag,
        CASE
              WHEN ref_agency_yearly.agency_status = 'D'::bpchar THEN 'Y'::text
              ELSE 'N'::text
          END AS dormant_flag
  	FROM ucr_prd.ref_agency_yearly ref_agency_yearly
  	LEFT JOIN ucr_prd.ref_agency ref_agency USING (agency_id)
  	LEFT JOIN ucr_prd.ref_state USING (state_id)
  	LEFT JOIN ucr_prd.ref_agency_status ref_agency_status USING (agency_id, data_year)
  	LEFT JOIN ucr_prd.ref_agency_type USING (agency_type_id)
  	WHERE ref_agency_status.data_year IS NOT NULL AND ref_agency_yearly.is_nibrs IS TRUE
   ) agencies 
   	ON ((nibrs_incident.agency_id = agencies.agency_id) AND (EXTRACT(year FROM nibrs_incident.incident_date) = agencies.data_year))
  LEFT JOIN ucr_prd.nibrs_victim nibrs_victim using (incident_id)
  LEFT JOIN ucr_prd.lkup_nibrs_victim_type nibrs_victim_type using (victim_type_code)
  LEFT JOIN ucr_prd.nibrs_victim_offense nibrs_victim_offense using (victim_id)
  LEFT JOIN ucr_prd.nibrs_offense on (nibrs_victim_offense.offense_id = nibrs_offense.offense_id)
  LEFT JOIN ucr_prd.lkup_nibrs_offense nibrs_offense_type using (offense_code)
  LEFT JOIN ucr_prd.lkup_nibrs_location nibrs_location using (location_code)
 WHERE ", state_year_where)
offenses_df <- time_query(con, query_offenses)
offenses_df %>% write_csv(gzfile(paste0(queried_data_path,"raw_offenses_all_cols_",INPUT_STATE,".csv.gz")), na="")

offenses_df %>% 
  select(ori, legacy_ori, data_year, incident_id, agency_status, covered_flag,
         dormant_flag, agency_type_name, victim_id, victim_type_code, offense_id,
         state_id, state_name, state_abbr, state_postal_abbr, 
         offense_code, offense_name, crime_against, offense_category_name,
         offense_group, location_code, location_name) %>%  
  write_csv(gzfile(paste0(der_bystate_file_path,"raw_all_Offenses_offenses_",INPUT_STATE,".csv.gz")), na="")

offenses_df %>% 
  select(ori, data_year, incident_id, victim_id, offense_id, state_id, state_name,
         state_abbr, state_postal_abbr, location_code, location_name) %>%  
  write_csv(gzfile(paste0(der_bystate_file_path,"raw_location_offenses_",INPUT_STATE,".csv.gz")), na="")

### MORE THAN 2 FILES ####
## generate_estimates/Setup_part1_bystate/00a_Create_Datasets_full.Rmd
## generate_estimates/Setup_part1_bystate/000a_Create_Extracts_Carjacking.Rmd 
## generate_estimates/Setup_part1_bystate/00_Create_Datasets_full_Drug_Module.Rmd
## tasks/create_nibrs_extracts/property/00_Extract_Property.Rmd
query_property <- paste0("
 SELECT
  agencies.ori AS ori,
  agencies.legacy_ori AS legacy_ori,
  agencies.state_abbr AS state_abbr,
  extract(year FROM incident_date) as data_year,
  nibrs_incident.incident_id AS incident_id,
  nibrs_property.property_id,
  nibrs_property.prop_loss_code,
  nibrs_property.stolen_count AS stolen_count,
  nibrs_property_desc.prop_desc_code,
  nibrs_property_desc_lkup.name as prop_desc_name,
  nibrs_property_desc.property_value,
  nibrs_prop_loss_type.name AS prop_loss_name,
  nibrs_prop_loss_type.description AS prop_loss_desc
 FROM ucr_prd.nibrs_incident nibrs_incident
  LEFT JOIN (
  	SELECT
  	  ref_agency.agency_id,
  	  ref_agency_status.data_year,
  	  ref_agency.ori,
  	  ref_agency.legacy_ori,
  	  ref_state.abbr as state_abbr
  	FROM ucr_prd.ref_agency_yearly ref_agency_yearly
  	LEFT JOIN ucr_prd.ref_agency ref_agency USING (agency_id)
  	LEFT JOIN ucr_prd.ref_state USING (state_id)
  	LEFT JOIN ucr_prd.ref_agency_status ref_agency_status USING (agency_id, data_year)
  	WHERE ref_agency_status.data_year IS NOT NULL AND ref_agency_yearly.is_nibrs IS TRUE
  ) agencies 
  		ON ((nibrs_incident.agency_id = agencies.agency_id) AND (EXTRACT(year FROM nibrs_incident.incident_date) = agencies.data_year))
    LEFT JOIN ucr_prd.nibrs_property nibrs_property ON (nibrs_incident.incident_id = nibrs_property.incident_id)
  LEFT JOIN ucr_prd.nibrs_property_description nibrs_property_desc ON (nibrs_property.property_id = nibrs_property_desc.property_id)
  LEFT JOIN ucr_prd.lkup_nibrs_property_description nibrs_property_desc_lkup ON (nibrs_property_desc.prop_desc_code = nibrs_property_desc_lkup.prop_desc_code)
  LEFT JOIN ucr_prd.lkup_nibrs_property_loss nibrs_prop_loss_type ON (nibrs_property.prop_loss_code = nibrs_prop_loss_type.prop_loss_code)
 WHERE ", state_year_where)
property_df <- time_query(con, query_property)

property_df %>% 
  select(ori, state_abbr, incident_id, prop_loss_desc, prop_loss_code,
         prop_loss_name, prop_desc_code, prop_desc_name) %>% 
  write_csv(gzfile(paste0(queried_data_path,"raw_property_",INPUT_STATE,".csv.gz")), na="")

property_df %>% 
  select(data_year, incident_id, prop_desc_code, prop_desc_name, stolen_count) %>% 
  write_csv(gzfile(paste0(der_bystate_file_path,"raw_property_stolen_count_",INPUT_STATE,".csv.gz")), na="")

property_df %>% 
  select(incident_id, ori, legacy_ori, state_abbr, property_id, 
         prop_loss_code, prop_desc_code, prop_desc_name, 
         property_value, prop_loss_name) %>% 
  write_csv(gzfile(paste0(artifacts_path,"00_property_extract_",INPUT_STATE,".csv.gz")), na="")

  
### Group B only arrestee data ####

#Create the query statement
state_arrest_year_where = paste0("EXTRACT(YEAR FROM nibrs_groupb_arrestee.arrest_date) = ",  CONST_YEAR, " AND ref_state.abbr = '",INPUT_STATE,"'")

query_arrestee_offense_b <- paste0("
 SELECT 
  fm.data_month,
  fm.data_year,
  fm.form_code, 
  nibrs_groupb_arrestee.*, 
  nibrs_offense_type.crime_against,
  nibrs_offense_type.name as offense_name,
  ref_agency.ori,
  ref_agency.legacy_ori,
  ref_agency.nibrs_start_date,
  ref_state.abbr AS state_abbr
 FROM ucr_prd.form_month fm
  INNER JOIN ucr_prd.nibrs_groupb_arrestee nibrs_groupb_arrestee ON (fm.form_month_id = nibrs_groupb_arrestee.form_month_id)
  LEFT JOIN ucr_prd.ref_agency ref_agency ON (ref_agency.agency_id = nibrs_groupb_arrestee.agency_id)
  LEFT JOIN ucr_prd.ref_state ref_state ON (ref_agency.state_id = ref_state.state_id)
  LEFT JOIN ucr_prd.lkup_nibrs_offense nibrs_offense_type ON (nibrs_groupb_arrestee.offense_code = nibrs_offense_type.offense_code)  
 WHERE ", state_arrest_year_where)

#Run the query
arrestee_offense_b <- time_query(con, query_arrestee_offense_b)

if(nrow(arrestee_offense_b) >0){
  arrestee_offense_b %>% 
    write_csv(gzfile(paste0(der_bystate_file_path,"raw_all_arrestee_group_b_",INPUT_STATE, ".csv.gz")), na="")
}

#Delete the objects
rm(query_arrestee_offense_b, arrestee_offense_b)
invisible(gc())

#Note an arrestee can report up to two weapons
query_arrestee_offense_b_weapon <- paste0("
 SELECT 
  fm.data_month, 
  fm.data_year, 
  fm.form_code, 
  nibrs_groupb_arrestee.groupb_arrestee_id,
  nibrs_groupb_arrestee_weapon.weapon_code AS weapon_code,
  lkup_weapon.name AS weapon_name,
  ref_state.abbr AS state_abbr
 FROM ucr_prd.form_month fm
  INNER JOIN ucr_prd.nibrs_groupb_arrestee nibrs_groupb_arrestee ON (fm.form_month_id = nibrs_groupb_arrestee.form_month_id)
  LEFT JOIN ucr_prd.nibrs_groupb_arrestee_weapon nibrs_groupb_arrestee_weapon ON (nibrs_groupb_arrestee.groupb_arrestee_id = nibrs_groupb_arrestee_weapon.groupb_arrestee_id)
  LEFT JOIN ucr_prd.lkup_weapon lkup_weapon ON (nibrs_groupb_arrestee_weapon.weapon_code = lkup_weapon.weapon_code)
  LEFT JOIN ucr_prd.ref_agency ref_agency ON (ref_agency.agency_id = nibrs_groupb_arrestee.agency_id)
  LEFT JOIN ucr_prd.ref_state ref_state ON (ref_agency.state_id = ref_state.state_id)
 WHERE ", state_arrest_year_where)

#Run the query
arrestee_offense_b_weapon <- time_query(con, query_arrestee_offense_b_weapon)

if(nrow(arrestee_offense_b_weapon) >0){
  arrestee_offense_b_weapon %>% 
    write_csv(gzfile(paste0(der_bystate_file_path,"raw_all_arrestee_weapon_group_b_",INPUT_STATE, ".csv.gz")), na="")
}

#Delete the objects
rm(query_arrestee_offense_b_weapon, arrestee_offense_b_weapon)
invisible(gc())

  
#################################################################################################################################################  
### close connection ####
dbDisconnect(con)

invisible(gc())
rm(list=c(ls(pattern="query_*"), ls(pattern="*_df")))
