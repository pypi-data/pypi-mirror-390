## Program Outline


#   * Read in packages, create new functions
# * Read in raw data
# * Check that all raw ORIs are in the universe file - output any ORIs not found in universe <-send these to Dan
# * Manipulate/clean raw data - fix ORIs identified above if possible, select necessary variables, create indicators
# * Merge data - left join onto eligible universe file
# * Check merged file
# * Output clean frame

#Note (JDB 20Jul2023): Incorporating outlier detection results

#########################
## Step 1: Read in packages, create new functions

#Read in Packages
library(tidyverse)
library(DBI)
library(readxl)
library(DT)
library(lubridate)
library(rjson)
library(reshape2)

source(here::here("tasks/logging.R"))


outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")
inputPipelineDir <- Sys.getenv("INPUT_PIPELINE_DIR")
external_path <- Sys.getenv("EXTERNAL_FILE_PATH")

output_folder <- sprintf("%s", outputPipelineDir)
input_folder <- sprintf("%s", inputPipelineDir)

input_weighting_data_folder = paste0(inputPipelineDir, "/srs/weighting/Data/")
output_weighting_folder = paste0(outputPipelineDir, "/srs/weighting/")
output_weighting_data_folder = paste0(outputPipelineDir, "/srs/weighting/Data/")
output_weighting_tableshell_folder = paste0(outputPipelineDir, "/srs/weighting/TableShells/")
output_weighting_populated_folder = paste0(outputPipelineDir, "/srs/weighting/Populated/")
raw_srs_file_path = paste0(inputPipelineDir, "/initial_tasks_output/")

directories = c(input_weighting_data_folder,output_weighting_folder, output_weighting_data_folder,output_weighting_tableshell_folder,output_weighting_populated_folder)

for (d in directories) {
  if (! dir.exists(d)) {
    dir.create(d, recursive = TRUE)
  }
}

file_locs <- fromJSON(file = sprintf("%s/external_file_locations.json", input_folder))

year <- Sys.getenv("DATA_YEAR")
log_info("Running 01_Create_Clean_Frame.R")


#Create new functions
`%notin%` <- Negate(`%in%`) #creates opposite of %in%
strip_toupper <- compose(toupper, partial(trimws, which="both") )
tableshowna <- partial(table, useNA="ifany")

checkfunction <- function(data, ...){
  log_debug("Calling checkfunction")
  raw1 <- data %>% group_by(...) %>% summarise(count=n())
  datatable(raw1)
}


#########################
## Step 2: Read in raw data


#READ IN RAW DATA
ucr_srs_clean_raw <- paste0(raw_srs_file_path,"/UCR_SRS_",year,"_clean_reta_mm_selected_vars.csv") %>%
  read_csv()


##########
#outlier detection - read in file
outlier_raw<- paste0(output_folder,"/outlier_data/outlier_data_file.csv") %>%
  read_csv_logging(guess_max=1e6)


#########################
## Step 3: Check that all raw ORIs are in the universe file
###CHECKS ON RAW DATA TO MAKE SURE ALL ORI IN EACH FILE ARE ALSO IN UNIVERSE


#reta mm  ORI X universe ORI
# length(reta_mm_raw$ORI[reta_mm_raw$ORI %notin% univ_raw$LEGACY_ORI]) #none
# if (length(reta_mm_raw$ORI[reta_mm_raw$ORI %notin% univ_raw$LEGACY_ORI])>0){
#   reta_mm_raw$ORI[reta_mm_raw$ORI %notin% univ_raw$LEGACY_ORI]
# }


#########################
## Step 4: Manipulate/clean raw data


# UNIVERSE
# keeps all universe variables for eligible agencies
#
#Note (27OCT2021): AGENCY_STATUS requirement for eligibility has changed from AGENCY_STATUS="ACTIVE" to AGENCY_STATUS="A". This has been the case for a while before today.
# eligible defined as
# 1) it is located within the geographical area of 50 states and Washington, D.C. and
# 2) has responsibility to report crimes (AGENCY in the missingmonths report data and is shown as AGENCY_STATUS="ACTIVE";   DORMANT_FLAG=N; COVERED_FLAG=N)
#
# 50 states and DC
# note: Nebraska is NB
# note: FS or Federal is considered in US

# PL update on 20200422:
#   Current Definition of Eligible agencies:
#   * AGENCY_STATUS="Active",
# * COVERED_FLAG="N",
# * DORMANT_FLAG="N",
# * AGENCY_TYPE_NAME != "Federal", and
# * STATE_NAME in 1 of the 50 official states + D.C

