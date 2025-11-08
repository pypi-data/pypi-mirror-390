library(tidyverse)
library(openxlsx)
library(DBI)
library(DT)
library(lubridate)
library(data.table)

source(here::here("tasks/logging.R"))
source(here::here("tasks/impute_items/0-Common_functions_for_imputation.R"))

source("util.R")

outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")
CONST_OUTPUT_PATH = paste0(outputPipelineDir, "/indicator_table_estimates/")

#Read in the Table GV2a_Reporting_Database_part1.csv file
raw_gv2a_rd <- fread(paste0(CONST_OUTPUT_PATH, "Table GV2a_Reporting_Database_part1.csv"))

#Need to drop the rate rows
raw_gv2a_rd1 <- raw_gv2a_rd %>%
  filter(estimate_type_num != 3) #3 is rate

#Check the size
dim(raw_gv2a_rd1)
dim(raw_gv2a_rd)

#Read in the Table GV2b_Reporting_Database.csv file
raw_gv2b_rd <- fread(paste0(CONST_OUTPUT_PATH, "Table GV2b_Reporting_Database_part1.csv"))

#Need to keep the rate rows
raw_gv2b_rd1 <- raw_gv2b_rd %>%
  filter(estimate_type_num == 3) #3 is rate

#Combined the two files together and output
raw_final <- bind_rows(raw_gv2a_rd1, raw_gv2b_rd1) 

#Make sure that the number of rows are correct
dim(raw_final)
dim(raw_gv2a_rd)

#Output new reporting database
raw_final %>%
  write.csv(paste0(CONST_OUTPUT_PATH, "Table GV2a_Reporting_Database.csv"))


