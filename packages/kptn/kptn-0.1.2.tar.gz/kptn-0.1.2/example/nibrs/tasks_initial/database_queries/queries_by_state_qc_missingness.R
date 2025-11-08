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
queried_data_path = paste0(outputPipelineDir, "/QC_query_outputs_files/")
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

state_year_where <- paste0("EXTRACT(YEAR FROM incident_date) = ", CONST_YEAR," AND state_abbr = '", INPUT_STATE,"'")

initial_offense_query <- paste0("
 SELECT 
 a.state_abbr,
 o.offense_id, 
 o.num_premises_entered, 
 o.method_of_entry_code AS method_entry_code,
 o.offense_code, 
 bm.bias_code, 
 o.location_code, 
 ca.criminal_activity_code AS criminal_act_code, 
 ow.weapon_code
FROM ucr_prd.nibrs_incident
 LEFT JOIN (
  SELECT
     ref_agency.ori,
     ref_agency.nibrs_start_date,
     ref_agency.legacy_ori,
     ref_agency_status.data_year,
     ref_agency.agency_id,
     ref_agency.state_id,
     ref_state.name AS state_name,
     ref_state.abbr AS state_abbr,
     ref_state.postal_abbr AS state_postal_abbr
  FROM ucr_prd.ref_agency_yearly ref_agency_yearly
	 LEFT JOIN ucr_prd.ref_agency ref_agency USING (agency_id)
	 LEFT JOIN ucr_prd.ref_state USING (state_id)
	 LEFT JOIN ucr_prd.ref_agency_status ref_agency_status USING (agency_id, data_year)
  WHERE ref_agency_status.data_year IS NOT NULL AND ref_agency_yearly.is_nibrs IS TRUE) a 
     ON ((nibrs_incident.agency_id = a.agency_id) 
     AND (EXTRACT(year FROM nibrs_incident.incident_date) = a.data_year))
 LEFT JOIN ucr_prd.nibrs_offense o USING (incident_id)
 LEFT JOIN ucr_prd.nibrs_bias_motivation bm USING (offense_id)
 LEFT JOIN ucr_prd.nibrs_criminal_activity ca USING (offense_id)
 LEFT JOIN ucr_prd.nibrs_offense_weapon ow USING (offense_id)
 LEFT JOIN ucr_prd.form_month fm ON (nibrs_incident.form_month_id = fm.form_month_id AND a.agency_id = fm.agency_id AND a.data_year = fm.data_year)
 WHERE ", state_year_where, " AND fm.form_code = 'N'"
)
offense_frame <- time_query(con, initial_offense_query)
offense_frame %>% write_csv(gzfile(paste0(queried_data_path,"qc_missingness_offense_frame_",INPUT_STATE,".csv.gz")), na="")
rm(list=c(ls(pattern="*_frame")))
invisible(gc())

initial_admin_query <- paste0("
SELECT 
 a.state_abbr,
 nibrs_incident.incident_id, 
 nibrs_incident.incident_date, 
 CASE
     WHEN nibrs_incident.is_cargo_theft IS TRUE THEN 'Y'::bpchar
     WHEN nibrs_incident.is_cargo_theft IS FALSE THEN 'N'::bpchar
     ELSE NULL::bpchar
 END AS cargo_theft_flag, 
 CASE
     WHEN nibrs_incident.is_reported_date IS TRUE THEN 'R'::bpchar
     WHEN nibrs_incident.is_reported_date IS FALSE THEN ''::bpchar
     ELSE NULL::bpchar
 END AS report_date_flag, 
 nibrs_incident.incident_hour,
 nibrs_incident.cleared_exceptionally_date AS cleared_except_date,
 nibrs_offense.offense_code, 
 nibrs_victim.victim_type_code, 
 nibrs_incident.cleared_exceptionally_code AS cleared_except_code
FROM ucr_prd.nibrs_incident
 LEFT JOIN (
  SELECT
     ref_agency.ori,
     ref_agency.nibrs_start_date,
     ref_agency.legacy_ori,
     ref_agency_status.data_year,
     ref_agency.agency_id,
     ref_agency.state_id,
     ref_state.name AS state_name,
     ref_state.abbr AS state_abbr,
     ref_state.postal_abbr AS state_postal_abbr
  FROM ucr_prd.ref_agency_yearly ref_agency_yearly
	 LEFT JOIN ucr_prd.ref_agency ref_agency USING (agency_id)
	 LEFT JOIN ucr_prd.ref_state USING (state_id)
	 LEFT JOIN ucr_prd.ref_agency_status ref_agency_status USING (agency_id, data_year)
  WHERE ref_agency_status.data_year IS NOT NULL AND ref_agency_yearly.is_nibrs IS TRUE) a 
     ON ((nibrs_incident.agency_id = a.agency_id) 
     AND (EXTRACT(year FROM nibrs_incident.incident_date) = a.data_year))     
 LEFT JOIN ucr_prd.nibrs_victim USING (incident_id)
 LEFT JOIN ucr_prd.nibrs_victim_offense USING (victim_id)
 LEFT JOIN ucr_prd.nibrs_offense USING (incident_id, offense_id)
 WHERE ", state_year_where
)
admin_frame <- time_query(con, initial_admin_query)
admin_frame %>% write_csv(gzfile(paste0(queried_data_path,"qc_missingness_admin_frame_",INPUT_STATE,".csv.gz")), na="")
rm(list=c(ls(pattern="*_frame")))
invisible(gc())

