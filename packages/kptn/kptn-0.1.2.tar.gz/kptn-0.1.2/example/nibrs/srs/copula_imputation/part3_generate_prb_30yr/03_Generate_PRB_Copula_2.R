library(tidyverse)
library(openxlsx)
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

input_copula_prb_folder <- file.path(inputPipelineDir,"srs","copula_imputation", "PRB")
output_copula_prb_folder <- file.path(outputPipelineDir,"srs","copula_imputation", "PRB")

if (! dir.exists(output_copula_prb_folder)) {
  dir.create(output_copula_prb_folder, recursive = TRUE)
}

#set-up year
CONST_YEAR <- Sys.getenv("DATA_YEAR")
table <- trimws(Sys.getenv("TABLE_NAME"))
perm <- Sys.getenv("DER_CURRENT_PERMUTATION_NUM") %>% as.numeric()

log_info("Running 03_Generate_PRB_Copula_2.R")
log_debug(system("free -mh", intern = FALSE))

#Need to get list of csv output to compute PRB
#raw_list_files <- list.files(path=paste0(input_copula_prb_folder), pattern="PRB_\\w+_Final_Agency_File_Perm_\\d+.csv.gz" )
raw_list_files <- paste0("PRB_", table, "_Final_Agency_File_Perm_", perm,  ".csv.gz" )


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
#Next need to bring in the template
#tbd_template <- read_csv(file.path(output_copula_prb_folder, "Relative_Bias_Output.csv.gz"))
tbd_template <- readRDS(paste0(output_copula_prb_folder, "/temp_prb_", table, "_", perm, ".rds"))

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
	write_rds(paste0(output_copula_prb_folder, "/Relative_Bias_Estimates_", table, "_", perm , ".rds"), compress = "gz")


log_debug("Finishing...")
log_debug(system("free -mh", intern = FALSE))
