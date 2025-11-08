#install.packages("RPostgres")
#install.packages("dbplyr")
library("rjson")
library(tidyverse)
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

der_file_path = paste0(inputPipelineDir, "/indicator_table_extracts/") #output path for all the data extracts

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


#Read in the main datasets to be used for the table
main <- fread(
    file = paste0(der_file_path, "cleaned_recoded_all_Offenses_recoded_incident.csv.gz"),
    select = c(
        "ori",
        "weight",
        "incident_id",
        "offense_id",
        "der_robbery",
        "der_car_jacking"
    )
)

agg_weapon_no_yes_inc_offenses <- fread(paste0(der_file_path, "agg_weapon_no_yes_inc_offenses.csv.gz"))

#Deduplicate
agg_weapon_no_yes_inc_offenses <- agg_to_1(agg_weapon_no_yes_inc_offenses)


agg_weapon_yes_cat_inc_offenses <- fread(paste0(der_file_path, "agg_weapon_yes_cat_inc_offenses.csv.gz"))
#agg_injury_no_yes_victim  			<- fread(paste0(der_file_path, "agg_injury_no_yes_victim.csv.gz"))
#Deduplicate
#agg_injury_no_yes_victim <- agg_to_1(agg_injury_no_yes_victim)

#We need to use the incident version of injury
agg_injury_no_yes <- fread(paste0(der_file_path, "agg_injury_no_yes.csv.gz"))

#Deduplicate and keep the Yes Injury incidents if there are both injuries and non-injuries
agg_injury_no_yes <- agg_to_1(agg_injury_no_yes) %>%
    keep_to_yes(yesstring="der_injury_no_yes == 2")


agg_victim_count_1_2_plus <- fread(paste0(der_file_path, "agg_victim_count_1_2_plus.csv.gz"))
agg_offender_count_1_2_plus <- fread(paste0(der_file_path, "agg_offender_count_1_2_plus.csv.gz"))
#agg_relationship_cat_victim 		<- fread(paste0(der_file_path, "agg_relationship_cat_victim_imp.csv.gz"))
agg_location_cat_1_10_inc_offenses  <- fread(paste0(der_file_path, "agg_location_cat_1_10_inc_offenses.csv.gz"))
agg_time_of_day_cat_incident <- fread(paste0(der_file_path, "agg_time_of_day_cat_incident.csv.gz"))
agg_time_of_day_cat_report <- fread(paste0(der_file_path, "agg_time_of_day_cat_report.csv.gz"))
ori_population_group_cat <- fread(paste0(der_file_path, "ori_population_group_cat.csv.gz"))
ori_agency_type_cat_1_7  <- fread(paste0(der_file_path, "ori_agency_type_cat_1_7.csv.gz"))
agg_clearance_cat_1_2 <- fread(paste0(der_file_path, "agg_clearance_cat_1_2.csv.gz"))
ori_msa_cat   	          <- fread(paste0(der_file_path, "ori_msa_cat.csv.gz"))
agg_location_cat_1_11_inc_offenses   	      <- fread(paste0(der_file_path, "agg_location_cat_1_11_inc_offenses.csv.gz"))
#agg_relationship_cat2_victim   	  <- fread(paste0(der_file_path, "agg_relationship_cat2_victim.csv.gz"))
agg_location_cyberspace_inc_offenses  <- fread(paste0(der_file_path, "agg_location_cyberspace_inc_offenses.csv.gz"))

#Weapon involved hierarchy
# 1:    Handgun
# 2:    Firearm
# 3:    Rifle
# 4:    Shotgun
# 5:    Other Firearm
# 6:    Knife/Cutting Instrument
# 7:    Blunt Object
# 8:    Motor Vehicle
# 9:    Personal Weapons (hands, feet, teeth, etc.)
# 10:    Asphyxiation
# 11:    Drugs/Narcotics/Sleeping Pills
# 12:    Poison (include gas)
# 13:    Explosives
# 14:    Fire/Incendiary Device
# 15:    Other
# 16:    No Weapon
# 17:    Unknown
# 18:    Not Applicable

