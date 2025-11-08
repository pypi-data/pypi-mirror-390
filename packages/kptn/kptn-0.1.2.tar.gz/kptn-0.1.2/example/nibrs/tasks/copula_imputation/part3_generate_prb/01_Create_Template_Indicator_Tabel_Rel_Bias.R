library(tidyverse)
library(openxlsx)
library(readxl)
library(DBI)
library(DT)
library(lubridate)

#Read in the common functions to be used in R
source(here::here("tasks/logging.R"))
source(here::here("tasks/impute_items/0-Common_functions_for_imputation.R"))
source("../../generate_estimates/Demo_Tables_Func.R")										 

#input/output directories for pipeline artifacts
outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")
inputPipelineDir <- Sys.getenv("INPUT_PIPELINE_DIR")

single_path = paste0(inputPipelineDir, "/indicator_table_estimates/") #this is where the final estimates go

output_copula_folder <- file.path(outputPipelineDir, "copula_imputation")
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
  mutate(indicator_name_clean = case_when(
    indicator_name == "Counterfeiting/forgery" ~ "Counterfeiting/Forgery",
    indicator_name == "Human Trafficking- Labor" ~  "Human Trafficking-Labor",
    indicator_name == "Human Trafficking- Sex" ~  "Human Trafficking-Sex",
    TRUE ~ indicator_name
))

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

# save the table details 
save(raw_main6, file=paste0(output_copula_prb_folder, "/all_table_details_PRB.RData"))
