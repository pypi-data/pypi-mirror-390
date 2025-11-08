#Note: this is a modified version of a program originally created by Taylor Lewis.


### Purpose of program is to create a working NIBRS data set for implementing various calibration weighting strategies
### Author: Taylor Lewis
### Modified by JD Bunker
### Last updated: 20Jul2023

# key difference in this version is not treating all 400 NCS-X LEAs as reporters, only those that are reporting
# do not need to do naive design-based strategy here
# another modification on 9.28.20 is introducing a condition where we poststratify to combination of zeropop LEAs indicator and population size
#Note (JDB 20Jul2023): Incorporating outlier results

### load necessary packages
#source("http://pcwww.liv.ac.uk/~william/R/crosstab.r")
library(DescTools)
library(sampling)
library(data.table)
library(Hmisc)
library(mice)
library(party)
library(partykit)
library(tidyverse)
library(lubridate)
library(data.table)

log_info("Running 02_Weights_Data_Setup.R")

### preparing the sampling frame
# read in and recode the sampling frame
#Update (05NOV2021): Adding guess_max argument
#SF <- read_csv(paste0(output_weighting_data_folder,"cleanframe.csv"),
#               guess_max=1e6)
SF <- fread(paste0(output_weighting_data_folder,"cleanframe.csv")) %>%
  data.frame() %>%
  mutate(in_nibrs=as.double(in_nibrs))

# rename LEGACY_ORI to ORI_universe to match JD's file
SF$ORI_universe <- SF$LEGACY_ORI


# merge in some fields from the UCR SRS crime report data
#Note (21MAY2021): using 2018 SRS instead of 2020
#Note (27OCT2021): using 2016-2020 smoothed SRS. Has been the case but adding note.
#srs2016_2020_smoothed <- read.csv("Data/srs2016_2020_smoothed.csv")
srs2016_2020_smoothed_raw <- fread("Data/srs2016_2020_smoothed.csv")

crimeVars <- colnames(srs2016_2020_smoothed_raw) %>%
  str_subset("^tot.*")

# keep only the needed fields from this file
srs2016_2020_smoothed <- srs2016_2020_smoothed_raw %>%
  select(ORI_UNIVERSE,LEGACY_ORI,all_of(crimeVars))

#25Jul2023: append _smoothed to end of crime vars
colnames(srs2016_2020_smoothed) <- colnames(srs2016_2020_smoothed) %>%
  str_replace("(totcrime.*)","\\1_smoothed")

#smoothed SRS (with all years)
#25Jul2023: adding so that we can access each year between 2016 and 2020
srs2016_2020_smoothed_allYrs <- fread("Data/srs2016_2020_smoothed_allYrs.csv")

# keep only the needed fields from this file
srs2016_2020_smoothed_allYrs <- srs2016_2020_smoothed_allYrs %>%
  select(ORI_UNIVERSE,LEGACY_ORI,SRS_YEAR,matches("^totcrime"))

#Merge together the 2 smoothed datasets
srs2016_2020_smoothed <- srs2016_2020_smoothed %>%
  full_join(srs2016_2020_smoothed_allYrs)

crimeVars <- colnames(srs2016_2020_smoothed) %>%
  str_subset("^totcrime")

