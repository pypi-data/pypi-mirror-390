source("../../Tables_Shared_Scripts/setup_environment.R", keep.source=TRUE)
source("util.R")

log_info("Running 29_TableGV2a_part1_prepare_datasets.R")
log_debug(system("free -mh", intern = FALSE))

collist <- c(
  "der_against_person",
  "der_total_gun_violence",
  "der_fatal_gun_violence",
  "der_nonfatal_gun_violence",
  "der_nonfatal_gun_violence2",
  "der_murder_non_neg_manslaughter",
  "der_neg_manslaughter",
  "der_revised_rape",
  "der_robbery",
  "der_aggravated_assault",
  "der_kidnapping_abduction",
  "der_human_trafficking_offenses",
  "der_car_jacking"				   
)

#Try using offense file
main <- fread(
  file = paste0(der_file_path, "cleaned_recoded_all_Firearm_Offenses_recoded_offenses.csv.gz"),
  select = c(
    "ori",
    "weight",
    "victim_type_code",
    "der_in_univ_elig",
    "incident_id",
    "victim_id",
    "offense_id",
    "der_offender_id_exclude",
    collist
  )
)

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
#   filter(der_in_univ_elig == 1 & der_victim_person == 1)

main <- main[ , der_victim_person := fcase(victim_type_code %in% c("I","L"), 1, default = NA_real_)][, der_victim_LEO := fcase(
  victim_type_code %in% c("L"), 1,
  default = NA_real_
)][der_in_univ_elig == 1 & der_victim_person == 1]

#agg_victim_age_cat
# der_victim_age_cat = fcase( 0 <= der_victim_age  & der_victim_age < 5 , 1, #Under 5
#                             5 <= der_victim_age  & der_victim_age < 15, 2, #5-14
#                             15 <= der_victim_age & der_victim_age < 18, 3, #15-17
#                             18 <= der_victim_age & der_victim_age < 25, 4, #18-24
#                             25 <= der_victim_age & der_victim_age < 35, 5, #25-34
#                             35 <= der_victim_age & der_victim_age < 65, 6, #35-64
#                             65 <= der_victim_age                      , 7, #65+
#                             victim_age_code %in% c("00","NS")                   , 8, #Unknown or not Specified

agg_victim_age_cat_victim <- fread(paste0(der_file_path, "agg_victim_age_cat_victim_imp.csv.gz"))

# der_victim_age_cat_2_uo18 = fcase( 0 <= der_victim_age  & der_victim_age < 18 , 1, #Under 18
#                                    18 <= der_victim_age                        , 2, #18+
#                                    victim_age_code %in% c("00","NS")                     , 3, #Unknown or Not Specified
#                                    default = 3 # Unknown
# ),

agg_victim_age_cat_2_uo18_victim <- fread(paste0(der_file_path, "agg_victim_age_cat_2_uo18_victim_imp.csv.gz"))


# der_victim_age_cat_under18_2 = fcase( 0 <= der_victim_age  & der_victim_age  < 12, 1, #Under 12
#                                       12 <= der_victim_age  & der_victim_age < 18, 2 #12-17
# ),     

agg_victim_age_cat_under18_2_victim <- fread(paste0(der_file_path, "agg_victim_age_cat_under18_2_victim_imp.csv.gz"))

# mutate(der_number_of_victims_cat = fcase(
#   raw_victim_count == 1, 1, # 1
#   raw_victim_count == 2, 2, # 2
#   raw_victim_count == 3, 3, # 3
#   raw_victim_count  > 3, 4 # 4+
# ), 

agg_number_of_victims_cat <- fread(paste0(der_file_path, "agg_number_of_victims_cat.csv.gz"))


# der_victim_gender = fcase(trim_upper(victim_sex_code)  == "M", 1,
#                           trim_upper(victim_sex_code)  == "F", 2,
#                           trim_upper(victim_sex_code)  == "U", 3,
#                           default = 3 # Unknown
# ),

#der_victim_gender
agg_victim_gender_victim <- fread(paste0(der_file_path, "agg_victim_gender_victim_imp.csv.gz"))

# der_victim_race = fcase(
#   victim_race_code == "W" , 1, #White:  White
#   victim_race_code == "B" , 2, #Black or African American:  Black
#   victim_race_code == "I" , 3, #American Indian or Alaska Native:  American Indian or Alaska Native
#   victim_race_code == "A" , 4, #Asian:  Asian
#   victim_race_code == "AP" , 4, #Asian, Native Hawaiian, or Other Pacific Islander:  Asian
#   victim_race_code == "C" , 4, #Chinese:  Asian
#   victim_race_code == "J" , 4, #Japanese:  Asian
#   victim_race_code == "P" , 5, #Native Hawaiian or Other Pacific Islander:  Native Hawaiian or Other Pacific Islander
#   victim_race_code == "U" , 6, # Unknown
#   default = 6 ),             # O (Other), M (Multiple), NS (Not Specified)

#der_victim_race
agg_victim_race_victim <- fread(paste0(der_file_path, "agg_victim_race_victim_imp.csv.gz"))

#der_victim_murder_non_neg_manslaughter
#1 = Yes
#2 = No
agg_victim_murder_non_neg_manslaughter_victim <- fread(paste0(der_file_path, "agg_victim_murder_non_neg_manslaughter_victim.csv.gz"))