initial_property_query <- paste0("
SELECT 
 a.state_abbr,
 nibrs_incident.incident_id,  
 nibrs_offense.offense_id, 
 nibrs_offense.offense_code, 
 nibrs_incident.form_month_id AS nibrs_month_id, 
 lkup_nibrs_property_loss.name AS prop_loss_name,
 nibrs_property.prop_loss_code,
 nibrs_property_description.prop_desc_code,
 nibrs_property_description.property_value 
FROM ucr_prd.nibrs_incident
 LEFT JOIN (
  SELECT
     ref_agency.ori,
     ref_agency.nibrs_start_date,
     ref_agency.legacy_ori,
     ref_agency_status.data_year,
     ref_agency.agency_id,
     ref_agency.state_id,
     ref_state.name AS state_name,
     ref_state.abbr AS state_abbr,
     ref_state.postal_abbr AS state_postal_abbr
  FROM ucr_prd.ref_agency_yearly ref_agency_yearly
	 LEFT JOIN ucr_prd.ref_agency ref_agency USING (agency_id)
	 LEFT JOIN ucr_prd.ref_state USING (state_id)
	 LEFT JOIN ucr_prd.ref_agency_status ref_agency_status USING (agency_id, data_year)
  WHERE ref_agency_status.data_year IS NOT NULL AND ref_agency_yearly.is_nibrs IS TRUE) a 
     ON ((nibrs_incident.agency_id = a.agency_id) 
     AND (EXTRACT(year FROM nibrs_incident.incident_date) = a.data_year))
 LEFT JOIN ucr_prd.nibrs_offense USING(incident_id)--ON ((nibrs_incident.incident_id = nibrs_offense.incident_id) AND (nibrs_victim_offense.offense_id = nibrs_offense.offense_id))
 LEFT JOIN ucr_prd.nibrs_property USING (incident_id) --ON (nibrs_incident.incident_id = nibrs_property.incident_id)
 LEFT JOIN ucr_prd.nibrs_property_description USING (property_id) --ON (nibrs_property.property_id = nibrs_property_desc.property_id)
 LEFT JOIN ucr_prd.lkup_nibrs_property_loss USING (prop_loss_code) --ON (nibrs_property.prop_loss_code = nibrs_prop_loss_type.prop_loss_code)
 WHERE ", state_year_where
)
property_frame <- time_query(con, initial_property_query)
property_frame %>% write_csv(gzfile(paste0(queried_data_path,"qc_missingness_property_frame_",INPUT_STATE,".csv.gz")), na="")
rm(list=c(ls(pattern="*_frame")))
invisible(gc())

