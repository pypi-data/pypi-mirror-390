library(tidyverse)
library(openxlsx)
library(DT)
library("rjson")
library(data.table)

#Read in the common functions to be used in R
source(here::here("tasks/logging.R"))
source(here::here("tasks/impute_items/0-Common_functions_for_imputation.R"))
source("../../generate_estimates/Demo_Tables_Func.R")													 

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

der_file_path = paste0(inputPipelineDir, "/indicator_table_extracts/") #output path for all the data extracts
der_file_indicator_table_estimates_path = paste0(inputPipelineDir, "/indicator_table_estimates/")																								 
pop_file_path = paste0(inputPipelineDir, "/weighting/Data/")

#set-up year
CONST_YEAR <- Sys.getenv("DATA_YEAR")
table <- Sys.getenv("TABLE_NAME")
perm <- Sys.getenv("DER_CURRENT_PERMUTATION_NUM") %>% as.numeric()

if (perm < 1000) {
  copula_perm <- 1
} else {
  copula_perm <- perm - (perm %% 1000) + 1
}

input_copula_data_folder <- file.path(inputPipelineDir, "copula_imputation", "Data")
output_copula_prb_folder <- file.path(outputPipelineDir,"copula_imputation", "PRB")

if (! dir.exists(output_copula_prb_folder)) {
  dir.create(output_copula_prb_folder, recursive = TRUE)
}

log_info(paste0("Starting 02_Generate_PRB_Copula.R for TABLE:",table," and PERMUTATION: ",perm))
log_debug(system("free -mh", intern = FALSE))

