#Create ORI-level data to use throughout copula imputation (for a given table)

#Note (26May2023): Creating SRS pipeline version. Heavily basing off equivalent NIBRS pipeline program. Any dates referred to prior to today are a result of copy-pasting. Tweaks include adding "_SRS" to all output and changing NIBRS/SRS split for sourceInd to "SRS Reporter"/"SRS Non-reporter".

#Note: For 3a, get warning about "The size of the connection buffer (131072)
#      was not large enough to fit a complete line"
#      In response, temporarily update environment variable then revert back
#vrcs <- Sys.getenv("VROOM_CONNECTION_SIZE")
#Sys.setenv("VROOM_CONNECTION_SIZE"=1e6)
library(data.table)
temp.allVars <-file.path(input_estimate_folder,
                         paste0("Table ",temp.table," ORI.csv.gz")) %>%
  #read_csv(n_max=0) %>%
  fread(nrows=0) %>%
  colnames()
#temp.varTypes <- ifelse(str_detect(temp.allVars,"^t_"),"d","?") %>%
#  as.list()
#names(temp.varTypes) <- temp.allVars

table_ORI_raw <- file.path(input_estimate_folder,
                           paste0("Table ",temp.table," ORI.csv.gz")) %>%
  #read_csv(guess_max=1e6,col_types=temp.varTypes)
  fread()
#Sys.setenv("VROOM_CONNECTION_SIZE"=vrcs)

#srs2016_2020_smoothed <- read_csv("../../compute_weights/Data/srs2016_2020_smoothed.csv")
srs2016_2020_smoothed <- fread("../../../tasks/compute_weights/Data/srs2016_2020_smoothed.csv")

univ_raw<- file.path(input_files_folder, paste0("ref_agency_", year, ".csv")) %>%
  #read_csv(guess_max=1e6)
  fread()

#NOTE: Setup as external file
allLEAsCBISummary <- read.xlsx(file.path(external_path,file_locs[[year]]$cbi_summary_county_reduced))

#oriMappings <- read_csv(paste0(input_extract_folder,"ORI_VARIANCE.csv.gz"),
#                        guess_max=1e6)
oriMappings <- paste0(input_extract_folder,"ORI_VARIANCE.csv.gz") %>%
  fread()

#Add ORI to table_ORI
table_ORI <- oriMappings %>% 
subset(!is.na(JDWgt)) %>%
  dplyr::select(ORI=ORI_universe,ori) %>% 
  unique() %>%
  merge.data.table(table_ORI_raw,by="ori") %>%
  dplyr::select(-ori) %>%
  unique()
rm(table_ORI_raw)

#First: get list of UCR-only LEAs (e.g., not SRS reporters)
#Update (02MAR2022): Renaming indicator table's ORI to LEGACY_ORI yields better join 
srsORIs <- table_ORI %>%
  #select(ORI=ori)
  dplyr::select(ORI)

log_debug("Creating allORIs")
allORIs <- oriMappings %>%
  select(ORI) %>%
  subset(duplicated(ORI)==FALSE)

ucrORIs <- srs2016_2020_smoothed %>% #ucr2016_2020_long %>%
  dplyr::select(ORI=ORI_UNIVERSE) %>%
  merge.data.table(oriMappings) %>%
  dplyr::select(ORI) %>%
  #select(ORI=LEGACY_ORI) %>%
  subset(duplicated(ORI)==FALSE)

ucrOnlyORIs <- anti_join(allORIs,srsORIs,by="ORI")

log_debug("Creating table_ORI_all")
#Stack SRS reporters+SRS non-reporters
#Note (JDB 09MAY2022): Drop 'weight' from original file and replace with weight from ORI_VARIANCE
table_ORI_all <- list(table_ORI,
                      ucrOnlyORIs) %>%
  rbindlist(fill=TRUE) %>%#bind_rows(table_ORI,table_ORI_ucrOnly) %>%
  #dplyr::select(colnames(table_ORI)) %>%
  dplyr::select(-weight)
log_debug("Merge table_ORI_all and oriMappings")
table_ORI_all <- table_ORI_all %>%
  merge.data.table(dplyr::select(oriMappings,ORI,REGION_CODE,STATE_ABBR) %>% unique(),
                   by="ORI")
rm(table_ORI)
#rm(oriMappings)


log_debug("Merging table_ORI_all and smoothed SRS")
table_ORI_all <- table_ORI_all %>%
  merge.data.table(dplyr::select(srs2016_2020_smoothed,ORI=ORI_UNIVERSE,matches("totcrime.*_imp")),by="ORI",all.x=TRUE)
  
  log_debug("Merging table_ORI_all and univ_raw")