# 2022 SRS
#Note (25Jul2023): Including 2022 SRS in benchmark selection
#Note (28Mar2024): Generalizing to use current year SRS for 2022 onward (will run into errors if we don't have both the full NIBRS and SRS for a year, in which case we simply patch the below code)
#Note (15May2024): Overhauling how we use SRS (from email with Marcus on 30Apr2024):
# 1.	Use current year SRS (e.g., 2023 this year)
# 2.	Use current year minus 1 SRS if current year not available
# 3.	Use 5-year smoothed SRS starting with current year minus 2 if current year and current year minus 1 is not available
if (as.numeric(year)>=2022){
  recentSRSYrs <- (as.numeric(year):2022)[1:min(length(as.numeric(year):2022),5)]
  smoothedSRSYrs <- 2016:2020
  
  map(recentSRSYrs,function(temp.year){
    
    ucr_srs_clean_raw <- paste0(raw_srs_file_path,"/UCR_SRS_",temp.year,"_clean_reta_mm_selected_vars.csv") %>%
      read_csv()
    
    ucr_srs_clean <- ucr_srs_clean_raw %>%
      rename(m01_murder=v70, #January
             m01_mnslghtr=v71,
             m01_rapetotal=v72,
             m01_forcerape=v73,
             m01_attrape=v74,
             m01_robtotal=v75,
             m01_robgun=v76,
             m01_robknife=v77,
             m01_robother=v78,
             m01_robstrgarm=v79,
             m01_asslttotal=v80,
             m01_assltgun=v81,
             m01_assltknife=v82,
             m01_assltother=v83,
             m01_assltpersonal=v84,
             m01_sasslt=v85,
             m01_burgltotal=v86,
             m01_burgforceentry=v87,
             m01_burgNforceentry=v88,
             m01_attmptburgl=v89,
             m01_larcenytotal=v90,
             m01_mvttotal=v91,
             m01_autotheft=v92,
             m01_thefttruckbus=v93,
             m01_mvtother=v94,
             m01_grandtotal=v95,
             
             m02_murder=v188, #February
             m02_mnslghtr=v189,
             m02_rapetotal=v190,
             m02_forcerape=v191,
             m02_attrape=v192,
             m02_robtotal=v193,
             m02_robgun=v194,
             m02_robknife=v195,
             m02_robother=v196,
             m02_robstrgarm=v197,
             m02_asslttotal=v198,
             m02_assltgun=v199,
             m02_assltknife=v200,
             m02_assltother=v201,
             m02_assltpersonal=v202,
             m02_sasslt=v203,
             m02_burgltotal=v204,
             m02_burgforceentry=v205,
             m02_burgNforceentry=v206,
             m02_attmptburgl=v207,
             m02_larcenytotal=v208,
             m02_mvttotal=v209,
             m02_autotheft=v210,
             m02_thefttruckbus=v211,
             m02_mvtother=v212,
             m02_grandtotal=v213,
             
             m03_murder=v306, #March
             m03_mnslghtr=v307,
             m03_rapetotal=v308,
             m03_forcerape=v309,
             m03_attrape=v310,
             m03_robtotal=v311,
             m03_robgun=v312,
             m03_robknife=v313,
             m03_robother=v314,
             m03_robstrgarm=v315,
             m03_asslttotal=v316,
             m03_assltgun=v317,
             m03_assltknife=v318,
             m03_assltother=v319,
             m03_assltpersonal=v320,
             m03_sasslt=v321,
             m03_burgltotal=v322,
             m03_burgforceentry=v323,
             m03_burgNforceentry=v324,
             m03_attmptburgl=v325,
             m03_larcenytotal=v326,
             m03_mvttotal=v327,
             m03_autotheft=v328,
             m03_thefttruckbus=v329,
             m03_mvtother=v330,
             m03_grandtotal=v331,
             
             m04_murder=v424, #April
             m04_mnslghtr=v425,
             m04_rapetotal=v426,
             m04_forcerape=v427,
             m04_attrape=v428,
             m04_robtotal=v429,
             m04_robgun=v430,
             m04_robknife=v431,
             m04_robother=v432,
             m04_robstrgarm=v433,
             m04_asslttotal=v434,
             m04_assltgun=v435,
             m04_assltknife=v436,
             m04_assltother=v437,
             m04_assltpersonal=v438,
             m04_sasslt=v439,
             m04_burgltotal=v440,
             m04_burgforceentry=v441,
             m04_burgNforceentry=v442,
             m04_attmptburgl=v443,
             m04_larcenytotal=v444,
             m04_mvttotal=v445,
             m04_autotheft=v446,
             m04_thefttruckbus=v447,
             m04_mvtother=v448,
             m04_grandtotal=v449,
             
             m05_murder=v542, #May
             m05_mnslghtr=v543,
             m05_rapetotal=v544,
             m05_forcerape=v545,
             m05_attrape=v546,
             m05_robtotal=v547,
             m05_robgun=v548,
             m05_robknife=v549,
             m05_robother=v550,
             m05_robstrgarm=v551,
             m05_asslttotal=v552,
             m05_assltgun=v553,
             m05_assltknife=v554,
             m05_assltother=v555,
             m05_assltpersonal=v556,
             m05_sasslt=v557,
             m05_burgltotal=v558,
             m05_burgforceentry=v559,
             m05_burgNforceentry=v560,
             m05_attmptburgl=v561,
             m05_larcenytotal=v562,
             m05_mvttotal=v563,
             m05_autotheft=v564,
             m05_thefttruckbus=v565,
             m05_mvtother=v566,
             m05_grandtotal=v567,
             
             m06_murder=v660, #June
             m06_mnslghtr=v661,
             m06_rapetotal=v662,
             m06_forcerape=v663,
             m06_attrape=v664,
             m06_robtotal=v665,
             m06_robgun=v666,
             m06_robknife=v667,
             m06_robother=v668,
             m06_robstrgarm=v669,
             m06_asslttotal=v670,
             m06_assltgun=v671,
             m06_assltknife=v672,
             m06_assltother=v673,
             m06_assltpersonal=v674,
             m06_sasslt=v675,
             m06_burgltotal=v676,
             m06_burgforceentry=v677,
             m06_burgNforceentry=v678,
             m06_attmptburgl=v679,
             m06_larcenytotal=v680,
             m06_mvttotal=v681,
             m06_autotheft=v682,
             m06_thefttruckbus=v683,
             m06_mvtother=v684,
             m06_grandtotal=v685,
             
             m07_murder=v778, #July
             m07_mnslghtr=v779,
             m07_rapetotal=v780,
             m07_forcerape=v781,
             m07_attrape=v782,
             m07_robtotal=v783,
             m07_robgun=v784,
             m07_robknife=v785,
             m07_robother=v786,
             m07_robstrgarm=v787,
             m07_asslttotal=v788,
             m07_assltgun=v789,
             m07_assltknife=v790,
             m07_assltother=v791,
             m07_assltpersonal=v792,
             m07_sasslt=v793,
             m07_burgltotal=v794,
             m07_burgforceentry=v795,
             m07_burgNforceentry=v796,
             m07_attmptburgl=v797,
             m07_larcenytotal=v798,
             m07_mvttotal=v799,
             m07_autotheft=v800,
             m07_thefttruckbus=v801,
             m07_mvtother=v802,
             m07_grandtotal=v803,
             
             m08_murder=v896, #August
             m08_mnslghtr=v897,
             m08_rapetotal=v898,
             m08_forcerape=v899,
             m08_attrape=v900,
             m08_robtotal=v901,
             m08_robgun=v902,
             m08_robknife=v903,
             m08_robother=v904,
             m08_robstrgarm=v905,
             m08_asslttotal=v906,
             m08_assltgun=v907,
             m08_assltknife=v908,
             m08_assltother=v909,
             m08_assltpersonal=v910,
             m08_sasslt=v911,
             m08_burgltotal=v912,
             m08_burgforceentry=v913,
             m08_burgNforceentry=v914,
             m08_attmptburgl=v915,
             m08_larcenytotal=v916,
             m08_mvttotal=v917,
             m08_autotheft=v918,
             m08_thefttruckbus=v919,
             m08_mvtother=v920,
             m08_grandtotal=v921,
             
             m09_murder=v1014, #September
             m09_mnslghtr=v1015,
             m09_rapetotal=v1016,
             m09_forcerape=v1017,
             m09_attrape=v1018,
             m09_robtotal=v1019,
             m09_robgun=v1020,
             m09_robknife=v1021,
             m09_robother=v1022,
             m09_robstrgarm=v1023,
             m09_asslttotal=v1024,
             m09_assltgun=v1025,
             m09_assltknife=v1026,
             m09_assltother=v1027,
             m09_assltpersonal=v1028,
             m09_sasslt=v1029,
             m09_burgltotal=v1030,
             m09_burgforceentry=v1031,
             m09_burgNforceentry=v1032,
             m09_attmptburgl=v1033,
             m09_larcenytotal=v1034,
             m09_mvttotal=v1035,
             m09_autotheft=v1036,
             m09_thefttruckbus=v1037,
             m09_mvtother=v1038,
             m09_grandtotal=v1039,
             
             m10_murder=v1132, #October
             m10_mnslghtr=v1133,
             m10_rapetotal=v1134,
             m10_forcerape=v1135,
             m10_attrape=v1136,
             m10_robtotal=v1137,
             m10_robgun=v1138,
             m10_robknife=v1139,
             m10_robother=v1140,
             m10_robstrgarm=v1141,
             m10_asslttotal=v1142,
             m10_assltgun=v1143,
             m10_assltknife=v1144,
             m10_assltother=v1145,
             m10_assltpersonal=v1146,
             m10_sasslt=v1147,
             m10_burgltotal=v1148,
             m10_burgforceentry=v1149,
             m10_burgNforceentry=v1150,
             m10_attmptburgl=v1151,
             m10_larcenytotal=v1152,
             m10_mvttotal=v1153,
             m10_autotheft=v1154,
             m10_thefttruckbus=v1155,
             m10_mvtother=v1156,
             m10_grandtotal=v1157,
             
             m11_murder=v1250, #November
             m11_mnslghtr=v1251,
             m11_rapetotal=v1252,
             m11_forcerape=v1253,
             m11_attrape=v1254,
             m11_robtotal=v1255,
             m11_robgun=v1256,
             m11_robknife=v1257,
             m11_robother=v1258,
             m11_robstrgarm=v1259,
             m11_asslttotal=v1260,
             m11_assltgun=v1261,
             m11_assltknife=v1262,
             m11_assltother=v1263,
             m11_assltpersonal=v1264,
             m11_sasslt=v1265,
             m11_burgltotal=v1266,
             m11_burgforceentry=v1267,
             m11_burgNforceentry=v1268,
             m11_attmptburgl=v1269,
             m11_larcenytotal=v1270,
             m11_mvttotal=v1271,
             m11_autotheft=v1272,
             m11_thefttruckbus=v1273,
             m11_mvtother=v1274,
             m11_grandtotal=v1275,
             
             m12_murder=v1368, #December
             m12_mnslghtr=v1369,
             m12_rapetotal=v1370,
             m12_forcerape=v1371,
             m12_attrape=v1372,
             m12_robtotal=v1373,
             m12_robgun=v1374,
             m12_robknife=v1375,
             m12_robother=v1376,
             m12_robstrgarm=v1377,
             m12_asslttotal=v1378,
             m12_assltgun=v1379,
             m12_assltknife=v1380,
             m12_assltother=v1381,
             m12_assltpersonal=v1382,
             m12_sasslt=v1383,
             m12_burgltotal=v1384,
             m12_burgforceentry=v1385,
             m12_burgNforceentry=v1386,
             m12_attmptburgl=v1387,
             m12_larcenytotal=v1388,
             m12_mvttotal=v1389,
             m12_autotheft=v1390,
             m12_thefttruckbus=v1391,
             m12_mvtother=v1392,
             m12_grandtotal=v1393
      ) %>%
      mutate(across(matches("^m1_"),~ifelse(jan_mm_flag==1,.x,NA_real_)),
             across(matches("^m2_"),~ifelse(feb_mm_flag==1,.x,NA_real_)),
             across(matches("^m3_"),~ifelse(mar_mm_flag==1,.x,NA_real_)),
             across(matches("^m4_"),~ifelse(apr_mm_flag==1,.x,NA_real_)),
             across(matches("^m5_"),~ifelse(may_mm_flag==1,.x,NA_real_)),
             across(matches("^m6_"),~ifelse(jun_mm_flag==1,.x,NA_real_)),
             across(matches("^m7_"),~ifelse(jul_mm_flag==1,.x,NA_real_)),
             across(matches("^m8_"),~ifelse(aug_mm_flag==1,.x,NA_real_)),
             across(matches("^m9_"),~ifelse(sep_mm_flag==1,.x,NA_real_)),
             across(matches("^m10_"),~ifelse(oct_mm_flag==1,.x,NA_real_)),
             across(matches("^m11_"),~ifelse(nov_mm_flag==1,.x,NA_real_)),
             across(matches("^m12_"),~ifelse(dec_mm_flag==1,.x,NA_real_))) %>%
      mutate(nMonths_SRS_cYr=select(.,matches("_mm_flag")) %>% {
        rowSums(.==1,na.rm=TRUE)
      },
      resp_ind_srs_cYr=nMonths_SRS_cYr>=3) %>%
      mutate(
        #Annual crime counts (unimputed)
        #Note (28Mar2024): Generalizing from _2022 suffix to _cYr suffix
        totcrime_cYr = select(.,m01_grandtotal, m02_grandtotal, m03_grandtotal,
                              m04_grandtotal, m05_grandtotal, m06_grandtotal,
                              m07_grandtotal, m08_grandtotal, m09_grandtotal,
                              m10_grandtotal, m11_grandtotal, m12_grandtotal) %>% 
          rowSums(.,na.rm=TRUE),
        totcrime_murder_cYr = select(.,m01_murder, m02_murder, m03_murder,
                                     m04_murder, m05_murder, m06_murder,
                                     m07_murder, m08_murder, m09_murder,
                                     m10_murder, m11_murder, m12_murder) %>%
          rowSums(., na.rm=TRUE),
        totcrime_manslaughter_cYr= select(.,m01_mnslghtr, m02_mnslghtr, m03_mnslghtr,
                                          m04_mnslghtr, m05_mnslghtr, m06_mnslghtr,
                                          m07_mnslghtr, m08_mnslghtr, m09_mnslghtr,
                                          m10_mnslghtr, m11_mnslghtr, m12_mnslghtr) %>%
          rowSums(., na.rm=TRUE),
        totcrime_rape_cYr= select(.,m01_rapetotal, m02_rapetotal, m03_rapetotal,
                                  m04_rapetotal, m05_rapetotal, m06_rapetotal,
                                  m07_rapetotal, m08_rapetotal, m09_rapetotal,
                                  m10_rapetotal, m11_rapetotal, m12_rapetotal) %>%
          rowSums(., na.rm=TRUE),
        totcrime_rob_cYr= select(.,m01_robtotal, m02_robtotal, m03_robtotal,
                                 m04_robtotal, m05_robtotal, m06_robtotal,
                                 m07_robtotal, m08_robtotal, m09_robtotal,
                                 m10_robtotal, m11_robtotal, m12_robtotal) %>%
          rowSums(., na.rm=TRUE),
        totcrime_assault_cYr= select(.,m01_asslttotal, m02_asslttotal, m03_asslttotal,
                                     m04_asslttotal, m05_asslttotal, m06_asslttotal,
                                     m07_asslttotal, m08_asslttotal, m09_asslttotal,
                                     m10_asslttotal, m11_asslttotal, m12_asslttotal) %>%
          rowSums(., na.rm=TRUE),
        totcrime_aggAssault_cYr= select(., m01_assltgun, m01_assltknife, m01_assltother, m01_assltpersonal,
                                        m02_assltgun, m02_assltknife, m02_assltother, m02_assltpersonal,
                                        m03_assltgun, m03_assltknife, m03_assltother, m03_assltpersonal,
                                        m04_assltgun, m04_assltknife, m04_assltother, m04_assltpersonal,
                                        m05_assltgun, m05_assltknife, m05_assltother, m05_assltpersonal,
                                        m06_assltgun, m06_assltknife, m06_assltother, m06_assltpersonal,
                                        m07_assltgun, m07_assltknife, m07_assltother, m07_assltpersonal,
                                        m08_assltgun, m08_assltknife, m08_assltother, m08_assltpersonal,
                                        m09_assltgun, m09_assltknife, m09_assltother, m09_assltpersonal,
                                        m10_assltgun, m10_assltknife, m10_assltother, m10_assltpersonal,
                                        m11_assltgun, m11_assltknife, m11_assltother, m11_assltpersonal,
                                        m12_assltgun, m12_assltknife, m12_assltother, m12_assltpersonal) %>%
          rowSums(., na.rm=TRUE),
        totcrime_simpAssault_cYr= select(., m01_sasslt, m02_sasslt, m03_sasslt,
                                         m04_sasslt, m05_sasslt, m06_sasslt,
                                         m07_sasslt, m08_sasslt, m09_sasslt,
                                         m10_sasslt, m11_sasslt, m12_sasslt) %>%
          rowSums(., na.rm=TRUE),
        totcrime_burglary_cYr= select(.,m01_burgltotal, m02_burgltotal, m03_burgltotal,
                                      m04_burgltotal, m05_burgltotal, m06_burgltotal,
                                      m07_burgltotal, m08_burgltotal, m09_burgltotal,
                                      m10_burgltotal, m11_burgltotal, m12_burgltotal) %>%
          rowSums(., na.rm=TRUE),
        totcrime_larceny_cYr= select(.,m01_larcenytotal, m02_larcenytotal, m03_larcenytotal,
                                     m04_larcenytotal, m05_larcenytotal, m06_larcenytotal,
                                     m07_larcenytotal, m08_larcenytotal, m09_larcenytotal,
                                     m10_larcenytotal, m11_larcenytotal, m12_larcenytotal) %>%
          rowSums(.,na.rm=TRUE),
        totcrime_vhcTheft_cYr= select(.,m01_mvttotal, m02_mvttotal, m03_mvttotal,
                                      m04_mvttotal, m05_mvttotal, m06_mvttotal,
                                      m07_mvttotal, m08_mvttotal, m09_mvttotal,
                                      m10_mvttotal, m11_mvttotal, m12_mvttotal) %>%
          rowSums(., na.rm=TRUE)) %>%
      mutate(totcrime_violent_cYr=select(.,
                                         totcrime_murder_cYr,
                                         totcrime_manslaughter_cYr,
                                         totcrime_rape_cYr,
                                         totcrime_rob_cYr,
                                         totcrime_aggAssault_cYr) %>%
               rowSums(.,na.rm=TRUE),
             #tot_violent_imp=select(.,tot_murder_imp,tot_manslaughter_imp,tot_rape_imp,tot_rob_imp,tot_aggAssault_imp) %>%
             #  rowSums(.,na.rm=TRUE),
             totcrime_property_cYr=select(.,
                                          totcrime_burglary_cYr,
                                          totcrime_larceny_cYr,
                                          totcrime_vhcTheft_cYr) %>% #,tot_arson) %>%
               rowSums(.,na.rm=TRUE)
             #tot_property_imp=select(.,tot_burglary_imp,tot_larceny_imp,tot_vhcTheft_imp) %>% #,tot_arson_imp) %>%
             #  rowSums(.,na.rm=TRUE)
      ) %>% 
      mutate(across(matches("^totcrime"),~ifelse(nMonths_SRS_cYr>0,.x,NA_real_))) %>%
      #select(-matches("totcrime")) %>%
      mutate(totcrime_cYr=totcrime_violent_cYr+totcrime_property_cYr) %>%
      select(ORI=ORI_UNIV,matches("_cYr"))
    
    colnames(ucr_srs_clean) <- str_replace(colnames(ucr_srs_clean),
                                           "_cYr",
                                           paste0("_",as.character(temp.year)))
    temp.out <- list(ucr_srs_clean)
    names(temp.out) <- paste0("ucr_srs_",temp.year)
    list2env(temp.out,env=.GlobalEnv)
    return(NULL)
  })
  #Now, let's merge them all together
  ucr_srs_recent <- Reduce(full_join,mget(paste0("ucr_srs_",recentSRSYrs)))
}

