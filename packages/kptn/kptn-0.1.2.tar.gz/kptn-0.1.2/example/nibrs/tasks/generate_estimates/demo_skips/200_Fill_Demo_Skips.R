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
filepathin_initial = paste0(inputPipelineDir, "/initial_tasks_output/")

final_path_after_variance = paste0(outputPipelineDir, "/indicator_table_estimates_after_variance/") #this is where the final estimates go

if (! dir.exists(final_path_after_variance)) {
  dir.create(final_path_after_variance, recursive = TRUE)
}

#External files json
input_folder <- sprintf("%s", inputPipelineDir)
file_locs <- fromJSON(file = sprintf("%s/external_file_locations.json", input_folder))

#set-up year
CONST_YEAR <- Sys.getenv("DATA_YEAR")
TABLE <- Sys.getenv("TABLE_NAME")
DEMO_PERM <- Sys.getenv("DEMO_PERM")

# read in the geographic exclusions
geo_exclude <- file.path(external_path, file_locs[[CONST_YEAR]]$exclusion) %>%
  fread(select = c("PERMUTATION_NUMBER"))

all_perms <- paste0(filepathin_initial, "POP_TOTALS_PERM_", CONST_YEAR, ".csv") %>%
  fread(select=c("PERMUTATION_NUMBER")) %>%
  filter(PERMUTATION_NUMBER < 1000)

final_all_perms <- all_perms %>%
  anti_join(geo_exclude) %>%
  pull()

# figure out which  geographies we need to create files for based on the demographic
# permutation
if (DEMO_PERM < 12000 | DEMO_PERM %in% c(17000, 18000, 19000, 21000, 22000, 23000, 24000, 25000, 27000, 136000, 139000, 258000) | 
    (DEMO_PERM > 144000 & DEMO_PERM < 154000)) {
  create_geo_list <- final_all_perms
} else if (DEMO_PERM < 12000  | DEMO_PERM %in% c(17000, 18000, 19000, 21000, 22000, 23000, 24000, 25000, 27000) | 
            (DEMO_PERM > 135000 & DEMO_PERM < 142000) | (DEMO_PERM > 145000 & DEMO_PERM < 170000)) {
  region_list <- c(12,23,34,45)
  create_geo_list <- Reduce(intersect, list(region_list,final_all_perms))
} else {
  create_geo_list <- c(1)
}

# list of variables to zero fill
var_list <- c("der_cleared_cells", "estimate_standard_error", "estimate_prb", "estimate_bias", "estimate_rmse",
              "estimate_upper_bound", "estimate_lower_bound", "relative_standard_error", "relative_rmse", "PRB_ACTUAL", 
              "tbd_estimate", "estimate_unweighted", "population_estimate_unweighted", "unweighted_counts")

for (i in c(1:length(create_geo_list))) {
  DER_CURRENT_PERMUTATION_NUM = as.numeric(DEMO_PERM) + create_geo_list[i]
  
  source("../POP_Total_code_assignment.R")
  main_reporting_db <- read_csv(file=paste0(in_file_path, "Table ", TABLE, "_Reporting_Database.csv")) %>%
    POPUALATION_VARIABLE_FUNCTION() %>%
    mutate(estimate = ifelse(estimate == -9, estimate, 0),
           variable_name = "")
  main_reporting_db[,var_list] <- NA
  
  write_csv(main_reporting_db, paste0(final_path_after_variance, "Table ", TABLE, "_Reporting_Database_After_Variance_", DER_CURRENT_PERMUTATION_NUM, ".csv"), na = "")

}