table_ORI_all <- table_ORI_all %>%
  data.table() %>%
  merge.data.table(dplyr::select(univ_raw,ORI,AGENCY_TYPE_NAME,POPULATION,PARENT_POP_GROUP_CODE,POPULATION_GROUP_DESC,PE_MALE_OFFICER_COUNT,PE_FEMALE_OFFICER_COUNT),by="ORI")  %>%
  mutate(PARENT_POP_GROUP_CODE2=ifelse(PARENT_POP_GROUP_CODE %in% 1:2,
                                       1,
                                       PARENT_POP_GROUP_CODE-1))
log_debug("Merging table_ORI_all and allLEAsCBISummary")
#29Apr2024: use new propMult variable from pop file instead of creating propPOP1
table_ORI_all <- table_ORI_all %>%
  merge.data.table(dplyr::select(allLEAsCBISummary,ORI,county,popResidAgcyCounty_cbi,matches("^pct"),propMult),by="ORI") %>%
  mutate(popResidAgcyCounty_cbi=ifelse(is.na(popResidAgcyCounty_cbi),0,popResidAgcyCounty_cbi)) %>%
  #group_by(ORI) %>%
  #mutate(propPOP1=popResidAgcyCounty_cbi/sum(popResidAgcyCounty_cbi,na.rm=TRUE)) %>%
  #ungroup() %>%
  #mutate(propPOP1=ifelse(is.na(propPOP1),1,propPOP1)) %>%
  #subset(!(propPOP1==0 & county=="NULL"))
  subset(!(propMult==0 & county=="NULL"))
rm(allLEAsCBISummary)

rm(univ_raw)
log_debug("Merge table_ORI_all and oriMappings (part 2)")
table_ORI_all <- table_ORI_all %>%
  data.table() %>%
  merge.data.table(dplyr::select(oriMappings,ORI,county,weight=JDWgt),
                   by=c("ORI","county"))
log_debug("Finish modifying table_ORI_all")
#29Apr2024: use propMult instead of propPOP1
table_ORI_all <- table_ORI_all %>%
  mutate(PE_FEMALE_OFFICER_COUNT=ifelse(is.na(PE_FEMALE_OFFICER_COUNT),0,PE_FEMALE_OFFICER_COUNT),
         PE_MALE_OFFICER_COUNT=ifelse(is.na(PE_MALE_OFFICER_COUNT),0,PE_MALE_OFFICER_COUNT)) %>%
  mutate(TOT_OFFICER_COUNT=PE_MALE_OFFICER_COUNT+PE_FEMALE_OFFICER_COUNT) %>%
  #mutate(TOT_OFFICER_COUNT_COUNTY=propPOP1*TOT_OFFICER_COUNT,
  #       POPULATION=propPOP1*POPULATION) %>%
  mutate(TOT_OFFICER_COUNT_COUNTY=propMult*TOT_OFFICER_COUNT,
         POPULATION=propMult*POPULATION) %>%
  #dplyr::select(-LEGACY_ORI) %>%
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
  dplyr::select(ORI,everything()) %>%
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
		 weight=ifelse(is.na(weight),0,weight),
         #Create source indicator (SRS reporter vs. SRS non-reporter)
         sourceInd=ifelse(weight==0 & is.na(eval(sym(temp.allVars %>% str_subset("^t_") %>% .[1]))),"SRS Non-reporter","SRS Reporter"))

log_debug("Recode NA -> 0")
#Note (JDB 09MAY2022): Adding code to set missing toc variables to 0 for SRS reporting LEAs (should only affect a few hundred LEAs with weights but no incidents)
temp.tocVars <- temp.allVars %>% str_subset("^t_")
#Note (JDB 19Aug2022): Optimizing section
# for (i in 1:length(temp.tocVars)){
#
# temp.tocVar <- temp.tocVars[i]
#   table_ORI_attemp.tocVar := ifelse(sourceInd=="SRS Reporter" & is.na(eval(as.symbol(temp.tocVar))),0,eval(as.symbol(temp.tocVar))))
# }
table_ORI_all <- table_ORI_all %>%
  mutate(across(all_of(temp.tocVars),
                ~ifelse(sourceInd=="SRS Reporter" & is.na(.),0,.)))
#23Apr2024: swapping out propPOP1 for propMult
table_ORI_all <- table_ORI_all %>%
  mutate(across(all_of(temp.tocVars),
                #~ifelse(sourceInd=="SRS Reporter",.x*propPOP1,.)))
                ~ifelse(sourceInd=="SRS Reporter",.x*propMult,.)))
#table_ORI_all %>% nrow()

#table_ORI_all %>% colnames() %>% str_subset("^pct",negate=TRUE) %>% str_subset("^t_1a",negate=TRUE)

log_debug("Write file")
fwrite_wrapper(table_ORI_all,
       file.path(output_copula_data_folder,
                 paste0("Table_",temp.table,"_ORI_all_SRS.csv")))