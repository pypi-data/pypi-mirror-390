library("rmarkdown")
library("tidyverse")
library(RPostgres)
library(data.table)

source(here::here("tasks/logging.R"))

#Read in the common functions to be used in R
source(here::here("tasks/impute_items/0-Common_functions_for_imputation.R"))
source("../NIBRS_function.R")
source("../NIBRS_Property_function.r")									  

#SET UP ALL THE NECESSARY INPUT/OUTPUT PATHS
outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")
filepathout = paste0(outputPipelineDir, "/markdown/") #output path for markdown files
mainpath = paste0(outputPipelineDir, "/item_imputation_data/") #output path for data
miscpathout = paste0(outputPipelineDir, "/item_imputation_misc/") #other misc item imputation output
artifacts_path = paste0(outputPipelineDir, "/artifacts/") #location for the property segment																							

if (! dir.exists(filepathout)) {
  dir.create(filepathout, recursive = TRUE)
}
if (! dir.exists(mainpath)) {
  dir.create(mainpath, recursive = TRUE)
}
if (! dir.exists(miscpathout)) {
  dir.create(miscpathout, recursive = TRUE)
}

#output location of logical edits
inputPipelineDir <- Sys.getenv("INPUT_PIPELINE_DIR")
artifactsmainpath = paste0(inputPipelineDir, "/item_imputation_data/") #input path
inputmainpath = paste0(inputPipelineDir, "/item_imputation_data/") #input path for part 1 output

#get the current year
CONST_YEAR <- as.integer(Sys.getenv("DATA_YEAR"))
input_state <- Sys.getenv("INPUT_STATE")

source("../NIBRS_Variable_type.R")
logical_edits_frame <- data.frame(fread_logging(paste0(inputmainpath, "02_", input_state, "_logical_edits.csv.gz")))
num_cols <- unlist(lapply(logical_edits_frame, is.numeric))
logical_edits_frame[, num_cols] <- sapply(logical_edits_frame[, num_cols], as.numeric)


log_info(paste0(input_state,": 301_Recode_Data_for_Imputation_v2.Rmd starting ..."))
rmarkdown::render("301_Recode_Data_for_Imputation_v2.Rmd",
                  output_format = html_document(),
                  output_file = paste0(filepathout, "301_Recode_Data_for_Imputation_v2_", input_state, ".html"),
                  envir = new.env(), quiet = TRUE)

invisible(gc())
knitr::knit_meta(clean = TRUE)
log_info(paste0(input_state,": 330_MICE_Impute_Relationship_code_offender_le3.Rmd starting ..."))
rmarkdown::render("330_MICE_Impute_Relationship_code_offender_le3.Rmd",
                  output_format = html_document(),
                  output_file = paste0(filepathout, "330_MICE_Impute_Relationship_code_offender_le3_", input_state, ".html"),
                  envir = new.env(), quiet = TRUE)

invisible(gc())
knitr::knit_meta(clean = TRUE)

#Handle the case for NY to find donors in another state for 2020
if(CONST_YEAR == 2020 & trim_upcase(input_state) == "NY"){
  log_info(paste0(input_state,": 331_MICE_Impute_Relationship_code_offender_gt3_NY.Rmd starting ..."))
  rmarkdown::render("331_MICE_Impute_Relationship_code_offender_gt3_NY.Rmd",
                    output_format = html_document(),
                    output_file = paste0(filepathout, "331_MICE_Impute_Relationship_code_offender_gt3_", input_state, ".html"),
                    envir = new.env(), quiet = TRUE)

  invisible(gc())
  knitr::knit_meta(clean = TRUE)

}else if(CONST_YEAR == 2021 & trim_upcase(input_state) == "FL"){
  log_info(paste0(input_state,": 331_MICE_Impute_Relationship_code_offender_gt3_FL.Rmd starting ..."))
  rmarkdown::render("331_MICE_Impute_Relationship_code_offender_gt3_FL.Rmd",
                    output_format = html_document(),
                    output_file = paste0(filepathout, "331_MICE_Impute_Relationship_code_offender_gt3_", input_state, ".html"),
                    envir = new.env(), quiet = TRUE)

  invisible(gc())
  knitr::knit_meta(clean = TRUE)

}else{
  log_info(paste0(input_state,": 331_MICE_Impute_Relationship_code_offender_gt3.Rmd starting ..."))
  rmarkdown::render("331_MICE_Impute_Relationship_code_offender_gt3.Rmd",
                    output_format = html_document(),
                    output_file = paste0(filepathout, "331_MICE_Impute_Relationship_code_offender_gt3_", input_state, ".html"),
                    envir = new.env(), quiet = TRUE)

  invisible(gc())
  knitr::knit_meta(clean = TRUE)
}