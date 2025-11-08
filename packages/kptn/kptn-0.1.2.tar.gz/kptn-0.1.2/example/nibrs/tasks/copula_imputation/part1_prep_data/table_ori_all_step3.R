log_debug(system("free -mh", intern = FALSE))

# list of demographic tables to check against
demo_table_list <- c("3a", "3aunclear", "3aclear", "3b", "3bunclear", "3bclear",  "4a", "4b", "5a", "5b", "DM7", "DM9", "DM10", "GV2a")

log_debug("Getting temp.allVars")
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

log_debug(system("free -mh", intern = FALSE))

log_debug("Reading allLEAsCBISummary")
#NOTE: Setup as external file
#NOte (28Jun2023): Switching from ORI-level to (ORI x county)-level file
#Note (03May2024): Include the new propMult variable
allLEAsCBISummary <- read.xlsx(file.path(external_path,file_locs[[year]]$cbi_summary_county_reduced)) %>%
  dplyr::select(LEGACY_ORI,county,MSA_NAME_COUNTY,JUDICIAL_DISTRICT_NAME,FIELD_OFFICE_NAME,popResidAgcyCounty_cbi,propMult,matches("^pct"))
log_dim(allLEAsCBISummary)
log_debug(system("free -mh", intern = FALSE))

log_debug("Reading oriMappings")
oriMappings <- paste0(input_extract_folder,"ORI_VARIANCE.csv.gz") %>%
  fread(select=c("LEGACY_ORI","county", "NationalWgt")) %>%
  dplyr::rename(weight = NationalWgt)
log_dim(oriMappings)
log_debug(system("free -mh", intern = FALSE))

log_debug("Reading univ_raw")
univ_raw <- file.path(input_files_folder, paste0("ref_agency_", year, ".csv")) %>%
  fread() %>%
  dplyr::select(LEGACY_ORI,POPULATION_GROUP_DESC,PE_MALE_OFFICER_COUNT,PE_FEMALE_OFFICER_COUNT)
log_dim(univ_raw)
log_debug(system("free -mh", intern = FALSE))

