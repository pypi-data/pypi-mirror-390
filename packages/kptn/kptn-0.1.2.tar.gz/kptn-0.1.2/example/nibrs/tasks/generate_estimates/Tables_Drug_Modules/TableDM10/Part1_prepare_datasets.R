source("../../Tables_Shared_Scripts/setup_environment.R", keep.source=TRUE)
source("util.R")

log_info("Running 31_TableDM10_part1_prepare_datasets.R")
log_debug(system("free -mh", intern = FALSE))


collist <- c(
    "der_drug_narcotic_inc",
    "der_crim_activity_drug_poss_traff_35A_c_inc",
    "der_crim_activity_drug_poss_pc_35A_c_inc",
    "der_crim_activity_drug_poss_npc_35A_c_inc"
)

main <- fread(
    file = paste0(der_file_path, "cleaned_recoded_all_Offenses_recoded_arrestee.csv.gz"),
    select = c(
        "ori",
        "weight",
        "incident_id",
        "arrestee_id",
        collist
    )
) %>%
  #Create a new variable to count the number of arrestee
  mutate(der_total_arrest = 1)

log_debug("After reading in main")
log_debug(system("free -mh", intern = FALSE))

#Read in additional offense indicator with the following variables
# der_drug_narcotic_inc
# der_crim_activity_drug_poss_traff_35A_c_inc
# der_crim_activity_drug_poss_pc_35A_c_inc
# der_crim_activity_drug_poss_npc_35A_c_inc

drug_module_inc_additional_offenses <- fread(paste0(der_file_path, "drug_module_inc_additional_offenses.csv.gz"))

log_dim(main)
log_debug(system("free -mh", intern = FALSE))

main <- merge(main, drug_module_inc_additional_offenses,
              by = c("incident_id"), all.x = TRUE)
log_dim(main)


#der_arrestee_gender
agg_arrestee_gender_arrestee <- fread(paste0(der_file_path, "agg_arrestee_gender_arrestee_imp.csv.gz"))


#Arrestee Hispanic Origin
# der_arrestee_ethnicity = fcase(arrestee_ethnicity_code == "H", 1, #Hispanic or Latino
#                                arrestee_ethnicity_code == "N", 2, #Not Hispanic or Latino
#                                default= 3),  #Multiple/Unknown/Not Specified	

agg_arrestee_ethnicity_arrestee <- fread(paste0(der_file_path, "agg_arrestee_ethnicity_arrestee_imp.csv.gz"))


#############################################################################################################################

#Get dataset files for demographic permutations
#der_arrestee_age_cat_15_17
agg_arrestee_age_cat_15_17_arrestee <- fread(paste0(der_file_path, "agg_arrestee_age_cat_15_17_arrestee_imp.csv.gz"))

#der_arrestee_race
agg_arrestee_race_arrestee <- fread(paste0(der_file_path, "agg_arrestee_race_arrestee_imp.csv.gz"))


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
DER_MAXIMUM_ROW = 3
DER_MAXIMUM_COLUMN = 4
#############################################################################


log_debug(system("free -mh", intern = FALSE))
save.image(file=paste0(out_file_path,"/",DER_TABLE_NAME,"_prep_env.RData"))
