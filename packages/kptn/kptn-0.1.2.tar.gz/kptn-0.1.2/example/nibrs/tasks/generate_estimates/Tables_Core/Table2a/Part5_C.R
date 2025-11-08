#install.packages("RPostgres")
#install.packages("dbplyr")
library("rjson")
library(tidyverse)
#library(xlsx)
library(openxlsx)
library(DBI)
library(DT)
library(lubridate)
library(data.table)

read_csv <- partial(read_csv, guess_max = 1000000) #For now, read thru the 1st 1,000,000 rows to determine variable type
write.csv0 <- partial(write.csv, row.names = FALSE, na ="0")
write.csv <- partial(write.csv, row.names = FALSE, na ="")

#Read in the common functions to be used in R
source(here::here("tasks/logging.R"))
source(here::here("tasks/impute_items/0-Common_functions_for_imputation.R"))

#input/output directories for pipeline artifacts
DER_TABLE_NAME <- Sys.getenv("DER_TABLE_NAME")
outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")
inputPipelineDir <- Sys.getenv("INPUT_PIPELINE_DIR")
external_path <- Sys.getenv("EXTERNAL_FILE_PATH")

der_file_path = paste0(outputPipelineDir, "/indicator_table_extracts/") #output path for all the data extracts

if (! dir.exists(der_file_path)) {
  dir.create(der_file_path, recursive = TRUE)
}

final_path_in = paste0(inputPipelineDir, "/indicator_table_estimates/") #this is where the final estimates go
final_path = paste0(outputPipelineDir, "/indicator_table_estimates/") #this is where the final estimates go

if (! dir.exists(final_path)) {
  dir.create(final_path, recursive = TRUE)
}

#External files json
input_folder <- sprintf("%s", inputPipelineDir)
file_locs <- fromJSON(file = sprintf("%s/external_file_locations.json", input_folder))

#set-up year
CONST_YEAR <- Sys.getenv("DATA_YEAR")

#for the single run code we want to point it to the NATIONAL population information
DER_CURRENT_PERMUTATION_NUM <- 1
Sys.setenv("DER_CURRENT_PERMUTATION_NUM" = DER_CURRENT_PERMUTATION_NUM)

#source code for a lot of shared functions (needs to run after setting year & permutation or it will error)
source("../../POP_Total_code_assignment.R")

# read in the 2a part a functions. Some will be overwritten
source("util.R")


##########################Set the variables for table #######################
DER_MAXIMUM_ROW = 110
DER_MAXIMUM_COLUMN = 20


#############################################################################
#Create the final ORI dataset
raw_ori <- fread(paste0(final_path_in,"Table ", DER_TABLE_NAME, " ORI.csv.gz"))

#Get the list of variables
der_list_of_variables_variance <- colnames(raw_ori) %>%
  str_match(pattern="t_\\w+_\\d+_\\d+_\\d+") %>%
  as_tibble() %>%
  filter(!is.na(V1)) %>%
  pull()

#These are the total variables
print(der_list_of_variables_variance)

raw_total_list <- map(der_list_of_variables_variance, ~ {

  #.x <- der_list_of_variables_variance[[1]]
  invar <- .x %>% rlang:::parse_expr()

  der_variable_info <- .x %>%
    str_match(pattern=DER_TABLE_PATTERN_STRING) %>%
    as_tibble() %>%
    #Make sure the variable is a match to the pattern name
    filter(!is.na(V1)) %>%
    #Make the derived variables from variable name
    mutate(variable_name = V1,
           table = V2,
           section = as.numeric(V3),
           row = as.numeric(V4),
           column = as.numeric(V5)) %>%
    select(-V1,-V2,-V3,-V4,-V5)



  #Need to sum up the totals
  raw_data <- raw_ori %>%
    summarise(final_count = sum(weight*!!invar, na.rm = TRUE)) %>%
    bind_cols(der_variable_info)

  #Return the data
  return(raw_data)

})

#Bind the list
raw_total <- raw_total_list %>% bind_rows()

