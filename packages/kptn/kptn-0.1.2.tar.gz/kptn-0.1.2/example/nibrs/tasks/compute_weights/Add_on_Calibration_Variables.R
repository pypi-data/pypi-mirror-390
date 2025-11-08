#This program will create final lists of cal vars by perm

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
filepathin_initial = paste0(inputPipelineDir, "/initial_tasks_output/")

input_folder <- sprintf("%s", inputPipelineDir)
file_locs <- fromJSON(file = sprintf("%s/external_file_locations.json", input_folder))

input_weighting_data_folder = paste0(inputPipelineDir, "/weighting/Data/")
output_weighting_data_folder = paste0(outputPipelineDir, "/weighting/Data/")

log_info("Running Add_on_Calibration_Variables.R")

#####
#Load files

#14May2025: specifying guess_max parameter for all read_csv_logging() calls

#ORI-level frame
calDat1 <- read_csv_logging(file=paste0(output_weighting_data_folder,"SF_postS.csv"),
                            guess_max=Inf)

#Sub-state frame (2021+)
if (as.numeric(CONST_YEAR)>=2021){
  calDat2 <- read_csv_logging(file=paste0(output_weighting_data_folder,"SF_postMSA_cal_srs_altcombs_col.csv"),
                              guess_max=Inf)
}
#Perm file
permFile <- read_csv_logging(paste0(filepathin_initial, "POP_TOTALS_PERM_", CONST_YEAR, ".csv"),
                             guess_max=Inf)

#National crosses
natCrosses <- paste0(input_weighting_data_folder,"Geography_Crossings.xlsx") %>%
  read_xlsx(sheet="National") %>%
  mutate(natLvl="National") %>%
  rename(wgtGpNational=natWgtGp,
         crossNum=natCrossNum)

#Region crosses
regCrosses <- paste0(input_weighting_data_folder,"Geography_Crossings.xlsx") %>%
  read_xlsx(sheet="Region") %>%
  rename(REGION_NAME=regLvl,
         wgtGpRegion=regWgtGp,
         crossNum=regCrossNum) %>%
  mutate(inReg=TRUE)

#State crossses
stateCrosses <- paste0(input_weighting_data_folder,"Geography_Crossings.xlsx") %>%
  read_xlsx(sheet="State") %>%
  rename(STATE_NAME=stateLvl,
         wgtGpState=stateWgtGp,
         crossNum=stateCrossNum) %>%
  mutate(inState=TRUE)

	
#Region model
regModel <- paste0(input_weighting_data_folder,"SRS_Variable_Combination_Convergence_by_Region_X_Weighting_Group_AltCombs_Automatic.xlsx") %>%
    read_xlsx() %>%
	subset(Select=="X") %>%
	group_by(REGION_NAME) %>%
	dplyr::summarize(nZero=sum(nVar==0),
	                 nNonzero=sum(nVar>0)) %>%
	mutate(DER_ORI_CALIBRATION_MODEL_PROCESS_REGION=!(nZero>0 & nNonzero==0)) %>%
	select(REGION_NAME,DER_ORI_CALIBRATION_MODEL_PROCESS_REGION)
	
#State model
stateModel <- paste0(input_weighting_data_folder,"SRS_Variable_Combination_Convergence_by_State_X_Weighting_Group_AltCombs_Automatic.xlsx") %>%
    read_xlsx()  %>%
	subset(Select=="X") %>%
	group_by(STATE_NAME) %>%
	dplyr::summarize(nZero=sum(nVar==0),
	                 nNonzero=sum(nVar>0)) %>%
	mutate(DER_ORI_CALIBRATION_MODEL_PROCESS_STATE=!(nZero>0 & nNonzero==0)) %>%
	select(STATE_NAME,DER_ORI_CALIBRATION_MODEL_PROCESS_STATE)
