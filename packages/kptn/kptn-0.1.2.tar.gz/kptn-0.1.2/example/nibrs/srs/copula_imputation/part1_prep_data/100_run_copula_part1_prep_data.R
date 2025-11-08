#This program is intended to serve as the master program for SRS copula
library(reshape2)
library(tidyverse)
library(openxlsx)
library(copula)
library(rjson)
library(logger)
library(data.table)
library(parallel)
source(here::here("tasks/logging.R"))

outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")
inputPipelineDir <- Sys.getenv("INPUT_PIPELINE_DIR")
external_path <- Sys.getenv("EXTERNAL_FILE_PATH")

output_folder <- sprintf("%s", outputPipelineDir)
input_folder <- sprintf("%s", inputPipelineDir)

input_estimate_folder <- paste0(inputPipelineDir, "/srs/indicator_table_estimates/")
input_extract_folder <- paste0(inputPipelineDir, "/srs/indicator_table_extracts/")
input_files_folder <- paste0(inputPipelineDir, "/initial_tasks_output/")

file_locs <- fromJSON(file = sprintf("%s/external_file_locations.json", input_folder))

output_copula_folder <- file.path(outputPipelineDir, "/srs/copula_imputation")
output_copula_data_folder <- file.path(output_copula_folder, "Data")
output_copula_temp_folder <- file.path(output_copula_folder, "Temp")


directories <- c(input_estimate_folder, input_extract_folder, output_copula_folder, output_copula_data_folder)

for (d in directories) {
  if (! dir.exists(d)) {
    dir.create(d, recursive = TRUE)
  }
}

file_locs <- fromJSON(file = sprintf("%s/external_file_locations.json", input_folder))

year <- Sys.getenv("DATA_YEAR")
temp.table <- Sys.getenv("TABLE_NAME")

source("table_ORI_all_SRS.R",local=TRUE,echo=TRUE)