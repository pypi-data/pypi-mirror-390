source("../../Tables_Shared_Scripts/setup_environment.R", keep.source=TRUE)
source("util.R")

log_info("Running 03_Table1b_part1_prepare_datasets.R")
log_debug(system("free -mh", intern = FALSE))

collist <- c(
    "der_against_property",
    "der_arson",
    "der_bribery",
    "der_burglary_b_e",
    "der_counterf_forgery",
    "der_destruction_damage_vand",
    "der_embezzlement",
    "der_extortion_black_mail",
    "der_fraud_offenses",
    "der_larceny_theft",
    "der_motor_vehicle_theft",
    "der_robbery",
    "der_stolen_property_offenses",
    "der_property_crime_all",
    "der_car_jacking"
)

main <- fread(
    file = paste0(der_file_path, "cleaned_recoded_all_Offenses_recoded_incident.csv.gz"),
    select = c(
        "ori",
        "weight",
        "incident_id",
        collist
    )
)

log_debug("After reading in main")
log_debug(system("free -mh", intern = FALSE))


# log_debug("About to kick off clean_main")
#Filter to eligible agencies
#main <- main %>%
#  clean_main()


agg_weapon_no_yes  				      <- fread(paste0(der_file_path, "agg_weapon_no_yes.csv.gz"))

#Deduplicate
agg_weapon_no_yes <- agg_to_1(agg_weapon_no_yes) %>%
  keep_to_yes(yesstring="der_weapon_no_yes==2")

log_debug("After deduping agg_weapon_no_yes")
log_debug(system("free -mh", intern = FALSE))

agg_weapon_yes_cat 				      <- fread(paste0(der_file_path, "agg_weapon_yes_cat.csv.gz"))
agg_victim_count_1_2_plus 		  <- fread(paste0(der_file_path, "agg_victim_count_1_2_plus.csv.gz"))
agg_offender_count_1_2_plus 	  <- fread(paste0(der_file_path, "agg_offender_count_1_2_plus.csv.gz"))
agg_offense_count_1_2_3_plus 	  <- fread(paste0(der_file_path, "agg_offense_count_1_2_3_plus.csv.gz"))
agg_location_cat_1_10 				  <- fread(paste0(der_file_path, "agg_location_cat_1_10.csv.gz"))
agg_time_of_day_cat_incident 		<- fread(paste0(der_file_path, "agg_time_of_day_cat_incident.csv.gz"))
agg_time_of_day_cat_report 			<- fread(paste0(der_file_path, "agg_time_of_day_cat_report.csv.gz"))
ori_population_group_cat 		    <- fread(paste0(der_file_path, "ori_population_group_cat.csv.gz"))
ori_agency_type_cat_1_7         <- fread(paste0(der_file_path, "ori_agency_type_cat_1_7.csv.gz"))
agg_clearance_cat             	<- fread(paste0(der_file_path, "agg_clearance_cat.csv.gz"))
agg_exception_clearance_cat   	<- fread(paste0(der_file_path, "agg_exception_clearance_cat.csv.gz"))
agg_property_loss   	          <- fread(paste0(der_file_path, "agg_property_loss.csv.gz"))
ori_msa_cat   	                <- fread(paste0(der_file_path, "ori_msa_cat.csv.gz"))
agg_location_cat_1_11   	      <- fread(paste0(der_file_path, "agg_location_cat_1_11.csv.gz"))
agg_location_residence   	  		<- fread(paste0(der_file_path, "agg_location_residence.csv.gz"))


log_debug("After reading remaining agg files")
log_debug(system("free -mh", intern = FALSE))

#Need the weight variable
weight_dataset <- main %>%
  select(ori, weight) %>%
  #Deduplicate and keep the unique weight for each ORI
  group_by(ori) %>%
  mutate(raw_first = row_number() == 1) %>%
  ungroup() %>%
  filter(raw_first == TRUE) %>%
  select(-raw_first)

log_debug("After creating weight dataset")
log_debug(system("free -mh", intern = FALSE))

##########################Set the variables for table #######################
DER_MAXIMUM_ROW = 88
#############################################################################

save.image(file=paste0(out_file_path,"/",DER_TABLE_NAME,"_prep_env.RData"))

log_debug("After saving workspace")
log_debug(system("free -mh", intern = FALSE))