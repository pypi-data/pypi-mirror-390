library(rmarkdown)
library(tidyverse)
library(rjson)

source(here::here("tasks/logging.R"))

## Setup Environment Variables
#```{r env}

external_path <- Sys.getenv("EXTERNAL_FILE_PATH")
inputPipelineDir <- Sys.getenv("INPUT_PIPELINE_DIR")
outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")

validation_output_path <- paste0(outputPipelineDir, "/validation_outputs/")
validation_input_path <- paste0(inputPipelineDir, "/validation_inputs/")

if (! dir.exists(validation_output_path)) {
  dir.create(validation_output_path, recursive = TRUE)
}
if (! dir.exists(validation_input_path)) {
  dir.create(validation_input_path, recursive = TRUE)
}

file_locs <- fromJSON(file = sprintf("%s/external_file_locations.json", inputPipelineDir))

year <- Sys.getenv("DATA_YEAR")

log_info("SEARCH_Validation_All_States.Rmd starting...")
rmarkdown::render("SEARCH_Validation_All_States_v3.Rmd", output_format = html_document(),
                  output_file = paste0(validation_output_path, "SEARCH_Validation_All_States_", year, ".html"),
                  envir = new.env(), quiet = TRUE)
