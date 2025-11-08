library("rmarkdown")
library("tidyverse")
library("rjson")

source(here::here("tasks/logging.R"))

#input/output directories for pipeline artifacts
outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")
inputPipelineDir <- Sys.getenv("INPUT_PIPELINE_DIR")

validation_input_path_bystate = paste0(inputPipelineDir, "/validation_inputs/bystate/") #output path for state-level extracts
validation_input_path = paste0(outputPipelineDir, "/validation_inputs/") #output path for all the data extracts

if (! dir.exists(validation_input_path)) {
  dir.create(validation_input_path, recursive = TRUE)
}

output_file_list <- c(
  "2A_Cargo_Theft",
  "3_Incident_Time",
  "4_Cleared_Exceptionally",
  "6_Attempted_Incidents",
  "8A_Bias_Motivation",                              
  "9_Unknown_Location_Type",
  "15_Unknown_Property_Type",
  "26_Victim_Age",                                   
  "27_Victim_Sex",
  "28_Victim_Race",                          
  "31_Unknown_Agg_Asslt_Circ",
  "32_ADDITIONAL_JUSTIFIABLE_HOMICIDE_CIRCUMSTANCES",
  "37_Offender_Age",
  "38_Offender_Sex",                               
  "39_Offender_Race",                                                         
  "47_Arrestee_Age",
  "49_Arrestee_Race"                                
)

for( file in output_file_list) {
  log_debug(paste0('Processing file:',file))
  all_state_files <- list.files(path=validation_input_path_bystate, pattern=paste0(file,"_\\w{2}.csv.gz"))
  file_sizes <- file.info(all_state_files)
  all_state_files <- all_state_files[match(1:length(all_state_files),rank(-file_sizes$size))]
  
  #Create list to hold files
  list_of_tables <- vector("list", length(all_state_files))
  list_of_tables[[1]] <- read_csv(gzfile(paste0(validation_input_path_bystate, all_state_files[[1]])))
  
  for(i in 2:length(all_state_files)){
    list_of_tables[[i]] <- read_csv(gzfile(paste0(validation_input_path_bystate, all_state_files[[i]])), col_types=spec(list_of_tables[[1]]))
  }
  merged_df <- list_of_tables %>% bind_rows()
  merged_df %>% write_csv(gzfile(paste0(validation_input_path,file,".csv.gz")), na="")
  
}