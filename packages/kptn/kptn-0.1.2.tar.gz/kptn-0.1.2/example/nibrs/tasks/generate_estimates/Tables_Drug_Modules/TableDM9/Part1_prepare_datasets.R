source("../../Tables_Shared_Scripts/setup_environment.R", keep.source=TRUE)
source("util.R")

log_info("Running 25_TableDM9_part1_prepare_datasets.R")
log_debug(system("free -mh", intern = FALSE))


raw_main <- fread(paste0(der_file_path, "recoded_all_Offenses_recoded_arrestee.csv.gz"))

#These are completed drug/narcotics incidents
agg_drug_narcotic_equipment_cat  				      <- fread(paste0(der_file_path, "agg_drug_narcotic_equipment_cat.csv.gz"))

dim(raw_main)
#Need to create new indicator for table after merging
# raw_main <- raw_main0 %>%
#   left_join(agg_drug_narcotic_equipment_cat %>% select(-count), by="incident_id")
raw_main <- merge(raw_main, agg_drug_narcotic_equipment_cat[,count:=NULL], by="incident_id", all.x=TRUE)

dim(agg_drug_narcotic_equipment_cat)
dim(raw_main)

#raw_main2 <- raw_main %>%
#Filter to drug/narcotic violations (35A)
#der_drug_narcotic_any == 1 & der_drug_equipment_any == 1 ~ 3, #Both drug/narcotic and drug equipment violations
#der_drug_narcotic_any == 1 ~ 1, #Only drug/narcotic violations
#Note this variable contains completed offenses
#filter(der_drug_narcotic_equipment_cat %in% c(1,3))

raw_main <- raw_main[der_drug_narcotic_equipment_cat %in% c(1,3)]

dim(raw_main)

#Check the recodes

#Subset to include the subset of completed drug/narcotic offenses without multiple suspected drug types AND multiple criminal activities

#Subset to include the subset of completed multiple drug/narcotic offenses AND multiple criminal activities
agg_suspected_type_of_drug_crim_activity_35A_c <- fread(paste0(der_file_path, "agg_suspected_type_of_drug_crim_activity_35A_c.csv.gz"))

# raw_main3 <- raw_main2 %>%
#   left_join(agg_suspected_type_of_drug_crim_activity_35A_c %>% select(-count), by="incident_id")
raw_main <- merge(raw_main, agg_suspected_type_of_drug_crim_activity_35A_c[,count:=NULL], by="incident_id", all.x = TRUE)

#Note that agg_suspected_type_of_drug_crim_activity_35A_c is a incident level with multiple levels due to the drug cross activity codes.
dim(raw_main)

#Filter to eligible agencies
main <- raw_main %>% clean_main()
log_debug("After running clean_main")
log_debug(system("free -mh", intern = FALSE))

#Delete the raw datasets
remove(list=ls(pattern="raw_main"))
invisible(gc())

#der_arrestee_age_cat
agg_arrestee_age_cat_arrestee <- fread(paste0(der_file_path, "agg_arrestee_age_cat_arrestee_imp.csv.gz"))

#der_arrestee_gender
agg_arrestee_gender_arrestee <- fread(paste0(der_file_path, "agg_arrestee_gender_arrestee_imp.csv.gz"))

#der_arrestee_race
agg_arrestee_race_arrestee <- fread(paste0(der_file_path, "agg_arrestee_race_arrestee_imp.csv.gz"))


#der_arrestee_gender_race
agg_arrestee_gender_race_arrestee <- fread(paste0(der_file_path, "agg_arrestee_gender_race_arrestee_imp.csv.gz"))

# agg_arrestee_gender_race_arrestee_male <- agg_arrestee_gender_race_arrestee %>%
#   filter(der_arrestee_gender_race %in% c(1:6) )
agg_arrestee_gender_race_arrestee_male <- agg_arrestee_gender_race_arrestee[der_arrestee_gender_race %in% c(1:6)]

# agg_arrestee_gender_race_arrestee_female <- agg_arrestee_gender_race_arrestee %>%
#   filter(der_arrestee_gender_race %in% c(7:12) )
agg_arrestee_gender_race_arrestee_female <- agg_arrestee_gender_race_arrestee[der_arrestee_gender_race %in% c(7:12)]

# agg_arrestee_gender_race_arrestee_unknown <- agg_arrestee_gender_race_arrestee %>%
#   filter(der_arrestee_gender_race %in% c(13:18) )
agg_arrestee_gender_race_arrestee_unknown <- agg_arrestee_gender_race_arrestee[der_arrestee_gender_race %in% c(13:18)]

#der_juvenile_disp
agg_juvenile_disp_arrestee <- fread(paste0(der_file_path, "agg_juvenile_disp_arrestee_imp.csv.gz"))

#der_multiple_arrest
agg_multiple_arrest_arrestee  	  <- fread(paste0(der_file_path, "agg_multiple_arrest_arrestee_imp.csv.gz"))

###Weapon at Arrestee Level - Armed with #####

#der_weapon_no_yes
agg_weapon_no_yes_arrestee  	  <- fread(paste0(der_file_path, "agg_weapon_no_yes_arrestee.csv.gz"))