initial_offender_query <- paste0("
SELECT 
  a.state_abbr,
  nibrs_offender.offender_id,
  nibrs_offender.sequence_number AS offender_seq_num,
  nibrs_offender.age_code as age_code,
  CASE
     WHEN nibrs_offender.sex_code = 'X'::bpchar THEN ' '::bpchar
     ELSE nibrs_offender.sex_code
  END AS sex_code,
  CASE 
      WHEN nibrs_offender.race_code = '' THEN 'NA'
      ELSE nibrs_offender.race_code
  END AS race_code,
  CASE
     WHEN nibrs_offender.ethnicity_code = 'X'::bpchar THEN ' '::bpchar
     ELSE nibrs_offender.ethnicity_code
  END AS ethnicity_code,
  nibrs_offense.offense_code
FROM ucr_prd.nibrs_incident
 LEFT JOIN (
  SELECT
     ref_agency.ori,
     ref_agency.nibrs_start_date,
     ref_agency.legacy_ori,
     ref_agency_status.data_year,
     ref_agency.agency_id,
     ref_agency.state_id,
     ref_state.name AS state_name,
     ref_state.abbr AS state_abbr,
     ref_state.postal_abbr AS state_postal_abbr
  FROM ucr_prd.ref_agency_yearly ref_agency_yearly
	 LEFT JOIN ucr_prd.ref_agency ref_agency USING (agency_id)
	 LEFT JOIN ucr_prd.ref_state USING (state_id)
	 LEFT JOIN ucr_prd.ref_agency_status ref_agency_status USING (agency_id, data_year)
  WHERE ref_agency_status.data_year IS NOT NULL AND ref_agency_yearly.is_nibrs IS TRUE) a 
     ON ((nibrs_incident.agency_id = a.agency_id) 
     AND (EXTRACT(year FROM nibrs_incident.incident_date) = a.data_year))
 LEFT JOIN ucr_prd.nibrs_offense USING (incident_id)
 LEFT JOIN ucr_prd.nibrs_offender USING (incident_id)
 WHERE ", state_year_where
)
offender_frame <- time_query(con, initial_offender_query)
offender_frame %>% write_csv(gzfile(paste0(queried_data_path,"qc_missingness_offender_frame_",INPUT_STATE,".csv.gz")), na="")
rm(list=c(ls(pattern="*_frame")))
invisible(gc())

initial_victim_dem_query <- paste0("
SELECT 
  a.state_abbr,
  EXTRACT(year FROM nibrs_incident.incident_date) as data_year,
  nibrs_victim.victim_id,
  nibrs_incident.incident_id,
  nibrs_victim.sequence_number AS victim_seq_num,
  nibrs_victim.victim_type_code AS victim_type_code,
  nibrs_victim.assignment_code,
  nibrs_victim.activity_code,
  nibrs_victim.outside_agency_id,
  nibrs_victim.age_code,
  CASE
      WHEN nibrs_victim.sex_code = 'X'::bpchar THEN ' '::bpchar
      ELSE nibrs_victim.sex_code
  END AS sex_code,
  nibrs_victim.race_code,
  nibrs_victim.ethnicity_code,
  nibrs_victim.resident_status_code,
  nibrs_offense.offense_code
 FROM ucr_prd.nibrs_incident
 LEFT JOIN (
  SELECT
     ref_agency.ori,
     ref_agency.nibrs_start_date,
     ref_agency.legacy_ori,
     ref_agency_status.data_year,
     ref_agency.agency_id,
     ref_agency.state_id,
     ref_state.name AS state_name,
     ref_state.abbr AS state_abbr,
     ref_state.postal_abbr AS state_postal_abbr
  FROM ucr_prd.ref_agency_yearly ref_agency_yearly
	 LEFT JOIN ucr_prd.ref_agency ref_agency USING (agency_id)
	 LEFT JOIN ucr_prd.ref_state USING (state_id)
	 LEFT JOIN ucr_prd.ref_agency_status ref_agency_status USING (agency_id, data_year)
  WHERE ref_agency_status.data_year IS NOT NULL AND ref_agency_yearly.is_nibrs IS TRUE) a 
     ON ((nibrs_incident.agency_id = a.agency_id) 
     AND (EXTRACT(year FROM nibrs_incident.incident_date) = a.data_year))
  LEFT JOIN ucr_prd.nibrs_victim nibrs_victim USING (incident_id)
  LEFT JOIN ucr_prd.nibrs_offense USING (incident_id)
WHERE ", state_year_where, " AND nibrs_victim.victim_type_code in ('I','L')"
)
victim_dem_frame <- time_query(con, initial_victim_dem_query)
victim_dem_frame %>% write_csv(gzfile(paste0(queried_data_path,"qc_missingness_victim_dem_frame_",INPUT_STATE,".csv.gz")), na="")
rm(list=c(ls(pattern="*_frame")))
invisible(gc())