#Note this is aggregated at the incident, victim, and offense level
#Only one weapon per incident, victim, and offense is chosen
agg_raw_weapon_hierarchy_recode_inc_offenses  	  <- fread(paste0(der_file_path, "agg_raw_weapon_hierarchy_recode_inc_offenses.csv.gz"))


agg_location_residence_inc_offenses   	  		  <- fread(paste0(der_file_path, "agg_location_residence_inc_offenses.csv.gz"))

agg_cleared_cat_1_2                         <- fread(paste0(der_file_path, "agg_cleared_cat_1_2.csv.gz"))
agg_raw_weapon_hierarchy_recode_col_inc_offenses <- fread(paste0(der_file_path, "agg_raw_weapon_hierarchy_recode_col_inc_offenses.csv.gz"))

#Declare the final section and row number for the table
assign_row <- function(data){

  returndata <- data %>% mutate(

  row = case_when(
    section == 1 ~ 1,
    section == 2 ~ 2,
    der_weapon_no_yes %in% c(1:2) ~ der_weapon_no_yes + 2,
    der_weapon_yes_cat %in% c(1:6) ~ der_weapon_yes_cat + 4,
    der_injury_no_yes %in% c(1:2) ~ der_injury_no_yes + 10,
    der_victim_count %in% c(1:2) ~ der_victim_count + 12,
    der_offender_count %in% c(1:3) ~ der_offender_count + 14,
    #der_relationship %in% c(1:6) ~ der_relationship + 17,
    der_location_1_10 %in% c(1:10) ~ der_location_1_10 + 23,
    der_time_of_day_incident %in% c(1:7) ~ der_time_of_day_incident + 33,
    der_time_of_day_report %in% c(1:7) ~ der_time_of_day_report + 40,
    der_population_group %in% c(1:6) ~ der_population_group + 47,
    der_agency_type_1_7 %in% c(1:7) ~ der_agency_type_1_7 + 53,
    der_clearance_cat_1_2 %in% c(1:2) ~ der_clearance_cat_1_2 + 60,
    der_msa %in% c(1:4) ~ der_msa + 62,
    der_location_1_11 %in% c(1:11) ~ der_location_1_11 + 66,
    #Don't use relationship from incident
    der_location_cyberspace %in% c(1) ~ 83,
	
	der_raw_weapon_hierarchy_recode %in% c(1:18) ~  der_raw_weapon_hierarchy_recode + 83,
	der_location_residence %in% c(1:2) ~ der_location_residence + 101, 
	der_cleared_cat_1_2 %in% c(1:2) ~ der_cleared_cat_1_2 + 103,
	der_raw_weapon_hierarchy_recode_col %in% c(1:5) ~ der_raw_weapon_hierarchy_recode_col + 105
	
	
    )

  )

  return(returndata)
}

#Need the weight variable
weight_dataset <- main %>%
  select(ori, weight) %>%
  #Deduplicate and keep the unique weight for each ORI
  group_by(ori) %>%
  mutate(raw_first = row_number() == 1) %>%
  ungroup() %>%
  filter(raw_first == TRUE) %>%
  select(-raw_first)

##########################Set the variables for table #######################
DER_MAXIMUM_ROW = 110
#############################################################################



#This function will calculate the counts and percentage one column at a time

