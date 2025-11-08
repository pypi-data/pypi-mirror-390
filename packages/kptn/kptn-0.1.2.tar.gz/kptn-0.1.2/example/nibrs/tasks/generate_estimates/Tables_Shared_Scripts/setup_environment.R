library("tidyverse")
library("rjson")
library(openxlsx)
library(DBI)
library(DT)
library(lubridate)
library(data.table)

read_csv <- partial(read_csv, guess_max = 1000000) #For now, read thru the 1st 1,000,000 rows to determine variable type
write.csv0 <- partial(write.csv, row.names = FALSE, na ="0")
write.csv <- partial(write.csv, row.names = FALSE, na ="")

#Read in the common functions to be used in R
source(here::here("tasks/logging.R"), keep.source=TRUE)
source("../../../impute_items/0-Common_functions_for_imputation.R", keep.source=TRUE)

#input/output directories for pipeline artifacts
outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")
inputPipelineDir <- Sys.getenv("INPUT_PIPELINE_DIR")
external_path <- Sys.getenv("EXTERNAL_FILE_PATH")
DER_TABLE_NAME <- Sys.getenv("DER_TABLE_NAME")

filepathout = paste0(outputPipelineDir, "/markdown/") #output path for markdown files

if (! dir.exists(filepathout)) {
  dir.create(filepathout, recursive = TRUE)
}

der_file_path = paste0(inputPipelineDir, "/indicator_table_extracts/") #input path where all the data extracts are located

if (! dir.exists(der_file_path)) {
  dir.create(der_file_path, recursive = TRUE)
}

out_file_path = paste0(outputPipelineDir, "/indicator_table_single_intermediate/")

if (! dir.exists(out_file_path)) {
  dir.create(out_file_path, recursive = TRUE)
}

final_path = paste0(outputPipelineDir, "/indicator_table_estimates/") #this is where the final estimates go

if (! dir.exists(final_path)) {
  dir.create(final_path, recursive = TRUE)
}

final_path_after_variance = paste0(outputPipelineDir, "/indicator_table_estimates_after_variance/")

if (! dir.exists(final_path_after_variance)) {
  dir.create(final_path_after_variance, recursive = TRUE)
}

item_imp_path = paste0(outputPipelineDir, "/item_imputation_data/") #item imputation (including victim/offender relationship)
block_imp_path = paste0(outputPipelineDir, "/block_imputation_data/") #block imputation
weight_path = paste0(outputPipelineDir, "/weighting/Data/") #weights
der_bystate_file_path = paste0(outputPipelineDir, "/indicator_table_extracts_bystate/") #output path for state-level extracts


#External files json
input_folder <- sprintf("%s", inputPipelineDir)
file_locs <- fromJSON(file = sprintf("%s/external_file_locations.json", input_folder))

#set-up year
CONST_YEAR <- Sys.getenv("DATA_YEAR")

#for the single run code we want to point it to the NATIONAL population information
DER_CURRENT_PERMUTATION_NUM <- 1
Sys.setenv("DER_CURRENT_PERMUTATION_NUM" = DER_CURRENT_PERMUTATION_NUM)

#source code for a lot of shared functions (needs to run after setting year & permutation or it will error)
source("../../POP_Total_code_assignment.R")