#Sub-state estimates (only for 2021+)
if (as.numeric(CONST_YEAR)>=2021){
  #FO crosses
  foCrosses <- paste0(input_weighting_data_folder,"Geography_Crossings.xlsx") %>%
    read_xlsx(sheet="FO") %>%
    rename(FIELD_OFFICE_NAME=foLvl,
           wgtGpFO=foWgtGp,
           crossNum=foCrossNum) %>%
    mutate(inFO=TRUE)
  
  #JD crosses
  jdCrosses <- paste0(input_weighting_data_folder,"Geography_Crossings.xlsx") %>%
    read_xlsx(sheet="JD") %>%
    rename(JUDICIAL_DISTRICT_NAME=jdLvl,
           wgtGpJD=jdWgtGp,
           crossNum=jdCrossNum) %>%
    mutate(inJD=TRUE)
  
  #MSA crosses
  msaCrosses <- paste0(input_weighting_data_folder,"Geography_Crossings.xlsx") %>%
    read_xlsx(sheet="MSA") %>%
    rename(MSA_NAME_COUNTY=msaLvl,
           wgtGpMSA=msaWgtGp,
           crossNum=msaCrossNum) %>%
    mutate(inMSA=TRUE)
	
	#FO model
	foModel <- paste0(input_weighting_data_folder,"SRS_Variable_Combination_Convergence_by_FO_X_Weighting_Group_AltCombs_Collapsed_Automatic.xlsx") %>%
    read_xlsx()  %>%
	subset(Select=="X") %>%
	group_by(FIELD_OFFICE_NAME) %>%
	dplyr::summarize(nZero=sum(nVar==0),
	                 nNonzero=sum(nVar>0)) %>%
	mutate(DER_ORI_CALIBRATION_MODEL_PROCESS_FO=!(nZero>0 & nNonzero==0)) %>%
	select(FIELD_OFFICE_NAME,DER_ORI_CALIBRATION_MODEL_PROCESS_FO)
	
	#JD model
	jdModel <- paste0(input_weighting_data_folder,"SRS_Variable_Combination_Convergence_by_JD_X_Weighting_Group_AltCombs_Collapsed_Automatic.xlsx") %>%
    read_xlsx()  %>%
	subset(Select=="X") %>%
	group_by(JUDICIAL_DISTRICT_NAME) %>%
	dplyr::summarize(nZero=sum(nVar==0),
	                 nNonzero=sum(nVar>0)) %>%
	mutate(DER_ORI_CALIBRATION_MODEL_PROCESS_JD=!(nZero>0 & nNonzero==0)) %>%
	select(JUDICIAL_DISTRICT_NAME,DER_ORI_CALIBRATION_MODEL_PROCESS_JD)
	
	#MSA model
	msaModel <- paste0(input_weighting_data_folder,"SRS_Variable_Combination_Convergence_by_MSA_X_Weighting_Group_AltCombs_Collapsed_Automatic.xlsx") %>%
    read_xlsx()  %>%
	subset(Select=="X") %>%
	group_by(MSA_NAME_COUNTY) %>%
	dplyr::summarize(nZero=sum(nVar==0),
	                 nNonzero=sum(nVar>0)) %>%
	mutate(DER_ORI_CALIBRATION_MODEL_PROCESS_MSA=!(nZero>0 & nNonzero==0)) %>%
	select(MSA_NAME_COUNTY,DER_ORI_CALIBRATION_MODEL_PROCESS_MSA)
}


#####
#Get calibration variables from ORI-level file
calVars1 <- calDat1%>% 
  colnames() %>% 
  str_subset("^V\\d+") %>% 
  data.frame(name=.) %>% 
  mutate(crossNum=as.numeric(str_extract(name,"\\d+"))) %>% 
  mutate(inNat=crossNum %in% natCrosses$crossNum,
         inReg=crossNum %in% regCrosses$crossNum,
         inState=crossNum %in% stateCrosses$crossNum,
         natLvl=ifelse(inNat,"National",NA_character_)) %>%
  left_join(natCrosses) %>%
  left_join(regCrosses) %>%
  left_join(stateCrosses) %>%
  left_join(regModel) %>%
  left_join(stateModel) %>%
  mutate(inNat=ifelse(is.na(inNat),FALSE,inNat),
         inReg=ifelse(is.na(inReg),FALSE,inReg),
         inState=ifelse(is.na(inState),FALSE,inState),
         listVars=NA_character_,
		 DER_ORI_CALIBRATION_MODEL_PROCESS=FALSE) %>%
  group_by(natLvl) %>%
  mutate(listVars=ifelse(inNat,str_flatten(name,col=","),listVars),
         DER_ORI_CALIBRATION_MODEL_PROCESS=ifelse(inNat,TRUE,DER_ORI_CALIBRATION_MODEL_PROCESS)) %>%
  group_by(REGION_NAME) %>%
  mutate(listVars=ifelse(inReg,str_flatten(name,col=","),listVars),
         DER_ORI_CALIBRATION_MODEL_PROCESS=ifelse(inReg,DER_ORI_CALIBRATION_MODEL_PROCESS_REGION,DER_ORI_CALIBRATION_MODEL_PROCESS)) %>%
  group_by(STATE_NAME) %>%
  mutate(listVars=ifelse(inState,str_flatten(name,col=","),listVars),
         DER_ORI_CALIBRATION_MODEL_PROCESS=ifelse(inState,DER_ORI_CALIBRATION_MODEL_PROCESS_STATE,DER_ORI_CALIBRATION_MODEL_PROCESS)) %>%
  ungroup() %>%
  select(natLvl,REGION_NAME,STATE_NAME,inNat,inReg,inState,listVars,DER_ORI_CALIBRATION_MODEL_PROCESS) %>%
  unique() %>%
  mutate(PERMUTATION_DESCRIPTION2=case_when(inNat ~ paste0("National"),
                                            inReg ~ paste0("Regional ",REGION_NAME),
                                            inState ~ paste0("State ",STATE_NAME))) %>%
  select(PERMUTATION_DESCRIPTION2,DER_ORI_CALIBRATION_MODEL=listVars,DER_ORI_CALIBRATION_MODEL_PROCESS)

