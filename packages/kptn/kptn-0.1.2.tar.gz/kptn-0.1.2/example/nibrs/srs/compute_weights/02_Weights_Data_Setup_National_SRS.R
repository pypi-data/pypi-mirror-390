#Note: this is a modified version of a program originally created by Taylor Lewis.


### Purpose of program is to create a working NIBRS data set for implementing various calibration weighting strategies
### Author: Taylor Lewis
### Modified by JD Bunker
### Last updated: 20Jul2023


# key difference in this version is not treating all 400 NCS-X LEAs as reporters, only those that are reporting
# do not need to do naive design-based strategy here
# another modification on 9.28.20 is introducing a condition where we poststratify to combination of zeropop LEAs indicator and population size
#Note (JDB 20Jul2023): Incorporating outlier results
#Note (JDB 12Nov2024): Creating version that will be used when creating the 30 years of SRS estimates (1993-2023)
#					   It will be the same as the other version, except that it supports use of 5 most recent years of SRS for before 2020,
#					   uses legacy rape for years before 2013 (2013 and later will use revised rape),
#                      and doesn't merge on the county-level pop estimates or the JD/FO crosswalks

### load necessary packages

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

log_info("Running 02_Weights_Data_Setup_SRS.R")

### preparing the sampling frame
# read in and recode the sampling frame
#Update (05NOV2021): Adding guess_max argument
#SF <- read_csv(paste0(output_weighting_data_folder,"cleanframe.csv"),
#               guess_max=1e6)
SF <- fread(paste0(output_weighting_data_folder,"cleanframe_srs.csv")) %>%
  data.frame() %>%
  mutate(in_srs=as.double(in_srs))

# rename LEGACY_ORI to ORI_universe to match JD's file
SF$ORI_universe <- SF$ORI_UNIV


