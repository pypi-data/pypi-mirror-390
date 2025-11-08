source("../../Tables_Shared_Scripts/setup_environment.R", keep.source=TRUE)
source("util.R")

log_info("Running 18_TableDM2_part1_prepare_datasets.R")
log_debug(system("free -mh", intern = FALSE))

raw_main <- fread(paste0(der_file_path, "recoded_all_Offenses_recoded_incident.csv.gz"))

log_debug("After running clean_main")
log_debug(system("free -mh", intern = FALSE))

agg_drug_narcotic_equipment_cat <- fread(paste0(der_file_path, "agg_drug_narcotic_equipment_cat.csv.gz"))

#Need to create new indicator for table after merging
# raw_main <- main %>%
#   left_join(agg_drug_narcotic_equipment_cat  %>% select(-count), by="incident_id") %>%
#   mutate(der_35A_c = fcase(der_drug_narcotic_equipment_cat %in% c(1,3), 1, default = 0))
raw_main <- merge(raw_main, agg_drug_narcotic_equipment_cat[,count:=NULL], by="incident_id", all.x=TRUE)
raw_main <- raw_main[,der_35A_c := fcase(der_drug_narcotic_equipment_cat %in% c(1,3), 1, default = 0)]

log_dim(raw_main)
log_dim(agg_drug_narcotic_equipment_cat)


#Filter to eligible agencies
main <- raw_main %>%  clean_main()

# agg_crim_activity_35A_c <- read_csv(file=gzfile(paste0(der_file_path, "agg_crim_activity_35A_c.csv.gz"))) %>%
#   filter(der_crim_activity_35A_c %in% c(1:8) )
agg_crim_activity_35A_c <- fread(paste0(der_file_path, "agg_crim_activity_35A_c.csv.gz"))
agg_crim_activity_35A_c <- agg_crim_activity_35A_c[der_crim_activity_35A_c %in% c(1:8)]

#Need to bring in additional extracts
agg_crim_activity_drug_poss_traff_35A_c  <- fread(paste0(der_file_path, "agg_crim_activity_drug_poss_traff_35A_c.csv.gz"))
agg_crim_activity_drug_poss_pc_35A_c     <- fread(paste0(der_file_path, "agg_crim_activity_drug_poss_pc_35A_c.csv.gz"))
agg_crim_activity_drug_poss_npc_35A_c    <- fread(paste0(der_file_path, "agg_crim_activity_drug_poss_npc_35A_c.csv.gz"))

collist <- c(
    "der_35A_c"
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
DER_MAXIMUM_ROW = 12
#############################################################################

log_debug(system("free -mh", intern = FALSE))
save.image(file=paste0(out_file_path,"/",DER_TABLE_NAME,"_prep_env.RData"))