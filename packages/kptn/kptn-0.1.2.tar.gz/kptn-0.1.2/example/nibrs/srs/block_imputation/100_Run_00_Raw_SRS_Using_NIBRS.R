library(rmarkdown)
library(tidyverse)
library(DBI)
library(rjson)

source(here::here("tasks/logging.R"))

inputPipelineDir <- Sys.getenv("INPUT_PIPELINE_DIR")
outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")
external_path <- Sys.getenv("EXTERNAL_FILE_PATH")

filepathin = paste0(inputPipelineDir, "/srs/converted/")
outlier_detection_in = paste0(inputPipelineDir, "/outlier_data/") #output path for data
indicator_table_extracts_in = paste0(inputPipelineDir,"/indicator_table_extracts/")																				   
block_imputation_output = paste0(outputPipelineDir, "/srs/block_imputation/")
raw_srs_file_path = paste0(inputPipelineDir, "/initial_tasks_output/")

if (! dir.exists(block_imputation_output)) {
  dir.create(block_imputation_output, recursive = TRUE)
}

file_locs <- fromJSON(file = sprintf("%s/external_file_locations.json", inputPipelineDir))

# YEAR
year <- Sys.getenv("DATA_YEAR")

source("00_Raw_SRS_Using_NIBRS.R")