# merge in some fields from the UCR SRS crime report data
#Note (21MAY2021): using 2018 SRS instead of 2020
#Note (27OCT2021): using 2016-2020 smoothed SRS. Has been the case but adding note.
#Note (06DEC2024): only read in and merge smoothed SRS for 2020 onward
if (as.numeric(year)>=2020){
srs2016_2020_smoothed_raw <- fread("../../tasks/compute_weights/Data/srs2016_2020_smoothed.csv")

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
srs2016_2020_smoothed_allYrs <- fread("../../tasks/compute_weights/Data/srs2016_2020_smoothed_allYrs.csv")

# keep only the needed fields from this file
srs2016_2020_smoothed_allYrs <- srs2016_2020_smoothed_allYrs %>%
  select(ORI_UNIVERSE,LEGACY_ORI,SRS_YEAR,matches("^totcrime"))

#Merge together the 2 smoothed datasets
srs2016_2020_smoothed <- srs2016_2020_smoothed %>%
  full_join(srs2016_2020_smoothed_allYrs)

crimeVars <- colnames(srs2016_2020_smoothed) %>% str_subset("^totcrime")


#######################
#Update (21MAY2021): Since we're switching from 2020 SRS to 2018 SRS, need to change merge strategy
#Note (27OCT2021): We're now using smoothed 2016-2020 SRS, but methodology otherwise applies
#Note (25Jul2023): Adding SRS_YEAR to all joins
SF_merge1A_inner <- inner_join(SF,
                               srs2016_2020_smoothed %>% select(ORI_UNIVERSE,SRS_YEAR,all_of(crimeVars)),
                               by = c("ORI_UNIV" = "ORI_UNIVERSE"))
log_dim(SF_merge1A_inner)

#Get the unmatched ones
SF_merge1A_anti <- anti_join(SF,
                             srs2016_2020_smoothed %>% select(ORI_UNIVERSE,SRS_YEAR,all_of(crimeVars)),
                             by = c("ORI_UNIV" = "ORI_UNIVERSE"))
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
  inner_join(srs2016_2020_smoothed %>% select(LEGACY_ORI,SRS_YEAR,all_of(crimeVars)), by=c("ORI" = "LEGACY_ORI") )
log_dim(SF_merge1C_inner)

#Get the unmatched ones
SF_merge1C_anti <- SF_merge1B_anti %>%
  anti_join(srs2016_2020_smoothed %>% select(LEGACY_ORI,SRS_YEAR,all_of(crimeVars)), by=c("ORI" = "LEGACY_ORI") )
log_dim(SF_merge1C_anti)

#####
#Stack datasets together and summarize 2022 SRS
#Note (28Mar2024): Generalizing to use current year SRS for 2022 onward (will run into errors if we don't have both the full NIBRS and SRS for a year, in which case we simply patch the below code)
#Note (16May2024): Overhauling how we use SRS (from email with Marcus on 30Apr2024):
# 1.	Use current year SRS (e.g., 2023 this year)
# 2.	Use current year minus 1 SRS if current year not available
# 3.	Use 5-year smoothed SRS starting with current year minus 2 if current year and current year minus 1 is not available
#Note (12Nov2024): Use 5 most recent years for years before 2020
#Note (12Nov2024): Also, use revised rape for 2013 and later, and use legacy rape for years before 2013
SF_merge_stacked <- bind_rows(SF_merge1A_inner,SF_merge1B_inner,SF_merge1C_inner,SF_merge1C_anti) 
} else {
  #For remaining years, just use the existing frame
 SF_merge_stacked <- SF
}
if (as.numeric(year)>=2022|as.numeric(year)<2020){
  if (as.numeric(year)>=2022){
    recentSRSYrs <- (as.numeric(year):2022)[1:min(length(as.numeric(year):2022),5)]
  } else {
    recentSRSYrs <- as.numeric(year):(as.numeric(year)-4)
  }
  #23Dec2024: this code didn't actually do anything so commenting out
  #smoothedSRSYrs <- 2016:2020
  #Current year SRS
  SF_merge_stacked <- SF_merge_stacked %>%
    rename(m01_murder=v70, #January
           m01_mnslghtr=v71,
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
    ) 
	if (as.numeric(year)>=2013){
	  SF_merge_stacked <- SF_merge_stacked %>%
	    rename(m01_rapetotal=v72, #January
               m01_forcerape=v73,
               m01_attrape=v74,		
			   
			   m02_rapetotal=v190, #Feburary
			   m02_forcerape=v191,
			   m02_attrape=v192,
			   
			   m03_rapetotal=v308, #March
			   m03_forcerape=v309,
			   m03_attrape=v310,
			   
			   m04_rapetotal=v426, #April
			   m04_forcerape=v427,
			   m04_attrape=v428,
			   
			   m05_rapetotal=v544, #May
			   m05_forcerape=v545,
			   m05_attrape=v546, 
		   
			   m06_rapetotal=v662, #June
			   m06_forcerape=v663,
			   m06_attrape=v664,
			   
			   m07_rapetotal=v780, #July
			   m07_forcerape=v781,
			   m07_attrape=v782,
			   
			   m08_rapetotal=v898, #August
			   m08_forcerape=v899,
			   m08_attrape=v900,
		   
			   m09_rapetotal=v1016, #September
			   m09_forcerape=v1017,
			   m09_attrape=v1018,
			   
			   m10_rapetotal=v1134, #October
			   m10_forcerape=v1135,
			   m10_attrape=v1136,
			   
			   m11_rapetotal=v1252, #November
			   m11_forcerape=v1253,
			   m11_attrape=v1254,
			   
			   m12_rapetotal=v1370, #December
			   m12_forcerape=v1371,
			   m12_attrape=v1372)
	} else if (as.numeric(year)<2013){
	  SF_merge_stacked <- SF_merge_stacked %>%
	    rename(m01_rapetotal=v96,
		       m02_rapetotal=v214,
			   m03_rapetotal=v332,
			   m04_rapetotal=v450,
			   m05_rapetotal=v568,
			   m06_rapetotal=v686,
			   m07_rapetotal=v804,
			   m08_rapetotal=v922,
			   m09_rapetotal=v1040,
			   m10_rapetotal=v1158,
			   m11_rapetotal=v1276,
			   m12_rapetotal=v1394)
	}
	SF_merge_stacked <- SF_merge_stacked %>%
    #select(-matches("totcrime")) %>%
    #06Jun2024: adding nMonths and response indicator for current year
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
    mutate(totcrime_cYr=totcrime_violent_cYr+totcrime_property_cYr) %>%
	#13Dec2024: use ORI_UNIV, not ORI
	select(-ORI) %>%
	rename(ORI=ORI_UNIV)
  
  colnames(SF_merge_stacked) <- str_replace(colnames(SF_merge_stacked),
                                            "_cYr",
                                            paste0("_",as.character(year)))
  
  
  #16May2024: for 2023 and later, we're now going to loop over the remaining recent SRS years
  #12Nov2024: expanding to 4 other most recent years for years before 2020
  if (as.numeric(year)>=2023|as.numeric(year)<2020){
    map(recentSRSYrs[-1],function(temp.year){
      ucr_srs_clean_raw <- paste0(raw_srs_file_path,"/UCR_SRS_",temp.year,"_clean_reta_mm_selected_vars.csv") %>%
        read_csv()
      
      ucr_srs_clean <- ucr_srs_clean_raw %>%
    rename(m01_murder=v70, #January
           m01_mnslghtr=v71,
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
    ) 
	if (temp.year>=2013){
	  ucr_srs_clean <- ucr_srs_clean %>%
	    rename(m01_rapetotal=v72, #January
               m01_forcerape=v73,
               m01_attrape=v74,		
			   
			   m02_rapetotal=v190, #Feburary
			   m02_forcerape=v191,
			   m02_attrape=v192,
			   
			   m03_rapetotal=v308, #March
			   m03_forcerape=v309,
			   m03_attrape=v310,
			   
			   m04_rapetotal=v426, #April
			   m04_forcerape=v427,
			   m04_attrape=v428,
			   
			   m05_rapetotal=v544, #May
			   m05_forcerape=v545,
			   m05_attrape=v546, 
		   
			   m06_rapetotal=v662, #June
			   m06_forcerape=v663,
			   m06_attrape=v664,
			   
			   m07_rapetotal=v780, #July
			   m07_forcerape=v781,
			   m07_attrape=v782,
			   
			   m08_rapetotal=v898, #August
			   m08_forcerape=v899,
			   m08_attrape=v900,
		   
			   m09_rapetotal=v1016, #September
			   m09_forcerape=v1017,
			   m09_attrape=v1018,
			   
			   m10_rapetotal=v1134, #October
			   m10_forcerape=v1135,
			   m10_attrape=v1136,
			   
			   m11_rapetotal=v1252, #November
			   m11_forcerape=v1253,
			   m11_attrape=v1254,
			   
			   m12_rapetotal=v1370, #December
			   m12_forcerape=v1371,
			   m12_attrape=v1372)
	} else if (temp.year<2013){
	  ucr_srs_clean <- ucr_srs_clean %>% 
	    rename(m01_rapetotal=v96,
		       m02_rapetotal=v214,
			   m03_rapetotal=v332,
			   m04_rapetotal=v450,
			   m05_rapetotal=v568,
			   m06_rapetotal=v686,
			   m07_rapetotal=v804,
			   m08_rapetotal=v922,
			   m09_rapetotal=v1040,
			   m10_rapetotal=v1158,
			   m11_rapetotal=v1276,
			   m12_rapetotal=v1394)
	}
	ucr_srs_clean <- ucr_srs_clean %>% 
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
    #Now, let's merge them all together (except for current year)
    ucr_srs_othrecent <- Reduce(full_join,mget(paste0("ucr_srs_",recentSRSYrs[-1])))
    #Now merge together the current year and other recent years
    SF_merge_stacked <- SF_merge_stacked %>%
      left_join(ucr_srs_othrecent)
  }
}
#######################
### inspect missing data patterns
# create a 0/1 indicator for whether the LEA is currently reporting to SRS
#Note (25Jul2023): moving up where this is done so we'll have it in time for imputation
#Note (16May2024): Creating dup of resp_ind_srs for current year (will use this version later when picking the SRS year to use)
SF_merge_stacked <- SF_merge_stacked %>%
  mutate(resp_ind_srs=ifelse(str_count(srs_month,"1")>=3,
                             1,
                             0),
         srs_month_adj = srs_month) %>%
  mutate(!!paste0("resp_ind_srs_",year) := resp_ind_srs)


#Incorporating outlier results
tempEnv <- environment()
sapply(c(1,2,3,5,6,7,9,10,11,13,14,15),function(i){
  #1st, let's determine records that need to be updated
  inds <- SF_merge_stacked %>%
    mutate(ind=(str_sub(srs_month_adj,i,i)=="1" & str_sub(outlier,i,i)=="0")) %>%
    pull(ind)
  #2nd, assign as nonreporters for that month
  str_sub(SF_merge_stacked[inds,"srs_month_adj"],i,i) <- "0"
  list2env(list("SF_merge_stacked"=SF_merge_stacked),envir=tempEnv)
  return(NULL)
})
#Update (29JUL2021): Treat Type I agencies who only reported 1 or 2 months according to reta-mm (Missingmonths) data file as Nonrespondent
#Update (11MAR2022): For agencies with 50+ total crimes in the smoothed SRS, check if in NIBRS database
#Update (15MAR2022): Limit list of NIBRS reporters to those with start dates before November of the data year
#Update (23MAR2022): Ignore months in reta-MM before start date; create reta_MM_adj and use in place of reta_MM variable
#Update (23MAR2022): Switching from reta-MM to nibrs_month - variable is analogous to reta_MM
SF_merge_stacked <- SF_merge_stacked %>%
  #mutate(nTimes=month(as_date(NIBRS_START_DATE,format="%d-%B-%y"))-1L) %>%
  #mutate(nTimes=ifelse(is.na(nTimes),
  #                     0,
  #                     nTimes)) %>%
  #If year of start date same as data year, set all months prior to start as 0s (will work even if start date in January)
  #Else if start year comes after data year, set all months to 0s
  #Else leave reta_MM alone
  # mutate(reta_MM_adj=case_when(year(as_date(NIBRS_START_DATE,format="%d-%B-%y"))==year ~  str_remove_all(reta_MM,"-") %>% 
  #                                str_replace(pattern=paste0("^.{",nTimes,"}"),
  #                                            replacement=str_dup("0",times=nTimes)),
  #                              year(as_date(NIBRS_START_DATE,format="%d-%B-%y")) > year ~ str_remove_all(reta_MM,"-") %>% 
#                                str_replace(pattern=paste0("^.{",12,"}"),
#                                            replacement=str_dup("0",times=12)),
#                              TRUE ~ reta_MM)) %>%
# mutate(resp_ind_m3=case_when(resp_ind_m3==1 & str_count(reta_MM_adj,"1")<3 ~0,
#                              TRUE ~ resp_ind_m3)) %>%
#Note (16May2023): Commenting out adjustments for now
# mutate(nibrs_month_adj=case_when(year(as_date(NIBRS_START_DATE,format="%d-%B-%y"))==year ~  str_remove_all(nibrs_month,"-") %>% 
#                                    str_replace(pattern=paste0("^.{",nTimes,"}"),
#                                                replacement=str_dup("0",times=nTimes)),
#                                  
#                                  year(as_date(NIBRS_START_DATE,format="%d-%B-%y")) > year ~ str_remove_all(nibrs_month,"-") %>% 
#                                    str_replace(pattern=paste0("^.{",12,"}"),
#                                                replacement=str_dup("0",times=12)),
#                                  is.na(NIBRS_START_DATE) ~ str_dup("0",times=12),
#                                  TRUE ~ srs_month %>% str_remove_all("-"))) %>%
mutate(resp_ind_srs=case_when(resp_ind_srs==1 & str_count(srs_month_adj,"1")<3 ~0,
                              TRUE ~ resp_ind_srs)) %>%
  mutate(in_srs=case_when(is.na(in_srs) ~ 0,
                          TRUE ~ in_srs)) #%>%
  #06Dec2024: moving this condition from here to after we create the imputed totals
  #mutate(resp_ind_srs=case_when(resp_ind_srs==1 & totcrime_imp_smoothed>=50 ~ in_srs,
  #                              TRUE ~ resp_ind_srs)) #%>%
#mutate(resp_ind_srs=case_when(resp_ind_srs==1 & as_date(NIBRS_START_DATE,format="%d-%B-%y")>=as_date(paste0(year,"-11-01")) ~ 0,
#                              TRUE ~ resp_ind_srs))

#####
#Choose which year of SRS to use
#Note (28Mar2024): Again, generalizing from 2022-only to 2022 onward
#Note (16May2024): Again, shifted from always using only current year to potentially using multiple recent years ... see rules above
#Note (12Nov2024): Using 5 most recent years for years before 2020

#13Dec2024: moved this if() statement out of the if () statement it was nested within
if (as.numeric(year)>=2020){
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
  }
if (as.numeric(year)>=2022|as.numeric(year)<2020){
  #06Dec2024: only run this for 2020 and later
  
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
  
} else {
  #13Dec2024: rather than set use_year here, just initialize to missing
  SF_merge_stacked <- SF_merge_stacked %>%
    #mutate(use_year=case_when(!is.na(totcrime_imp_smoothed) ~ as.character(SRS_YEAR),
    #                          TRUE ~ "Imputed"))
    mutate(use_year=NA_character_)
}

#13Dec2024: moved this from within the if() statement above
#Now that we have the recent SRS years done, let's fill in the remaining as either smoothed SRS or to be imputed
  #12Nov2024: updating so that we only use smoothed SRS for 2020 thru 2025 
  #06Dec2024: changing this from a single mutate() to 2 mutate() calls depending on year
  if (as.numeric(year) %in% 2020:2025){
  SF_merge_stacked <- SF_merge_stacked %>%
    mutate(use_year=case_when(is.na(use_year) & nYears_2016_2020>=1 ~ as.character(SRS_YEAR), #No recent SRS available but have smoothed SRS --> Use smoothed SRS
                              is.na(use_year) ~ "Imputed", #No recent SRS or smoothed SRS available --> Impute
                              TRUE ~ use_year))
  } else {
    SF_merge_stacked <- SF_merge_stacked %>%
    mutate(use_year=case_when(is.na(use_year) ~ "Imputed", #No recent SRS or smoothed SRS available --> Impute
                              TRUE ~ use_year))
  }
  
#Now set benchmark crime vars based on use_year
#06Dec2024: only creating 2016-2020 variables for 2020-2025
if (as.numeric(year) %in% 2020:2025){
use_2016 <- SF_merge_stacked$use_year == "2016"
use_2017 <- SF_merge_stacked$use_year == "2017"
use_2018 <- SF_merge_stacked$use_year == "2018"
use_2019 <- SF_merge_stacked$use_year == "2019"
use_2020 <- SF_merge_stacked$use_year == "2020"
}
#Note (28Mar2024): Again, generalizing from 2022-only to 2022 onward
#Note (16May2024): Again, shifting which year to pick (e.g., allow 5 most recent years after 2022 to be chosen)
#Note (12Nov2024): Using 5 most recent years for years before 2020
if (as.numeric(year)>=2022|as.numeric(year)<2020){
  map(recentSRSYrs,function(temp.year){
    temp.ind <- SF_merge_stacked$use_year == as.character(temp.year) & 
      getElement(SF_merge_stacked,paste0("resp_ind_srs_",temp.year))==1
    temp.out <- list(temp.ind)
    names(temp.out) <- paste0("use_",temp.year)
    
    list2env(temp.out,tempEnv)
  })
  
}
use_imputed <- SF_merge_stacked$use_year == "Imputed"

#06Dec2024: get variables off SF_merge_stacked, not smoothed SRS
#13Dec2024: just manually specify them...
#crimeVarsBenchImp <- colnames(srs2016_2020_smoothed_raw) %>% str_subset("_imp")
#crimeVarsBenchRaw <- colnames(srs2016_2020_smoothed_raw) %>% str_subset("^totcrime") %>% str_subset("_(rec|imp)",negate=TRUE)
#crimeVarsBenchRaw <- colnames(SF_merge_stacked) %>% str_subset("^totcrime.*_\\d{4}") %>% str_remove("_imp_\\d{4}$") %>% unique()
crimeVarsBenchRaw <- c("totcrime",
                       str_c("totcrime_", 
					         c("murder",
							   "manslaughter",
							   "rape",
							   "rob",
							   "assault",
							   "aggAssault",
							   "simpAssault",
							   "burglary",
							   "larceny",
							   "vhcTheft",
							   "violent",
							   "property")))
crimeVarsBenchImp <- str_c(crimeVarsBenchRaw,"_imp")
#06Dec2024: only creating 2016-2020 variables for 2020-2025
if (as.numeric(year) %in% 2020:2025){
SF_merge_stacked[use_2016,c(crimeVarsBenchRaw,crimeVarsBenchImp)] <- SF_merge_stacked[use_2016,paste0(c(crimeVarsBenchRaw,crimeVarsBenchImp),"_2016")]
SF_merge_stacked[use_2017,c(crimeVarsBenchRaw,crimeVarsBenchImp)] <- SF_merge_stacked[use_2017,paste0(c(crimeVarsBenchRaw,crimeVarsBenchImp),"_2017")]
SF_merge_stacked[use_2018,c(crimeVarsBenchRaw,crimeVarsBenchImp)] <- SF_merge_stacked[use_2018,paste0(c(crimeVarsBenchRaw,crimeVarsBenchImp),"_2018")]
SF_merge_stacked[use_2019,c(crimeVarsBenchRaw,crimeVarsBenchImp)] <- SF_merge_stacked[use_2019,paste0(c(crimeVarsBenchRaw,crimeVarsBenchImp),"_2019")]
SF_merge_stacked[use_2020,c(crimeVarsBenchRaw,crimeVarsBenchImp)] <- SF_merge_stacked[use_2020,paste0(c(crimeVarsBenchRaw,crimeVarsBenchImp),"_2020")]
}
#Note (28Mar2024): Again, generalizing from 2022-only to 2022 onward. Also, rename _cYr variables to actually use the current year (e.g., _2023).
#Note (16May2024): Again, we'll now need to loop over the recent SRS years... also, no longer need to change _cYr to the actual year...
#Note (12Nov2024): Using 5 most recent years for years before 2020
if (as.numeric(year)>=2022|as.numeric(year)<2020){
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

#04Dec2024: create total officer Count
SF_merge_stacked <- SF_merge_stacked %>%
  mutate(TOT_OFFICER_COUNT=MALE_OFFICER_UNIV+FEMALE_OFFICER_UNIV)
####
#Update (25AUG2021): Add imputation for LEAs not in SRS 2016-2020
#Impute crime values
#Note: will be based on original SRS imputation program


###########
#Existing LEAs
#No imputation needed; separate by FBI group for use with 0-2 month LEAs
tot_typeVars <- paste0("totcrime_", c("murder","manslaughter","rape","rob","assault","aggAssault","simpAssault","burglary","larceny","vhcTheft"))
tot_type_impVars <- paste0("totcrime_", c("murder","manslaughter","rape","rob","assault","aggAssault","simpAssault","burglary","larceny","vhcTheft"), "_imp")

#Assign imputed versions of counts using originals, split by FBI group
#Note (26Jul2023): Only use records that are full reporters
#Note (24Nov2024): Recently switched to imputation groups that match our weighting groups.
#                  Today, I'm also supporting collapsing (e.g., need to impute when <50 donors)
#Note (09Dec2024): Automatically split 0 pop groups into up to 4 subgroups each based on ctree()
#                  If ctree() yields <4 groups, pad out using dummy groups 
#                  (e.g., TOT_OFFICER_COUNT == 0, which will already be covered by existing group)
#Note (11Dec2024): Actually, fill in with TRUE... 
#                  Also, if ctree() says not to split at all, make sure that's TRUE too
#Note (13Dec2024): Use different donor condition for 2020 & 2021 vs. every other year
#Note (23Dec2024): Issues calibrating 0 pop cities in 1996 ... try without splitting
#Zero Pop Cities
if (as.numeric(year) %in% 2020:2021){
rules0PopCities <- SF_merge_stacked %>%
  subset(use_year != "Imputed" & totcrime==totcrime_imp) %>%
  #subset(use_year == year & str_count(srs_month_adj,"1")==12) %>%
  mutate(TOT_OFFICER_COUNT=MALE_OFFICER_UNIV+FEMALE_OFFICER_UNIV) %>%
  subset(POPULATION_GROUP_DESC_UNIV=="Cities under 2,500" & POPULATION_UNIV==0) %>%
  ctree(formula=totcrime_imp ~ TOT_OFFICER_COUNT,control=ctree_control(minbucket=30,maxdepth=2)) %>%
  partykit:::.list.rules.party()
} else if (as.numeric(year) %in% 1996){
rules0PopCities <- SF_merge_stacked %>%
  #subset(use_year != "Imputed" & totcrime==totcrime_imp) %>%
  subset(use_year == year & str_count(srs_month_adj,"1")==12) %>%
  mutate(TOT_OFFICER_COUNT=MALE_OFFICER_UNIV+FEMALE_OFFICER_UNIV) %>%
  subset(POPULATION_GROUP_DESC_UNIV=="Cities under 2,500" & POPULATION_UNIV==0) %>%
  ctree(formula=totcrime_imp ~ TOT_OFFICER_COUNT,control=ctree_control(minbucket=30,maxdepth=0)) %>%
  partykit:::.list.rules.party()
} else {
rules0PopCities <- SF_merge_stacked %>%
  #subset(use_year != "Imputed" & totcrime==totcrime_imp) %>%
  subset(use_year == year & str_count(srs_month_adj,"1")==12) %>%
  mutate(TOT_OFFICER_COUNT=MALE_OFFICER_UNIV+FEMALE_OFFICER_UNIV) %>%
  subset(POPULATION_GROUP_DESC_UNIV=="Cities under 2,500" & POPULATION_UNIV==0) %>%
  ctree(formula=totcrime_imp ~ TOT_OFFICER_COUNT,control=ctree_control(minbucket=30,maxdepth=2)) %>%
  partykit:::.list.rules.party()
}
#Identify which values are missing, then replace with "TRUE"
tf <- is.na(rules0PopCities[1:4])|rules0PopCities=="" 
rules0PopCities[tf] <- "TRUE"

#Zero Pop MSA County/State Police
if (as.numeric(year) %in% 2020:2021){
rules0PopMSA <- SF_merge_stacked %>%
  subset(use_year != "Imputed" & totcrime==totcrime_imp) %>%
  #subset(use_year == year & str_count(srs_month_adj,"1")==12) %>%
  mutate(TOT_OFFICER_COUNT=MALE_OFFICER_UNIV+FEMALE_OFFICER_UNIV) %>%
  subset(POPULATION_GROUP_DESC_UNIV %in% c("MSA counties under 10,000","MSA State Police") & POPULATION_UNIV==0) %>%
  ctree(formula=totcrime_imp ~ TOT_OFFICER_COUNT,control=ctree_control(minbucket=30,maxdepth=2)) %>%
  partykit:::.list.rules.party()
} else {
rules0PopMSA <- SF_merge_stacked %>%
  #subset(use_year != "Imputed" & totcrime==totcrime_imp) %>%
  subset(use_year == year & str_count(srs_month_adj,"1")==12) %>%
  mutate(TOT_OFFICER_COUNT=MALE_OFFICER_UNIV+FEMALE_OFFICER_UNIV) %>%
  subset(POPULATION_GROUP_DESC_UNIV %in% c("MSA counties under 10,000","MSA State Police") & POPULATION_UNIV==0) %>%
  ctree(formula=totcrime_imp ~ TOT_OFFICER_COUNT,control=ctree_control(minbucket=30,maxdepth=2)) %>%
  partykit:::.list.rules.party()
}
#Identify which values are missing, then replace with "TRUE"
tf <- is.na(rules0PopMSA[1:4])|rules0PopMSA=="" 
rules0PopMSA[tf] <- "TRUE"

#Zero Pop Non-MSA County/State Police
if (as.numeric(year) %in% 2020:2021){
rules0PopNonMSA <- SF_merge_stacked %>%
  subset(use_year != "Imputed" & totcrime==totcrime_imp) %>%
  #subset(use_year == year & str_count(srs_month_adj,"1")==12) %>%
  mutate(TOT_OFFICER_COUNT=MALE_OFFICER_UNIV+FEMALE_OFFICER_UNIV) %>%
  subset(POPULATION_GROUP_DESC_UNIV %in% c("Non-MSA counties under 10,000","Non-MSA State Police") & POPULATION_UNIV==0) %>%
  ctree(formula=totcrime_imp ~ TOT_OFFICER_COUNT,control=ctree_control(minbucket=30,maxdepth=2)) %>%
  partykit:::.list.rules.party()
} else {
rules0PopNonMSA <- SF_merge_stacked %>%
  #subset(use_year != "Imputed" & totcrime==totcrime_imp) %>%
  subset(use_year == year & str_count(srs_month_adj,"1")==12) %>%
  mutate(TOT_OFFICER_COUNT=MALE_OFFICER_UNIV+FEMALE_OFFICER_UNIV) %>%
  subset(POPULATION_GROUP_DESC_UNIV %in% c("Non-MSA counties under 10,000","Non-MSA State Police") & POPULATION_UNIV==0) %>%
  ctree(formula=totcrime_imp ~ TOT_OFFICER_COUNT,control=ctree_control(minbucket=30,maxdepth=2)) %>%
  partykit:::.list.rules.party()
}

#Identify which values are missing, then replace with "TRUE"
tf <- is.na(rules0PopNonMSA[1:4])|rules0PopNonMSA=="" 
rules0PopNonMSA[tf] <- "TRUE"

if (as.numeric(year) %in% 2020:2021){
flag0LEAs <- SF_merge_stacked %>%
  subset(use_year != "Imputed" & totcrime==totcrime_imp) #%>%
  #subset(use_year == year & str_count(srs_month_adj,"1")==12)
} else {
flag0LEAs <- SF_merge_stacked %>%
  #subset(use_year != "Imputed" & totcrime==totcrime_imp) %>%
  subset(use_year == year & str_count(srs_month_adj,"1")==12)
}  
flag0LEAs <- flag0LEAs %>%
  mutate(TOT_OFFICER_COUNT=MALE_OFFICER_UNIV+FEMALE_OFFICER_UNIV) %>%
  mutate(groupImp=case_when(
    #Cities 250,000 or over
    POPULATION_GROUP_DESC_UNIV=="Cities 1,000,000 or over" ~ 1,
    POPULATION_GROUP_DESC_UNIV=="Cities from 500,000 thru 999,999" ~ 1,
    POPULATION_GROUP_DESC_UNIV=="Cities from 250,000 thru 499,999" ~ 1,
    #Cities from 100,000 - 249,999
    POPULATION_GROUP_DESC_UNIV=="Cities from 100,000 thru 249,999" ~ 4,
    #Cities from 50,000 - 99,999
    POPULATION_GROUP_DESC_UNIV=="Cities from 50,000 thru 99,999" ~ 5,
    #Cities from 25,000 - 49,999
    POPULATION_GROUP_DESC_UNIV=="Cities from 25,000 thru 49,999" ~ 6,
    #Cities from 10,000 - 24,999
    POPULATION_GROUP_DESC_UNIV=="Cities from 10,000 thru 24,999" ~ 7,
    #Cities from 2,500 - 9,999
    POPULATION_GROUP_DESC_UNIV=="Cities from 2,500 thru 9,999" ~ 8,
    #Cities under 2,500
    POPULATION_GROUP_DESC_UNIV=="Cities under 2,500" & POPULATION_UNIV > 0 ~ 8,
    #MSA counties and MSA State Police
    POPULATION_GROUP_DESC_UNIV=="MSA counties 100,000 or over" ~ 9,
    POPULATION_GROUP_DESC_UNIV=="MSA counties from 25,000 thru 99,999" ~ 10,
    POPULATION_GROUP_DESC_UNIV=="MSA counties from 10,000 thru 24,999" ~ 11,
    POPULATION_GROUP_DESC_UNIV=="MSA counties under 10,000" & POPULATION_UNIV > 0 ~ 11,
    POPULATION_GROUP_DESC_UNIV=="MSA State Police" & POPULATION_UNIV > 0 ~ 13,
    #Non-MSA counties and non-MSA State Police
    POPULATION_GROUP_DESC_UNIV=="Non-MSA counties 100,000 or over" ~ 14,
    POPULATION_GROUP_DESC_UNIV=="Non-MSA counties from 25,000 thru 99,999" ~ 14,
    POPULATION_GROUP_DESC_UNIV=="Non-MSA counties from 10,000 thru 24,999" ~ 15,
    POPULATION_GROUP_DESC_UNIV=="Non-MSA counties under 10,000" & POPULATION_UNIV > 0 ~ 16,
    POPULATION_GROUP_DESC_UNIV=="Non-MSA State Police" & POPULATION_UNIV > 0 ~ 17,
	#Zero pop agencies
	POPULATION_GROUP_DESC_UNIV=="Cities under 2,500" & POPULATION_UNIV==0 & 
	  eval(parse(text=rules0PopCities[1])) ~ 18,
	POPULATION_GROUP_DESC_UNIV=="Cities under 2,500" & POPULATION_UNIV==0 & 
	  eval(parse(text=rules0PopCities[2])) ~ 19,
	POPULATION_GROUP_DESC_UNIV=="Cities under 2,500" & POPULATION_UNIV==0 & 
	  eval(parse(text=rules0PopCities[3])) ~ 20,
	POPULATION_GROUP_DESC_UNIV=="Cities under 2,500" & POPULATION_UNIV==0 & 
	  eval(parse(text=rules0PopCities[4])) ~ 21,
	POPULATION_GROUP_DESC_UNIV %in% c("MSA counties under 10,000","MSA State Police") & POPULATION_UNIV==0 & 
	  eval(parse(text=rules0PopMSA[1])) ~ 22,
	POPULATION_GROUP_DESC_UNIV %in% c("MSA counties under 10,000","MSA State Police") & POPULATION_UNIV==0 & 
	  eval(parse(text=rules0PopMSA[2])) ~ 23,
	POPULATION_GROUP_DESC_UNIV %in% c("MSA counties under 10,000","MSA State Police") & POPULATION_UNIV==0 & 
	  eval(parse(text=rules0PopMSA[3])) ~ 24,
	POPULATION_GROUP_DESC_UNIV %in% c("MSA counties under 10,000","MSA State Police") & POPULATION_UNIV==0 & 
	  eval(parse(text=rules0PopMSA[4])) ~ 25,
	POPULATION_GROUP_DESC_UNIV %in% c("Non-MSA counties under 10,000","Non-MSA State Police") & 
	  POPULATION_UNIV==0 & eval(parse(text=rules0PopNonMSA[1])) ~ 26,
	POPULATION_GROUP_DESC_UNIV %in% c("Non-MSA counties under 10,000","Non-MSA State Police") & 
	  POPULATION_UNIV==0 & eval(parse(text=rules0PopNonMSA[2])) ~ 27,
	POPULATION_GROUP_DESC_UNIV %in% c("Non-MSA counties under 10,000","Non-MSA State Police") & 
	  POPULATION_UNIV==0 & eval(parse(text=rules0PopNonMSA[3])) ~ 28,
	POPULATION_GROUP_DESC_UNIV %in% c("Non-MSA counties under 10,000","Non-MSA State Police") & 
	  POPULATION_UNIV==0 & eval(parse(text=rules0PopNonMSA[4])) ~ 29,
    TRUE ~ 0
  ))
#If necessary, collapse group(s)
#if (as.numeric(year)==2001){
#  log_debug("Collapsing group 17 into group 20")
#  flag0LEAs <- flag0LEAs %>%
#    mutate(groupImp=case_when(groupImp==17 ~ 20,
#	                          TRUE ~ groupImp))
#} 
#Now proceed with splitting up by group
flag0LEAs <- flag0LEAs %>%
  split(.,.$groupImp)


#Make the names dynamic
flag0LEAs_group <- names(flag0LEAs) %>% as.numeric()
log_debug("Make the names dynamic")
#print(flag0LEAs_group)

names(flag0LEAs) <- paste0("flag0Group",flag0LEAs_group)

#Count number of rows for FBI group
log_debug("Count number of rows for FBI group")
nFlag0LEAs <- sapply(paste0("flag0Group", flag0LEAs_group), function(x){nrow(flag0LEAs[[x]])})
#print(nFlag0LEAs)


###
#To be imputed
#Note (24Nov2024): Recently switched imputation groups to match weighting groups.
#                  Today, also supporting collapsing (e.g., if <50 donors and 1+ nonrespondent)
flag1LEAs <- SF_merge_stacked%>%
  subset(use_year=="Imputed") %>%
  select(-matches("tot.*_imp$")) %>%
  mutate(groupImp=case_when(
    POPULATION_GROUP_DESC_UNIV=="Cities 1,000,000 or over" ~ 1,
    POPULATION_GROUP_DESC_UNIV=="Cities from 500,000 thru 999,999" ~ 1,
    POPULATION_GROUP_DESC_UNIV=="Cities from 250,000 thru 499,999" ~ 1,
    #Cities from 100,000 - 249,999
    POPULATION_GROUP_DESC_UNIV=="Cities from 100,000 thru 249,999" ~ 4,
    #Cities from 50,000 - 99,999
    POPULATION_GROUP_DESC_UNIV=="Cities from 50,000 thru 99,999" ~ 5,
    #Cities from 25,000 - 49,999
    POPULATION_GROUP_DESC_UNIV=="Cities from 25,000 thru 49,999" ~ 6,
    #Cities from 10,000 - 24,999
    POPULATION_GROUP_DESC_UNIV=="Cities from 10,000 thru 24,999" ~ 7,
    #Cities from 2,500 - 9,999
    POPULATION_GROUP_DESC_UNIV=="Cities from 2,500 thru 9,999" ~ 8,
    #Cities under 2,500
    POPULATION_GROUP_DESC_UNIV=="Cities under 2,500" & POPULATION_UNIV > 0 ~ 8,
    #MSA counties and MSA State Police
    POPULATION_GROUP_DESC_UNIV=="MSA counties 100,000 or over" ~ 9,
    POPULATION_GROUP_DESC_UNIV=="MSA counties from 25,000 thru 99,999" ~ 10,
    POPULATION_GROUP_DESC_UNIV=="MSA counties from 10,000 thru 24,999" ~ 11,
    POPULATION_GROUP_DESC_UNIV=="MSA counties under 10,000" & POPULATION_UNIV > 0 ~ 11,
    POPULATION_GROUP_DESC_UNIV=="MSA State Police" & POPULATION_UNIV > 0 ~ 13,
    #Non-MSA counties and non-MSA State Police
    POPULATION_GROUP_DESC_UNIV=="Non-MSA counties 100,000 or over" ~ 14,
    POPULATION_GROUP_DESC_UNIV=="Non-MSA counties from 25,000 thru 99,999" ~ 14,
    POPULATION_GROUP_DESC_UNIV=="Non-MSA counties from 10,000 thru 24,999" ~ 15,
    POPULATION_GROUP_DESC_UNIV=="Non-MSA counties under 10,000" & POPULATION_UNIV > 0 ~ 16,
    POPULATION_GROUP_DESC_UNIV=="Non-MSA State Police" & POPULATION_UNIV > 0 ~ 17,
	#Zero pop agencies
	POPULATION_GROUP_DESC_UNIV=="Cities under 2,500" & POPULATION_UNIV==0 & 
	  eval(parse(text=rules0PopCities[1])) ~ 18,
	POPULATION_GROUP_DESC_UNIV=="Cities under 2,500" & POPULATION_UNIV==0 & 
	  eval(parse(text=rules0PopCities[2])) ~ 19,
	POPULATION_GROUP_DESC_UNIV=="Cities under 2,500" & POPULATION_UNIV==0 & 
	  eval(parse(text=rules0PopCities[3])) ~ 20,
	POPULATION_GROUP_DESC_UNIV=="Cities under 2,500" & POPULATION_UNIV==0 & 
	  eval(parse(text=rules0PopCities[4])) ~ 21,
	POPULATION_GROUP_DESC_UNIV %in% c("MSA counties under 10,000","MSA State Police") & POPULATION_UNIV==0 & 
	  eval(parse(text=rules0PopMSA[1])) ~ 22,
	POPULATION_GROUP_DESC_UNIV %in% c("MSA counties under 10,000","MSA State Police") & POPULATION_UNIV==0 & 
	  eval(parse(text=rules0PopMSA[2])) ~ 23,
	POPULATION_GROUP_DESC_UNIV %in% c("MSA counties under 10,000","MSA State Police") & POPULATION_UNIV==0 & 
	  eval(parse(text=rules0PopMSA[3])) ~ 24,
	POPULATION_GROUP_DESC_UNIV %in% c("MSA counties under 10,000","MSA State Police") & POPULATION_UNIV==0 & 
	  eval(parse(text=rules0PopMSA[4])) ~ 25,
	POPULATION_GROUP_DESC_UNIV %in% c("Non-MSA counties under 10,000","Non-MSA State Police") & 
	  POPULATION_UNIV==0 & eval(parse(text=rules0PopNonMSA[1])) ~ 26,
	POPULATION_GROUP_DESC_UNIV %in% c("Non-MSA counties under 10,000","Non-MSA State Police") & 
	  POPULATION_UNIV==0 & eval(parse(text=rules0PopNonMSA[2])) ~ 27,
	POPULATION_GROUP_DESC_UNIV %in% c("Non-MSA counties under 10,000","Non-MSA State Police") & 
	  POPULATION_UNIV==0 & eval(parse(text=rules0PopNonMSA[3])) ~ 28,
	POPULATION_GROUP_DESC_UNIV %in% c("Non-MSA counties under 10,000","Non-MSA State Police") & 
	  POPULATION_UNIV==0 & eval(parse(text=rules0PopNonMSA[4])) ~ 29,
    TRUE ~ 0
  )) 
#Collapse if necessary
if (as.numeric(year)==2001){
  #For 2001, let's collapse Non-MSA State Police (>0 pop) with the Non-MSA Zero Pop group 
  #(Thankfully, there's only 1 Non-MSA Zero Pop Group for 2001)
 flag1LEAs <- flag1LEAs %>%
   mutate(groupImp=case_when(groupImp==17 ~ 26,
	                          TRUE ~ groupImp))
}
#Proceed with splitting up by group
flag1LEAs <- flag1LEAs %>%
  split(.,.$groupImp)

if (length(flag1LEAs)>0){
  #Create new flag1LEAs_group variable to identify groups that needs imputation
  log_debug("Create new flag1LEAs_group variable to identify groups that needs imputation")
  flag1LEAs_group <- names(flag1LEAs) %>% as.numeric()
  #print(flag1LEAs_group)
  
  names(flag1LEAs) <- paste0("flag1Group", flag1LEAs_group)
  
  
  #Count number of rows for FBI group
  log_debug("Count number of rows for FBI group")
  nFlag1LEAs <- sapply(paste0("flag1Group", flag1LEAs_group) ,function(x){nrow(flag1LEAs[[x]])})
  #print(nFlag1LEAs)
  #Randomly select 12 month LEA in FBI group - use that LEA's crime totals
  
  
	#06Dec2024: including an imputation check to make sure things went okay
	#13Dec2024: moving this from after imputation done to right before
	#For checking purposes:
	#1) Look for any groups where there are LEAs needing to be imputated but no donors
	prob1 <- flag1LEAs %>% 
	  names() %>% 
	  str_remove("flag1") %>% 
	  subset(!. %in% (
		flag0LEAs %>% 
		names() %>% 
		str_remove("flag0")))
	#2) Look for groups where there's 1+ imputed LEA and <30 donors
	prob2 <- nFlag0LEAs %>% 
	  data.frame(nFlag0=.) %>% 
	  mutate(group=names(nFlag0LEAs) %>%
			   str_extract("\\d+$")) %>% 
	  inner_join(nFlag1LEAs %>% 
				   data.frame(nFlag1=.) %>% 
				   mutate(group=names(nFlag1LEAs) %>%
							str_extract("\\d+$"))) %>%
	  select(group,nFlag0,nFlag1) %>%
	  subset(nFlag1>0 & nFlag0<30)
	#
	if (length(prob1)>0 | nrow(prob2)>0){
	  if (length(prob1)>0){
		str_c("Issue: trying to impute LEAs in group with no donors in ",
			  str_flatten(prob1,", ")) %>%
		  log_debug()
	  }
	  if (nrow(prob2)>0){
		log_debug("Issue: imputing 1+ LEA in group(s) with <30 donors - see list below.")
		print(prob2)
	  }
	  #If problem - this should be useful for deciding what to collapse
	  print(tagList(bind_rows(bind_rows(flag0LEAs),bind_rows(flag1LEAs)) %>%
		  subset(use_year != "Imputed") %>%
		  mutate(zeroPop=POPULATION_UNIV==0) %>%
		  group_by(groupImp) %>%
		  dplyr::summarize(N=n(),
						   n=sum(resp_ind_srs==1),
						   across(totcrime_imp,
								  list("sum"=~sum(.x) %>% round(digits=1),
									   "mean"=~mean(.x) %>% round(digits=1),
									   "sd"=~sd(.x) %>% round(digits=1),
									   "median"=~median(.x) %>% round(digits=1),
									   "mad"=~mad(.x) %>% round(digits=1)),
								  .names="{.fn}"),
						   across(matches("^totcrime.*imp$"),
								  ~mean(ifelse(totcrime_imp>0,
											   100*.x/totcrime_imp,
											   NA_real_),
										na.rm=TRUE) %>%
									round(digits=4),
								  .names="pct_{.col}"),
					#sum_crimes_rep=sum(ifelse(resp_ind_srs==1,1,0)*totcrime_imp),
					#sum_crimes_wgt=sum(NationalWgt*totcrime_imp,na.rm=TRUE)
					) %>%
		  select(-pct_totcrime_imp,-pct_totcrime_manslaughter_imp,
				 -pct_totcrime_assault_imp,-pct_totcrime_simpAssault_imp) %>%
		  data.frame() %>%
		  DT::datatable()))
	  
	  stop("Stopping - See issue(s) above.")
	} else {
	  log_debug("No issues found during imputation.")
	}

  #set.seed(1)
  flag1LEAsImp <- sapply(flag1LEAs_group,function(x){
    #############
    #Randomly select reference agency per 0-2 month agency
    sample.int(nFlag0LEAs[paste0("flag0Group", x)],nFlag1LEAs[paste0("flag1Group", x)], replace=TRUE) %>%
      flag0LEAs[[paste0("flag0Group", x)]][.,c("ORI","totcrime_imp",tot_type_impVars)] %>%
      rename(.,ORI_imp=ORI) %>%
      #############
    #Merge imputed count variables with original record
    select(.,ORI_imp,totcrime_imp,tot_type_impVars) %>%
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
SF_mergeAll <- bind_rows(SF_merge_stacked %>% subset(use_year!="Imputed"),
                         flag1LEAsImp) %>%
  data.frame() %>%
  #Note (09Jan2023): Creating violent/property sums
  mutate(totcrime_violent_imp=select(.,totcrime_murder_imp,totcrime_manslaughter_imp,totcrime_rape_imp,totcrime_rob_imp,totcrime_aggAssault_imp) %>%
           rowSums(.,na.rm=TRUE),
         totcrime_property_imp=select(.,totcrime_burglary_imp,totcrime_larceny_imp,totcrime_vhcTheft_imp) %>% #,totcrime_arson_imp)
           rowSums(.,na.rm=TRUE)) %>%
  #Note (06Dec2024): Moving reporting condition from earlier to here (and using the calibration crime total vs. smoothed imputed crime total
  mutate(resp_ind_srs=case_when(resp_ind_srs==1 & totcrime_imp>=50 ~ in_srs,
                                TRUE ~ resp_ind_srs)) #%>%


SF_all <- SF_mergeAll
SF <- SF_all


# flag 0-population agencies
SF$zeropopLEA <- as.numeric(SF$POPULATION_UNIV == 0)




#######################
# move LEAs in stratum_f 2 that are not in NCSX_stratum 2 to stratum_f 3 or 5 based on type
#Update (24AUG2021): Remove references to NCSX stratum
#Note (27OCT2021): Confirm handling?
SF$stratum_f[SF$stratum_f == 2  & SF$AGENCY_TYPE_NAME_UNIV == "Other State Agency"] <- 3
SF$stratum_f[SF$stratum_f == 2  & SF$AGENCY_TYPE_NAME_UNIV == "State Police"] <- 3
SF$stratum_f[SF$stratum_f == 2  & SF$AGENCY_TYPE_NAME_UNIV == "County"] <- 5
SF$stratum_f[SF$stratum_f == 2  & SF$AGENCY_TYPE_NAME_UNIV == "City"] <- 5

# else, for situations where NCSX_stratum is non-missing, recode stratum_f to NCSX_stratum
#Update (24AUG2021): Remove reference to NCSX stratum
#SF$stratum_f <- ifelse(is.na(SF$NCSX_Stratum) == FALSE, SF$NCSX_Stratum, SF$stratum_f)

# verify coding worked as planned
#table(SF$NCSX_Stratum, SF$stratum_f, useNA = "always")

# reassign stratum 4 (state/muni LEAs with 0 officers in 2011) to stratum 10 (agency type = City) or stratum 3 (all others)
SF$stratum_f[SF$stratum_f == 4 & SF$AGENCY_TYPE_NAME_UNIV == "City"] <- 10
SF$stratum_f[SF$stratum_f == 4 & (SF$AGENCY_TYPE_NAME_UNIV == "Other State Agency" |
                                    SF$AGENCY_TYPE_NAME_UNIV == "State Police" |
                                    SF$AGENCY_TYPE_NAME_UNIV == "University or College")] <- 3


#06Dec2024: forcing KY State Police HQ (KYKSP0000) to 0 for 2009 thru 2012
#09Dec2024: forcing FL Highway Patrol HQ (FLFHP0000) to 0 for certain years (e.g., 1993)
#           same for Delaware (DEDSP0000), Idaho (IDISP0000), Indiana (INISP0000), 
#                    Kentucky (KYKSP0000), Maine (MEMSP0000), Maryland (MDMSP0000), 
#                    Massachusetts (MAMSP0000), Michigan (MI3300100), New Hampshire (NHNSP0000), 
#                    New Jersey (NJNSP0000), Oregon (OROSP1000), Pennsylvania (PAPSP0000),
#                    Rhode Island (RIRSP0000), South Carolina (SCSHP0000), Virginia (VAVSP0000),
#                    and West Virginia (WVWSP0000) equivalents
#09Dec2024: also forcing duplicate set of state police in NY (e.g., NY301SP00) to 0
#           same for GA (e.g., GAGSP0100-GAGSP4800), CT (e.g., CT001SP00-CT008SP00), 
#           and NC (e.g., NC001SP00-NC100SP00) equivalents
#11Dec2024: some signs that OROSP1000 really could report crimes (e.g., reported in 1996 alongside others)
#13Dec2024: moving KYKSP0000 to its own code block (only wipe out for certain years)
#16Dec2024: moving NHNHSP000 to its own code block (only wipe out for certain years)
#           same for OROSP1000 (only wipe out for certain years)
#18Dec2024: NJNSP0000 seemingly swapped out for NJNSP2200 (reports 0 crimes) in 2015 fwiw
#           SCSHP0000 seemingly drops off frame in 2016 fwiw
#           VAVSP0000 reports (0 crimes) in 2016 fwiw
#           FLFHP0000 seemingly drops off frame in 2017 fwiw
#           both GAGSP0000 & 1 other GA LEA report in 2017 (first time I think) [same for 2018] - 
#             consider letting impute for all years? 
#             (19Dec2024) fwiw, that 1 other LEA drops off frame in 2019
#19Dec2024: DEDSP0000 started reporting 2010 - splitting out
#19Dec2024: MEMSP0000 only ME LEA starting in 2017... plus, reported (first time I think)
#           INISP0000 reported 0 in 2018 fwiw (first time I think)
#           WVWSP0000 reported 0 in 2018 fwiw (first time I think), then 3 crimes in 2019, then 0 in 2020
#           MI3300100 seemingly drops off frame in 2019 fwiw  
#           PAPSP0000 reported 0 in 2020 fwiw (first time I think)
#19Dec2024: using different rules for 2020
if (as.numeric(year) %in% 1993:2019){
  SF <- SF %>%
    mutate(across(all_of(crimeVarsBenchImp),
		          ~case_when(use_year == as.numeric(year) ~ .x,
				             ORI %in% c("FLFHP0000","IDISP0000","INISP0000",#"DEDSP0000",
				                        "MEMSP0000","MDMSP0000","MAMSP0000",#"KYKSP0000",
										"MI3300100","NJNSP0000",#"NHNSP0000","OROSP1000",
										"PAPSP0000","RIRSP0000","SCSHP0000","VAVSP0000",
										"WVWSP0000") ~ 0,
							 str_detect(ORI,"^CT.*SP") & ORI != "CTCSP0000" ~ 0,
	                         str_detect(ORI,"^GA.*SP") & ORI != "GAGSP0000" ~ 0,
	                         str_detect(ORI,"^NY.*SP") ~ 0,
							 str_detect(ORI,"^NC.*SP") ~ 0,
		                     TRUE ~ .x)),
		   use_year=case_when(use_year == as.numeric(year) ~ use_year,
		                      ORI %in% c("FLFHP0000","IDISP0000","INISP0000",#"DEDSP0000",
				                         "MEMSP0000","MDMSP0000","MAMSP0000",#"KYKSP0000",
										 "MI3300100","NJNSP0000",#"NHNSP0000","OROSP1000",
										 "PAPSP0000","RIRSP0000","SCSHP0000","VAVSP0000",
										 "WVWSP0000") ~ str_c(use_year," --> Manual"),
							  str_detect(ORI,"^CT.*SP") & ORI != "CTCSP0000" ~ str_c(use_year," --> Manual"),
							  str_detect(ORI,"^GA.*SP") & ORI != "GAGSP0000" ~ str_c(use_year," --> Manual"),
							  str_detect(ORI,"^NY.*SP") ~ str_c(use_year," --> Manual"),
							  str_detect(ORI,"^NC.*SP") ~ str_c(use_year," --> Manual"),
							  TRUE ~ use_year))
} 
#19Dec2024: GA LEAs are all using smoothed SRS in 2020 (none of them reported in 2020) - 
#             set all of them to 0, even if they seemingly reported in 2020...
#             prob do something similar for other years that use smoothed SRS (e.g., 2021)
#           Also, MDMSP0000, MAMSP0000, & NHNSP0000 didn't report in 2020, even tho using 2020 from smoothed SRS...
#             the imputed value is 0 so I think it's fine
#23Dec2024: including 2021-2023 here
#           also, INISP0000 is only Indiana LEA in 2020 & 2021 (vs one of 93 in 2019 and earlier) - 
#             use 2020 totals, which reflect it being the only Indiana LEA
#           also, new set of MD agencies starting in 2020 - 
#             consider tweaking calibration totals (esp if issues during calibration)...?
#           also, MI3300100 is added back to the frame in 2021... set counts to 0?
if (as.numeric(year) %in% c(2020:2023)){

  SF <- SF %>%
    mutate(across(all_of(crimeVarsBenchImp),
		          ~case_when(str_detect(ORI,"^GA.*SP") & use_year %in% 2016:2020 ~ 0,
				             ORI == "INISP0000" & as.numeric(use_year) < 2020 ~ cur_column() %>% 
							   str_replace("_imp$","_imp_2020") %>%
							   sym() %>%
							   eval(),
		                     TRUE ~ .x)),
		   use_year=case_when(str_detect(ORI,"^GA.*SP") & use_year %in% 2016:2020 ~ str_c(use_year," --> Manual"),
							  ORI == "INISP0000" & as.numeric(use_year) < 2020 ~ str_c(use_year," --> 2020"),
							  TRUE ~ use_year))
}



#11Dec2024: supporting additional manual edits (in addition to those mentioned above)
# 			IL0849700 (Illinois State Police) is on my to-watch list (uses 1993 data in 1994)
#           CA Highway Patrol & CA State Police merged in 1995 - need to make sure State Police have 0 counts 1996 onward
if (as.numeric(year) %in% 1996:1999){
  SF <- SF %>%
    mutate(across(all_of(crimeVarsBenchImp),
		          ~case_when(use_year == as.numeric(year) ~ .x,
							 STATE_NAME_UNIV=="California" & AGENCY_TYPE_NAME_UNIV=="State Police" & 
							   str_detect(PUB_AGENCY_NAME_UNIV,"State Police") ~ 0,
		                     TRUE ~ .x)),
		   use_year=case_when(use_year == as.numeric(year) ~ use_year,
							 STATE_NAME_UNIV=="California" & AGENCY_TYPE_NAME_UNIV=="State Police" & 
							   str_detect(PUB_AGENCY_NAME_UNIV,"State Police") ~ str_c(use_year," --> Manual"),
							  TRUE ~ use_year))
}
#11Dec2024: looks like the FL Highway Patrol agencies flipped in 1997 - make sure old ones are set to 0
#           seemingly deleted in 1998 onward so not an issue then
if (as.numeric(year) %in% 1997){
  SF <- SF %>%
    mutate(across(all_of(crimeVarsBenchImp),
		          ~case_when(use_year == as.numeric(year) ~ .x,
							 str_detect(ORI,"^FL.*HP") ~ 0,
		                     TRUE ~ .x)),
		   use_year=case_when(use_year == as.numeric(year) ~ use_year,
							 str_detect(ORI,"^FL.*HP") ~ str_c(use_year," --> Manual"),
							  TRUE ~ use_year))
}
#11Dec2024: Illinois State Police (IL0849700) starts getting imputed in 1998, but individual SP counties don't...
#           also, all Oregon state police besides main one didn't report - just use the main one
#16Dec2024: splitting out Oregon LEA to own code block
if (as.numeric(year) %in% 1998){
  SF <- SF %>%
    mutate(across(all_of(crimeVarsBenchImp),
		          ~case_when(use_year == as.numeric(year) ~ .x,
				             ORI %in% c("IL0849700") ~ 0,
							 #str_detect(ORI,"^OR.*SP") & ORI != "OROSP1000" ~ 0,
		                     TRUE ~ .x)),
		   use_year=case_when(use_year == as.numeric(year) ~ use_year,
		                      ORI %in% c("IL0849700") ~ str_c(use_year," --> Manual"),
							  #str_detect(ORI,"^OR.*SP") & ORI != "OROSP1000" ~ "Manual",
							  TRUE ~ use_year))
} 

#11Dec2024: All Illinois State Police LEAs are now getting imputed in 1999 - zero out the non-HQ/main LEAs
#           And, non-main Oregon state police started reporting again so don't have to worry...
#           Also, looks like set of WV LEAs changed - wiping out old (e.g., WV001SP00-WV055SP00)
#16Dec2024: WV LEAs disappear after 1999 while IL LEAs disappear after 2009, 
#           however, running for both states for 2000-2009 won't actually affect WV results
if (as.numeric(year) %in% 1999:2009){
  SF <- SF %>%
    mutate(across(all_of(crimeVarsBenchImp),
		          ~case_when(use_year == as.numeric(year) ~ .x,
				             STATE_NAME_UNIV=="Illinois" & AGENCY_TYPE_NAME_UNIV == "State Police" & 
							   ORI != "IL0849700" ~ 0,
							 str_detect(ORI,"^WV\\d{3}SP") ~ 0,
		                     TRUE ~ .x)),
		   use_year=case_when(use_year == as.numeric(year) ~ use_year,
				             STATE_NAME_UNIV=="Illinois" & AGENCY_TYPE_NAME_UNIV == "State Police" & 
							   ORI != "IL0849700" ~ str_c(use_year," --> Manual"),
							  str_detect(ORI,"^WV\\d{3}SP") ~ str_c(use_year," --> Manual"),
							  TRUE ~ use_year))

}

#19Dec2024: moved DEDSP0000 to its own code block - started to report in 2010 (0s and near-0s)
#           will set to 0 if was being imputed, otherwise use most recently available year
if (as.numeric(year) %in% c(1993:2019)){
  SF <- SF %>%
    mutate(across(all_of(crimeVarsBenchImp),
		          ~case_when(use_year == as.numeric(year) ~ .x,
				             ORI %in% c("DEDSP0000") & use_year == "Imputed" ~ 0,
		                     TRUE ~ .x)),
		   use_year=case_when(use_year == as.numeric(year) ~ use_year,
		                      ORI %in% c("DEDSP0000") & use_year == "Imputed" ~ str_c(use_year," --> Manual"),
							  TRUE ~ use_year))
}

#13Dec2024: moved KYKSP0000 to its own code block since no reporters (county or main SP) in 2000 -
#           instead for 2000 (& other relevant years), wipe out the county LEAs
#18Dec2024: KYKSP0000 reports (0 crimes) in 2017-2019
if (as.numeric(year) %in% c(1993:1999,2009:2016)){
  SF <- SF %>%
    mutate(across(all_of(crimeVarsBenchImp),
		          ~case_when(use_year == as.numeric(year) ~ .x,
				             ORI %in% c("KYKSP0000") ~ 0,
		                     TRUE ~ .x)),
		   use_year=case_when(use_year == as.numeric(year) ~ use_year,
		                      ORI %in% c("KYKSP0000") ~ str_c(use_year," --> Manual"),
							  TRUE ~ use_year))
} else if (as.numeric(year) %in% 2000:2008){
  SF <- SF %>%
    mutate(across(all_of(crimeVarsBenchImp),
		          ~case_when(use_year == as.numeric(year) ~ .x,
				             str_detect(ORI,"KY.*SP") & ORI != "KYKSP0000" ~ 0,
		                     TRUE ~ .x)),
		   use_year=case_when(use_year == as.numeric(year) ~ use_year,
		                      str_detect(ORI,"KY.*SP") & ORI != "KYKSP0000" ~ str_c(use_year," --> Manual"),
							  TRUE ~ use_year))
}

#16Dec2024: wipe out MOMHP0000 (~1/2 of county LEAs reported in 2006, & other 1/2 are imputed) starting 2006
#18Dec2024: MOMHP0000 drops off of frame in 2016 (& 2017)
#19Dec2024: MOMHP0000 only MO LEA on frame starting in 2018
if (as.numeric(year) %in% 2006:2015){
  SF <- SF %>%
    mutate(across(all_of(crimeVarsBenchImp),
		          ~case_when(use_year == as.numeric(year) ~ .x,
				             ORI %in% c("MOMHP0000") ~ 0,
		                     TRUE ~ .x)),
		   use_year=case_when(use_year == as.numeric(year) ~ use_year,
		                      ORI %in% c("MOMHP0000") ~ str_c(use_year," --> Manual"),
							  TRUE ~ use_year))
}

#16Dec2024: splitting out NHNSP0000 from main block - 
#           we want to use it and wipe out county LEAs 2009 thru 2011 
#           (in 2012-2019, 1+ county LEA reports so revert to wiping out main LEA)
if (as.numeric(year) %in% c(1993:2008,2012:2019)){
  SF <- SF %>%
    mutate(across(all_of(crimeVarsBenchImp),
		          ~case_when(use_year == as.numeric(year) ~ .x,
				             ORI=="NHNSP0000" ~ 0,
		                     TRUE ~ .x)),
		   use_year=case_when(use_year == as.numeric(year) ~ use_year,
	                          ORI=="NHNSP0000" ~ str_c(use_year," --> Manual"),
	                          TRUE ~ use_year))
} else if (as.numeric(year) %in% 2009:2011){
  SF <- SF %>%
    mutate(across(all_of(crimeVarsBenchImp),
		          ~case_when(use_year == as.numeric(year) ~ .x,
				             STATE_NAME_UNIV == "New Hampshire" & AGENCY_TYPE_NAME_UNIV == "State Police" & 
							   ORI != "NHNSP0000" ~ 0,
		                     TRUE ~ .x)),
		   use_year=case_when(use_year == as.numeric(year) ~ use_year,
	                          STATE_NAME_UNIV == "New Hampshire" & AGENCY_TYPE_NAME_UNIV == "State Police" & 
							    ORI != "NHNSP0000" ~ str_c(use_year," --> Manual"),
	                          TRUE ~ use_year))

}

#29Dec2024: tempted to add section for NJNSP2200...
#             only the main LEA reported in 2022, whereas using county LEAs' smoothed SRS...
#             this might be a rare instance where I trust the older county LEAs' over  the newer main LEA counts...
#             leaving alone for now...
# if (as.numeric(year) %in% 2022:2023){
# SF <- SF %>%
    # mutate(across(all_of(crimeVarsBenchImp),
		          # ~case_when(use_year == as.numeric(year) ~ .x,
							 # ORI == "NJNSP2200" ~ 0,
		                     # TRUE ~ .x)),
		   # use_year=case_when(use_year == as.numeric(year) ~ use_year,
							  # ORI == "NJNSP2200" ~ str_c(use_year," --> Manual"),
							  # TRUE ~ use_year))
# }

#16Dec2024: Splitting out OROSP1000 from main block (and the 1998 block)
#16Dec2024: wipe out the Oregon county LEAs for 2009 (& other years)
#16Dec2024: no need to wipe out 2006 bc the county LEAs + main LEA reported
#16Dec2024: county LEAs start reporting again in 2013
#19Dec2024: OROSP1000 seemingly drops off frame in 2018
#29Dec2024: OROSP1000 reports in 1996 fwiw ... 
#             perhaps reverse decision to wipe out to 0 in most years?
if (as.numeric(year) %in% c(1993:1995,1997,1999:2008,2013:2017)){
  SF <- SF %>%
    mutate(across(all_of(crimeVarsBenchImp),
		          ~case_when(use_year == as.numeric(year) ~ .x,
							 ORI == "OROSP1000" ~ 0,
		                     TRUE ~ .x)),
		   use_year=case_when(use_year == as.numeric(year) ~ use_year,
							  ORI == "OROSP1000" ~ str_c(use_year," --> Manual"),
							  TRUE ~ use_year))
} else if (as.numeric(year) %in% c(1998,2009:2012)){
  SF <- SF %>%
    mutate(across(all_of(crimeVarsBenchImp),
		          ~case_when(use_year == as.numeric(year) ~ .x,
							 str_detect(ORI,"^OR.*SP") & ORI != "OROSP1000" ~ 0,
		                     TRUE ~ .x)),
		   use_year=case_when(use_year == as.numeric(year) ~ use_year,
							  str_detect(ORI,"^OR.*SP") & ORI != "OROSP1000" ~ str_c(use_year," --> Manual"),
							  TRUE ~ use_year))
}

#######################
# output data for next program in sequence

fwrite_wrapper(SF, paste0(output_weighting_data_folder,"SF_national_srs.csv"))

log_info("Finished 02_Weights_Data_Setup_National_SRS.R\n\n")
