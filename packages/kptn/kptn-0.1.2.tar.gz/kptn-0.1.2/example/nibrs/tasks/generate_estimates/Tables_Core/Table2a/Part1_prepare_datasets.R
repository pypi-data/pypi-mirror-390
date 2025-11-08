source("../../Tables_Shared_Scripts/setup_environment.R", keep.source=TRUE)
source("util.R")

log_info("Running 05_Table2a_part1_prepare_datasets.R")
log_debug(system("free -mh", intern = FALSE))


collist <- c(
    "der_against_person",
    "der_aggravated_assault",
    "der_simple_assault",
    "der_intimidation",
    "der_murder_non_neg_manslaughter",
    "der_neg_manslaughter",
    "der_kidnapping_abduction",
    "der_human_trafficking_sex",
    "der_human_trafficking_labor",
    "der_rape",
    "der_sodomy",
    "der_sexual_assault_object",
    "der_fondling",
    "der_sexual_offenses_nonforcible",
    "der_robbery",
    "der_revised_rape",
    "der_violent_crime_no_robbery",
    "der_car_jacking",
    "der_assault_offenses_all", 
    "der_violent_crime_no_robbery_2"    
)

main <- fread(
    file = paste0(der_file_path, "cleaned_recoded_all_Offenses_recoded_offenses.csv.gz"),
    select = c(
        "ori",
        "weight",
        "incident_id",
        "victim_id",
        "offense_id",
        collist
    )
)

log_debug("After reading in main")
log_debug(system("free -mh", intern = FALSE))

#Filter to eligible agencies
#main <- main %>%
#  clean_main()

agg_weapon_no_yes_offenses  	  <- fread(paste0(der_file_path, "agg_weapon_no_yes_offenses.csv.gz"))

#Deduplicate
agg_weapon_no_yes_offenses <- agg_to_1(agg_weapon_no_yes_offenses)


agg_weapon_yes_cat_offenses 		<- fread(paste0(der_file_path, "agg_weapon_yes_cat_offenses.csv.gz"))
agg_injury_no_yes_victim  			<- fread(paste0(der_file_path, "agg_injury_no_yes_victim.csv.gz"))

#Deduplicate
agg_injury_no_yes_victim <- agg_to_1(agg_injury_no_yes_victim)


agg_victim_count_1_2_plus 		  <- fread(paste0(der_file_path, "agg_victim_count_1_2_plus.csv.gz"))
agg_offender_count_1_2_plus 	  <- fread(paste0(der_file_path, "agg_offender_count_1_2_plus.csv.gz"))
agg_relationship_cat_victim 		<- fread(paste0(der_file_path, "agg_relationship_cat_victim_imp.csv.gz"))
agg_location_cat_1_10_offenses     	<- fread(paste0(der_file_path, "agg_location_cat_1_10_offenses.csv.gz"))
agg_time_of_day_cat_incident 			      <- fread(paste0(der_file_path, "agg_time_of_day_cat_incident.csv.gz"))
agg_time_of_day_cat_report 			      <- fread(paste0(der_file_path, "agg_time_of_day_cat_report.csv.gz"))
ori_population_group_cat 		    <- fread(paste0(der_file_path, "ori_population_group_cat.csv.gz"))
ori_agency_type_cat_1_7           	<- fread(paste0(der_file_path, "ori_agency_type_cat_1_7.csv.gz"))
agg_clearance_cat_1_2          	<- fread(paste0(der_file_path, "agg_clearance_cat_1_2.csv.gz"))
ori_msa_cat   	          <- fread(paste0(der_file_path, "ori_msa_cat.csv.gz"))
agg_location_cat_1_11_offenses     	<- fread(paste0(der_file_path, "agg_location_cat_1_11_offenses.csv.gz"))
agg_relationship_cat2_victim_imp 		<- fread(paste0(der_file_path, "agg_relationship_cat2_victim_imp.csv.gz"))
agg_location_cyberspace_offenses 		<- fread(paste0(der_file_path, "agg_location_cyberspace_offenses.csv.gz"))

#Weapon involved hierarchy
# 1:    Handgun
# 2:    Firearm
# 3:    Rifle
# 4:    Shotgun
# 5:    Other Firearm
# 6:    Knife/Cutting Instrument
# 7:    Blunt Object
# 8:    Motor Vehicle
# 9:    Personal Weapons (hands, feet, teeth, etc.)
# 10:    Asphyxiation
# 11:    Drugs/Narcotics/Sleeping Pills
# 12:    Poison (include gas)
# 13:    Explosives
# 14:    Fire/Incendiary Device
# 15:    Other
# 16:    No Weapon
# 17:    Unknown
# 18:    Not Applicable

#Note this is aggregated at the incident, victim, and offense level
#Only one weapon per incident, victim, and offense is chosen
agg_raw_weapon_hierarchy_recode_offenses  	  <- fread(paste0(der_file_path, "agg_raw_weapon_hierarchy_recode_offenses.csv.gz"))

agg_location_residence_offenses   	  		  <- fread(paste0(der_file_path, "agg_location_residence_offenses.csv.gz"))

agg_cleared_cat_1_2                         <- fread(paste0(der_file_path, "agg_cleared_cat_1_2.csv.gz"))

agg_raw_weapon_hierarchy_recode_col_offenses <- fread(paste0(der_file_path, "agg_raw_weapon_hierarchy_recode_col_offenses.csv.gz"))

#Need to merge on the agg_victim_gender_victim extract for imputed gender
#der_victim_gender
agg_victim_gender_victim <- fread(paste0(der_file_path, "agg_victim_gender_victim_imp.csv.gz"))

log_dim(main)
main <- merge(main, agg_victim_gender_victim[,.(incident_id, victim_id, der_new_column_gender=der_victim_gender)],
              by = c("incident_id","victim_id"), all.x = TRUE)
log_dim(main)						  



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
DER_MAXIMUM_ROW = 110
#############################################################################


log_debug(system("free -mh", intern = FALSE))
save.image(file=paste0(out_file_path,"/",DER_TABLE_NAME,"_prep_env.RData"))