#######################
#Update (21MAY2021): Since we're switching from 2020 SRS to 2018 SRS, need to change merge strategy
#Note (27OCT2021): We're now using smoothed 2016-2020 SRS, but methodology otherwise applies
#Note (25Jul2023): Adding SRS_YEAR to all joins
SF_merge1A_inner <- inner_join(SF,
                               srs2016_2020_smoothed %>% select(ORI_UNIVERSE,SRS_YEAR,all_of(crimeVars)),
                               by = c("LEGACY_ORI" = "ORI_UNIVERSE"))
log_dim(SF_merge1A_inner)

#Get the unmatched ones
SF_merge1A_anti <- anti_join(SF,
                             srs2016_2020_smoothed %>% select(ORI_UNIVERSE,SRS_YEAR,all_of(crimeVars)),
                             by = c("LEGACY_ORI" = "ORI_UNIVERSE"))
log_dim(SF_merge1A_anti)

#####
#Merge the unmatched ones by ori
SF_merge1B_inner <- SF_merge1A_anti %>%
  inner_join(srs2016_2020_smoothed %>% select(ORI_UNIVERSE,SRS_YEAR,all_of(crimeVars)), by=c("ORI" = "ORI_UNIVERSE") )
log_dim(SF_merge1B_inner)

#Get the unmatched ones
SF_merge1B_anti <- SF_merge1A_anti %>%
  anti_join(srs2016_2020_smoothed %>% select(ORI_UNIVERSE,SRS_YEAR,all_of(crimeVars)), by=c("ORI" = "ORI_UNIVERSE") )
