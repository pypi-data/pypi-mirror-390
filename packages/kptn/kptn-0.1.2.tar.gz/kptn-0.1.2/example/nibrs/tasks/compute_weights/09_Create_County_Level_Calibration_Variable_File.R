#Create county-level version of the NIBRS calibration variables

#14May2025: manually specifying guess_rows parameter for read_csv_logging() calls

#State frame (with national/region/state calibration variables at ORI-level)
stateDat <- paste0(output_weighting_data_folder,"SF_postS.csv") %>%
  read_csv_logging(guess_max=Inf)

#MSA frame (with FO/JD/MSA calibration variables at ORI-level)
msaDat <- paste0(output_weighting_data_folder,"SF_postMSA_cal_srs_altcombs_col.csv") %>%
  read_csv_logging(guess_max=Inf)

#County-level file
SF <- paste0(output_weighting_data_folder,"SF_county.csv") %>%
  read_csv_logging(guess_max=Inf)

#National crosses
natCrosses <- paste0(input_weighting_data_folder,"Geography_Crossings.xlsx") %>%
  read_xlsx(sheet="National") %>%
  rename(wgtGpNational=natWgtGp,
         crossNum=natCrossNum)

#Region crosses
regCrosses <- paste0(input_weighting_data_folder,"Geography_Crossings.xlsx") %>%
  read_xlsx(sheet="Region") %>%
  rename(REGION_NAME=regLvl,
         wgtGpRegion=regWgtGp,
         crossNum=regCrossNum)

#State crosses
stateCrosses <- paste0(input_weighting_data_folder,"Geography_Crossings.xlsx") %>%
  read_xlsx(sheet="State") %>%
  rename(STATE_NAME=stateLvl,
         wgtGpState=stateWgtGp,
         crossNum=stateCrossNum)

#FO crosses
foCrosses <- paste0(input_weighting_data_folder,"Geography_Crossings.xlsx") %>%
  read_xlsx(sheet="FO") %>%
  rename(FIELD_OFFICE_NAME=foLvl,
         wgtGpFO=foWgtGp,
         crossNum=foCrossNum)

#JD crosses
jdCrosses <- paste0(input_weighting_data_folder,"Geography_Crossings.xlsx") %>%
  read_xlsx(sheet="JD") %>%
  rename(JUDICIAL_DISTRICT_NAME=jdLvl,
         wgtGpJD=jdWgtGp,
         crossNum=jdCrossNum)

#MSA crosses
msaCrosses <- paste0(input_weighting_data_folder,"Geography_Crossings.xlsx") %>%
  read_xlsx(sheet="MSA") %>%
  rename(MSA_NAME_COUNTY=msaLvl,
         wgtGpMSA=msaWgtGp,
         crossNum=msaCrossNum)

#Identify calibration variables in ORI-level file
calVars1 <- bind_rows(natCrosses,
                      regCrosses,
                      stateCrosses) %>%
  pull(crossNum) %>%
  {outer(paste0("V",.,"_"),
         paste0(c("A","B","C","D","E","F","G","H","I","J","K")),
         paste0)} %>% 
  as.character() %>%
  subset(. %in% colnames(stateDat)) %>%
  str_sort(numeric=TRUE)

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

stateDat2 <- stateDat %>%
  select(ORI_universe,LEGACY_ORI,all_of(calVars1)) %>%
  #02May2024: swapping out propPOP1 for propMult
  #inner_join(SF %>% select(ORI_universe,LEGACY_ORI,county,FIELD_OFFICE_NAME,JUDICIAL_DISTRICT_NAME,MSA_NAME_COUNTY,propPOP1)) %>%
  inner_join(SF %>% select(ORI_universe,LEGACY_ORI,county,FIELD_OFFICE_NAME,JUDICIAL_DISTRICT_NAME,MSA_NAME_COUNTY,propMult)) %>%
  #mutate(across(all_of(calVars1),~.x*propPOP1)) %>%
  mutate(across(all_of(calVars1),~.x*propMult)) %>%
  select(ORI_universe,LEGACY_ORI,county,all_of(calVars1))
  
calVarsDat <- stateDat2 %>%
  full_join(msaDat)%>%
  left_join(jdCrosses %>% select(JUDICIAL_DISTRICT_NAME,wgtGpJD,crossNum)) %>%
  #02Mar2024: including RTI population (popResidAgcyCounty_cbi), population proportion by county (propMult), and metro division (METRO_DIVISION_COUNTY)
  select(ORI_universe,LEGACY_ORI,county,crossNum,popResidAgcyCounty_cbi,propMult,METRO_DIVISION_COUNTY,all_of(calVars1),all_of(calVars2)) %>%
  mutate(across(c(all_of(calVars1),all_of(calVars2)),~ifelse(is.na(.x),0,.x)))
  
calVarsDat %>%
  write_csv_logging(file=paste0(output_weighting_data_folder,"County_Level_Calibration_Variable_File.csv"))