# JDB update on 27OCT2021:
#   Current Definition of Eligible agencies:
#   * AGENCY_STATUS="A",
# * COVERED_FLAG="N",
# * DORMANT_FLAG="N",
# * AGENCY_TYPE_NAME != "Federal", and
# * STATE_NAME in 1 of the 50 official states + D.C

###MANIPULATE RAW DATA

#Drop Federal FS as state below

states_name= c(
  'ALABAMA',
  'ALASKA',
  'ARIZONA',
  'ARKANSAS',
  'CALIFORNIA',
  'COLORADO',
  'CONNECTICUT',
  'DELAWARE',
  'DISTRICT OF COLUMBIA',
  'FLORIDA',
  'GEORGIA',
  'HAWAII',
  'IDAHO',
  'ILLINOIS',
  'INDIANA',
  'IOWA',
  'KANSAS',
  'KENTUCKY',
  'LOUISIANA',
  'MAINE',
  'MARYLAND',
  'MASSACHUSETTS',
  'MICHIGAN',
  'MINNESOTA',
  'MISSISSIPPI',
  'MISSOURI',
  'MONTANA',
  'NEBRASKA',
  'NEVADA',
  'NEW HAMPSHIRE',
  'NEW JERSEY',
  'NEW MEXICO',
  'NEW YORK',
  'NORTH CAROLINA',
  'NORTH DAKOTA',
  'OHIO',
  'OKLAHOMA',
  'OREGON',
  'PENNSYLVANIA',
  'RHODE ISLAND',
  'SOUTH CAROLINA',
  'SOUTH DAKOTA',
  'TENNESSEE',
  'TEXAS',
  'UTAH',
  'VERMONT',
  'VIRGINIA',
  'WASHINGTON',
  'WEST VIRGINIA',
  'WISCONSIN',
  'WYOMING')



#PL update on 20200422:
#Current Definition of Eligible agencies:
#
# AGENCY_STATUS="Active", COVERED_FLAG="N", DORMANT_FLAG="N", AGENCY_TYPE_NAME != "Federal", and STATE_NAME in 1 of the 50 official states + D.C

#JDB update on 27OCT2021:
#Current Definition of Eligible agencies:
#
# AGENCY_STATUS="A", COVERED_FLAG="N", DORMANT_FLAG="N", AGENCY_TYPE_NAME != "Federal", and STATE_NAME in 1 of the 50 official states + D.C


ucr_srs_clean <- ucr_srs_clean_raw %>%
  mutate(in_univ=1,
         ori7=substr(ORI,1,7),
         #legacy_ori7=substr(LEGACY_ORI,1,7),
         #LEGACY_ORI= as.character(LEGACY_ORI),
         DATA_YEAR=DATA_YEAR_UNIV,
         ORI_UNIVERSE=as.character(ORI),
         FEMALE_OFFICER_UNIV=ifelse(is.na(FEMALE_OFFICER_UNIV),0,FEMALE_OFFICER_UNIV),
         MALE_OFFICER_UNIV=ifelse(is.na(MALE_OFFICER_UNIV),0,MALE_OFFICER_UNIV),
         totofficer= FEMALE_OFFICER_UNIV+ MALE_OFFICER_UNIV,
         agency_type= ifelse(AGENCY_TYPE_NAME_UNIV== 'State Police' |
                               AGENCY_TYPE_NAME_UNIV=='Other State Agency'|
                               AGENCY_TYPE_NAME_UNIV=="University or College", 'State',
                             ifelse(AGENCY_TYPE_NAME_UNIV=='County', 'C&T',
                                    ifelse(AGENCY_TYPE_NAME_UNIV=='City', 'Municipal',
                                           ifelse(AGENCY_TYPE_NAME_UNIV=='Tribal', 'Tribal', 'Remainder')))),
         stratum_f= ifelse(totofficer>=750, 2,
                           ifelse(totofficer > 0 & totofficer<750 & agency_type=="State", 3,
                                  ifelse(totofficer==0 & agency_type %in% c("State","Municipal"), 4,
                                         ifelse(totofficer %in% 36:749 & agency_type=="C&T", 5,
                                                ifelse(totofficer %in% 0:35 & agency_type=="C&T", 6,
                                                       ifelse(totofficer %in% 181:749 & agency_type=="Municipal", 7,
                                                              ifelse(totofficer %in% 61:180 & agency_type=="Municipal", 8,
                                                                     ifelse(totofficer %in% 16:60 &
                                                                              agency_type=="Municipal", 9,
                                                                            ifelse(totofficer %in% 1:15 &
                                                                                     agency_type=="Municipal", 10,
                                                                                   ifelse(agency_type=="Tribal", 12, 11)))))))))),

         in_univ_elig_state = strip_toupper(STATE_NAME_UNIV) %in% states_name,

         in_univ_elig = strip_toupper(AGENCY_STATUS_UNIV) == "A" &
           strip_toupper(COVERED_FLAG_UNIV) == "N" &
           strip_toupper(DORMANT_FLAG_UNIV) == "N" &
           strip_toupper(AGENCY_TYPE_NAME_UNIV) != "FEDERAL" &
           in_univ_elig_state == TRUE)




