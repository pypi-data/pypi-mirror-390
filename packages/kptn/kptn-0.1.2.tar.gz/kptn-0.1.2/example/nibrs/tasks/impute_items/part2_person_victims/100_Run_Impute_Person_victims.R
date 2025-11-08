library("rmarkdown")
library("tidyverse")
library(RPostgres)
library(DT)
library(mice)
library(miceadds)
library(data.table)

source(here::here("tasks/logging.R"))

#Read in the common functions to be used in R plus helper scripts needed
#by multiple markdown files
source(here::here("tasks/impute_items/0-Common_functions_for_imputation.R"))
source("../NIBRS_Offense_function.r")
source("../NIBRS_function.R")

#SET UP ALL THE NECESSARY INPUT/OUTPUT PATHS
outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")
filepathout = paste0(outputPipelineDir, "/markdown/") #output path for markdown files

mainpath = paste0(outputPipelineDir, "/item_imputation_data/") #output path for data

miscpathout = paste0(outputPipelineDir, "/item_imputation_misc/") #other misc item imputation output

if (! dir.exists(filepathout)) {
  dir.create(filepathout, recursive = TRUE)
}
if (! dir.exists(mainpath)) {
  dir.create(mainpath, recursive = TRUE)
}
if (! dir.exists(miscpathout)) {
  dir.create(miscpathout, recursive = TRUE)
}

#output location of create_NIBRS_extracts
inputPipelineDir <- Sys.getenv("INPUT_PIPELINE_DIR")
inputmainpath = paste0(inputPipelineDir, "/item_imputation_data/") #input path for part 1 output
artifactsmainpath = paste0(inputPipelineDir, "/artifacts/") #input path for other task output

input_state <- Sys.getenv("INPUT_STATE")

logical_edits_frame <- data.frame(fread_logging(paste0(inputmainpath, "02_", input_state, "_logical_edits.csv.gz")))

# 03 Impute Offender/Arrestee when they match
log_info(paste0(input_state,": 03_MICE_Item_Missing_Imputation_arrestee_offender_match_v3.Rmd starting..."))
rmarkdown::render("03_MICE_Item_Missing_Imputation_arrestee_offender_match_v3.Rmd",
                  output_format = html_document(),
                  output_file = paste0(filepathout, "03_MICE_Item_Missing_Imputation_arrestee_offender_match_v3_", input_state, ".html"),
                  envir = new.env(), quiet = TRUE)
invisible(gc())
knitr::knit_meta(clean = TRUE)

# 04 Create Data Offender Imputation Cleared
log_info(paste0(input_state,": 04_Create_Data_Offender_Imputation_Cleared.Rmd starting..."))
rmarkdown::render("04_Create_Data_Offender_Imputation_Cleared.Rmd",
                  output_format = html_document(),
                  output_file = paste0(filepathout, "04_Create_Data_Offender_Imputation_Cleared_", input_state, ".html"),
                  envir = new.env(), quiet = TRUE)
invisible(gc())
knitr::knit_meta(clean = TRUE)

# 05 Impute Offender when offender/arrestee don't match
log_info(paste0(input_state,": 05_MICE_Item_Missing_Imputation_offender_v3.Rmd starting..."))
rmarkdown::render("05_MICE_Item_Missing_Imputation_offender_v3.Rmd",
                  output_format = html_document(),
                  output_file = paste0(filepathout, "05_MICE_Item_Missing_Imputation_offender_v3_", input_state, ".html"),
                  envir = new.env(), quiet = TRUE)
invisible(gc())
knitr::knit_meta(clean = TRUE)

# 06 Create Data Victim Imputation Cleared
log_info(paste0(input_state,": 06_Create_Data_Victim_Imputation_Cleared.Rmd starting..."))
rmarkdown::render("06_Create_Data_Victim_Imputation_Cleared.Rmd",
                  output_format = html_document(),
                  output_file = paste0(filepathout, "06_Create_Data_Victim_Imputation_Cleared_", input_state, ".html"),
                  envir = new.env(), quiet = TRUE)
invisible(gc())
knitr::knit_meta(clean = TRUE)

# 07 Impute Victim
log_info(paste0(input_state,": 07_MICE_Item_Missing_Imputation_victim_v3.Rmd starting..."))
rmarkdown::render("07_MICE_Item_Missing_Imputation_victim_v3.Rmd",
                  output_format = html_document(),
                  output_file = paste0(filepathout, "07_MICE_Item_Missing_Imputation_victim_v3_", input_state, ".html"),
                  envir = new.env(), quiet = TRUE)
invisible(gc())
knitr::knit_meta(clean = TRUE)

# 08 Create Data Arrestee Imputation Cleared
log_info(paste0(input_state,": 08_Create_Data_Arrestee_Imputation_Cleared.Rmd starting..."))
rmarkdown::render("08_Create_Data_Arrestee_Imputation_Cleared.Rmd",
                  output_format = html_document(),
                  output_file = paste0(filepathout, "08_Create_Data_Arrestee_Imputation_Cleared_", input_state, ".html"),
                  envir = new.env(), quiet = TRUE)
invisible(gc())
knitr::knit_meta(clean = TRUE)

# 09 Impute Arrestee when offender/arrestee do not match
log_info(paste0(input_state,": 09_MICE_Item_Missing_Imputation_Arrestee_v3.Rmd starting..."))
rmarkdown::render("09_MICE_Item_Missing_Imputation_Arrestee_v3.Rmd",
                  output_format = html_document(),
                  output_file = paste0(filepathout, "09_MICE_Item_Missing_Imputation_Arrestee_v3_", input_state, ".html"),
                  envir = new.env(), quiet = TRUE)
invisible(gc())
knitr::knit_meta(clean = TRUE)