#der_number_of_victims_firearm_cat.csv.gz
# mutate(der_number_of_victims_firearm_cat = fcase(
#   raw_victim_count == 1, 1, # 1
#   raw_victim_count == 2, 2, # 2
#   raw_victim_count == 3, 3, # 3
#   raw_victim_count  > 3, 4 # 4+
# ), 

agg_number_of_victims_firearm_cat <- fread(paste0(der_file_path, "agg_number_of_victims_firearm_cat.csv.gz"))

#Injury hierarchy 
# Major injury (other major injury, severe laceration, possible internal injury)
# Unconsciousness, apparent broken bones, loss of teeth
# Apparent minor injury
# No injury

agg_injury_hierarchy_victim <- fread(paste0(der_file_path, "agg_injury_hierarchy_victim.csv.gz"))

# Injury hierarchy 2
# Other major injury
# Severe laceration, possible internal injury
# Unconsciousness, apparent broken bones, loss of teeth
# Apparent minor injury
# No injury

agg_injury_hierarchy2_victim <- fread(paste0(der_file_path, "agg_injury_hierarchy2_victim.csv.gz"))

# Victim-offender relationship hierarchy
# Intimate partner
# Other family
# Outside family but known to victim
# Stranger
# Victim was Offender
# Unknown relationship
# Unknown Offender Incidents
# Missing from Uncleared Incidents

agg_relationship_hierarchy_victim <- fread(paste0(der_file_path, "agg_relationship_hierarchy_victim_imp.csv.gz"))

#Subset to known offenders
# Victim-offender relationship hierarchy among known offenders
# Intimate partner
# Other family
# Outside family but known to victim
# Stranger
# Victim was Offender
# Unknown relationship

agg_relationship_hierarchy_victim_known <- agg_relationship_hierarchy_victim %>%
  #Filter to the known relationship
  filter(der_relationship_hierarchy %in% c(1:6)) %>%
  #Rename the variable for easier assignment
  rename(der_relationship_hierarchy_victim_known = der_relationship_hierarchy)

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




###################Additional extract for demographic permutations###############################

# der_victim_age_cat_15_17 = fcase( 0 <= der_victim_age  & der_victim_age < 5, 1, #Under 5
#                                   5 <= der_victim_age  & der_victim_age < 15, 2, #5-14
#                                   der_victim_age == 15, 3, #15
#                                   der_victim_age == 16, 4, #16
#                                   der_victim_age == 17, 5, #17
#                                   18 <= der_victim_age & der_victim_age < 25, 6, #18-24
#                                   25 <= der_victim_age & der_victim_age < 35, 7, #25-34
#                                   35 <= der_victim_age & der_victim_age < 65, 8, #35-64
#                                   65 <= der_victim_age, 9, #65+
#                                   victim_age_code %in% code %in% c("00","NS"), 10, #Unknown or Not Specified
#                                   default = 10 # Unknown
# ),


#der_victim_age_cat_15_17
agg_victim_age_cat_15_17_victim <- fread(paste0(der_file_path, "agg_victim_age_cat_15_17_victim_imp.csv.gz"))

#Create a generic age variable for subsetting in demographic permutations.  Should have range of 0 - 99
#der_victim_age_round = floor(der_victim_age),

agg_victim_age_round_victim <- fread(paste0(der_file_path, "agg_victim_age_round_victim_imp.csv.gz"))


#################################################################################################



main <- merge(main, agg_victim_age_cat_15_17_victim[,.(incident_id, victim_id, der_new_column_age=der_victim_age_cat_15_17)],
              by = c("incident_id","victim_id"), all.x = TRUE)
log_dim(main)

log_debug(system("free -mh", intern = FALSE))


log_dim(main)
main <- merge(main, agg_victim_gender_victim[,.(incident_id, victim_id, der_new_column_gender=der_victim_gender)],
              by = c("incident_id","victim_id"), all.x = TRUE)
log_dim(main)

log_debug(system("free -mh", intern = FALSE))
log_dim(main)
main <- merge(main, agg_victim_race_victim[,.(incident_id, victim_id, der_new_column_race=der_victim_race)],
              by = c( "incident_id", "victim_id"), all.x = TRUE)
log_dim(main)
log_debug(system("free -mh", intern = FALSE))
log_dim(main)

main <- merge(main, agg_victim_ethnicity_victim[,.(incident_id, victim_id, der_new_column_ethnicity=der_victim_ethnicity)],
              by = c( "incident_id", "victim_id"), all.x = TRUE)
log_dim(main)
log_debug(system("free -mh", intern = FALSE))



#For Any other victim ages
main <- merge(main, agg_victim_age_round_victim[,.(incident_id, victim_id, der_new_column_age_round=der_victim_age_round)],
              by = c("incident_id","victim_id"), all.x = TRUE)

log_dim(main)


log_debug("After all of the main merges")
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

##########################Set the variables for table #######################
DER_MAXIMUM_ROW = 73
DER_MAXIMUM_COLUMN = 13
#############################################################################
log_debug(system("free -mh", intern = FALSE))
save.image(file=paste0(out_file_path,"/",DER_TABLE_NAME,"_prep_env.RData"))
