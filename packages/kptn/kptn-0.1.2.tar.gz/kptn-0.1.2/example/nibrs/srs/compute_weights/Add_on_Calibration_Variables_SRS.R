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

log_info("Running Add_on_Calibration_Variables.R")

#####
#Load files

#ORI-level frame
#calDat1 <- read_csv_logging(file=paste0(output_weighting_data_folder,"SF_postS.csv"))

#Sub-state frame (2021+)

calDat2 <- read_csv_logging(file=paste0(output_weighting_data_folder,"SF_postMSA_cal_srs_altcombs_col_srs.csv"))

#Perm file
permFile <- read_csv_logging(paste0(filepathin_initial, "POP_TOTALS_PERM_", CONST_YEAR, "_SRS.csv"))

#National crosses
# natCrosses <- paste0(input_weighting_data_folder,"Geography_Crossings.xlsx") %>%
#   read_xlsx(sheet="National") %>%
#   mutate(natLvl="National") %>%
#   rename(wgtGpNational=natWgtGp,
#          crossNum=natCrossNum)
# 
# #Region crosses
# regCrosses <- paste0(input_weighting_data_folder,"Geography_Crossings.xlsx") %>%
#   read_xlsx(sheet="Region") %>%
#   rename(REGION_NAME=regLvl,
#          wgtGpRegion=regWgtGp,
#          crossNum=regCrossNum) %>%
#   mutate(inReg=TRUE)
# 
# #State crossses
# stateCrosses <- paste0(input_weighting_data_folder,"Geography_Crossings.xlsx") %>%
#   read_xlsx(sheet="State") %>%
#   rename(STATE_NAME=stateLvl,
#          wgtGpState=stateWgtGp,
#          crossNum=stateCrossNum) %>%
#   mutate(inState=TRUE)

#Sub-state estimates (only for 2021+)

#FO crosses
foCrosses <- paste0(input_weighting_data_folder,"Geography_Crossings_SRS.xlsx") %>%
  read_xlsx(sheet="FO") %>%
  rename(FIELD_OFFICE_NAME=foLvl,
         wgtGpFO=foWgtGp,
         crossNum=foCrossNum) %>%
  mutate(inFO=TRUE)

#JD crosses
jdCrosses <- paste0(input_weighting_data_folder,"Geography_Crossings_SRS.xlsx") %>%
  read_xlsx(sheet="JD") %>%
  rename(JUDICIAL_DISTRICT_NAME=jdLvl,
         wgtGpJD=jdWgtGp,
         crossNum=jdCrossNum) %>%
  mutate(inJD=TRUE)

#MSA crosses
msaCrosses <- paste0(input_weighting_data_folder,"Geography_Crossings_SRS.xlsx") %>%
  read_xlsx(sheet="MSA") %>%
  rename(MSA_NAME_COUNTY=msaLvl,
         wgtGpMSA=msaWgtGp,
         crossNum=msaCrossNum) %>%
  mutate(inMSA=TRUE)

