library(tidyverse)
library(openxlsx)
library(DBI)
library(DT)
library(lubridate)
library(data.table)

#Read in the common functions to be used in R
source(here::here("tasks/logging.R"))
source(here::here("tasks/impute_items/0-Common_functions_for_imputation.R"))

source("util.R")

inputPipelineDir <- Sys.getenv("INPUT_PIPELINE_DIR")
der_file_path = paste0(inputPipelineDir, "/srs/indicator_table_extracts/")
in_file_path = paste0(inputPipelineDir, "/srs/indicator_table_single_intermediate/")

outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")
out_file_path = paste0(outputPipelineDir, "/srs/indicator_table_single_intermediate/")
load(paste0(in_file_path,"/SRS1a_prep_env.RData"))

args = commandArgs(trailingOnly=TRUE)
if (length(args)==0) {
  stop("This script expects a column number", call.=FALSE)
} else if (length(args)==1) {
  column <- as.integer(args[1])
}


log_debug(system("free -mh", intern = FALSE))

num_cols <- length(collist)
if (column %in% c(1:num_cols)) {
  subsetvareq1 = collist[column]
} else {
  stop(paste0("This script expects a column number between 1 and ", num_cols), call.=FALSE)
}

log_info(paste0("Calling generate_est in 01_TableSRS1a for column:",column," and subsetvareq1: ",subsetvareq1))
log_debug(system("free -mh", intern = FALSE))
data  <- generate_est(maindata=main, subsetvareq1=subsetvareq1, column_number=column)
datai <- paste0("data_SRS1a_",column)
log_debug(paste0("Saving data item ",datai))
log_debug(system("free -mh", intern = FALSE))
saveRDS(data,file=paste0(out_file_path,"/",datai,".rds"))
