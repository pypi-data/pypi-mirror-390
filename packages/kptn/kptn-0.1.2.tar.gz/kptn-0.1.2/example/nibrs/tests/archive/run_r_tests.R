library(rjson)
library(tidyverse)

Sys.setenv(VROOM_CONNECTION_SIZE=500072*2)

args <- commandArgs(trailingOnly = TRUE)
if (length(args) == 1) {
  print('ERROR: need to provide the path to the test folder to run or "all" to run all tests.')
  quit(save="no",status=1)
}

dir_arg <- args[2]
# get all the subfolders which start with the pattern 'tests_'
all_dir_list <- grep("tests/tests_*", list.dirs(path = "tests", full.names = TRUE), value = TRUE)


if(dir_arg == "all"){
  dirs_to_test <- all_dir_list
} else if (is.element(dir_arg, all_dir_list)) {
  dirs_to_test <- list(dir_arg)
} else {
  print(paste0('ERROR: first argument was neither a path to testing directory or "all".'))
  quit(save = "no", status = 1)
}

inputPipelineDir <- "gold_standard_output_full"

Sys.setenv(
  INPUT_PIPELINE_DIR_NAME = inputPipelineDir,
  INPUT_STATE = "AL",
  DATA_YEAR = 2020,
  LOG_THRESHOLD = "INFO"
)


if(args[1] == "SETUP"){
  gs_files_list <- list()
  for(testdir in dirs_to_test) {
    print(paste0("Gathering gold standard files for directory:",testdir))
    script_list = list.files(path=testdir,pattern="setup_tests*",include.dirs=FALSE)
    print(script_list)
    for(script in script_list){
      # call the scripts with the SETUP command to get all gold standard files
      source(file.path(testdir,script))
      for(test in list_of_tests){
        for(output_file in listOfFiles[[test]])
        {
          gs_files_list <- append(gs_files_list,paste0(output_folder[[test]],output_file))
        }
      }
    }
  }
  write(toJSON(gs_files_list),"tests/gs_files_to_copy.json")
} else {
  for(testdir in dirs_to_test) {
    print(paste0("Running tests for directory:",testdir))
    testthat::test_dir(testdir,stop_on_failure=TRUE)
  }
}