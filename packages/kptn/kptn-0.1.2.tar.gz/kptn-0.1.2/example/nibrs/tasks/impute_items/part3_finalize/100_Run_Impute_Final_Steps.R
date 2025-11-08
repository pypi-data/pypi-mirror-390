library("rmarkdown")
library("tidyverse")
library(RPostgres)
library(DT)
library(data.table)

source(here::here("tasks/logging.R"))

#Read in the common functions to be used in R plus helper scripts needed
#by multiple markdown files
source(here::here("tasks/impute_items/0-Common_functions_for_imputation.R"))
source("../NIBRS_Offense_function.r")
source("../NIBRS_function.R")

#SET UP ALL THE NECESSARY INPUT/OUTPUT PATHS
outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")
filepathout = paste0(outputPipelineDir, "/markdown/") #output path for markdown files

mainpath = paste0(outputPipelineDir, "/item_imputation_data/") #output path for data
miscpathout = paste0(outputPipelineDir, "/item_imputation_misc/") #other misc item imputation output

if (! dir.exists(filepathout)) {
  dir.create(filepathout, recursive = TRUE)
}
if (! dir.exists(mainpath)) {
  dir.create(mainpath, recursive = TRUE)
}
if (! dir.exists(miscpathout)) {
  dir.create(miscpathout, recursive = TRUE)
}

#output location of create_NIBRS_extracts
inputPipelineDir <- Sys.getenv("INPUT_PIPELINE_DIR")
inputmainpath = paste0(inputPipelineDir, "/item_imputation_data/") #input path for imputation parts 1+2 output
artifactsmainpath = paste0(inputPipelineDir, "/artifacts/") #input path for other task output

input_state <- Sys.getenv("INPUT_STATE")

#Read in the variable type
source("../NIBRS_Variable_type.R")

logical_edits_frame <- data.frame(fread_logging(paste0(inputmainpath, "02_", input_state, "_logical_edits.csv.gz"), colClasses=logical_edits_variable_types))

#logical_edits_frame <- read_csv_logging(paste0(inputmainpath, "02_", input_state, "_logical_edits.csv.gz"),col_types=logical_edits_variable_types)
sapply(logical_edits_frame, class)

# 15 Create data victim imputation uncleared
log_info(paste0(input_state,": 15_Create_Data_Victim_Imputation_Uncleared.Rmd starting..."))
rmarkdown::render("15_Create_Data_Victim_Imputation_Uncleared.Rmd",
                  output_format = html_document(),
                  output_file = paste0(filepathout, "15_Create_Data_Victim_Imputation_Uncleared_", input_state, ".html"),
                  envir = new.env(), quiet = TRUE)
invisible(gc())
knitr::knit_meta(clean = TRUE)

# 16 Impute victim Uncleared
log_info(paste0(input_state,": 16_MICE_Item_Missing_Imputation_victim_v3_Uncleared.Rmd starting..."))
rmarkdown::render("16_MICE_Item_Missing_Imputation_victim_v3_Uncleared.Rmd",
                  output_format = html_document(),
                  output_file = paste0(filepathout, "16_MICE_Item_Missing_Imputation_victim_v3_Uncleared_", input_state, ".html"),
                  envir = new.env(), quiet = TRUE)
invisible(gc())
knitr::knit_meta(clean = TRUE)

# 17 Combine+Analyze imputations
log_info(paste0(input_state,": 17_Combine_and_Analyze_Imputation.Rmd starting..."))
rmarkdown::render("17_Combine_and_Analyze_Imputation.Rmd",
                  output_format = html_document(),
                  output_file = paste0(filepathout, "17_Combine_and_Analyze_Imputation_", input_state, ".html"),
                  envir = new.env(), quiet = TRUE)
invisible(gc())
knitr::knit_meta(clean = TRUE)
