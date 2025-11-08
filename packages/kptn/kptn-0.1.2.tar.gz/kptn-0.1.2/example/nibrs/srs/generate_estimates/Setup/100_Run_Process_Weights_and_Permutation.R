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

filepathout = paste0(outputPipelineDir, "/srs/markdown/") #output path for markdown files

if (! dir.exists(filepathout)) {
  dir.create(filepathout, recursive = TRUE)
}

der_file_path = paste0(outputPipelineDir, "/srs/indicator_table_extracts/") #output path for all the data extracts

if (! dir.exists(der_file_path)) {
  dir.create(der_file_path, recursive = TRUE)
}

final_path = paste0(outputPipelineDir, "/srs/indicator_table_estimates/") #this is where the final estimates go

if (! dir.exists(final_path)) {
  dir.create(final_path, recursive = TRUE)
}

final_path_after_variance = paste0(outputPipelineDir, "/srs/indicator_table_estimates_after_variance/")

if (! dir.exists(final_path_after_variance)) {
  dir.create(final_path_after_variance, recursive = TRUE)
}

#item_imp_path = paste0(outputPipelineDir, "/item_imputation_data/") #item imputation (including victim/offender relationship)
block_imp_path = paste0(outputPipelineDir, "/srs/block_imputation_data/") #block imputation
weight_path = paste0(outputPipelineDir, "/srs/weighting/Data/") #weights
#der_bystate_file_path = paste0(outputPipelineDir, "/indicator_table_extracts_bystate/") #output path for state-level extracts
input_files_path = paste0(inputPipelineDir, "/initial_tasks_output/")
variance_analysis_data_folder <- file.path(outputPipelineDir, "variance_analysis_dataset", "Data")

#External files json
input_folder <- sprintf("%s", inputPipelineDir)
file_locs <- fromJSON(file = sprintf("%s/external_file_locations.json", input_folder))

#set-up year
CONST_YEAR <- Sys.getenv("DATA_YEAR")

#for the single run code we want to point it to the NATIONAL population information
DER_CURRENT_PERMUTATION_NUM <- 1
Sys.setenv("DER_CURRENT_PERMUTATION_NUM" = DER_CURRENT_PERMUTATION_NUM)

#source code for a lot of shared functions (needs to run after setting year & permutation or it will error)
source("../POP_Total_code_assignment.R")

#get the list of all objects created in memory up to this point
keep_objs = ls(all=TRUE)

#RUN THE PROGRAMS
#DATA SETUP
gc(rm(list= ls(all=TRUE)[! (ls(all=TRUE) %in% c("keep_objs",keep_objs))]))
log_info("01_Process_Weights_and_permutation_variable.Rmd starting...")
gc(rm(list= ls(all=TRUE)[! (ls(all=TRUE) %in% c("keep_objs",keep_objs))]))
rmarkdown::render("01_Process_Weights_and_permutation_variable.Rmd", output_format = html_document(),
                  output_file = paste0(filepathout, "01_Process_Weights_and_permutation_variable.html"), envir = new.env(), quiet = TRUE)
gc()
