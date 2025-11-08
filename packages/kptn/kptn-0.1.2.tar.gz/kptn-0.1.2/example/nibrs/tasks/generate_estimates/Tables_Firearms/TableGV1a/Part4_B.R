#install.packages("RPostgres")
#install.packages("dbplyr")
library("rjson")
library(tidyverse)
library(openxlsx)
library(DBI)
library(DT)
library(lubridate)
library(data.table)

#read_csv <- partial(read_csv, guess_max = 1000000) #For now, read thru the 1st 1,000,000 rows to determine variable type
write.csv0 <- partial(write.csv, row.names = FALSE, na ="0")
#write.csv <- partial(write.csv, row.names = FALSE, na ="")

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

# read in the GV1a part a functions. Some will be overwritten
source("util.R")


#Read in the main datasets to be used for the table
main <- fread(
  file = paste0(der_file_path, "cleaned_recoded_all_Firearm_Offenses_recoded_incident.csv.gz"),
  select = c(
    "ori",
    "weight",
    "incident_id",
    "offense_id",
    "der_robbery",
    "der_car_jacking"
  )
)

# Firearm type
# Multiple firearm types

agg_single_multi_firearm_types_inc_offenses <- fread(paste0(der_file_path, "agg_single_multi_firearm_types_inc_offenses.csv.gz"))


# Single gun type
# Handgun only
# Long gun (Rifle and Shotgun) only
# Unknown firearm type (Other Firearm and Firearm) only

agg_single_gun_cat_inc_offenses <- fread(paste0(der_file_path, "agg_single_gun_cat_inc_offenses.csv.gz"))

# Location Type 4
# Residence
# Hotel
# Transportation hub/outdoor public locations
# Schools, daycares, and universities
# Retail/financial/other commercial establishment
# Restaurant/bar/sports or entertainment venue
# Religious buildings
# Government/public buildings
# Jail/prison
# Shelter-mission/homeless
# Drug Store/Doctor’s Office/Hospital
# Other/unknown location

agg_location_1_12_inc_offenses <- fread(paste0(der_file_path, "agg_location_1_12_inc_offenses.csv.gz"))




