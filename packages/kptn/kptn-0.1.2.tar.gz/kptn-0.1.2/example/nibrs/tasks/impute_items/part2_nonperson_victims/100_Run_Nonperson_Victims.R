library("rmarkdown")
library("tidyverse")
library(RPostgres)
library(DT)
library(mice)
library(miceadds)
library(data.table)

source(here::here("tasks/logging.R"))

#Read in the common functions to be used in R
source(here::here("tasks/impute_items/0-Common_functions_for_imputation.R"))
source("../NIBRS_function.R")
source("../NIBRS_Offense_function.r")

#SET UP ALL THE NECESSARY INPUT/OUTPUT PATHS
outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")
filepathout = paste0(outputPipelineDir, "/markdown/") #output path for markdown files

if (! dir.exists(filepathout)) {
  dir.create(filepathout, recursive = TRUE)
}

mainpath = paste0(outputPipelineDir, "/item_imputation_data/") #output path for data

if (! dir.exists(mainpath)) {
  dir.create(mainpath, recursive = TRUE)
}

miscPathout = paste0(outputPipelineDir, "/item_imputation_misc/") #other misc item imputation output

if (! dir.exists(miscPathout)) {
  dir.create(miscPathout, recursive = TRUE)
}

read_csv <- partial(read_csv, guess_max = 1000000) #For now, read thru the 1st 1,000,000 rows to determine variable type
md.pattern <- partial(md.pattern, plot=FALSE)


#output location of create_NIBRS_extracts
inputPipelineDir <- Sys.getenv("INPUT_PIPELINE_DIR")
inputmainpath = paste0(inputPipelineDir, "/item_imputation_data/") #input path for part 1 output
artifactsmainpath = paste0(inputPipelineDir, "/artifacts/") #input path for other task output

input_state <- Sys.getenv("INPUT_STATE")


logical_edits_frame <- data.frame(fread_logging(paste0(inputmainpath, "02_", input_state, "_logical_edits.csv.gz")))

# 10 Imputation when offender and arrestee match and the incident is cleared
log_info(paste0(input_state,": 10_MICE_Item_Missing_Imputation_arr_off_match_v3-non-person.Rmd starting..."))
rmarkdown::render("10_MICE_Item_Missing_Imputation_arr_off_match_v3-non-person.Rmd", output_format = html_document(),
                  output_file = paste0(filepathout, "10_MICE_Item_Missing_Imputation_arr_off_match_v3-non-person_", input_state, ".html"),
                  envir = new.env(), quiet = TRUE)
invisible(gc())
knitr::knit_meta(clean = TRUE)

# 11 Create offender imputation data when the incident is cleared
log_info(paste0(input_state,": 11_Create_Data_Offender_Imputation_Cleared-non-person.Rmd starting..."))
rmarkdown::render("11_Create_Data_Offender_Imputation_Cleared-non-person.Rmd", output_format = html_document(),
                  output_file = paste0(filepathout, "11_Create_Data_Offender_Imputation_Cleared-non-person_", input_state, ".html"),
                  envir = new.env(), quiet = TRUE)
invisible(gc())
knitr::knit_meta(clean = TRUE)

# 12 Imputation of offender when offender and arrestee do not match and the incident is cleared
log_info(paste0(input_state,": 12_MICE_Item_Missing_Imputation_offender_v3-non-person.Rmd starting..."))
rmarkdown::render("12_MICE_Item_Missing_Imputation_offender_v3-non-person.Rmd", output_format = html_document(),
                  output_file = paste0(filepathout, "12_MICE_Item_Missing_Imputation_offender_v3-non-person_", input_state, ".html"),
                  envir = new.env(), quiet = TRUE)
invisible(gc())
knitr::knit_meta(clean = TRUE)

# 13 Create arrestee imputation data when the incident is cleared
log_info(paste0(input_state,": 13_Create_Data_Arrestee_Imputation_Cleared-non-person.Rmd starting..."))
rmarkdown::render("13_Create_Data_Arrestee_Imputation_Cleared-non-person.Rmd", output_format = html_document(),
                  output_file = paste0(filepathout, "13_Create_Data_Arrestee_Imputation_Cleared-non-person_", input_state, ".html"),
                  envir = new.env(), quiet = TRUE)
invisible(gc())
knitr::knit_meta(clean = TRUE)

# 14 Imputation of arrestee when offender and arrestee do not match and the incident is cleared
log_info(paste0(input_state,": 14_MICE_Item_Missing_Imputation_Arrestee_v3-non-person.Rmd starting..."))
rmarkdown::render("14_MICE_Item_Missing_Imputation_Arrestee_v3-non-person.Rmd", output_format = html_document(),
                  output_file = paste0(filepathout, "14_MICE_Item_Missing_Imputation_Arrestee_v3-non-person_", input_state, ".html"),
                  envir = new.env(), quiet = TRUE)
invisible(gc())
knitr::knit_meta(clean = TRUE)