log_dim(SF_merge1B_anti)

#####
#Merge the unmatched ones by LEGACY_ORI
SF_merge1C_inner <- SF_merge1B_anti %>%
  inner_join(srs2016_2020_smoothed %>% select(LEGACY_ORI,SRS_YEAR,all_of(crimeVars)), by=c("LEGACY_ORI" = "LEGACY_ORI") )
log_dim(SF_merge1C_inner)

#Get the unmatched ones
SF_merge1C_anti <- SF_merge1B_anti %>%
  anti_join(srs2016_2020_smoothed %>% select(LEGACY_ORI,SRS_YEAR,all_of(crimeVars)), by=c("LEGACY_ORI" = "LEGACY_ORI") )
log_dim(SF_merge1C_anti)




#####
#Stack datasets and add on the 2022 SRS
#Note (28Mar2024): Again, generalizing from 2022-only to every year 2022 onward
#Note (15May2024): Again, shifted from always using only current year to potentially using multiple recent years
SF_merge_stacked <- bind_rows(SF_merge1A_inner,
                              SF_merge1B_inner,
                              SF_merge1C_inner,
                              SF_merge1C_anti) 

if (as.numeric(year)>=2022){
  SF_merge_stacked <- SF_merge_stacked %>%
    left_join(ucr_srs_recent)
}
#######################
### inspect missing data patterns
# create a 0/1 indicator for whether the LEA is currently reporting to NIBRS,
# one for each blending method, setting the 0/1 indicator to missing for out-of-scope cases
#Update (24AUG2021): Simplify to only be based on REPORTING_TYPE
#Note (25Jul2023): Moving this section up so that it's available when picking which SRS year to use
SF_merge_stacked$resp_ind_m3 <- as.numeric(SF_merge_stacked$REPORTING_TYPE=="I")#SF$R2012.YEAR + SF$R.NCSX.2011 + SF$R2011 #+ SF$NR.NCSX.2011

