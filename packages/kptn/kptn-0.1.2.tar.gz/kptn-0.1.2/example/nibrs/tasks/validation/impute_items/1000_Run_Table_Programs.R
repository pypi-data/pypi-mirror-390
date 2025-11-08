library("rmarkdown")
library("tidyverse")
library("data.table")
library(readxl)

source(here::here("tasks/logging.R"))
#Read in the common functions to be used in R
source(here::here("tasks/impute_items/0-Common_functions_for_imputation.R"))


#SET UP ALL THE NECESSARY INPUT/OUTPUT PATHS
inputPipelineDir <- Sys.getenv("INPUT_PIPELINE_DIR")
outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")
validation_output_path <- paste0(outputPipelineDir, "/validation_outputs/")

if (! dir.exists(validation_output_path)) {
  dir.create(validation_output_path, recursive = TRUE)
}

input_item_imp = paste0(inputPipelineDir, "/item_imputation_data/") #output path for data
extract_data = paste0(inputPipelineDir, "/indicator_table_extracts/")

year <- Sys.getenv("DATA_YEAR")

read_csv <- partial(read_csv, guess_max = 1000000) #For now, read thru the 1st 1,000,000 rows to determine variable type
write.csv0 <- partial(write.csv, row.names = FALSE, na ="0")
write.csv <- partial(write.csv, row.names = FALSE, na ="")
read_xlsx <- partial(read_xlsx, guess_max = 1000000)

roundfunction <- partial(round, digits=4)

#Run programs
log_info("Running '1_Check_imputation_demographics.Rmd'")
rmarkdown::render(
  "1_Check_imputation_demographics.Rmd",
  output_format =html_document(),
  envir = new.env(),
  output_file = paste0(validation_output_path, "1_Check_imputation_demographics_",year,".html")
)

log_info("Running '2_Check_imputation_relationship.Rmd'")
rmarkdown::render(
  "2_Check_imputation_relationship.Rmd",
  output_format =html_document(),
  envir = new.env(),
  output_file = paste0(validation_output_path, "2_Check_imputation_relationship_",year,".html")
)

log_info("Running '4_Check_before_and_after_imputation_merge.Rmd'")
rmarkdown::render(
  "4_Check_before_and_after_imputation_merge.Rmd",
  output_format =html_document(),
  envir = new.env(),
  output_file = paste0(validation_output_path, "4_Check_before_and_after_imputation_merge_",year,".html")
)

log_info("Running '5_Check_imputation_ethnicity.Rmd'")
rmarkdown::render(
  "5_Check_imputation_ethnicity.Rmd",
  output_format =html_document(),
  envir = new.env(),
  output_file = paste0(validation_output_path, "5_Check_imputation_ethnicity_",year,".html")
)