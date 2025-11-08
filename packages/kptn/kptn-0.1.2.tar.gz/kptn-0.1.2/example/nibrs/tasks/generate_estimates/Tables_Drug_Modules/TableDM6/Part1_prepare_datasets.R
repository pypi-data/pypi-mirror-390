source("../../Tables_Shared_Scripts/setup_environment.R", keep.source=TRUE)
source("util.R")

log_info("Running 22_TableDM6_part1_prepare_datasets.R")
log_debug(system("free -mh", intern = FALSE))

raw_main <- fread(paste0(der_file_path, "recoded_all_Offenses_recoded_incident.csv.gz"))

#These are completed drug/narcotics incidents
agg_drug_narcotic_equipment_cat  <- fread(paste0(der_file_path, "agg_drug_narcotic_equipment_cat.csv.gz"))

#Need to create new indicator for table after merging
# raw_main <- raw_main0 %>% left_join(agg_drug_narcotic_equipment_cat %>% select(-count), by="incident_id")
raw_main <- merge(raw_main, agg_drug_narcotic_equipment_cat[,count:=NULL], by="incident_id", all.x=TRUE)

#raw_main2 <- raw_main %>% filter(der_drug_narcotic_equipment_cat %in% c(1,3))
raw_main <- raw_main[der_drug_narcotic_equipment_cat %in% c(1,3)]

#These are the incidents that either 1 suspected drug or 1 criminal activities
agg_1suspected_type_of_drug_1crim_activity_35A_c <- fread(paste0(der_file_path, "agg_1suspected_type_of_drug_1crim_activity_35A_c.csv.gz"))

#raw_main3 <- raw_main2 %>% left_join(agg_1suspected_type_of_drug_1crim_activity_35A_c %>% select(-count), by="incident_id")
raw_main <- merge(raw_main,agg_1suspected_type_of_drug_1crim_activity_35A_c[,count:=NULL], by="incident_id", all.x = TRUE)

#Filter to eligible agencies
main <- raw_main %>% clean_main()
log_debug("After running clean_main")
log_debug(system("free -mh", intern = FALSE))

agg_location_cat_1_10 <- fread(paste0(der_file_path, "agg_location_cat_1_10.csv.gz"))
agg_time_of_day_cat_incident <- fread(paste0(der_file_path, "agg_time_of_day_cat_incident.csv.gz"))
agg_time_of_day_cat_report <- fread(paste0(der_file_path, "agg_time_of_day_cat_report.csv.gz"))
ori_population_group_cat <- fread(paste0(der_file_path, "ori_population_group_cat.csv.gz"))
ori_agency_type_cat_1_7 <- fread(paste0(der_file_path, "ori_agency_type_cat_1_7.csv.gz"))
ori_msa_cat <- fread(paste0(der_file_path, "ori_msa_cat.csv.gz"))

agg_location_cat_1_11   	      <- fread(paste0(der_file_path, "agg_location_cat_1_11.csv.gz"))