#MD crosses
#Note (13Mar2024): Adding today
mdCrosses <- msaCrosses %>%
  subset(wgtGpMSA>3) %>%
  mutate(METRO_DIVISION_COUNTY=case_when(wgtGpMSA<=6 ~ 'Anaheim-Santa Ana-Irvine, CA',
										wgtGpMSA<=9 ~ 'Arlington-Alexandria-Reston, VA-WV',
										wgtGpMSA<=12 ~ 'Atlanta-Sandy Springs-Roswell, GA',
										wgtGpMSA<=15 ~ 'Boston, MA',
										wgtGpMSA<=18 ~ 'Cambridge-Newton-Framingham, MA',
										wgtGpMSA<=21 ~ 'Camden, NJ',
										wgtGpMSA<=24 ~ 'Chicago-Naperville-Schaumburg, IL',
										wgtGpMSA<=27 ~ 'Dallas-Plano-Irving, TX',
										wgtGpMSA<=30 ~ 'Detroit-Dearborn-Livonia, MI',
										wgtGpMSA<=33 ~ 'Elgin, IL',
										wgtGpMSA<=36 ~ 'Everett, WA',
										wgtGpMSA<=39 ~ 'Fort Lauderdale-Pompano Beach-Sunrise, FL',
										wgtGpMSA<=42 ~ 'Fort Worth-Arlington-Grapevine, TX',
										wgtGpMSA<=45 ~ 'Frederick-Gaithersburg-Bethesda, MD',
										wgtGpMSA<=48 ~ 'Lake County, IL',
										wgtGpMSA<=51 ~ 'Lake County-Porter County-Jasper County, IN',
										wgtGpMSA<=54 ~ 'Lakewood-New Brunswick, NJ',
										wgtGpMSA<=57 ~ 'Los Angeles-Long Beach-Glendale, CA',
										wgtGpMSA<=60 ~ 'Marietta, GA',
										wgtGpMSA<=63 ~ 'Miami-Miami Beach-Kendall, FL',
										wgtGpMSA<=66 ~ 'Montgomery County-Bucks County-Chester County, PA',
										wgtGpMSA<=69 ~ 'Nassau County-Suffolk County, NY',
										wgtGpMSA<=72 ~ 'New York-Jersey City-White Plains, NY-NJ',
										wgtGpMSA<=75 ~ 'Newark, NJ',
										wgtGpMSA<=78 ~ 'Oakland-Fremont-Berkeley, CA',
										wgtGpMSA<=81 ~ 'Philadelphia, PA',
										wgtGpMSA<=84 ~ 'Rockingham County-Strafford County, NH',
										wgtGpMSA<=87 ~ 'San Francisco-San Mateo-Redwood City, CA',
										wgtGpMSA<=90 ~ 'San Rafael, CA',
										wgtGpMSA<=93 ~ 'Seattle-Bellevue-Kent, WA',
										wgtGpMSA<=96 ~ 'St. Petersburg-Clearwater-Largo, FL',
										wgtGpMSA<=99 ~ 'Tacoma-Lakewood, WA',
										wgtGpMSA<=102 ~ 'Tampa, FL',
										wgtGpMSA<=105 ~ 'Warren-Troy-Farmington Hills, MI',
										wgtGpMSA<=108 ~ 'Washington, DC-MD',
										wgtGpMSA<=111 ~ 'West Palm Beach-Boca Raton-Delray Beach, FL',
										wgtGpMSA<=114 ~ 'Wilmington, DE-MD-NJ',
										TRUE ~ NA_character_)) %>%
  select(-MSA_NAME_COUNTY,-inMSA) %>%
  mutate(inMD=TRUE)
#FO model
foModel <- paste0(input_weighting_data_folder,"SRS_Variable_Combination_Convergence_by_FO_X_Weighting_Group_AltCombs_Collapsed_Automatic_SRS.xlsx") %>%
  read_xlsx()  %>%
  subset(Select=="X") %>%
  group_by(FIELD_OFFICE_NAME) %>%
  dplyr::summarize(nZero=sum(nVar==0),
                   nNonzero=sum(nVar>0)) %>%
  mutate(DER_ORI_CALIBRATION_MODEL_PROCESS_FO=!(nZero>0 & nNonzero==0)) %>%
  select(FIELD_OFFICE_NAME,DER_ORI_CALIBRATION_MODEL_PROCESS_FO)

#JD model
jdModel_raw <- paste0(input_weighting_data_folder,"SRS_Variable_Combination_Convergence_by_JD_X_Weighting_Group_AltCombs_Collapsed_Automatic_SRS.xlsx") %>%
  read_xlsx()  %>%
  subset(Select=="X") 

jdModel <- jdModel_raw %>%
  group_by(JUDICIAL_DISTRICT_NAME) %>%
  dplyr::summarize(nZero=sum(nVar==0),
                   nNonzero=sum(nVar>0)) %>%
  mutate(DER_ORI_CALIBRATION_MODEL_PROCESS_JD=!(nZero>0 & nNonzero==0)) %>%
  select(JUDICIAL_DISTRICT_NAME,DER_ORI_CALIBRATION_MODEL_PROCESS_JD)

#MSA model
#Note (13Mar2024): Takes a while to read in... given we're now needing for MSA and MDs, let's read in 1x and use for both
msaModel_raw <- paste0(input_weighting_data_folder,"SRS_Variable_Combination_Convergence_by_MSA_X_Weighting_Group_AltCombs_Collapsed_Automatic_SRS.xlsx") %>%
  read_xlsx()  %>%
  subset(Select=="X") 