initial_victim_injury_query <- paste0("
SELECT 
 a.state_abbr,
 nibrs_victim.victim_id, 
 nibrs_victim.incident_id, 
 nibrs_offense.offense_code,
 nibrs_victim_injury.injury_code
FROM ucr_prd.nibrs_incident
 LEFT JOIN (
  SELECT
     ref_agency.ori,
     ref_agency.nibrs_start_date,
     ref_agency.legacy_ori,
     ref_agency_status.data_year,
     ref_agency.agency_id,
     ref_agency.state_id,
     ref_state.name AS state_name,
     ref_state.abbr AS state_abbr,
     ref_state.postal_abbr AS state_postal_abbr
  FROM ucr_prd.ref_agency_yearly ref_agency_yearly
	 LEFT JOIN ucr_prd.ref_agency ref_agency USING (agency_id)
	 LEFT JOIN ucr_prd.ref_state USING (state_id)
	 LEFT JOIN ucr_prd.ref_agency_status ref_agency_status USING (agency_id, data_year)
  WHERE ref_agency_status.data_year IS NOT NULL AND ref_agency_yearly.is_nibrs IS TRUE) a 
     ON ((nibrs_incident.agency_id = a.agency_id) 
     AND (EXTRACT(year FROM nibrs_incident.incident_date) = a.data_year))
 LEFT JOIN ucr_prd.nibrs_victim nibrs_victim USING (incident_id)
 LEFT JOIN ucr_prd.nibrs_victim_offense ON (nibrs_victim.victim_id = nibrs_victim_offense.victim_id)
 LEFT JOIN ucr_prd.nibrs_offense ON ((nibrs_incident.incident_id = nibrs_offense.incident_id) AND (nibrs_victim_offense.offense_id = nibrs_offense.offense_id))
 LEFT JOIN ucr_prd.nibrs_victim_injury ON (nibrs_victim.victim_id = nibrs_victim_injury.victim_id)
WHERE ", state_year_where, " AND nibrs_offense.offense_code IN ('100','11A','11B','11C','11D','120','13A','13B','210','64A','64B')"
)
victim_injury_frame <- time_query(con, initial_victim_injury_query)
victim_injury_frame %>% write_csv(gzfile(paste0(queried_data_path,"qc_missingness_victim_injury_frame_",INPUT_STATE,".csv.gz")), na="")
rm(list=c(ls(pattern="*_frame")))
invisible(gc())


initial_victim_circumstances_query <- paste0("
SELECT 
 a.state_abbr,
 nibrs_victim_circumstance.circumstance_code, 
 nibrs_victim_circumstance.justifiable_force_code,
 nibrs_offense.offense_code
FROM ucr_prd.nibrs_incident
 LEFT JOIN (
  SELECT
     ref_agency.ori,
     ref_agency.nibrs_start_date,
     ref_agency.legacy_ori,
     ref_agency_status.data_year,
     ref_agency.agency_id,
     ref_agency.state_id,
     ref_state.name AS state_name,
     ref_state.abbr AS state_abbr,
     ref_state.postal_abbr AS state_postal_abbr
  FROM ucr_prd.ref_agency_yearly ref_agency_yearly
	 LEFT JOIN ucr_prd.ref_agency ref_agency USING (agency_id)
	 LEFT JOIN ucr_prd.ref_state USING (state_id)
	 LEFT JOIN ucr_prd.ref_agency_status ref_agency_status USING (agency_id, data_year)
  WHERE ref_agency_status.data_year IS NOT NULL AND ref_agency_yearly.is_nibrs IS TRUE) a 
     ON ((nibrs_incident.agency_id = a.agency_id) 
     AND (EXTRACT(year FROM nibrs_incident.incident_date) = a.data_year))
 LEFT JOIN ucr_prd.nibrs_victim USING (incident_id)
 LEFT JOIN ucr_prd.nibrs_victim_offense USING (victim_id)
 LEFT JOIN ucr_prd.nibrs_offense USING (offense_id)
 LEFT JOIN ucr_prd.nibrs_victim_circumstance USING (victim_id)
WHERE ", state_year_where, " AND nibrs_offense.offense_code in ('13A', '09A', '09B', '09C')"
)
victim_circumstances_frame <- time_query(con, initial_victim_circumstances_query)
victim_circumstances_frame %>% write_csv(gzfile(paste0(queried_data_path,"qc_missingness_victim_circumstances_frame_",INPUT_STATE,".csv.gz")), na="")
rm(list=c(ls(pattern="*_frame")))
invisible(gc())


