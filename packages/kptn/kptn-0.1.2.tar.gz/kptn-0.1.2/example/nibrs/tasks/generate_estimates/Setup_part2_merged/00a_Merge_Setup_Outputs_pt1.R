library("rmarkdown")
library("tidyverse")
library("data.table")
library("rjson")

source(here::here("tasks/logging.R"))

#input/output directories for pipeline artifacts
outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")
inputPipelineDir <- Sys.getenv("INPUT_PIPELINE_DIR")

der_bystate_file_path = paste0(inputPipelineDir, "/indicator_table_extracts_bystate/") #output path for state-level extracts
der_file_path = paste0(outputPipelineDir, "/indicator_table_extracts/") #output path for all the data extracts

if (! dir.exists(der_file_path)) {
  dir.create(der_file_path, recursive = TRUE)
}

output_file_list = c(
   'NIBRS_LEO_Assaulted',
   'agg_activity_cat_victim',
   'agg_agency_type_cat',
   'agg_agency_type_cat_1_7',
   'agg_arrest_type_arrestee',
   'agg_arrestee_age_cat_15_17_arrestee',
   'agg_arrestee_age_cat_arrestee',
   'agg_arrestee_gender_arrestee',
   'agg_arrestee_gender_race_arrestee',
   'agg_arrestee_race_arrestee',
   'agg_assignment_cat_victim',
   'agg_bias_hate_cat_1_6',
   'agg_bias_hate_cat_1_6_arrestee',
   'agg_bias_hate_cat_1_6_offenses',
   'agg_bias_hate_cat_1_6_victim',
   'agg_bias_hate_no_yes',
   'agg_bias_hate_no_yes_arrestee',
   'agg_bias_hate_no_yes_offenses',
   'agg_bias_hate_no_yes_victim',
   'agg_clearance_cat',
   'agg_clearance_cat_1_2',
   'agg_exception_clearance_cat',
   'agg_gang_cat',
   'agg_gang_cat_offenses',
   'agg_gang_cat_victim',
   'agg_injury_no_yes',
   'agg_injury_no_yes_victim',   
   'agg_injury_hierarchy_victim',
   'agg_injury_hierarchy2_victim',   
   'agg_juvenile_disp_arrestee',
   'agg_location_cat',
   'agg_location_cat_1_10',
   'agg_location_cat_1_10_offenses',
   'agg_location_cat_1_10_victim',
   'agg_location_cat_1_7',
   'agg_location_cat_1_7_offenses',
   'agg_location_cat_1_7_victim',
   'agg_location_cat_offenses',
   'agg_location_cat_victim',
   'agg_multiple_arrest_arrestee',
   'agg_offender_count_1_2_plus',
   'agg_offense_count_1_2_3_plus',
   'agg_offense_group_a_1_48',
   'agg_offense_group_a_1_48_arrestee',
   'agg_offense_group_a_1_48_offenses',
   'agg_population_group_cat',
   #'agg_population_total',
   #'agg_population_total_elig',
   'agg_property_loss',
   'agg_relationship_cat',
   'agg_relationship_cat_forimp',
   'agg_relationship_cat_forimp_victim',
   'agg_relationship_cat_victim',
   'agg_time_of_day_cat',
   'agg_time_of_day_cat_incident',
   'agg_time_of_day_cat_report',
   'agg_victim_age_cat_15_17_victim',
   'agg_victim_age_cat_victim',
   'agg_victim_count_1_2_plus',
   'agg_victim_gender_race_victim',
   'agg_victim_gender_victim',
   'agg_victim_offender_age_1_4_victim',
   'agg_victim_offender_gender_1_4_victim',
   'agg_victim_offender_race_1_10_victim',
   'agg_victim_race_victim',
   'agg_weapon_no_yes',
   'agg_weapon_no_yes_arrestee',
   'agg_weapon_no_yes_offenses',
   'agg_weapon_no_yes_victim',
   'agg_weapon_yes_cat',
   'agg_weapon_yes_cat_arrestee',
   'agg_weapon_yes_cat_offenses',
   'agg_weapon_yes_cat_victim',
   'raw_Injury',
   'raw_Time_of_day_population_agency',
   'raw_all_Offenses_arrestee',
   'raw_all_arrestee_arrest_code',
   'raw_all_Offenses_incident',
   'raw_all_Offenses_offenses',
   'raw_all_Offenses_recoded_incident_drug_activity',
   'raw_arrest_type',
   'raw_arrestee',
   'raw_arrestee_weapon',
   'raw_bias_hate_crime',
   'raw_bias_hate_crime_arrestee',
   'raw_bias_hate_crime_offenses',
   'raw_bias_hate_crime_victim',
   'raw_clearance',
   'raw_gang',
   'raw_gang_offense',
   'raw_location',
   'raw_location_offenses',
   'raw_offender',
   'raw_property_loss',
   'raw_victim',
   'raw_victim_offender_rel',
   'raw_weapon',
   'raw_weapon_offense',
   'recoded_all_Hate_Crime_Offenses_recoded_arrestee',
   'recoded_all_Hate_Crime_Offenses_recoded_incident',
   'recoded_all_Hate_Crime_Offenses_recoded_offenses',
   'recoded_all_Hate_Crime_Offenses_recoded_victim',
  #Add in the following for the GV run
  'agg_victim_murder_non_neg_manslaughter_victim'													  
)


for( file in output_file_list) {
  log_debug(paste0('Processing file:',file))
  all_state_files_raw <- list.files(path=der_bystate_file_path, pattern=paste0(file,"_\\w{2}.csv.gz"),full.names=TRUE)
  file_sizes <- data.frame(file.info(all_state_files_raw))

  all_state_files <- rownames(file_sizes[order(-file_sizes$size),])

  #Create list to hold files
  list_of_tables <- vector("list", length(all_state_files))
  list_of_tables[[1]] <- fread(all_state_files[[1]])

  temp_frame <- data.frame(sapply(list_of_tables[[1]],class))
  # if there are any date columns sapply will return multiple values
  # the dataframe will have one column per col.
  if(ncol(temp_frame) == 1){
    classTypes <- unlist(sapply(list_of_tables[[1]],class))

  } else {
    classTypes <- unlist(temp_frame[1,])
  }

  if("method_entry_code" %in% names(classTypes)) {
    classTypes["method_entry_code"] <- "character"
  }

  for(i in 2:length(all_state_files)){
    temp <- fread(all_state_files[[i]],colClasses=classTypes)
    if(nrow(temp) > 0){
      list_of_tables[[i]] <- temp
    }
  }
  merged_df <- list_of_tables %>% bind_rows()
  merged_df %>% fwrite_wrapper(paste0(der_file_path,file,".csv.gz"), na="")

}