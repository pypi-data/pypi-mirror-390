library(rmarkdown)
library(tidyverse)
library(DBI)
library(rjson)

source(here::here("tasks/logging.R"))
source(here::here("tasks/impute_items/0-Common_functions_for_imputation.R"))
source("Recode_Other_Agency_Function.R")

inputPipelineDir <- Sys.getenv("INPUT_PIPELINE_DIR")
outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")
external_path <- Sys.getenv("EXTERNAL_FILE_PATH")

#filepathin = paste0(inputPipelineDir, "/srs/converted/")
#outlier_detection_in = paste0(inputPipelineDir, "/outlier_data/") #output path for data
#indicator_table_extracts_in = paste0(inputPipelineDir,"/indicator_table_extracts/")																				   
officer_imputation_path = paste0(outputPipelineDir, "/initial_tasks_output/officer_imputation/")

if (! dir.exists(officer_imputation_path)) {
  dir.create(officer_imputation_path, recursive = TRUE)
}

#Create the path to the initial outputs folder
initial_tasks_output_path = paste0(outputPipelineDir, "/initial_tasks_output/")

file_locs <- fromJSON(file = sprintf("%s/external_file_locations.json", inputPipelineDir))

# YEAR
CONST_YEAR <- Sys.getenv("DATA_YEAR")

source("01_Impute_Officers_30yr.R")