source("../../Tables_Shared_Scripts/setup_environment.R", keep.source=TRUE)
source("util.R")

log_info("Running 27_Table5b_part1_prepare_datasets.R")
log_debug(system("free -mh", intern = FALSE))


collist <- c(
    'der_against_person',
    'der_aggravated_assault',
    'der_simple_assault',
    'der_intimidation',
    'der_murder_non_neg_manslaughter',
    'der_neg_manslaughter',
    'der_kidnapping_abduction',
    'der_human_trafficking_sex',
    'der_human_trafficking_labor',
    'der_rape',
    'der_sodomy',
    'der_sexual_assault_object',
    'der_fondling',
    'der_sexual_offenses_nonforcible',
    'der_against_property',
    'der_arson',
    'der_bribery',
    'der_burglary_b_e',
    'der_counterf_forgery',
    'der_destruction_damage_vand',
    'der_embezzlement',
    'der_extortion_black_mail',
    'der_fraud_offenses',
    'der_larceny_theft',
    'der_motor_vehicle_theft',
    'der_robbery',
    'der_stolen_property_offenses',
    'der_society',
    'der_revised_rape',
    'der_violent_crime_all',
    'der_property_crime_all',
    'der_import_violations',
    'der_export_violations',
    'der_federal_liquor_offenses',
    'der_federal_tobacco_offenses',
    'der_wildlife_trafficking',
    'der_espionage',
    'der_money_laundering',
    'der_harboring_escapee_concealing_from_arrest',
    'der_flight_to_avoid_prosecution',
    'der_flight_to_avoid_deportation',
    'der_illegal_entry_into_the_united_states',
    'der_false_citizenship',
    'der_smuggling_aliens',
    'der_re_entry_after_deportation',
    'der_failure_to_register_as_a_sex_offender',
    'der_treason',
    'der_violation_of_national_firearm_act',
    'der_weapons_of_mass_destruction',
    'der_explosives_violation',
    'der_family_offenses',
    'der_trespass',
    'der_curfew_loit_vag',
    'der_liquor_law_viol',
    'der_disorder_conduct',
    'der_failure_to_appear',
    'der_federal_resource_viol',
    'der_perjury',
    'der_dui',
    'der_partb_other',
    'der_car_jacking',
    'der_total_arrest',
    
    'der_assault_offenses_all',
    'der_violent_crime_all_2',
    'der_animal_cruelty',
    'der_drug_narcotic',
    'der_gambling',
    'der_pornography_obscene',
    'der_prostitution',
    'der_weapon_law',
    'der_drug_equipment'    
    
)

main <- fread(
    file = paste0(der_file_path, "cleaned_recoded_all_recoded_arrestee_arrest_code.csv.gz"),
    select = c(
        "ori",
        "weight",
        "incident_id",
        "arrestee_id",
        collist
    )
)


log_debug("After reading in main")
log_debug(system("free -mh", intern = FALSE))


#Note use the below dataset for hate crime
# main_hate_crime <- fread(paste0(der_file_path, "recoded_all_Hate_Crime_Offenses_recoded_arrestee.csv.gz"))
#
#
# #Filter to eligible agencies
# main_hate_crime <- main_hate_crime %>%
#   clean_main()


#der_arrest_type
agg_arrest_type_arrestee <- fread(paste0(der_file_path, "agg_arrest_type_arrestee.csv.gz"))

#der_arrestee_age_cat_15_17
agg_arrestee_age_cat_15_17_arrestee <- fread(paste0(der_file_path, "agg_arrestee_age_cat_15_17_arrestee_imp.csv.gz"))

#der_arrestee_gender
agg_arrestee_gender_arrestee <- fread(paste0(der_file_path, "agg_arrestee_gender_arrestee_imp.csv.gz"))

#der_arrestee_race
agg_arrestee_race_arrestee <- fread(paste0(der_file_path, "agg_arrestee_race_arrestee_imp.csv.gz"))

############################################Arrestee age 2##################################################################
# der_arrestee_age_cat_under18_2 = fcase( 0 <= der_arrestee_age  & der_arrestee_age  < 12, 1, #Under 12
#                                       12 <= der_arrestee_age  & der_arrestee_age < 18, 2 #12-17
# ),

agg_arrestee_age_cat_under18_2_arrestee_imp <- fread(paste0(der_file_path, "agg_arrestee_age_cat_under18_2_arrestee_imp.csv.gz"))

# der_arrestee_age_cat_12_17_cat = fcase( 12 <= der_arrestee_age  & der_arrestee_age  < 15, 1, #12-14
#                                      15 <= der_arrestee_age  & der_arrestee_age < 18, 2 #15-17
# ),

agg_arrestee_age_cat_12_17_cat_arrestee_imp <- fread(paste0(der_file_path, "agg_arrestee_age_cat_12_17_cat_arrestee_imp.csv.gz"))


# der_arrestee_age_cat_2_uo18 = fcase( 0 <= der_arrestee_age  & der_arrestee_age < 18 , 1, #Under 18
#                                    18 <= der_arrestee_age                        , 2, #18+
#                                    arrestee_age_code %in% c("00","NS")                      , 3, #Unknown or Not Specified
#                                    default = 3 # Unknown
# ),

