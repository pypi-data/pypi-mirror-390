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

#output path for markdown files
filepathout = paste0(outputPipelineDir, "/markdown/")
if (! dir.exists(filepathout)) {
  dir.create(filepathout, recursive = TRUE)
}

artifacts_path = paste0(outputPipelineDir, "/artifacts/")
if (! dir.exists(artifacts_path)) {
  dir.create(artifacts_path, recursive = TRUE)
}

#output path for all the data extracts
queried_data_path = paste0(outputPipelineDir, "/initial_tasks_output/database_queries/")
if (! dir.exists(queried_data_path)) {
  dir.create(queried_data_path, recursive = TRUE)
}

CONST_YEAR <- as.integer(Sys.getenv("DATA_YEAR"))

con <- dbConnect(RPostgres::Postgres())

data_year_where <- paste0("nibrs_incident.data_year = ",  CONST_YEAR)

# tasks/generate_estimates/Setup_part2_merged/01_Process_Weights_and_permutation_variable.Rmd
# tasks/generate_estimates/Setup_part2_merged/02_Create_Datasets_Agency_ORI.Rmd
query_agencies_data_year <- paste0("
 SELECT 
  ref_agency.ori,
  ref_agency.legacy_ori,
  CASE
      WHEN ref_agency_yearly.agency_status = 'D'::bpchar THEN 'Y'::text
      ELSE 'N'::text
  END AS tbd_dormant_flag,
  CASE
      WHEN ref_agency_yearly.is_covered IS TRUE THEN 'Y'::text
      WHEN ref_agency_yearly.is_covered IS FALSE THEN 'N'::text
      ELSE ' '::text
  END AS tbd_covered_flag,
  ref_agency_status.agency_status AS tbd_agency_status
 FROM ucr_prd.ref_agency_yearly ref_agency_yearly
  LEFT JOIN ucr_prd.ref_agency ref_agency USING (agency_id)
  LEFT JOIN ucr_prd.ref_agency_status ref_agency_status USING (agency_id, data_year)
 WHERE ref_agency_status.data_year IS NOT NULL 
       AND ref_agency_yearly.is_nibrs IS TRUE
       AND ref_agency_status.data_year = ", CONST_YEAR
)
agencies_data_year_df <- time_query(con, query_agencies_data_year)
agencies_data_year_df %>% write_csv(gzfile(paste0(queried_data_path,"agencies_data_year_",CONST_YEAR,".csv.gz")), na="")