#Update (29JUL2021): Treat Type I agencies who only reported 1 or 2 months according to reta-mm (Missingmonths) data file as Nonrespondent
#Update (11MAR2022): For agencies with 50+ total crimes in the smoothed SRS, check if in NIBRS database
#Update (15MAR2022): Limit list of NIBRS reporters to those with start dates before November of the data year
#Update (23MAR2022): Ignore months in reta-MM before start date; create reta_MM_adj and use in place of reta_MM variable
#Update (23MAR2022): Switching from reta-MM to nibrs_month - variable is analogous to reta_MM
#Update (06JUN2023): Switching from pre 2022 date format ("%d-%B-%y") to new date format ("%m/%d/%y)
SF_merge_stacked <- SF_merge_stacked %>%
  mutate(nTimes=month(as_date(NIBRS_START_DATE,format="%m/%d/%y"))-1L) %>%
  mutate(nTimes=ifelse(is.na(nTimes),
                       0,
                       nTimes)) %>%
  #If year of start date same as data year, set all months prior to start as 0s (will work even if start date in January)
  #Else if start year comes after data year, set all months to 0s
  #Else leave reta_MM alone
  # mutate(reta_MM_adj=case_when(year(as_date(NIBRS_START_DATE,format="%d-%B-%y"))==year ~  str_remove_all(reta_MM,"-") %>% 
  #                                str_replace(pattern=paste0("^.{",nTimes,"}"),
  #                                            replacement=str_dup("0",times=nTimes)),
  #                             
  #                              year(as_date(NIBRS_START_DATE,format="%d-%B-%y")) > year ~ str_remove_all(reta_MM,"-") %>% 
  #                                str_replace(pattern=paste0("^.{",12,"}"),
  #                                            replacement=str_dup("0",times=12)),
  #                              TRUE ~ reta_MM)) %>%
# mutate(resp_ind_m3=case_when(resp_ind_m3==1 & str_count(reta_MM_adj,"1")<3 ~0,
#                              TRUE ~ resp_ind_m3)) %>%
mutate(nibrs_month_adj=case_when(year(as_date(NIBRS_START_DATE,format="%m/%d/%y"))==year ~  str_remove_all(nibrs_month,"-") %>% 
                                   str_replace(pattern=paste0("^.{",nTimes,"}"),
                                               replacement=str_dup("0",times=nTimes)),
                                 
                                 year(as_date(NIBRS_START_DATE,format="%m/%d/%y")) > year ~ str_remove_all(nibrs_month,"-") %>% 
                                   str_replace(pattern=paste0("^.{",12,"}"),
                                               replacement=str_dup("0",times=12)),
                                 is.na(NIBRS_START_DATE) ~ str_dup("0",times=12),
                                 TRUE ~ nibrs_month %>% str_remove_all("-"))) 
#Incorporating outlier results
tempEnv <- environment()
#Note (25Jul2023): Unlike with SRS where there are dashes between quarters, no dashes in nibrs_month_adj, so just loop over 1:12
sapply(c(1:12),function(i){
  #1st, let's determine records that need to be updated
  inds <- SF_merge_stacked %>%
    mutate(ind=str_sub(nibrs_month_adj,i,i)=="1" & str_sub(outlier %>% str_remove_all("-"),i,i)=="0") %>%
    pull(ind)
  #2nd, assign as nonreporters for that month
  str_sub(SF_merge_stacked[inds,"nibrs_month_adj"],i,i) <- "0"
  list2env(list("SF_merge_stacked"=SF_merge_stacked),envir=tempEnv)
  return(NULL)
})

