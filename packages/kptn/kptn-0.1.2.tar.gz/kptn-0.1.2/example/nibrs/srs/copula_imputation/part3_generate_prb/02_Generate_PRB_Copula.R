library(tidyverse)
library(openxlsx)
library(DT)
library("rjson")

#Read in the common functions to be used in R
source(here::here("tasks/logging.R"))
source(here::here("tasks/impute_items/0-Common_functions_for_imputation.R"))

#input/output
read_csv_quick <- partial(read_csv, guess_max = 100) #For now, read thru the 1st 1,000,000 rows to determine variable type
read_csv <- partial(read_csv, guess_max = 10000) #For now, read thru the 1st 1,000,000 rows to determine variable type
write.csv0 <- partial(write.csv, row.names = FALSE, na ="0")
write.csv <- partial(write.csv, row.names = FALSE, na ="")

#Get the needed variables from the POP_Total_code_assignment.R program so it can be run without reading in this file
DER_TABLE_PATTERN_STRING = "t_(\\w+)_(\\d+)_(\\d+)_(\\d+)"

#input/output directories for pipeline artifacts
outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")
inputPipelineDir <- Sys.getenv("INPUT_PIPELINE_DIR")
external_path <- Sys.getenv("EXTERNAL_FILE_PATH")

#External files json
input_folder <- sprintf("%s", inputPipelineDir)
file_locs <- fromJSON(file = sprintf("%s/external_file_locations.json", input_folder))

der_file_path = paste0(inputPipelineDir, "/srs/indicator_table_extracts/") #output path for all the data extracts
der_file_indicator_table_estimates_path = paste0(inputPipelineDir, "/srs/indicator_table_estimates/")
pop_file_path = paste0(inputPipelineDir, "/srs/weighting/Data/")

#set-up year
CONST_YEAR <- Sys.getenv("DATA_YEAR")
table <- Sys.getenv("TABLE_NAME")
perm <- Sys.getenv("DER_CURRENT_PERMUTATION_NUM") %>% as.numeric()

if (perm < 1000) {
  copula_perm <- 1
} else {
  copula_perm <- perm - (perm %% 1000) + 1
}

input_copula_data_folder <- file.path(inputPipelineDir,"srs" ,"copula_imputation", "Data")
output_copula_prb_folder <- file.path(outputPipelineDir,"srs","copula_imputation", "PRB")

if (! dir.exists(output_copula_prb_folder)) {
  dir.create(output_copula_prb_folder, recursive = TRUE)
}

log_info(paste0("Starting 02_Generate_PRB_Copula.R for TABLE:",table," and PERMUTATION: ",perm))
log_debug(system("free -mh", intern = FALSE))

merge_on_weights_variance_new_for_bias <- function(indata, incounty){

  #Read in the variance dataset
  raw_variance <- read_csv(gzfile(file.path(der_file_path, "ORI_VARIANCE.csv.gz")))

  print("The variance dataset has the following dim:")
  print(log_dim(raw_variance))

  #Need to subset on the current permutation
  raw_variance <- raw_variance %>%
	filter(!!DER_PERMUTATION_SUBSET_SYMBOL)  %>%
	select(ORI, ori, !!DER_WEIGHT_VARIABLE_SYMBOL, !!DER_ORI_WEIGHT_GROUP_SYMBOL, !!DER_ORI_WEIGHT_DESCRIPT_GROUP_SYMBOL, county) %>%
	#Recreate the weight variable
	mutate(raw_weight = as.double(!!DER_WEIGHT_VARIABLE_SYMBOL), county = as.numeric(county))

  print(paste0("The variance dataset has the following dim after subsetting to ", DER_PERMUTATION_SUBSET_STRING))
  print(log_dim(raw_variance))
  
  print("The main dataset has the following dim:")
  print(log_dim(indata))
  
  # need to subset the main data to the current permutation
  #indata <- indata
    #20230720 - Relax this condition since not all variables will be on there - Only really need to check is at the national level
    #filter(!!DER_PERMUTATION_SUBSET_SYMBOL) %>%

  #print(paste0("The main dataset has the following dim after subsetting to ", DER_PERMUTATION_SUBSET_STRING))
  #print(log_dim(indata))

  #Need to merge on by the weight dataset first
  #Also the NIBRS database ori should be the full string current ORI in the Universe file from the weighting task
  if(incounty == 1){
  returndata <- raw_variance %>%
    left_join(indata %>%
	#Drop the NATIONAL weight variable
	select(-weight) %>%
	#Create an indicator variable
	mutate(in_main_data = 1), by=c("ORI" = "ori", "county"))

  print("The number of merges to the variance dataset are:")
  print(sum(returndata$in_main_data, na.rm = TRUE))
  } else{
    returndata <- raw_variance %>%
      left_join(indata %>%
                  #Drop the NATIONAL weight variable
                  select(-weight) %>%
                  #Create an indicator variable
                  mutate(in_main_data = 1), by=c("ORI" = "ori"))
    
    print("The number of merges to the variance dataset are:")
    print(sum(returndata$in_main_data, na.rm = TRUE))    
    
    
  }

	#Create new weight variable
  returndata <- returndata %>%
    mutate(weight = case_when(in_main_data == 1 ~ raw_weight)) %>%
	select(-raw_weight, -in_main_data)

  print("After merging, the combined dataset has the following dim:")
  print(log_dim(returndata))

  #Need to get the list of variables to code the missings as 0
  raw_selected_vars <- returndata  %>%
    colnames() %>%
    str_match(pattern=DER_TABLE_PATTERN_STRING) %>%
    as_tibble() %>%
    #Make sure the variable is a match to the pattern name
    filter(!is.na(V1)) %>%
    #Make the derived variables from variable name
    select(V1) %>%
    pull() %>%
    rlang:::parse_exprs()

  #Code the missings as 0
  for(i in 1:length(raw_selected_vars)){

    #Select the current variables
    invar <- raw_selected_vars[[i]]

      returndata <- returndata %>%
      #Add code to make sure it is a double
      mutate(!!invar := as.double(!!invar)) %>%
      mutate(!!invar := case_when(is.na(!!invar) ~ 0,
                                  TRUE ~ !!invar
    ))
  }

  #Return the data
  return(returndata)
}