#####################
######Monthly indicators#######
#####################
months <- ucr_srs_clean %>%
  #Note (16May2023): Subsetting to non-missing state names to avoid issues with merging
  subset(!is.na(STATE_NAME_UNIV)) %>%
  mutate(variable="srs_month",
         one=1) %>%
  mutate(across(paste0(month.abb %>% str_to_lower(),"_mm_flag"),
                function(i){
                  case_when(is.na(i)~0,
                            i==9~1,#Note (17May2023): Changing 9s to 1s
                            TRUE ~ i)
                  })) %>%
  mutate(srs_month=paste0(jan_mm_flag,feb_mm_flag,mar_mm_flag,
                            "-",
                            apr_mm_flag,may_mm_flag,jun_mm_flag,
                            "-",
                            jul_mm_flag,aug_mm_flag,sep_mm_flag,
                            "-",
                            oct_mm_flag,nov_mm_flag,dec_mm_flag)) %>%
  select(AGENCY_ID_UNIV,srs_month) %>%
  mutate(in_srs_month=1)

#####################
####Reta MM  ####
#####################
# filterout_state = c("American Samoa", "U.S. Virgin Islands", "Canal Zone", "Puerto Rico", "Mariana Islands", "Guam", "Federal", "Other")
# 
# reta_mm <- reta_mm_raw %>%
#   filter(STATE_NAME %notin% filterout_state) %>%
#   mutate(ORI= as.character(ORI), in_reta_MM=1, reta_MM = paste0(JAN_MM_FLAG,	FEB_MM_FLAG,	MAR_MM_FLAG, "-",
#                                                                           APR_MM_FLAG,  MAY_MM_FLAG,	JUN_MM_FLAG, "-",
#                                                                           JUL_MM_FLAG,	AUG_MM_FLAG,	SEP_MM_FLAG, "-",
#                                                                           OCT_MM_FLAG, 	NOV_MM_FLAG,	DEC_MM_FLAG)) %>%
#   select(ORI, reta_MM, in_reta_MM)
# 
# #checks
# glimpse(reta_mm) #ORI - 9 digits, reta_MM_2020 - 12 digits, in_reta_MM_2020 indicator)
# table(reta_mm$in_reta_MM)#all 1
# 
# #NEW check:  See which agencies are eligible
# #Check the states
# checkfunction(reta_mm_raw %>%
#                 filter(STATE_NAME %notin% filterout_state), STATE_NAME)
# 
# checkfunction(reta_mm_raw %>%
#                 filter(STATE_NAME %notin% filterout_state) %>%
#                 mutate(ORI= as.character(ORI), in_reta_MM=1, reta_MM = paste0(JAN_MM_FLAG,	FEB_MM_FLAG,	MAR_MM_FLAG, "-",
#                                                                                         APR_MM_FLAG,  MAY_MM_FLAG,	JUN_MM_FLAG, "-",
#                                                                                         JUL_MM_FLAG,	AUG_MM_FLAG,	SEP_MM_FLAG, "-",
#                                                                                         OCT_MM_FLAG, 	NOV_MM_FLAG,	DEC_MM_FLAG)),
# 
# 
#               reta_MM,
#               JAN_MM_FLAG,	FEB_MM_FLAG,	MAR_MM_FLAG,
#               APR_MM_FLAG,  MAY_MM_FLAG,	JUN_MM_FLAG,
#               JUL_MM_FLAG,	AUG_MM_FLAG,	SEP_MM_FLAG,
#               OCT_MM_FLAG, 	NOV_MM_FLAG,	DEC_MM_FLAG)


