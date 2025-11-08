library(reshape2)
library(tidyverse)
library(openxlsx)
library(copula)
library(rjson)
library(data.table)
source(here::here("tasks/logging.R"))


outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")
inputPipelineDir <- Sys.getenv("INPUT_PIPELINE_DIR")
external_path <- Sys.getenv("EXTERNAL_FILE_PATH")

output_folder <- sprintf("%s", outputPipelineDir)
input_folder <- sprintf("%s", inputPipelineDir)

final_path <- paste0(inputPipelineDir, "/indicator_table_estimates/")

output_copula_folder <- file.path(outputPipelineDir, "copula_imputation")
output_copula_data_folder <- file.path(output_copula_folder, "Data")
output_copula_temp_folder <- file.path(output_copula_folder, "Temp")
validation_output_path <- paste0(outputPipelineDir, "/validation_outputs/copula_imputation/split/")

directories <- c(output_copula_folder, output_copula_data_folder, output_copula_temp_folder, validation_output_path)

for (d in directories) {
  if (! dir.exists(d)) {
    dir.create(d, recursive = TRUE)
  }
}

file_locs <- fromJSON(file = sprintf("%s/external_file_locations.json", input_folder))

year <- Sys.getenv("DATA_YEAR")
temp.table <- Sys.getenv("TABLE_NAME")
temp.perm <- Sys.getenv("DER_CURRENT_PERMUTATION_NUM")

log_info(paste0("Running Copula_Imputation_Instance_Step1_Summary.R for table ",temp.table, " permutation ",temp.perm))

source("Copula_Imputation_Instance_Step1_Summary.R", keep.source=TRUE)
log_debug(system("free -mh", intern = FALSE))