#Now return to creating response indicator
SF_merge_stacked <- SF_merge_stacked %>%
  mutate(resp_ind_m3=case_when(resp_ind_m3==1 & str_count(nibrs_month_adj,"1")<3 ~0,
                               TRUE ~ resp_ind_m3)) %>%
  mutate(in_nibrs=case_when(is.na(in_nibrs) ~ 0,
                            TRUE ~ in_nibrs)) %>%
  mutate(resp_ind_m3=case_when(resp_ind_m3==1 & totcrime_imp_smoothed>=50 ~ in_nibrs,
                               TRUE ~ resp_ind_m3)) %>%
  mutate(resp_ind_m3=case_when(resp_ind_m3==1 & as_date(NIBRS_START_DATE,format="%m/%d/%y")>=as_date(paste0(year,"-11-01")) ~ 0,
                               TRUE ~ resp_ind_m3))

#####
#Choose which year of SRS to use
#Note (28Mar2024): Again, generalizing from 2022-only to 2022 onward
#Note (15May2024): Again, shifted from always using only current year to potentially using multiple recent years ... see rules above
if (as.numeric(year)>=2022){
  SF_merge_stacked <- SF_merge_stacked %>%
    
    mutate(nYears_2016_2020=select(.,totcrime_2016,totcrime_2017,totcrime_2018,totcrime_2019,totcrime_2020) %>% 
             {
               rowSums(!is.na(.),na.rm=TRUE)
             }) %>%
    group_by(ORI_UNIVERSE) %>% #Note the group_by() here...
    mutate(max_totcrime_imp_2016_2020=ifelse(nYears_2016_2020>0,
                                             max(totcrime_imp_2016,totcrime_imp_2017,totcrime_imp_2018,totcrime_imp_2019,totcrime_imp_2020,na.rm=TRUE),
                                             0)) %>%
    ungroup()
  #Now process the recent years...
  SF_merge_stacked_recent <- map(recentSRSYrs,function(temp.year){
    SF_merge_stacked %>%
      mutate(!!paste0("totcrime_imp_",temp.year) := ifelse(eval(sym(paste0("resp_ind_srs_",temp.year)))==1,
                                                           eval(sym(paste0("totcrime_",temp.year)))*12/eval(sym(paste0("nMonths_SRS_",temp.year))),
                                                           0)) %>%
      select(paste0("totcrime_imp_",temp.year))
    
  }) %>% bind_cols()
  
  SF_merge_stacked <- SF_merge_stacked %>%
    bind_cols(SF_merge_stacked_recent)
  
  #Now pick which year we're using...
  tempEnv <- environment() #Current environment
  SF_merge_stacked <- SF_merge_stacked %>%
    mutate(use_year=NA_character_) #Initialize the year we're using to missing
  
  #We'll loop over the recent SRS years, updating use_year as we go
  #Note that list2env() will allow us to continuously update use_year after each year in recentSRSYrs... we won't be returning anything in the literal sense however
  map(recentSRSYrs,function(temp.year){
    temp.dat <- SF_merge_stacked %>%
      mutate(use_year=ifelse(is.na(use_year) & eval(sym(paste0("resp_ind_srs_",temp.year)))==1,temp.year,use_year))
    
    temp.out <- list(temp.dat)
    names(temp.out) <- "SF_merge_stacked"
    list2env(temp.out,env=tempEnv) #Push updated dataset to environment captured earlier
    return(NULL)
  })
  #Now that we have the recent SRS years done, let's fill in the remaining as either smoothed SRS or to be imputed
  SF_merge_stacked <- SF_merge_stacked %>%
    mutate(use_year=case_when(is.na(use_year) & nYears_2016_2020>=1 ~ as.character(SRS_YEAR), #No recent SRS available but have smoothed SRS --> Use smoothed SRS
                              is.na(use_year) ~ "Imputed", #No recent SRS or smoothed SRS available --> Impute
                              TRUE ~ use_year))
} else {
  SF_merge_stacked <- SF_merge_stacked %>%
    mutate(use_year=case_when(!is.na(totcrime_imp_smoothed) ~ as.character(SRS_YEAR),
                              TRUE ~ "Imputed"))
}
#Now set benchmark crime vars based on use_year
use_2016 <- SF_merge_stacked$use_year == "2016"
use_2017 <- SF_merge_stacked$use_year == "2017"
use_2018 <- SF_merge_stacked$use_year == "2018"
use_2019 <- SF_merge_stacked$use_year == "2019"
use_2020 <- SF_merge_stacked$use_year == "2020"
#Note (28Mar2024): Again, generalizing from 2022-only to 2022 onward
#Note (15May2024): Again, shifting which year to pick (e.g., allow 5 most recent years 2022 or later to be chosen)
if (as.numeric(year)>=2022){
  map(recentSRSYrs,function(temp.year){
    temp.ind <- SF_merge_stacked$use_year == as.character(temp.year) & 
      getElement(SF_merge_stacked,paste0("resp_ind_srs_",temp.year))==1
    temp.out <- list(temp.ind)
    names(temp.out) <- paste0("use_",temp.year)
    
    list2env(temp.out,tempEnv)
  })
  
}
use_imputed <- SF_merge_stacked$use_year == "Imputed"

