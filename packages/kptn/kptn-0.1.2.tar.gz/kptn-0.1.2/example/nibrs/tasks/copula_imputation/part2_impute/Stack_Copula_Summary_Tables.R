#Stack files in summary tables for copula

library(reshape2)
library(tidyverse)
library(openxlsx)
library(copula)
library(rjson)
library(data.table)
source(here::here("tasks/logging.R"))

outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")
inputPipelineDir <- Sys.getenv("INPUT_PIPELINE_DIR")
external_path <- Sys.getenv("EXTERNAL_FILE_PATH")
table <- Sys.getenv("TABLE_NAME")

output_folder <- sprintf("%s", outputPipelineDir)
input_folder <- sprintf("%s", inputPipelineDir)

input_estimate_folder <- paste0(inputPipelineDir, "/indicator_table_estimates/")
input_extract_folder <- paste0(inputPipelineDir, "/indicator_table_extracts/")

output_copula_folder <- file.path(outputPipelineDir, "copula_imputation")
output_copula_data_folder <- file.path(output_copula_folder, "Data")
output_copula_sum_folder <- file.path(output_copula_folder, "Summary")

directories <- c(output_copula_sum_folder)

for (d in directories) {
  if (! dir.exists(d)) {
    dir.create(d, recursive = TRUE)
  }
}

year <- Sys.getenv("DATA_YEAR")

log_info("Starting Stack_Copula_Summary_Tables.R...")

log_debug("Start step 1...")
##################
#Imputation Step 1
#Nonzero Pop (non-missing demo)
files_step1_nz <- list.files(output_copula_data_folder) %>%   
  str_subset(paste0("Table_",table,"_Imputation_Step1_Summary_Perm_\\d+_ColNum_\\d+_Nonzero_Pop_Rates_PARENT_POP_GROUP_CODE2_\\d+.csv")) 

stacked_step1_nz <- lapply(files_step1_nz,function(i){
	#message(i)
  out <- fread(file.path(output_copula_data_folder,i)) 
   if (nrow(out)>0){
   #print(">0")
	return(out %>%
    mutate(subset="popResidAgcy_cbi>0 & nDemoMissing==0",
           stratvar="PARENT_POP_GROUP_CODE2",
           stratlvl=str_sub(i,-5,-5)) %>%
    select(table,permutation,subset,stratvar,stratlvl,everything()))
	} else {
	#print("==0")
	return(NULL)
	}
})  %>% rbindlist()
 
#Missing Demo
files_step1_m <- list.files(output_copula_data_folder) %>% 
  str_subset(paste0("Table_",table,"_Imputation_Step1_Summary_Perm_\\d+_ColNum_\\d+_Missing_Demo_Rates_PARENT_POP_GROUP_CODE2_\\d+.csv")) 

stacked_step1_m <- lapply(files_step1_m,function(i){
  out <- fread(file.path(output_copula_data_folder,i))
   if (nrow(out)>0){
	return(out %>%
    mutate(subset="popResidAgcy_cbi>0 & nDemoMissing>0",
           stratvar="PARENT_POP_GROUP_CODE2",
           stratlvl=str_sub(i,-5,-5))  %>%
    select(table,permutation,subset,stratvar,stratlvl,everything()))
	} else {
	return(NULL)
	}
}) %>% rbindlist()

#Zero Pop
files_step1_z <- list.files(output_copula_data_folder) %>% 
  str_subset(paste0("Table_",table,"_Imputation_Step1_Summary_Perm_\\d+_ColNum_\\d+_Zero_Pop_Rates_PARENT_POP_GROUP_CODE2_\\d+.csv")) 
  
stacked_step1_z <- lapply(files_step1_z,function(i){
  out <- fread(file.path(output_copula_data_folder,i)) 
   if (nrow(out)>0){
	return(out%>%
    mutate(subset="popResidAgcy_cbi==0",
           stratvar="PARENT_POP_GROUP_CODE2",
           stratlvl=str_sub(i,-5,-5)) %>%
    select(table,permutation,subset,stratvar,stratlvl,everything()))
	} else {
	return(NULL)
	}
}) %>% rbindlist()
  
#Stack all subsets
stacked_step1 <- rbindlist(list(stacked_step1_nz,
                                stacked_step1_m,
								stacked_step1_z))
								
rm(stacked_step1_nz,stacked_step1_m,stacked_step1_z)

fwrite(stacked_step1,
       file=file.path(output_copula_sum_folder,
                      paste0("Copula_Imputation_Step1_Summary_",table,".csv")))

log_debug("Start step 2...")	
##################
#Imputation Step 2		
#Nonzero Pop (non-missing demo)
files_step2_nz <- list.files(output_copula_data_folder) %>%   
  str_subset(paste0("Table_",table,"_Imputation_Step2_Summary_Perm_\\d+_ColNum_\\d+_Nonzero_Pop_Rates_PARENT_POP_GROUP_CODE2_\\d+.csv")) 
  
stacked_step2_nz <- lapply(files_step2_nz,function(i){
  out <- fread(file.path(output_copula_data_folder,i)) 
   if (nrow(out)>0){
	return(out %>%
    mutate(subset="popResidAgcy_cbi>0 & nDemoMissing==0",
           stratvar="PARENT_POP_GROUP_CODE2",
           stratlvl=str_sub(i,-5,-5)) %>%
    select(table,permutation,subset,stratvar,stratlvl,tier,column,section,everything()))
	} else {
	return(NULL)
	}
}) %>% rbindlist()
  
