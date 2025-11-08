### script that creates the datasets for the gun module tables

library(tidyverse)
library(openxlsx)
library(DBI)
library(DT)
library(lubridate)
library(readxl)
library(data.table)
library(rjson)

source(here::here("tasks/logging.R"))


#input/output directories for pipeline artifacts
outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")
inputPipelineDir <- Sys.getenv("INPUT_PIPELINE_DIR")
external_path <- Sys.getenv("EXTERNAL_FILE_PATH")

filepathout = paste0(outputPipelineDir, "/markdown/") #output path for markdown files

if (! dir.exists(filepathout)) {
  dir.create(filepathout, recursive = TRUE)
}

der_file_path = paste0(outputPipelineDir, "/indicator_table_extracts/") #output path for all the data extracts

if (! dir.exists(der_file_path)) {
  dir.create(der_file_path, recursive = TRUE)
}

#External files json
input_folder <- sprintf("%s", inputPipelineDir)
file_locs <- fromJSON(file = sprintf("%s/external_file_locations.json", input_folder))

#set-up year
CONST_YEAR <- Sys.getenv("DATA_YEAR")

log_info("Starting 00c_Create_Firearm_Datasets.R...")
#############################Need to create new victim imputed outputs#########################

source(here::here("tasks/impute_items/0-Common_functions_for_imputation.R"))

###############################################################################################

#Write the function for common offense recode

fire_arm_offense_recode <- function(data){
  
  returndata <- data %>% mutate(
    
    
    # NOTE:  Total Gun Violence includes the following offenses:
    # 
    # 1.	Murder and Non-negligent Manslaughter
    # 2.	Negligent Manslaughter
    # 3.	Revised Rape
    # 4.	Robbery
    # 5.	Aggravated Assault
    # 6.	Kidnapping/Abduction
    # 7.	Human Trafficking- Sex and Human Trafficking- Labor
    
    der_total_gun_violence = fcase(
      trim_upcase(offense_code) %in% c(
        
        "09A", #09A	Murder and Nonnegligent Manslaughter
        "09B", #09B	Negligent Manslaughter
        
        #Revised Rape#################################
        "11A", #11A	Rape
        "11B", #11B Sodomy
        "11C",  #11C Sexual Assault With An Object    
        #############################################
        
        "120",  #120 Robbery
        "13A",  #13A	Aggravated Assault
        "100",  #100  Kidnapping/Abduction
        "64A",  #64A	Human Trafficking, Commercial Sex Acts
        "64B"  #64B	Human Trafficking, Involuntary Servitude
      ),  1, 
      default = 0),   
    
    der_total_gun_violence_no_rob = fcase(
      trim_upcase(offense_code) %in% c(
        
        "09A", #09A	Murder and Nonnegligent Manslaughter
        "09B", #09B	Negligent Manslaughter
        
        #Revised Rape#################################
        "11A", #11A	Rape
        "11B", #11B Sodomy
        "11C",  #11C Sexual Assault With An Object    
        #############################################
        
        #"120",  #120 Robbery
        "13A",  #13A	Aggravated Assault
        "100",  #100  Kidnapping/Abduction
        "64A",  #64A	Human Trafficking, Commercial Sex Acts
        "64B"  #64B	Human Trafficking, Involuntary Servitude
      ),  1, 
      default = 0), 	
    
    # NOTE:  Fatal Gun Violence:
    # 
    # 1.	Murder and Non-negligent Manslaughter
    
    der_fatal_gun_violence = fcase(
      trim_upcase(offense_code) %in% c(
        
        "09A" #09A	Murder and Nonnegligent Manslaughter
        
      ),  1, 
      default = 0), 
    
    # NOTE:  Nonfatal Gun Violence:
    # 
    # 1.	Revised Rape
    # 2.	Robbery
    # 3.	Aggravated Assault
    # 4.	Kidnapping/Abduction
    # 5.	Human Trafficking- Sex and Human Trafficking- Labor
    
    der_nonfatal_gun_violence = fcase(
      trim_upcase(offense_code) %in% c(
        
        #Revised Rape#################################
        "11A", #11A	Rape
        "11B", #11B Sodomy
        "11C",  #11C Sexual Assault With An Object    
        #############################################
        
        "120",  #120 Robbery
        "13A",  #13A	Aggravated Assault
        "100",  #100  Kidnapping/Abduction
        "64A",  #64A	Human Trafficking, Commercial Sex Acts
        "64B"  #64B	Human Trafficking, Involuntary Servitude
      ),  1, 
      default = 0),   
    
    der_nonfatal_gun_violence_no_rob = fcase(
      trim_upcase(offense_code) %in% c(
        
        #Revised Rape#################################
        "11A", #11A	Rape
        "11B", #11B Sodomy
        "11C",  #11C Sexual Assault With An Object    
        #############################################
        
        #"120",  #120 Robbery
        "13A",  #13A	Aggravated Assault
        "100",  #100  Kidnapping/Abduction
        "64A",  #64A	Human Trafficking, Commercial Sex Acts
        "64B"  #64B	Human Trafficking, Involuntary Servitude
      ),  1, 
      default = 0), 
    
    # NOTE:  Nonfatal Gun Violence 2:
    # 
    # 1.	Revised Rape
    # 2.	Robbery
    # 3.	Aggravated Assault
    
    der_nonfatal_gun_violence2 = fcase(
      trim_upcase(offense_code) %in% c(
        
        #Revised Rape#################################
        "11A", #11A	Rape
        "11B", #11B Sodomy
        "11C",  #11C Sexual Assault With An Object    
        #############################################
        
        "120",  #120 Robbery
        "13A"  #13A	Aggravated Assault
      ),  1, 
      default = 0),
    
    der_nonfatal_gun_violence2_no_rob = fcase(
      trim_upcase(offense_code) %in% c(
        
        #Revised Rape#################################
        "11A", #11A	Rape
        "11B", #11B Sodomy
        "11C",  #11C Sexual Assault With An Object    
        #############################################
        
        #"120",  #120 Robbery
        "13A"  #13A	Aggravated Assault
      ),  1, 
      default = 0)
    
  )  
  
  return(returndata)
  
}


