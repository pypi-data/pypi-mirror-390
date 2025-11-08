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


##########################Set the variables for table #######################
DER_MAXIMUM_ROW = 19
DER_MAXIMUM_COLUMN = 13


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
       if(raw_variable_row == 3){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(3, 7), raw_variable_column)} #Firearm type: Single gun type
  else if(raw_variable_row == 4){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(3), raw_variable_column)} #Firearm type: Handgun only
  else if(raw_variable_row == 5){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(3), raw_variable_column)} #Firearm type: Long gun (Rifle and Shotgun) only
  else if(raw_variable_row == 6){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(3), raw_variable_column)} #Firearm type: Unknown firearm type (Other Firearm and Firearm) only
  else if(raw_variable_row == 7){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(3, 7), raw_variable_column)} #Firearm type: Multiple firearm types
  else if(raw_variable_row == 8){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(8:19), raw_variable_column)} #Location Type 4: Residence
  else if(raw_variable_row == 9){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(8:19), raw_variable_column)} #Location Type 4: Hotel
  else if(raw_variable_row == 10){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(8:19), raw_variable_column)} #Location Type 4: Transportation hub/outdoor public locations
  else if(raw_variable_row == 11){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(8:19), raw_variable_column)} #Location Type 4: Schools, daycares, and universities
  else if(raw_variable_row == 12){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(8:19), raw_variable_column)} #Location Type 4: Retail/financial/other commercial establishment
  else if(raw_variable_row == 13){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(8:19), raw_variable_column)} #Location Type 4: Restaurant/bar/sports or entertainment venue
  else if(raw_variable_row == 14){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(8:19), raw_variable_column)} #Location Type 4: Religious buildings
  else if(raw_variable_row == 15){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(8:19), raw_variable_column)} #Location Type 4: Government/public buildings
  else if(raw_variable_row == 16){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(8:19), raw_variable_column)} #Location Type 4: Jail/prison
  else if(raw_variable_row == 17){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(8:19), raw_variable_column)} #Location Type 4: Shelter-mission/homeless
  else if(raw_variable_row == 18){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(8:19), raw_variable_column)} #Location Type 4: Drug Store/Doctor’s Office/Hospital
  else if(raw_variable_row == 19){raw_denominator = CREATE_PERCENTAGE_DENOMINATOR2(raw_total, c(8:19), raw_variable_column)} #Location Type 4: Other/unknown location
  
  
  
  
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
  2, 5, 11)


# Specify the filename of existing workbook(Do not have file open)
file <- paste0("../TableShells/", "Gun_Violence_Draft_Table_Shells.xlsx")

# Load the existing workbook
wb <- loadWorkbook(file = file)
table_sheet = "TableGV1a-Offenses"

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

fileout <- paste0(final_path, "Indicator_Table_GV1a.xlsx")

# Save the workbook
saveWorkbook(wb, fileout, overwrite = TRUE)
