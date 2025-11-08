#Create ORI-level data to use throughout copula imputation (for a given table)
#Note: For 3a, get warning about "The size of the connection buffer (131072)
#      was not large enough to fit a complete line"
#      In response, temporarily update environment variable then revert back
#Note (28Jun2023): Switching from agency-level pop to (agency X county)-level pop
#vrcs <- Sys.getenv("VROOM_CONNECTION_SIZE")
#Sys.setenv("VROOM_CONNECTION_SIZE"=1e6)
library(data.table)

log_debug(system("free -mh", intern = FALSE))

# list of demographic tables to check against
demo_table_list <- c("3a", "3aunclear", "3aclear", "3b", "3bunclear", "3bclear",  "4a", "4b", "5a", "5b", "DM7", "DM9", "DM10", "GV2a")

log_debug("Reading table_ORI_raw")
if (temp.table %in% demo_table_list) {
  table_ORI_raw <- file.path(input_estimate_folder,
                           paste0("Table ",temp.table," ORI_",temp.perm,".csv.gz")) %>%
    fread()
} else {
  table_ORI_raw <- file.path(input_estimate_folder,
                           paste0("Table ",temp.table," ORI.csv.gz")) %>%
  fread()
}

#Sys.setenv("VROOM_CONNECTION_SIZE"=vrcs)
log_dim(table_ORI_raw)
log_debug(system("free -mh", intern = FALSE))

log_debug("Reading srs_smoothed")
srs2016_2020_smoothed <- fread("../../compute_weights/Data/srs2016_2020_smoothed.csv")
log_dim(srs2016_2020_smoothed)
log_debug(system("free -mh", intern = FALSE))

#Note (12Jul2023): Since we don't need to worry about county-level info until step 2, can drop down to ORI-level
log_debug("Reading oriMappings")
oriMappings <- paste0(input_extract_folder,"ORI_VARIANCE.csv.gz") %>%
  fread(select=c("ORI","ORI_universe","LEGACY_ORI","ori",
                 "AGENCY_TYPE_NAME","PARENT_POP_GROUP_CODE","REGION_CODE","STATE_ABBR")) %>%
				 unique()
log_dim(oriMappings)
log_debug(system("free -mh", intern = FALSE))

#Add ORI to table_ORI
log_debug("Merging oriMappings with table_ORI_raw")
table_ORI <- oriMappings %>% 
  dplyr::select(ORI=ORI_universe,ori) %>% 
  unique() %>% #03Jul2023: Adding to reflect change in structure (ORI -> ORI x county)
  merge.data.table(table_ORI_raw,by="ori") %>%
  dplyr::select(-ori)
rm(table_ORI_raw)
log_dim(table_ORI)
log_debug(system("free -mh", intern = FALSE))

#First: get list of UCR-only LEAs (e.g., not NIBRS responders)
#Update (02MAR2022): Renaming indicator table's ORI to LEGACY_ORI yields better join 
log_debug("Getting list of UCR-only ORIs")
nibrsORIs <- table_ORI %>%
  #select(ORI=ori)
  dplyr::select(LEGACY_ORI=ORI)
log_dim(nibrsORIs)

log_debug("Creating allORIs")
allORIs <- oriMappings %>%
  select(LEGACY_ORI) %>%
  subset(duplicated(LEGACY_ORI)==FALSE)
log_dim(allORIs)

ucrOnlyORIs <- anti_join(allORIs,nibrsORIs,by="LEGACY_ORI")
log_dim(ucrOnlyORIs)
log_debug(system("free -mh", intern = FALSE))

log_debug("Creating table_ORI_all")
#Stack NIBRS+UCR only
#Note (JDB 09MAY2022): Drop 'weight' from original file and replace with weight from ORI_VARIANCE
#Note (JDB 09MAY2022): Add sourceInd (SRS vs. NIBRS) here
table_ORI_all <- list(table_ORI %>%
                        rename(LEGACY_ORI=ORI),
                      ucrOnlyORIs) %>%
  rbindlist(fill=TRUE) %>%#bind_rows(table_ORI,table_ORI_ucrOnly) %>%
  #dplyr::select(colnames(table_ORI)) %>%
  dplyr::select(-weight)
log_dim(table_ORI_all)
log_debug(system("free -mh", intern = FALSE))

log_debug("Writing table_ORI_all in batches")

batch_size <- 5000
batch_starts <- seq(from = 1, to = nrow(table_ORI_all), by = batch_size)
batch_counter <- 0

for (batch_start in batch_starts) {
    batch_counter <- batch_counter + 1
    batch_end <- min(batch_start + batch_size - 1, nrow(table_ORI_all))
    batch_filename <- paste0("/Table_", temp.table, "_ORI_all_",temp.perm,"_temp_step1_batch", batch_counter, ".csv.gz")

    log_debug(paste0("Writing table_ORI_all batch ", batch_counter, " [rows ", batch_start, "-", batch_end, "]"))
    fwrite(
        x = table_ORI_all[batch_start:batch_end],
        file = file.path(output_copula_temp_folder, batch_filename)
    )
    gc()
    log_debug(system("free -mh", intern = FALSE))
}

log_debug("End of script")
