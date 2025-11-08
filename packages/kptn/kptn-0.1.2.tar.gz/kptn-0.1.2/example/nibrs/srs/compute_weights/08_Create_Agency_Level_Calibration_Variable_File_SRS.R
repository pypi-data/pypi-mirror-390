#Create agency-level version of the SRS calibration variables
#02Jan2025: making agency-level SRS variant, heavily based on county-level SRS variant

#National frame (with national calibration variables at ORI-level)
natDat <- paste0(output_weighting_data_folder,"SF_national_postN_srs.csv") %>%
  read_csv_logging()
  
#Agency-level file
SF <- paste0(output_weighting_data_folder,"SF_national_srs.csv") %>%
  read_csv_logging()


#National crosses
natCrosses <- paste0(input_weighting_data_folder,"Geography_Crossings_National_SRS.xlsx") %>%  
  read_xlsx(sheet="National") %>%
  rename(wgtGpNational=natWgtGp,
         crossNum=natCrossNum)


#Identify calibration variables in ORI-level file
calVars1 <- bind_rows(natCrosses) %>%
  pull(crossNum) %>%
  {outer(paste0("V",.,"_"),
         paste0(c("A","B","C","D","E","F","G","H","I","J","K")),
         paste0)} %>% 
  as.character() %>%
  subset(. %in% colnames(natDat)) %>%
  str_sort(numeric=TRUE)


natDat2 <- natDat %>%
  select(ORI_universe,wgtGpNational,all_of(calVars1))
  
calVarsDat <- natDat2 %>%
  left_join(natCrosses %>% select(wgtGpNational,crossNum)) %>%
  #02Mar2024: including RTI population (popResidAgcyCounty_cbi), population proportion by county (propMult), and metro division (METRO_DIVISION_COUNTY)
  select(ORI_universe,crossNum,all_of(calVars1)) %>%
  mutate(across(c(all_of(calVars1)),~ifelse(is.na(.x),0,.x)))
  
calVarsDat %>%
  write_csv_logging(file=paste0(output_weighting_data_folder,"Agency_Level_Calibration_Variable_File_SRS.csv"))