library(tidyverse)
library(openxlsx)
library(readxl)
library(DT)

library("rjson")

#Read in the common functions to be used in R
source(here::here("tasks/logging.R"))
source(here::here("tasks/impute_items/0-Common_functions_for_imputation.R"))

read_csv_quick <- partial(read_csv, guess_max = 100) #For now, read thru the 1st 1,000,000 rows to determine variable type
read_csv <- partial(read_csv, guess_max = 10000) #For now, read thru the 1st 1,000,000 rows to determine variable type
write.csv0 <- partial(write.csv, row.names = FALSE, na ="0")
write.csv <- partial(write.csv, row.names = FALSE, na ="")

DER_TABLE_PATTERN_STRING = "t_(\\w+)_(\\d+)_(\\d+)_(\\d+)"

#input/output directories for pipeline artifacts
outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")
inputPipelineDir <- Sys.getenv("INPUT_PIPELINE_DIR")
external_path <- Sys.getenv("EXTERNAL_FILE_PATH")

single_path = paste0(inputPipelineDir, "/indicator_table_estimates/") #this is where the reporting dbs are
input_copula_prb_folder <- file.path(inputPipelineDir,"copula_imputation", "PRB")
output_copula_prb_folder <- file.path(outputPipelineDir,"copula_imputation", "PRB")

if (! dir.exists(output_copula_prb_folder)) {
  dir.create(output_copula_prb_folder, recursive = TRUE)
}

#set-up year
CONST_YEAR <- Sys.getenv("DATA_YEAR")
CONST_TABLE <- trimws(Sys.getenv("TABLE_NAME"))
perm <- Sys.getenv("DER_CURRENT_PERMUTATION_NUM") %>% as.numeric()
geo_perm <- perm %% 1000

log_info("Running 03_Generate_PRB_Copula_2.R")
log_debug(system("free -mh", intern = FALSE))

#Need to get list of csv output to compute PRB
#raw_list_files <- list.files(path=paste0(input_copula_prb_folder), pattern="PRB_\\w+_Final_Agency_File_Perm_\\d+.csv.gz" )
raw_list_files <- paste0("PRB_", CONST_TABLE, "_Final_Agency_File_Perm_", perm,  ".csv.gz" )

print(raw_list_files)
#Compile the list
tbd_list <- map(raw_list_files, ~{

  #Get the initial file
  raw_file <- .x

  return(read_csv(gzfile(file.path(input_copula_prb_folder,raw_file))))

})

#Combine the list together
tbd_final <- tbd_list %>%
  #Combine the data together
  bind_rows() %>%
  #Do some rename to match the PRB dataset
  rename(percent_relative_bias=percent_relative_bias_imputed,
         der_all_counts=der_unweighted_counts) %>% #Want the "all" agencies count - This is new for Copula
  #Create new variable
  mutate(PRB_ACTUAL = percent_relative_bias)

#Need to add on the variable info
tbd_vars <-tbd_final %>%
  select(variable_name) %>%
  #Deduplicate
  group_by(variable_name) %>%
  mutate(raw_first = row_number() == 1 ) %>%
  ungroup() %>%
  filter(raw_first == TRUE) %>%
  #Get the unique variable names
  select(variable_name) %>%
  pull()


tbd_vars <-  str_match(string=tbd_vars, pattern=DER_TABLE_PATTERN_STRING) %>%
          as_tibble() %>%
          filter(!is.na(V1)) %>%   #Make the derived variables from variable name
          mutate(variable_name = V1,
                 table = V2,
                 section = as.numeric(V3),
                 row = as.numeric(V4),
                 column = as.numeric(V5)) %>%
          select(-V1,-V2,-V3,-V4,-V5)

tbd_final2 <- tbd_final %>%
  left_join(tbd_vars, by=c("variable_name"))

log_dim(tbd_final2)
log_dim(tbd_final)
log_dim(tbd_vars)