collist <- c(
  "der_1suspected_type_of_drug_1crim_activity == 1",
  "der_1suspected_type_of_drug_1crim_activity == 2",
  "der_1suspected_type_of_drug_1crim_activity == 3",
  "der_1suspected_type_of_drug_1crim_activity == 6",
  "der_1suspected_type_of_drug_1crim_activity == 7",
  "der_1suspected_type_of_drug_1crim_activity == 8",
  "der_1suspected_type_of_drug_1crim_activity == 9",
  "der_1suspected_type_of_drug_1crim_activity == 10",
  "der_1suspected_type_of_drug_1crim_activity == 11",
  "der_1suspected_type_of_drug_1crim_activity == 14",
  "der_1suspected_type_of_drug_1crim_activity == 15",
  "der_1suspected_type_of_drug_1crim_activity == 16",
  "der_1suspected_type_of_drug_1crim_activity == 17",
  "der_1suspected_type_of_drug_1crim_activity == 18",
  "der_1suspected_type_of_drug_1crim_activity == 19",
  "der_1suspected_type_of_drug_1crim_activity == 22",
  "der_1suspected_type_of_drug_1crim_activity == 23",
  "der_1suspected_type_of_drug_1crim_activity == 24",
  "der_1suspected_type_of_drug_1crim_activity == 25",
  "der_1suspected_type_of_drug_1crim_activity == 26",
  "der_1suspected_type_of_drug_1crim_activity == 27",
  "der_1suspected_type_of_drug_1crim_activity == 30",
  "der_1suspected_type_of_drug_1crim_activity == 31",
  "der_1suspected_type_of_drug_1crim_activity == 32",
  "der_1suspected_type_of_drug_1crim_activity == 33",
  "der_1suspected_type_of_drug_1crim_activity == 34",
  "der_1suspected_type_of_drug_1crim_activity == 35",
  "der_1suspected_type_of_drug_1crim_activity == 38",
  "der_1suspected_type_of_drug_1crim_activity == 39",
  "der_1suspected_type_of_drug_1crim_activity == 40",
  "der_1suspected_type_of_drug_1crim_activity == 41",
  "der_1suspected_type_of_drug_1crim_activity == 42",
  "der_1suspected_type_of_drug_1crim_activity == 43",
  "der_1suspected_type_of_drug_1crim_activity == 46",
  "der_1suspected_type_of_drug_1crim_activity == 47",
  "der_1suspected_type_of_drug_1crim_activity == 48",
  "der_1suspected_type_of_drug_1crim_activity == 49",
  "der_1suspected_type_of_drug_1crim_activity == 50",
  "der_1suspected_type_of_drug_1crim_activity == 51",
  "der_1suspected_type_of_drug_1crim_activity == 54",
  "der_1suspected_type_of_drug_1crim_activity == 55",
  "der_1suspected_type_of_drug_1crim_activity == 56",
  "der_1suspected_type_of_drug_1crim_activity == 57",
  "der_1suspected_type_of_drug_1crim_activity == 58",
  "der_1suspected_type_of_drug_1crim_activity == 59",
  "der_1suspected_type_of_drug_1crim_activity == 62",
  "der_1suspected_type_of_drug_1crim_activity == 63",
  "der_1suspected_type_of_drug_1crim_activity == 64",
  "der_1suspected_type_of_drug_1crim_activity == 65",
  "der_1suspected_type_of_drug_1crim_activity == 66",
  "der_1suspected_type_of_drug_1crim_activity == 67",
  "der_1suspected_type_of_drug_1crim_activity == 70",
  "der_1suspected_type_of_drug_1crim_activity == 71",
  "der_1suspected_type_of_drug_1crim_activity == 72"
)