#Next need to read in the population file
#Get the population total files and create variables
pop_data <- read_csv(paste0(pop_file_path, "POP_TOTALS_PERM_", CONST_YEAR, "_FINAL_SRS.csv"))

#Need to get list of csv output to compute PRB
copula_file_name = paste0("Table_",table,"_Final_Agency_File_Perm_",copula_perm,"_Rates_PARENT_POP_GROUP_CODE2_SRS.csv")

#Save the current path
#raw_file <- .x
raw_file <- file.path(input_copula_data_folder,copula_file_name)

#Get the initial variable types
raw_variable_specs <- spec_csv(file=raw_file)

#Get the variable names <- Okay to have parsing errors
raw_variable_types <- read_csv_quick(file=raw_file) %>%
  #Get variable names
  colnames() %>%
  #Change to a dataset
  as_tibble()


raw_variable_types2 <-raw_variable_types %>%
  #Identify the variables that corresponds to the id of the table cells
  mutate(
    der_table_string = str_match(.$value, pattern="t_\\w+_\\d+_\\d+_\\d+")) %>%
  #Subset to matches only
  filter(!is.na(der_table_string)) %>%
  #Create code to identify these as type double
  #mutate(
  #  der_table_variable_double = paste0(value, " = col_double()")) %>%
  #Pull the variables
  select(der_table_string) %>%
  pull()

#If the dataset is blank then return
if(nrow(raw_variable_types2) == 0){
  #return(NULL)
  rm(list=ls(pattern="raw_"))
  invisible(gc())
  next
}

#Need to loop thru variables to change the type
for(i in 1:length(raw_variable_types2)){
  raw_variable_specs$cols[[raw_variable_types2[[i]]]] <- col_double()
}

#Read in the data
raw_main <- read_csv(file=raw_file, col_types=raw_variable_specs) %>%
  rename(ori=ORI) %>%
  #Force the county variable to be numeric in order to be consistent with what's done in the ORI_VARIANCE.csv.gz 
  mutate(
	county = as.numeric(county)
  )		

#Remove objects
rm(raw_variable_specs, raw_variable_types, raw_variable_types2)
invisible(gc())

#Need to get the current permutation number
raw_permutation_num <- perm

#Create permutation number
raw_main2 <- raw_main %>%
  mutate(permutation_number = raw_permutation_num)

#Next need to fill in the following variables
raw_pop_data <- pop_data %>% filter(PERMUTATION_NUMBER == raw_permutation_num)

#Declare the variables needed for variance estimation
DER_PERMUTATION_SUBSET_STRING = raw_pop_data$PERMUTATION_NUMBER_DESC
DER_PERMUTATION_SUBSET_SYMBOL <- raw_pop_data %>% select(PERMUTATION_NUMBER_DESC) %>% pull() %>% rlang:::parse_expr()
DER_WEIGHT_VARIABLE_SYMBOL    <- raw_pop_data %>% select(WEIGHT_VAR) %>% pull() %>% rlang:::parse_expr()
DER_ORI_WEIGHT_GROUP_SYMBOL   <- raw_pop_data %>% select(WEIGHT_GROUP_VAR) %>% pull() %>% rlang:::parse_expr()
DER_ORI_WEIGHT_DESCRIPT_GROUP_SYMBOL <- raw_pop_data %>% select(PERMUTATION_DESCRIPTION_VAR) %>% pull() %>% rlang:::parse_expr()

#Merge on the information from the weight dataset
main_copula <- merge_on_weights_variance_new_for_bias(raw_main2, incounty=1)

log_dim(raw_main)
log_dim(main_copula)