#Deduplication
agg_weapon_no_yes_arrestee <- agg_to_1(agg_weapon_no_yes_arrestee) %>%
  keep_to_yes_arrestee(yesstring = "der_weapon_no_yes == 2" ) #Keep Yes Category if have both yes and no incidents

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




#Demographics
agg_arrestee_age_cat_15_17_arrestee  	  <- fread(paste0(der_file_path, "agg_arrestee_age_cat_15_17_arrestee.csv.gz"))

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

log_dim(main)


collist <- c(
  "der_suspected_type_of_drug_crim_activity == 1",
  "der_suspected_type_of_drug_crim_activity == 2",
  "der_suspected_type_of_drug_crim_activity == 3",
  "der_suspected_type_of_drug_crim_activity == 6",
  "der_suspected_type_of_drug_crim_activity == 7",
  "der_suspected_type_of_drug_crim_activity == 8",
  "der_suspected_type_of_drug_crim_activity == 9",
  "der_suspected_type_of_drug_crim_activity == 10",
  "der_suspected_type_of_drug_crim_activity == 11",
  "der_suspected_type_of_drug_crim_activity == 14",
  "der_suspected_type_of_drug_crim_activity == 15",
  "der_suspected_type_of_drug_crim_activity == 16",
  "der_suspected_type_of_drug_crim_activity == 17",
  "der_suspected_type_of_drug_crim_activity == 18",
  "der_suspected_type_of_drug_crim_activity == 19",
  "der_suspected_type_of_drug_crim_activity == 22",
  "der_suspected_type_of_drug_crim_activity == 23",
  "der_suspected_type_of_drug_crim_activity == 24",
  "der_suspected_type_of_drug_crim_activity == 25",
  "der_suspected_type_of_drug_crim_activity == 26",
  "der_suspected_type_of_drug_crim_activity == 27",
  "der_suspected_type_of_drug_crim_activity == 30",
  "der_suspected_type_of_drug_crim_activity == 31",
  "der_suspected_type_of_drug_crim_activity == 32",
  "der_suspected_type_of_drug_crim_activity == 33",
  "der_suspected_type_of_drug_crim_activity == 34",
  "der_suspected_type_of_drug_crim_activity == 35",
  "der_suspected_type_of_drug_crim_activity == 38",
  "der_suspected_type_of_drug_crim_activity == 39",
  "der_suspected_type_of_drug_crim_activity == 40",
  "der_suspected_type_of_drug_crim_activity == 41",
  "der_suspected_type_of_drug_crim_activity == 42",
  "der_suspected_type_of_drug_crim_activity == 43",
  "der_suspected_type_of_drug_crim_activity == 46",
  "der_suspected_type_of_drug_crim_activity == 47",
  "der_suspected_type_of_drug_crim_activity == 48",
  "der_suspected_type_of_drug_crim_activity == 49",
  "der_suspected_type_of_drug_crim_activity == 50",
  "der_suspected_type_of_drug_crim_activity == 51",
  "der_suspected_type_of_drug_crim_activity == 54",
  "der_suspected_type_of_drug_crim_activity == 55",
  "der_suspected_type_of_drug_crim_activity == 56",
  "der_suspected_type_of_drug_crim_activity == 57",
  "der_suspected_type_of_drug_crim_activity == 58",
  "der_suspected_type_of_drug_crim_activity == 59",
  "der_suspected_type_of_drug_crim_activity == 62",
  "der_suspected_type_of_drug_crim_activity == 63",
  "der_suspected_type_of_drug_crim_activity == 64",
  "der_suspected_type_of_drug_crim_activity == 65",
  "der_suspected_type_of_drug_crim_activity == 66",
  "der_suspected_type_of_drug_crim_activity == 67",
  "der_suspected_type_of_drug_crim_activity == 70",
  "der_suspected_type_of_drug_crim_activity == 71",
  "der_suspected_type_of_drug_crim_activity == 72"
)

