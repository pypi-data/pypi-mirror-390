library(reshape2)
library(tidyverse)
library(openxlsx)
library(copula)
library(rjson)
library(data.table)
source(here::here("tasks/logging.R"))

options <- c(
  "popResidAgcy_cbi>0 & nDemoMissing==0",
  "popResidAgcy_cbi>0 & nDemoMissing>0",
  "popResidAgcy_cbi==0"
)

args = commandArgs(trailingOnly=TRUE)
if (length(args)==0) {
  stop(paste0("This script expects an argument one of these options:",toString(options)), call.=FALSE)
} else if (length(args)==1) {
  # default output file
  temp.subset <- args[1]
}

outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")
inputPipelineDir <- Sys.getenv("INPUT_PIPELINE_DIR")
external_path <- Sys.getenv("EXTERNAL_FILE_PATH")

output_folder <- sprintf("%s", outputPipelineDir)
input_folder <- sprintf("%s", inputPipelineDir)

input_estimate_folder <- paste0(inputPipelineDir, "/indicator_table_estimates/")
input_extract_folder <- paste0(inputPipelineDir, "/indicator_table_extracts/")

output_copula_folder <- file.path(outputPipelineDir, "copula_imputation")
output_copula_data_folder <- file.path(output_copula_folder, "Data")
output_copula_temp_folder <- file.path(output_copula_folder, "Temp")

directories <- c(output_copula_folder, output_copula_data_folder, output_copula_temp_folder)

for (d in directories) {
  if (! dir.exists(d)) {
    dir.create(d, recursive = TRUE)
  }
}

file_locs <- fromJSON(file = sprintf("%s/external_file_locations.json", input_folder))

year <- Sys.getenv("DATA_YEAR")
temp.table <- Sys.getenv("TABLE_NAME")
temp.perm <- Sys.getenv("DER_CURRENT_PERMUTATION_NUM")
temp.colnum <- Sys.getenv("COLUMN_INDEX") %>% as.numeric()
temp.stratLvl <- Sys.getenv("STRAT_VAR") %>% as.numeric()

temp.stratVar <- "PARENT_POP_GROUP_CODE2"

#Subsets of data
subsets <- c("popResidAgcy_cbi>0 & nDemoMissing==0",
             "popResidAgcy_cbi>0 & nDemoMissing>0",
             "popResidAgcy_cbi==0")

log_info("Current step: 3")
log_info(paste0("Current table: ",temp.table, "; Current permutation: ",temp.perm))
log_info(paste0("Current subset: ", temp.subset))
log_info(paste0("Current column set: ", temp.colnum))
log_info(paste0("Current stratification level: ", temp.stratLvl))
log_debug(system("free -mh", intern = FALSE))
source("Copula_Imputation_Instance_Step3_Alt.R")
log_debug(system("free -mh", intern = FALSE))