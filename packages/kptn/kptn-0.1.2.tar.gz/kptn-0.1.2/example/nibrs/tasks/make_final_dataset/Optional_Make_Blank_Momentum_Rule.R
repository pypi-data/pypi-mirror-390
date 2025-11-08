library(tidyverse)
library(data.table)
library(here)

#Read in the logging package
source(paste0(here(), "/tasks/logging.R"))


#############################Declare CONSTANTS#################################

#Declare the geographic permutation numbers to make the momentum rule output
#Example code is the Field Office Geographic permutations
CONST_GEO_NUM <- c(583:637)

#Starts in nibrs-estimation-pipeline/ 
outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")
CONST_OUTPUT <- paste0(outputPipelineDir, "/final-estimates/Momentum_Rule/")

#Create the output directory if it does not exist
if(!dir.exists(CONST_OUTPUT)){
  dir.create(CONST_OUTPUT, recursive = TRUE)
}

##############################################################################

#Loop thru CONST_GEO_NUM and write file if it does not exists
walk(CONST_GEO_NUM, ~{
  
  #Need to create POPTOTAL_ORIG_PERMUTATION_NUMBER and der_rrmse_gt_30_se_estimate_0_2_cond_top
  loop_data_1 <- data.frame(
    
    POPTOTAL_ORIG_PERMUTATION_NUMBER = .x,
    der_rrmse_gt_30_se_estimate_0_2_cond_top = 0
  )
  
  #Write out if it does not exists
  if( !(file.exists(paste0(CONST_OUTPUT, "Momemtum_Rule_", .x, ".rds")))){
    
    #Write a message to the log
    log_debug(paste0("Creating Momemtum_Rule_", .x, ".rds"))
    
    #Output the data
    loop_data_1 %>%
      write_rds(paste0(CONST_OUTPUT, "Momemtum_Rule_", .x, ".rds"))
    
  }
  
  #Delete the object
  rm(loop_data_1)  
  
  
  
  
  
})