msaModel <- msaModel_raw %>%
  group_by(MSA_NAME_COUNTY) %>%
  dplyr::summarize(nZero=sum(nVar==0),
                   nNonzero=sum(nVar>0)) %>%
  mutate(DER_ORI_CALIBRATION_MODEL_PROCESS_MSA=!(nZero>0 & nNonzero==0)) %>%
  select(MSA_NAME_COUNTY,DER_ORI_CALIBRATION_MODEL_PROCESS_MSA)
  
#MD model
#Note (13Mar2024): Added today
mdModel <- msaModel_raw %>%
  subset(wgtGpMSA>3) %>%
  mutate(METRO_DIVISION_COUNTY=case_when(wgtGpMSA<=6 ~ 'Anaheim-Santa Ana-Irvine, CA',
										wgtGpMSA<=9 ~ 'Arlington-Alexandria-Reston, VA-WV',
										wgtGpMSA<=12 ~ 'Atlanta-Sandy Springs-Roswell, GA',
										wgtGpMSA<=15 ~ 'Boston, MA',
										wgtGpMSA<=18 ~ 'Cambridge-Newton-Framingham, MA',
										wgtGpMSA<=21 ~ 'Camden, NJ',
										wgtGpMSA<=24 ~ 'Chicago-Naperville-Schaumburg, IL',
										wgtGpMSA<=27 ~ 'Dallas-Plano-Irving, TX',
										wgtGpMSA<=30 ~ 'Detroit-Dearborn-Livonia, MI',
										wgtGpMSA<=33 ~ 'Elgin, IL',
										wgtGpMSA<=36 ~ 'Everett, WA',
										wgtGpMSA<=39 ~ 'Fort Lauderdale-Pompano Beach-Sunrise, FL',
										wgtGpMSA<=42 ~ 'Fort Worth-Arlington-Grapevine, TX',
										wgtGpMSA<=45 ~ 'Frederick-Gaithersburg-Bethesda, MD',
										wgtGpMSA<=48 ~ 'Lake County, IL',
										wgtGpMSA<=51 ~ 'Lake County-Porter County-Jasper County, IN',
										wgtGpMSA<=54 ~ 'Lakewood-New Brunswick, NJ',
										wgtGpMSA<=57 ~ 'Los Angeles-Long Beach-Glendale, CA',
										wgtGpMSA<=60 ~ 'Marietta, GA',
										wgtGpMSA<=63 ~ 'Miami-Miami Beach-Kendall, FL',
										wgtGpMSA<=66 ~ 'Montgomery County-Bucks County-Chester County, PA',
										wgtGpMSA<=69 ~ 'Nassau County-Suffolk County, NY',
										wgtGpMSA<=72 ~ 'New York-Jersey City-White Plains, NY-NJ',
										wgtGpMSA<=75 ~ 'Newark, NJ',
										wgtGpMSA<=78 ~ 'Oakland-Fremont-Berkeley, CA',
										wgtGpMSA<=81 ~ 'Philadelphia, PA',
										wgtGpMSA<=84 ~ 'Rockingham County-Strafford County, NH',
										wgtGpMSA<=87 ~ 'San Francisco-San Mateo-Redwood City, CA',
										wgtGpMSA<=90 ~ 'San Rafael, CA',
										wgtGpMSA<=93 ~ 'Seattle-Bellevue-Kent, WA',
										wgtGpMSA<=96 ~ 'St. Petersburg-Clearwater-Largo, FL',
										wgtGpMSA<=99 ~ 'Tacoma-Lakewood, WA',
										wgtGpMSA<=102 ~ 'Tampa, FL',
										wgtGpMSA<=105 ~ 'Warren-Troy-Farmington Hills, MI',
										wgtGpMSA<=108 ~ 'Washington, DC-MD',
										wgtGpMSA<=111 ~ 'West Palm Beach-Boca Raton-Delray Beach, FL',
										wgtGpMSA<=114 ~ 'Wilmington, DE-MD-NJ',
										TRUE ~ NA_character_)) %>%
  group_by(METRO_DIVISION_COUNTY) %>%
  dplyr::summarize(nZero=sum(nVar==0),
                   nNonzero=sum(nVar>0)) %>%
  mutate(DER_ORI_CALIBRATION_MODEL_PROCESS_MD=!(nZero>0 & nNonzero==0)) %>%
  select(METRO_DIVISION_COUNTY,DER_ORI_CALIBRATION_MODEL_PROCESS_MD)


