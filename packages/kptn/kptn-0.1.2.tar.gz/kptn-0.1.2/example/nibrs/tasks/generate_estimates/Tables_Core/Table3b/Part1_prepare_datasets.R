source("../../Tables_Shared_Scripts/setup_environment.R", keep.source=TRUE)
source("util.R")

log_info("Running 10_Table3b_part1_prepare_datasets.R")
log_debug(system("free -mh", intern = FALSE))

full_table = "Table3b-Person Victims-Rates"

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
    "der_revised_rape",
    "der_violent_crime_all",
    "der_robbery",
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
    "der_stolen_property_offenses",
    "der_property_crime_all",
    "der_car_jacking", 
    "der_assault_offenses_all",
    "der_violent_crime_all_2"    
)

main <- fread(
    file = paste0(der_file_path, "cleaned_recoded_all_Offenses_recoded_offenses.csv.gz"),
    select = c(
        "ori",
        "weight",
        "victim_type_code",
        "der_in_univ_elig",
        "incident_id",
        "victim_id",
        "offense_id",
        "der_victim_LEO",
        collist
    )
)

log_debug("After reading in main")
log_debug(system("free -mh", intern = FALSE))

#Filter to eligible agencies
# main <- main %>%
#     mutate(
# 
#     #Victim Type ID = 4 is Individual; Victim Type ID = 5 is Law Enforcement Officer;
#     der_victim_person = fcase(
#       victim_type_code %in% c("I","L"), 1,
#       default = NA_real_
#     ),
# 
#     der_victim_LEO = fcase(
#       victim_type_code %in% c("L"), 1,
#       default = NA_real_
#     )) %>%
#   filter(der_in_univ_elig == 1 & der_victim_person == 1 )

main <- main[ , der_victim_person := fcase(victim_type_code %in% c("I","L"), 1, default = NA_real_)][, der_victim_LEO := fcase(
  victim_type_code %in% c("L"), 1,
  default = NA_real_
)][der_in_univ_elig == 1 & der_victim_person == 1]

#der_victim_age_cat_15_17
agg_victim_age_cat_15_17_victim <- fread(paste0(der_file_path, "agg_victim_age_cat_15_17_victim_imp.csv.gz"))

#der_victim_gender
agg_victim_gender_victim <- fread(paste0(der_file_path, "agg_victim_gender_victim_imp.csv.gz"))

#der_victim_race
agg_victim_race_victim <- fread(paste0(der_file_path, "agg_victim_race_victim_imp.csv.gz"))

###########################################Age-specific victimization rate 2##################################################
# der_victim_age_cat_under18_2 = fcase( 0 <= der_victim_age  & der_victim_age  < 12, 1, #Under 12
#                                       12 <= der_victim_age  & der_victim_age < 18, 2 #12-17
# ),

agg_victim_age_cat_under18_2_victim_imp <- fread(paste0(der_file_path, "agg_victim_age_cat_under18_2_victim_imp.csv.gz"))

# der_victim_age_cat_12_17_cat = fcase( 12 <= der_victim_age  & der_victim_age  < 15, 1, #12-14
#                                      15 <= der_victim_age  & der_victim_age < 18, 2 #15-17
# ),

agg_victim_age_cat_12_17_cat_victim_imp <- fread(paste0(der_file_path, "agg_victim_age_cat_12_17_cat_victim_imp.csv.gz"))


# der_victim_age_cat_2_uo18 = fcase( 0 <= der_victim_age  & der_victim_age < 18 , 1, #Under 18
#                                    18 <= der_victim_age                        , 2, #18+
#                                    victim_age_code %in% c("00","NS")                      , 3, #Unknown
#                                    default = 3 # Unknown
# ),

agg_victim_age_cat_2_uo18_victim_imp <- fread(paste0(der_file_path, "agg_victim_age_cat_2_uo18_victim_imp.csv.gz"))

###############################################################################################################################


##############################################Weapon involved###############################################################

#der_weapon_no_yes
agg_weapon_no_yes_victim <- fread(paste0(der_file_path, "agg_weapon_no_yes_victim.csv.gz")) %>%
  keep_to_yes_victim(yesstring = "der_weapon_no_yes == 2")

#Deduplicate
agg_weapon_no_yes_victim <- agg_to_1(agg_weapon_no_yes_victim)


#der_weapon_yes_cat
agg_weapon_yes_cat_victim <- fread(paste0(der_file_path, "agg_weapon_yes_cat_victim.csv.gz"))



###############################################################################################################################


############################################Victim-offender relationship#######################################################

