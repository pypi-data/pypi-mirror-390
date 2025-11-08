library(rmarkdown)
library(tidyverse)
library(DBI)

source("../../tasks/logging.R")

inputPipelineDir <- Sys.getenv("INPUT_PIPELINE_DIR")
outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")

filepathin = paste0(inputPipelineDir, "/bjs_grant/extracts/")
filepathout = paste0(outputPipelineDir, "/bjs_grant/converted/")
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

#Get the maximum year
CONST_YEAR_MAX <- Sys.getenv("DATA_YEAR") 
CONST_YEAR_MIN <- Sys.getenv("DATA_YEAR_MIN")

#Call the markdown file  
rmarkdown::render("5_Create_Combine_File.Rmd",
                    output_file = paste0(markdownpathout, 
                                         "5_Create_Combine_File.html"),
                    output_format =html_document(), 
                    envir = new.env())  