#Need to read in the clean offenses dataset
raw_offenses <- fread(paste0(der_file_path, "cleaned_recoded_all_Offenses_recoded_offenses.csv.gz"), 
					  colClasses = list(character = c("offense_code"))) %>%
  #Need to code the new offenses
  fire_arm_offense_recode()

#Check the recodes
# raw_offenses %>% checkfunction(der_total_gun_violence, der_total_gun_violence_no_rob, crime_against, offense_code, offense_name)
# raw_offenses %>% checkfunction(der_fatal_gun_violence, crime_against, offense_code, offense_name)
# raw_offenses %>% checkfunction(der_nonfatal_gun_violence, der_nonfatal_gun_violence_no_rob, crime_against, offense_code, offense_name)
# raw_offenses %>% checkfunction(der_nonfatal_gun_violence2, der_nonfatal_gun_violence2_no_rob, crime_against, offense_code, offense_name)

#Need to read in the weapon involved extract:  agg_weapon_yes_cat_offenses.csv.gz with the following levels:
#1 Personal weapons
#2 Firearms
#3 Knives and other cutting instruments
#4 Blunt instruments
#5 Other non-personal weapons
#6 Unknown

#Note this data is at the incident_id, victim_id, offense_id level but may be duplicated since more than 1 weapon could be reported for each offense id
raw_weapon_offense <- fread(paste0(der_file_path, "agg_weapon_yes_cat_offenses.csv.gz"))

#Subset to offense records with firearm recodes
raw_weapon_offense_firearm <- raw_weapon_offense %>%
  filter(der_weapon_yes_cat == 2) %>% #2 Firearms
  select(incident_id, victim_id, offense_id )

#Check the dimension
log_dim(raw_weapon_offense_firearm)
log_dim(raw_weapon_offense)

#Join the data by the common variables
raw_offenses_weapon <- raw_offenses %>%
  inner_join(raw_weapon_offense_firearm, by = c("incident_id", "victim_id", "offense_id"))

#Check the dimension
log_dim(raw_offenses_weapon)
log_dim(raw_offenses)
log_dim(raw_weapon_offense_firearm)

#Need to make sure that raw_offenses_weapon is unique at the "ori", "incident_id", "victim_id", "offense_id" level.  Note ori is included since we are using the block imputed dataset

