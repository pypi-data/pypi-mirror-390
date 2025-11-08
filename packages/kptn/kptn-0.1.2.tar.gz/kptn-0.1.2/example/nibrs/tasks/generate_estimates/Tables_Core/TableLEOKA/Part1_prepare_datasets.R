source("../../Tables_Shared_Scripts/setup_environment.R", keep.source=TRUE)
source("util.R")

#####everything between main and setting constants
log_info("Running 16_TableLEOKA_part1_prepare_datasets.R")
log_debug(system("free -mh", intern = FALSE))


#Bring in the main file that have the victim of interest
collist <- c(
    "der_assault_victim"
)

main <- fread(
    file = paste0(der_file_path, "cleaned_NIBRS_LEO_Assaulted.csv.gz"),
    select = c(
        "ori",
        "weight",
        "incident_id",
        "victim_id",
        collist
    )
)

log_debug("After reading in main")
log_debug(system("free -mh", intern = FALSE))

#Filter to eligible agencies
#main <- main %>%
#    clean_main()

#agg_activity_cat_victim
agg_activity_cat_victim <- fread(paste0(der_file_path, "agg_activity_cat_victim.csv.gz"))


#agg_assignment_cat_victim
agg_assignment_cat_victim <- fread(paste0(der_file_path, "agg_assignment_cat_victim.csv.gz"))


#agg_weapon_no_yes_victim
agg_weapon_no_yes_victim <- fread(paste0(der_file_path, "agg_weapon_no_yes_victim.csv.gz"))

agg_weapon_no_yes_victim <- agg_weapon_no_yes_victim %>%
  keep_to_yes_victim(yesstring="der_weapon_no_yes == 2") %>%
  agg_to_1()

#agg_weapon_yes_cat_victim
agg_weapon_yes_cat_victim <- fread(paste0(der_file_path, "agg_weapon_yes_cat_victim.csv.gz"))

#agg_injury_no_yes_victim
agg_injury_no_yes_victim <- fread(paste0(der_file_path, "agg_injury_no_yes_victim.csv.gz"))

agg_injury_no_yes_victim <- agg_injury_no_yes_victim %>%
  keep_to_yes_victim(yesstring="der_injury_no_yes == 2") %>%
  agg_to_1()

#agg_victim_count_1_2_plus
agg_victim_count_1_2_plus <- fread(paste0(der_file_path, "agg_victim_count_1_2_plus.csv.gz"))

#agg_offender_count_1_2_plus
agg_offender_count_1_2_plus <- fread(paste0(der_file_path, "agg_offender_count_1_2_plus.csv.gz"))


#agg_offense_count_1_2_3_plus
agg_offense_count_1_2_3_plus  	  <- fread(paste0(der_file_path, "agg_offense_count_1_2_3_plus.csv.gz"))


#agg_relationship_cat_victim
agg_relationship_cat_victim 		<- fread(paste0(der_file_path, "agg_relationship_cat_victim_imp.csv.gz"))

#agg_location_cat_1_10_victim
agg_location_cat_1_10_victim  			<- fread(paste0(der_file_path, "agg_location_cat_1_10_victim.csv.gz"))

#agg_time_of_day_cat_incident
agg_time_of_day_cat_incident 			      <- fread(paste0(der_file_path, "agg_time_of_day_cat_incident.csv.gz"))

#agg_time_of_day_cat_report
agg_time_of_day_cat_report 			      <- fread(paste0(der_file_path, "agg_time_of_day_cat_report.csv.gz"))

#agg_clearance_cat
agg_clearance_cat   	      <- fread(paste0(der_file_path, "agg_clearance_cat.csv.gz"))

#agg_exception_clearance_cat
agg_exception_clearance_cat  	  <- fread(paste0(der_file_path, "agg_exception_clearance_cat.csv.gz"))

#agg_relationship_cat2_victim
agg_relationship_cat2_victim 		<- fread(paste0(der_file_path, "agg_relationship_cat2_victim_imp.csv.gz"))

#agg_location_cat_1_11_victim
agg_location_cat_1_11_victim  			<- fread(paste0(der_file_path, "agg_location_cat_1_11_victim.csv.gz"))


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
DER_MAXIMUM_ROW = 91
#############################################################################

log_debug(system("free -mh", intern = FALSE))
save.image(file=paste0(out_file_path,"/",DER_TABLE_NAME,"_prep_env.RData"))