merge_on_weights_variance_new_for_bias <- function(indata, incounty){

  #Read in the variance dataset
  raw_variance <- tibble::as_tibble(fread(paste0(der_file_path, "ORI_VARIANCE.csv.gz")))

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

    #Borrow code from the program that creates the ORI_VARIANCE.csv.gz file to do the processing
    raw_final_weight_original <- raw_variance %>%
      group_by(ORI) %>%
      mutate(der_ori_counts = n() ) %>%
      ungroup()    
    
    ####Next do the join between the raw_final_weight_original and indata files
    #Try to process the raw_final_weight_original by single record and more than one record
    #Single record do not need county and more than one record will use county as critera
    
    raw_final_weight_original_only1 <- raw_final_weight_original %>% filter(der_ori_counts == 1)
    raw_final_weight_original_mt1   <- raw_final_weight_original %>% filter(der_ori_counts > 1)
    
    #Check the size
    print(log_dim(raw_final_weight_original))
    print(log_dim(raw_final_weight_original_only1))
    print(log_dim(raw_final_weight_original_mt1))
    
    #Using raw_final_weight_original_only1 do the processing without using the county variable for better merges
    
    tbd_good_1 <- raw_final_weight_original_only1 %>%
      inner_join(indata %>% select(-county), by=c("ORI")) %>%
      #Create an indicator variable
      mutate(in_main_data = 1)
    
    tbd_bad_1 <- raw_final_weight_original_only1 %>%
      anti_join(indata %>% select(-county), by=c("ORI"))
    
    #Stack the data together
    raw_final_weight_original_only1_final <- bind_rows(tbd_good_1, tbd_bad_1)
    
    print(log_dim(raw_final_weight_original_only1_final))
    print(log_dim(raw_final_weight_original_only1))
    print(log_dim(tbd_good_1))
    print(log_dim(tbd_bad_1))
    
    #Check the merge
    print("The number of single county ORIs in the variance dataset are:")
    print(nrow(raw_final_weight_original_only1))       
    
    print("The number of merges to the single county ORIs are:")
    print(sum(raw_final_weight_original_only1_final$in_main_data, na.rm = TRUE))   
    
    #Delete the tbd datasets
    rm(list=ls(pattern="tbd_"))
    invisible(gc())
    
    #Dataset to use:  raw_final_weight_original_only1_final
    
    #Next process the raw_final_weight_original_mt1 dataset
    
    #Using raw_final_weight_original_mt1 do the processing the county variable for better merges
    
    tbd_good_1 <- raw_final_weight_original_mt1 %>%
      inner_join(indata, by=c("ORI", "county")) %>%
      #Create an indicator variable
      mutate(in_main_data = 1)      
    
    tbd_bad_1 <- raw_final_weight_original_mt1 %>%
      anti_join(indata, by=c("ORI", "county"))
    
    #Stack the data together
    raw_final_weight_original_mt1_final <- bind_rows(tbd_good_1, tbd_bad_1)
    
    print(log_dim(raw_final_weight_original_mt1_final))
    print(log_dim(raw_final_weight_original_mt1))
    print(log_dim(tbd_good_1))
    print(log_dim(tbd_bad_1))
    
    #Check the merge
    print("The number of multi-county ORIs in the variance dataset are:")
    print(nrow(raw_final_weight_original_mt1))       
    
    print("The number of merges to the multi-county ORIs are:")
    print(sum(raw_final_weight_original_mt1_final$in_main_data, na.rm = TRUE))       
    
    
    #Delete the tbd datasets
    rm(list=ls(pattern="tbd_"))
    invisible(gc())
    
    #Stack the two datasets together raw_final_weight_original_only1_final and raw_final_weight_original_mt1_final to have all the information on one dataset
    
    final_weight <- bind_rows(raw_final_weight_original_only1_final, 
                              raw_final_weight_original_mt1_final
    )

    #Make sure the datasets have the same amount of rows
    print(log_dim(final_weight))
    print(log_dim(raw_final_weight_original))
    print(log_dim(indata))
    
    #Check the merge
    print("The number of pseudo-ORIs in the variance dataset are:")
    print(nrow(raw_variance))   
    
    print("The number of pseudo-ORIs in the copula dataset are:")
    print(nrow(indata))       
    
    print("The number of merges overall are:")
    print(sum(final_weight$in_main_data, na.rm = TRUE))         
    
    #Final dataset to use is final_weight for the weights
    rm(list=ls(pattern="raw_final_"))
    invisible(gc())
    
    #Need to create the returndata object
    returndata <- final_weight  %>%
      #Drop the NATIONAL weight variable
      select(-weight) 

    print("The number of merges to the variance dataset are:")
    print(sum(returndata$in_main_data, na.rm = TRUE))
  } else{

    #Do the merge
    tbd_good_1 <- raw_variance %>%
      inner_join(indata , by=c("ori")) %>%									 
      #Create an indicator variable
      mutate(in_main_data = 1)
    
    tbd_bad_1 <- raw_variance %>%
      anti_join(indata , by=c("ori"))    
    
    #Stack the data together
    tbd_final <- bind_rows(tbd_good_1, tbd_bad_1)
    
    print(log_dim(tbd_final))
    print(log_dim(raw_variance))
    print(log_dim(tbd_good_1))
    print(log_dim(tbd_bad_1))    
    
    #Check to see if the number of merges are good
    print("The number of pseudo-ORIs in the variance dataset are:")
    print(nrow(raw_variance))           
    
    print("The number of ORIs in the single level ori dataset are:")
    print(nrow(indata))           
    
    print("The number of unique ORIs merge to the variance dataset are:")
    print( nrow( tbd_good_1 %>% distinct(ori) %>% as_tibble()))           
    
    #Create the returndata
    returndata <- tbd_final %>%
      #Drop the NATIONAL weight variable
      select(-weight) 
	  
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
    as.data.frame() %>%
    #Make sure the variable is a match to the pattern name
    filter(!is.na(V1)) %>%
    #Make the derived variables from variable name
    select(V1) %>%
    pull() 

  #Code the missings as 0
  # for(i in 1:length(raw_selected_vars)){
  # 
  #   #Select the current variables
  #   invar <- raw_selected_vars[[i]]
  # 
  #     returndata <- returndata %>%
  #     #Add code to make sure it is a double
  #     mutate(!!invar := as.double(!!invar)) %>%
  #     mutate(!!invar := case_when(is.na(!!invar) ~ 0,
  #                                 TRUE ~ !!invar
  #   ))
  # }
  
  setnafill(returndata, cols = raw_selected_vars, fill = 0)

  #Return the data
  return(returndata)
}


#Next need to read in the population file
#Get the population total files and create variables
pop_data <- read_csv(paste0(pop_file_path, "POP_TOTALS_PERM_", CONST_YEAR, "_FINAL.csv"))

#Need to get list of csv output to compute PRB
copula_file_name = paste0("Table_",table,"_Final_Agency_File_Perm_",copula_perm,"_Rates_PARENT_POP_GROUP_CODE2.csv")

#Save the current path
#raw_file <- .x
raw_file <- file.path(input_copula_data_folder,copula_file_name)

#Get the initial variable types
raw_variable_specs <- spec_csv(file=raw_file)

#Get the variable names <- Okay to have parsing errors
raw_variable_types <- fread(file=raw_file) %>%
  #Get variable names
  colnames() %>%
  #Change to a dataset
  as_tibble()


raw_variable_types2 <-raw_variable_types %>%
  #Identify the variables that corresponds to the id of the table cells
  mutate(
    der_table_string = str_match(.$value, pattern="t_\\w+_\\d+_\\d+_\\d+")) %>%
  #Subset to matches only
  filter(!is.na(der_table_string[,1])) %>%
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
raw_main <- tibble::as_tibble(fread(file=raw_file, colClasses = raw_variable_specs)) %>%
  mutate(
    old_county = county,
    county = as.numeric(old_county))
 
raw_main %>% checkfunction(old_county, county)  


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