raw_test <- raw_offenses_weapon %>%
  count(ori, incident_id, victim_id, offense_id) %>%
  filter(n > 1)

#Make sure that the row is zero
nrow(raw_test)

#Output to share
raw_offenses_weapon %>% 
  write_csv(gzfile(paste0(der_file_path,"/cleaned_recoded_all_Firearm_Offenses_recoded_offenses.csv.gz")), na="") 


#Using raw_offenses_weapon, count the number of firearm victims in an incident
#Note is the block imputed data, so need the original records
raw_offenses_weapon_victim_count <- raw_offenses_weapon %>%
  #Need the non-imputed block data since we are counting the original records only 
  filter(der_imputed_incident == 0) %>%
  #Need to filter to person victims
  #Victim Type code = I is Individual; Victim Type code = L is Law Enforcement Officer;
  filter(victim_type_code %in% c("I", "L")) %>% 
  #Need to deduplicate the number of victims
  count(incident_id, victim_id) %>%
  #Drop the n variable
  select(-n) %>%
  #Count at the incident level
  group_by(incident_id) %>%
  summarise(raw_victim_count = n() ) %>% 
  ungroup() %>%
  mutate(der_number_of_victims_firearm_cat = fcase(
    raw_victim_count == 1, 1, # 1
    raw_victim_count == 2, 2, # 2
    raw_victim_count == 3, 3, # 3
    raw_victim_count  > 3, 4 # 4+
  ), 
  
  #Create a count variable of 1
  count = 1
  )



#Check the recodes
raw_offenses_weapon_victim_count %>% checkfunction(der_number_of_victims_firearm_cat, raw_victim_count)

#Output to share
raw_offenses_weapon_victim_count %>%
  select(incident_id, der_number_of_victims_firearm_cat, count) %>% 
  write_csv(gzfile(paste0(der_file_path,"/agg_number_of_victims_firearm_cat.csv.gz")), na="") 


#Clean up the environment - need to keep raw_weapon_offense_firearm 
rm(raw_offenses, raw_offenses_weapon,  raw_test, raw_weapon_offense, raw_offenses_weapon_victim_count)
invisible(gc())


#Using raw_weapon_offense_firearm need to keep unique incident_id and offense_id
raw_weapon_offense_firearm_inc <- raw_weapon_offense_firearm %>%
  count(incident_id, offense_id) 

#Check the dimension
log_dim(raw_weapon_offense_firearm_inc)
log_dim(raw_weapon_offense_firearm)

#Clean up the environment - need to keep raw_weapon_offense_firearm 
rm(raw_weapon_offense_firearm)
invisible(gc())

#Next need to process the incident level file

raw_incident <- fread(paste0(der_file_path, "cleaned_recoded_all_Offenses_recoded_incident.csv.gz")) %>%
  #Need to code the new offenses
  fire_arm_offense_recode()

#Check the recodes
# raw_incident %>% checkfunction(der_total_gun_violence, der_total_gun_violence_no_rob, crime_against, offense_code, offense_name)
# raw_incident %>% checkfunction(der_fatal_gun_violence, crime_against, offense_code, offense_name)
# raw_incident %>% checkfunction(der_nonfatal_gun_violence, der_nonfatal_gun_violence_no_rob, crime_against, offense_code, offense_name)
# raw_incident %>% checkfunction(der_nonfatal_gun_violence2, der_nonfatal_gun_violence2_no_rob, crime_against, offense_code, offense_name)


#Join the data by the common variables
raw_incident_weapon <- raw_incident %>%
  inner_join(raw_weapon_offense_firearm_inc %>% select(-n), by = c("incident_id", "offense_id"))

#Check the dimension
log_dim(raw_incident_weapon)
log_dim(raw_incident)
log_dim(raw_weapon_offense_firearm_inc)

#Need to make sure that raw_incident_weapon is unique at the "ori", "incident_id", "offense_id" level.  Note ori is included since we are using the block imputed dataset

raw_test <- raw_incident_weapon %>%
  count(ori, incident_id, offense_id) %>%
  filter(n > 1)

#Make sure that the row is zero
nrow(raw_test)

#Output to share
raw_incident_weapon %>% 
  write_csv(gzfile(paste0(der_file_path,"/cleaned_recoded_all_Firearm_Offenses_recoded_incident.csv.gz")), na="") 