#####################
####Outlier  ####
#####################
#12Nov2024: updating to support years outside 21st century
outlier <- outlier_raw %>%
  #select(ori,matches(paste0("\\w{3}-",as.numeric(year)-2000)))
  select(ori,matches(paste0("\\w{3}-",str_pad(as.numeric(year)-100*floor(as.numeric(year)/100),side="left",width=2,pad="0"))))
  
#Rename months to exclude year
colnames(outlier) <- colnames(outlier) %>% str_remove("-\\d+")

#Now let's melt then create a reporting pattern similar to nibrs_month
#19Apr2024: instead of assigning missing outlier indicator to 0, assign as a space
#           in addition, will also need to convert 0 and 1 from numeric to character
outlier <- outlier %>%
 melt(id.vars="ori") %>%
 mutate(value=case_when(is.na(value) ~ " ",#0,
                        value %in% c("red","orange") ~ "0",#0,
						TRUE ~ "1")) %>% #1)) %>%
 dcast(ori ~ variable) %>%
 mutate(outlier=paste0(Jan,Feb,Mar,
                            "-",
                            Apr,May,Jun,
                            "-",
                            Jul,Aug,Sep,
                            "-",
                            Oct,Nov,Dec)) %>%
  select(ORI=ori,outlier) %>%
  mutate(in_outlier=1)


#########################
## Step 5: Merge data
##MERGE DATA


#Assign universe data as final_1
#Note (16May2023): Subsetting on state name to avoid dups that have mostly NAs
final_1 <- ucr_srs_clean %>% subset(!is.na(STATE_NAME_UNIV))

##############################Merge on the nibrs_month############################################
maindata_1 <- inner_join(final_1, months, by = c("AGENCY_ID_UNIV"="AGENCY_ID_UNIV"))
log_dim(maindata_1)

#Get the unmatched ones
maindata_1_anti_join <- final_1 %>%
  anti_join(months, by = c("AGENCY_ID_UNIV"="AGENCY_ID_UNIV")) %>%
  #Since not every LEA in nibrs_month, set all LEAs not in table as if didn't respond
  mutate(srs_month="000-000-000-000",
         in_srs_month=0)
log_dim(maindata_1_anti_join)



#Stack all the datasets together
final_1 <- bind_rows(maindata_1, maindata_1_anti_join) %>%
  #Note (16May2023): Adding in_srs indicator
  mutate(in_srs=str_detect(srs_month,"1")>=1) %>%
  mutate(in_srs=ifelse(in_srs==FALSE,0,1))
log_dim(ucr_srs_clean)
log_dim(final_1)
log_dim(months)

#Delete the dataset
rm(list=c("maindata_1", "maindata_1_anti_join" ))

checkfunction(final_1, in_univ_elig, in_srs_month)
checkfunction(final_1, in_srs_month)



##############################Merge on the outlier############################################
#Update (19JUL2023): Added outlier section

maindata_1 <- inner_join(final_1, outlier, by = c("ORI"="ORI"))
log_dim(maindata_1)

#Get the unmatched ones
maindata_1_anti_join <- final_1 %>%
  anti_join(outlier, by = c("ORI"="ORI")) %>%
  #Since not every LEA in nibrs_month, set all LEAs not in table as if didn't respond
  mutate(outlier="   -   -   -   ",
         in_outlier=0)
log_dim(maindata_1_anti_join)



#Stack all the datasets together
final_1 <- bind_rows(maindata_1, maindata_1_anti_join)

log_dim(outlier)
log_dim(final_1)
log_dim(months)

#Delete the dataset
rm(list=c("maindata_1", "maindata_1_anti_join" ))

checkfunction(final_1, in_univ_elig, in_srs_month)
checkfunction(final_1, in_srs_month)



##############################Subset to eligible##########################################


cleanframe <- final_1 %>% filter(in_univ_elig == 1)


#########################
## Step 6: Check merged file

##CHECKS ON MERGED FILE
#Note (27OCT2021): Not using but leaving commented-out code for now
#dim(cleanframe) #same number of rows as univ which is all eligible agencies
#dim(univ %>% filter(in_univ_elig))

#all have an ORI
#cleanframe %>% filter(is.na(ORI) & in_univ == 1) %>% print()
# cleanframe %>% filter(is.na(ORI) & in_reta_MM_ == 1) %>% print()
#

#########################
## Step 7: Output clean frame
##WRITE CSV

cleanframe %>%
  write_dot_csv_logging(paste0(output_weighting_data_folder,"cleanframe_srs.csv"),
            na = "", row.names=FALSE)

log_info("Finished 01_Create_Clean_Frame_SRS.R\n\n")
