source("../../Tables_Shared_Scripts/setup_environment.R", keep.source=TRUE)
source("util.R")

log_info("Running 07_Table2c_part1_prepare_datasets.R")
log_debug(system("free -mh", intern = FALSE))


collist <- c(
    "der_society",
    "der_animal_cruelty",
    "der_drug_narcotic",
    "der_gambling",
    "der_pornography_obscene",
    "der_prostitution",
    "der_weapon_law",
    "der_import_violations",
    "der_export_violations",
    "der_federal_liquor_offenses",
    "der_federal_tobacco_offenses",
    "der_wildlife_trafficking",
    "der_espionage",
    "der_money_laundering",
    "der_harboring_escapee_concealing_from_arrest",
    "der_flight_to_avoid_prosecution",
    "der_flight_to_avoid_deportation",
    "der_illegal_entry_into_the_united_states",
    "der_false_citizenship",
    "der_smuggling_aliens",
    "der_re_entry_after_deportation",
    "der_failure_to_register_as_a_sex_offender",
    "der_treason",
    "der_violation_of_national_firearm_act",
    "der_weapons_of_mass_destruction",
    "der_explosives_violation",
    "der_drug_equipment"    
    
)

main <- fread(
    file = paste0(der_file_path, "cleaned_recoded_all_Offenses_recoded_incident.csv.gz"),
    select = c(
        "ori",
        "weight",
        "incident_id",
        "offense_id",
        collist
    )
)

log_debug("After reading in main")
log_debug(system("free -mh", intern = FALSE))

#Filter to eligible agencies
#main <- main %>%
#  clean_main()


agg_location_cat_1_10_inc_offenses 	    <- fread(paste0(der_file_path, "agg_location_cat_1_10_inc_offenses.csv.gz"))
agg_time_of_day_cat_incident 			      <- fread(paste0(der_file_path, "agg_time_of_day_cat_incident.csv.gz"))
agg_time_of_day_cat_report 			      <- fread(paste0(der_file_path, "agg_time_of_day_cat_report.csv.gz"))
ori_population_group_cat 		    <- fread(paste0(der_file_path, "ori_population_group_cat.csv.gz"))
ori_agency_type_cat_1_7           	<- fread(paste0(der_file_path, "ori_agency_type_cat_1_7.csv.gz"))
agg_clearance_cat_1_2           <- fread(paste0(der_file_path, "agg_clearance_cat_1_2.csv.gz"))
agg_gang_cat_inc_offenses   	      <- fread(paste0(der_file_path, "agg_gang_cat_inc_offenses.csv.gz"))

#Deduplicate - Could report up to 3 Criminal/Gang Involvement
agg_gang_cat_inc_offenses <- agg_to_1(agg_gang_cat_inc_offenses)

ori_msa_cat   	          <- fread(paste0(der_file_path, "ori_msa_cat.csv.gz"))
agg_location_cat_1_11_inc_offenses   	      <- fread(paste0(der_file_path, "agg_location_cat_1_11_inc_offenses.csv.gz"))

agg_location_residence_inc_offenses   	  	<- fread(paste0(der_file_path, "agg_location_residence_inc_offenses.csv.gz"))
agg_cleared_cat_1_2                         <- fread(paste0(der_file_path, "agg_cleared_cat_1_2.csv.gz"))


#Need the weight variable
weight_dataset <- main %>%
  select(ori, weight) %>%
  #Deduplicate and keep the unique weight for each ORI
  group_by(ori) %>%
  mutate(raw_first = row_number() == 1) %>%
  ungroup() %>%
  filter(raw_first == TRUE) %>%
  select(-raw_first)

##########################Set the variables for table #######################
DER_MAXIMUM_ROW = 62
#############################################################################


log_debug(system("free -mh", intern = FALSE))
save.image(file=paste0(out_file_path,"/",DER_TABLE_NAME,"_prep_env.RData"))