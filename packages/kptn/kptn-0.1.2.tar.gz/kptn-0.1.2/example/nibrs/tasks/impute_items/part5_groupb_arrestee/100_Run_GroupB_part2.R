library("rmarkdown")
library("tidyverse")
library(RPostgres)
library(DT)
library(data.table)
library("rjson")

source(here::here("tasks/logging.R"))

#Read in the common functions to be used in R plus helper scripts needed
#by multiple markdown files
source(here::here("tasks/impute_items/0-Common_functions_for_imputation.R"))
source("../NIBRS_Offense_function.r")
source("../NIBRS_function.R")

#SET UP ALL THE NECESSARY INPUT/OUTPUT PATHS
outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")
inputPipelineDir <- Sys.getenv("INPUT_PIPELINE_DIR")
external_path <- Sys.getenv("EXTERNAL_FILE_PATH")

filepathout = paste0(outputPipelineDir, "/markdown/") #output path for markdown files
if (! dir.exists(filepathout)) {
  dir.create(filepathout, recursive = TRUE)
}

mainpath = paste0(outputPipelineDir, "/item_imputation_data/") #output path for data
if (! dir.exists(mainpath)) {
  dir.create(mainpath, recursive = TRUE)
}

miscPathout = paste0(outputPipelineDir, "/item_imputation_misc/") #other misc item imputation output
if (! dir.exists(miscPathout)) {
  dir.create(miscPathout, recursive = TRUE)
}

#External files json
input_folder <- sprintf("%s", inputPipelineDir)
file_locs <- fromJSON(file = sprintf("%s/external_file_locations.json", input_folder))

#Read in the variable type
source("../NIBRS_Variable_type.R")

# Get states associated with each ethnicity number
ctrl <- read_csv("../part3_5_ethnicity/Data/Ethnicity_State_PERM.csv")
eth_states_1 <- trimws(strsplit(ctrl$ETH_PERM_STATES[ctrl$ETH_PERM_NUM == 1], ",")[[1]])
eth_states_2 <- trimws(strsplit(ctrl$ETH_PERM_STATES[ctrl$ETH_PERM_NUM == 2], ",")[[1]])
eth_states_3 <- trimws(strsplit(ctrl$ETH_PERM_STATES[ctrl$ETH_PERM_NUM == 3], ",")[[1]])


# Get data year
CONST_YEAR = Sys.getenv("DATA_YEAR")

# 02 Imputation of group b arrestee data
log_info(paste0("02_MICE_group_b_arrestee.Rmd starting..."))
rmarkdown::render("02_MICE_group_b_arrestee.Rmd", output_format = html_document(),
                  output_file = paste0(filepathout, "02_MICE_group_b_arrestee.html"),
                  envir = new.env(), quiet = TRUE)
invisible(gc())
knitr::knit_meta(clean = TRUE)
