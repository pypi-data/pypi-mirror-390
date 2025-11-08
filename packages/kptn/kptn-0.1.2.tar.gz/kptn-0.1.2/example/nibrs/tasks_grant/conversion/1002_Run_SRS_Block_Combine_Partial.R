library(rmarkdown)
library(tidyverse)
library(DBI)

source("../../tasks/logging.R")

inputPipelineDir <- Sys.getenv("INPUT_PIPELINE_DIR")
outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")

filepathin_initial = paste0(inputPipelineDir, "/initial_tasks_output/")
filepathin = paste0(inputPipelineDir, "/bjs_grant/extracts/", Sys.getenv("DATA_YEAR"), "/")
filepathout = paste0(outputPipelineDir, "/bjs_grant/converted/")#, Sys.getenv("DATA_YEAR"), "/")
filepathflag = paste0(outputPipelineDir, "/bjs_grant/flag/")
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

if (! dir.exists(filepathflag)) {
  dir.create(filepathflag, recursive = TRUE)
}

# get YEAR
CONST_YEAR <- Sys.getenv("DATA_YEAR")



#Call the markdown file  
rmarkdown::render("3_Combined_Original_SRS_Partial.Rmd",
                    output_file = paste0(markdownpathout, 
                                         "3_Combined_Original_SRS_Partial_", CONST_YEAR, ".html"),
                    output_format =html_document(), 
                    envir = new.env())  

rmarkdown::render("4_Create_Annual_Totals_Partial.Rmd",
                  output_file = paste0(markdownpathout, 
                                       "4_Create_Annual_Totals_Partial_Partial_", CONST_YEAR, ".html"),
                  output_format =html_document(), 
                  envir = new.env())  
