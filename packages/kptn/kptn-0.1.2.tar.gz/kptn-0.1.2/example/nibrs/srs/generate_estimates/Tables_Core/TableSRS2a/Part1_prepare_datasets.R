library("tidyverse")
library("rjson")
library(openxlsx)
library(DBI)
library(DT)
library(lubridate)
library(data.table)

#read_csv <- partial(read_csv, guess_max = 1000000) #For now, read thru the 1st 1,000,000 rows to determine variable type
write.csv0 <- partial(write.csv, row.names = FALSE, na ="0")
write.csvSpace <- partial(write.csv, row.names = FALSE, na ="")

#Read in the common functions to be used in R
source(here::here("tasks/logging.R"))
source(here::here("tasks/impute_items/0-Common_functions_for_imputation.R"))

#input/output directories for pipeline artifacts
outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")
inputPipelineDir <- Sys.getenv("INPUT_PIPELINE_DIR")
external_path <- Sys.getenv("EXTERNAL_FILE_PATH")

filepathout = paste0(outputPipelineDir, "/markdown/") #output path for markdown files

if (! dir.exists(filepathout)) {
  dir.create(filepathout, recursive = TRUE)
}

der_file_path = paste0(inputPipelineDir, "/srs/indicator_table_extracts/") #input path where all the data extracts are located

if (! dir.exists(der_file_path)) {
  dir.create(der_file_path, recursive = TRUE)
}

out_file_path = paste0(outputPipelineDir, "/srs/indicator_table_single_intermediate/")

if (! dir.exists(out_file_path)) {
  dir.create(out_file_path, recursive = TRUE)
}

final_path = paste0(outputPipelineDir, "/srs/indicator_table_estimates/") #this is where the final estimates go

if (! dir.exists(final_path)) {
  dir.create(final_path, recursive = TRUE)
}

final_path_after_variance = paste0(outputPipelineDir, "/srs/indicator_table_estimates_after_variance/")

if (! dir.exists(final_path_after_variance)) {
  dir.create(final_path_after_variance, recursive = TRUE)
}

block_imp_path = paste0(outputPipelineDir, "/srs/block_imputation_data/") #block imputation
weight_path = paste0(outputPipelineDir, "/srs/weighting/Data/") #weights

#External files json
input_folder <- sprintf("%s", inputPipelineDir)
file_locs <- fromJSON(file = sprintf("%s/external_file_locations.json", input_folder))

#set-up year
CONST_YEAR <- Sys.getenv("DATA_YEAR")

#for the single run code we want to point it to the NATIONAL population information
DER_CURRENT_PERMUTATION_NUM <- 1
Sys.setenv("DER_CURRENT_PERMUTATION_NUM" = DER_CURRENT_PERMUTATION_NUM)

#source code for a lot of shared functions (needs to run after setting year & permutation or it will error)
source("../../POP_Total_code_assignment.R")

#####everything between main and setting constants
log_info("Running 02_TableSRS2a_part1_prepare_datasets.R")
log_debug(system("free -mh", intern = FALSE))


collist <- c(
    "der_violent_crime",
    "der_murder",
    "der_rape",
    "der_robbery",
    "der_aggravated_assault",
    "der_property_crime",
    "der_burglary",
    "der_larceny_theft",
    "der_mvt"
)

main <- fread(
    file = paste0(der_file_path, "cleaned_recoded_SRS.csv.gz"),
    select = c(
        "ori",
        "weight",
		"der_region",
        collist
    )
)

log_debug("After reading in main")
log_debug(system("free -mh", intern = FALSE))


#Need the weight variable
weight_dataset <- main %>%
  select(ori, weight) %>%
  #Deduplicate and keep the unique weight for each ORI
  group_by(ori) %>%
  mutate(raw_first = row_number() == 1) %>%
  ungroup() %>%
  filter(raw_first == TRUE) %>%
  select(-raw_first)

##########################Set the variables for table #######################
DER_TABLE_NAME = "SRS2a"
DER_MAXIMUM_ROW = 4
#############################################################################

log_debug(system("free -mh", intern = FALSE))
save.image(file=paste0(out_file_path,"/SRS2a_prep_env.RData"))