generate_est <- function(maindata, subsetvareq1, column_number){

  #Declare the variable for the column subset
  filtervarsting <- subsetvareq1

  #Make the var into a symbol
  infiltervar <- filtervarsting %>% rlang:::parse_expr()

  #Create the incidicator filter
  infilter <- paste0(filtervarsting," == 1") %>% rlang:::parse_expr()

  #Create the column variable
  columnnum <- column_number
  incolumn_count <- paste0("final_count_", columnnum) %>% rlang:::parse_expr()
  incolumn_percentage <- paste0("percent_", columnnum) %>% rlang:::parse_expr()

  #Filter the dataset
  main_filter <- maindata[eval(infilter), c("ori", "weight", "incident_id", "offense_id", filtervarsting), with = FALSE]

  log_debug("After filtering and deduping main")
  log_dim(main_filter)
  log_debug(system("free -mh", intern = FALSE))

  #Incident count
  s1 <- vector("list", 2)
  #For Table
  s1[[1]] <- main_filter %>%
    mutate(weighted_count = weight *!!infiltervar) %>%
    summarise(final_count = sum(weighted_count)) %>%
    mutate(section = 1)
  #For ORI level - Need unweighted counts
  s1[[2]] <- main_filter %>%
    group_by(ori) %>%
    summarise(final_count = sum(!!infiltervar)) %>%
    ungroup() %>%
    mutate(section = 1)

  #Total Denominator
  der_total_denom <- s1[[1]] %>% select(final_count) %>% as.double()

  #Incident rate
  s2 <- vector("list", 2)
  #For Table
  s2[[1]] <- s1[[1]] %>%
    mutate(final_count = (final_count / POP_TOTAL) * 100000,
           population_estimate = POP_TOTAL
           ) %>%
    mutate(section = 2)
  #For ORI level - Report totals - Need unweighted counts
  s2[[2]] <- main_filter %>%
    group_by(ori) %>%
    summarise(final_count = sum(!!infiltervar)) %>%
    ungroup() %>%
    mutate(section = 2)

  #Weapon involved
  s3 <- agg_percent(leftdata = main_filter, rightdata = agg_weapon_no_yes_inc_offenses, var=der_weapon_no_yes, section=3, mergeby=c( "incident_id", "offense_id"))

  der_weapon_yes_denom <- s3[[1]] %>%
    filter(der_weapon_no_yes == 2) %>% #Yes response
    select(final_count) %>%
    as.double()

  #Weapon involved Categories
  s4 <- agg_percent_CAA(leftdata = main_filter, rightdata = agg_weapon_yes_cat_inc_offenses, var=der_weapon_yes_cat, section=4, mergeby=c( "incident_id", "offense_id"), denom=der_weapon_yes_denom )

  #Injury - Edited to use Incident version
  s5 <- agg_percent(leftdata = main_filter, rightdata = agg_injury_no_yes, var=der_injury_no_yes, section=5, mergeby=c( "incident_id"))

  #Multiple victims
  s6 <- agg_percent(leftdata = main_filter, rightdata = agg_victim_count_1_2_plus, var=der_victim_count, section=6, mergeby=c( "incident_id"))

  #Multiple offenders
  s7 <- agg_percent(leftdata = main_filter, rightdata = agg_offender_count_1_2_plus, var=der_offender_count, section=7, mergeby=c( "incident_id"))

  #Victim-offender relationship - Will use the counts from the Person file
  #s8 <- agg_percent_CAA(leftdata = main_filter, rightdata = agg_relationship_cat_victim, var=der_relationship, section=8, mergeby=c( "incident_id", "victim_id"), denom=der_total_denom)

  #Location type
  s9 <- agg_percent_CAA(leftdata = main_filter, rightdata = agg_location_cat_1_10_inc_offenses, var=der_location_1_10, section=9, mergeby=c( "incident_id", "offense_id"), denom=der_total_denom)

  #Time of day - Incident
  s10 <- agg_percent(leftdata = main_filter, rightdata = agg_time_of_day_cat_incident, var=der_time_of_day_incident, section=10, mergeby=c( "incident_id"))

  #Time of day - Report
  s11 <- agg_percent(leftdata = main_filter, rightdata = agg_time_of_day_cat_report, var=der_time_of_day_report, section=11, mergeby=c( "incident_id"))

  #Population group
  s12 <- agg_percent(leftdata = main_filter, rightdata = ori_population_group_cat, var=der_population_group, section=12, mergeby=c("ori"))
  
  #Agency indicator
  s13 <- agg_percent(leftdata = main_filter, rightdata = ori_agency_type_cat_1_7, var=der_agency_type_1_7, section=13, mergeby=c("ori"))
  
  #Clearance 1 -2
  s14 <- agg_percent(leftdata = main_filter, rightdata = agg_clearance_cat_1_2, var=der_clearance_cat_1_2, section=14, mergeby=c( "incident_id"))
  
  #MSA indicator
  s15 <- agg_percent(leftdata = main_filter, rightdata = ori_msa_cat, var=der_msa, section=15, mergeby=c("ori"))
  
  #Location type
  s16 <- agg_percent_CAA(leftdata = main_filter, rightdata = agg_location_cat_1_11_inc_offenses, var=der_location_1_11, section=16, mergeby=c( "incident_id", "offense_id"), denom=der_total_denom)

  #Victim-offender relationship - Will use the counts from the Person file

  #Location type
  s17 <- agg_percent_CAA(leftdata = main_filter, rightdata = agg_location_cyberspace_inc_offenses, var=der_location_cyberspace, section=17, mergeby=c( "incident_id", "offense_id"), denom=der_total_denom)

  #Weapon involved hierarchy
  s18 <- agg_percent(leftdata = main_filter, rightdata = agg_raw_weapon_hierarchy_recode_inc_offenses, var=der_raw_weapon_hierarchy_recode, section=18, 
                     mergeby=c( "incident_id", "offense_id"))	
  
  #Location type
  s19 <- agg_percent_CAA(leftdata = main_filter, rightdata = agg_location_residence_inc_offenses, var=der_location_residence, section=19, mergeby=c( "incident_id", "offense_id"), denom=der_total_denom)
  
  #Clearance 2:  1 -2
  s20 <- agg_percent(leftdata = main_filter, rightdata = agg_cleared_cat_1_2, var=der_cleared_cat_1_2, section=20, mergeby=c( "incident_id"))

  #Weapon involved hierarchy collapse
  s21 <- agg_percent(leftdata = main_filter, rightdata = agg_raw_weapon_hierarchy_recode_col_inc_offenses, var=der_raw_weapon_hierarchy_recode_col, section=21, mergeby=c( "incident_id", "offense_id"))  
  

  #Need to get objects of interest
  raw_s_list <- ls(pattern="s\\d+")

  maximum_s_object <- length(raw_s_list)

  #Loop thru to separate the original table information and the ORI level totals
  raw_list_table <- vector("list", maximum_s_object)
  raw_list_ori <- vector("list", maximum_s_object)

  for(i in 1:maximum_s_object){

    #get the object
    raw_object <- get(raw_s_list[[i]])

    #Extract the information to list
    raw_list_table[[i]] <- raw_object[[1]]
    raw_list_ori[[i]] <- raw_object[[2]]

    #Clear the object
    rm(raw_object)
    invisible(gc())


  }

  #Get the datsets together
  #merge_list <- ls(pattern="s\\d+")
  #merge_list_data <- mget(merge_list)

  #Stack the datasets, fix the final_count variable, and rename the variables
  final_data <- reduce(raw_list_table, bind_rows)
  final_data2 <- final_data %>%
    mutate(
      final_count = as.double(final_count)) %>%
    mutate(!!incolumn_count := final_count,
           !!incolumn_percentage := percent)

  #Create the row and reassign the section variable
  final_data3 <- assign_row(final_data2)
  final_data4 <- assign_section(final_data3)

  #Keep variables and sort the dataset
  final_data5 <- final_data4 %>%
    select(section, row, !!incolumn_count, !!incolumn_percentage) %>%
    arrange(section, row)

  #Output data in reporting database

  #Create the filler dataset
  raw_filler <- c(1:DER_MAXIMUM_ROW) %>% as_tibble() %>%
    rename(row = value)
  raw_filler <- assign_section(raw_filler)

  final_reporting_database <-
    raw_filler %>%
    left_join(final_data4, by=c("section","row") ) %>%
    mutate(column = column_number) %>%
    assign_labels() %>%
    arrange(section, row, column) %>%
    #Check to make sure that the NA are in the proper section
    mutate(final_count = case_when(is.na(final_count) ~ 0,
                                   TRUE ~ final_count),
           percent = case_when(is.na(percent) ~ 0,
                                   TRUE ~ percent),

           #UPDATE this for each table:  Make the estimates of the database
           count    = case_when(!row %in% c(2) ~ final_count,
                                      TRUE ~ DER_NA_CODE),
           percentage  = case_when(!row %in% c(1,2) ~ percent,
                                      TRUE ~ DER_NA_CODE),
           rate     = case_when(row %in% c(2) ~ final_count,
                                      TRUE ~ DER_NA_CODE),
           population_estimate     = case_when(row %in% c(2) ~ population_estimate,
                                      TRUE ~ DER_NA_CODE)
           ) %>%
    select(full_table, table, section, row, estimate_domain, column, indicator_name,  count, percentage, rate, population_estimate)

  #Create ORI dataset for variance estimation
  raw_list_ori2 <- raw_list_ori %>%
    bind_rows() %>%
    mutate(column = column_number) %>%
    assign_row() %>%
    assign_section() %>%
    assign_labels() %>%
    arrange(ori, table, section, row, column) %>%
    select(ori, table, section, row, column, final_count) %>%
    mutate(new_key = paste0("t_", table,"_", section, "_", row, "_", column) )

  #Get list of variables in order
  raw_ori_vars <-raw_list_ori2 %>%
    select(table, section, row, column, new_key) %>%
    #Dedepulicate
    group_by(table, section, row, column) %>%
    mutate(raw_first = row_number() == 1) %>%
    ungroup() %>%
    filter(raw_first == TRUE) %>%
    #Sort
    arrange(table, section, row, column) %>%
    select(new_key) %>%
    pull() %>%
    rlang:::enquos()


  #Transpose the dataset
  raw_list_ori3 <- raw_list_ori2 %>%
    select(ori, new_key, final_count) %>%
    spread(new_key, final_count) %>%
    select(ori, !!!raw_ori_vars, everything() )

  #Create list object to return
    return_object <- vector("list", 3)

    return_object[[1]] <- final_data5
    return_object[[2]] <- final_reporting_database
    return_object[[3]] <- raw_list_ori3

  return(return_object)

}

