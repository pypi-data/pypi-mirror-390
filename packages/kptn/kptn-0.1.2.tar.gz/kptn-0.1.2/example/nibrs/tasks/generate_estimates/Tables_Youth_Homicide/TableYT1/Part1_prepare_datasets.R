source("../../Tables_Shared_Scripts/setup_environment.R", keep.source=TRUE)
source("util.R")

log_info("Running 36_TableYT1_part1_prepare_datasets.R")
log_debug(system("free -mh", intern = FALSE))

#Try using offense file
collist <- c(
	"der_murder_non_neg_manslaughter"
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
        "der_offender_id_exclude",
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
#   filter(der_in_univ_elig == 1 & der_victim_person == 1)

main <- main[ , der_victim_person := fcase(victim_type_code %in% c("I","L"), 1, default = NA_real_)][, der_victim_LEO := fcase(
  victim_type_code %in% c("L"), 1,
  default = NA_real_
)][der_in_univ_elig == 1 & der_victim_person == 1]

#Subset to individuals aged 12-17################################
#Create a generic age variable for subsetting in demographic permutations.  Should have range of 0 - 99
#der_victim_age_round = floor(der_victim_age),

agg_victim_age_round_victim <- fread(paste0(der_file_path, "agg_victim_age_round_victim_imp.csv.gz"))

log_debug("Before subset")
#For Any other victim ages
main <- merge(main, agg_victim_age_round_victim[,.(incident_id, victim_id, der_new_column_age_round=der_victim_age_round)],
              by = c("incident_id","victim_id"), all.x = TRUE)

log_dim(main)

main <- main [ (12 <= der_new_column_age_round) & (der_new_column_age_round < 18) ]

log_debug("After subset")
log_debug(system("free -mh", intern = FALSE))

#Read in the additional extracts needed 

#der_victim_age_cat_12_17_cat
#1, #12-14
#2, #15-17
agg_victim_age_cat_12_17_cat_victim_imp <- fread(paste0(der_file_path, "agg_victim_age_cat_12_17_cat_victim_imp.csv.gz"))

#der_victim_gender
# "M" ~ 1,
# "F" ~ 2,
# "U" ~ 3,
agg_victim_gender_victim_imp <- fread(paste0(der_file_path, "agg_victim_gender_victim_imp.csv.gz"))

#der_victim_ethnicity
# 1, #Hispanic or Latino
# 2, #Not Hispanic or Latino
# 3),  #Multiple/Unknown/Not Specified
agg_victim_ethnicity_victim_imp <- fread(paste0(der_file_path, "agg_victim_ethnicity_victim_imp.csv.gz"))

#der_victim_eth_race
# 1:    Hispanic or Latino White
# 2:    Hispanic or Latino Black
# 3:    Hispanic or Latino Other Race (i.e. American Indian or Alaska Native/Asian/Native Hawaiian or Other Pacific Islander)
# 4:    Hispanic or Latino Unknown Race
# 5:    Not Hispanic or Latino White
# 6:    Not Hispanic or Latino Black
# 7:    Not Hispanic or Latino Other Race (i.e. American Indian or Alaska Native/Asian/Native Hawaiian or Other Pacific Islander)
# 8:    Not Hispanic or Latino Unknown Race
# 9:     Multiple/Unknown/Not Specified White
# 10:     Multiple/Unknown/Not Specified Black
# 11:     Multiple/Unknown/Not Specified Other Race (i.e. American Indian or Alaska Native/Asian/Native Hawaiian or Other Pacific Islander)
# 12:     Multiple/Unknown/Not Specified Unknown Race

#der_victim_offender_gender_1_4
agg_victim_eth_race_victim_imp <- fread(paste0(der_file_path, "agg_victim_eth_race_victim_imp.csv.gz"))


log_debug("After all of the extracts read in")
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
DER_MAXIMUM_ROW = 21
DER_MAXIMUM_COLUMN = 1
#############################################################################

log_debug(system("free -mh", intern = FALSE))
save.image(file=paste0(out_file_path,"/",DER_TABLE_NAME,"_prep_env.RData"))
