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

Sys.setenv(VROOM_CONNECTION_SIZE=500072*2)

print(paste0("Current table: ",temp.table)) #%>%

source("table_ori_all_step4.R")