#Get the t variables of interest
needed_vars <- colnames(main_copula) %>%
  str_match(pattern=DER_TABLE_PATTERN_STRING) %>%
  as.data.frame() %>%
  filter(!is.na(V1)) %>%   #Make the derived variables from variable name
  mutate(variable_name = V1,
         table = V2,
         section = as.numeric(V3),
         row = as.numeric(V4),
         column = as.numeric(V5)) %>%
  select(-V1,-V2,-V3,-V4,-V5) %>%
  filter(row != 999) %>%
  select(variable_name) %>%
  pull()

log_dim(raw_main)
log_dim(main_copula)

#NEW:  Need to run this for the weighted estimates using the original ORI file
#NEW:  Determine if demographic table or not
#Note:  DER_DEFINE_DEMO_TABLES has all the demographic tables, perm is the current permutation number

#If this is a demo table then choose the correct file to use
if(table %in% DER_DEFINE_DEMO_TABLES){
  
  tbd_current_perm = find_demo_table_num(inperm=perm)
  
  log_debug("Using the demographic version of the ", "Table ", table, " ORI_",tbd_current_perm ,".csv.gz")
  
  raw_weighted <- tibble::as_tibble(fread(paste0(der_file_indicator_table_estimates_path, "Table ", table, " ORI_",tbd_current_perm ,".csv.gz"), 
                                          select = c(needed_vars, "ori","weight")))  
  
  
}else{
  
  log_debug("Using the normal ", "Table ", table, " ORI.csv.gz")	
  
raw_weighted <- tibble::as_tibble(fread(paste0(der_file_indicator_table_estimates_path, "Table ", table, " ORI.csv.gz"), 
                                        select = c(needed_vars, "ori","weight")))  

 }

 
main_weighted <- merge_on_weights_variance_new_for_bias(raw_weighted, incounty=0)

log_dim(raw_weighted)
log_dim(main_weighted)

#Next step is to use the dataset main and calculate the PRBs

#Create a vector to hold the variables
#Need to switch to main_weighted, since copula have some of the t_table_section_999_column variables created that is not on the main dataset																																			
get_raw_variables <- function(indata){

  #Get the t variables of interest
  returndata <- colnames(indata) %>%
  str_match(pattern=DER_TABLE_PATTERN_STRING) %>%
  as.data.frame() %>%
  filter(!is.na(V1)) %>%   #Make the derived variables from variable name
  mutate(variable_name = V1,
         table = V2,
         section = as.numeric(V3),
         row = as.numeric(V4),
         column = as.numeric(V5)) %>%
  select(-V1,-V2,-V3,-V4,-V5)
  
  #Return the data
  return(returndata)
  
}

#Get the variables
raw_variable_list_copula <- get_raw_variables(indata=main_copula)   %>% select(variable_name)
raw_variable_list_main   <- get_raw_variables(indata=main_weighted) %>% select(variable_name)

#Get the common list of variables
raw_variable_list <- raw_variable_list_copula %>%
  inner_join(raw_variable_list_main, by="variable_name") %>%
  select(variable_name) %>%
  pull()

raw_variable_list_copula_only <- raw_variable_list_copula %>%
  anti_join(raw_variable_list_main, by="variable_name") %>%
  select(variable_name) %>%
  pull()

#See the dimension
print("The number of variables in copula is:")
print(nrow(raw_variable_list_copula))

print("The number of variables in single ori is:")
print(nrow(raw_variable_list_main))

print("The number of common variables between copula and single ori is:")
print(length(raw_variable_list))

print("See the variables that are in copula only:")
print(raw_variable_list_copula_only)

main_copula_sub <- main_copula %>%
  select(all_of(raw_variable_list))
main_weighted_sub <-main_weighted %>%
  select(all_of(c("weight",raw_variable_list))) %>%
  mutate(across(all_of(raw_variable_list), ~weight*.)) %>%
  select(-weight)

# unweighted sums
unweighted_counts <- colSums(main_copula_sub, na.rm=TRUE)
unweighted_counts_df <- data.frame(variable_name = names(main_copula_sub), der_unweighted_counts = unweighted_counts)

row.names(unweighted_counts_df) <- NULL

# weighted sums
weighted_counts <- colSums(main_weighted_sub, na.rm=TRUE)
weighted_counts_df <- data.frame(variable_name = names(main_weighted_sub), der_weighted_counts = weighted_counts)

row.names(weighted_counts_df) <- NULL

#Bind the datasets together
final_imputed_prb <- unweighted_counts_df %>%
  inner_join(weighted_counts_df) %>%
#Create the percent relative bias
mutate(percent_relative_bias_imputed = case_when(
  der_weighted_counts > 0 ~ ((der_weighted_counts - der_unweighted_counts) / der_weighted_counts )*100),
  permutation_number = raw_permutation_num)


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
"main_weighted",
"main_copula_sub",
"main_weighted_sub"
))
invisible(gc())

log_debug("Finishing...")
log_debug(system("free -mh", intern = FALSE))
