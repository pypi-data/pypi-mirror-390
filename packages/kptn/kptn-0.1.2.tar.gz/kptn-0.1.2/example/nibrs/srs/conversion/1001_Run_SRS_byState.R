library(rmarkdown)
library(tidyverse)
library(DBI)

source(here::here("tasks/logging.R"))

con <- dbConnect(RPostgres::Postgres())
inputPipelineDir <- Sys.getenv("INPUT_PIPELINE_DIR")
outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")

filepathin = paste0(inputPipelineDir, "/srs/extracts/")
filepathout = paste0(outputPipelineDir, "/srs/extracts/")
filepathout_lr = paste0(outputPipelineDir, "/srs/extracts/lr/")
markdownpathout = paste0(outputPipelineDir, "/srs/markdown/")

if (! dir.exists(filepathin)) {
  dir.create(filepathin, recursive = TRUE)
}

if (! dir.exists(filepathout)) {
  dir.create(filepathout, recursive = TRUE)
}

if (! dir.exists(filepathout_lr)) {
  dir.create(filepathout_lr, recursive = TRUE)
}

if (! dir.exists(markdownpathout)) {
  dir.create(markdownpathout, recursive = TRUE)
}

# get STATE & YEAR
CONST_STATE <- Sys.getenv("INPUT_STATE")
CONST_YEAR <- Sys.getenv("DATA_YEAR")


#Call the markdown file
rmarkdown::render("1_Create_Extracts.Rmd",
                    output_file = paste0(markdownpathout,
                                         "1_Create_Extracts_", CONST_STATE, "_",  CONST_YEAR, ".html"),
                    output_format =html_document(),
                    envir = new.env())

if(as.numeric(CONST_YEAR) >= 2015){
  
  log_debug("Running 2_Implement_SRS_Rule.Rmd - Revised Rape Version")  

  #Call the markdown file  
  rmarkdown::render("2_Implement_SRS_Rule.Rmd",
                      output_file = paste0(markdownpathout, 
                                           "2_Implement_SRS_Rule_", CONST_STATE, "_",  CONST_YEAR, ".html"),
                      output_format =html_document(), 
                      envir = new.env())  
}else{
  
  log_debug("Running 2_Implement_SRS_Rule.Rmd - Legacy Rape Version")  
  
  #Call the markdown file  
  rmarkdown::render("2_Implement_SRS_Rule_LR.Rmd",
                    output_file = paste0(markdownpathout, 
                                         "2_Implement_SRS_Rule_LR_", CONST_STATE, "_",  CONST_YEAR, ".html"),
                    output_format =html_document(), 
                    envir = new.env())  

}
