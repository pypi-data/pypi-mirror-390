#Create county-level version of the SRS calibration variables

#MSA frame (with FO/JD/MSA calibration variables at ORI-level)
msaDat <- paste0(output_weighting_data_folder,"SF_postMSA_cal_srs_altcombs_col_srs.csv") %>%
  read_csv_logging()
  
#judicial district frame (just using temporarily to pull wgtGpJD)
jdDat <- paste0(output_weighting_data_folder,"SF_postJD_cal_srs_altcombs_col_srs.csv") %>%
  read_csv_logging()
#County-level file
SF <- paste0(output_weighting_data_folder,"SF_srs.csv") %>%
  read_csv_logging()


#FO crosses
foCrosses <- paste0(input_weighting_data_folder,"Geography_Crossings_SRS.xlsx") %>%
  read_xlsx(sheet="FO") %>%
  rename(FIELD_OFFICE_NAME=foLvl,
         wgtGpFO=foWgtGp,
         crossNum=foCrossNum)

#JD crosses
jdCrosses <- paste0(input_weighting_data_folder,"Geography_Crossings_SRS.xlsx") %>%
  read_xlsx(sheet="JD") %>%
  rename(JUDICIAL_DISTRICT_NAME=jdLvl,
         wgtGpJD=jdWgtGp,
         crossNum=jdCrossNum)

#MSA crosses
msaCrosses <- paste0(input_weighting_data_folder,"Geography_Crossings_SRS.xlsx") %>%
  read_xlsx(sheet="MSA") %>%
  rename(MSA_NAME_COUNTY=msaLvl,
         wgtGpMSA=msaWgtGp,
         crossNum=msaCrossNum)


#Identify calibration variables in (ORI x county)-level file
calVars2 <- bind_rows(foCrosses,
                      jdCrosses,
                      msaCrosses) %>%
  pull(crossNum) %>%
  {outer(paste0("V",.,"_"),
         paste0(c("A","B","C","D","E","F","G","H","I","J","K")),
         paste0)} %>% 
  as.character() %>%
  subset(. %in% colnames(msaDat)) %>%
  str_sort(numeric=TRUE)


calVarsDat <- msaDat %>%
  select(-matches("wgtGpJD")) %>%
  left_join(jdDat %>% select(ORI_universe,county,JUDICIAL_DISTRICT_NAME,wgtGpJD)) %>%
  left_join(jdCrosses %>% select(JUDICIAL_DISTRICT_NAME,wgtGpJD,crossNum)) %>%
  #14Mar2024: including RTI population (popResidAgcyCounty_cbi), population proportion by county (propPOP1), and metro division (METRO_DIVISION_COUNTY)
  #19Apr2024: swapping out propPOP1 and swapping in propMult
  #select(ORI_universe,county,crossNum,popResidAgcyCounty_cbi=POP1,propPOP1,REGION_CODE=REGION_CODE_UNIV,STATE_ABBR=STATE_ABBR_UNIV,METRO_DIVISION_COUNTY,all_of(calVars2)) %>%
  select(ORI_universe,county,crossNum,popResidAgcyCounty_cbi,propMult,REGION_CODE=REGION_CODE_UNIV,STATE_ABBR=STATE_ABBR_UNIV,METRO_DIVISION_COUNTY,all_of(calVars2)) %>%
  mutate(across(all_of(calVars2),~ifelse(is.na(.x),0,.x)))
  
calVarsDat %>%
  write_csv_logging(file=paste0(output_weighting_data_folder,"County_Level_Calibration_Variable_File_SRS.csv"))