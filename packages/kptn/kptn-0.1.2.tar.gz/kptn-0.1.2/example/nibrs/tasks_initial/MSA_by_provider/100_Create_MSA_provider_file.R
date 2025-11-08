
library("tidyverse")

source(here::here("tasks/logging.R"))

con <- dbConnect(RPostgres::Postgres())
outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")
external_path <- Sys.getenv("EXTERNAL_FILE_PATH")
inputPipelineDir <- Sys.getenv("INPUT_PIPELINE_DIR")

input_folder <- sprintf("%s", inputPipelineDir)

filepathout = paste0(outputPipelineDir, "/initial_tasks_output/")

if (! dir.exists(filepathout)) {
  dir.create(filepathout, recursive = TRUE)
}

DATA_YEAR <- Sys.getenv("DATA_YEAR")

# query to get the file we need
msa_query <- paste0(
  "select distinct ag.legacy_ori as agency_ori, in_msa, srs.population
  from ucr_prd.est_12mc_reta_counts srs
  join ucr_prd.ref_agency ag using (agency_id)
  where data_year = ", DATA_YEAR
)

# some transformations to be consistent with prior file from CJIS
msa <- time_query(con, msa_query) %>%
  mutate(in_msa = ifelse(in_msa == "TRUE", "Y","N")) %>%
  select(agency_ori, in_msa, population) %>%
  rename(ORI = agency_ori,
         In_MSA = in_msa,
         `Estimated Population` = population)

dbDisconnect(con)

write_csv(msa, paste0(filepathout, "CIUS_MSA_by_provider_", DATA_YEAR, ".csv"))