collist2 <- c(
  "der_suspected_type_of_drug_crim_activity %in%c(1, 2, 3, 6, 7, 8)",
  "der_suspected_type_of_drug_crim_activity %in%c(1, 2, 3, 6, 7, 8)",
  "der_suspected_type_of_drug_crim_activity %in%c(1, 2, 3, 6, 7, 8)",
  "der_suspected_type_of_drug_crim_activity %in%c(1, 2, 3, 6, 7, 8)",
  "der_suspected_type_of_drug_crim_activity %in%c(1, 2, 3, 6, 7, 8)",
  "der_suspected_type_of_drug_crim_activity %in%c(1, 2, 3, 6, 7, 8)",
  "der_suspected_type_of_drug_crim_activity %in%c(9, 10, 11, 14, 15, 16)",
  "der_suspected_type_of_drug_crim_activity %in%c(9, 10, 11, 14, 15, 16)",
  "der_suspected_type_of_drug_crim_activity %in%c(9, 10, 11, 14, 15, 16)",
  "der_suspected_type_of_drug_crim_activity %in%c(9, 10, 11, 14, 15, 16)",
  "der_suspected_type_of_drug_crim_activity %in%c(9, 10, 11, 14, 15, 16)",
  "der_suspected_type_of_drug_crim_activity %in%c(9, 10, 11, 14, 15, 16)",
  "der_suspected_type_of_drug_crim_activity %in%c(17, 18, 19, 22, 23, 24)",
  "der_suspected_type_of_drug_crim_activity %in%c(17, 18, 19, 22, 23, 24)",
  "der_suspected_type_of_drug_crim_activity %in%c(17, 18, 19, 22, 23, 24)",
  "der_suspected_type_of_drug_crim_activity %in%c(17, 18, 19, 22, 23, 24)",
  "der_suspected_type_of_drug_crim_activity %in%c(17, 18, 19, 22, 23, 24)",
  "der_suspected_type_of_drug_crim_activity %in%c(17, 18, 19, 22, 23, 24)",
  "der_suspected_type_of_drug_crim_activity %in%c(25, 26, 27, 30, 31, 32)",
  "der_suspected_type_of_drug_crim_activity %in%c(25, 26, 27, 30, 31, 32)",
  "der_suspected_type_of_drug_crim_activity %in%c(25, 26, 27, 30, 31, 32)",
  "der_suspected_type_of_drug_crim_activity %in%c(25, 26, 27, 30, 31, 32)",
  "der_suspected_type_of_drug_crim_activity %in%c(25, 26, 27, 30, 31, 32)",
  "der_suspected_type_of_drug_crim_activity %in%c(25, 26, 27, 30, 31, 32)",
  "der_suspected_type_of_drug_crim_activity %in%c(33, 34, 35, 38, 39, 40)",
  "der_suspected_type_of_drug_crim_activity %in%c(33, 34, 35, 38, 39, 40)",
  "der_suspected_type_of_drug_crim_activity %in%c(33, 34, 35, 38, 39, 40)",
  "der_suspected_type_of_drug_crim_activity %in%c(33, 34, 35, 38, 39, 40)",
  "der_suspected_type_of_drug_crim_activity %in%c(33, 34, 35, 38, 39, 40)",
  "der_suspected_type_of_drug_crim_activity %in%c(33, 34, 35, 38, 39, 40)",
  "der_suspected_type_of_drug_crim_activity %in%c(41, 42, 43, 46, 47, 48)",
  "der_suspected_type_of_drug_crim_activity %in%c(41, 42, 43, 46, 47, 48)",
  "der_suspected_type_of_drug_crim_activity %in%c(41, 42, 43, 46, 47, 48)",
  "der_suspected_type_of_drug_crim_activity %in%c(41, 42, 43, 46, 47, 48)",
  "der_suspected_type_of_drug_crim_activity %in%c(41, 42, 43, 46, 47, 48)",
  "der_suspected_type_of_drug_crim_activity %in%c(41, 42, 43, 46, 47, 48)",
  "der_suspected_type_of_drug_crim_activity %in%c(49, 50, 51, 54, 55, 56)",
  "der_suspected_type_of_drug_crim_activity %in%c(49, 50, 51, 54, 55, 56)",
  "der_suspected_type_of_drug_crim_activity %in%c(49, 50, 51, 54, 55, 56)",
  "der_suspected_type_of_drug_crim_activity %in%c(49, 50, 51, 54, 55, 56)",
  "der_suspected_type_of_drug_crim_activity %in%c(49, 50, 51, 54, 55, 56)",
  "der_suspected_type_of_drug_crim_activity %in%c(49, 50, 51, 54, 55, 56)",
  "der_suspected_type_of_drug_crim_activity %in%c(57, 58, 59, 62, 63, 64)",
  "der_suspected_type_of_drug_crim_activity %in%c(57, 58, 59, 62, 63, 64)",
  "der_suspected_type_of_drug_crim_activity %in%c(57, 58, 59, 62, 63, 64)",
  "der_suspected_type_of_drug_crim_activity %in%c(57, 58, 59, 62, 63, 64)",
  "der_suspected_type_of_drug_crim_activity %in%c(57, 58, 59, 62, 63, 64)",
  "der_suspected_type_of_drug_crim_activity %in%c(57, 58, 59, 62, 63, 64)",
  "der_suspected_type_of_drug_crim_activity %in%c(65, 66, 67, 70, 71, 72)",
  "der_suspected_type_of_drug_crim_activity %in%c(65, 66, 67, 70, 71, 72)",
  "der_suspected_type_of_drug_crim_activity %in%c(65, 66, 67, 70, 71, 72)",
  "der_suspected_type_of_drug_crim_activity %in%c(65, 66, 67, 70, 71, 72)",
  "der_suspected_type_of_drug_crim_activity %in%c(65, 66, 67, 70, 71, 72)",
  "der_suspected_type_of_drug_crim_activity %in%c(65, 66, 67, 70, 71, 72)"
)

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
DER_MAXIMUM_ROW = 65
DER_MAXIMUM_COLUMN = 54
#############################################################################

log_debug(system("free -mh", intern = FALSE))
save.image(file=paste0(out_file_path,"/",DER_TABLE_NAME,"_prep_env.RData"))