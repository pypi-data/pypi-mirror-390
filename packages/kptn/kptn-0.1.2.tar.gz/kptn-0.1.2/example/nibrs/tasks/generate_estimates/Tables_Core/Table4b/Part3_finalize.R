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


log_info("Running 13_Table4b_part3_finalize.R")
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

  final_ori_data[[i+1]] <-   raw_object[[3]]
  
  # if(nrow(raw_object[[3]]) > 0){
  #   #Increment the count by 1
  #   COUNTER_NUMBER_FILES = COUNTER_NUMBER_FILES + 1
  #   final_ori_data[[COUNTER_NUMBER_FILES]] <-   raw_object[[3]]
  # }
 

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
2, 4, 8, 19, 23, 30, 37, 41)


# Specify the filename of existing workbook(Do not have file open)
file <- paste0("../TableShells/", "Indicator_Table_Shells.xlsx")

# Load the existing workbook
wb <- loadWorkbook(file = file)
table_sheet = "Table4b-Arrestees-Rates"

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

fileout <- paste0(final_path, "Indicator_Table_4b.xlsx")

# Save the workbook
saveWorkbook(wb, fileout, overwrite = TRUE)

#Output the Reporting database
final_reporting_database2 <- final_reporting_database %>%
bind_rows()  %>%
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
          trim_upcase(estimate_type) %in% c("COUNT"),  1,
          trim_upcase(estimate_type) %in% c("PERCENTAGE"),  2,
          trim_upcase(estimate_type) %in% c("RATE"),  3
       )) %>%
#Create the estimate_type_detail_percentage variable
estimate_type_detail_percentage_label() %>%
#Create the estimate_type_detail_rate variable
estimate_type_detail_rate_label() %>%
write.csv(paste0(final_path,"Table ", DER_TABLE_NAME, "_Reporting_Database.csv"))

#Output the ORI domains for Variance

#Create the final ORI dataset
# final_ori_data2 <- final_ori_data %>%
# reduce(left_join, by = c("ori")) %>%
# write.csv0(gzfile(paste0(final_path,"Table ", DER_TABLE_NAME, " ORI.csv.gz")))

#########################################New code to handle split the single ORI file into multiple files###########################
#Note maximum_column contains the number of files (i.e. each file is an offense subset to demographics)
#     final_ori_data contains the list of the files mentioned above
#     DER_MAXIMUM_COLUMN contains how many columns in a demographic permutation

#Next need to create a data file to loop thru to create the various demographic files
CONST_MAXIMUM_FILES <- (maximum_column / DER_MAXIMUM_COLUMN)

log_debug("The number of files that will be created in Table ", DER_TABLE_NAME, " is ", CONST_MAXIMUM_FILES)
log_debug(system("free -mh", intern = FALSE))

main_loop_file <- c(1:CONST_MAXIMUM_FILES) %>%
  as_tibble() %>%
  #Rename value to row
  rename(row=value) %>%
  mutate(
    #Create the maximum number of columns within a file
    der_main_column =  DER_MAXIMUM_COLUMN,
    #Create the starting and ending number per row
    der_start_num = (row-1)*der_main_column + 1,
    der_end_num   = (row-1)*der_main_column + der_main_column,
    
    #Create the suffix for the file
    der_suffix_num = ((row-1) * 1000) + 1
  )


#Create a function to create the separate datasets

pmap(list(der_start_num   = main_loop_file$der_start_num, 
          der_main_column = main_loop_file$der_main_column, 
          der_suffix_num  = main_loop_file$der_suffix_num),
     
     function(der_start_num, der_main_column, der_suffix_num){
     

  #Get the starting number
  TBD_START_NUM  <- der_start_num
  TBD_NUM_COLUMN <- der_main_column
  TBD_SUFFIX     <- der_suffix_num
  
  
  #Create a list object to hold the results
  TBD_LIST <- vector("list", TBD_NUM_COLUMN+1)
  
  #Put the weights in the first position of TBD_LIST
  TBD_LIST[[1]] <- final_ori_data[[1]] #Weights are in the first portion of the list
  
  #Keep a counter to see when to add data
  #Add 1 to skip the weight data
  TBD_COUNTER <- 1
  
  #Next need to loop thru 2 to the TBD_NUM_COLUMN+1 and add on the appropriate objects to the list
  for(i in c(2:(TBD_NUM_COLUMN+1))){
    
    
    #If the current list has data then save to list
    #Need to minus one to account for the starting position of the weights
    if(nrow(final_ori_data[[i - 1 + TBD_START_NUM]]) > 0  ){
      
      #Increase the counter
      TBD_COUNTER = TBD_COUNTER + 1    
      
      #Save data to list
      TBD_LIST[[TBD_COUNTER]] <- final_ori_data[[i - 1 + TBD_START_NUM]]
      
    }
  }
  
  log_debug("Processing Table ", DER_TABLE_NAME, " Permutation ", TBD_SUFFIX, " and starting file ", TBD_START_NUM, 
            " have ", TBD_COUNTER, " non-empty files.")
  
  #With the results in TBD_LIST, need to form the dataset and output 
  TBD_FINAL <- TBD_LIST[c(1:TBD_COUNTER)] %>% reduce(left_join, by="ori") %>%
    mutate(
      #Next need to 0 fill
      across(
        .cols=matches("t_(\\w+)_(\\d+)_(\\d+)_(\\d+)"),
        #.cols=starts_with("t_"),
        .fns = ~{ replace_na(.,replace=0) },
        .names = "{.col}"
      )
    )
  
  #Output the dataset to the share
  #Use fwrite if got data
  if(nrow(TBD_FINAL) > 0){
    TBD_FINAL %>%
      select(ori, weight, matches("t_(\\w+)_(\\d+)_(\\d+)_(\\d+)")) %>%
      fwrite(paste0(final_path,"Table ", DER_TABLE_NAME, " ORI_", TBD_SUFFIX , ".csv.gz"))
    #Otherwise use write_csv  
  }else{
    TBD_FINAL %>%
      select(ori, weight, matches("t_(\\w+)_(\\d+)_(\\d+)_(\\d+)")) %>%
      write_csv(paste0(final_path,"Table ", DER_TABLE_NAME, " ORI_", TBD_SUFFIX , ".csv.gz"))    
    
  }
  rm(list=c("TBD_FINAL","TBD_LIST"))
  invisible(gc())
})

#Ending the program
log_debug("Ending table")
log_debug(system("free -mh", intern = FALSE))