#####
#Get calibration variables for national/region/state

#Note (23Jun2023): Eventually will need to fine-tune which calibration variables are assigned to regions and states, but for now assign all of them to full set (like national)

# calVars1 <- calDat1%>% 
#   colnames() %>% 
#   str_subset("^V\\d+") %>% 
#   data.frame(name=.) %>% 
#   mutate(crossNum=as.numeric(str_extract(name,"\\d+"))) %>% 
#   mutate(inNat=crossNum %in% natCrosses$crossNum,
#          inReg=crossNum %in% regCrosses$crossNum,
#          inState=crossNum %in% stateCrosses$crossNum,
#          natLvl=ifelse(inNat,"National",NA_character_)) %>%
#   left_join(natCrosses) %>%
#   left_join(regCrosses) %>%
#   left_join(stateCrosses) %>%
#   mutate(inNat=ifelse(is.na(inNat),FALSE,inNat),
#          inReg=ifelse(is.na(inReg),FALSE,inReg),
#          inState=ifelse(is.na(inState),FALSE,inState),
#          listVars=NA_character_) %>%
#   group_by(natLvl) %>%
#   mutate(listVars=ifelse(inNat,str_flatten(name,col=","),listVars)) %>%
#   group_by(REGION_NAME) %>%
#   mutate(listVars=ifelse(inReg,str_flatten(name,col=","),listVars)) %>%
#   group_by(STATE_NAME) %>%
#   mutate(listVars=ifelse(inState,str_flatten(name,col=","),listVars)) %>%
#   ungroup() %>%
#   select(natLvl,REGION_NAME,STATE_NAME,inNat,inReg,inState,listVars) %>%
#   unique() %>%
#   mutate(PERMUTATION_DESCRIPTION2=case_when(inNat ~ paste0("National"),
#                                             inReg ~ paste0("Regional ",REGION_NAME),
#                                             inState ~ paste0("State ",STATE_NAME))) %>%
#   select(PERMUTATION_DESCRIPTION2,DER_ORI_CALIBRATION_MODEL=listVars)

#Note (23Jun2023): Eventually will want to fine-tune which calibration variables are assigned to regions and states, but for now assign all of them to full set (like national)
#Note (29Jun2023): Started fine-tuning

#National Crosswalk
natCW <- calDat2 %>%
  select(JUDICIAL_DISTRICT_NAME) %>%
  unique() %>%
  left_join(jdCrosses) %>%
  select(crossNum,JUDICIAL_DISTRICT_NAME) %>%
  mutate(natLvl="National") %>%
  unique()

#Region Crosswalk
regCW <- calDat2 %>%
  select(JUDICIAL_DISTRICT_NAME,REGION_NAME_UNIV) %>%
  unique() %>%
  left_join(jdCrosses) %>%
  select(crossNum,JUDICIAL_DISTRICT_NAME,wgtGpJD,REGION_NAME_UNIV) %>%
  unique()

#Division Crosswalk
divCW <- calDat2 %>%
  select(JUDICIAL_DISTRICT_NAME,DIVISION_NAME_UNIV) %>%
  unique() %>%
  left_join(jdCrosses) %>%
  select(crossNum,JUDICIAL_DISTRICT_NAME,wgtGpJD,DIVISION_NAME_UNIV) %>%
  unique()

#State Crosswalk
stateCW <- calDat2 %>%
  select(JUDICIAL_DISTRICT_NAME,STATE_NAME_UNIV) %>%
  unique() %>%
  left_join(jdCrosses) %>%
  select(crossNum,JUDICIAL_DISTRICT_NAME,wgtGpJD,STATE_NAME_UNIV) %>%
  unique()

#Levels by geography  
natLvls <- "National"
regLvls <- calDat2 %>% pull(REGION_NAME_UNIV) %>% unique() %>% sort()
divLvls <- calDat2 %>% pull(STATE_NAME_UNIV) %>% unique() %>% sort()
stateLvls <- calDat2 %>% pull(STATE_NAME_UNIV) %>% unique() %>% sort()