#Call the functions for each column
data15  <- generate_est(maindata=main, subsetvareq1 = "der_robbery", column_number=15)
data18  <- generate_est(maindata=main, subsetvareq1 = "der_car_jacking", column_number=18)

#Have data15 which is the single offense count version.
#Next will to read in the 2a Person file to update the robbery estimates
raw_person_file_ori <- fread(paste0(final_path_in, "Table ", DER_TABLE_NAME, " ORI_PERSON.csv.gz"))

#Next need to drop the Robbery estimates except for the victim offender relationship section
#Also drop car jacking
raw_drop_columns <-colnames(raw_person_file_ori) %>%
  #Keep the matches to column 15 = Robbery or 18 = Car Jacking
  str_match(pattern=paste0("t_", DER_TABLE_NAME, "_(\\d+)_(\\d+)_(15|18)")) %>%
  as_tibble() %>%
  #Drop the non-matches
  filter(!is.na(V1)) %>%
  #Set the names
  set_names("variable", "section", "row", "column") %>%
  #Need to drop all rows but the victim offender relationship
  filter(!row %in% c(18:23, 78:82)) %>%
  mutate(dropvars = paste0("-", variable)) %>%
  select(dropvars) %>%
  pull() %>%
  rlang:::parse_exprs()


#See the columns to be drop
print(raw_drop_columns)

