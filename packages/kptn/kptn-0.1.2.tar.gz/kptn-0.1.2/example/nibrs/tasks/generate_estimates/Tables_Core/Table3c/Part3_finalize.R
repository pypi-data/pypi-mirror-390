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

log_info("Running 11_Table3c_part3_finalize.R")
log_debug(system("free -mh", intern = FALSE))

#Create the filler dataset
data0 <- c(1:4) %>% as_tibble() %>%
  rename(row = value)
data0 <- assign_section(data0)

maximum_column = 15

#Create the list objects to separate
final_reporting_database <- vector("list", maximum_column)
final_data_list <- vector("list", maximum_column+1)
final_ori_data <- vector("list", maximum_column+1)


#Add on the filler dataset
final_data_list[[1]] <- data0
final_ori_data[[1]] <- weight_dataset

#Separate out the data from list objects
for(i in 1:maximum_column){

  #Get the data object
  raw_object1 <- readRDS(paste0(out_file_path,"/data_",DER_TABLE_NAME,"_",i,".rds"))
  raw_object2 <- readRDS(paste0(out_file_path,"/data_",DER_TABLE_NAME,"_",i+100,".rds"))
  #Save normal table to list
  final_data_list[[i+1]] <- bind_rows(raw_object1[[1]], raw_object2[[1]] %>% assign_row_section2() )

  #Save the reporting database to new object
  final_reporting_database[[i]] <-   bind_rows(raw_object1[[2]], raw_object2[[2]] %>%
                                                 assign_row_section2() %>%
                                                 assign_labels() )

  #Need to fix raw_object2[[3] - issue is that the section and row numbers are incorrect due to using the original assign_row_section function

  #Fix the column names in the ORI dataset
  raw_colnames <- raw_object2[[3]] %>%
    colnames() %>%
    str_match(pattern="t_(\\w+)_(\\d+)_(\\d+)_(\\d+)") %>%
    as_tibble() %>%
    filter(!is.na(V1)) %>%
    #V1 has original name of variable
    #V2 has table number
    #V3 has section number
    #V4 has row number
    #V5 has column number
    mutate(new_section = 2,
           new_row     = as.numeric(V4) + 2,
           new_column_name = paste0("t_", V2, "_", new_section, "_", new_row,"_", V5),
           rename = paste0(new_column_name, "=", V1)) %>%
    select(new_column_name, V1)

  #Rename if there are variable
  if(nrow(raw_colnames) > 0){
    for(j in 1:nrow(raw_colnames)){

      #Get recoded variable name
      innewname = raw_colnames[j,1] %>% as.character() %>% rlang:::parse_expr()

      #Get current variable name
      inoldname = raw_colnames[j,2] %>% as.character() %>% rlang:::parse_expr()

      #Rename the variable
    raw_object2[[3]] <- raw_object2[[3]] %>%
      rename(!!innewname := !!inoldname)
    }
  }

  final_ori_data[[i+1]] <-  full_join(raw_object1[[3]],
                                      raw_object2[[3]],
                                      by=c("ori"))


  #Delete the raw objects
  rm(raw_object1, raw_object2, raw_colnames)
  invisible(gc())


}




#Clear up memory
rm(list = c(ls(pattern="^agg"), ls(pattern="^data\\d+"), ls(pattern="^main")))
invisible(gc())

#Put datasets in list and merge
final_data <- reduce(final_data_list, left_join, by=c("section","row"))





#Get list of variables and make NAs to 0
listofvars_count <- final_data %>% select(starts_with("final_count")) %>% colnames()
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

  #Insert a blank
  output_list_vars[[list_counter]] <- paste0("blank_", i)
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
  3, 6)

file <- paste0("../TableShells/", "Indicator_Table_Shells.xlsx")

# Load the existing workbook
wb <- loadWorkbook(file = file)
table_sheet = "Table3c-Non-Person Victims"

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
  bind_rows()

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
final_ori_data2 <- final_ori_data %>%
  reduce(left_join, by = c("ori")) %>%
  write.csv0(gzfile(paste0(final_path,"Table ", DER_TABLE_NAME, " ORI.csv.gz")))

log_debug("Ending table")
log_debug(system("free -mh", intern = FALSE))