#Declare the final section and row number for the table
assign_row <- function(data){

  returndata <- data %>% mutate(

  row = fcase(
    section == 1 , 1,
    section == 2 , 2, 
    
    der_single_multi_firearm_types %in% c(1), 3, #Firearm type	Single gun type
    der_single_gun_cat %in% c(1:3), der_single_gun_cat + 3 ,
    der_single_multi_firearm_types %in% c(2), 7,#Firearm type	Multiple firearm types
    der_location_1_12 %in% c(1:12), 7 + der_location_1_12
    
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
DER_MAXIMUM_ROW = 19
#############################################################################



#This function will calculate the counts and percentage one column at a time

generate_est2 <- function(maindata, subsetvareq1, column_number){

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
  
  #Firearm type
  # Single gun type
  # Multiple firearm types
  s3 <- agg_percent(leftdata = main_filter, rightdata = agg_single_multi_firearm_types_inc_offenses, var=der_single_multi_firearm_types, section=3, mergeby=c( "incident_id", "offense_id"))
  
  der_firearm_single_denom <- s3[[1]] %>%
    filter(der_single_multi_firearm_types == 1) %>% #Yes response
    select(final_count) %>%
    as.double()  
  
  #Firearm type 
  # Handgun only
  # Long gun (Rifle and Shotgun) only
  # Unknown firearm type (Other Firearm and Firearm) only
  
  s4 <- agg_percent_CAA(leftdata = main_filter, rightdata = agg_single_gun_cat_inc_offenses, var=der_single_gun_cat, section=4, mergeby=c( "incident_id", "offense_id"), 
                        denom=der_firearm_single_denom)  
  
  #Location Type 4
  s5 <- agg_percent(leftdata = main_filter, rightdata = agg_location_1_12_inc_offenses, var=der_location_1_12, section=5, mergeby=c( "incident_id", "offense_id"))
  


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
                                   TRUE ~ final_count)) %>%
           mutate(percent = case_when(is.na(percent) ~ 0,TRUE ~ percent),

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
data9  <- generate_est2(maindata=main, subsetvareq1 = "der_robbery", column_number=9)
data13  <- generate_est2(maindata=main, subsetvareq1 = "der_car_jacking", column_number=13)

#Have data9 which is the single offense count version.
#Next will to read in the GV1a Person file to update the robbery estimates
raw_person_file_ori <- fread(paste0(final_path_in, "Table ", DER_TABLE_NAME, " ORI_PERSON.csv.gz"))

#Next need to drop the Robbery estimates except for the victim offender relationship section
raw_drop_columns <-colnames(raw_person_file_ori) %>%
  #Keep the matches to column 9 = Robbery, 13 = Car Jacking
  str_match(pattern=paste0("t_", DER_TABLE_NAME, "_(\\d+)_(\\d+)_(9|13)")) %>%
  as_tibble() %>%
  #Drop the non-matches
  filter(!is.na(V1)) %>%
  #Set the names
  set_names("variable", "section", "row", "column") %>%
  #Need to drop all rows but the victim offender relationship
  #filter(!row %in% c(18:23)) %>%
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

#Next need to use the data9[[3]] ORI file to add on variables to raw_person_file_ori2
glimpse(data9[[3]])
raw_person_file_ori3_1 <- raw_person_file_ori2 %>%
  left_join(data9[[3]], by=c("ori"))

#Check the dimension
dim(raw_person_file_ori)
dim(raw_person_file_ori2)
dim(raw_person_file_ori3_1)

#Next need to use the data13[[3]] ORI file to add on variables to raw_person_file_ori3_1
glimpse(data13[[3]])
raw_person_file_ori3_2 <- raw_person_file_ori3_1 %>%
  left_join(data13[[3]], by=c("ori"))

#Check the dimension
dim(raw_person_file_ori)
dim(raw_person_file_ori3_1)
dim(raw_person_file_ori3_2)


#Create data file raw_person_file_ori3
raw_person_file_ori3 <- raw_person_file_ori3_2


#Using dataset raw_person_file_ori3 - Need to fix the indicators with Robbery
#Need to keep the Total Gun Violence indicators - column 2
raw_totalgun_vars <- colnames(raw_person_file_ori3) %>%
  str_match(pattern=paste0("t_", DER_TABLE_NAME, "_\\d+_\\d+_2")) %>%
  as_tibble() %>%
  filter(!is.na(V1)) %>%
  pull() 

print(raw_totalgun_vars)

#Need to keep the Nonfatal Gun Violence indicators - column 4
raw_nonfatalgun_vars <- colnames(raw_person_file_ori3) %>%
  str_match(pattern=paste0("t_", DER_TABLE_NAME, "_\\d+_\\d+_4")) %>%
  as_tibble() %>%
  filter(!is.na(V1)) %>%
  pull() 

print(raw_nonfatalgun_vars)

#Need to keep the Nonfatal Gun Violence 2 indicators - column 5
raw_nonfatalgun2_vars <- colnames(raw_person_file_ori3) %>%
  str_match(pattern=paste0("t_", DER_TABLE_NAME, "_\\d+_\\d+_5")) %>%
  as_tibble() %>%
  filter(!is.na(V1)) %>%
  pull() 

print(raw_nonfatalgun2_vars)

#Need to keep the Robbery indicators - column 9
raw_robbery_vars <- colnames(raw_person_file_ori3) %>%
  str_match(pattern=paste0("t_", DER_TABLE_NAME, "_\\d+_\\d+_9")) %>%
  as_tibble() %>%
  filter(!is.na(V1)) %>%
  pull() %>%
  rlang:::parse_exprs()

print(raw_robbery_vars)

#Select the variables
raw_totalgun_data  <- raw_person_file_ori3 %>% select(ori, !!!raw_totalgun_vars)
raw_nonfatalgun_data  <- raw_person_file_ori3 %>% select(ori, !!!raw_nonfatalgun_vars)
raw_nonfatalgun2_data  <- raw_person_file_ori3 %>% select(ori, !!!raw_nonfatalgun2_vars)

raw_robbery_data        <- raw_person_file_ori3 %>% select(ori, !!!raw_robbery_vars)

raw_updated_totalgun_data <- combinedoris(incombined=raw_totalgun_data, inadditional=raw_robbery_data, incombinednum=2, inadditionalnum=9)
raw_updated_nonfatalgun_data <- combinedoris(incombined=raw_nonfatalgun_data, inadditional=raw_robbery_data, incombinednum=4, inadditionalnum=9)
raw_updated_nonfatalgun2_data <- combinedoris(incombined=raw_nonfatalgun2_data, inadditional=raw_robbery_data, incombinednum=5, inadditionalnum=9)


#Using the updated data in raw_updated_ data need to replace the variables in the following dataset: raw_person_file_ori3 

#Drop the variables that do not have robbery variables
raw_person_file_ori4 <- raw_person_file_ori3 %>%
  #select(!!!(paste0("-",raw_totalgun_vars, raw_nonfatalgun_vars, raw_nonfatalgun2_vars) %>% rlang:::parse_exprs() ))
  select(
         !!!(paste0("-",raw_totalgun_vars) %>% rlang:::parse_exprs() ),  
         !!!(paste0("-", raw_nonfatalgun_vars)  %>% rlang:::parse_exprs() ), 
         !!!(paste0("-", raw_nonfatalgun2_vars) %>% rlang:::parse_exprs()) 
         )

dim(raw_person_file_ori3)
dim(raw_person_file_ori4)
length(raw_totalgun_vars)
length(raw_nonfatalgun_vars)
length(raw_nonfatalgun2_vars)

#Next need to add on the variables
# raw_person_file_ori5 <- raw_person_file_ori4 %>%
#   left_join(raw_updated_violent_crime_data, by=c("ori"))

raw_person_file_ori5 <- reduce(
  #Get the files
  mget(c("raw_person_file_ori4", "raw_updated_totalgun_data", "raw_updated_nonfatalgun_data", "raw_updated_nonfatalgun2_data")),
  #Do a left join
  left_join, 
  by=c("ori"))


dim(raw_person_file_ori4)
dim(raw_updated_totalgun_data)
dim(raw_updated_nonfatalgun_data)
dim(raw_updated_nonfatalgun2_data)
dim(raw_person_file_ori5)

#Create the final ORI dataset
raw_person_file_ori5 %>%
  write_csv(gzfile(paste0(final_path,"Table ", DER_TABLE_NAME, " ORI.csv.gz")),na="0")