#Next need to calculate the percentage
raw_total_percent_list <- map(der_list_of_variables_variance, ~{

  #Declare the variable
  raw_denominator <- NA

  #Get the current variable
  #.x <- der_list_of_variables_variance[[1]]
  raw_variable <- .x


  #Get the information on the variable
  raw_variable_info <- raw_variable %>%
    str_match(pattern=DER_TABLE_PATTERN_STRING) %>%
    as_tibble() %>%
    #Make sure the variable is a match to the pattern name
    filter(!is.na(V1)) %>%
    #Make the derived variables from variable name
    mutate(variable_name = V1,
           table = V2,
           section = as.numeric(V3),
           row = as.numeric(V4),
           column = as.numeric(V5)) %>%
    select(-V1,-V2,-V3,-V4,-V5)


  #Calculate the standard error of percentages - Use the main dataset
  #Get the information about the variable
  raw_variable_column <- raw_variable_info %>%
    select(column) %>%
    as.numeric()

  #Get the row
  raw_variable_row <- raw_variable_info %>%
    select(row) %>%
    as.numeric()



##################################Edit code for each table on how to define the denominator #########################

#Offense count
#Offense rate (per 100k total pop)
if(raw_variable_row == 3){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(3:4), raw_variable_column)} #Weapon involved: No
else if(raw_variable_row == 4){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(3:4), raw_variable_column)} #Weapon involved: Yes
else if(raw_variable_row == 5){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(4), raw_variable_column)} #Weapon involved: Personal weapons
else if(raw_variable_row == 6){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(4), raw_variable_column)} #Weapon involved: Firearms
else if(raw_variable_row == 7){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(4), raw_variable_column)} #Weapon involved: Knives and other cutting instruments
else if(raw_variable_row == 8){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(4), raw_variable_column)} #Weapon involved: Blunt instruments
else if(raw_variable_row == 9){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(4), raw_variable_column)} #Weapon involved: Other non-personal weapons
else if(raw_variable_row == 10){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(4), raw_variable_column)} #Weapon involved: Unknown
else if(raw_variable_row == 11){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(11:12), raw_variable_column)} #Injury: No
else if(raw_variable_row == 12){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(11:12), raw_variable_column)} #Injury: Yes
else if(raw_variable_row == 13){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(13:14), raw_variable_column)} #Multiple victims: 1 victim
else if(raw_variable_row == 14){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(13:14), raw_variable_column)} #Multiple victims: 2+ victims
else if(raw_variable_row == 15){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(15:17), raw_variable_column)} #Multiple offenders: 1 offender
else if(raw_variable_row == 16){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(15:17), raw_variable_column)} #Multiple offenders: 2+ offenders
else if(raw_variable_row == 17){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(15:17), raw_variable_column)} #Multiple offenders: Unknown offenders
else if(raw_variable_row == 18){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(1), raw_variable_column)} #Victim-offender relationship: Intimate partner
else if(raw_variable_row == 19){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(1), raw_variable_column)} #Victim-offender relationship: Other family
else if(raw_variable_row == 20){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(1), raw_variable_column)} #Victim-offender relationship: Outside family but known to victim
else if(raw_variable_row == 21){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(1), raw_variable_column)} #Victim-offender relationship: Stranger
else if(raw_variable_row == 22){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(1), raw_variable_column)} #Victim-offender relationship: Victim was Offender
else if(raw_variable_row == 23){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(1), raw_variable_column)} #Victim-offender relationship: Unknown relationship
else if(raw_variable_row == 24){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(1), raw_variable_column)} #Location type: Residence/hotel
else if(raw_variable_row == 25){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(1), raw_variable_column)} #Location type: Transportation hub/outdoor public locations
else if(raw_variable_row == 26){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(1), raw_variable_column)} #Location type: Schools, daycares, and universities
else if(raw_variable_row == 27){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(1), raw_variable_column)} #Location type: Retail/financial/other commercial establishment
else if(raw_variable_row == 28){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(1), raw_variable_column)} #Location type: Restaurant/bar/sports or entertainment venue
else if(raw_variable_row == 29){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(1), raw_variable_column)} #Location type: Religious buildings
else if(raw_variable_row == 30){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(1), raw_variable_column)} #Location type: Government/public buildings
else if(raw_variable_row == 31){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(1), raw_variable_column)} #Location type: Jail/prison
else if(raw_variable_row == 32){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(1), raw_variable_column)} #Location type: Shelter-mission/homeless
else if(raw_variable_row == 33){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(1), raw_variable_column)} #Location type: Other/unknown location
else if(raw_variable_row == 34){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(34:40), raw_variable_column)} #Time of day- Incident time: Midnight-4am
else if(raw_variable_row == 35){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(34:40), raw_variable_column)} #Time of day- Incident time: 4-8am
else if(raw_variable_row == 36){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(34:40), raw_variable_column)} #Time of day- Incident time: 8am-noon
else if(raw_variable_row == 37){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(34:40), raw_variable_column)} #Time of day- Incident time: Noon-4pm
else if(raw_variable_row == 38){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(34:40), raw_variable_column)} #Time of day- Incident time: 4-8pm
else if(raw_variable_row == 39){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(34:40), raw_variable_column)} #Time of day- Incident time: 8pm-midnight
else if(raw_variable_row == 40){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(34:40), raw_variable_column)} #Time of day- Incident time: Unknown
else if(raw_variable_row == 41){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(41:47), raw_variable_column)} #Time of day- Report time: Midnight-4am
else if(raw_variable_row == 42){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(41:47), raw_variable_column)} #Time of day- Report time: 4-8am
else if(raw_variable_row == 43){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(41:47), raw_variable_column)} #Time of day- Report time: 8am-noon
else if(raw_variable_row == 44){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(41:47), raw_variable_column)} #Time of day- Report time: Noon-4pm
else if(raw_variable_row == 45){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(41:47), raw_variable_column)} #Time of day- Report time: 4-8pm
else if(raw_variable_row == 46){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(41:47), raw_variable_column)} #Time of day- Report time: 8pm-midnight
else if(raw_variable_row == 47){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(41:47), raw_variable_column)} #Time of day- Report time: Unknown
else if(raw_variable_row == 48){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(48:52), raw_variable_column)} #Population group: Cities and counties 100,000 or over
else if(raw_variable_row == 49){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(48:52), raw_variable_column)} #Population group: Cities and counties 25,000-99,999
else if(raw_variable_row == 50){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(48:52), raw_variable_column)} #Population group: Cities and counties 10,000-24,999
else if(raw_variable_row == 51){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(48:52), raw_variable_column)} #Population group: Cities and counties under 10,000
else if(raw_variable_row == 52){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(48:52), raw_variable_column)} #Population group: State police
#Population group: Possessions and Canal Zone
else if(raw_variable_row == 54){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(54:59), raw_variable_column)} #Agency indicator: City
else if(raw_variable_row == 55){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(54:59), raw_variable_column)} #Agency indicator: County
else if(raw_variable_row == 56){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(54:59), raw_variable_column)} #Agency indicator: University or college
else if(raw_variable_row == 57){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(54:59), raw_variable_column)} #Agency indicator: State police
else if(raw_variable_row == 58){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(54:59), raw_variable_column)} #Agency indicator: Other state agencies
else if(raw_variable_row == 59){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(54:59), raw_variable_column)} #Agency indicator: Tribal agencies
#Agency indicator: Federal agencies
else if(raw_variable_row == 61){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(61:62), raw_variable_column)} #Clearance: Not cleared through arrest
else if(raw_variable_row == 62){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(61:62), raw_variable_column)} #Clearance: Cleared through arrest
else if(raw_variable_row == 63){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(63:66), raw_variable_column)} #MSA: MSA Counties
else if(raw_variable_row == 64){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(63:66), raw_variable_column)} #MSA: Outside MSA
else if(raw_variable_row == 65){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(63:66), raw_variable_column)} #MSA: Non-MSA Counties
else if(raw_variable_row == 66){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(63:66), raw_variable_column)} #MSA: Missing