agg_arrestee_age_cat_2_uo18_arrestee_imp <- fread(paste0(der_file_path, "agg_arrestee_age_cat_2_uo18_arrestee_imp.csv.gz"))

#############################################################################################################################

#Arrestee Hispanic Origin
# der_arrestee_ethnicity = fcase(arrestee_ethnicity_code == "H", 1, #Hispanic or Latino
#                                arrestee_ethnicity_code == "N", 2, #Not Hispanic or Latino
#                                default= 3),  #Multiple/Unknown/Not Specified	

agg_arrestee_ethnicity_arrestee <- fread(paste0(der_file_path, "agg_arrestee_ethnicity_arrestee_imp.csv.gz"))

#Arrestee race and Hispanic Origin
# der_arrestee_ethnicity_race = fcase(
#   arrestee_ethnicity_code == "H", 1, #  Hispanic or Latino
#   arrestee_ethnicity_code == "N" & arrestee_race_code == "W", 2,  # Non-Hispanic, White
#   arrestee_ethnicity_code == "N" & arrestee_race_code == "B", 3,  #  Non-Hispanic, Black
#   arrestee_ethnicity_code == "N" & arrestee_race_code == "I", 4,  # Non-Hispanic, American Indian or Alaska Native
#   arrestee_ethnicity_code == "N" & arrestee_race_code == "A", 5,  # Asian:  Non-Hispanic, Asian
#   arrestee_ethnicity_code == "N" & arrestee_race_code == "AP", 5, # Asian, Native Hawaiian or Other Pacific Islander: Non-Hispanic, Asian
#   arrestee_ethnicity_code == "N" & arrestee_race_code == "C", 5,  # Chinese: Non-Hispanic, Asian
#   arrestee_ethnicity_code == "N" & arrestee_race_code == "J", 5,  # Japanese: Non-Hispanic, Asian
#   arrestee_ethnicity_code == "N" & arrestee_race_code == "P", 6,  # Non-Hispanic, Native Hawaiian or Other Pacific Islander
#   arrestee_ethnicity_code == "N" & arrestee_race_code == "U", 7,  # U - Unknown
#   default = 7                    # includes O (Other), M (Multiple), NS (Not Specified)  

agg_arrestee_ethnicity_race_arrestee <- fread(paste0(der_file_path, "agg_arrestee_ethnicity_race_arrestee_imp.csv.gz"))





log_dim(main)
log_debug(system("free -mh", intern = FALSE))

main <- merge(main, agg_arrestee_age_cat_15_17_arrestee[,.(incident_id, arrestee_id, der_new_column_age = der_arrestee_age_cat_15_17)],
              by = c("incident_id","arrestee_id"), all.x = TRUE)
log_dim(main)


log_dim(main)
log_debug(system("free -mh", intern = FALSE))
main <- merge(main, agg_arrestee_gender_arrestee[,.(incident_id, arrestee_id, der_new_column_gender = der_arrestee_gender)],
              by = c("incident_id","arrestee_id"), all.x = TRUE)
log_dim(main)

log_dim(main)
log_debug(system("free -mh", intern = FALSE))
main <- merge(main, agg_arrestee_race_arrestee[,.(incident_id, arrestee_id, der_new_column_race = der_arrestee_race)],
              by = c("incident_id","arrestee_id"), all.x = TRUE)

log_dim(main)



main <- merge(main, agg_arrestee_ethnicity_arrestee[,.(incident_id, arrestee_id, der_new_column_ethnicity=der_arrestee_ethnicity)],
              by = c( "incident_id", "arrestee_id"), all.x = TRUE)
log_dim(main)
log_debug(system("free -mh", intern = FALSE))

#Create a generic age variable for subsetting in demographic permutations.  Should have range of 0 - 99
#der_arrestee_age_round = floor(der_arrestee_age),

agg_arrestee_age_round_arrestee <- fread(paste0(der_file_path, "agg_arrestee_age_round_arrestee_imp.csv.gz"))

#For Any other arrestee ages
main <- merge(main, agg_arrestee_age_round_arrestee[,.(incident_id, arrestee_id, der_new_column_age_round=der_arrestee_age_round)],
              by = c("incident_id","arrestee_id"), all.x = TRUE)


#Call the Group B arrestee data
source("Part1_prepare_datasets_groupb.R")


#Need the weight variable
weight_dataset <- bind_rows(main, main_group_b)  %>%
  select(ori, weight) %>%
  #Deduplicate and keep the unique weight for each ORI
  group_by(ori) %>%
  mutate(raw_first = row_number() == 1) %>%
  ungroup() %>%
  filter(raw_first == TRUE) %>%
  select(-raw_first)

##########################Set the variables for table #######################
DER_MAXIMUM_ROW = 39
DER_MAXIMUM_COLUMN = 71
#############################################################################

log_debug(system("free -mh", intern = FALSE))
save.image(file=paste0(out_file_path,"/",DER_TABLE_NAME,"_prep_env.RData"))