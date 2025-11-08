library("rmarkdown")
library("tidyverse")
library("rjson")

#Read in the common functions to be used in R
source(here::here("tasks/logging.R"))
source(here::here("tasks/impute_items/0-Common_functions_for_imputation.R"))


#input/output directories for pipeline artifacts
outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")
inputPipelineDir <- Sys.getenv("INPUT_PIPELINE_DIR")
external_path <- Sys.getenv("EXTERNAL_FILE_PATH")

queried_data_path = paste0(outputPipelineDir, "/initial_tasks_output/database_queries/") # path where queried data is stored

filepathout = paste0(outputPipelineDir, "/markdown/") #output path for markdown files

if (! dir.exists(filepathout)) {
  dir.create(filepathout, recursive = TRUE)
}

der_file_path = paste0(outputPipelineDir, "/indicator_table_extracts/") #output path for all the data extracts

if (! dir.exists(der_file_path)) {
  dir.create(der_file_path, recursive = TRUE)
}

initial_inputs_path = paste0(inputPipelineDir, "/initial_tasks_output/")

#External files json
input_folder <- sprintf("%s", inputPipelineDir)
file_locs <- fromJSON(file = sprintf("%s/external_file_locations.json", input_folder))

#set-up year
CONST_YEAR <- Sys.getenv("DATA_YEAR")

#get the list of all objects created in memory up to this point
keep_objs = ls(all=TRUE)

#RUN THE PROGRAM

gc(rm(list= ls(all=TRUE)[! (ls(all=TRUE) %in% c("keep_objs",keep_objs))]))

log_info("02_Create_Datasets_Agency_ORI.Rmd starting...")
rmarkdown::render("02_Create_Datasets_Agency_ORI.Rmd", output_format =html_document(),
                  output_file = paste0(filepathout, "02_Create_Datasets_Agency_ORI.html"), envir = new.env(), quiet = TRUE)
gc()