crimeVarsBenchImp <- colnames(srs2016_2020_smoothed_raw) %>% str_subset("_imp")
crimeVarsBenchRaw <- colnames(srs2016_2020_smoothed_raw) %>% str_subset("^totcrime") %>% str_subset("_(rec|imp)",negate=TRUE)
SF_merge_stacked[use_2016,c(crimeVarsBenchRaw,crimeVarsBenchImp)] <- SF_merge_stacked[use_2016,paste0(c(crimeVarsBenchRaw,crimeVarsBenchImp),"_2016")]
SF_merge_stacked[use_2017,c(crimeVarsBenchRaw,crimeVarsBenchImp)] <- SF_merge_stacked[use_2017,paste0(c(crimeVarsBenchRaw,crimeVarsBenchImp),"_2017")]
SF_merge_stacked[use_2018,c(crimeVarsBenchRaw,crimeVarsBenchImp)] <- SF_merge_stacked[use_2018,paste0(c(crimeVarsBenchRaw,crimeVarsBenchImp),"_2018")]
SF_merge_stacked[use_2019,c(crimeVarsBenchRaw,crimeVarsBenchImp)] <- SF_merge_stacked[use_2019,paste0(c(crimeVarsBenchRaw,crimeVarsBenchImp),"_2019")]
SF_merge_stacked[use_2020,c(crimeVarsBenchRaw,crimeVarsBenchImp)] <- SF_merge_stacked[use_2020,paste0(c(crimeVarsBenchRaw,crimeVarsBenchImp),"_2020")]
#Note (28Mar2024): Again, generalizing from 2022-only to 2022 onward. Also, rename _cYr variables to actually use the current year (e.g., _2023).
#Note (15May2024): Again, we'll now need to loop over the recent SRS years... also, no longer need to change _cYr to the actual year...
if (as.numeric(year)>=2022){
  map(recentSRSYrs,function(temp.year){
    #Create raw version of the SRS calibration variables (for records that will use temp.year SRS)
    SF_merge_stacked[eval(sym(paste0("use_",temp.year))),crimeVarsBenchRaw] <- SF_merge_stacked[eval(sym(paste0("use_",temp.year))),paste0(crimeVarsBenchRaw,"_",temp.year)] 
    
    #Create imputed version of the SRS calibration variables (for records that will use temp.year SRS)
    SF_merge_stacked[eval(sym(paste0("use_",temp.year))),crimeVarsBenchImp] <- SF_merge_stacked[eval(sym(paste0("use_",temp.year))),paste0(crimeVarsBenchRaw,"_",temp.year)]*12/as.matrix(SF_merge_stacked[eval(sym(paste0("use_",temp.year))),paste0("nMonths_SRS_",temp.year)])
    
    temp.out <- list(SF_merge_stacked)
    names(temp.out) <- "SF_merge_stacked"
    list2env(temp.out,tempEnv)
    return(NULL)
  })
  
} 
#Make sure records set to be imputed are missing going into imputation
SF_merge_stacked[use_imputed,crimeVarsBenchImp] <- NA_real_ 
#####
#Update (25AUG2021): Add imputation for LEAs not in SRS 2016-2020
#Impute crime values
#Note: will be based on original SRS imputation program


###########
#Existing LEAs
#No imputation needed; separate by FBI group for use with 0-2 month LEAs
tot_typeVars <- paste0("totcrime_", c("murder","manslaughter","rape","rob","assault","aggAssault","simpAssault","burglary","larceny","vhcTheft"))
tot_type_impVars <- paste0("totcrime_", c("murder","manslaughter","rape","rob","assault","aggAssault","simpAssault","burglary","larceny","vhcTheft"), "_imp")

#Assign imputed versions of counts using originals, split by FBI group
flag0LEAs <- SF_merge_stacked %>%
  subset(use_year != "Imputed" & totcrime==totcrime_imp) %>% #Only include records for full reporters
  mutate(groupImp=case_when(
    #Cities 250,000 or over
    POPULATION_GROUP_DESC=="Cities 1,000,000 or over" ~ 1,
    POPULATION_GROUP_DESC=="Cities from 500,000 thru 999,999" ~ 1,
    POPULATION_GROUP_DESC=="Cities from 250,000 thru 499,999" ~ 1,
    #Cities from 100,000 - 249,999
    POPULATION_GROUP_DESC=="Cities from 100,000 thru 249,999" ~ 2,
    #Cities from 50,000 - 99,999
    POPULATION_GROUP_DESC=="Cities from 50,000 thru 99,999" ~ 3,
    #Cities from 25,000 - 49,999
    POPULATION_GROUP_DESC=="Cities from 25,000 thru 49,999" ~ 4,
    #Cities from 10,000 - 24,999
    POPULATION_GROUP_DESC=="Cities from 10,000 thru 24,999" ~ 5,
    #Cities from 2,500 - 9,999
    POPULATION_GROUP_DESC=="Cities from 2,500 thru 9,999" ~ 6,
    #Cities under 2,500
    POPULATION_GROUP_DESC=="Cities under 2,500" ~ 7,
    #Non-MSA counties and non-MSA State Police
    POPULATION_GROUP_DESC=="Non-MSA counties 100,000 or over" ~ 8,
    POPULATION_GROUP_DESC=="Non-MSA counties from 25,000 thru 99,999" ~ 8,
    POPULATION_GROUP_DESC=="Non-MSA counties from 10,000 thru 24,999" ~ 8,
    POPULATION_GROUP_DESC=="Non-MSA counties under 10,000" ~ 8,
    POPULATION_GROUP_DESC=="Non-MSA State Police" ~ 8,
    #MSA counties and MSA State Police
    POPULATION_GROUP_DESC=="MSA counties 100,000 or over" ~ 9,
    POPULATION_GROUP_DESC=="MSA counties from 25,000 thru 99,999" ~ 9,
    POPULATION_GROUP_DESC=="MSA counties from 10,000 thru 24,999" ~ 9,
    POPULATION_GROUP_DESC=="MSA counties under 10,000" ~ 9,
    POPULATION_GROUP_DESC=="MSA State Police" ~ 9,
    TRUE ~ 0
  )) %>%
  split(.,.$groupImp)


#Make the names dynamic
flag0LEAs_group <- names(flag0LEAs) %>% as.numeric()
log_debug("Make the names dynamic")
print(flag0LEAs_group)

names(flag0LEAs) <- paste0("flag0Group",flag0LEAs_group)

