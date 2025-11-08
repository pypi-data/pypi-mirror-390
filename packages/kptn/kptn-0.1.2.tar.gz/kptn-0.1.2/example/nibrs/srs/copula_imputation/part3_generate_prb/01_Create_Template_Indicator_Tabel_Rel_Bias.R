library(tidyverse)
library(openxlsx)
library(readxl)
library(DBI)
library(DT)
library(lubridate)

#Read in the common functions to be used in R
source(here::here("tasks/logging.R"))
source(here::here("tasks/impute_items/0-Common_functions_for_imputation.R"))

#input/output directories for pipeline artifacts
outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")
inputPipelineDir <- Sys.getenv("INPUT_PIPELINE_DIR")

single_path = paste0(inputPipelineDir, "/srs/indicator_table_estimates/") #this is where the final estimates go

output_copula_folder <- file.path(outputPipelineDir, "srs", "copula_imputation")
output_copula_prb_folder <- file.path(output_copula_folder, "PRB")

if (! dir.exists(output_copula_prb_folder)) {
  dir.create(output_copula_prb_folder, recursive = TRUE)
}

#Read in the common functions to be used in R
read_csv <- partial(read_csv, guess_max = 1000000) #For now, read thru the 1st 1,000,000 rows to determine variable type
write.csv0 <- partial(write.csv, row.names = FALSE, na ="0")
write.csv <- partial(write.csv, row.names = FALSE, na ="")

#Create function to process the output
processtempprb <- function(indata){
  
  #Select the variables
  returdata <- indata %>%
    select(permutation_number, permutation_number_desc, permutation_number_code,
           variable,
           table, full_table,
           section, row, estimate_domain, estimate_domain_num,
           column, indicator_name, indicator_name_clean, indicator_name_num
    ) %>%
    mutate(percent_relative_bias = NA_real_)
  
  #Return the data
  return(returdata)

}

log_info("Running 01_Create_Template_Indicator_Tabel_Rel_Bias.R")
log_debug(system("free -mh", intern = FALSE))
#Get the Table x_Reporting_Database.csv files
raw_list_of_files <- list.files(path=single_path, pattern = "\\w+_Reporting_Database.csv$")

raw_main <- vector("list", length(raw_list_of_files))

for(i in 1:length(raw_list_of_files)){

  raw_main[[i]] <- read_csv(paste0(single_path, raw_list_of_files[[i]])) %>% mutate(
    estimate_type_detail_rate = as.character(estimate_type_detail_rate),
    variable = paste0("t_", table,"_", section, "_", row, "_", column)

  )


}

#Combine the files
raw_main2 <- raw_main %>%
  bind_rows()

#Deplicate since there are 3 version for type of estimates (i.e. counts, rates, percentages)
raw_main3 <- raw_main2 %>%
  filter(estimate_type_num == 1)

log_dim(raw_main2)
log_dim(raw_main3)

#See the unique levels of estimate_domain
#Appears to be no issue with deduplicates in terms of white spaces
raw_main3 %>%
  checkfunction(estimate_domain)

#Create numeric version of estimate_domain
raw_main3_categories <- raw_main3 %>%
  group_by(estimate_domain) %>%
  mutate(raw_first = row_number() ) %>%
  ungroup() %>%
  filter(raw_first == TRUE) %>%
  mutate(estimate_domain_num = row_number() ) %>%
  select(estimate_domain, estimate_domain_num)

#Check the recodes
raw_main3_categories %>%
  checkfunction(estimate_domain, estimate_domain_num)

raw_main4 <- raw_main3 %>%
  left_join(raw_main3_categories, by="estimate_domain")

log_dim(raw_main3)
log_dim(raw_main4)

raw_main4 %>%
  checkfunction(estimate_domain, estimate_domain_num)

#Next clean up the indicator_name
#Need to clean up some labels
raw_main4 %>%
  checkfunction(indicator_name)

raw_main5 <- raw_main4 %>%
  mutate(
    indicator_name_clean = indicator_name
    # indicator_name_clean = case_when(
    # indicator_name == "Counterfeiting/forgery" ~ "Counterfeiting/Forgery",
    # indicator_name == "Human Trafficking- Labor" ~  "Human Trafficking-Labor",
    # indicator_name == "Human Trafficking- Sex" ~  "Human Trafficking-Sex",
    # TRUE ~ indicator_name
)