else if(raw_variable_row == 67){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(1), raw_variable_column)} #Location type 2: Residence/hotel
else if(raw_variable_row == 68){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(1), raw_variable_column)} #Location type 2: Transportation hub/outdoor public locations
else if(raw_variable_row == 69){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(1), raw_variable_column)} #Location type 2: Schools, daycares, and universities
else if(raw_variable_row == 70){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(1), raw_variable_column)} #Location type 2: Retail/financial/other commercial establishment
else if(raw_variable_row == 71){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(1), raw_variable_column)} #Location type 2: Restaurant/bar/sports or entertainment venue
else if(raw_variable_row == 72){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(1), raw_variable_column)} #Location type 2: Religious buildings
else if(raw_variable_row == 73){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(1), raw_variable_column)} #Location type 2: Government/public buildings
else if(raw_variable_row == 74){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(1), raw_variable_column)} #Location type 2: Jail/prison
else if(raw_variable_row == 75){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(1), raw_variable_column)} #Location type 2: Shelter-mission/homeless
else if(raw_variable_row == 76){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(1), raw_variable_column)} #Location type 2: Drug Store/Doctor’s Office/Hospital
else if(raw_variable_row == 77){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(1), raw_variable_column)} #Location type 2: Other/unknown location
else if(raw_variable_row == 78){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(1), raw_variable_column)} #Victim-offender relationship 2: Intimate partner plus Family
else if(raw_variable_row == 79){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(1), raw_variable_column)} #Victim-offender relationship 2: Outside family but known to victim
else if(raw_variable_row == 80){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(1), raw_variable_column)} #Victim-offender relationship 2: Stranger
else if(raw_variable_row == 81){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(1), raw_variable_column)} #Victim-offender relationship 2: Victim was Offender
else if(raw_variable_row == 82){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(1), raw_variable_column)} #Victim-offender relationship 2: Unknown relationship
else if(raw_variable_row == 83){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(1), raw_variable_column)} #Location cyberspace: Cyberspace
  
