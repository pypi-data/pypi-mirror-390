library("rmarkdown")
library("tidyverse")
library(RPostgres)
library(DT)

source(here::here("tasks/logging.R"))

#Read in the common functions to be used in R
source(here::here("tasks/impute_items/0-Common_functions_for_imputation.R"))

#SET UP ALL THE NECESSARY INPUT/OUTPUT PATHS
outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")
filepathout = paste0(outputPipelineDir, "/markdown/") #output path for markdown files

if (! dir.exists(filepathout)) {
  dir.create(filepathout, recursive = TRUE)
}

mainpath = paste0(outputPipelineDir, "/item_imputation_data/") #output path for data

if (! dir.exists(mainpath)) {
  dir.create(mainpath, recursive = TRUE)
}

#output location of create_NIBRS_extracts
inputPipelineDir <- Sys.getenv("INPUT_PIPELINE_DIR")
artifactsmainpath = paste0(inputPipelineDir, "/artifacts/") #input path


input_state <- Sys.getenv("INPUT_STATE")


log_info(paste0(input_state,": 02_Logicial_Edits.Rmd starting..."))
rmarkdown::render("02_Logicial_Edits.Rmd", output_format = html_document(),
                  output_file = paste0(filepathout, "02_logical_edits_", input_state, ".html"),
                  envir = new.env(), quiet = TRUE)
invisible(gc())
knitr::knit_meta(clean = TRUE)