#Determine if any region/divisions/states have all 0 models (based on JDs)
DER_ORI_CALIBRATION_MODEL_PROCESS_REGIONS <- jdModel_raw %>%
  left_join(regCW) %>%
  group_by(REGION_NAME_UNIV) %>%
  dplyr::summarize(nZero=sum(nVar==0),
                   nNonzero=sum(nVar>0)) %>%
  mutate(DER_ORI_CALIBRATION_MODEL_PROCESS_REGION=!(nZero>0 & nNonzero==0)) %>%
  select(REGION_NAME_UNIV,DER_ORI_CALIBRATION_MODEL_PROCESS_REGION)

DER_ORI_CALIBRATION_MODEL_PROCESS_DIVISIONS <- jdModel_raw %>%
  left_join(divCW) %>%
  group_by(DIVISION_NAME_UNIV) %>%
  dplyr::summarize(nZero=sum(nVar==0),
                   nNonzero=sum(nVar>0)) %>%
  mutate(DER_ORI_CALIBRATION_MODEL_PROCESS_DIVISION=!(nZero>0 & nNonzero==0)) %>%
  select(DIVISION_NAME_UNIV,DER_ORI_CALIBRATION_MODEL_PROCESS_DIVISION)

DER_ORI_CALIBRATION_MODEL_PROCESS_STATES <- jdModel_raw %>%
  left_join(stateCW) %>%
  group_by(STATE_NAME_UNIV) %>%
  dplyr::summarize(nZero=sum(nVar==0),
                   nNonzero=sum(nVar>0)) %>%
  mutate(DER_ORI_CALIBRATION_MODEL_PROCESS_STATE=!(nZero>0 & nNonzero==0)) %>%
  select(STATE_NAME_UNIV,DER_ORI_CALIBRATION_MODEL_PROCESS_STATE)

calVarsNat <- calDat2 %>%
  colnames() %>%
  str_subset("^V\\d+") %>%
  str_sort(numeric=TRUE) %>%
  data.frame(name=.) %>%
  mutate(crossNum=as.numeric(str_extract(name,"\\d+"))) %>%
  inner_join(natCW) %>%
  mutate(DER_ORI_CALIBRATION_MODEL_PROCESS=TRUE) %>% #Always process national
  group_by(natLvl) %>%
  mutate(listVars=str_flatten(name,col=",")) %>%
  ungroup() %>%
  mutate(PERMUTATION_DESCRIPTION2=natLvls) %>%
  select(PERMUTATION_DESCRIPTION2,DER_ORI_CALIBRATION_MODEL=listVars,DER_ORI_CALIBRATION_MODEL_PROCESS) %>%
  unique()

calVarsReg <- calDat2 %>%
  colnames() %>%
  str_subset("^V\\d+") %>%
  str_sort(numeric=TRUE) %>%
  data.frame(name=.) %>%
  mutate(crossNum=as.numeric(str_extract(name,"\\d+"))) %>%
  inner_join(regCW) %>%
  left_join(DER_ORI_CALIBRATION_MODEL_PROCESS_REGIONS) %>%
  group_by(REGION_NAME_UNIV) %>%
  mutate(listVars=str_flatten(name,col=",")) %>%
  ungroup() %>%
  mutate(PERMUTATION_DESCRIPTION2=paste0("Regional ",REGION_NAME_UNIV)) %>%
  select(PERMUTATION_DESCRIPTION2,DER_ORI_CALIBRATION_MODEL=listVars,DER_ORI_CALIBRATION_MODEL_PROCESS=DER_ORI_CALIBRATION_MODEL_PROCESS_REGION) %>%
  unique()


calVarsDiv <- calDat2 %>%
  colnames() %>%
  str_subset("^V\\d+") %>%
  str_sort(numeric=TRUE) %>%
  data.frame(name=.) %>%
  mutate(crossNum=as.numeric(str_extract(name,"\\d+"))) %>%
  inner_join(divCW) %>%
  left_join(DER_ORI_CALIBRATION_MODEL_PROCESS_DIVISIONS) %>%
  group_by(DIVISION_NAME_UNIV) %>%
  mutate(listVars=str_flatten(name,col=",")) %>%
  ungroup() %>%
  mutate(PERMUTATION_DESCRIPTION2=paste0("Census Division ",DIVISION_NAME_UNIV)) %>%
  select(PERMUTATION_DESCRIPTION2,DER_ORI_CALIBRATION_MODEL=listVars,DER_ORI_CALIBRATION_MODEL_PROCESS=DER_ORI_CALIBRATION_MODEL_PROCESS_DIVISION) %>%
  unique()

