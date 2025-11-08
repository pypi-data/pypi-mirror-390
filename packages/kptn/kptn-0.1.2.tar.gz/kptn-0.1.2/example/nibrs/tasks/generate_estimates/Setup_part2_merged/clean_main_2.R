library("rmarkdown")
library("tidyverse")
library("rjson")
library(openxlsx)
library(DBI)
library(DT)
library(lubridate)
library(data.table)

#Read in the common functions to be used in R
source(here::here("tasks/logging.R"))
source(here::here("tasks/impute_items/0-Common_functions_for_imputation.R"))

options <- c(
  "incident",
  "offenses",
  "arrestee",
  "LEOKA",
  "arrest_code",
  "group_b_arrestee"
)

source_type <- Sys.getenv("SOURCE_TYPE")

if(source_type == "incident"){
  main_file = "recoded_all_Offenses_recoded_incident.csv.gz"
} else if(source_type == "offenses"){
  main_file = "recoded_all_Offenses_recoded_offenses.csv.gz"
} else if(source_type == "arrestee"){
  main_file = "recoded_all_Offenses_recoded_arrestee.csv.gz"
} else if(source_type == "LEOKA"){
  main_file = "NIBRS_LEO_Assaulted.csv.gz"
} else if(source_type == "arrest_code"){
  main_file = "recoded_all_recoded_arrestee_arrest_code.csv.gz"
} else if(source_type == "group_b_arrestee"){
  main_file = "recoded_all_recoded_arrestee_groupb_arrest_code.csv.gz"    
} else {
  stop(paste0("ERROR: first argument was not one of these:",toString(options)," it was",source_type), call.=FALSE)
}

log_info(paste0("Running clean main for ",main_file))

#input/output directories for pipeline artifacts
outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")
inputPipelineDir <- Sys.getenv("INPUT_PIPELINE_DIR")
external_path <- Sys.getenv("EXTERNAL_FILE_PATH")

der_file_path = paste0(outputPipelineDir, "/indicator_table_extracts/") #output path for all the data extracts

#External files json
input_folder <- sprintf("%s", inputPipelineDir)
file_locs <- fromJSON(file = sprintf("%s/external_file_locations.json", input_folder))

#set-up year
CONST_YEAR <- Sys.getenv("DATA_YEAR")

#for the single run code we want to point it to the NATIONAL population information
DER_CURRENT_PERMUTATION_NUM <- 1
Sys.setenv("DER_CURRENT_PERMUTATION_NUM" = DER_CURRENT_PERMUTATION_NUM)

log_debug("About to run population file")
log_debug(system("free -mh", intern = FALSE))

#source code for a lot of shared functions (needs to run after setting year & permutation or it will error)
source("../POP_Total_code_assignment.R")

log_debug("After running population file")
log_debug(system("free -mh", intern = FALSE))

TEMP_main <- fread(paste0(der_file_path,"TEMP_cleaned_",main_file))

log_debug("About to kick off clean_main_part_2")
log_debug(system("free -mh", intern = FALSE))

#Filter to eligible agencies
main <- TEMP_main %>% clean_main_part_2()

log_debug(paste0("Writing cleaned_",main_file))
log_debug(system("free -mh", intern = FALSE))

# main %>% write_csv(gzfile(paste0(der_file_path,"cleaned_",main_file)), na="")

fwrite_wrapper(main,paste0(der_file_path, "cleaned_", main_file), na = "")

log_debug("Done")
log_debug(system("free -mh", intern = FALSE))