#Drop the columns from the ORI level file
raw_person_file_ori2 <- raw_person_file_ori %>%
  select(!!!raw_drop_columns)

dim(raw_person_file_ori)
length(raw_drop_columns)
dim(raw_person_file_ori2)

#Next need to use the data15[[3]] ORI file to add on variables to raw_person_file_ori2
glimpse(data15[[3]])

raw_person_file_ori3_0 <- raw_person_file_ori2 %>%
  left_join(data15[[3]], by=c("ori"))

glimpse(data18[[3]])

raw_person_file_ori3 <- raw_person_file_ori3_0 %>%
  left_join(data18[[3]], by=c("ori"))


dim(raw_person_file_ori)
dim(raw_person_file_ori2)
dim(raw_person_file_ori3)


#Using dataset raw_person_file_ori3 - Need to fix the indicator Violent Crime
#Need to keep the Violent Crime indicators - column 17
raw_violent_crime_vars <- colnames(raw_person_file_ori3) %>%
  str_match(pattern=paste0("t_", DER_TABLE_NAME, "_\\d+_\\d+_17")) %>%
  as_tibble() %>%
  filter(!is.na(V1)) %>%
  pull() %>%
  rlang:::parse_exprs()

#Need to keep the Robbery indicators - column 15
raw_robbery_vars <- colnames(raw_person_file_ori3) %>%
  str_match(pattern=paste0("t_", DER_TABLE_NAME, "_\\d+_\\d+_15")) %>%
  as_tibble() %>%
  filter(!is.na(V1)) %>%
  pull() %>%
  rlang:::parse_exprs()

