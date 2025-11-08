library(tidyverse)
library(openxlsx)
library(DBI)
library(DT)
library(lubridate)
library(data.table)
library(logger)

DER_TABLE_NAME <- Sys.getenv("DER_TABLE_NAME")
inputPipelineDir <- Sys.getenv("INPUT_PIPELINE_DIR")
der_file_path = paste0(inputPipelineDir, "/indicator_table_extracts/")
in_file_path = paste0(inputPipelineDir, "/indicator_table_single_intermediate/")

source(here::here("tasks/logging.R"), keep.source=TRUE)
source("../../../impute_items/0-Common_functions_for_imputation.R", keep.source=TRUE)

load(paste0(in_file_path,"/",DER_TABLE_NAME,"_prep_env.RData"))

log_info(paste0("Running generate_est for table ",DER_TABLE_NAME))
log_debug(system("free -mh", intern = FALSE))

args = commandArgs(trailingOnly=TRUE)
if (length(args)==0) {
  stop("This script expects a column number", call.=FALSE)
} else if (length(args)==1) {
  column <- as.integer(args[1])
}

num_cols <- length(collist)
if (column %in% c(1:num_cols)) {
  subsetvareq1 = collist[column]
} else {
  stop(paste0("This script expects a column number between 1 and ", num_cols), call.=FALSE)
}

log_info(paste0("Calling generate_est in", DER_TABLE_NAME ,"for column:",column," and subsetvareq1: ",subsetvareq1))

# There are three special cases for this file: 2b, 3c, and DM6-DM9.
# if the table is 2b we use the additionalweight argument
if (DER_TABLE_NAME == "2b") {

  if (subsetvareq1 == "der_motor_vehicle_theft") {
    additionalweight="der_automobile_stolen_count"
  } else {
    additionalweight="one"
  }
  data  <- generate_est(maindata=main, subsetvareq1=subsetvareq1, column_number=column, additionalweight=additionalweight)
  saveRDS(data,file=paste0(out_file_path,"/data_",DER_TABLE_NAME,"_",column,".rds"))

} else if (DER_TABLE_NAME == "3c") {
  # if the table is 3c then we filter the table to victim==business before running generate_est
  data  <- generate_est(maindata=main %>% filter(der_victim_business == 1), subsetvareq1=subsetvareq1, column_number=column)
  saveRDS(data,file=paste0(out_file_path,"/data_",DER_TABLE_NAME,"_",column,".rds"))

  log_info("Calling generate_est again but this time for der_victim_other_non_person == 1")
  data2  <- generate_est(maindata=main %>% filter(der_victim_other_non_person == 1), subsetvareq1=subsetvareq1, column_number=column)
  saveRDS(data2,file=paste0(out_file_path,"/data_",DER_TABLE_NAME,"_",column + 100,".rds"))

}else if (DER_TABLE_NAME %in% c("DM6","DM7","DM8","DM9")) {
  
  # if the table is DM6-9 we have two subsetvareq arguments to be passed to the function
  subsetvareq2 = collist2[column]
  data  <- generate_est(maindata=main, subsetvareq1=subsetvareq1, subsetvareq2=subsetvareq2, column_number=column)
  saveRDS(data,file=paste0(out_file_path,"/data_",DER_TABLE_NAME,"_",column,".rds"))

}else if (DER_TABLE_NAME %in% c("5a", "5b")) {
  
  #Need to pass on two main data 
  #One for the group A incidents
  #The other one for the group B arrestee
  
  data  <- generate_est(maindata=main, maindatagroupb=main_group_b, subsetvareq1=subsetvareq1, column_number=column)
  saveRDS(data,file=paste0(out_file_path,"/data_",DER_TABLE_NAME,"_",column,".rds"))  
  
} else {
  data  <- generate_est(maindata=main, subsetvareq1=subsetvareq1, column_number=column)
  saveRDS(data,file=paste0(out_file_path,"/data_",DER_TABLE_NAME,"_",column,".rds"))
}

log_debug(system("free -mh", intern = FALSE))
log_debug("Done")