#NEW:  Need to run this for the weighted estimates using the original ORI file
raw_weighted <- read_csv_quick(file = gzfile(paste0(der_file_indicator_table_estimates_path, "Table ", table, " ORI.csv.gz")))
main_weighted <- merge_on_weights_variance_new_for_bias(raw_weighted, incounty=0)

log_dim(raw_weighted)
log_dim(main_weighted)


#Next step is to use the dataset main and calculate the PRBs

#Create a vector to hold the variables
raw_variables <- colnames(main_copula) %>%
str_match(pattern=DER_TABLE_PATTERN_STRING) %>%
as_tibble() %>%
filter(!is.na(V1)) %>%   #Make the derived variables from variable name
mutate(variable_name = V1,
       table = V2,
       section = as.numeric(V3),
       row = as.numeric(V4),
       column = as.numeric(V5)) %>%
select(-V1,-V2,-V3,-V4,-V5)

#Declare list and loop thru variables
raw_variable_list <- raw_variables %>%
select(variable_name) %>%
pull()


raw_process_list_1 <- map(raw_variable_list, ~ {

tbd_var_name <- .x

#Create a symbol
tbd_var_name_symbol = tbd_var_name %>% rlang:::parse_expr()

#Get the raw counts
tbd_raw_unweighted_counts <- main_copula %>%
  summarise(der_unweighted_counts = sum(!!(tbd_var_name_symbol), na.rm=TRUE)) %>%
  pull() %>%
  as.numeric()

#Get the weighted counts
tbd_raw_weighted_counts <- main_weighted %>%
  mutate(raw_weighted_counts = weight *!!(tbd_var_name_symbol) ) %>%
  summarise(der_weighted_counts = sum(raw_weighted_counts, na.rm=TRUE)) %>%
  pull() %>%
  as.numeric()

#Combine the data together
tbd_return_data <- bind_cols(tbd_var_name, tbd_raw_unweighted_counts, tbd_raw_weighted_counts)
colnames(tbd_return_data) <- c("variable_name", "der_unweighted_counts", "der_weighted_counts")

#Return the data to list
return(tbd_return_data)

})


#Bind the datasets together
final_imputed_prb <- raw_process_list_1 %>%
bind_rows() %>%
#Create the percent relative bias
mutate(percent_relative_bias_imputed = case_when(
  der_weighted_counts > 0 ~ ((der_weighted_counts - der_unweighted_counts) / der_weighted_counts )*100),
  permutation_number = raw_permutation_num)


#New in 20240507 - For permutations where the COVERAGETABLE_NIBRSSRS_3MONTHS_AGN_PERCENT is 100%
#Make the bias to be 0 and the copula totals to be the same as the weighted total
CONST_COVERAGETABLE_NIBRSSRS_3MONTHS_AGN_PERCENT <- pop_data %>%
  filter(PERMUTATION_NUMBER == raw_permutation_num) %>%
  select(COVERAGETABLE_NIBRSSRS_3MONTHS_AGN_PERCENT) %>%
  pull()

#See the number
print(CONST_COVERAGETABLE_NIBRSSRS_3MONTHS_AGN_PERCENT)

if(!is.na(CONST_COVERAGETABLE_NIBRSSRS_3MONTHS_AGN_PERCENT) & CONST_COVERAGETABLE_NIBRSSRS_3MONTHS_AGN_PERCENT == 100){
  log_debug(paste0("Permutation Number ", raw_permutation_num, " detected 100% agency reporting.  Setting bias to 0"))
  
  log_debug(paste0("Before setting bias to 0"))
  log_dim(final_imputed_prb)
  
  final_imputed_prb <- final_imputed_prb %>%
    mutate(
      #Make the copula counts to be the same as the weighted counts
      der_unweighted_counts = der_weighted_counts,
      
      #Make the PRB to be 0
      percent_relative_bias_imputed  = 0
      
    )
  
  log_debug(paste0("After setting bias to 0"))
  log_dim(final_imputed_prb) 
  
}


#return(final_imputed_prb)
#Return the dataset
#tbd_list[[i]] <-final_imputed_prb

#Create new file name
raw_new_file_name2 <- paste0("PRB_",table,"_Final_Agency_File_Perm_",perm,".csv.gz")

final_imputed_prb %>%
  write_csv(gzfile(file.path(output_copula_prb_folder, raw_new_file_name2)), na="")

#Clear the objects
rm(list=c(ls(pattern="raw_"),
"DER_PERMUTATION_SUBSET_STRING",
"DER_PERMUTATION_SUBSET_SYMBOL",
"DER_WEIGHT_VARIABLE_SYMBOL",
"DER_ORI_WEIGHT_GROUP_SYMBOL",
"DER_ORI_WEIGHT_DESCRIPT_GROUP_SYMBOL",
"final_imputed_prb",
"main_copula", 
"main_weighted"
))
invisible(gc())

log_debug("Finishing...")
log_debug(system("free -mh", intern = FALSE))
