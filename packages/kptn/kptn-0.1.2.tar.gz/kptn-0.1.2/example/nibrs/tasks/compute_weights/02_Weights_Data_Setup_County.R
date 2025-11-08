#Note: this is a modified version of a program originally created by Taylor Lewis.
#Note (15May2024): Streamlining this program. Originally I went through the exact same operations as 02_Weights_Data_Setup.R, plus a bit more. Rather than redo much of the work from the agency-level program, I'm instead going to just use the output from that program and tweak it a bit (eg, merge on the population file)

### Purpose of program is to create a working NIBRS data set for implementing various calibration weighting strategies
### Author: Taylor Lewis
### Modified by JD Bunker
### Last updated: 20Jul2023


# key difference in this version is not treating all 400 NCS-X LEAs as reporters, only those that are reporting
# do not need to do naive design-based strategy here
# another modification on 9.28.20 is introducing a condition where we poststratify to combination of zeropop LEAs indicator and population size
#Note (JDB 20Jul2023): Incorporating outlier results

### load necessary packages
#source("http://pcwww.liv.ac.uk/~william/R/crosstab.r")
library(DescTools)
library(sampling)
library(data.table)
library(Hmisc)
library(mice)
library(party)
library(partykit)
library(tidyverse)
library(lubridate)
library(data.table)

log_info("Running 02_Weights_Data_Setup_County.R")

### preparing the sampling frame
# read in and recode the sampling frame
#Update (05NOV2021): Adding guess_max argument
#SF <- read_csv(paste0(output_weighting_data_folder,"cleanframe.csv"),
#               guess_max=1e6)
SF <- fread(paste0(output_weighting_data_folder,"SF.csv")) %>%
  data.frame() %>%
  mutate(in_nibrs=as.double(in_nibrs))


#LEA x County file
#Note (23May2023): Added today
#Note (05Jun2023): Updating to 2022 file
#Note (02May2024): Switching to reduced version
#pop_raw <- "//rtpnfil02/0216153_NIBRS/05_PopulationData/ANNUAL_PROCESS_CODEBASE/ANNUAL_RUNS/2021/DEV_0_1/07_FILE_CREATE/Data/allLEAsCntyCBISummaryFinal.xlsx" %>%
#  read_xlsx()
pop_raw <- file.path(external_path,file_locs[[year]]$cbi_summary_county_reduced) %>%
  read_xlsx()

#JD and FO crosswalks
jdCW <- "Data/JD_and_FO_Crosswalk.xlsx" %>%
  read_xlsx("JD") %>%
  rename(JUDICIAL_DISTRICT_CODE=JUDICIAL_DISTRICT_CODE_UNIV)
foCW <- "Data/JD_and_FO_Crosswalk.xlsx" %>%
  read_xlsx("FO") %>%
  rename(FIELD_OFFICE=FIELD_OFFICE_UNIV)


#23May2023: merging on LEA x county file
#01May2024: including METRO_DIVISION_COUNTY
#01May2024: swapping out POP1 for popResidAgcyCounty_cbi and adding propMult ... in addition, adding ORI (alongside LEGACY_ORI)
#pop <- pop_raw %>% select(LEGACY_ORI,state,county,COUNTY_NAME_CENSUS,MSA_NAME_COUNTY,JUDICIAL_DISTRICT_NAME,FIELD_OFFICE_NAME,POP1,METRO_DIVISION_COUNTY)
pop <- pop_raw %>% select(ORI,LEGACY_ORI,state,county,COUNTY_NAME_CENSUS,MSA_NAME_COUNTY,JUDICIAL_DISTRICT_NAME,FIELD_OFFICE_NAME,popResidAgcyCounty_cbi,propMult,METRO_DIVISION_COUNTY)
#19Apr2024: split up merge into a handful of steps: 1st on ORI=ORI, then ORI=LEGACY_ORI on the remainder, then stack
# SF <- SF %>% 
  # left_join(pop,by=c("ORI"="LEGACY_ORI")) %>%
  # mutate(MSA_NAME_COUNTY=ifelse(is.na(MSA_NAME_COUNTY),"Not Available",MSA_NAME_COUNTY),
         # JUDICIAL_DISTRICT_NAME=ifelse(is.na(JUDICIAL_DISTRICT_NAME),"Not Available",JUDICIAL_DISTRICT_NAME),
         # FIELD_OFFICE_NAME=ifelse(is.na(FIELD_OFFICE_NAME),"Not Available",FIELD_OFFICE_NAME),
		 # METRO_DIVISION_COUNTY=ifelse(is.na(METRO_DIVISION_COUNTY),"Not Available",METRO_DIVISION_COUNTY)) 
SF_1_inner <- SF %>%
  inner_join(pop %>% select(-LEGACY_ORI),by=c("ORI"="ORI"))
