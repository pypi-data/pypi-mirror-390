library("rmarkdown")
library("tidyverse")
library("rjson")

#Read in the common functions to be used in R
source(here::here("tasks/logging.R"))
source(here::here("tasks/impute_items/0-Common_functions_for_imputation.R"))
source("shared_setup_functions.R")

#input/output directories for pipeline artifacts
outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")
inputPipelineDir <- Sys.getenv("INPUT_PIPELINE_DIR")
external_path <- Sys.getenv("EXTERNAL_FILE_PATH")

queried_data_path = paste0(outputPipelineDir, "/initial_tasks_output/database_queries/") # path where queried data is stored
filepathout = paste0(outputPipelineDir, "/markdown/") #output path for markdown files

if (! dir.exists(filepathout)) {
  dir.create(filepathout, recursive = TRUE)
}

der_bystate_file_path = paste0(outputPipelineDir, "/indicator_table_extracts_bystate/") #output path for all the data extracts

if (! dir.exists(der_bystate_file_path)) {
  dir.create(der_bystate_file_path, recursive = TRUE)
}

input_files_folder <- paste0(inputPipelineDir, "/initial_tasks_output/")

#External files json
input_folder <- sprintf("%s", inputPipelineDir)
file_locs <- fromJSON(file = sprintf("%s/external_file_locations.json", input_folder))

#set-up year
CONST_YEAR <- Sys.getenv("DATA_YEAR")

#RUN THE PROGRAMS
input_state <- Sys.getenv("INPUT_STATE")

log_info(paste0(input_state,": 000a_Create_Extracts_Carjacking.Rmd starting..."))
rmarkdown::render("000a_Create_Extracts_Carjacking.Rmd", output_format =html_document(),
                  output_file = paste0(filepathout, "000a_Create_Extracts_Carjacking",input_state,".html"), envir = new.env(), quiet = TRUE)

log_info(paste0(input_state,": 00a_Create_Datasets_full.Rmd starting..."))
rmarkdown::render("00a_Create_Datasets_full.Rmd", output_format =html_document(),
                  output_file = paste0(filepathout, "00a_Create_Datasets_full",input_state,".html"), envir = new.env(), quiet = TRUE)

log_info(paste0(input_state,": 00_Create_Datasets_full_Drug_Module.Rmd starting..."))
rmarkdown::render("00_Create_Datasets_full_Drug_Module.Rmd", output_format =html_document(),
                  output_file = paste0(filepathout, "00_Create_Datasets_full_Drug_Module",input_state,".html"), envir = new.env(), quiet = TRUE)