#Missing Demo
files_step2_m <- list.files(output_copula_data_folder) %>% 
  str_subset(paste0("Table_",table,"_Imputation_Step2_Summary_Perm_\\d+_ColNum_\\d+_Missing_Demo_Rates_PARENT_POP_GROUP_CODE2_\\d+.csv")) 

stacked_step2_m <- lapply(files_step2_m,function(i){
  out <- fread(file.path(output_copula_data_folder,i)) 
   if (nrow(out)>0){
	return(out %>%
    mutate(subset="popResidAgcy_cbi>0 & nDemoMissing>0",
           stratvar="PARENT_POP_GROUP_CODE2",
           stratlvl=str_sub(i,-5,-5)) %>%
    select(table,permutation,subset,stratvar,stratlvl,tier,column,section,everything()))
	} else {
	return(NULL)
	}
}) %>% rbindlist()

#Zero Pop
files_step2_z <- list.files(output_copula_data_folder) %>% 
  str_subset(paste0("Table_",table,"_Imputation_Step2_Summary_Perm_\\d+_ColNum_\\d+_Zero_Pop_Rates_PARENT_POP_GROUP_CODE2_\\d+.csv")) 
  
stacked_step2_z <- lapply(files_step2_z,function(i){
  out <- fread(file.path(output_copula_data_folder,i)) 
   if (nrow(out)>0){
	return(out %>%
    mutate(subset="popResidAgcy_cbi==0",
           stratvar="PARENT_POP_GROUP_CODE2",
           stratlvl=str_sub(i,-5,-5)) %>%
    select(table,permutation,subset,stratvar,stratlvl,tier,column,section,everything()))
	} else {
	return(NULL)
	}
}) %>% rbindlist()

#Stack all subsets
stacked_step2 <- rbindlist(list(stacked_step2_nz,
                                stacked_step2_m,
								stacked_step2_z))				
rm(stacked_step2_nz,stacked_step2_m,stacked_step2_z)

fwrite(stacked_step2,
       file=file.path(output_copula_sum_folder,
                      paste0("Copula_Imputation_Step2_Summary_",table,".csv")))

log_debug("Start step 3...")
##################
#Imputation Step 3 (Ratio Adjustment)		
#Nonzero Pop (non-missing demo)
files_step3_nz <- list.files(output_copula_data_folder) %>%   
  str_subset(paste0("Table_",table,"_Ratio_Adjustment_Summary_Perm_\\d+_ColNum_\\d+_Nonzero_Pop_Rates_PARENT_POP_GROUP_CODE2_\\d+.csv")) 
  
stacked_step3_nz <- lapply(files_step3_nz,function(i){
  out <- fread(file.path(output_copula_data_folder,i))
   if (nrow(out)>0){
	return(out %>%
    mutate(subset="popResidAgcy_cbi>0 & nDemoMissing==0",
           stratvar="PARENT_POP_GROUP_CODE2",
           stratlvl=str_sub(i,-5,-5)) %>%
    select(table,permutation,subset,stratvar,stratlvl,tier,column,section,everything()))
	} else {
	return(NULL)
	}
}) %>% rbindlist()
  
#Missing Demo
files_step3_m <- list.files(output_copula_data_folder) %>% 
  str_subset(paste0("Table_",table,"_Ratio_Adjustment_Summary_Perm_\\d+_ColNum_\\d+_Missing_Demo_Rates_PARENT_POP_GROUP_CODE2_\\d+.csv")) 

stacked_step3_m <- lapply(files_step3_m,function(i){
  out <- fread(file.path(output_copula_data_folder,i)) 
   if (nrow(out)>0){
	return(out %>%
    mutate(subset="popResidAgcy_cbi>0 & nDemoMissing>0",
           stratvar="PARENT_POP_GROUP_CODE2",
           stratlvl=str_sub(i,-5,-5)) %>%
    select(table,permutation,subset,stratvar,stratlvl,tier,column,section,everything()))
	} else {
	return(NULL)
	}
}) %>% rbindlist()

#Zero Pop
files_step3_z <- list.files(output_copula_data_folder) %>% 
  str_subset(paste0("Table_",table,"_Ratio_Adjustment_Summary_Perm_\\d+_ColNum_\\d+_Zero_Pop_Rates_PARENT_POP_GROUP_CODE2_\\d+.csv")) 
  
stacked_step3_z <- lapply(files_step3_z,function(i){
  out <- fread(file.path(output_copula_data_folder,i)) 
   if (nrow(out)>0){
	return(out %>%
    mutate(subset="popResidAgcy_cbi==0",
           stratvar="PARENT_POP_GROUP_CODE2",
           stratlvl=str_sub(i,-5,-5)) %>%
    select(table,permutation,subset,stratvar,stratlvl,tier,column,section,everything()))
	} else {
	return(NULL)
	}
}) %>% rbindlist()

#Stack all subsets
stacked_step3 <- rbindlist(list(stacked_step3_nz,
                                stacked_step3_m,
								stacked_step3_z))				
rm(stacked_step3_nz,stacked_step3_m,stacked_step3_z)

fwrite(stacked_step3,
       file=file.path(output_copula_sum_folder,
                      paste0("Copula_Imputation_Step3_Summary_",table,".csv")))