#Count number of rows for FBI group
log_debug("Count number of rows for FBI group")
nFlag0LEAs <- sapply(paste0("flag0Group", flag0LEAs_group), function(x){nrow(flag0LEAs[[x]])})
print(nFlag0LEAs)
###
#To be imputed
flag1LEAs <- SF_merge_stacked %>%
  subset(use_year=="Imputed") %>%
  select(-matches("tot.*_imp$")) %>%
  mutate(groupImp=case_when(
    #Cities 250,000 or over
    POPULATION_GROUP_DESC=="Cities 1,000,000 or over" ~ 1,
    POPULATION_GROUP_DESC=="Cities from 500,000 thru 999,999" ~ 1,
    POPULATION_GROUP_DESC=="Cities from 250,000 thru 499,999" ~ 1,
    #Cities from 100,000 - 249,999
    POPULATION_GROUP_DESC=="Cities from 100,000 thru 249,999" ~ 2,
    #Cities from 50,000 - 99,999
    POPULATION_GROUP_DESC=="Cities from 50,000 thru 99,999" ~ 3,
    #Cities from 25,000 - 49,999
    POPULATION_GROUP_DESC=="Cities from 25,000 thru 49,999" ~ 4,
    #Cities from 10,000 - 24,999
    POPULATION_GROUP_DESC=="Cities from 10,000 thru 24,999" ~ 5,
    #Cities from 2,500 - 9,999
    POPULATION_GROUP_DESC=="Cities from 2,500 thru 9,999" ~ 6,
    #Cities under 2,500
    POPULATION_GROUP_DESC=="Cities under 2,500" ~ 7,
    #Non-MSA counties and non-MSA State Police
    POPULATION_GROUP_DESC=="Non-MSA counties 100,000 or over" ~ 8,
    POPULATION_GROUP_DESC=="Non-MSA counties from 25,000 thru 99,999" ~ 8,
    POPULATION_GROUP_DESC=="Non-MSA counties from 10,000 thru 24,999" ~ 8,
    POPULATION_GROUP_DESC=="Non-MSA counties under 10,000" ~ 8,
    POPULATION_GROUP_DESC=="Non-MSA State Police" ~ 8,
    #MSA counties and MSA State Police
    POPULATION_GROUP_DESC=="MSA counties 100,000 or over" ~ 9,
    POPULATION_GROUP_DESC=="MSA counties from 25,000 thru 99,999" ~ 9,
    POPULATION_GROUP_DESC=="MSA counties from 10,000 thru 24,999" ~ 9,
    POPULATION_GROUP_DESC=="MSA counties under 10,000" ~ 9,
    POPULATION_GROUP_DESC=="MSA State Police" ~ 9,
    TRUE ~ 0
  )) %>%
  split(.,.$groupImp)

if (length(flag1LEAs)>0){
  #Create new flag1LEAs_group variable to identify groups that needs imputation
  log_debug("Create new flag1LEAs_group variable to identify groups that needs imputation")
  flag1LEAs_group <- names(flag1LEAs) %>% as.numeric()
  print(flag1LEAs_group)
  
  names(flag1LEAs) <- paste0("flag1Group", flag1LEAs_group)
  
  
  #Count number of rows for FBI group
  log_debug("Count number of rows for FBI group")
  nFlag1LEAs <- sapply(paste0("flag1Group", flag1LEAs_group) ,function(x){nrow(flag1LEAs[[x]])})
  print(nFlag1LEAs)
  #Randomly select 12 month LEA in FBI group - use that LEA's crime totals
  
  
  #set.seed(1)
  flag1LEAsImp <- sapply(flag1LEAs_group,function(x){
    #############
    #Randomly select reference agency per 0-2 month agency
    sample.int(nFlag0LEAs[paste0("flag0Group", x)],nFlag1LEAs[paste0("flag1Group", x)], replace=TRUE) %>%
      flag0LEAs[[paste0("flag0Group", x)]][.,c("ORI","totcrime_imp","LEGACY_ORI",tot_type_impVars)] %>%
      rename(.,ORI_imp=ORI,LEGACY_ORI_imp=LEGACY_ORI) %>%
      #############
    #Merge imputed count variables with original record
    select(.,ORI_imp,LEGACY_ORI_imp,totcrime_imp,tot_type_impVars) %>%
      cbind(flag1LEAs[[paste0("flag1Group", x)]],.) %>%
      list(.)
  })
  names(flag1LEAsImp) <- paste0("flag1Group",flag1LEAs_group,"Imp")
  
  flag1LEAsImp <- flag1LEAsImp %>% bind_rows()
} else {
  flag1LEAsImp <- flag1LEAs %>% bind_rows()
}


#####
#Stack
SF_mergeAll <- bind_rows(SF_merge_stacked %>% subset(use_year != "Imputed"),
                         flag1LEAsImp) %>%
  data.frame() %>%
  #Note (09Jan2023): Creating violent/property sums
  mutate(totcrime_violent_imp=select(.,totcrime_murder_imp,totcrime_manslaughter_imp,totcrime_rape_imp,totcrime_rob_imp,totcrime_aggAssault_imp) %>%
           rowSums(.,na.rm=TRUE),
         totcrime_property_imp=select(.,totcrime_burglary_imp,totcrime_larceny_imp,totcrime_vhcTheft_imp) %>% #,totcrime_arson_imp)
           rowSums(.,na.rm=TRUE))


SF_all <- SF_mergeAll
SF <- SF_all


# flag 0-population agencies
SF$zeropopLEA <- as.numeric(SF$POPULATION == 0)




#######################
# move LEAs in stratum_f 2 that are not in NCSX_stratum 2 to stratum_f 3 or 5 based on type
#Update (24AUG2021): Remove references to NCSX stratum
#Note (27OCT2021): Confirm handling?
SF$stratum_f[SF$stratum_f == 2  & SF$AGENCY_TYPE_NAME == "Other State Agency"] <- 3
SF$stratum_f[SF$stratum_f == 2  & SF$AGENCY_TYPE_NAME == "State Police"] <- 3
SF$stratum_f[SF$stratum_f == 2  & SF$AGENCY_TYPE_NAME == "County"] <- 5
SF$stratum_f[SF$stratum_f == 2  & SF$AGENCY_TYPE_NAME == "City"] <- 5

# else, for situations where NCSX_stratum is non-missing, recode stratum_f to NCSX_stratum
#Update (24AUG2021): Remove reference to NCSX stratum
#SF$stratum_f <- ifelse(is.na(SF$NCSX_Stratum) == FALSE, SF$NCSX_Stratum, SF$stratum_f)

# verify coding worked as planned
#table(SF$NCSX_Stratum, SF$stratum_f, useNA = "always")

# reassign stratum 4 (state/muni LEAs with 0 officers in 2011) to stratum 10 (agency type = City) or stratum 3 (all others)
SF$stratum_f[SF$stratum_f == 4 & SF$AGENCY_TYPE_NAME == "City"] <- 10
SF$stratum_f[SF$stratum_f == 4 & (SF$AGENCY_TYPE_NAME == "Other State Agency" |
                                    SF$AGENCY_TYPE_NAME == "State Police" |
                                    SF$AGENCY_TYPE_NAME == "University or College")] <- 3




#######################
# output data for next program in sequence

#write.csv(SF,
fwrite_wrapper(SF,
               paste0(output_weighting_data_folder,"SF.csv"))

log_info("Finished 02_Weights_Data_Setup.R\n\n")
