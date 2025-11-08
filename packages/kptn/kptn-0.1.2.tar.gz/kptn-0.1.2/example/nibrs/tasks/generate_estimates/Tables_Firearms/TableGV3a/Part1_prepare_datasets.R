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
  file = paste0(der_file_path, "cleaned_recoded_all_Firearm_Offenses_recoded_incident.csv.gz"),
  select = c(
    "ori",
    "weight",
    "incident_id",
    "offense_id",
    collist
  )
)

# Number of Offenders
# 1
# 2
# 3
# 4+
#   Unknown Offender Incidents

agg_offender_cat <- fread(paste0(der_file_path, "agg_offender_cat.csv.gz"))


# Clearance
# Not cleared
# Cleared through arrest
# Exceptional clearance

agg_clearance_cat <- fread(paste0(der_file_path, "agg_clearance_cat.csv.gz"))

#   Death of offender
#   Prosecution declined
#   In custody of other jurisdiction
#   Victim refused to cooperate
#   Juvenile/no custody

agg_exception_clearance_cat <- fread(paste0(der_file_path, "agg_exception_clearance_cat.csv.gz"))


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
DER_MAXIMUM_ROW = 15
DER_MAXIMUM_COLUMN = 13
#############################################################################
log_debug(system("free -mh", intern = FALSE))
save.image(file=paste0(out_file_path,"/",DER_TABLE_NAME,"_prep_env.RData"))
