#21Jun2023: Need to tweak sub-state weights so that math works during later tasks (e.g. variance step)
#19Apr2024: instead of propPOP1, use newly created propMult variable to update the weights
log_info("Started 07_Adjust_Substate_Weights_SRS.R\n\n")

weights_jd <- paste0(output_weighting_data_folder,
                     "weights_jd_cal_srs_altcombs_col_srs.csv") %>%
  read_csv_logging()

weights_msa <- paste0(output_weighting_data_folder,
                      "weights_MSA_cal_srs_altcombs_col_srs.csv") %>%
  read_csv_logging()

weights_fo <- paste0(output_weighting_data_folder,
                     "weights_FO_cal_srs_altcombs_col_srs.csv") %>%
  read_csv_logging()

sf <- paste0(output_weighting_data_folder, "SF_srs.csv") %>%
  read_csv_logging() %>%
  #select(ORI_universe,county,propPOP1)
  select(ORI_universe,county,propMult)

#if (!"propPOP1" %in% colnames(weights_jd)){
if (!"propMult" %in% colnames(weights_jd)){
  message("Updating JD weights")
  weights_jd2 <- weights_jd %>%
    full_join(sf) %>%
    #mutate(JDWgt=JDWgt*propPOP1)
    mutate(JDWgt=JDWgt*propMult)
  weights_jd2 %>%
    write_csv_logging(file=paste0(output_weighting_data_folder,
                                  "weights_jd_cal_srs_altcombs_col_srs.csv"))
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
                                  "weights_MSA_cal_srs_altcombs_col_srs.csv"))
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
                                  "weights_FO_cal_srs_altcombs_col_srs.csv"))
}

log_info("Finished 07_Adjust_Substate_Weights_SRS.R\n\n")