#der_relationship
agg_relationship_cat_victim <- fread(paste0(der_file_path, "agg_relationship_cat_victim_imp.csv.gz"))


###############################################################################################################################


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
agg_raw_weapon_hierarchy_recode_victim 	  <- fread(paste0(der_file_path, "agg_raw_weapon_hierarchy_recode_victim.csv.gz"))

#Victim-offender relationship hierarchy
# 1:    Intimate partner
# 2:    Other family
# 3:    Outside family but known to victim
# 4:    Stranger
# 5:    Victim was Offender
# 6:    Unknown relationship
# 7:    Unknown Offender Incidents
# 8:    Missing from Uncleared Incidents

#Note this is aggregated at the incident and victim level
#Only one VOR per incident and victim is chosen
agg_relationship_hierarchy_victim 		  <- fread(paste0(der_file_path, "agg_relationship_hierarchy_victim_imp.csv.gz"))

#Victim Hispanic Origin
# der_victim_ethnicity = fcase(victim_ethnicity_code == "H", 1, #Hispanic or Latino
#                              victim_ethnicity_code == "N", 2, #Not Hispanic or Latino
#                              default= 3),  #Multiple/Unknown/Not Specified

agg_victim_ethnicity_victim <- fread(paste0(der_file_path, "agg_victim_ethnicity_victim_imp.csv.gz"))

#Victim race and Hispanic Origin
# der_victim_ethnicity_race = fcase(
#   victim_ethnicity_code == "H", 1, #  Hispanic or Latino
#   victim_ethnicity_code == "N" & victim_race_code == "W", 2,  # Non-Hispanic, White
#   victim_ethnicity_code == "N" & victim_race_code == "B", 3,  #  Non-Hispanic, Black
#   victim_ethnicity_code == "N" & victim_race_code == "I", 4,  # Non-Hispanic, American Indian or Alaska Native
#   victim_ethnicity_code == "N" & victim_race_code == "A", 5,  # Asian:  Non-Hispanic, Asian
#   victim_ethnicity_code == "N" & victim_race_code == "AP", 5, # Asian, Native Hawaiian or Other Pacific Islander: Non-Hispanic, Asian
#   victim_ethnicity_code == "N" & victim_race_code == "C", 5,  # Chinese: Non-Hispanic, Asian
#   victim_ethnicity_code == "N" & victim_race_code == "J", 5,  # Japanese: Non-Hispanic, Asian
#   victim_ethnicity_code == "N" & victim_race_code == "P", 6,  # Non-Hispanic, Native Hawaiian or Other Pacific Islander
#   victim_ethnicity_code == "N" & victim_race_code == "U", 7,  # U - Unknown
#   default = 7                    # includes O (Other), M (Multiple), NS (Not Specified)
# ),    

agg_victim_ethnicity_race_victim <- fread(paste0(der_file_path, "agg_victim_ethnicity_race_victim_imp.csv.gz"))

dim(main)
main <- merge(main, agg_victim_age_cat_15_17_victim[,.(incident_id, victim_id, der_new_column_age=der_victim_age_cat_15_17)],
              by = c("incident_id","victim_id"), all.x = TRUE)

dim(main)

dim(main)
main <- merge(main, agg_victim_gender_victim[,.(incident_id, victim_id, der_new_column_gender=der_victim_gender)],
              by = c("incident_id","victim_id"), all.x = TRUE)

dim(main)

dim(main)
main <- merge(main, agg_victim_race_victim[,.(incident_id, victim_id, der_new_column_race=der_victim_race)],
              by = c( "incident_id", "victim_id"), all.x = TRUE)

dim(main)

main <- merge(main, agg_victim_ethnicity_victim[,.(incident_id, victim_id, der_new_column_ethnicity=der_victim_ethnicity)],
              by = c( "incident_id", "victim_id"), all.x = TRUE)
log_dim(main)
log_debug(system("free -mh", intern = FALSE))


#Create a generic age variable for subsetting in demographic permutations.  Should have range of 0 - 99
#der_victim_age_round = floor(der_victim_age),

agg_victim_age_round_victim <- fread(paste0(der_file_path, "agg_victim_age_round_victim_imp.csv.gz"))

#For Any other victim ages
main <- merge(main, agg_victim_age_round_victim[,.(incident_id, victim_id, der_new_column_age_round=der_victim_age_round)],
              by = c("incident_id","victim_id"), all.x = TRUE)


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
DER_MAXIMUM_ROW = 79
DER_MAXIMUM_COLUMN = 33
#############################################################################


log_debug(system("free -mh", intern = FALSE))
save.image(file=paste0(out_file_path,"/",DER_TABLE_NAME,"_prep_env.RData"))