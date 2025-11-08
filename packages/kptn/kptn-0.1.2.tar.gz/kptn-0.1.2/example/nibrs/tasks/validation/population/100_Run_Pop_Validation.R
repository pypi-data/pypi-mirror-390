library(rmarkdown)
library(tidyverse)
library(rjson)

source(here::here("tasks/logging.R"))

## Setup Environment Variables
#```{r env}

external_path <- Sys.getenv("EXTERNAL_FILE_PATH")
inputPipelineDir <- Sys.getenv("INPUT_PIPELINE_DIR")
outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")

input_files_folder <- paste0(inputPipelineDir, "/initial_tasks_output/")
validation_output_path <- paste0(outputPipelineDir, "/validation_outputs/")

if (! dir.exists(validation_output_path)) {
  dir.create(validation_output_path, recursive = TRUE)
}

file_locs <- fromJSON(file = sprintf("%s/external_file_locations.json", inputPipelineDir))

year <- Sys.getenv("DATA_YEAR")
pep_location <- file.path(external_path,file_locs[[year]]$pep)

log_info("Population_Validation_With_Tables.Rmd starting...")
rmarkdown::render("Population_Validation_With_Tables.Rmd", output_format = html_document(),
                  output_file = paste0(validation_output_path, "Population_Validation_With_Tables_", year, ".html"),
                  envir = new.env(), quiet = TRUE)
