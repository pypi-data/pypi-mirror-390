library("rmarkdown")
library("tidyverse")
library(RPostgres)
library(DT)
library(mice)
library(miceadds)
library(data.table)
library("rjson")

source(here::here("tasks/logging.R"))

#Read in the common functions to be used in R
source(here::here("tasks/impute_items/0-Common_functions_for_imputation.R"))

read_csv <- partial(read_csv, guess_max = 1000000) #For now, read thru the 1st 1,000,000 rows to determine variable type
#md.pattern <- partial(md.pattern, plot=FALSE)

#SET UP ALL THE NECESSARY INPUT/OUTPUT PATHS
outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")
inputPipelineDir <- Sys.getenv("INPUT_PIPELINE_DIR")
external_path <- Sys.getenv("EXTERNAL_FILE_PATH")

# set up state
CONST_STATE <- Sys.getenv("INPUT_STATE")
#set-up year
CONST_YEAR <- Sys.getenv("DATA_YEAR")

der_bystate_file_path = paste0(outputPipelineDir,"/indicator_table_extracts_bystate/")

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


#output location of create_NIBRS_extracts
inputmainpath = paste0(inputPipelineDir, "/item_imputation_data/") #input path for part 1 output
artifactsmainpath = paste0(inputPipelineDir, "artifacts/") #input path for other task output

if (CONST_STATE == "MT" & CONST_YEAR == "2024") {
  log_info(paste0("01_MICE_group_b_arrestee.Rmd for ", CONST_STATE, " starting..."))
  rmarkdown::render("01_MICE_group_b_arrestee_MT2024.Rmd", output_format = html_document(),
                    output_file = paste0(filepathout, "01_MICE_group_b_arrestee_", CONST_STATE,".html"),
                    envir = new.env(), quiet = TRUE)
  invisible(gc())
  knitr::knit_meta(clean = TRUE)
} else {
  # 01 Imputation of group b arrestee data
  log_info(paste0("01_MICE_group_b_arrestee.Rmd for ", CONST_STATE, " starting..."))
  rmarkdown::render("01_MICE_group_b_arrestee.Rmd", output_format = html_document(),
                    output_file = paste0(filepathout, "01_MICE_group_b_arrestee_", CONST_STATE,".html"),
                    envir = new.env(), quiet = TRUE)
  invisible(gc())
  knitr::knit_meta(clean = TRUE)
}