table_ORI_batch_paths <- list.files(
  path = output_copula_temp_folder,
  pattern = paste0("Table_", temp.table, "_ORI_all_",temp.perm,"_temp_step2_batch.*\\.csv\\.gz"),
  full.names = TRUE
)
for (table_ORI_batch_path in table_ORI_batch_paths) {
    log_debug(paste0("Reading ", table_ORI_batch_path))
    table_ORI_batch <- fread(table_ORI_batch_path)
    log_dim(table_ORI_batch)
    log_debug(system("free -mh", intern = FALSE))

    log_debug("Merging table_ORI_batch and allLEAsCBISummary and oriMappings")
    #Note (28Jun2023): Including county, MSA_NAME_COUNTY, JUDICIAL_DISTRICT_NAME, and FIELD_OFFICE_NAME in variables merged on from pop estimates
    #Note (28Jun2023): Also, we'll create propPOP1 to get proportion of officer counts to assign by county
    #Note (03May2024): Not creating propPOP1 here anymore (instead we'll use existing propMult variable in subsequent lines)
    #Note (03Jun2025): Set propMult to >0 if: (a) propMult is missing, and (b) ORI-level sum of propMult is 0
	#                    otherwise, set to 0 if propMult is missing
    table_ORI_batch <- table_ORI_batch %>%
        merge.data.table(allLEAsCBISummary,by="LEGACY_ORI",all.x=TRUE) %>%
        merge.data.table(oriMappings,by=c("LEGACY_ORI","county"),all.x=TRUE) %>%
        mutate(weight=ifelse(is.na(weight),0,weight)) %>% #03Jul2023: Adding bc not all LEAs in oriMappings
        mutate(popResidAgcyCounty_cbi=ifelse(is.na(popResidAgcyCounty_cbi),0,popResidAgcyCounty_cbi)) %>%
        group_by(LEGACY_ORI) %>%
        #mutate(propPOP1=popResidAgcyCounty_cbi/sum(popResidAgcyCounty_cbi,na.rm=TRUE)) %>%
        #mutate(propPOP1=ifelse(is.na(propPOP1),1,propPOP1)) %>%
        mutate(nCountiesORI=n(),
		       propMultSum=sum(ifelse(is.na(propMult),0,propMult)) %>% 
                 round(digits=10)) %>%
        ungroup() %>%
        mutate(propMult=fcase(is.na(propMult) & propMultSum==0,1/nCountiesORI,
                              is.na(propMult),0,
                              !is.na(propMult), propMult)) %>%
        as.data.table()
    log_dim(table_ORI_batch)
    log_debug(system("free -mh", intern = FALSE))

    log_debug("Merging table_ORI_batch and univ_raw")
    table_ORI_batch <- table_ORI_batch %>%
        merge.data.table(univ_raw,by="LEGACY_ORI") 
    log_dim(table_ORI_batch)
    log_debug(system("free -mh", intern = FALSE))

    log_debug("Finishing modifying table_ORI_batch")
    #Note (28Jun2023): Create (agency X county)-level version of officer counts
    #Note (03May2024): Replace propPOP1 with propMult
    table_ORI_batch <- table_ORI_batch %>%
        mutate(PE_FEMALE_OFFICER_COUNT=ifelse(is.na(PE_FEMALE_OFFICER_COUNT),0,PE_FEMALE_OFFICER_COUNT),
               PE_MALE_OFFICER_COUNT=ifelse(is.na(PE_MALE_OFFICER_COUNT),0,PE_MALE_OFFICER_COUNT)) %>%
        mutate(TOT_OFFICER_COUNT=PE_MALE_OFFICER_COUNT+PE_FEMALE_OFFICER_COUNT) %>%
        #mutate(TOT_OFFICER_COUNT_COUNTY=propPOP1*TOT_OFFICER_COUNT) %>%
        mutate(TOT_OFFICER_COUNT_COUNTY=propMult*TOT_OFFICER_COUNT) %>%
        dplyr::select(-LEGACY_ORI) %>%
        mutate(popResidAgcyCounty_ageLT5_cbi=popResidAgcyCounty_cbi*pctAgeLT5/100,
               popResidAgcyCounty_age5to14_cbi=popResidAgcyCounty_cbi*pctAge5to14/100,
               popResidAgcyCounty_age15_cbi=popResidAgcyCounty_cbi*pctAge15/100,
               popResidAgcyCounty_age16_cbi=popResidAgcyCounty_cbi*pctAge16/100,
               popResidAgcyCounty_age17_cbi=popResidAgcyCounty_cbi*pctAge17/100,
               popResidAgcyCounty_age18to24_cbi=popResidAgcyCounty_cbi*pctAge18to24/100,
               popResidAgcyCounty_age25to34_cbi=popResidAgcyCounty_cbi*pctAge25to34/100,
               popResidAgcyCounty_age35to64_cbi=popResidAgcyCounty_cbi*pctAge35to64/100,
               popResidAgcyCounty_ageGTE65_cbi=popResidAgcyCounty_cbi*pctAgeGTE65/100,
               popResidAgcyCounty_sexMale_cbi=popResidAgcyCounty_cbi*pctSexMale/100,
               popResidAgcyCounty_sexFemale_cbi=popResidAgcyCounty_cbi*pctSexFemale/100,
               popResidAgcyCounty_raceWhite_cbi=popResidAgcyCounty_cbi*pctRaceWhite/100,
               popResidAgcyCounty_raceBlack_cbi=popResidAgcyCounty_cbi*pctRaceBlack/100,
               popResidAgcyCounty_raceAIAN_cbi=popResidAgcyCounty_cbi*pctRaceAIAN/100,
               popResidAgcyCounty_raceAsian_cbi=popResidAgcyCounty_cbi*pctRaceAsian/100,
               popResidAgcyCounty_raceNHPI_cbi=popResidAgcyCounty_cbi*pctRaceNHPI/100,
               #Note (JDB 30MAR2023): Adding poverty vars
               popResidAgcyCounty_incomeRatioLT1_cbi=popResidAgcyCounty_cbi*pctIncomeRatioLT1/100,
               popResidAgcyCounty_incomeRatio1to2_cbi=popResidAgcyCounty_cbi*pctIncomeRatio1to2/100,
               popResidAgcyCounty_incomeRatioGTE2_cbi=popResidAgcyCounty_cbi*pctIncomeRatioGTE2/100,
               #Note (JDB 09MAY2023): Adding 5-11, 12-14, LT 12, 12-17, LT 18, GTE 18
               popResidAgcyCounty_age5to11_cbi=popResidAgcyCounty_cbi*pctAge5to11/100,
               popResidAgcyCounty_age12to14_cbi=popResidAgcyCounty_cbi*pctAge12to14/100,
               popResidAgcyCounty_ageLT12_cbi=popResidAgcyCounty_cbi*pctAgeLT12/100,
               popResidAgcyCounty_age12to17_cbi=popResidAgcyCounty_cbi*pctAge12to17/100,
               popResidAgcyCounty_ageLT18_cbi=popResidAgcyCounty_cbi*pctAgeLT18/100,
               popResidAgcyCounty_ageGTE18_cbi=popResidAgcyCounty_cbi*pctAgeGTE18/100) %>%
        dplyr::select(-matches("^pct")) %>%
        dplyr::select(ORI,county,everything()) %>%
        mutate(der_national=1) %>% #Set for national permutation
        #Below will track number of missing demo variables
        mutate(nDemoMissing=dplyr::select(.
                                         ,popResidAgcyCounty_ageLT5_cbi
                                         ,popResidAgcyCounty_age5to14_cbi
                                         ,popResidAgcyCounty_age15_cbi
                                         ,popResidAgcyCounty_age16_cbi
                                         ,popResidAgcyCounty_age17_cbi
                                         ,popResidAgcyCounty_age18to24_cbi
                                         ,popResidAgcyCounty_age25to34_cbi
                                         ,popResidAgcyCounty_age35to64_cbi
                                         ,popResidAgcyCounty_ageGTE65_cbi
                                         ,popResidAgcyCounty_sexMale_cbi
                                         ,popResidAgcyCounty_sexFemale_cbi
                                         ,popResidAgcyCounty_raceWhite_cbi
                                         ,popResidAgcyCounty_raceBlack_cbi
                                         ,popResidAgcyCounty_raceAIAN_cbi
                                         ,popResidAgcyCounty_raceAsian_cbi
                                         ,popResidAgcyCounty_raceNHPI_cbi
                                         ,popResidAgcyCounty_incomeRatioLT1_cbi
                                         ,popResidAgcyCounty_incomeRatio1to2_cbi
                                         ,popResidAgcyCounty_incomeRatioGTE2_cbi
                                         ,popResidAgcyCounty_age5to11_cbi
                                         ,popResidAgcyCounty_age12to14_cbi
                                         ,popResidAgcyCounty_ageLT12_cbi
                                         ,popResidAgcyCounty_age12to17_cbi
                                         ,popResidAgcyCounty_ageLT18_cbi
                                         ,popResidAgcyCounty_ageGTE18_cbi) %>%
                   {rowSums(ifelse(is.na(.),1,0))})%>%
        #Create percentage versions of demographics
        mutate(ageLT5=popResidAgcyCounty_ageLT5_cbi/(popResidAgcyCounty_cbi),
               age5to14=popResidAgcyCounty_age5to14_cbi/(popResidAgcyCounty_cbi),
               age15=popResidAgcyCounty_age15_cbi/(popResidAgcyCounty_cbi),
               age16=popResidAgcyCounty_age16_cbi/(popResidAgcyCounty_cbi),
               age17=popResidAgcyCounty_age17_cbi/(popResidAgcyCounty_cbi),
               age18to24=popResidAgcyCounty_age18to24_cbi/(popResidAgcyCounty_cbi),
               age25to34=popResidAgcyCounty_age25to34_cbi/(popResidAgcyCounty_cbi),
               age35to64=popResidAgcyCounty_age35to64_cbi/(popResidAgcyCounty_cbi),
               ageGTE65=popResidAgcyCounty_ageGTE65_cbi/(popResidAgcyCounty_cbi),
               sexMale=popResidAgcyCounty_sexMale_cbi/(popResidAgcyCounty_cbi),
               sexFemale=popResidAgcyCounty_sexFemale_cbi/(popResidAgcyCounty_cbi),
               raceWhite=popResidAgcyCounty_raceWhite_cbi/(popResidAgcyCounty_cbi),
               raceBlack=popResidAgcyCounty_raceBlack_cbi/(popResidAgcyCounty_cbi),
               raceAIAN=popResidAgcyCounty_raceAIAN_cbi/(popResidAgcyCounty_cbi),
               raceAsian=popResidAgcyCounty_raceAsian_cbi/(popResidAgcyCounty_cbi),
               raceNHPI=popResidAgcyCounty_raceNHPI_cbi/(popResidAgcyCounty_cbi),
               #Note (JDB 30MAR2023): Adding poverty variables
               incomeRatioLT1=popResidAgcyCounty_incomeRatioLT1_cbi/(popResidAgcyCounty_cbi),
               incomeRatio1to2=popResidAgcyCounty_incomeRatio1to2_cbi/(popResidAgcyCounty_cbi),
               incomeRatioGTE2=popResidAgcyCounty_incomeRatioGTE2_cbi/(popResidAgcyCounty_cbi),
               #Note (JDB 09MAY2023): Adding 5-11, 12-14, LT 12, 12-17, LT 18, GTE 18
               age5to11=popResidAgcyCounty_age5to11_cbi/popResidAgcyCounty_cbi,
               age12to14=popResidAgcyCounty_age12to14_cbi/popResidAgcyCounty_cbi,
               ageLT12=popResidAgcyCounty_ageLT12_cbi/popResidAgcyCounty_cbi,
               age12to17=popResidAgcyCounty_age12to17_cbi/popResidAgcyCounty_cbi,
               ageLT18=popResidAgcyCounty_ageLT18_cbi/popResidAgcyCounty_cbi,
               ageGTE18=popResidAgcyCounty_ageGTE18_cbi/popResidAgcyCounty_cbi,
               #Set negative population values to 0
               popResidAgcyCounty_cbi=ifelse(popResidAgcyCounty_cbi<0,0,popResidAgcyCounty_cbi),
               #Create source indicator (SRS vs. NIBRS)
               sourceInd=ifelse(weight==0 & is.na(eval(sym(temp.allVars %>% str_subset("^t_") %>% .[1]))),"SRS","NIBRS")) %>%
        subset(!(popResidAgcyCounty_cbi==0 & PARENT_POP_GROUP_CODE2 %in% c(1:5))) %>% #03Jul2023: subset to avoid problem scenario where 1 (LEA x county) crossing has 0 pop but overall LEA has >0 pop
        subset(!(propMultSum>0 & round(propMult,digits=10)==0)) %>% #03Jun2025: further reduce the cases described above
        dplyr::select(-c(propMultSum,nCountiesORI))
		
    log_dim(table_ORI_batch)
    log_debug(system("free -mh", intern = FALSE))

    log_debug("Writing table_ORI_batch")
    fwrite(
        x = table_ORI_batch,
        file = gsub("step2", "step3", table_ORI_batch_path)
    )
    gc()
    log_debug(system("free -mh", intern = FALSE))
}

log_debug("End of script")
