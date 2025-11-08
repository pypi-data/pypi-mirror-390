source("../../Tables_Shared_Scripts/setup_environment.R", keep.source=TRUE)
source("util.R")

log_info("Running 28_TablGV1a_part1_prepare_datasets.R")
log_debug(system("free -mh", intern = FALSE))

collist <- c(
  "der_against_person",
  "der_total_gun_violence_no_rob",
  "der_fatal_gun_violence",
  "der_nonfatal_gun_violence_no_rob",
  "der_nonfatal_gun_violence2_no_rob",
  "der_murder_non_neg_manslaughter",
  "der_neg_manslaughter",
  "der_revised_rape",
  "der_robbery",
  "der_aggravated_assault",
  "der_kidnapping_abduction",
  "der_human_trafficking_offenses",
  "der_car_jacking"
)


main <- fread(
  file = paste0(der_file_path, "cleaned_recoded_all_Firearm_Offenses_recoded_offenses.csv.gz"),
  select = c(
    "ori",
    "weight",
    "incident_id",
    "victim_id",
    "offense_id",
    collist
  )
)

# Firearm type
# Multiple firearm types

agg_single_multi_firearm_types_offenses <- fread(paste0(der_file_path, "agg_single_multi_firearm_types_offenses.csv.gz"))


# Single gun type
# Handgun only
# Long gun (Rifle and Shotgun) only
# Unknown firearm type (Other Firearm and Firearm) only

agg_single_gun_cat_offenses <- fread(paste0(der_file_path, "agg_single_gun_cat_offenses.csv.gz"))

# Location Type 4
# Residence
# Hotel
# Transportation hub/outdoor public locations
# Schools, daycares, and universities
# Retail/financial/other commercial establishment
# Restaurant/bar/sports or entertainment venue
# Religious buildings
# Government/public buildings
# Jail/prison
# Shelter-mission/homeless
# Drug Store/Doctor’s Office/Hospital
# Other/unknown location

agg_location_1_12_offenses <- fread(paste0(der_file_path, "agg_location_1_12_offenses.csv.gz"))


log_debug("After reading in main")
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
DER_MAXIMUM_ROW = 19
#############################################################################


log_debug(system("free -mh", intern = FALSE))
save.image(file=paste0(out_file_path,"/",DER_TABLE_NAME,"_prep_env.RData"))
