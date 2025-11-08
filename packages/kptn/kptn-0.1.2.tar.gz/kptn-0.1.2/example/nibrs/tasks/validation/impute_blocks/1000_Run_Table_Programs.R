library("rmarkdown")
library("tidyverse")
library(rjson)


source(here::here("tasks/logging.R"))
#Read in the common functions to be used in R
source(here::here("tasks/impute_items/0-Common_functions_for_imputation.R"))


#SET UP ALL THE NECESSARY INPUT/OUTPUT PATHS
inputPipelineDir <- Sys.getenv("INPUT_PIPELINE_DIR")
outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")
external_path <- Sys.getenv("EXTERNAL_FILE_PATH")
validation_output_path <- paste0(outputPipelineDir, "/validation_outputs/")
input_files_folder <- paste0(inputPipelineDir, "/initial_tasks_output/")

file_locs <- fromJSON(file = sprintf("%s/external_file_locations.json", inputPipelineDir))

if (! dir.exists(validation_output_path)) {
  dir.create(validation_output_path, recursive = TRUE)
}

input_block_imp = paste0(inputPipelineDir, "/block_imputation_data/")

year <- Sys.getenv("DATA_YEAR")

read_csv <- partial(read_csv, guess_max = 1000000) #For now, read thru the 1st 1,000,000 rows to determine variable type
write.csv0 <- partial(write.csv, row.names = FALSE, na ="0")
write.csv <- partial(write.csv, row.names = FALSE, na ="")

roundfunction <- partial(round, digits=4)

#Run programs
log_info("Running '3_Check_block_imputation.Rmd'")
rmarkdown::render(
  "3_Check_block_imputation.Rmd", 
  output_format =html_document(), 
  envir = new.env(), 
  output_file = paste0(validation_output_path, "3_Check_block_imputation_",year,".html")
)