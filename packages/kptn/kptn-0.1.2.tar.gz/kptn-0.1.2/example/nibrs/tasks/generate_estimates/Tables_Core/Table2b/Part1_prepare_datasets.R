source("../../Tables_Shared_Scripts/setup_environment.R", keep.source=TRUE)
source("util.R")

log_info("Running 06_Table2b_part1_prepare_datasets.R")
log_debug(system("free -mh", intern = FALSE))


collist <- c(
    "der_against_property_no_mvt",
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
    "der_property_crime_no_mvt",
    "der_car_jacking",
    "der_corruption",
    "der_other_corruption",
    "der_hacking"
    
    
)

main <- fread(
    file = paste0(der_file_path, "cleaned_recoded_all_Offenses_recoded_incident.csv.gz"),
    select = c(
        "ori",
        "weight",
        "incident_id",
        "offense_id",
        #"der_automobile_stolen_count", - This is read in the next code below
        "one",
        collist
    )
)

log_debug("After reading in main")
log_debug(system("free -mh", intern = FALSE))

#Need to merge on the MVT weight variable:  der_automobile_stolen_count
## QUESTION: does this HAVE to happen before clean main?
agg_automobile_stolen_count <- fread(paste0(der_file_path, "agg_automobile_stolen_count.csv.gz"))

dim(main)
# main <- main %>%
# 	left_join(agg_automobile_stolen_count, by=c("incident_id"))
main <- merge(main, agg_automobile_stolen_count, by = c("incident_id"), all.x = TRUE)
dim(main)


agg_weapon_no_yes_inc_offenses  	  <- fread(paste0(der_file_path, "agg_weapon_no_yes_inc_offenses.csv.gz"))

#Deduplicate
agg_weapon_no_yes_inc_offenses <- agg_to_1(agg_weapon_no_yes_inc_offenses)


agg_weapon_yes_cat_inc_offenses 		<- fread(paste0(der_file_path, "agg_weapon_yes_cat_inc_offenses.csv.gz"))

agg_victim_count_1_2_plus 		  <- fread(paste0(der_file_path, "agg_victim_count_1_2_plus.csv.gz"))
agg_offender_count_1_2_plus 	  <- fread(paste0(der_file_path, "agg_offender_count_1_2_plus.csv.gz"))
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
DER_MAXIMUM_ROW = 75
#############################################################################


log_debug(system("free -mh", intern = FALSE))
save.image(file=paste0(out_file_path,"/",DER_TABLE_NAME,"_prep_env.RData"))