library(tidyverse)
library(openxlsx)
library(DBI)
library(DT)
library(lubridate)
library(data.table)

source(here::here("tasks/logging.R"))
source(here::here("tasks/impute_items/0-Common_functions_for_imputation.R"))

source("util.R")

DER_TABLE_NAME <- Sys.getenv("DER_TABLE_NAME")
inputPipelineDir <- Sys.getenv("INPUT_PIPELINE_DIR")
outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")
in_file_path = paste0(inputPipelineDir, "/indicator_table_single_intermediate/")
load(paste0(in_file_path,"/",DER_TABLE_NAME,"_prep_env.RData"))


#Figure out the number of columns
der_determine_column <- list.files(path=in_file_path, pattern=paste0("data_", DER_TABLE_NAME, "_")) %>%
  as_tibble() %>%
  mutate(der_table_num = str_match(string=.$value, pattern="\\w+_\\w+_(\\d+)\\.rds")[,2] %>% as.numeric()) %>%
  summarise(max_column = max(der_table_num)) %>%
  pull()

#Print the column
der_determine_column

#Overwrite maximum column
maximum_column <- der_determine_column

log_info("Running Part3_finalize.R")
log_debug(system("free -mh", intern = FALSE))

#Create the filler dataset
data0 <- c(1:DER_MAXIMUM_ROW) %>% as_tibble() %>%
  rename(row = value)
data0 <- assign_section(data0)

#Create the list objects to separate
final_reporting_database <- vector("list", maximum_column)
final_data_list <- vector("list", maximum_column+1)
final_ori_data <- vector("list", maximum_column+1)

#Add on the filler dataset
final_data_list[[1]] <- data0
final_ori_data[[1]] <- weight_dataset

#Create a new counter variable - start at 1 since the weights is at first position 
COUNTER_NUMBER_FILES = 1

#Separate out the data from list objects
for(i in 1:maximum_column){

  #Get the data object
  raw_object <- readRDS(paste0(out_file_path,"/data_",DER_TABLE_NAME,"_",i,".rds"))


  #Save normal table to list
  final_data_list[[i+1]] <- raw_object[[1]]

  #Save the reporting database to new object
  final_reporting_database[[i]] <-   raw_object[[2]]

  #final_ori_data[[i+1]] <-   raw_object[[3]]
  
  if(nrow(raw_object[[3]]) > 0){
    #Increment the count by 1
    COUNTER_NUMBER_FILES = COUNTER_NUMBER_FILES + 1
    final_ori_data[[COUNTER_NUMBER_FILES]] <-   raw_object[[3]]
  }  

  #Delete the raw objects
  rm(raw_object)
  invisible(gc())

}

#Clear up memory
rm(list = c(ls(pattern="^agg"), ls(pattern="^data\\d+"), ls(pattern="^main")))
invisible(gc())

#Put datasets in list and merge
final_data <- reduce(final_data_list, left_join, by=c("section","row"))

#Get list of variables and make NAs to 0
listofvars_count <- final_data %>% select(starts_with("final_count")) %>% colnames() %>% 
  as_tibble() %>% 
  mutate(der_keep = str_match(string=.$value, pattern="final_count_(\\d+)")[,2] %>% as.numeric()) %>%
  filter(der_keep %in% c(1:DER_MAXIMUM_COLUMN)) %>%
  pull(value)
print(listofvars_count)

listofvars_percentage <- final_data %>% select(starts_with("percent")) %>% colnames()%>% 
  as_tibble() %>% 
  mutate(der_keep = str_match(string=.$value, pattern="percent_(\\d+)")[,2] %>% as.numeric()) %>%
  filter(der_keep %in% c(1:DER_MAXIMUM_COLUMN)) %>%
  pull(value)
print(listofvars_percentage)

final_data3 <- NA_to_0_count(data=final_data, list=listofvars_count)


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

#Need to overwrite the number of columns to keep
output_column <- DER_MAXIMUM_COLUMN

print(output_column)

#Create string of variables to output
outputvarsorder <- NULL

#Create the list of variables to output in order
output_list_vars <- vector("list", 1*output_column)
list_counter = 1

#Loop through and create the variable order
for(i in 1:output_column){


  #Get the current column number
  output_list_vars[[list_counter]] <- paste0("final_count_", i)
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
  2, 5, 14, 20, 25, 29, 36, 41, 44, 49, 55, 62, 71, 78, 82)


# Specify the filename of existing workbook(Do not have file open)
file <- paste0("../TableShells/", "Gun_Violence_Draft_Table_Shells.xlsx")

# Load the existing workbook
wb <- loadWorkbook(file = file)
table_sheet = "TableGV2b-Victim-Rates"

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

fileout <- paste0(final_path, "Indicator_Table_",DER_TABLE_NAME,".xlsx")

# Save the workbook
saveWorkbook(wb, fileout, overwrite = TRUE)