#####
#Repeat but for (ORI x county)-level for 2021+
if (as.numeric(CONST_YEAR)>=2021){
  
  calVars2 <- calDat2 %>% 
    colnames() %>% 
    str_subset("^V\\d+") %>% 
    data.frame(name=.) %>% 
    mutate(crossNum=as.numeric(str_extract(name,"\\d+"))) %>% 
    mutate(inMSA=crossNum %in% msaCrosses$crossNum,
           inJD=crossNum %in% jdCrosses$crossNum,
           inFO=crossNum %in% foCrosses$crossNum) %>%
    left_join(jdCrosses) %>%
    left_join(msaCrosses) %>%
    left_join(foCrosses) %>%
    left_join(foModel) %>%
    left_join(jdModel) %>%
    left_join(msaModel) %>%
    mutate(inJD=ifelse(is.na(inJD),FALSE,inJD),
           inMSA=ifelse(is.na(inMSA),FALSE,inMSA),
           inFO=ifelse(is.na(inFO),FALSE,inFO),
           listVars=NA_character_,
		   DER_ORI_CALIBRATION_MODEL_PROCESS=NA) %>%
    group_by(JUDICIAL_DISTRICT_NAME) %>%
    mutate(listVars=ifelse(inJD,str_flatten(name,col=","),listVars),
	       DER_ORI_CALIBRATION_MODEL_PROCESS=ifelse(inJD,DER_ORI_CALIBRATION_MODEL_PROCESS_JD,DER_ORI_CALIBRATION_MODEL_PROCESS)) %>%
    group_by(MSA_NAME_COUNTY) %>%
    mutate(listVars=ifelse(inMSA,str_flatten(name,col=","),listVars),  
	       DER_ORI_CALIBRATION_MODEL_PROCESS=ifelse(inMSA,DER_ORI_CALIBRATION_MODEL_PROCESS_MSA,DER_ORI_CALIBRATION_MODEL_PROCESS)) %>%
    group_by(FIELD_OFFICE_NAME) %>%
    mutate(listVars=ifelse(inFO,str_flatten(name,col=","),listVars),
	       DER_ORI_CALIBRATION_MODEL_PROCESS=ifelse(inFO,DER_ORI_CALIBRATION_MODEL_PROCESS_FO,DER_ORI_CALIBRATION_MODEL_PROCESS)) %>%
    ungroup() %>%
	mutate(DER_ORI_CALIBRATION_MODEL_PROCESS=ifelse(is.na(DER_ORI_CALIBRATION_MODEL_PROCESS),FALSE,DER_ORI_CALIBRATION_MODEL_PROCESS)) %>%
    select(JUDICIAL_DISTRICT_NAME,MSA_NAME_COUNTY,FIELD_OFFICE_NAME,inJD,inMSA,inFO,listVars,DER_ORI_CALIBRATION_MODEL_PROCESS) %>%
    unique() %>%
    mutate(PERMUTATION_DESCRIPTION2=case_when(inMSA ~ paste0("MSA ",MSA_NAME_COUNTY),
                                              inJD ~ paste0("Judicial District ",JUDICIAL_DISTRICT_NAME),
                                              inFO ~ paste0("Field Office ",FIELD_OFFICE_NAME))) %>%
    select(PERMUTATION_DESCRIPTION2,DER_ORI_CALIBRATION_MODEL=listVars,DER_ORI_CALIBRATION_MODEL_PROCESS)
  
  #####
  #Stack lists together
  calVars <- calVars1 %>%
    bind_rows(calVars2)
} else {#Earlier: just use ORI-level calibration variables
  calVars <- calVars1
}

#####
#Merge onto permutation file
permFile2 <- permFile %>%
  mutate(PERMUTATION_DESCRIPTION2=ifelse(str_detect(PERMUTATION_DESCRIPTION,"(Tribal|University)"),
                                         PERMUTATION_DESCRIPTION,
                                         PERMUTATION_DESCRIPTION %>%
										   str_extract("(National|Regional|State|MSA|Judicial District|Field Office).*") %>%
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
                                "POP_TOTALS_PERM_", CONST_YEAR, "_FINAL.csv"), 
                    na="")

log_info("Finished Add_on_Calibration_Variables.R")