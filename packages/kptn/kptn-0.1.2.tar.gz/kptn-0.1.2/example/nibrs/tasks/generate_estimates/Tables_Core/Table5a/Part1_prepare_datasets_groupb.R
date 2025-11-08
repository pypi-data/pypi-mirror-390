log_info("Running 26_Table5a_Part1_prepare_datasets_groupb.R")
log_debug(system("free -mh", intern = FALSE))

main_group_b <- fread(
    file = paste0(der_file_path, "cleaned_recoded_all_recoded_arrestee_groupb_arrest_code.csv.gz"),
    select = c(
        "ori",
        "weight",
        "groupb_arrestee_id",
        collist
    )
) %>%
  #Group B arrestee does not have car jacking since there is no incident report
  #Create variable so variable exists
  mutate(der_car_jacking = 0)


log_debug("After reading in main_group_b")
log_debug(system("free -mh", intern = FALSE))




#der_arrest_type
agg_arrest_type_arrestee_groupb <- fread(paste0(der_file_path, "agg_arrest_type_arrestee_groupb.csv.gz"))

#der_arrestee_age_cat_15_17
agg_arrestee_age_cat_15_17_arrestee_groupb <- fread(paste0(der_file_path, "agg_arrestee_age_cat_15_17_arrestee_groupb_imp.csv.gz"))

#der_arrestee_gender
agg_arrestee_gender_arrestee_groupb <- fread(paste0(der_file_path, "agg_arrestee_gender_arrestee_groupb_imp.csv.gz"))

#der_arrestee_race
agg_arrestee_race_arrestee_groupb <- fread(paste0(der_file_path, "agg_arrestee_race_arrestee_groupb_imp.csv.gz"))


#der_arrestee_gender_race
agg_arrestee_gender_race_arrestee_groupb <- fread(paste0(der_file_path, "agg_arrestee_gender_race_arrestee_groupb_imp.csv.gz"))

# agg_arrestee_gender_race_arrestee_male <- agg_arrestee_gender_race_arrestee %>%
#   filter(der_arrestee_gender_race %in% c(1:6) )
agg_arrestee_gender_race_arrestee_groupb_male <- agg_arrestee_gender_race_arrestee_groupb[der_arrestee_gender_race %in% c(1:6)]

# agg_arrestee_gender_race_arrestee_groupb_female <- agg_arrestee_gender_race_arrestee_groupb %>%
#   filter(der_arrestee_gender_race %in% c(7:12) )
agg_arrestee_gender_race_arrestee_groupb_female <- agg_arrestee_gender_race_arrestee_groupb[der_arrestee_gender_race %in% c(7:12)]

# agg_arrestee_gender_race_arrestee_groupb_unknown <- agg_arrestee_gender_race_arrestee_groupb %>%
#   filter(der_arrestee_gender_race %in% c(13:18) )
agg_arrestee_gender_race_arrestee_groupb_unknown <- agg_arrestee_gender_race_arrestee_groupb[der_arrestee_gender_race %in% c(13:18)]

#der_juvenile_disp
agg_juvenile_disp_arrestee_groupb <- fread(paste0(der_file_path, "agg_juvenile_disp_arrestee_groupb_imp.csv.gz"))

#der_multiple_arrest
#Group B does not have multiple arrest
#agg_multiple_arrest_arrestee_groupb  	  <- fread(paste0(der_file_path, "agg_multiple_arrest_arrestee_groupb_imp.csv.gz"))


###Weapon at Arrestee Level - Armed with #####

#der_weapon_no_yes
agg_weapon_no_yes_arrestee_groupb  	  <- fread(paste0(der_file_path, "agg_weapon_no_yes_arrestee_groupb.csv.gz"))

#Deduplication
agg_weapon_no_yes_arrestee_groupb <- agg_to_1(agg_weapon_no_yes_arrestee_groupb)

#der_weapon_yes_cat
agg_weapon_yes_cat_arrestee_groupb 		<- fread(paste0(der_file_path, "agg_weapon_yes_cat_arrestee_groupb.csv.gz"))


#####################Group B arrestee does not have incident level data##################################
# ###Weapon at Incident Level - Weapon involved #####
# 
# #der_weapon_no_yes
# agg_weapon_no_yes  	  <- fread(paste0(der_file_path, "agg_weapon_no_yes.csv.gz"))
# 
# #Deduplication
# agg_weapon_no_yes <- agg_to_1(agg_weapon_no_yes) %>%
#   keep_to_yes(yesstring = "der_weapon_no_yes == 2" ) #Keep Yes Category if have both yes and no incidents
# 
# 
# #der_weapon_yes_cat
# agg_weapon_yes_cat  	  <- fread(paste0(der_file_path, "agg_weapon_yes_cat.csv.gz"))