initial_victim_relationship_query <- paste0("
SELECT 
 a.state_abbr,
 nibrs_victim_offender_relationship.relationship_code,
 nibrs_victim_offender_relationship.victim_id,
 nibrs_victim_offender_relationship.offender_id,
 nibrs_offense.offense_code
FROM ucr_prd.nibrs_incident
 LEFT JOIN (
  SELECT
     ref_agency.ori,
     ref_agency.nibrs_start_date,
     ref_agency.legacy_ori,
     ref_agency_status.data_year,
     ref_agency.agency_id,
     ref_agency.state_id,
     ref_state.name AS state_name,
     ref_state.abbr AS state_abbr,
     ref_state.postal_abbr AS state_postal_abbr
  FROM ucr_prd.ref_agency_yearly ref_agency_yearly
LEFT JOIN ucr_prd.ref_agency ref_agency USING (agency_id)
LEFT JOIN ucr_prd.ref_state USING (state_id)
LEFT JOIN ucr_prd.ref_agency_status ref_agency_status USING (agency_id, data_year)
  WHERE ref_agency_status.data_year IS NOT NULL AND ref_agency_yearly.is_nibrs IS TRUE) a 
     ON ((nibrs_incident.agency_id = a.agency_id) 
     AND (EXTRACT(year FROM nibrs_incident.incident_date) = a.data_year))
 LEFT JOIN ucr_prd.nibrs_offender USING (incident_id)
 LEFT JOIN ucr_prd.nibrs_victim USING (incident_id)
 LEFT JOIN ucr_prd.nibrs_victim_offender_relationship USING (victim_id, offender_id)
 LEFT JOIN ucr_prd.nibrs_offense USING (incident_id)
WHERE ", state_year_where
)
victim_relationship_frame <- time_query(con, initial_victim_relationship_query)
victim_relationship_frame %>% write_csv(gzfile(paste0(queried_data_path,"qc_missingness_victim_relationship_frame_",INPUT_STATE,".csv.gz")), na="")
rm(list=c(ls(pattern="*_frame")))
invisible(gc())



