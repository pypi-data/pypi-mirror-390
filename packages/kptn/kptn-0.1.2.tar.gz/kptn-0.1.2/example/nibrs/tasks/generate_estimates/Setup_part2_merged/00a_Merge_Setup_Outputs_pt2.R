library("rmarkdown")
library("tidyverse")
library(data.table)
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
  'recoded_all_Offenses_recoded_arrestee',
  'recoded_all_recoded_arrestee_arrest_code',
  'recoded_all_Offenses_recoded_arrestee_drug_activity',
  #'recoded_all_Offenses_recoded_drug_activity_arrestee',
  #'recoded_all_Offenses_recoded_drug_activity_incident',
  'recoded_all_Offenses_recoded_incident',
  'recoded_all_Offenses_recoded_offenses',
  # drug outputs
  "nibrs_offense_attempt_complete_flag",
  "agg_drug_narcotic_equipment_cat",
  "agg_crim_activity_35A_c",
  "agg_property_seized_categories_full",
  "agg_property_seized_categories_short",
  "agg_property_seized_any",
  "agg_suspected_type_of_drug",
  "agg_suspected_type_of_drug_seized",
  "agg_suspected_type_of_drug_crim_activity_35A_c",
  "agg_1suspected_type_of_drug_1crim_activity_35A_c",
  "agg_automobile_stolen_count",
  "raw_property_stolen_count",
  "agg_location_cat_inc_offenses",
  "agg_location_cat_1_7_inc_offenses",
  "agg_location_cat_1_10_inc_offenses",
  #"agg_injury_no_yes_inc_offenses",
  #"agg_injury_no_yes_victim_inc_offenses",
  "agg_weapon_no_yes_inc_offenses",
  "agg_weapon_yes_cat_inc_offenses",
  "agg_gang_cat_inc_offenses",
  "agg_relationship_cat2",
  "agg_relationship_cat2_victim",
  
  "agg_location_cat_1_11",
  "agg_location_cat_1_11_inc_offenses",
  "agg_location_cat_1_11_victim",
  "agg_location_cat_1_11_offenses",
  
  "agg_weapon_yes_cat2",
  "agg_weapon_subset_firearm",
  "agg_weapon_subset_knives",
  
  "agg_weapon_yes_cat2_inc_offenses",
  "agg_weapon_subset_firearm_inc_offenses",
  "agg_weapon_subset_knives_inc_offenses",
  
  "agg_weapon_yes_cat2_offenses",
  "agg_weapon_subset_firearm_offenses",
  "agg_weapon_subset_knives_offenses",
  
  "agg_weapon_yes_cat2_victim",
  "agg_weapon_subset_firearm_victim",
  "agg_weapon_subset_knives_victim",
  
  
  "agg_location_cyberspace",
  "agg_location_cyberspace_inc_offenses",
  "agg_location_cyberspace_offenses",
  "agg_location_cyberspace_victim",
  
  "agg_crim_activity_drug_poss_traff_35A_c",
  "agg_crim_activity_drug_poss_pc_35A_c",
  "agg_crim_activity_drug_poss_npc_35A_c",
  "drug_module_inc_additional_offenses",
  
  "unknown_offender_incident",
  "agg_offender_cat",
										 									 						
  "agg_raw_weapon_hierarchy_recode",
  "agg_raw_weapon_hierarchy_recode_inc_offenses",
  "agg_raw_weapon_hierarchy_recode_victim",
  "agg_raw_weapon_hierarchy_recode_offenses",
  
  "agg_raw_weapon_hierarchy_recode_col",
  "agg_raw_weapon_hierarchy_recode_col_inc_offenses",
  "agg_raw_weapon_hierarchy_recode_col_victim",
  "agg_raw_weapon_hierarchy_recode_col_offenses",  
  
  "agg_single_multi_firearm_types_inc_offenses",
  "agg_single_multi_firearm_types_offenses",
  
  "agg_single_gun_cat_inc_offenses",
  "agg_single_gun_cat_offenses",
  
  "agg_location_residence",
  "agg_location_residence_inc_offenses",
  "agg_location_residence_offenses",
  "agg_location_residence_victim",
  
  "agg_location_1_12",
  "agg_location_1_12_inc_offenses",
  "agg_location_1_12_offenses",
  "agg_location_1_12_victim",  
  
  "agg_cleared_cat_1_2", 
  
  "agg_raw_weapon_recode_4_level",
  "agg_raw_weapon_recode_4_level_inc_offenses",
  "agg_raw_weapon_recode_4_level_offenses",
  "agg_raw_weapon_recode_4_level_victim", 
  
  "recoded_all_recoded_arrestee_groupb_arrest_code",  
  "agg_juvenile_disp_arrestee_groupb",
  "agg_arrest_type_arrestee_groupb",
  "agg_weapon_no_yes_arrestee_groupb",
  "agg_weapon_yes_cat_arrestee_groupb"
  
  
  
  
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

  for(i in 2:length(all_state_files)){
    temp <- fread(all_state_files[[i]],colClasses=classTypes)
    if(nrow(temp) > 0){
      list_of_tables[[i]] <- temp
    }
  }
  merged_df <- list_of_tables %>% bind_rows()
  merged_df %>% fwrite_wrapper(paste0(der_file_path,file,".csv.gz"), na="")

}