#Output the Reporting database
final_reporting_database2 <- final_reporting_database %>%
  bind_rows() %>%
  #Subset to original variables
  filter(column %in% c(1:DER_MAXIMUM_COLUMN))

#Choose columns to not be transpose
final_reporting_database2_column <- final_reporting_database2 %>%
  head(1) %>%
  colnames() %>%
  as_tibble() %>%
  filter(!trim_upcase(value) %in% c("COUNT", "PERCENTAGE", "RATE") ) %>%
  select(1) %>%
  pull() %>%
  paste0("-", .) %>%
  rlang:::parse_exprs()

#Create the final database
final_reporting_database2 %>%
  gather(key="estimate_type", value="estimate", !!!final_reporting_database2_column) %>%
  #Clear population_estimate if not estimate_type RATE
  mutate(population_estimate = case_when(!trim_upcase(estimate_type) %in% c("RATE") ~ DER_NA_CODE,
                                         TRUE ~ population_estimate),
         estimate_geographic_location = DER_GEOGRAPHIC_LOCATION,
         analysis_weight_name = DER_WEIGHT_VARIABLE_STRING,
         estimate_type_num = fcase(
            trim_upcase(estimate_type) %in% c("COUNT"), 1,
            trim_upcase(estimate_type) %in% c("PERCENTAGE"), 2,
            trim_upcase(estimate_type) %in% c("RATE"), 3
         )) %>%
  #Create the estimate_type_detail_percentage variable
  estimate_type_detail_percentage_label() %>%
  #Create the estimate_type_detail_rate variable
  estimate_type_detail_rate_label() %>%
  write.csv(paste0(final_path,"Table ", DER_TABLE_NAME, "_Reporting_Database_part1.csv"))

#Output the ORI domains for Variance

#Create the final ORI dataset
#final_ori_data2 <- final_ori_data %>%
#  reduce(left_join, by = c("ori")) %>%
#  write.csv0(gzfile(paste0(final_path,"Table ", DER_TABLE_NAME, " ORI.csv.gz")))

#########################################New code to handle large demographic permutations###########################
#Create a list object to separate the files
#Note %% is for the remainder
#Note %/% is for the root
CONST_NUMBER_OF_FILES <- 100
CONST_NUMBER_OF_FILES_IN_LAST_LOOP <- COUNTER_NUMBER_FILES %% CONST_NUMBER_OF_FILES

#See the total number of files
print(COUNTER_NUMBER_FILES)
print(CONST_NUMBER_OF_FILES_IN_LAST_LOOP)

#Declare the length of the list
CONST_NUMBER_LIST <- (COUNTER_NUMBER_FILES %/% CONST_NUMBER_OF_FILES) + 1
print(CONST_NUMBER_LIST)

LIST_FINAL_DATA <- vector("list", CONST_NUMBER_LIST )

#Declare a counter variable to loop thru the list
for(i in 1:length(LIST_FINAL_DATA)){
  #Get the number of files to process
  tbd_min <-  (i-1)*CONST_NUMBER_OF_FILES + 1
  tbd_max <-  (i-1)*CONST_NUMBER_OF_FILES + CONST_NUMBER_OF_FILES
  
  #Save to list
  LIST_FINAL_DATA[[i]] <- final_ori_data[c(tbd_min:tbd_max) ]
  
  #Delete the object
  rm(tbd_min, tbd_max)
  invisible(gc())
  
  log_debug(paste0("Finish separating loop:  ", i))
}

#Next want to loop thru and use reduce on each list
LIST_FINAL_DATA2 <- vector("list", CONST_NUMBER_LIST )

#Declare a counter variable to loop thru the list
for(i in 1:length(LIST_FINAL_DATA2)){
  
  #If it is the list part of the list, need to specific the last non-missing element
  if(i == length(LIST_FINAL_DATA2)) {
    #Save to list
    LIST_FINAL_DATA2[[i]] <- LIST_FINAL_DATA[[i]][1:CONST_NUMBER_OF_FILES_IN_LAST_LOOP] %>% reduce(merge, by="ori", all=TRUE)
  } else{
    #Save to list
    LIST_FINAL_DATA2[[i]] <- LIST_FINAL_DATA[[i]] %>% reduce(merge, by="ori", all=TRUE)
  }
  
  log_debug(paste0("Finish merging loop:  ", i))
}

#Create the final_ori_data2 
final_ori_data2 <- LIST_FINAL_DATA2 %>%
  reduce(merge, by="ori", all=TRUE)

log_debug(paste0("Finish merging all files"))

#Write the data to the share
final_ori_data2 %>%
  fwrite_wrapper(paste0(final_path,"Table ", DER_TABLE_NAME, " ORI.csv.gz"), na=0)


log_debug("Ending table")
log_debug(system("free -mh", intern = FALSE))
