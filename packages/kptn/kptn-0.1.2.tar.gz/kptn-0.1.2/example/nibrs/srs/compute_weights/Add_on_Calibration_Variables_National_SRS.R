#This program will create final lists of cal vars by perm
#Note (29Jun2023): Supporting divisions and fine-tuning which variables are included on state/region/division
#####
#Setup 
library(tidyverse)
library(readxl)
library(rjson)

source(here::here("tasks/logging.R"))

CONST_YEAR <- Sys.getenv("DATA_YEAR")
outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")
inputPipelineDir <- Sys.getenv("INPUT_PIPELINE_DIR")
external_path <- Sys.getenv("EXTERNAL_FILE_PATH")

input_folder <- sprintf("%s", inputPipelineDir)
file_locs <- fromJSON(file = sprintf("%s/external_file_locations.json", input_folder))

input_weighting_data_folder = paste0(inputPipelineDir, "/srs/weighting/Data/")
output_weighting_data_folder = paste0(outputPipelineDir, "/srs/weighting/Data/")
filepathin_initial = paste0(inputPipelineDir, "/initial_tasks_output/")

log_info("Running Add_on_Calibration_Variables_National_SRS.R")

#####
#Load files

#ORI-level frame
calDat1 <- read_csv_logging(file=paste0(output_weighting_data_folder,"SF_national_postN_srs.csv"))

#Perm file
permFile <- read_csv_logging(paste0(filepathin_initial, "POP_TOTALS_PERM_", CONST_YEAR, "_SRS.csv"))

#National crosses
natCrosses <- paste0(input_weighting_data_folder,"Geography_Crossings_National_SRS.xlsx") %>%
  read_xlsx(sheet="National") %>%
  mutate(natLvl="National") %>%
  rename(wgtGpNational=natWgtGp,
         crossNum=natCrossNum)



#####
#Get calibration variables for national

#Note (23Jun2023): Eventually will need to fine-tune which calibration variables are assigned to regions and states, but for now assign all of them to full set (like national)

calVars1 <- calDat1%>% 
  colnames() %>% 
  str_subset("^V\\d+") %>% 
  data.frame(name=.) %>% 
  mutate(crossNum=as.numeric(str_extract(name,"\\d+"))) %>% 
  mutate(inNat=crossNum %in% natCrosses$crossNum,
         natLvl=ifelse(inNat,"National",NA_character_)) %>%
  left_join(natCrosses) %>%
  mutate(inNat=ifelse(is.na(inNat),FALSE,inNat),
         listVars=NA_character_,
		 DER_ORI_CALIBRATION_MODEL_PROCESS=FALSE) %>%
  group_by(natLvl) %>%
  mutate(listVars=ifelse(inNat,str_flatten(name,col=","),listVars),
         DER_ORI_CALIBRATION_MODEL_PROCESS=ifelse(inNat,TRUE,DER_ORI_CALIBRATION_MODEL_PROCESS)) %>%
  ungroup() %>%
  select(natLvl,inNat,listVars,DER_ORI_CALIBRATION_MODEL_PROCESS) %>%
  unique() %>%
  mutate(PERMUTATION_DESCRIPTION2=case_when(inNat ~ paste0("National"))) %>%
  select(PERMUTATION_DESCRIPTION2,DER_ORI_CALIBRATION_MODEL=listVars,DER_ORI_CALIBRATION_MODEL_PROCESS)


#Stack
calVars <- bind_rows(calVars1)

#####
#Merge onto permutation file
permFile2 <- permFile %>%
  mutate(PERMUTATION_DESCRIPTION2=ifelse(str_detect(PERMUTATION_DESCRIPTION,"(Tribal|University)"),
                                         PERMUTATION_DESCRIPTION,
                                         PERMUTATION_DESCRIPTION %>%
                                           str_extract("^(National|Regional|Census Division|State|MSA|Judicial District|Field Office|MD).*") %>%
                                           str_remove(" (Size|Agency Type) .*"))) %>%
  left_join(calVars) %>%
  select(-PERMUTATION_DESCRIPTION2) %>%
  mutate(DER_ORI_CALIBRATION_MODEL_PROCESS=ifelse(is.na(DER_ORI_CALIBRATION_MODEL_PROCESS),FALSE,DER_ORI_CALIBRATION_MODEL_PROCESS))

#Double check that the output did not change
identical(permFile %>% data.frame(),
          permFile2 %>% select(colnames(permFile)) %>% data.frame())

#Output file to the share
permFile2 %>%
  write_csv_logging(file=paste0(output_weighting_data_folder, 
                                "POP_TOTALS_PERM_", CONST_YEAR, "_FINAL_NATIONAL_SRS.csv"), 
                    na="")

log_info("Finished Add_on_Calibration_Variables_National_SRS.R")