initial_arrestee_dem_query <- paste0("
SELECT
 a.state_abbr,
 nibrs_arrestee.arrestee_id,
 nibrs_arrestee.age_code,
 CASE
      WHEN nibrs_arrestee.age_code = ANY (ARRAY['NN'::bpchar, 'NB'::bpchar, 'BB'::bpchar, '00'::bpchar, 'NS'::bpchar, '99'::bpchar]) THEN NULL::bpchar
      ELSE nibrs_arrestee.age_code
 END AS age_num,
 CASE
      WHEN nibrs_arrestee.sex_code = 'X'::bpchar THEN ' '::bpchar
      ELSE nibrs_arrestee.sex_code
 END AS sex_code, 
 CASE
     WHEN nibrs_arrestee.age_code = ANY (ARRAY['NN'::bpchar, 'NB'::bpchar, 'BB'::bpchar, '00'::bpchar, 'NS'::bpchar, '99'::bpchar]) THEN NULL::bpchar
     ELSE nibrs_arrestee.age_code
 END AS age_num,
 CASE 
      WHEN nibrs_arrestee.race_code = '' THEN 'NA'
      ELSE nibrs_arrestee.race_code
 END AS race_code,
 CASE
     WHEN nibrs_arrestee.ethnicity_code = 'X'::bpchar THEN ' '::bpchar
     ELSE nibrs_arrestee.ethnicity_code
 END AS ethnicity_code,
 nibrs_arrestee.arrest_type_code,
 nibrs_arrestee.multiple_indicator_code AS multiple_indicator,
 CASE
     WHEN nibrs_arrestee.under_18_disposition_code IS NULL THEN ' '::bpchar
     ELSE nibrs_arrestee.under_18_disposition_code
 END AS under_18_disposition_code,
 nibrs_offense.offense_code
FROM ucr_prd.nibrs_arrestee
 LEFT JOIN ucr_prd.nibrs_offense USING (incident_id)
 LEFT JOIN ucr_prd.nibrs_incident USING (incident_id)
 LEFT JOIN (
  SELECT
     ref_agency.ori,
     ref_agency.nibrs_start_date,
     ref_agency.legacy_ori,
     ref_agency_status.data_year,
     ref_agency.agency_id,
     ref_agency.state_id,
     ref_state.name AS state_name,
     ref_state.abbr AS state_abbr,
     ref_state.postal_abbr AS state_postal_abbr
  FROM ucr_prd.ref_agency_yearly ref_agency_yearly
	 LEFT JOIN ucr_prd.ref_agency ref_agency USING (agency_id)
	 LEFT JOIN ucr_prd.ref_state USING (state_id)
	 LEFT JOIN ucr_prd.ref_agency_status ref_agency_status USING (agency_id, data_year)
  WHERE ref_agency_status.data_year IS NOT NULL AND ref_agency_yearly.is_nibrs IS TRUE) a 
     ON ((nibrs_incident.agency_id = a.agency_id) 
     AND (EXTRACT(year FROM nibrs_incident.incident_date) = a.data_year))
WHERE ", state_year_where
)
arrestee_dem_frame <- time_query(con, initial_arrestee_dem_query)
arrestee_dem_frame %>% write_csv(gzfile(paste0(queried_data_path,"qc_missingness_arrestee_dem_frame_",INPUT_STATE,".csv.gz")), na="")
rm(list=c(ls(pattern="*_frame")))
invisible(gc())



initial_arrestee_weapon_query <- paste0("
SELECT
 a.state_abbr,
 nibrs_offense.offense_code,
 nibrs_arrestee_weapon.weapon_code,
 lkup_weapon.name as weapon_name
FROM ucr_prd.nibrs_arrestee_weapon
 LEFT JOIN ucr_prd.nibrs_arrestee USING (arrestee_id)
 LEFT JOIN ucr_prd.nibrs_offense USING (incident_id)
 LEFT JOIN ucr_prd.nibrs_incident USING (incident_id)
 LEFT JOIN (
  SELECT
     ref_agency.ori,
     ref_agency.nibrs_start_date,
     ref_agency.legacy_ori,
     ref_agency_status.data_year,
     ref_agency.agency_id,
     ref_agency.state_id,
     ref_state.name AS state_name,
     ref_state.abbr AS state_abbr,
     ref_state.postal_abbr AS state_postal_abbr
  FROM ucr_prd.ref_agency_yearly ref_agency_yearly
	 LEFT JOIN ucr_prd.ref_agency ref_agency USING (agency_id)
	 LEFT JOIN ucr_prd.ref_state USING (state_id)
	 LEFT JOIN ucr_prd.ref_agency_status ref_agency_status USING (agency_id, data_year)
  WHERE ref_agency_status.data_year IS NOT NULL AND ref_agency_yearly.is_nibrs IS TRUE) a 
     ON ((nibrs_incident.agency_id = a.agency_id) 
     AND (EXTRACT(year FROM nibrs_incident.incident_date) = a.data_year))
 LEFT JOIN ucr_prd.lkup_weapon USING (weapon_code) 
WHERE ", state_year_where
)
arrestee_weapon_frame <- time_query(con, initial_arrestee_weapon_query)
arrestee_weapon_frame %>% write_csv(gzfile(paste0(queried_data_path,"qc_missingness_arrestee_weapon_frame_",INPUT_STATE,".csv.gz")), na="")
rm(list=c(ls(pattern="*_frame")))
invisible(gc())


#################################################################################################################################################  
### close connection ####
dbDisconnect(con)