#Next need to create new column variable to handle the demographic permutations
tbd_final3 <- tbd_final2 %>%
  rename(old_column = column) %>%
  mutate(column = old_column %% 1000)

tbd_final3 %>%
  checkfunction(column, old_column)

# make the template
load(paste0(output_copula_prb_folder, "/all_table_details_PRB.RData"))

# geography
raw_geography_perm <- read_xlsx(path = file.path("Data", "Permutation for Indicator Tables.xlsx")) %>%
  filter(!is.na(permutation_number) ) %>%
  select(permutation_number, permutation_number_desc, code_for_subset) 

# demographics
raw_demographic_perm <- read_xlsx(path = file.path("Data", "Demo Permutation for Indicator Tables.xlsx")) %>%
  filter(!is.na(permutation_series_add) ) %>%
  select(permutation_series_add,	permutation_series_add_desc,	code_subset)

#Create some geographic permutation information
invarlabelsym <- raw_geography_perm %>% filter(permutation_number == geo_perm) %>% select(permutation_number_desc) %>% pull()  %>% as.character()
incode_for_subset <- raw_geography_perm %>% filter(permutation_number == geo_perm) %>% select(code_for_subset) %>% pull()  %>% as.character()

# make template
if (perm < 1000) { # non-demo
  # finalize the template
  tbd_template <- raw_main6 %>%
    filter(table == CONST_TABLE) %>%
    mutate(permutation_number = perm,
           permutation_number_desc = invarlabelsym,
           permutation_number_code = incode_for_subset) %>%
    select(permutation_number, permutation_number_desc, permutation_number_code,
           variable, table, full_table, section, row, estimate_domain, estimate_domain_num,
           column, indicator_name, indicator_name_clean, indicator_name_num) %>%
    mutate(percent_relative_bias = NA_real_) 
} else {
  demo <- perm - (perm %% 1000)
  invardemolabel <- raw_demographic_perm %>% filter(permutation_series_add == demo) %>% select(permutation_series_add_desc) %>% pull() %>% as.character()
  
  # some additional demo information
  tbd_template <- raw_main6 %>%
    filter(table == CONST_TABLE) %>%
    mutate(permutation_number = perm,
           permutation_number_desc = paste0(invardemolabel, " ", invarlabelsym),
           permutation_number_code = incode_for_subset) %>%
    select(permutation_number, permutation_number_desc, permutation_number_code,
           variable, table, full_table, section, row, estimate_domain, estimate_domain_num,
           column, indicator_name, indicator_name_clean, indicator_name_num) %>%
    mutate(percent_relative_bias = NA_real_) 
}

#Merge on the data
tbd_final4 <- tbd_template %>%
  #Drop the blank variable from template
  select(-percent_relative_bias) %>%
  left_join(tbd_final3, by=c("permutation_number", "table", "section", "row", "column"))

log_dim(tbd_final4)
log_dim(tbd_template)
log_dim(tbd_final3)

#Double check there is no problem cases
tbd_problem <- tbd_final3 %>%
  anti_join(tbd_template, by=c("permutation_number", "table", "section", "row", "column"))

#Okay if rows are 999
tbd_problem %>%
  checkfunction(permutation_number, variable_name, row)

#Output the dataset
Relative_Bias_Estimates_Final <- tbd_final4 %>%
  select(permutation_number, table, section, row, column, percent_relative_bias, PRB_ACTUAL, der_all_counts)

#Output file
#save(Relative_Bias_Estimates_Final, file=file.path(output_copula_prb_folder, "Relative_Bias_Estimates_Final.Rdata") )
Relative_Bias_Estimates_Final %>%
	write_rds(paste0(output_copula_prb_folder, "/Relative_Bias_Estimates_", CONST_TABLE, "_", perm , ".rds"), compress = "gz")

log_debug("Finishing...")
log_debug(system("free -mh", intern = FALSE))