### tasks/impute_blocks/02_BlockImputation_Incident_Table.Rmd ####
query_incidents_pop_group_year <- paste0("
 SELECT 
  EXTRACT(year FROM nibrs_incident.incident_date) AS data_year,
  nibrs_incident.incident_id AS incident_id,
  nibrs_incident.incident_date AS incident_date,
  agencies.ori AS ori,
  agencies.legacy_ori AS legacy_ori,
  agencies.nibrs_start_date AS nibrs_start_date
 FROM ucr_prd.nibrs_incident nibrs_incident
 LEFT JOIN (
  SELECT 
   ref_agency.ori,
   ref_agency.agency_id,
   ref_agency.legacy_ori,
   ref_agency.nibrs_start_date,
   ref_agency_status.data_year
  FROM ucr_prd.ref_agency_yearly ref_agency_yearly
  LEFT JOIN ucr_prd.ref_agency ref_agency USING (agency_id)
  LEFT JOIN ucr_prd.ref_agency_status ref_agency_status USING (agency_id, data_year)
  WHERE ref_agency_status.data_year IS NOT NULL AND ref_agency_yearly.is_nibrs IS TRUE
 ) agencies 
   ON ((nibrs_incident.agency_id = agencies.agency_id) 
   AND (EXTRACT(year FROM nibrs_incident.incident_date) = agencies.data_year))
 WHERE EXTRACT(year FROM nibrs_incident.incident_date) = ", CONST_YEAR)
incidents_pop_grp_df <- time_query(con, query_incidents_pop_group_year)
incidents_pop_grp_df %>% write_csv(gzfile(paste0(queried_data_path,"incidents_population_groups_",CONST_YEAR,".csv.gz")), na="")

### tasks/create_partial_reporters/generate_partial_reporters.R ####
query_data_year <- "SELECT DISTINCT EXTRACT(year FROM nibrs_incident.incident_date) as data_year from ucr_prd.nibrs_incident;"
list_of_years <- time_query(con,query_data_year) %>% filter(data_year <= CONST_YEAR & data_year >= (CONST_YEAR-4))

res_list <- map(list_of_years$data_year, ~{
  y <- .x
  query <- paste0("
        select 
	agencies.ori,
	extract(year from inc.incident_date) as incident_year,
    extract(month from inc.incident_date) as incident_month,
    oftype.offense_code,
    oftype.name as offense_name,
    oftype.crime_against,
    oftype.offense_group,
    count(*) as countofrecords
FROM ucr_prd.nibrs_incident inc
	LEFT JOIN (
	  SELECT
	  ref_agency.ori,
	  ref_agency.agency_id,
	  ref_agency.legacy_ori,
	  ref_agency.nibrs_start_date,
	  ref_agency_status.data_year,
	  ref_agency_yearly.is_nibrs
	  FROM ucr_prd.ref_agency_yearly ref_agency_yearly
	  LEFT JOIN ucr_prd.ref_agency ref_agency USING (agency_id)
	  LEFT JOIN ucr_prd.ref_agency_status ref_agency_status USING (agency_id, data_year)
	  WHERE ref_agency_status.data_year IS NOT NULL AND ref_agency_yearly.is_nibrs IS TRUE
	) agencies 
         ON ((inc.agency_id = agencies.agency_id) AND (EXTRACT(year from inc.incident_date) = agencies.data_year))
left join ucr_prd.nibrs_offense using (incident_id)
left join ucr_prd.lkup_nibrs_offense oftype using (offense_code)
where EXTRACT(year from inc.incident_date) = ", y, "
GROUP BY ori, incident_year, incident_month,  oftype.offense_code, oftype.name, oftype.crime_against, oftype.offense_group;
  ")
  log_debug(paste0("Run query for: ", y))
  time_query(con, query)
})
df1 <- res_list %>% rbindlist()
df1 <- df1[!is.na(ori)]
df1 %>% write_csv(gzfile(paste0(queried_data_path,"agencies_count_offenses_",CONST_YEAR,".csv.gz")), na="")

### tasks/create_partial_reporters/generate_partial_reporters_part2.R ####
agency_table_list <- list()
agency_county_list <- list()

for(y in list_of_years$data_year){
  
  query_agency_cty_data_year <- paste0("
    SELECT
  ref_agency_county.agency_id,
  ref_agency_county.data_year,
  lpad(ref_county.fips_code::text, 3, '0'::text) AS county_fips_code_all,
  ref_county.name AS county_name_all,
  lpad(ref_state.fips_code::text, 2, '0'::text) || lpad(ref_county.fips_code::text, 3, '0'::text) AS fips_code_all,
  lpad(ref_state.fips_code::text, 2, '0'::text) AS state_fips_code
FROM ucr_prd.ref_agency_county
INNER JOIN ucr_prd.ref_county ON ref_agency_county.county_id = ref_county.county_id
LEFT JOIN ucr_prd.ref_state ON ref_county.state_id = ref_state.state_id
LEFT JOIN ucr_prd.ref_agency_yearly 
    ON ref_agency_county.agency_id = ref_agency_yearly.agency_id 
    AND ref_agency_county.data_year = ref_agency_yearly.data_year
WHERE ref_agency_yearly.is_nibrs IS TRUE
    AND lpad(ref_county.fips_code::text, 3, '0'::text) != '0-1'
    AND ref_agency_county.data_year = ",y,"
  ")
  
  agency_county_list[[y]] <- time_query(con,query_agency_cty_data_year)
}
agency_county_df <- bind_rows(agency_county_list)

agency_county_df %>% write_csv(gzfile(paste0(queried_data_path,"agencies_counties_", CONST_YEAR-4, "_", CONST_YEAR, ".csv.gz")), na="")

### Query out 5 years all at once
query_agency_five_years <- paste0("
SELECT DISTINCT ref_agency_type.name AS agency_type_name,
    ref_agency.agency_type_id,
    ref_agency.pub_agency_unit,
    ref_agency.nibrs_ct_start_date,
    ref_agency.ori,
    ref_agency.agency_id,
    ref_agency.nibrs_off_eth_start_date,
    ref_agency.submitting_agency_id,
    ref_agency.ucr_agency_name,
    ref_agency.legacy_ori,
    ref_agency.nibrs_multi_bias_start_date,
    ref_agency.ncic_agency_name,
    ref_agency.nibrs_leoka_start_date,
    ref_agency.pub_agency_name,
    ref_agency.state_id,
    ref_agency.nibrs_start_date,
    ref_agency.judicial_district_code,
    ref_agency.tribe_id,
    ref_agency.department_id,
    ref_agency.legacy_notify_agency,
    ref_agency.city_id,
    ref_agency.special_mailing_group,
    ref_agency.population_family_id,
    ref_agency.campus_id,
    ref_agency.nibrs_leoka_except_flag,
    ref_agency.fid_code,
    ref_agency.field_office_id,
    ref_agency.tribal_district_id,
    ref_agency.added_date,
    ref_agency.special_mailing_address,
    ref_state.postal_abbr AS state_postal_abbr,
    ref_state.abbr AS state_abbr,
    ref_state.name AS state_name,
    ref_agency_status.agency_status,
    ref_agency_status.data_year,
    ref_submitting_agency.sai,
    ref_submitting_agency.nibrs_cert_date,
    ref_agency_yearly.is_direct_contributor AS direct_contributor_flag,
    ref_agency_yearly.is_nibrs,
    ref_agency_yearly.agency_status AS yearly_agency_status,
    ref_agency_yearly.population_group_id,
        CASE
            WHEN ref_agency_yearly.is_publishable IS TRUE THEN 'Y'::text
            WHEN ref_agency_yearly.is_publishable IS FALSE THEN 'N'::text
            ELSE ' '::text
        END AS publishable_flag,
        CASE
            WHEN ref_agency_yearly.is_nibrs IS TRUE THEN 'Y'::text
            WHEN ref_agency_yearly.is_nibrs IS FALSE THEN 'N'::text
            ELSE ' '::text
        END AS nibrs_participated,
    ref_population_group.code AS population_group_code,
    ref_population_group.description AS population_group_desc,
    ref_parent_population_group.code AS parent_pop_group_code,
    ref_parent_population_group.description AS parent_pop_group_desc,
        CASE
            WHEN ref_agency_yearly.is_covered IS TRUE THEN 'Y'::text
            WHEN ref_agency_yearly.is_covered IS FALSE THEN 'N'::text
            ELSE ' '::text
        END AS covered_flag,
    ref_agency_yearly.population,
        CASE
            WHEN ref_agency_yearly.agency_status = 'D'::bpchar THEN 'Y'::text
            ELSE 'N'::text
        END AS dormant_flag,
        CASE
            WHEN ref_agency_yearly.agency_status = 'D'::bpchar THEN ref_agency_yearly.data_year
            ELSE NULL::smallint
        END AS dormant_year,
    ref_division.code AS division_code,
    ref_division.name AS division_name,
    ref_region.code AS region_code,
    ref_region.name AS region_name,
    ref_region.description AS region_desc,
        CASE
            WHEN ref_agency_yearly.is_suburban_area IS TRUE THEN 'Y'::text
            WHEN ref_agency_yearly.is_suburban_area IS FALSE THEN 'N'::text
            ELSE ' '::text
        END AS suburban_area_flag,
    string_agg(ref_county.name::text, '; '::text ORDER BY (ref_county.name::text)) AS county_name,
    string_agg(ref_metro_division.name::text, '; '::text ORDER BY (ref_metro_division.name::text)) AS metro_div_name,
    string_agg(ref_msa.name::text, '; '::text ORDER BY (ref_msa.name::text)) AS msa_name
   FROM ucr_prd.ref_agency_yearly ref_agency_yearly
     LEFT JOIN ucr_prd.ref_agency USING (agency_id)
     LEFT JOIN ucr_prd.ref_state USING (state_id)
     LEFT JOIN ucr_prd.ref_division USING (division_id)
     LEFT JOIN ucr_prd.ref_region USING (region_id)
     LEFT JOIN ucr_prd.ref_agency_status USING (agency_id, data_year)
     LEFT JOIN ucr_prd.ref_submitting_agency USING (agency_id)
     LEFT JOIN ucr_prd.ref_agency_type USING (agency_type_id)
     LEFT JOIN ucr_prd.ref_agency_covered_by USING (agency_id, data_year)
     LEFT JOIN ucr_prd.ref_population_group USING (population_group_id)
     LEFT JOIN ucr_prd.ref_parent_population_group USING (parent_pop_group_id)
     LEFT JOIN ucr_prd.ref_agency_county USING (agency_id, data_year)
     LEFT JOIN ucr_prd.ref_county USING (county_id)
     LEFT JOIN ucr_prd.ref_metro_division USING (metro_div_id)
     LEFT JOIN ucr_prd.ref_msa USING (msa_id)
  WHERE ref_agency_status.data_year IS NOT NULL AND ref_agency_yearly.is_nibrs IS TRUE AND ref_agency_status.data_year >= ", CONST_YEAR-4, " AND
  ref_agency_status.data_year <= ", CONST_YEAR, "
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
")
agency_table_df <- time_query(con, query_agency_five_years)

agency_table_df %>% write_csv(gzfile(paste0(queried_data_path,"agencies_five_years.csv.gz")), na="")


### tasks/compute_weights/01_Create_Clean_Frame.R ####
query_month <- paste0("
 SELECT
  form_month.agency_id,
  form_month.data_month AS month_num,
  form_month.data_year,
  CASE
      WHEN form_month.is_zero_report IS TRUE THEN 'Z'
      WHEN form_month.is_zero_report IS FALSE THEN 'I'
      ELSE 'U'
  END AS reported_status
 FROM ucr_prd.form_month
 WHERE 
   (form_month.is_zero_report IS TRUE OR form_month.is_zero_report IS FALSE)
   AND form_month.form_code = 'N'
   AND form_month.data_year = ", as.integer(CONST_YEAR))

if (CONST_YEAR == 2024) {
  month_df <- time_query(con, query_month) %>%
  filter(agency_id != 1206)
} else {
  month_df <- time_query(con, query_month)
}
month_df %>% write_csv(gzfile(paste0(queried_data_path,"nibrs_month_",CONST_YEAR,".csv.gz")), na="")

### tasks/missing_months/100-Run_Program.R ####
for(y in list_of_years$data_year){
  query_month_agencies <- paste0("
  SELECT
    form_month.agency_id,
    ref_agency.ori,
    form_month.data_month AS month_num,
    form_month.data_year,
    CASE
        WHEN form_month.is_zero_report IS TRUE THEN 'Z'
        WHEN form_month.is_zero_report IS FALSE THEN 'I'
        ELSE 'U'
    END AS reported_status
  FROM ucr_prd.form_month
      INNER JOIN (
          ucr_prd.ref_agency_yearly 
          LEFT JOIN ucr_prd.ref_agency USING (agency_id)
          LEFT JOIN ucr_prd.ref_agency_status USING (agency_id, data_year)
      ) ON form_month.agency_id = ref_agency_yearly.agency_id
  WHERE 
      (form_month.is_zero_report IS TRUE OR form_month.is_zero_report IS FALSE)
      AND form_month.form_code = 'N'
      AND ref_agency_yearly.is_nibrs IS TRUE
      AND ref_agency_status.data_year IS NOT NULL
      AND form_month.data_year = ", as.integer(y))
  log_debug(paste0("Run month agencies query for: ", y))
  if (y == 2024) {
    month_agencies_df <- time_query(con, query_month_agencies) %>%
    filter(agency_id != 1206)
  }
  else {
    month_agencies_df <- time_query(con, query_month_agencies)
  }
  write_csv(month_agencies_df, gzfile(paste0(queried_data_path, "nibrs_month_agencies_", y, ".csv.gz")), na = "")
  rm(month_agencies_df)

}

### tasks/create_nibrs_extracts/victim_offender_relationship/00_Extract_V_O_Rel.Rmd ####
query_victim_offender_rel_year <- paste0("
 SELECT 
  EXTRACT(year FROM nibrs_incident.incident_date) as data_year,
  nibrs_incident.incident_id AS incident_id,
  nibrs_victim.victim_id AS victim_id,
  nibrs_offender.offender_id AS offender_id,
  lkup_nibrs_relationship.relationship_code AS relationship_code,
  lkup_nibrs_relationship.name AS relationship_name
 FROM 
  ucr_prd.nibrs_incident nibrs_incident
  LEFT JOIN ucr_prd.nibrs_victim nibrs_victim ON nibrs_incident.incident_id = nibrs_victim.incident_id
  LEFT JOIN ucr_prd.nibrs_offender nibrs_offender ON nibrs_incident.incident_id = nibrs_offender.incident_id
  LEFT JOIN ucr_prd.nibrs_victim_offender_relationship nibrs_victim_offender_relationship 
    ON nibrs_victim.victim_id = nibrs_victim_offender_relationship.victim_id 
    AND nibrs_offender.offender_id = nibrs_victim_offender_relationship.offender_id
  LEFT JOIN ucr_prd.lkup_nibrs_relationship lkup_nibrs_relationship 
    ON nibrs_victim_offender_relationship.relationship_code = lkup_nibrs_relationship.relationship_code
 WHERE 
  EXTRACT(year FROM nibrs_incident.incident_date) = ", CONST_YEAR)
vic_off_rel_df <- time_query(con, query_victim_offender_rel_year)
vic_off_rel_df %>% write_csv(gzfile(paste0(outputPipelineDir,"/artifacts/00_Victim_Offender_rel_extract.csv.gz")), na="")

### tasks/generate_estimates/Setup_part1_bystate/00a_Create_Datasets_full.Rmd ####
query_agencies_population_ct <- paste0("
 SELECT
  ref_agency_status.data_year,
  ref_agency.ori,
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
 FROM ucr_prd.ref_agency_yearly
  LEFT JOIN ucr_prd.ref_agency USING (agency_id)
  LEFT JOIN ucr_prd.ref_state USING (state_id)
  LEFT JOIN ucr_prd.ref_agency_status USING (agency_id, data_year)
  LEFT JOIN ucr_prd.ref_submitting_agency USING (agency_id)
  LEFT JOIN ucr_prd.ref_agency_type USING (agency_type_id)
 WHERE ref_agency_status.data_year IS NOT NULL AND ref_agency_yearly.is_nibrs IS TRUE"
)
agencies_pop_ct_df <- time_query(con, query_agencies_population_ct)
agencies_pop_ct_df %>% write_csv(gzfile(paste0(queried_data_path,"raw_agencies_table.csv.gz")), na="")

# 
query_nibrs_col_types <- paste0("
 SELECT DISTINCT DATA_TYPE,COLUMN_NAME
 
 FROM INFORMATION_SCHEMA.COLUMNS
 
 WHERE TABLE_NAME='nibrs_incident' OR
  TABLE_NAME='nibrs_offender' OR
  TABLE_NAME='nibrs_arrestee' OR
  TABLE_NAME='nibrs_arrest_type' OR
  TABLE_NAME='nibrs_arrestee_weapon' OR
  TABLE_NAME='nibrs_weapon_type' OR
  TABLE_NAME='agencies' OR
  TABLE_NAME='nibrs_bias_motivation' OR
  TABLE_NAME='nibrs_bias_list' OR
  TABLE_NAME='nibrs_weapon' OR
  TABLE_NAME='nibrs_victim' OR
  TABLE_NAME='nibrs_victim_offense' OR
  TABLE_NAME='nibrs_offense' OR
  TABLE_NAME='nibrs_offense_type' OR
  TABLE_NAME='nibrs_cleared_except' OR
  TABLE_NAME='nibrs_month'
")
nibrs_col_types_df <- time_query(con, query_nibrs_col_types) %>% 
  subset(duplicated(column_name)==FALSE)
nibrs_col_types_df %>% write_csv(gzfile(paste0(queried_data_path,"nibrs_col_types.csv.gz")), na="")

dbDisconnect(con)

invisible(gc())
rm(list=c(ls(pattern="query_*"), ls(pattern="*_df"), ls(pattern="*list*")))