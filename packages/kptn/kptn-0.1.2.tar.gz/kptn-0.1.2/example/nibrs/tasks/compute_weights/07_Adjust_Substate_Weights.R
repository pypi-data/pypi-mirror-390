#21Jun2023: Need to tweak sub-state weights so that math works during later tasks (e.g. variance step)

log_info("Started 07_Adjust_Substate_Weights.R\n\n")

weights_jd <- paste0(output_weighting_data_folder,
                     "weights_jd_cal_srs_altcombs_col.csv") %>%
  read_csv_logging()

weights_msa <- paste0(output_weighting_data_folder,
                      "weights_MSA_cal_srs_altcombs_col.csv") %>%
  read_csv_logging()

weights_fo <- paste0(output_weighting_data_folder,
                     "weights_FO_cal_srs_altcombs_col.csv") %>%
  read_csv_logging()

sf <- paste0(output_weighting_data_folder,
               "SF_county.csv") %>%
    read_csv_logging() %>%
    #select(ORI_universe,county,propPOP1)
    select(ORI_universe,county,propMult)

#02May2024: replacing propPOP1 with propMult
#if (!"propPOP1" %in% colnames(weights_jd)){
if (!"propMult" %in% colnames(weights_jd)){
  message("Updating JD weights")
  weights_jd2 <- weights_jd %>%
    full_join(sf) %>%
    #mutate(JDWgt=JDWgt*propPOP1)
    mutate(JDWgt=JDWgt*propMult)
  weights_jd2 %>%
    write_csv_logging(file=paste0(output_weighting_data_folder,
                                  "weights_jd_cal_srs_altcombs_col.csv"))
} else {
  stop("ERROR: propMult already existed on weights_jd_cal_srs_altcombs_col.csv before this step.")
}

#if (!"propPOP1" %in% colnames(weights_msa)){
if (!"propMult" %in% colnames(weights_msa)){
  message("Updating MSA weights")
  weights_msa2 <- weights_msa %>%
    full_join(sf) %>%
    #mutate(MSAWgt=MSAWgt*propPOP1)
    mutate(MSAWgt=MSAWgt*propMult)
  weights_msa2 %>%
    write_csv_logging(file=paste0(output_weighting_data_folder,
                                  "weights_MSA_cal_srs_altcombs_col.csv"))
} else {
  stop("ERROR: propMult already existed on weights_MSA_cal_srs_altcombs_col.csv before this step.")
}

#if (!"propPOP1" %in% colnames(weights_fo)){
if (!"propMult" %in% colnames(weights_fo)){
  message("Updating FO weights")
  weights_fo2 <- weights_fo %>%
    full_join(sf) %>%
    #mutate(FOWgt=FOWgt*propPOP1)
    mutate(FOWgt=FOWgt*propMult)
  weights_fo2 %>%
    write_csv_logging(file=paste0(output_weighting_data_folder,
                                  "weights_FO_cal_srs_altcombs_col.csv"))
} else {
  stop("ERROR: propMult already existed on weights_FO_cal_srs_altcombs_col.csv before this step.")
}


log_info("Finished 07_Adjust_Substate_Weights.R\n\n")
