library("rmarkdown")
library("tidyverse")
library(RPostgres)
library(data.table)

source(here::here("tasks/logging.R"))

#Read in the common functions to be used in R
source(here::here("tasks/impute_items/0-Common_functions_for_imputation.R"))
source("../NIBRS_function.R")
source("../NIBRS_Property_function.r")

#SET UP ALL THE NECESSARY INPUT/OUTPUT PATHS
outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")
filepathout = paste0(outputPipelineDir, "/markdown/") #output path for markdown files
mainpath = paste0(outputPipelineDir, "/item_imputation_data/") #output path for data
miscpathout = paste0(outputPipelineDir, "/item_imputation_misc/") #other misc item imputation output
artifacts_path = paste0(outputPipelineDir, "/artifacts/") #location for the property segment

if (! dir.exists(filepathout)) {
  dir.create(filepathout, recursive = TRUE)
}
if (! dir.exists(mainpath)) {
  dir.create(mainpath, recursive = TRUE)
}
if (! dir.exists(miscpathout)) {
  dir.create(miscpathout, recursive = TRUE)
}

#output location of logical edits
inputPipelineDir <- Sys.getenv("INPUT_PIPELINE_DIR")
artifactsmainpath = paste0(inputPipelineDir, "/item_imputation_data/") #input path
inputmainpath = paste0(inputPipelineDir, "/item_imputation_data/") #input path for part 1 output

#Declare the Constant
INPUT_NUM <- Sys.getenv("INPUT_NUM")

ctrl <- read_csv("./Data/VOR_Property_PERM.csv") %>%
  filter(VOR_PERM_NUM == as.numeric(INPUT_NUM))

Sys.setenv(INPUT_STATE = ctrl$VOR_PERM_STATES)

#New Imputation programs for property offenses
log_info(paste0("VOR Property Offense Group ", INPUT_NUM, ": 332_MICE_Impute_Relationship_code_offender_property.Rmd starting ..."))
rmarkdown::render("332_MICE_Impute_Relationship_code_offender_property.Rmd",
                  output_format = html_document(),
                  output_file = paste0(filepathout, "332_MICE_Impute_Relationship_code_offender_property_group_", INPUT_NUM, ".html"),
                  envir = new.env(), quiet = TRUE)

invisible(gc())
knitr::knit_meta(clean = TRUE)