raw_main5 %>%
  checkfunction(indicator_name_clean, indicator_name)

raw_main5_categories <- raw_main5 %>%
  group_by(indicator_name_clean) %>%
  mutate(raw_first = row_number() ) %>%
  ungroup() %>%
  filter(raw_first == TRUE) %>%
  mutate(indicator_name_num = row_number() ) %>%
  select(indicator_name_clean, indicator_name_num)

raw_main5_categories %>%
  checkfunction(indicator_name_clean, indicator_name_num)

raw_main6 <- raw_main5 %>%
  left_join(raw_main5_categories, by="indicator_name_clean")

log_dim(raw_main5)
log_dim(raw_main6)

raw_main6 %>%
  checkfunction(indicator_name_clean, indicator_name_num)


#Next to do the permutations
#Read in the following spreadsheet:  Permutation for Indicator Tables
raw_indicator_table_perm <- read_xlsx(path = file.path("Data", "Permutation for Indicator Tables.xlsx")) %>%
  filter(!is.na(permutation_number) ) %>%
  select(permutation_number, permutation_number_desc, code_for_subset)


#Need to output the template prb shells

#Need to get list of final tables
CONST_ALL_TABLES <- raw_main6 %>%
  distinct(table) %>%
  pull()

#See the tables
print(CONST_ALL_TABLES)

#Get the permutation number
CONST_ALL_GEO_PERM <- raw_indicator_table_perm %>%
  distinct(permutation_number) %>%
  pull()

#See the permutations
print(CONST_ALL_GEO_PERM)


#Create a cross between table and permutation number
RAW_CONST_ALL_GEO_TABLE_PERM <- expand_grid(CONST_ALL_GEO_PERM,  CONST_ALL_TABLES) %>%
  #Need to only do permutation 1 on "SRS2a" only
  mutate(der_keep = fcase(
    trim_upper(CONST_ALL_TABLES) %in% c("SRS2A") & CONST_ALL_GEO_PERM > 1, 0, #Keep only permutation 1 for SRS2a
    default = 1 #Keep the remaining tables to do all geographic permutations
  ))


#Keep the permutations of interest
CONST_ALL_GEO_TABLE_PERM <- RAW_CONST_ALL_GEO_TABLE_PERM %>%
  filter(der_keep == 1)

#Need to loop thru and create all the template table shells

map2(.x=CONST_ALL_GEO_TABLE_PERM$CONST_ALL_GEO_PERM, .y = CONST_ALL_GEO_TABLE_PERM$CONST_ALL_TABLES, ~ {
  
  #Read in the current row from the raw_indicator_table_perm table
  tbd_current_row_perm_table <- raw_indicator_table_perm %>% 
    filter(permutation_number == .x) 
  
  #Create the symbol
  invarsym          <- tbd_current_row_perm_table %>% select(permutation_number) %>% pull() %>% as.numeric()
  invarlabelsym     <- tbd_current_row_perm_table %>% select(permutation_number_desc) %>% pull()  %>% as.character()
  incode_for_subset <- tbd_current_row_perm_table %>% select(code_for_subset) %>% pull()  %>% as.character()
  
  #Using dataset raw_main6 that contains all tables, filter by table 
  tbd_1 <- raw_main6 %>%
    filter(table == .y) %>%
    mutate(permutation_number = invarsym,
           permutation_number_desc = invarlabelsym,
           permutation_number_code = incode_for_subset
    ) 
  #Run thru the function to finish processing  
  tbd_2 <- tbd_1 %>%
    processtempprb()
  
  #Output the template database
  tbd_2 %>%
    write_rds(paste0(output_copula_prb_folder, "/temp_prb_", .y, "_", .x, ".rds"), compress = "gz")
  
  #Remove the objects
  rm(tbd_current_row_perm_table, invarsym, invarlabelsym, incode_for_subset, tbd_1, tbd_2)
  
  
} )


log_debug("Finishing...")
log_debug(system("free -mh", intern = FALSE))