############################################Arrestee age 2##################################################################
# der_arrestee_age_cat_under18_2 = fcase( 0 <= der_arrestee_age  & der_arrestee_age  < 12, 1, #Under 12
#                                       12 <= der_arrestee_age  & der_arrestee_age < 18, 2 #12-17
# ),

agg_arrestee_age_cat_under18_2_arrestee_groupb_imp <- fread(paste0(der_file_path, "agg_arrestee_age_cat_under18_2_arrestee_groupb_imp.csv.gz"))

# der_arrestee_age_cat_12_17_cat = fcase( 12 <= der_arrestee_age  & der_arrestee_age  < 15, 1, #12-14
#                                      15 <= der_arrestee_age  & der_arrestee_age < 18, 2 #15-17
# ),

agg_arrestee_age_cat_12_17_cat_arrestee_groupb_imp <- fread(paste0(der_file_path, "agg_arrestee_age_cat_12_17_cat_arrestee_groupb_imp.csv.gz"))


# der_arrestee_age_cat_2_uo18 = fcase( 0 <= der_arrestee_age  & der_arrestee_age < 18 , 1, #Under 18
#                                    18 <= der_arrestee_age                        , 2, #18+
#                                    arrestee_age_code %in% c("00","NS")                    , 3, #Unknown or Not Specified
#                                    default = 3 # Unknown
# ),

agg_arrestee_age_cat_2_uo18_arrestee_groupb_imp <- fread(paste0(der_file_path, "agg_arrestee_age_cat_2_uo18_arrestee_groupb_imp.csv.gz"))

#############################################################################################################################

#Arrestee Hispanic Origin
# der_arrestee_ethnicity = fcase(arrestee_ethnicity_code == "H", 1, #Hispanic or Latino
#                                arrestee_ethnicity_code == "N", 2, #Not Hispanic or Latino
#                                default= 3),  #Multiple/Unknown/Not Specified	

agg_arrestee_ethnicity_arrestee_groupb <- fread(paste0(der_file_path, "agg_arrestee_ethnicity_arrestee_groupb_imp.csv.gz"))

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

agg_arrestee_ethnicity_race_arrestee_groupb <- fread(paste0(der_file_path, "agg_arrestee_ethnicity_race_arrestee_groupb_imp.csv.gz"))




log_dim(main_group_b)
log_debug(system("free -mh", intern = FALSE))

main_group_b <- merge(main_group_b, agg_arrestee_age_cat_15_17_arrestee_groupb[,.( groupb_arrestee_id, der_new_column_age = der_arrestee_age_cat_15_17)],
              by = c("groupb_arrestee_id"), all.x = TRUE)
log_dim(main_group_b)


log_dim(main_group_b)
log_debug(system("free -mh", intern = FALSE))
main_group_b <- merge(main_group_b, agg_arrestee_gender_arrestee_groupb[,.( groupb_arrestee_id, der_new_column_gender = der_arrestee_gender)],
              by = c("groupb_arrestee_id"), all.x = TRUE)
log_dim(main_group_b)

log_dim(main_group_b)
log_debug(system("free -mh", intern = FALSE))
main_group_b <- merge(main_group_b, agg_arrestee_race_arrestee_groupb[,.( groupb_arrestee_id, der_new_column_race = der_arrestee_race)],
              by = c("groupb_arrestee_id"), all.x = TRUE)

log_dim(main_group_b)

main_group_b <- merge(main_group_b, agg_arrestee_ethnicity_arrestee_groupb[,.( groupb_arrestee_id, der_new_column_ethnicity=der_arrestee_ethnicity)],
              by = c(  "groupb_arrestee_id"), all.x = TRUE)
log_dim(main_group_b)
log_debug(system("free -mh", intern = FALSE))

#Create a generic age variable for subsetting in demographic permutations.  Should have range of 0 - 99
#der_arrestee_age_round = floor(der_arrestee_age),

agg_arrestee_age_round_arrestee_groupb <- fread(paste0(der_file_path, "agg_arrestee_age_round_arrestee_groupb_imp.csv.gz"))

#For Any other arrestee ages
main_group_b <- merge(main_group_b, agg_arrestee_age_round_arrestee_groupb[,.( groupb_arrestee_id, der_new_column_age_round=der_arrestee_age_round)],
              by = c("groupb_arrestee_id"), all.x = TRUE)
