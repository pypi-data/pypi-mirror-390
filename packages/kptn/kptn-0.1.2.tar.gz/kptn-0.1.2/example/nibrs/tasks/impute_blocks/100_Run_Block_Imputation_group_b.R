library("rmarkdown")
library("tidyverse")
library(RPostgres)
library(DT)

#Read in the common functions to be used in R
source(here::here("tasks/logging.R"))
source(here::here("tasks/impute_items/0-Common_functions_for_imputation.R"))
source("0-200_Macros_imputed_block.R")

#SET UP ALL THE NECESSARY INPUT/OUTPUT PATHS
outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")
filepathout = paste0(outputPipelineDir, "/markdown/") #output path for markdown files

if (! dir.exists(filepathout)) {
  dir.create(filepathout, recursive = TRUE)
}

#output location for block imputation
outblockimp = paste0(outputPipelineDir, "/block_imputation_data/")
if (! dir.exists(outblockimp)) {
  dir.create(outblockimp, recursive = TRUE)
}

#output location for outlier_detection
inputPipelineDir <- Sys.getenv("INPUT_PIPELINE_DIR")
filepathin = paste0(inputPipelineDir, "/outlier_data/")

inblockimp = paste0(inputPipelineDir, "/block_imputation_data/")
if (! dir.exists(inblockimp)) {
  dir.create(inblockimp, recursive = TRUE)
}


#output location of create_NIBRS_extracts
mainpathdata = paste0(inputPipelineDir, "/artifacts/") #input path

# path where queried data is stored
queried_data_path = paste0(outputPipelineDir, "/indicator_table_extracts_bystate/") 

#Create the path to the initial outputs folder
#initial_tasks_output_path = paste0(outputPipelineDir, "/indicator_table_extracts_bystate/")

#get the data year
CONST_YEAR <- Sys.getenv("DATA_YEAR")
if (CONST_YEAR == ""){
  simpleError("Set DATA_YEAR as enviroment variable")
}

#get last two digits of data year
# CONST_YEAR_2_DIGIT <- as.numeric(substr(CONST_YEAR, nchar(CONST_YEAR[1])-1,nchar(CONST_YEAR[1])))
CONST_YEAR_2_DIGIT <- str_pad(string=as.numeric(substr(CONST_YEAR, nchar(CONST_YEAR[1])-1,nchar(CONST_YEAR[1]))), width=2, side="left", pad="0")

log_info("Starting 02_BlockImputation_Incident_Table_group_b.Rmd....")
rmarkdown::render("02_BlockImputation_Incident_Table_group_b.Rmd", output_format = html_document(),
                  output_file = paste0(filepathout, "02_BlockImputation_Incident_Table_group_b.html"),
                  envir = new.env(), quiet = TRUE)
invisible(gc())
knitr::knit_meta(clean = TRUE)