else if(raw_variable_row == 84){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(84:101), raw_variable_column)} #Weapon involved hierarchy: Handgun
else if(raw_variable_row == 85){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(84:101), raw_variable_column)} #Weapon involved hierarchy: Firearm
else if(raw_variable_row == 86){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(84:101), raw_variable_column)} #Weapon involved hierarchy: Rifle
else if(raw_variable_row == 87){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(84:101), raw_variable_column)} #Weapon involved hierarchy: Shotgun
else if(raw_variable_row == 88){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(84:101), raw_variable_column)} #Weapon involved hierarchy: Other Firearm
else if(raw_variable_row == 89){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(84:101), raw_variable_column)} #Weapon involved hierarchy: Knife/Cutting Instrument
else if(raw_variable_row == 90){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(84:101), raw_variable_column)} #Weapon involved hierarchy: Blunt Object
else if(raw_variable_row == 91){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(84:101), raw_variable_column)} #Weapon involved hierarchy: Motor Vehicle
else if(raw_variable_row == 92){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(84:101), raw_variable_column)} #Weapon involved hierarchy: Personal Weapons (hands, feet, teeth, etc.)
else if(raw_variable_row == 93){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(84:101), raw_variable_column)} #Weapon involved hierarchy: Asphyxiation
else if(raw_variable_row == 94){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(84:101), raw_variable_column)} #Weapon involved hierarchy: Drugs/Narcotics/Sleeping Pills
else if(raw_variable_row == 95){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(84:101), raw_variable_column)} #Weapon involved hierarchy: Poison (include gas)
else if(raw_variable_row == 96){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(84:101), raw_variable_column)} #Weapon involved hierarchy: Explosives
else if(raw_variable_row == 97){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(84:101), raw_variable_column)} #Weapon involved hierarchy: Fire/Incendiary Device
else if(raw_variable_row == 98){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(84:101), raw_variable_column)} #Weapon involved hierarchy: Other
else if(raw_variable_row == 99){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(84:101), raw_variable_column)} #Weapon involved hierarchy: No Weapon
else if(raw_variable_row == 100){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(84:101), raw_variable_column)} #Weapon involved hierarchy: Unknown
else if(raw_variable_row == 101){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(84:101), raw_variable_column)} #Weapon involved hierarchy: Not Applicable
else if(raw_variable_row == 102){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(1), raw_variable_column)} #Location type 3: Residence
else if(raw_variable_row == 103){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(1), raw_variable_column)} #Location type 3: Not residence
else if(raw_variable_row == 104){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(104:105), raw_variable_column)} #Clearance 2: Cleared incident
else if(raw_variable_row == 105){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(104:105), raw_variable_column)} #Clearance 2: Not cleared incident
else if(raw_variable_row == 106){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(106:110), raw_variable_column)} #Weapon involved hierarchy collapse: Firearm
else if(raw_variable_row == 107){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(106:110), raw_variable_column)} #Weapon involved hierarchy collapse: Other Weapon
else if(raw_variable_row == 108){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(106:110), raw_variable_column)} #Weapon involved hierarchy collapse: No Weapon
else if(raw_variable_row == 109){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(106:110), raw_variable_column)} #Weapon involved hierarchy collapse: Unknown
else if(raw_variable_row == 110){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(106:110), raw_variable_column)} #Weapon involved hierarchy collapse: Not Applicable


  #If raw_denominator is NULL then exit
  if(!exists("raw_denominator")){
    return(NULL)
  }

  #Get the numerator counts
  raw_denominator_num <- raw_total %>%
    filter(variable_name %in% raw_denominator) %>%
    summarise(raw_denominator_num = sum(final_count, na.rm=TRUE)) %>%
    pull() %>%
    as.numeric()

  #Create the percentage column
  raw_total2 <- raw_total %>%
    #Filter to correct cell
    filter(row == raw_variable_row) %>%
    filter(column == raw_variable_column) %>%
    #Calculate the percentage
    mutate(percent = (final_count / raw_denominator_num) *100 )

  #Return the object
  return(raw_total2)

})

#Create the percentage output
raw_total_percent <- raw_total_percent_list %>%
  bind_rows()

