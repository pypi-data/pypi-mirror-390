log_debug(system("free -mh", intern = FALSE))

# list of demographic tables to check against
demo_table_list <- c("3a", "3aunclear", "3aclear", "3b", "3bunclear", "3bclear",  "4a", "4b", "5a", "5b", "DM7", "DM9", "DM10", "GV2a")

log_debug("Creating temp.tocVars")
if (temp.table %in% demo_table_list) {
    temp.allVars <-file.path(input_estimate_folder,
                         paste0("Table ",temp.table," ORI_",temp.perm,".csv.gz")) %>%
    #read_csv(n_max=0) %>%
    fread(nrows=0) %>%
    colnames() 
} else {
    temp.allVars <-file.path(input_estimate_folder,
                         paste0("Table ",temp.table," ORI.csv.gz")) %>%
    #read_csv(n_max=0) %>%
    fread(nrows=0) %>%
    colnames()
}
#Note (JDB 09MAY2022): Adding code to set missing toc variables to 0 for NIBRS LEAs (should only affect a few hundred LEAs with weights but no incidents)
temp.tocVars <- temp.allVars %>% str_subset("^t_")
log_debug(paste0("Number of tocVars: ", length(temp.tocVars)))
log_debug(system("free -mh", intern = FALSE))

log_debug("Splitting temp.tocVars into chunks")
chunk_size <- 5000
chunked_toc_vars <- split(temp.tocVars, ceiling(seq_along(temp.tocVars) / chunk_size))
log_debug(paste0("Number of chunks: ", length(chunked_toc_vars)))
log_debug(paste0(
    "Size of each chunk: ",
    paste0(sapply(chunked_toc_vars, function(chunk) { length(chunk) }), collapse=", ")
))
log_debug(system("free -mh", intern = FALSE))


table_ORI_batch_paths <- list.files(
    path = output_copula_temp_folder,
    pattern = paste0("Table_", temp.table, "_ORI_all_",temp.perm,"_temp_step3_batch.*\\.csv\\.gz"),
    full.names = TRUE
)
for (table_ORI_batch_path in table_ORI_batch_paths) {
    log_debug(paste0("Reading ", table_ORI_batch_path))
    table_ORI_batch <- fread(table_ORI_batch_path)
    orig_col_order <- names(table_ORI_batch)
    num_rows <- nrow(table_ORI_batch)
    log_dim(table_ORI_batch)
    log_debug(system("free -mh", intern = FALSE))

    isNIBRS <- table_ORI_batch$sourceInd == "NIBRS"

    # We found that operating on columns at the beginning of the data table is
    # much faster than columns at the end. To take advantage of that, perform
    # the recodes on small-ish chunks of columns, reordering the columns before
    # each chunk so that the chunk is at the beginning of the data table.
    #Note (03May2024): Swapping out references to propPOP1 in favor of propMult
    #Note (09Jul2025): Forcing product of t_ variables and propMult to be double
    chunk_count <- 0
    for (toc_vars in chunked_toc_vars) {
        chunk_count <- chunk_count + 1
        log_debug(paste0("Processing chunk ", chunk_count, " of toc vars"))

        log_debug("Reordering columns")
        #used_vars <- c("sourceInd", "propPOP1", toc_vars)
        used_vars <- c("sourceInd", "propMult", toc_vars)
        unused_vars <- setdiff(names(table_ORI_batch), used_vars)
        new_col_order <- c(used_vars, unused_vars)
        setcolorder(table_ORI_batch, new_col_order)
        log_dim(table_ORI_batch)
        log_debug(system("free -mh", intern = FALSE))

        #log_debug("Recode NA -> 0 for NIBRS, multiply by propPOP1 for SRS")
        log_debug("Recode NA -> 0 for NIBRS, multiply by propMult for SRS")
        table_ORI_batch <- table_ORI_batch %>%
            mutate(across(all_of(toc_vars),
                          ~fcase(isNIBRS & is.na(.), 0.0,
                                 #isNIBRS, .x * propPOP1,
                                 isNIBRS, as.double(.x * propMult),
                                 rep_len(TRUE, num_rows), as.double(.))))
        log_dim(table_ORI_batch)
        log_debug(system("free -mh", intern = FALSE))
        setDT(table_ORI_batch)
    }

    #table_ORI_batch %>% colnames() %>% str_subset("^pct",negate=TRUE) %>% str_subset("^t_1a",negate=TRUE)

    log_debug("Restoring original column order")
    setcolorder(table_ORI_batch, orig_col_order)
    log_dim(table_ORI_batch)
    log_debug(system("free -mh", intern = FALSE))

    log_debug("Appending table_ORI_batch to final csv")
    fwrite(
        x = table_ORI_batch,
        file = file.path(output_copula_data_folder, paste0("Table_", temp.table, "_ORI_all_",temp.perm,".csv")),
        append = table_ORI_batch_path != table_ORI_batch_paths[1]
    )
    gc()
    log_debug(system("free -mh", intern = FALSE))
}

log_debug("End of script")