print(raw_violent_crime_vars)
print(raw_robbery_vars)

#Select the variables
raw_violent_crime_data  <- raw_person_file_ori3 %>% select(ori, !!!raw_violent_crime_vars)
raw_robbery_data        <- raw_person_file_ori3 %>% select(ori, !!!raw_robbery_vars)

raw_updated_violent_crime_data <- combinedoris(incombined=raw_violent_crime_data, inadditional=raw_robbery_data, incombinednum=17, inadditionalnum=15)


#Using the updated data in raw_updated_violent_crime_data need to replace the variables in the following dataset: raw_person_file_ori3 using raw_violent_crime_vars

#Drop the violent crime variables
raw_person_file_ori4 <- raw_person_file_ori3 %>%
  select(!!!(paste0("-",raw_violent_crime_vars) %>% rlang:::parse_exprs() ))

dim(raw_person_file_ori3)
dim(raw_person_file_ori4)
length(raw_violent_crime_vars)

#Next need to add on the variables
raw_person_file_ori5 <- raw_person_file_ori4 %>%
  left_join(raw_updated_violent_crime_data, by=c("ori"))

dim(raw_person_file_ori4)
dim(raw_updated_violent_crime_data)
dim(raw_person_file_ori5)

##############################Process Violent Crime 2 ###########################################

#Using dataset raw_person_file_ori5 - Need to fix the indicator Violent Crime
#Need to keep the Violent Crime indicators - column 17
raw_violent_crime2_vars <- colnames(raw_person_file_ori5) %>%
  str_match(pattern=paste0("t_", DER_TABLE_NAME, "_\\d+_\\d+_20")) %>%
  as_tibble() %>%
  filter(!is.na(V1)) %>%
  pull() %>%
  rlang:::parse_exprs()

#Need to keep the Robbery indicators - column 15
# raw_robbery_vars <- colnames(raw_person_file_ori3) %>%
#   str_match(pattern=paste0("t_", DER_TABLE_NAME, "_\\d+_\\d+_15")) %>%
#   as_tibble() %>%
#   filter(!is.na(V1)) %>%
#   pull() %>%
#   rlang:::parse_exprs()

print(raw_violent_crime2_vars)
print(raw_robbery_vars)

#Select the variables
raw_violent_crime2_data  <- raw_person_file_ori5 %>% select(ori, !!!raw_violent_crime2_vars)
raw_robbery2_data        <- raw_person_file_ori5 %>% select(ori, !!!raw_robbery_vars)

raw_updated_violent_crime2_data <- combinedoris(incombined=raw_violent_crime2_data, inadditional=raw_robbery2_data, incombinednum=20, inadditionalnum=15)


#Using the updated data in raw_updated_violent_crime2_data need to replace the variables in the following dataset: raw_person_file_ori5 using raw_violent_crime2_vars

#Drop the violent crime variables
raw_person_file_ori6 <- raw_person_file_ori5 %>%
  select(!!!(paste0("-",raw_violent_crime2_vars) %>% rlang:::parse_exprs() ))

dim(raw_person_file_ori5)
dim(raw_person_file_ori6)
length(raw_violent_crime2_vars)

#Next need to add on the variables
raw_person_file_ori7 <- raw_person_file_ori6 %>%
  left_join(raw_updated_violent_crime2_data, by=c("ori"))

dim(raw_person_file_ori6)
dim(raw_updated_violent_crime2_data)
dim(raw_person_file_ori7)


#######################################################################################

#Create the final ORI dataset
raw_person_file_ori7 %>%
  write_csv(gzfile(paste0(final_path,"Table ", DER_TABLE_NAME, " ORI.csv.gz")),na="0")
  