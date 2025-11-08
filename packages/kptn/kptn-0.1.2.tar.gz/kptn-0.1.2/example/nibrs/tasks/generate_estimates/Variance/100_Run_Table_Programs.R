library("rmarkdown")
library("tidyverse")
library("rjson")

#Read in the common functions to be used in R
source(here::here("tasks/logging.R"))
source(here::here("tasks/impute_items/0-Common_functions_for_imputation.R"))
source("../Demo_Tables_Func.R")

# Print traceback when unhandled error occurs
# (We should move this to a global file if it works well)
options(keep.source = TRUE, error=function(){traceback(2,max.lines=3);if(!interactive())quit("no",status=1,runLast=FALSE)})

# update connection buffer for reading new larger table data
Sys.setenv(VROOM_CONNECTION_SIZE=500072*7)

#input/output directories for pipeline artifacts
outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")
inputPipelineDir <- Sys.getenv("INPUT_PIPELINE_DIR")
external_path <- Sys.getenv("EXTERNAL_FILE_PATH")

filepathout = paste0(outputPipelineDir, "/markdown/") #output path for markdown files
filepathin_initial = paste0(inputPipelineDir, "/initial_tasks_output/")

if (! dir.exists(filepathout)) {
  dir.create(filepathout, recursive = TRUE)
}

der_file_path = paste0(outputPipelineDir, "/indicator_table_extracts/") #output path for all the data extracts

if (! dir.exists(der_file_path)) {
  dir.create(der_file_path, recursive = TRUE)
}

final_path_after_variance = paste0(outputPipelineDir, "/indicator_table_estimates_after_variance/") #this is where the final estimates go
if (! dir.exists(final_path_after_variance)) {
  dir.create(final_path_after_variance, recursive = TRUE)
}

final_path = paste0(outputPipelineDir, "/indicator_table_estimates/") #this is where the final estimates go

if (! dir.exists(final_path)) {
  dir.create(final_path, recursive = TRUE)
}

file_switch_to_design = paste0(outputPipelineDir, "/variance_switch/") #output path for log files that switch from calibrated to design based

if (! dir.exists(file_switch_to_design)) {
  dir.create(file_switch_to_design, recursive = TRUE)
}

file_skip_variance = paste0(outputPipelineDir, "/variance_skip/") #output path for log files that skip running the variance programs

if (! dir.exists(file_skip_variance)) {
  dir.create(file_skip_variance, recursive = TRUE)
}


input_copula_prb_folder <- file.path(inputPipelineDir,"copula_imputation", "PRB")

#External files json
input_folder <- sprintf("%s", inputPipelineDir)
file_locs <- fromJSON(file = sprintf("%s/external_file_locations.json", input_folder))

#set-up year
CONST_YEAR <- Sys.getenv("DATA_YEAR")

DER_CURRENT_PERMUTATION_NUM <- Sys.getenv("DER_CURRENT_PERMUTATION_NUM")
DER_TABLE <- Sys.getenv("TABLE_NAME")
log_info(paste0("Running permuation ",DER_CURRENT_PERMUTATION_NUM," and table ",DER_TABLE))

#pull the number of ORIs for the current permutation
#num_der_oris <- paste0(filepathin_initial, "POP_TOTALS_PERM_", CONST_YEAR, ".csv") %>%
#  read_csv() %>% filter(PERMUTATION_NUMBER == DER_CURRENT_PERMUTATION_NUM) %>%
#  select(NUMBER_OF_ELIGIBLE_ORIS) %>%
#  pull()
  
#For this run use the following file 
num_der_oris <- fread(paste0(outputPipelineDir, "/weighting/Data/POP_TOTALS_PERM_", CONST_YEAR, "_FINAL.csv") ) %>% 
  filter(PERMUTATION_NUMBER == DER_CURRENT_PERMUTATION_NUM) %>%
  select(NUMBER_OF_ELIGIBLE_ORIS) %>%
  pull()


source("../POP_Total_code_assignment.R", keep.source = TRUE)
source("../POP_create_percentage_denominator.R", keep.source = TRUE)
source("./variance_final_processing.R", keep.source = TRUE)
subset_variance <- fread(paste0(der_file_path, DER_ORI_VARIANCE_FILE)) %>% 
  filter(!!DER_PERMUTATION_SUBSET_SYMBOL)

#Need to read in the Single level ORI file to make sure that that there are agencies that reports incident
#Next read in the single level ORI file
#single_level_ori_file <- fread(paste0(final_path, "Table ", DER_TABLE_NAME_CHECK, " ORI.csv.gz"))
single_level_ori_file <- process_single_ori_tables(intable=DER_TABLE, 
                                                   inpermutation=DER_CURRENT_PERMUTATION_NUM, 
                                                   infilepath=final_path)

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

# we need to get the name of the program to run
table_programs <- list.files(here::here("tasks/generate_estimates/Variance"), pattern = "*.R")

TABLE_PROGRAM <- table_programs %>%
  as.data.frame()%>%
  filter(grepl(paste0("Table",DER_TABLE, "_"), `.`) == TRUE) %>%
  pull()

#Run if more than 0 ORIs & at least one respondent
if (num_der_oris >0 && !(all( is.na(subset_variance$ori) )) && wtsums$wgtsum > 0 && nrow(single_level_ori_file2) > 0 ) {
  source(TABLE_PROGRAM, keep.source = TRUE)
  run_main()

} else {
  print("Permutation has no agencies. Skipping....")

  #Write out a file to indicate skip
  paste0("") %>%
    as_tibble() %>%
    write_csv(paste0(file_skip_variance, "/", Sys.getenv("DER_CURRENT_PERMUTATION_NUM"), "_",  Sys.getenv("TABLE_NAME"), ".csv"))
}
