log_debug(system("free -mh", intern = FALSE))

log_debug("Reading oriMappings")
oriMappings <- paste0(input_extract_folder,"ORI_VARIANCE.csv.gz") %>%
  fread(select=c("ORI","ORI_universe","LEGACY_ORI","ori",
                 "AGENCY_TYPE_NAME","PARENT_POP_GROUP_CODE","REGION_CODE","STATE_ABBR")) %>%
				 unique()
log_dim(oriMappings)
log_debug(system("free -mh", intern = FALSE))

log_debug("Creating uniqueOriMappings")
uniqueOriMappings <- dplyr::select(oriMappings,ORI,LEGACY_ORI,AGENCY_TYPE_NAME,PARENT_POP_GROUP_CODE,REGION_CODE,STATE_ABBR) %>% #,weight=NationalWgt) %>% 03Jul2023: need to merge on NationalWgt later to make sure still at ORI-level here
    unique() #03Jul2023: added unique() here to reflect new structure (ORI -> ORI x county)
log_dim(oriMappings)
log_debug(system("free -mh", intern = FALSE))

log_debug("Reading srs_smoothed")
srs2016_2020_smoothed <- fread("../../compute_weights/Data/srs2016_2020_smoothed.csv") %>%
    dplyr::select(LEGACY_ORI, matches("totcrime.*_imp"))
log_dim(srs2016_2020_smoothed)
log_debug(system("free -mh", intern = FALSE))

table_ORI_batch_paths <- list.files(
    path = output_copula_temp_folder,
    pattern = paste0("Table_", temp.table, "_ORI_all_",temp.perm,"_temp_step1_batch.*\\.csv\\.gz"),
    full.names = TRUE
)
for (table_ORI_batch_path in table_ORI_batch_paths) {
    log_debug(paste0("Reading ", table_ORI_batch_path))
    table_ORI_batch <- fread(table_ORI_batch_path)
    log_dim(table_ORI_batch)
    log_debug(system("free -mh", intern = FALSE))

    log_debug("Merging table_ORI_batch and uniqueOriMappings")
    table_ORI_batch <- table_ORI_batch %>%
        merge.data.table(uniqueOriMappings, by="LEGACY_ORI") %>%
        mutate(PARENT_POP_GROUP_CODE2=ifelse(PARENT_POP_GROUP_CODE %in% 1:2,
                                             1,
                                             PARENT_POP_GROUP_CODE-1))
    log_dim(table_ORI_batch)
    log_debug(system("free -mh", intern = FALSE))

    log_debug("Merging table_ORI_batch and srs")
    table_ORI_batch <- table_ORI_batch %>%
        merge.data.table(srs2016_2020_smoothed, by="LEGACY_ORI", all.x=TRUE)
    log_dim(table_ORI_batch)
    log_debug(system("free -mh", intern = FALSE))

    log_debug("Writing table_ORI_batch")
    fwrite(
        x = table_ORI_batch,
        file = gsub("step1", "step2", table_ORI_batch_path)
    )
    gc()
    log_debug(system("free -mh", intern = FALSE))
}

log_debug("End of script")
