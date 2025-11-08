library(rmarkdown)
library(tidyverse)
library(DBI)
#library(rjson)			  

source(here::here("tasks/logging.R"))

inputPipelineDir <- Sys.getenv("INPUT_PIPELINE_DIR")
outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")

filepathin = paste0(inputPipelineDir, "/srs/extracts/")
filepathin_lr = paste0(inputPipelineDir, "/srs/extracts/lr/")
filepathout = paste0(outputPipelineDir, "/srs/converted/")
#filepathout_lr = paste0(outputPipelineDir, "/srs/converted/lr/")
markdownpathout = paste0(outputPipelineDir, "/srs/markdown/")

block_imp_path = paste0(inputPipelineDir, "/block_imputation_data/")

if (! dir.exists(filepathin)) {
  dir.create(filepathin, recursive = TRUE)
}

if (! dir.exists(filepathin_lr)) {
  dir.create(filepathin_lr, recursive = TRUE)
}

if (! dir.exists(filepathout)) {
  dir.create(filepathout, recursive = TRUE)
}

# if (! dir.exists(filepathout_lr)) {
#   dir.create(filepathout_lr, recursive = TRUE)
# }

if (! dir.exists(markdownpathout)) {
  dir.create(markdownpathout, recursive = TRUE)
}


#file_locs <- fromJSON(file = sprintf("%s/external_file_locations.json", inputPipelineDir))

input_files_path = paste0(inputPipelineDir, "/initial_tasks_output/")

# get YEAR
CONST_YEAR <- Sys.getenv("DATA_YEAR")


if(as.numeric(CONST_YEAR) >= 2015){
  
  log_debug("Running 2_Implement_SRS_Rule.Rmd - Revised Rape Version")  

  #Call the markdown file
  rmarkdown::render("3_Implement_SRS_Rule_Plus_Block.Rmd",
                      output_file = paste0(markdownpathout, 
                                           "3_Implement_SRS_Rule_Plus_Block_", CONST_YEAR, ".html"),
                      output_format =html_document(), 
                      envir = new.env())
  
  
  #Call the markdown file  
  rmarkdown::render("4_Combined_Original_SRS.Rmd",
                    output_file = paste0(markdownpathout, 
                                         "4_Combined_Original_SRS_", CONST_YEAR, ".html"),
                    output_format =html_document(), 
                    envir = new.env())  
  
  #Call the markdown file  
  #Run the 2024 version that includes the LAPD fix to use only the SRS's Return A 
  #since the NIBRS to SRS conversion is not accurate due to not all NIBRS records 
  #are reported by LAPD as of calendar year June 2025.
  if(as.numeric(CONST_YEAR) == 2024){
    rmarkdown::render("5_Fix_Imputed_SRS_2024.Rmd",
                      output_file = paste0(markdownpathout, 
                                           "5_Fix_Imputed_", CONST_YEAR, ".html"),
                      output_format =html_document(), 
                      envir = new.env())      
    
    
  }else{
    rmarkdown::render("5_Fix_Imputed_SRS.Rmd",
                      output_file = paste0(markdownpathout, 
                                           "5_Fix_Imputed_", CONST_YEAR, ".html"),
                      output_format =html_document(), 
                      envir = new.env())      
  }
					
  
}else{
  
  log_debug("Running 2_Implement_SRS_Rule.Rmd - Legacy Rape Version")    

  rmarkdown::render("3_Implement_SRS_Rule_Plus_Block_LR.Rmd",
                    output_file = paste0(markdownpathout, 
                                         "3_Implement_SRS_Rule_Plus_Block_LR_", CONST_YEAR, ".html"),
                    output_format =html_document(), 
                    envir = new.env())
    
  
  
  rmarkdown::render("4_Combined_Original_SRS_LR.Rmd",
                    output_file = paste0(markdownpathout, 
                                         "4_Combined_Original_SRS_LR_", CONST_YEAR, ".html"),
                    output_format =html_document(), 
                    envir = new.env())
  
  
  
  
  rmarkdown::render("5_Fix_Imputed_SRS_LR.Rmd",
                    output_file = paste0(markdownpathout, 
                                         "5_Fix_Imputed_SRS_LR_", CONST_YEAR, ".html"),
                    output_format =html_document(), 
                    envir = new.env())  
}
