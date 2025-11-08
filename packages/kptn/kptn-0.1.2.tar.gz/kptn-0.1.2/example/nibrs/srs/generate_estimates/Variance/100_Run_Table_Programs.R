library("rmarkdown")
library("tidyverse")
library("rjson")

#Read in the common functions to be used in R
source(here::here("tasks/logging.R"))
source(here::here("tasks/impute_items/0-Common_functions_for_imputation.R"))

# update connection buffer for reading new larger table data
Sys.setenv(VROOM_CONNECTION_SIZE=500072*2)

#input/output directories for pipeline artifacts
outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")
inputPipelineDir <- Sys.getenv("INPUT_PIPELINE_DIR")
external_path <- Sys.getenv("EXTERNAL_FILE_PATH")

filepathout = paste0(outputPipelineDir, "/srs/markdown/") #output path for markdown files

if (! dir.exists(filepathout)) {
  dir.create(filepathout, recursive = TRUE)
}

der_file_path = paste0(outputPipelineDir, "/srs/indicator_table_extracts/") #output path for all the data extracts

if (! dir.exists(der_file_path)) {
  dir.create(der_file_path, recursive = TRUE)
}

final_path_after_variance = paste0(outputPipelineDir, "/srs/indicator_table_estimates_after_variance/") #this is where the final estimates go
if (! dir.exists(final_path_after_variance)) {
  dir.create(final_path_after_variance, recursive = TRUE)
}

final_path = paste0(outputPipelineDir, "/srs/indicator_table_estimates/") #this is where the final estimates go

if (! dir.exists(final_path)) {
  dir.create(final_path, recursive = TRUE)
}

file_switch_to_design = paste0(outputPipelineDir, "/srs/variance_switch/") #output path for log files that switch from calibrated to design based

if (! dir.exists(file_switch_to_design)) {
  dir.create(file_switch_to_design, recursive = TRUE)
}

file_skip_variance = paste0(outputPipelineDir, "/srs/variance_skip/") #output path for log files that skip running the variance programs

if (! dir.exists(file_skip_variance)) {
  dir.create(file_skip_variance, recursive = TRUE)
}


input_copula_prb_folder <- file.path(inputPipelineDir,"/srs/copula_imputation", "PRB")

#External files json
input_folder <- sprintf("%s", inputPipelineDir)
file_locs <- fromJSON(file = sprintf("%s/external_file_locations.json", input_folder))

#set-up year
CONST_YEAR <- Sys.getenv("DATA_YEAR")

DER_CURRENT_PERMUTATION_NUM <- Sys.getenv("DER_CURRENT_PERMUTATION_NUM")
DER_TABLE <- Sys.getenv("TABLE_NAME")
log_info(paste0("Running permuation ",DER_CURRENT_PERMUTATION_NUM," and table ",DER_TABLE))

#pull the number of ORIs for the current permutation
#num_der_oris <- file.path(external_path,file_locs[[CONST_YEAR]]$population) %>%
#  read_csv() %>% filter(PERMUTATION_NUMBER == DER_CURRENT_PERMUTATION_NUM) %>%
#  select(NUMBER_OF_ELIGIBLE_ORIS) %>%
#  pull()
  
#For this run use the following file 
  num_der_oris <- fread(paste0(outputPipelineDir, "/srs/weighting/Data/POP_TOTALS_PERM_", CONST_YEAR, "_FINAL_SRS.csv") ) %>% 
  filter(PERMUTATION_NUMBER == DER_CURRENT_PERMUTATION_NUM) %>%
  select(NUMBER_OF_ELIGIBLE_ORIS) %>%
  pull()


source("../POP_Total_code_assignment.R")
subset_variance <- fread(paste0(der_file_path, DER_ORI_VARIANCE_FILE)) %>% 
  filter(!!DER_PERMUTATION_SUBSET_SYMBOL)

#######################Note if the table name is SRS1araw, then need to use SRS1a for the check#######################

if(DER_TABLE == "SRS1araw"){
  log_debug("Switch from SRS1araw to SRS1a")
  DER_TABLE_NAME_CHECK <- "SRS1a"
} else {
  DER_TABLE_NAME_CHECK <- DER_TABLE
}

#Next read in the single level ORI file
single_level_ori_file <- fread(paste0(final_path, "Table ", DER_TABLE_NAME_CHECK, " ORI.csv.gz"))

#Using subset_variance and single_level_ori_file check to see if there are any agencies in the two files
#If yes then run the program, if not then skip
single_level_ori_file2 <- subset_variance %>%
  select(ori) %>% 
  inner_join(single_level_ori_file %>%
              select(ori), by=c("ori")) 

#we need to create a sum of the appropriate weight to check if everyone is non-respondents
wtsums <- subset_variance %>% 
  filter(!is.na(ori)) %>% 
  summarise(wgtsum = sum(!!DER_WEIGHT_VARIABLE_SYMBOL, na.rm = TRUE))

table_programs <- list.files(here::here("srs/generate_estimates/Variance/"), pattern = "*.Rmd")

TABLE_PROGRAM <- table_programs %>%
  as.data.frame() %>%
  filter(grepl(paste0("Table", DER_TABLE, "_"), `.`) == TRUE) %>%
  pull()

#Run if more than 0 ORIs & at least one respondent
if (num_der_oris >0 && !(all( is.na(subset_variance$ori) )) && wtsums$wgtsum > 0 && nrow(single_level_ori_file2) > 0 ) {
  rmarkdown::render(
    TABLE_PROGRAM,
    output_format = html_document(),
    output_file = paste0(filepathout, TABLE_PROGRAM, "_", DER_CURRENT_PERMUTATION_NUM, ".html"),
    envir = new.env(),
    quiet = TRUE
  )
} else {
  print("Permutation has no agencies. Skipping....")
  
  #Write out a file to indicate skip
  paste0("") %>%
    as_tibble() %>%
    write_csv(paste0(file_skip_variance, "/", Sys.getenv("DER_CURRENT_PERMUTATION_NUM"), "_",  Sys.getenv("TABLE_NAME"), ".csv"))
}
