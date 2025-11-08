library(rmarkdown)
library(tidyverse)
library(DBI)
library(rjson)

#### RUNNING NIBRS WEIGHTING CODE TO IDENTIFY NIBRS RESPONDENTS ####
# setwd("../../tasks/compute_weights/")
# 
# source("../../tasks/compute_weights/01_Create_Clean_Frame.R")
# 
# source("../../tasks/compute_weights/02_Weights_Data_Setup.R")
# #### END NIBRS CODE ####
# 
# ## reset everything
# gc(rm(list=ls()))
# 
# setwd("../../srs/block_imputation/")

source(here::here("tasks/logging.R"))
source(here::here("tasks/impute_items/0-Common_functions_for_imputation.R"))

inputPipelineDir <- Sys.getenv("INPUT_PIPELINE_DIR")
outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")

filepathin = paste0(inputPipelineDir, "/srs/converted/")
outlier_detection_in = paste0(inputPipelineDir, "/outlier_data/") #output path for data
indicator_table_extracts_in = paste0(inputPipelineDir,"/indicator_table_extracts/")																				   
block_imputation_output = paste0(outputPipelineDir, "/srs/block_imputation/")
nibrs_weights_in = paste0(outputPipelineDir, "/weighting/Data")
raw_srs_file_path = paste0(inputPipelineDir, "/initial_tasks_output/")

if (! dir.exists(block_imputation_output)) {
  dir.create(block_imputation_output, recursive = TRUE)
}

# YEAR
year <- Sys.getenv("DATA_YEAR")

#Run programs based on year


if(as.numeric(year) %in% c(1993)){
  log_debug("Running the no outlier version")
  source("01_BlockImputation_SRS_no_outlier_LR.R")  
}else if(as.numeric(year) %in% c(1994)){
  log_debug("Running the 1994 version")
  source("01_BlockImputation_SRS_no_outlier_LR_1994.R")     
}else if(as.numeric(year) %in% c(1996)){
  log_debug("Running the 1996 version")
  source("01_BlockImputation_SRS_LR_1996.R")
}else if(as.numeric(year) %in% c(2013)){  
  log_debug("Running the 2013 version")
  source("01_BlockImputation_SRS_LR_2013.R") 
}else{
  log_debug("Running the normal version")
  source("01_BlockImputation_SRS.R")  
}

