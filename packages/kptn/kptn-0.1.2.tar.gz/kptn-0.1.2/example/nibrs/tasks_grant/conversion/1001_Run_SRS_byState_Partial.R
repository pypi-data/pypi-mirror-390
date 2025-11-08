library(rmarkdown)
library(tidyverse)
library(DBI)

source("../../tasks/logging.R")

con <- dbConnect(RPostgres::Postgres())
inputPipelineDir <- Sys.getenv("INPUT_PIPELINE_DIR")
outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")

filepathin = paste0(inputPipelineDir, "/bjs_grant/extracts/", Sys.getenv("DATA_YEAR"), "/")
filepathout = paste0(outputPipelineDir, "/bjs_grant/extracts/", Sys.getenv("DATA_YEAR"), "/")
markdownpathout = paste0(outputPipelineDir, "/bjs_grant/markdown/")

if (! dir.exists(filepathin)) {
  dir.create(filepathin, recursive = TRUE)
}

if (! dir.exists(filepathout)) {
  dir.create(filepathout, recursive = TRUE)
}

if (! dir.exists(markdownpathout)) {
  dir.create(markdownpathout, recursive = TRUE)
}

# get STATE & YEAR
CONST_STATE <- Sys.getenv("INPUT_STATE")
CONST_YEAR <- Sys.getenv("DATA_YEAR")

#Call the markdown file
rmarkdown::render("1_Create_Extracts_Partial.Rmd",
                    output_file = paste0(markdownpathout, 
                                         "1_Create_Extracts_Partial_", CONST_STATE, "_",  CONST_YEAR, ".html"),
                    output_format =html_document(), 
                    envir = new.env())
  

#Call the markdown file  
rmarkdown::render("2_Create_NIBRS_to_SRS_No_Hierarchy_Partial.Rmd",
                    output_file = paste0(markdownpathout, 
                                         "2_Create_NIBRS_to_SRS_No_Hierarchy_Partial_", CONST_STATE, "_",  CONST_YEAR, ".html"),
                    output_format =html_document(), 
                    envir = new.env())  
