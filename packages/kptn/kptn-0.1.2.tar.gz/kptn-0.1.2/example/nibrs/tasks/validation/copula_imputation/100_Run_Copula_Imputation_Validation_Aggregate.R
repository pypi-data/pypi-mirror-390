library(reshape2)
library(tidyverse)
library(openxlsx)
library(copula)
library(rjson)
library(data.table)
source(here::here("tasks/logging.R"))

outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")
inputPipelineDir <- Sys.getenv("INPUT_PIPELINE_DIR")
external_path <- Sys.getenv("EXTERNAL_FILE_PATH")

output_folder <- sprintf("%s", outputPipelineDir)
input_folder <- sprintf("%s", inputPipelineDir)

final_path <- paste0(inputPipelineDir, "/indicator_table_estimates/")

output_copula_folder <- file.path(outputPipelineDir, "copula_imputation")
output_copula_data_folder <- file.path(output_copula_folder, "Data")
output_copula_temp_folder <- file.path(output_copula_folder, "Temp")
validation_output_path <- paste0(outputPipelineDir, "/validation_outputs/copula_imputation/split")
validation_output_path_summary <- paste0(outputPipelineDir, "/validation_outputs/copula_imputation/")

file_locs <- fromJSON(file = sprintf("%s/external_file_locations.json", input_folder))

year <- Sys.getenv("DATA_YEAR")
log_info("Running Copula_Imputation_Aggregate_Step1_Summary.R")
#Get list of summary files and then read them in
files <- list.files(validation_output_path,full.names=TRUE) %>%
  str_subset("Table_\\w+_Perm_\\d+_Step1_Weighted_vs_Copula_Comparison.csv")
  
#Read in files from earlier program
dat <- map(files,function(temp.file){
  temp.dat <- fread_logging(temp.file)
}) %>% bind_rows() %>% mutate(propDiff=(copula_sum_all-weighted_sum)/weighted_sum) %>% subset(abs(propDiff)>=0.10)
	
log_info(paste0("Number of estimates to manually review: ",nrow(dat)))
  
#Export results
dat %>% fwrite_wrapper(file=paste0(validation_output_path_summary,"All_Table_X_Perm_Step1_Flagged_Estimates.csv"))
log_debug(system("free -mh", intern = FALSE))
