library(rmarkdown)
library(tidyverse)
library(DBI)
library(rjson)

source(here::here("tasks/logging.R"))

inputPipelineDir <- Sys.getenv("INPUT_PIPELINE_DIR")
outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")
external_path <- Sys.getenv("EXTERNAL_FILE_PATH")

file_locs <- fromJSON(file = sprintf("%s/external_file_locations.json", inputPipelineDir))

filepathin_initial = paste0(inputPipelineDir, "/initial_tasks_output/")
markdownpathout = paste0(outputPipelineDir, "/markdown/")


if (! dir.exists(filepathin_initial)) {
  dir.create(filepathin_initial, recursive = TRUE)
}


if (! dir.exists(markdownpathout)) {
  dir.create(markdownpathout, recursive = TRUE)
}

#Get the maximum year
CONST_YEAR <- Sys.getenv("DATA_YEAR")



#Call the markdown file  
rmarkdown::render("03_Update_POP_TOTALS_PERM_YEAR.Rmd",
                    output_file = paste0(markdownpathout, 
                                         "03_Update_POP_TOTALS_PERM_YEAR.html"),
                    output_format =html_document(), 
                    envir = new.env())  