collist2 <- c(
  "der_1suspected_type_of_drug_1crim_activity %in%c(1, 2, 3, 6, 7, 8)",
  "der_1suspected_type_of_drug_1crim_activity %in%c(1, 2, 3, 6, 7, 8)",
  "der_1suspected_type_of_drug_1crim_activity %in%c(1, 2, 3, 6, 7, 8)",
  "der_1suspected_type_of_drug_1crim_activity %in%c(1, 2, 3, 6, 7, 8)",
  "der_1suspected_type_of_drug_1crim_activity %in%c(1, 2, 3, 6, 7, 8)",
  "der_1suspected_type_of_drug_1crim_activity %in%c(1, 2, 3, 6, 7, 8)",
  "der_1suspected_type_of_drug_1crim_activity %in%c(9, 10, 11, 14, 15, 16)",
  "der_1suspected_type_of_drug_1crim_activity %in%c(9, 10, 11, 14, 15, 16)",
  "der_1suspected_type_of_drug_1crim_activity %in%c(9, 10, 11, 14, 15, 16)",
  "der_1suspected_type_of_drug_1crim_activity %in%c(9, 10, 11, 14, 15, 16)",
  "der_1suspected_type_of_drug_1crim_activity %in%c(9, 10, 11, 14, 15, 16)",
  "der_1suspected_type_of_drug_1crim_activity %in%c(9, 10, 11, 14, 15, 16)",
  "der_1suspected_type_of_drug_1crim_activity %in%c(17, 18, 19, 22, 23, 24)",
  "der_1suspected_type_of_drug_1crim_activity %in%c(17, 18, 19, 22, 23, 24)",
  "der_1suspected_type_of_drug_1crim_activity %in%c(17, 18, 19, 22, 23, 24)",
  "der_1suspected_type_of_drug_1crim_activity %in%c(17, 18, 19, 22, 23, 24)",
  "der_1suspected_type_of_drug_1crim_activity %in%c(17, 18, 19, 22, 23, 24)",
  "der_1suspected_type_of_drug_1crim_activity %in%c(17, 18, 19, 22, 23, 24)",
  "der_1suspected_type_of_drug_1crim_activity %in%c(25, 26, 27, 30, 31, 32)",
  "der_1suspected_type_of_drug_1crim_activity %in%c(25, 26, 27, 30, 31, 32)",
  "der_1suspected_type_of_drug_1crim_activity %in%c(25, 26, 27, 30, 31, 32)",
  "der_1suspected_type_of_drug_1crim_activity %in%c(25, 26, 27, 30, 31, 32)",
  "der_1suspected_type_of_drug_1crim_activity %in%c(25, 26, 27, 30, 31, 32)",
  "der_1suspected_type_of_drug_1crim_activity %in%c(25, 26, 27, 30, 31, 32)",
  "der_1suspected_type_of_drug_1crim_activity %in%c(33, 34, 35, 38, 39, 40)",
  "der_1suspected_type_of_drug_1crim_activity %in%c(33, 34, 35, 38, 39, 40)",
  "der_1suspected_type_of_drug_1crim_activity %in%c(33, 34, 35, 38, 39, 40)",
  "der_1suspected_type_of_drug_1crim_activity %in%c(33, 34, 35, 38, 39, 40)",
  "der_1suspected_type_of_drug_1crim_activity %in%c(33, 34, 35, 38, 39, 40)",
  "der_1suspected_type_of_drug_1crim_activity %in%c(33, 34, 35, 38, 39, 40)",
  "der_1suspected_type_of_drug_1crim_activity %in%c(41, 42, 43, 46, 47, 48)",
  "der_1suspected_type_of_drug_1crim_activity %in%c(41, 42, 43, 46, 47, 48)",
  "der_1suspected_type_of_drug_1crim_activity %in%c(41, 42, 43, 46, 47, 48)",
  "der_1suspected_type_of_drug_1crim_activity %in%c(41, 42, 43, 46, 47, 48)",
  "der_1suspected_type_of_drug_1crim_activity %in%c(41, 42, 43, 46, 47, 48)",
  "der_1suspected_type_of_drug_1crim_activity %in%c(41, 42, 43, 46, 47, 48)",
  "der_1suspected_type_of_drug_1crim_activity %in%c(49, 50, 51, 54, 55, 56)",
  "der_1suspected_type_of_drug_1crim_activity %in%c(49, 50, 51, 54, 55, 56)",
  "der_1suspected_type_of_drug_1crim_activity %in%c(49, 50, 51, 54, 55, 56)",
  "der_1suspected_type_of_drug_1crim_activity %in%c(49, 50, 51, 54, 55, 56)",
  "der_1suspected_type_of_drug_1crim_activity %in%c(49, 50, 51, 54, 55, 56)",
  "der_1suspected_type_of_drug_1crim_activity %in%c(49, 50, 51, 54, 55, 56)",
  "der_1suspected_type_of_drug_1crim_activity %in%c(57, 58, 59, 62, 63, 64)",
  "der_1suspected_type_of_drug_1crim_activity %in%c(57, 58, 59, 62, 63, 64)",
  "der_1suspected_type_of_drug_1crim_activity %in%c(57, 58, 59, 62, 63, 64)",
  "der_1suspected_type_of_drug_1crim_activity %in%c(57, 58, 59, 62, 63, 64)",
  "der_1suspected_type_of_drug_1crim_activity %in%c(57, 58, 59, 62, 63, 64)",
  "der_1suspected_type_of_drug_1crim_activity %in%c(57, 58, 59, 62, 63, 64)",
  "der_1suspected_type_of_drug_1crim_activity %in%c(65, 66, 67, 70, 71, 72)",
  "der_1suspected_type_of_drug_1crim_activity %in%c(65, 66, 67, 70, 71, 72)",
  "der_1suspected_type_of_drug_1crim_activity %in%c(65, 66, 67, 70, 71, 72)",
  "der_1suspected_type_of_drug_1crim_activity %in%c(65, 66, 67, 70, 71, 72)",
  "der_1suspected_type_of_drug_1crim_activity %in%c(65, 66, 67, 70, 71, 72)",
  "der_1suspected_type_of_drug_1crim_activity %in%c(65, 66, 67, 70, 71, 72)"
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
DER_MAXIMUM_ROW = 53
#############################################################################


log_debug(system("free -mh", intern = FALSE))
save.image(file=paste0(out_file_path,"/",DER_TABLE_NAME,"_prep_env.RData"))