#Next need to adjust for the rate rows
raw_total_percent_rate <- raw_total_percent %>%
  mutate(final_count = case_when(
    #The rate row
    row == 2 ~ (final_count / POP_TOTAL) * 100000,
    TRUE ~ final_count)) %>%
    #Make NAs on the percentage cells
  mutate(percent = case_when(
    row %in% c(1,2) ~ NA_real_,
    TRUE ~ percent))

#Create the filler dataset
raw_data0 <- c(1:DER_MAXIMUM_ROW) %>% as_tibble() %>%
  rename(row = value)
raw_data0 <- assign_section(raw_data0) %>%
  mutate(table = DER_TABLE_NAME)

#Add on the column and stack them
data0_list <- map(1:DER_MAXIMUM_COLUMN, ~ {

  returndata <- raw_data0 %>%
                  mutate(column = .x)

  return(returndata)

})

#Bind the row
data0 <- data0_list %>% bind_rows()

#Using dataset raw_total_percent_rate
# raw_final_data <- data0 %>%
#   left_join(raw_total_percent_rate, by=c("section", "row"))

#Need to transpose the dataset
raw_final_data_count <- data0 %>%
  left_join(raw_total_percent_rate, by=c("table", "section", "row", "column")) %>%
  mutate(newcolumn = paste0("final_count_", column)) %>%
  select(table, section, row, newcolumn, final_count) %>%
  spread(newcolumn, final_count)

raw_final_data_percent <- data0 %>%
  left_join(raw_total_percent_rate, by=c("table", "section", "row", "column")) %>%
  mutate(newcolumn = paste0("percent_", column)) %>%
  select(table, section, row, newcolumn, percent) %>%
  spread(newcolumn, percent)

#Need to combine the files
final_data_list <- list(raw_final_data_count, raw_final_data_percent)
final_data <- reduce(final_data_list, left_join, by=c("table", "section","row") )

#Get list of variables and make NAs to 0
listofvars_count <- final_data %>% select(starts_with("final_count")) %>% colnames()
print(listofvars_count)

listofvars_percentage <- final_data %>% select(starts_with("percent")) %>% colnames()
print(listofvars_percentage)

final_data2 <- NA_to_0_count(data=final_data, list=listofvars_count)
final_data3 <- NA_to_0_percent(data=final_data2, list=listofvars_percentage, keepNA=1)

#Assign dataset for printing
datasetforoutput <- final_data3 %>%
  arrange(section, row)


#Get the number of section
output_section <- datasetforoutput %>%
  summarise(num_section = max(section)) %>%
  as.numeric()

print(output_section)

#Get the number of columns
output_column<- datasetforoutput %>%
  head(1) %>%
  select(starts_with("final_count")) %>%
  colnames() %>%
  as_tibble()


output_column <-  str_match(output_column$value, "final_count_(\\d+)") %>%
    .[,c(2)] %>% #Get the digit
    as.numeric() %>% #Change to numeric
    max() #Get the max

print(output_column)

#Create string of variables to output
outputvarsorder <- NULL

#Create the list of variables to output in order
output_list_vars <- vector("list", 2*output_column)
list_counter = 1

#Loop through and create the variable order
for(i in 1:output_column){


  #Get the current column number
  output_list_vars[[list_counter]] <- paste0("final_count_", i)
  list_counter = list_counter + 1

  output_list_vars[[list_counter]] <- paste0("percent_", i)
  list_counter = list_counter + 1



}

#Save the variable list as a symbol
invarlist <- output_list_vars %>% unlist()  %>% rlang:::parse_exprs()

#Check the order
print(invarlist)

#See the printed dataset
datatable( datasetforoutput %>% select(!!!invarlist) )

#Create the start rows for each section
start_row = c(
  2, 5, 14, 17, 20, 24, 31, 42, 50, 58, 65, 73, 76, 81, 93, 99, 101, 120, 123, 126)


# Specify the filename of existing workbook(Do not have file open)
file <- paste0("../TableShells/", "Indicator_Table_Shells.xlsx")

# Load the existing workbook
wb <- loadWorkbook(file = file)
table_sheet = "Table2a-Person Offenses"

# Remove sheets for other tables
for(s in getSheetNames(file)){
  if(s != table_sheet){
    removeWorksheet(wb,s)
  }
}
#Create loop to output to Excel Workbook

for(i in 1:output_section){

  writeData(wb,
            sheet = table_sheet,
            x = datasetforoutput %>%
              filter(section == i) %>%
			        arrange(section, row) %>%
              select(!!!invarlist) ,
            startCol = "2",
            startRow = start_row[[i]],
            colNames = FALSE)



}

fileout <- paste0(final_path, "Indicator_Table_2a.xlsx")

# Save the workbook
saveWorkbook(wb, fileout, overwrite = TRUE)