SF_1_anti <- SF %>%
  anti_join(pop %>% select(-LEGACY_ORI),by=c("ORI"="ORI"))
SF_2_inner <- SF_1_anti %>%
  inner_join(pop %>% select(-ORI),by=c("ORI"="LEGACY_ORI"))
SF_2_anti <- SF_1_anti %>%
  anti_join(pop %>% select(-ORI),by=c("ORI"="LEGACY_ORI"))
SF <- SF_1_inner %>%
  bind_rows(SF_2_inner,
            SF_2_anti) %>%
  mutate(MSA_NAME_COUNTY=ifelse(is.na(MSA_NAME_COUNTY),"Not Available",MSA_NAME_COUNTY),
         JUDICIAL_DISTRICT_NAME=ifelse(is.na(JUDICIAL_DISTRICT_NAME),"Not Available",JUDICIAL_DISTRICT_NAME),
         FIELD_OFFICE_NAME=ifelse(is.na(FIELD_OFFICE_NAME),"Not Available",FIELD_OFFICE_NAME),
		 METRO_DIVISION_COUNTY=ifelse(is.na(METRO_DIVISION_COUNTY),"Not Available",METRO_DIVISION_COUNTY)) 
#01May2024: switch to using propMult instead of propPOP1 and popResidAgcyCounty_cbi instead of POP1
SF <- SF%>%
  left_join(jdCW) %>%
  left_join(foCW) %>%
  #26May2023: use universe JD/MSA/FO if not on pop file
  #18Jun2024: don't update MSA/judicial district/county name anymore...
  # mutate(MSA_NAME_COUNTY=ifelse(MSA_NAME_COUNTY %in% c("Not Specified","Not Available") & (is.na(COUNTY_NAME_CENSUS)|COUNTY_NAME_CENSUS=="NOT SPECIFIED") & !is.na(MSA_NAME),MSA_NAME,MSA_NAME_COUNTY),
         # JUDICIAL_DISTRICT_NAME=ifelse(JUDICIAL_DISTRICT_NAME %in% c("Not Specified","Not Available") & (is.na(COUNTY_NAME_CENSUS)|COUNTY_NAME_CENSUS=="NOT SPECIFIED") & !is.na(JUDICIAL_DISTRICT_NAME_UNIV),JUDICIAL_DISTRICT_NAME_UNIV,JUDICIAL_DISTRICT_NAME),
         # FIELD_OFFICE_NAME=ifelse(FIELD_OFFICE_NAME %in% c("Not Specified","NS","Not Available") & (is.na(COUNTY_NAME_CENSUS)|COUNTY_NAME_CENSUS=="NOT SPECIFIED") & !is.na(FIELD_OFFICE_NAME_UNIV),FIELD_OFFICE_NAME_UNIV,FIELD_OFFICE_NAME)) %>%
  #29May2023: temp fix for missing JD/FO
  mutate(JUDICIAL_DISTRICT_NAME=case_when(ORI=="AZDI08900" ~ "Arizona",
                                          ORI=="CADIT1400" ~ "California Southern",
                                          ORI=="NMDI08300" ~ "New Mexico",
                                          ORI=="OKDI16000" ~ "Oklahoma Western",
                                          TRUE ~ JUDICIAL_DISTRICT_NAME),
         FIELD_OFFICE_NAME=case_when(ORI=="CADIT1400" ~ "San Diego",
                                     ORI=="MI780219E" ~ "Detroit",
                                     ORI=="PA001DE0X" ~ "Philadelphia",
                                     ORI=="PA003DE0X" ~ "Pittsburgh",
                                     TRUE ~ FIELD_OFFICE_NAME)) %>%
  #mutate(POP1=ifelse(is.na(POP1) & POPULATION==0,0,POP1)) %>%
  mutate(popResidAgcyCounty_cbi=ifelse(is.na(popResidAgcyCounty_cbi) & POPULATION==0,0,popResidAgcyCounty_cbi)) %>%
  #group_by(ORI_universe) %>%
  #mutate(propPOP1=POP1/sum(POP1,na.rm=TRUE)) %>%
  #mutate(propPOP1=ifelse(is.nan(propPOP1)|is.na(propPOP1),1,propPOP1)) %>%
  ungroup() %>%
  mutate(across(matches("^totcrime.*_imp"),
                #~.x*propPOP1),
				~.x*propMult),
         #POPULATION=POPULATION*propPOP1)
		 POPULATION=POPULATION*propMult)

#######################
# output data for next program in sequence

#write.csv(SF,
fwrite_wrapper(SF,
       paste0(output_weighting_data_folder,"SF_county.csv"))

log_info("Finished 02_Weights_Data_Setup_County.R\n\n")