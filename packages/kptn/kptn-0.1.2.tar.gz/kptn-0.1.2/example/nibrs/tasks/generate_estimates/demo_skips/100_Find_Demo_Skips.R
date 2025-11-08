library("rmarkdown")
library("tidyverse")
library("rjson")
library(data.table)

#Read in the common functions to be used in R
source(here::here("tasks/logging.R"))
source(here::here("tasks/impute_items/0-Common_functions_for_imputation.R"))

#input/output directories for pipeline artifacts
outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")
inputPipelineDir <- Sys.getenv("INPUT_PIPELINE_DIR")
external_path <- Sys.getenv("EXTERNAL_FILE_PATH")

in_file_path = paste0(inputPipelineDir, "/indicator_table_estimates/") #output path for all the data extracts

out_file_path = paste0(outputPipelineDir, "/indicator_demo_missing/")

if (! dir.exists(out_file_path)) {
  dir.create(out_file_path, recursive = TRUE)
}

#External files json
input_folder <- sprintf("%s", inputPipelineDir)
file_locs <- fromJSON(file = sprintf("%s/external_file_locations.json", input_folder))

#set-up year
CONST_YEAR <- Sys.getenv("DATA_YEAR")

# list of demographic tables to check against
demo_table_list <- c("3a", "3aunclear", "3aclear", "3b", "3bunclear", "3bclear",  "4a", "4b", "5a", "5b", "DM7", "DM9", "DM10", "GV2a")

#set up the list of tables run
list_of_tables <- list.files(in_file_path, "Table.*ORI_\\d+\\.csv\\.gz")

skip_list <- data.frame(Table = as.character(), Demographic_Permutation = as.numeric())

#get the list of all objects created in memory up to this point
keep_objs <- ls(all=TRUE)

TABLE_PATTERN <- "Table (\\w+) ORI_(\\d+)\\.csv\\.gz"

# go through all the tables
for (f in c(1:length(list_of_tables))) {

  log_debug(paste0("Current table: ", list_of_tables[f]))
  # read  in column names and subset to only the estimate columns
  table_vars <- fread(paste0(in_file_path, list_of_tables[f]), nrow=0) %>% 
    colnames() %>%
    str_subset("^t_")
  table <- str_match(string=list_of_tables[f], pattern=TABLE_PATTERN)[,2] %>% as.character()
  perm <- str_match(string=list_of_tables[f], pattern=TABLE_PATTERN)[,3] %>% as.numeric()
  # loop through all the permutations and extract the estimate columns

  if (table %in% demo_table_list) {
    log_debug("Current Perm: ", perm)
    if (length(table_vars) == 0) {
      skip_list <- skip_list %>% bind_rows(data.frame(Table = table, Demographic_Permutation = perm-1))
    }

  }
}
gc(rm(list= ls(all=TRUE)[! (ls(all=TRUE) %in% c("keep_objs",keep_objs))]))

# write out results
skip_list %>% write_csv(file = paste0(out_file_path,"demographic_permutation_skipped_", CONST_YEAR, ".csv"), na="")
