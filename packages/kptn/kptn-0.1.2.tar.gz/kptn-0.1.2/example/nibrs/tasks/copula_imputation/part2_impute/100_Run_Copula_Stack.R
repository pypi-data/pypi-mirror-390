library(reshape2)
library(tidyverse)
library(openxlsx)
library(copula)
library(rjson)
source(here::here("tasks/logging.R"))


outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")
inputPipelineDir <- Sys.getenv("INPUT_PIPELINE_DIR")
external_path <- Sys.getenv("EXTERNAL_FILE_PATH")

output_folder <- sprintf("%s", outputPipelineDir)
input_folder <- sprintf("%s", inputPipelineDir)

input_estimate_folder <- paste0(inputPipelineDir, "/indicator_table_estimates/")
input_extract_folder <- paste0(inputPipelineDir, "/indicator_table_extracts/")

output_copula_folder <- file.path(outputPipelineDir, "copula_imputation")
output_copula_data_folder <- file.path(output_copula_folder, "Data")
filepathin_initial = paste0(inputPipelineDir, "/initial_tasks_output/")

directories <- c(output_copula_folder, output_copula_data_folder)

for (d in directories) {
  if (! dir.exists(d)) {
    dir.create(d, recursive = TRUE)
  }
}

file_locs <- fromJSON(file = sprintf("%s/external_file_locations.json", input_folder))

year <- Sys.getenv("DATA_YEAR")
temp.table <- Sys.getenv("TABLE_NAME")
temp.perm <- Sys.getenv("DER_CURRENT_PERMUTATION_NUM")

temp.stratLvls <- c(1:8)

temp.stratVars <- c("PARENT_POP_GROUP_CODE2")
temp.stratVar <- "PARENT_POP_GROUP_CODE2"

log_info(paste0("Current table: ",temp.table, "; Current permutation: ",temp.perm))
log_debug(system("free -mh", intern = FALSE))
source("Stack_Copula_Imputation_Subsets.R")
log_debug(system("free -mh", intern = FALSE))
