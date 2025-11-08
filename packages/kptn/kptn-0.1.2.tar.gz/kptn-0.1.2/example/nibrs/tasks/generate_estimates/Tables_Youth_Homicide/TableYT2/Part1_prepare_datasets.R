source("../../Tables_Shared_Scripts/setup_environment.R", keep.source=TRUE)
source("util.R")

log_info("Running 37_TableYT2_part1_prepare_datasets.R")
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


#Read in the additional extracts needed 

  #der_offender_age_12_plus_missing_unk_inc
  #Incident level data with the following values:
  # 1, #Offender aged 12 or older
  # 1, #Offender age is unknown
  # 1, #Unknown offender incidents

agg_offender_age_12_plus_missing_unk_inc_inc_imp <- read_csv(file=gzfile(paste0(der_file_path, "agg_offender_age_12_plus_missing_unk_inc_inc_imp.csv.gz"))) 

  #der_offender_cat_12_17
  #Incident level data with the following values:
  #1, #12-17

agg_offender_cat_12_17_inc_imp <- fread(paste0(der_file_path, "agg_offender_cat_12_17_inc_imp.csv.gz"))

  #der_offender_cat_18_plus
  #Incident level data with the following values:
  #1, #18 or older

agg_offender_cat_18_plus_inc_imp <- fread(paste0(der_file_path, "agg_offender_cat_18_plus_inc_imp.csv.gz"))

  #der_offender_age_missing
  #Incident level data with the following values:
  #1, #Known offender age missing  

agg_offender_age_missing_inc_imp <- fread(paste0(der_file_path, "agg_offender_age_missing_inc_imp.csv.gz")) 

  #der_unknown_offender_incident
  #Incident level data with the following values:
  #1, #Unknown offender incidents
agg_unknown_offender_incident_inc_imp <- fread(paste0(der_file_path, "agg_unknown_offender_incident_inc_imp.csv.gz"))




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
DER_MAXIMUM_ROW = 5
DER_MAXIMUM_COLUMN = 1
#############################################################################

log_debug(system("free -mh", intern = FALSE))
save.image(file=paste0(out_file_path,"/",DER_TABLE_NAME,"_prep_env.RData"))
