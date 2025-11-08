library(rmarkdown)
library(tidyverse)
library(rjson)

source(here::here("tasks/logging.R"))

external_path <- Sys.getenv("EXTERNAL_FILE_PATH")
inputPipelineDir <- Sys.getenv("INPUT_PIPELINE_DIR")
outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")

validation_output_path <- paste0(outputPipelineDir, "/validation_outputs/")
validation_input_path <- paste0(inputPipelineDir, "/validation_inputs/bystate")

if (! dir.exists(validation_output_path)) {
  dir.create(validation_output_path, recursive = TRUE)
}
if (! dir.exists(validation_input_path)) {
  dir.create(validation_input_path, recursive = TRUE)
}

file_locs <- fromJSON(file = sprintf("%s/external_file_locations.json", inputPipelineDir))

year <- Sys.getenv("DATA_YEAR")
#RUN THE PROGRAMS
input_state <- Sys.getenv("INPUT_STATE")

CONST_YEAR <- year

#Change this code to a 1 for testing out one state (i.e. AL is usually the first state)
#Change to 0 to use all states
MACRO_QUERY_TEST = 0

#Run programs
log_info("00-Create Datasets_full.Rmd starting...")
rmarkdown::render("00-Create_Datasets_full.Rmd", output_format =html_document(),
                  output_file = paste0(validation_input_path, "/Validation_Extracts_",input_state,"_", year, ".html"),
                                       envir = new.env())
