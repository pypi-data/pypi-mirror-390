source("../../Tables_Shared_Scripts/setup_environment.R", keep.source=TRUE)
source("util.R")

log_info("Running 11_Table3c_part1_prepare_datasets.R")
log_debug(system("free -mh", intern = FALSE))


collist <- c(
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
    "der_robbery",
    "der_stolen_property_offenses",
    "der_property_crime_all",
    "der_car_jacking"
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
        "der_victim_business",
        "der_victim_other_non_person",
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
#   filter(der_in_univ_elig == 1 & is.na(der_victim_person) )
main <- main[ , der_victim_person := fcase(victim_type_code %in% c("I","L"), 1, default = NA_real_)][, der_victim_LEO := fcase(
  victim_type_code %in% c("L"), 1,
  default = NA_real_
)][der_in_univ_elig == 1 & is.na(der_victim_person)]


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
DER_MAXIMUM_ROW = 2 #2 for this table since we processed Businesses and Other non-person victims separately
#############################################################################


log_debug(system("free -mh", intern = FALSE))
save.image(file=paste0(out_file_path,"/",DER_TABLE_NAME,"_prep_env.RData"))