calVarsState <- calDat2 %>%
  colnames() %>%
  str_subset("^V\\d+") %>%
  str_sort(numeric=TRUE) %>%
  data.frame(name=.) %>%
  mutate(crossNum=as.numeric(str_extract(name,"\\d+"))) %>%
  inner_join(stateCW) %>%
  left_join(DER_ORI_CALIBRATION_MODEL_PROCESS_STATES) %>%
  group_by(STATE_NAME_UNIV) %>%
  mutate(listVars=str_flatten(name,col=",")) %>%
  ungroup() %>%
  mutate(PERMUTATION_DESCRIPTION2=paste0("State ",STATE_NAME_UNIV)) %>%
  select(PERMUTATION_DESCRIPTION2,DER_ORI_CALIBRATION_MODEL=listVars,DER_ORI_CALIBRATION_MODEL_PROCESS=DER_ORI_CALIBRATION_MODEL_PROCESS_STATE) %>%
  unique()


#####
#Repeat but for (ORI x county)-level for 2021+
# if (as.numeric(CONST_YEAR)>=2021){
#Note (13Mar2024): Adding metro divisions
calVars2 <- calDat2 %>% 
  colnames() %>% 
  str_subset("^V\\d+") %>% 
  data.frame(name=.) %>% 
  mutate(crossNum=as.numeric(str_extract(name,"\\d+"))) %>% 
  mutate(inMSA=crossNum %in% msaCrosses$crossNum,
         inJD=crossNum %in% jdCrosses$crossNum,
         inFO=crossNum %in% foCrosses$crossNum,
         inMD=crossNum %in% mdCrosses$crossNum) %>%
  {
  bind_rows(left_join(.,jdCrosses) %>%
  left_join(msaCrosses) %>%
  left_join(foCrosses) %>%
  left_join(foModel) %>%
  left_join(jdModel) %>%
  left_join(msaModel) %>% mutate(inMD=FALSE),
  left_join(.,mdCrosses) %>% mutate(inMSA=FALSE) %>% left_join(mdModel))
  }  %>%
  mutate(inJD=ifelse(is.na(inJD),FALSE,inJD),
         inMSA=ifelse(is.na(inMSA),FALSE,inMSA),
         inFO=ifelse(is.na(inFO),FALSE,inFO),
		 inMD=ifelse(is.na(inMD),FALSE,inMD),
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
  group_by(METRO_DIVISION_COUNTY) %>%
  mutate(listVars=ifelse(inMD,str_flatten(name,col=","),listVars),  
         DER_ORI_CALIBRATION_MODEL_PROCESS=ifelse(inMD,DER_ORI_CALIBRATION_MODEL_PROCESS_MD,DER_ORI_CALIBRATION_MODEL_PROCESS)) %>%
  ungroup() %>%
  mutate(DER_ORI_CALIBRATION_MODEL_PROCESS=ifelse(is.na(DER_ORI_CALIBRATION_MODEL_PROCESS),FALSE,DER_ORI_CALIBRATION_MODEL_PROCESS)) %>%
  select(JUDICIAL_DISTRICT_NAME,MSA_NAME_COUNTY,FIELD_OFFICE_NAME,METRO_DIVISION_COUNTY,inJD,inMSA,inFO,inMD,listVars,DER_ORI_CALIBRATION_MODEL_PROCESS) %>%
  unique() %>%
  mutate(PERMUTATION_DESCRIPTION2=case_when(inMSA ~ paste0("MSA ",MSA_NAME_COUNTY),
                                            inJD ~ paste0("Judicial District ",JUDICIAL_DISTRICT_NAME),
                                            inFO ~ paste0("Field Office ",FIELD_OFFICE_NAME),
											inMD ~ paste0("MD ",METRO_DIVISION_COUNTY))) %>%
  select(PERMUTATION_DESCRIPTION2,DER_ORI_CALIBRATION_MODEL=listVars,DER_ORI_CALIBRATION_MODEL_PROCESS)

#Stack
calVars <- bind_rows(calVarsNat,
                     calVarsReg,
                     calVarsDiv,
                     calVarsState,
                     calVars2)

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
                                "POP_TOTALS_PERM_", CONST_YEAR, "_FINAL_SRS.csv"), 
                    na="")

log_info("Finished Add_on_Calibration_Variables_SRS.R")