###-------------------------------------------------------------------------------
### Define libraries
###-------------------------------------------------------------------------------

library(tidyverse)
library(openxlsx)
library(haven)
library(mice)
library(miceadds)
library(VIM)
library(naniar)
library(visdat)
library(ggplot2)
library(StatMatch)
library(writexl)
library(sas7bdat)
library(sjmisc)
library(gtools)
library(zoo)
library(reshape2)
library(lazyeval)
library(data.table)
library(DT)		   

set.seed(5242023)

#Create a dataset for the state factors
CONST_STATE_FACTOR <- c(
"1=AK",
"2=AL",
"3=AR",
"4=AS",
"5=AZ",
"6=CA",
"7=CO",
"8=CT",
"9=CZ",
"10=DC",
"11=DE",
"12=FL",
"13=GA",
"14=GM",
"15=HI",
"16=IA",
"17=ID",
"18=IL",
"19=IN",
"20=KS",
"21=KY",
"22=LA",
"23=MA",
"24=MD",
"25=ME",
"26=MI",
"27=MN",
"28=MO",
"29=MS",
"30=MT",
"31=NB",
"32=NC",
"33=ND",
"34=NH",
"35=NJ",
"36=NM",
"37=NV",
"38=NY",
"39=OH",
"40=OK",
"41=OR",
"42=PA",
"43=PR",
"44=RI",
"45=SC",
"46=SD",
"47=TN",
"48=TX",
"49=UT",
"50=VI",
"51=VA",
"52=VT",
"53=WA",
"54=WI",
"55=WV",
"56=WY",
"57=MP",
"98=FS") %>%
  as_tibble() %>%
  rename(
    state_factor=value
  ) %>%
  mutate(
    state_num = str_match(string=state_factor, pattern="(\\d+)=")[,2] %>% as.character()
  )

#See the dataset
CONST_STATE_FACTOR %>% datatable()

###################Add on additional objects for NIBRS eligibility##############
# Determine eligibility
CONST_STATES = c(
  "AL",     #Alabama
  "AK",     #Alaska
  "AZ",     #Arizona
  "AR",     #Arkansas
  "CA",     #California
  "CO",     #Colorado
  "CT",     #Connecticut
  "DE",     #Delaware
  "DC",     #District of Columbia
  "FL",     #Florida
  "GA",     #Georgia
  "HI",     #Hawaii
  "ID",     #Idaho
  "IL",     #Illinois
  "IN",     #Indiana
  "IA",     #Iowa
  "KS",     #Kansas
  "KY",     #Kentucky
  "LA",     #Louisiana
  "ME",     #Maine
  "MD",     #Maryland
  "MA",     #Massachusetts
  "MI",     #Michigan
  "MN",     #Minnesota
  "MS",     #Mississippi
  "MO",     #Missouri
  "MT",     #Montana
  "NB",     #Nebraska
  "NV",     #Nevada
  "NH",     #New Hampshire
  "NJ",     #New Jersey
  "NM",     #New Mexico
  "NY",     #New York
  "NC",     #North Carolina
  "ND",     #North Dakota
  "OH",     #Ohio
  "OK",     #Oklahoma
  "OR",     #Oregon
  "PA",     #Pennsylvania
  "RI",     #Rhode Island
  "SC",     #South Carolina
  "SD",     #South Dakota
  "TN",     #Tennessee
  "TX",     #Texas
  "UT",     #Utah
  "VT",     #Vermont
  "VA",     #Virginia
  "WA",     #Washington
  "WV",     #West Virginia
  "WI",     #Wisconsin
  "WY")     #Wyoming

############################Declare the SRS variables##########################

CONST_SRS_MURDER <- c(
  "v70", #JAN: ACT NUM MURDER
  "v188", #FEB: ACT NUM MURDER
  "v306", #MAR: ACT NUM MURDER
  "v424", #APR: ACT NUM MURDER
  "v542", #MAY: ACT NUM MURDER
  "v660", #JUN: ACT NUM MURDER
  "v778", #JUL: ACT NUM MURDER
  "v896", #AUG: ACT NUM MURDER
  "v1014", #SEP: ACT NUM MURDER
  "v1132", #OCT: ACT NUM MURDER
  "v1250", #NOV: ACT NUM MURDER
  "v1368" #DEC: ACT NUM MURDER
)


CONST_SRS_MANSLGHTR <- c(
  "v71", #JAN: ACT NUM MANSLGHTR
  "v189", #FEB: ACT NUM MANSLGHTR
  "v307", #MAR: ACT NUM MANSLGHTR
  "v425", #APR: ACT NUM MANSLGHTR
  "v543", #MAY: ACT NUM MANSLGHTR
  "v661", #JUN: ACT NUM MANSLGHTR
  "v779", #JUL: ACT NUM MANSLGHTR
  "v897", #AUG: ACT NUM MANSLGHTR
  "v1015", #SEP: ACT NUM MANSLGHTR
  "v1133", #OCT: ACT NUM MANSLGHTR
  "v1251", #NOV: ACT NUM MANSLGHTR
  "v1369" #DEC: ACT NUM MANSLGHTR
)


CONST_SRS_TOTAL_RAPE <- c(
  "v72", #JAN: ACT NUM RAPE TOTL
  "v190", #FEB: ACT NUM RAPE TOTL
  "v308", #MAR: ACT NUM RAPE TOTL
  "v426", #APR: ACT NUM RAPE TOTL
  "v544", #MAY: ACT NUM RAPE TOTL
  "v662", #JUN: ACT NUM RAPE TOTL
  "v780", #JUL: ACT NUM RAPE TOTL
  "v898", #AUG: ACT NUM RAPE TOTL
  "v1016", #SEP: ACT NUM RAPE TOTL
  "v1134", #OCT: ACT NUM RAPE TOTL
  "v1252", #NOV: ACT NUM RAPE TOTL
  "v1370" #DEC: ACT NUM RAPE TOTL
)


CONST_SRS_FORC_RAPE <- c(
  "v73", #JAN: ACT NUM FORC RAPE
  "v191", #FEB: ACT NUM FORC RAPE
  "v309", #MAR: ACT NUM FORC RAPE
  "v427", #APR: ACT NUM FORC RAPE
  "v545", #MAY: ACT NUM FORC RAPE
  "v663", #JUN: ACT NUM FORC RAPE
  "v781", #JUL: ACT NUM FORC RAPE
  "v899", #AUG: ACT NUM FORC RAPE
  "v1017", #SEP: ACT NUM FORC RAPE
  "v1135", #OCT: ACT NUM FORC RAPE
  "v1253", #NOV: ACT NUM FORC RAPE
  "v1371" #DEC: ACT NUM FORC RAPE
)


CONST_SRS_ATTEMPTED_RAPE <- c(
  "v74", #JAN: ACT NUM ATMPTD RAPE
  "v192", #FEB: ACT NUM ATMPTD RAPE
  "v310", #MAR: ACT NUM ATMPTD RAPE
  "v428", #APR: ACT NUM ATMPTD RAPE
  "v546", #MAY: ACT NUM ATMPTD RAPE
  "v664", #JUN: ACT NUM ATMPTD RAPE
  "v782", #JUL: ACT NUM ATMPTD RAPE
  "v900", #AUG: ACT NUM ATMPTD RAPE
  "v1018", #SEP: ACT NUM ATMPTD RAP
  "v1136", #OCT: ACT NUM ATMPTD RAP
  "v1254", #NOV: ACT NUM ATMPTD RAP
  "v1372" #DEC: ACT NUM ATMPTD RAP
)

CONST_SRS_TOTAL_ROBBERY <- c(
  "v75", #JAN: ACT NUM ROBBRY TOTL
  "v193", #FEB: ACT NUM ROBBRY TOTL
  "v311", #MAR: ACT NUM ROBBRY TOTL
  "v429", #APR: ACT NUM ROBBRY TOTL
  "v547", #MAY: ACT NUM ROBBRY TOTL
  "v665", #JUN: ACT NUM ROBBRY TOTL
  "v783", #JUL: ACT NUM ROBBRY TOTL
  "v901", #AUG: ACT NUM ROBBRY TOTL
  "v1019", #SEP: ACT NUM ROBBRY TOT
  "v1137", #OCT: ACT NUM ROBBRY TOT
  "v1255", #NOV: ACT NUM ROBBRY TOT
  "v1373" #DEC: ACT NUM ROBBRY TOT
)

CONST_SRS_GUN_ROBBERY <- c(
  "v76", #JAN: ACT NUM GUN ROBBERY
  "v194", #FEB: ACT NUM GUN ROBBERY
  "v312", #MAR: ACT NUM GUN ROBBERY
  "v430", #APR: ACT NUM GUN ROBBERY
  "v548", #MAY: ACT NUM GUN ROBBERY
  "v666", #JUN: ACT NUM GUN ROBBERY
  "v784", #JUL: ACT NUM GUN ROBBERY
  "v902", #AUG: ACT NUM GUN ROBBERY
  "v1020", #SEP: ACT NUM GUN ROBBER
  "v1138", #OCT: ACT NUM GUN ROBBER
  "v1256", #NOV: ACT NUM GUN ROBBER
  "v1374" #DEC: ACT NUM GUN ROBBER
)

CONST_SRS_KNIFE_ROBBERY <- c(
  "v77", #JAN: ACT NUM KNIFE ROBRY
  "v195", #FEB: ACT NUM KNIFE ROBRY
  "v313", #MAR: ACT NUM KNIFE ROBRY
  "v431", #APR: ACT NUM KNIFE ROBRY
  "v549", #MAY: ACT NUM KNIFE ROBRY
  "v667", #JUN: ACT NUM KNIFE ROBRY
  "v785", #JUL: ACT NUM KNIFE ROBRY
  "v903", #AUG: ACT NUM KNIFE ROBRY
  "v1021", #SEP: ACT NUM KNIFE ROBR
  "v1139", #OCT: ACT NUM KNIFE ROBR
  "v1257", #NOV: ACT NUM KNIFE ROBR
  "v1375" #DEC: ACT NUM KNIFE ROBR
)

CONST_SRS_OTHER_WPN_ROBBERY <- c(
  "v78", #JAN: ACT NUM OTH WPN ROB
  "v196", #FEB: ACT NUM OTH WPN ROB
  "v314", #MAR: ACT NUM OTH WPN ROB
  "v432", #APR: ACT NUM OTH WPN ROB
  "v550", #MAY: ACT NUM OTH WPN ROB
  "v668", #JUN: ACT NUM OTH WPN ROB
  "v786", #JUL: ACT NUM OTH WPN ROB
  "v904", #AUG: ACT NUM OTH WPN ROB
  "v1022", #SEP: ACT NUM OTH WPN RO
  "v1140", #OCT: ACT NUM OTH WPN RO
  "v1258", #NOV: ACT NUM OTH WPN RO
  "v1376" #DEC: ACT NUM OTH WPN RO
)

CONST_SRS_STRONG_ARM_ROBBERY <- c(
  "v79", #JAN: ACT NUM STR ARM ROB
  "v197", #FEB: ACT NUM STR ARM ROB
  "v315", #MAR: ACT NUM STR ARM ROB
  "v433", #APR: ACT NUM STR ARM ROB
  "v551", #MAY: ACT NUM STR ARM ROB
  "v669", #JUN: ACT NUM STR ARM ROB
  "v787", #JUL: ACT NUM STR ARM ROB
  "v905", #AUG: ACT NUM STR ARM ROB
  "v1023", #SEP: ACT NUM STR ARM RO
  "v1141", #OCT: ACT NUM STR ARM RO
  "v1259", #NOV: ACT NUM STR ARM RO
  "v1377" #DEC: ACT NUM STR ARM RO
)

CONST_SRS_TOTAL_ASSAULT <- c(
  "v80", #JAN: ACT NUM ASSLT TOTAL
  "v198", #FEB: ACT NUM ASSLT TOTAL
  "v316", #MAR: ACT NUM ASSLT TOTAL
  "v434", #APR: ACT NUM ASSLT TOTAL
  "v552", #MAY: ACT NUM ASSLT TOTAL
  "v670", #JUN: ACT NUM ASSLT TOTAL
  "v788", #JUL: ACT NUM ASSLT TOTAL
  "v906", #AUG: ACT NUM ASSLT TOTAL
  "v1024", #SEP: ACT NUM ASSLT TOTA
  "v1142", #OCT: ACT NUM ASSLT TOTA
  "v1260", #NOV: ACT NUM ASSLT TOTA
  "v1378" #DEC: ACT NUM ASSLT TOTA
)

CONST_SRS_GUN_ASSAULT <- c(
  "v81", #JAN: ACT NUM GUN ASSAULT
  "v199", #FEB: ACT NUM GUN ASSAULT
  "v317", #MAR: ACT NUM GUN ASSAULT
  "v435", #APR: ACT NUM GUN ASSAULT
  "v553", #MAY: ACT NUM GUN ASSAULT
  "v671", #JUN: ACT NUM GUN ASSAULT
  "v789", #JUL: ACT NUM GUN ASSAULT
  "v907", #AUG: ACT NUM GUN ASSAULT
  "v1025", #SEP: ACT NUM GUN ASSAUL
  "v1143", #OCT: ACT NUM GUN ASSAUL
  "v1261", #NOV: ACT NUM GUN ASSAUL
  "v1379" #DEC: ACT NUM GUN ASSAUL
)


CONST_SRS_KNIFE_ASSAULT <- c(
  "v82", #JAN: ACT NUM KNIFE ASSLT
  "v200", #FEB: ACT NUM KNIFE ASSLT
  "v318", #MAR: ACT NUM KNIFE ASSLT
  "v436", #APR: ACT NUM KNIFE ASSLT
  "v554", #MAY: ACT NUM KNIFE ASSLT
  "v672", #JUN: ACT NUM KNIFE ASSLT
  "v790", #JUL: ACT NUM KNIFE ASSLT
  "v908", #AUG: ACT NUM KNIFE ASSLT
  "v1026", #SEP: ACT NUM KNIFE ASSL
  "v1144", #OCT: ACT NUM KNIFE ASSL
  "v1262", #NOV: ACT NUM KNIFE ASSL
  "v1380" #DEC: ACT NUM KNIFE ASSL
)

CONST_SRS_OTHER_WPN_ASSAULT <- c(
  "v83", #JAN: ACT # OTH WPN ASSLT
  "v201", #FEB: ACT # OTH WPN ASSLT
  "v319", #MAR: ACT # OTH WPN ASSLT
  "v437", #APR: ACT # OTH WPN ASSLT
  "v555", #MAY: ACT # OTH WPN ASSLT
  "v673", #JUN: ACT # OTH WPN ASSLT
  "v791", #JUL: ACT # OTH WPN ASSLT
  "v909", #AUG: ACT # OTH WPN ASSLT
  "v1027", #SEP: ACT # OTH WPN ASSL
  "v1145", #OCT: ACT # OTH WPN ASSL
  "v1263", #NOV: ACT # OTH WPN ASSL
  "v1381" #DEC: ACT # OTH WPN ASSL
)

CONST_SRS_HAND_FEET_ASSAULT <- c(
  "v84", #JAN: ACT # HND/FEET ASLT
  "v202", #FEB: ACT # HND/FEET ASLT
  "v320", #MAR: ACT # HND/FEET ASLT
  "v438", #APR: ACT # HND/FEET ASLT
  "v556", #MAY: ACT # HND/FEET ASLT
  "v674", #JUN: ACT # HND/FEET ASLT
  "v792", #JUL: ACT # HND/FEET ASLT
  "v910", #AUG: ACT # HND/FEET ASLT
  "v1028", #SEP: ACT # HND/FEET ASL
  "v1146", #OCT: ACT # HND/FEET ASL
  "v1264", #NOV: ACT # HND/FEET ASL
  "v1382" #DEC: ACT # HND/FEET ASL
)


CONST_SRS_SIMPLE_ASSAULT <- c(
  "v85", #JAN: ACT # SIMPLE ASSLT
  "v203", #FEB: ACT # SIMPLE ASSLT
  "v321", #MAR: ACT # SIMPLE ASSLT
  "v439", #APR: ACT # SIMPLE ASSLT
  "v557", #MAY: ACT # SIMPLE ASSLT
  "v675", #JUN: ACT # SIMPLE ASSLT
  "v793", #JUL: ACT # SIMPLE ASSLT
  "v911", #AUG: ACT # SIMPLE ASSLT
  "v1029", #SEP: ACT # SIMPLE ASSLT
  "v1147", #OCT: ACT # SIMPLE ASSLT
  "v1265", #NOV: ACT # SIMPLE ASSLT
  "v1383" #DEC: ACT # SIMPLE ASSLT
)

CONST_SRS_TOTAL_BURGLARY <- c(
  "v86", #JAN: ACT # BURGLARY TOTL
  "v204", #FEB: ACT # BURGLARY TOTL
  "v322", #MAR: ACT # BURGLARY TOTL
  "v440", #APR: ACT # BURGLARY TOTL
  "v558", #MAY: ACT # BURGLARY TOTL
  "v676", #JUN: ACT # BURGLARY TOTL
  "v794", #JUL: ACT # BURGLARY TOTL
  "v912", #AUG: ACT # BURGLARY TOTL
  "v1030", #SEP: ACT # BURGLARY TOT
  "v1148", #OCT: ACT # BURGLARY TOT
  "v1266", #NOV: ACT # BURGLARY TOT
  "v1384" #DEC: ACT # BURGLARY TOT
)

CONST_SRS_FORC_ENTRY <- c(
  "v87", #JAN: ACT # FORCE ENTRY
  "v205", #FEB: ACT # FORCE ENTRY
  "v323", #MAR: ACT # FORCE ENTRY
  "v441", #APR: ACT # FORCE ENTRY
  "v559", #MAY: ACT # FORCE ENTRY
  "v677", #JUN: ACT # FORCE ENTRY
  "v795", #JUL: ACT # FORCE ENTRY
  "v913", #AUG: ACT # FORCE ENTRY
  "v1031", #SEP: ACT # FORCE ENTRY
  "v1149", #OCT: ACT # FORCE ENTRY
  "v1267", #NOV: ACT # FORCE ENTRY
  "v1385" #DEC: ACT # FORCE ENTRY
)


CONST_SRS_NO_FORC_ENTRY <- c(
  "v88", #JAN: ACT # ENTRY-NO FORC
  "v206", #FEB: ACT # ENTRY-NO FORC
  "v324", #MAR: ACT # ENTRY-NO FORC
  "v442", #APR: ACT # ENTRY-NO FORC
  "v560", #MAY: ACT # ENTRY-NO FORC
  "v678", #JUN: ACT # ENTRY-NO FORC
  "v796", #JUL: ACT # ENTRY-NO FORC
  "v914", #AUG: ACT # ENTRY-NO FORC
  "v1032", #SEP: ACT # ENTRY-NO FOR
  "v1150", #OCT: ACT # ENTRY-NO FOR
  "v1268", #NOV: ACT # ENTRY-NO FOR
  "v1386" #DEC: ACT # ENTRY-NO FOR
)

CONST_SRS_ATTEMPTED_BURGLARY <- c(
  "v89", #JAN: ACT # ATT BURGLARY
  "v207", #FEB: ACT # ATT BURGLARY
  "v325", #MAR: ACT # ATT BURGLARY
  "v443", #APR: ACT # ATT BURGLARY
  "v561", #MAY: ACT # ATT BURGLARY
  "v679", #JUN: ACT # ATT BURGLARY
  "v797", #JUL: ACT # ATT BURGLARY
  "v915", #AUG: ACT # ATT BURGLARY
  "v1033", #SEP: ACT # ATT BURGLARY
  "v1151", #OCT: ACT # ATT BURGLARY
  "v1269", #NOV: ACT # ATT BURGLARY
  "v1387" #DEC: ACT # ATT BURGLARY
)

CONST_SRS_TOTAL_LARCENY <- c(
  "v90", #JAN: ACT # LARCENY TOTAL
  "v208", #FEB: ACT # LARCENY TOTAL
  "v326", #MAR: ACT # LARCENY TOTAL
  "v444", #APR: ACT # LARCENY TOTAL
  "v562", #MAY: ACT # LARCENY TOTAL
  "v680", #JUN: ACT # LARCENY TOTAL
  "v798", #JUL: ACT # LARCENY TOTAL
  "v916", #AUG: ACT # LARCENY TOTAL
  "v1034", #SEP: ACT # LARCENY TOTA
  "v1152", #OCT: ACT # LARCENY TOTA
  "v1270", #NOV: ACT # LARCENY TOTA
  "v1388" #DEC: ACT # LARCENY TOTA
)


CONST_SRS_TOTAL_VEH_THEFT <- c(
  "v91", #JAN: ACT # VHC THEFT TOT
  "v209", #FEB: ACT # VHC THEFT TOT
  "v327", #MAR: ACT # VHC THEFT TOT
  "v445", #APR: ACT # VHC THEFT TOT
  "v563", #MAY: ACT # VHC THEFT TOT
  "v681", #JUN: ACT # VHC THEFT TOT
  "v799", #JUL: ACT # VHC THEFT TOT
  "v917", #AUG: ACT # VHC THEFT TOT
  "v1035", #SEP: ACT # VHC THEFT TO
  "v1153", #OCT: ACT # VHC THEFT TO
  "v1271", #NOV: ACT # VHC THEFT TO
  "v1389" #DEC: ACT # VHC THEFT TO
)

CONST_SRS_AUTO_THEFT <- c(
  "v92", #JAN: ACT # AUTO THEFT
  "v210", #FEB: ACT # AUTO THEFT
  "v328", #MAR: ACT # AUTO THEFT
  "v446", #APR: ACT # AUTO THEFT
  "v564", #MAY: ACT # AUTO THEFT
  "v682", #JUN: ACT # AUTO THEFT
  "v800", #JUL: ACT # AUTO THEFT
  "v918", #AUG: ACT # AUTO THEFT
  "v1036", #SEP: ACT # AUTO THEFT
  "v1154", #OCT: ACT # AUTO THEFT
  "v1272", #NOV: ACT # AUTO THEFT
  "v1390" #DEC: ACT # AUTO THEFT
)

CONST_SRS_TRUCK_BUS_THEFT <- c(
  "v93", #JAN: ACT # TRCK/BUS THFT
  "v211", #FEB: ACT # TRCK/BUS THFT
  "v329", #MAR: ACT # TRCK/BUS THFT
  "v447", #APR: ACT # TRCK/BUS THFT
  "v565", #MAY: ACT # TRCK/BUS THFT
  "v683", #JUN: ACT # TRCK/BUS THFT
  "v801", #JUL: ACT # TRCK/BUS THFT
  "v919", #AUG: ACT # TRCK/BUS THFT
  "v1037", #SEP: ACT # TRCK/BUS THF
  "v1155", #OCT: ACT # TRCK/BUS THF
  "v1273", #NOV: ACT # TRCK/BUS THF
  "v1391" #DEC: ACT # TRCK/BUS THF
)


CONST_SRS_OTH_VEH_THEFT <- c(
  "v94", #JAN: ACT # OTH VHC THEFT
  "v212", #FEB: ACT # OTH VHC THEFT
  "v330", #MAR: ACT # OTH VHC THEFT
  "v448", #APR: ACT # OTH VHC THEFT
  "v566", #MAY: ACT # OTH VHC THEFT
  "v684", #JUN: ACT # OTH VHC THEFT
  "v802", #JUL: ACT # OTH VHC THEFT
  "v920", #AUG: ACT # OTH VHC THEFT
  "v1038", #SEP: ACT # OTH VHC THEF
  "v1156", #OCT: ACT # OTH VHC THEF
  "v1274", #NOV: ACT # OTH VHC THEF
  "v1392" #DEC: ACT # OTH VHC THEF
)

CONST_SRS_ALL_FIELDS <- c(
  "v95", #JAN: ACT # ALL FIELDS
  "v213", #FEB: ACT # ALL FIELDS
  "v331", #MAR: ACT # ALL FIELDS
  "v449", #APR: ACT # ALL FIELDS
  "v567", #MAY: ACT # ALL FIELDS
  "v685", #JUN: ACT # ALL FIELDS
  "v803", #JUL: ACT # ALL FIELDS
  "v921", #AUG: ACT # ALL FIELDS
  "v1039", #SEP: ACT # ALL FIELDS
  "v1157", #OCT: ACT # ALL FIELDS
  "v1275", #NOV: ACT # ALL FIELDS
  "v1393" #DEC: ACT # ALL FIELDS
)

###############################################################################



###-------------------------------------------------------------------------------
### Data preparation: Read in the imputed SRS file
###-------------------------------------------------------------------------------

#Okay to use read_csv as is since it is just a character ori variable and all numeric v variables
raw_imputed_srs <- read_csv(paste0(filepathin, "SRS_NIBRS_BLOCK_IMP_ONLY_MAX_LR.csv"))
log_dim(raw_imputed_srs)

#####################Need to bypass this portion and identify which agencies are eligible##########

###-------------------------------------------------------------------------------
### Data preparation: Read in the NIBRS sampling frame and use the response 
###   indicator JD creates
###-------------------------------------------------------------------------------
# nibrs_sf_raw <- fread(paste0(nibrs_weights_in, "/SF.csv")) 
# 
# nibrs_sf <- nibrs_sf_raw %>%
#   filter(resp_ind_m3 == 1) 
# 
# #Check the dim
# log_dim(nibrs_sf_raw)
# log_dim(nibrs_sf)
# 
# #Do the merge by ori
# tbd_good_1 <- nibrs_sf %>%
#   inner_join(raw_imputed_srs, by="ORI")
# 
# tbd_bad_1 <- nibrs_sf %>%
#   anti_join(raw_imputed_srs, by="ORI")
# 
# #Do the remaining merge by LEGACY_ORI
# 
# tbd_good_2 <- tbd_bad_1 %>%
#   inner_join(raw_imputed_srs, by=c("LEGACY_ORI" = "ORI"))
# 
# tbd_bad_2 <- tbd_bad_1 %>%
#   anti_join(raw_imputed_srs, by=c("LEGACY_ORI" = "ORI"))
# 
# #Create the dataset that have the partial reporters converted to 
# 
# tbd_imputed_srs <- bind_rows(tbd_good_1, tbd_good_2, tbd_bad_2)
# 
# #Check the dimension
# log_dim(tbd_imputed_srs)
# log_dim(nibrs_sf)
# 
# log_dim(tbd_good_1)
# log_dim(tbd_bad_1)
# log_dim(tbd_good_2)
# log_dim(tbd_bad_2)

#Read in the current universe file
raw_universe <- read_csv(paste0(raw_srs_file_path, "orig_ref_agency_", year, ".csv"), guess_max=10000 )

raw_universe2 <- raw_universe %>%
  mutate(
    in_univ_elig_state = fcase(
      trim_upper(STATE_ABBR) %in% CONST_STATES, 1,
      default = 0
    ), 
    
    der_in_univ_elig =  fcase(
      trim_upper(AGENCY_STATUS) == "A" &
        trim_upper(COVERED_FLAG) == "N" &
        trim_upper(DORMANT_FLAG) == "N" &
        trim_upper(AGENCY_TYPE_NAME) != "FEDERAL" &
        in_univ_elig_state == 1,  1,
      default = 0)
    
  )

#Check the recodes
raw_universe2 %>% checkfunction(in_univ_elig_state, STATE_ABBR)
raw_universe2 %>% checkfunction(der_in_univ_elig, AGENCY_STATUS, COVERED_FLAG, DORMANT_FLAG, AGENCY_TYPE_NAME, in_univ_elig_state)

# #Do the merge by ori
tbd_good_1 <- raw_imputed_srs %>%
  inner_join(raw_universe2, by="ORI")

tbd_bad_1 <- raw_imputed_srs %>%
  anti_join(raw_universe2, by="ORI")

#Do the remaining merge by LEGACY_ORI

tbd_good_2 <- tbd_bad_1 %>%
  inner_join(raw_universe2, by=c("ORI" = "LEGACY_ORI"))

tbd_bad_2 <- tbd_bad_1 %>%
  anti_join(raw_universe2, by=c("ORI" = "LEGACY_ORI"))



#Create the dataset that have the partial reporters converted to

tbd_imputed_srs0 <- bind_rows(tbd_good_1, tbd_good_2, tbd_bad_2)

#Check the dimension
log_dim(tbd_imputed_srs0)
log_dim(raw_imputed_srs)

log_dim(tbd_good_1)
log_dim(tbd_bad_1)
log_dim(tbd_good_2)
log_dim(tbd_bad_2)

#Need to create the tbd_imputed_srs dataset by subsetting to the eligible NIBRS agencies
tbd_imputed_srs <- tbd_imputed_srs0 %>%
  filter(der_in_univ_elig == 1)

#See the eligible NIBRS agencies
log_dim(tbd_imputed_srs)
log_dim(tbd_imputed_srs0)

#Next need to create the final dataset and keep certain variables
final_imputed_srs <- tbd_imputed_srs %>%
  select(ORI, matches("v\\d+")) %>%
  #Note need to zero filled the NA v variables, the reasoning is that these agencies did not report
  #any incidents to NIBRS, so they are our 0 reporters
  mutate(
    across(
      .cols = matches("v\\d+"),
      .fns = ~ {
        replace_na(.x, value = 0) 
        },
      .names="{.col}")
  ) %>%
  #Next need to create the MM flags and make them all 1 to be a full year reporters since 
  #any ORI given a weight greater than or equal to 1 is at least a 3 month reporters
  mutate(
    jan_mm_flag = 1,
    feb_mm_flag = 1,
    mar_mm_flag = 1,
    apr_mm_flag = 1,
    may_mm_flag = 1,
    jun_mm_flag = 1,
    jul_mm_flag = 1,
    aug_mm_flag = 1,
    sep_mm_flag = 1,
    oct_mm_flag = 1,
    nov_mm_flag = 1,
    dec_mm_flag = 1
) 

#Delete all the raw and tbd datasets
rm(list=c(ls(pattern="tbd"), setdiff(ls(pattern="raw"), "raw_srs_file_path")))

#Create a list or variables to be drop from the srs
CONST_DROP_VARS <- colnames(final_imputed_srs) %>%
  as_tibble() %>%
  filter(value != "ORI") %>%
  select(value) %>%
  pull()

#See the list of variables
print(CONST_DROP_VARS)

###-------------------------------------------------------------------------------
### Data preparation: recoding and creating variables
###-------------------------------------------------------------------------------

# Read file created by Philip

tbd_srs0 <- read_csv(file.path(raw_srs_file_path,paste0("UCR_SRS_",year,"_clean_reta_mm_selected_vars.csv")))
log_dim(tbd_srs0)

#Using tbd_srs_returna, need to create variables that do not exist
tbd_col_names <- colnames(tbd_srs0) %>%
  as_tibble()

#Get all the SRS v variables
tbd_all_var_list <- ls(pattern="CONST_SRS_")

#Need to loop thru and get list of variables
tbd_all_v_vars <- map_dfr(tbd_all_var_list, ~{
  
  #Read in the current data
  tbd_1 <- get(.x) %>%
    as_tibble()
  
  #Return the data
  return(tbd_1)
  
  
}) %>%
  select(value) %>%
  pull()

#Check the dimension
length(tbd_all_v_vars)


#Get the variables to be created
tbd_create_vars <- tbd_all_v_vars %>%
  as_tibble() %>%
  anti_join(tbd_col_names, by="value") %>%
  select(value) %>%
  pull()

#Check the dimension
length(tbd_create_vars)
length(tbd_all_v_vars)
nrow(tbd_col_names)

#Create the additional variables
tbd_srs1 <- tbd_srs0

if(length(tbd_create_vars) > 0){
  
  for(tbd_var in tbd_create_vars){
    
    log_debug(paste0("Creating variable ", tbd_var, " in SRS Return A data"))
    
    #Create missing variables and assigning counts of 0
    tbd_srs1 <- tbd_srs1 %>%
      mutate(
        !!(tbd_var %>% rlang:::parse_expr()) := 0
      )
  }
  
}

###################################Declare the new legacy rape ################

CONST_SRS_TOTAL_LEGACY_RAPE <- c(
  "v96",  #JAN: ACT NUM RAPE TOTL
  "v214",  #FEB: ACT NUM RAPE TOTL
  "v332",  #MAR: ACT NUM RAPE TOTL
  "v450",  #APR: ACT NUM RAPE TOTL
  "v568",  #MAY: ACT NUM RAPE TOTL
  "v686",  #JUN: ACT NUM RAPE TOTL
  "v804",  #JUL: ACT NUM RAPE TOTL
  "v922",  #AUG: ACT NUM RAPE TOTL
  "v1040",  #SEP: ACT NUM RAPE TOTL
  "v1158",  #OCT: ACT NUM RAPE TOTL
  "v1276",  #NOV: ACT NUM RAPE TOTL
  "v1394" #DEC: ACT NUM RAPE TOTL
)

CONST_SRS_FORC_LEGACY_RAPE <- c(
  "v97", #JAN: ACT NUM FORC RAPE
  "v215", #FEB: ACT NUM FORC RAPE
  "v333", #MAR: ACT NUM FORC RAPE
  "v451", #APR: ACT NUM FORC RAPE
  "v569", #MAY: ACT NUM FORC RAPE
  "v687", #JUN: ACT NUM FORC RAPE
  "v805", #JUL: ACT NUM FORC RAPE
  "v923", #AUG: ACT NUM FORC RAPE
  "v1041", #SEP: ACT NUM FORC RAPE
  "v1159", #OCT: ACT NUM FORC RAPE
  "v1277", #NOV: ACT NUM FORC RAPE
  "v1395" #DEC: ACT NUM FORC RAPE
)


CONST_SRS_ATTEMPTED_LEGACY_RAPE <- c(
  "v98", #JAN: ACT NUM ATMPTD RAPE
  "v216", #FEB: ACT NUM ATMPTD RAPE
  "v334", #MAR: ACT NUM ATMPTD RAPE
  "v452", #APR: ACT NUM ATMPTD RAPE
  "v570", #MAY: ACT NUM ATMPTD RAPE
  "v688", #JUN: ACT NUM ATMPTD RAPE
  "v806", #JUL: ACT NUM ATMPTD RAPE
  "v924", #AUG: ACT NUM ATMPTD RAPE
  "v1042", #SEP: ACT NUM ATMPTD RAPE
  "v1160", #OCT: ACT NUM ATMPTD RAPE
  "v1278", #NOV: ACT NUM ATMPTD RAPE
  "v1396" #DEC: ACT NUM ATMPTD RAPE
  
)

################################################################

#Create dataset tbd_srs and drop the legacy ori variables
tbd_srs2 <- tbd_srs1 %>%
  #Need to drop the revised rape variables
  select(
    !!!(paste0("-", CONST_SRS_TOTAL_RAPE)) %>% rlang:::parse_exprs(),
    !!!(paste0("-", CONST_SRS_FORC_RAPE)) %>% rlang:::parse_exprs(),
    !!!(paste0("-", CONST_SRS_ATTEMPTED_RAPE)) %>% rlang:::parse_exprs()
  )

#Check the dimension
log_dim(tbd_srs2)
log_dim(tbd_srs1)


#Next do the rename
#Create dataset for the rename

tbd_rename_1 <- data.frame(
  #Revised Rape
  CONST_SRS_TOTAL_RAPE, 
  CONST_SRS_FORC_RAPE,
  CONST_SRS_ATTEMPTED_RAPE,
  
  #Legacy Rape
  CONST_SRS_TOTAL_LEGACY_RAPE,
  CONST_SRS_FORC_LEGACY_RAPE,
  CONST_SRS_ATTEMPTED_LEGACY_RAPE
)

#Need to loop thru and do the rename
tbd_srs3 <- tbd_srs2

for(i in 1:nrow(tbd_rename_1) ){
  
  #Revised Rape
  rn_total_rape = tbd_rename_1[i, "CONST_SRS_TOTAL_RAPE"] %>% rlang:::parse_expr()
  rn_for_rape = tbd_rename_1[i, "CONST_SRS_FORC_RAPE"] %>% rlang:::parse_expr()
  rn_attempted_rape = tbd_rename_1[i, "CONST_SRS_ATTEMPTED_RAPE"] %>% rlang:::parse_expr()
  
  #Legacy Rape
  rn_legacy_total_rape = tbd_rename_1[i, "CONST_SRS_TOTAL_LEGACY_RAPE"] %>% rlang:::parse_expr()
  rn_legacy_for_rape = tbd_rename_1[i, "CONST_SRS_FORC_LEGACY_RAPE"] %>% rlang:::parse_expr()
  rn_legacy_attempted_rape = tbd_rename_1[i, "CONST_SRS_ATTEMPTED_LEGACY_RAPE"] %>% rlang:::parse_expr()  
  
  #Rename the variables
  tbd_srs3 <- tbd_srs3 %>%
    rename(
      !!(rn_total_rape) := !!(rn_legacy_total_rape),
      !!(rn_for_rape) := !!(rn_legacy_for_rape),
      !!(rn_attempted_rape) := !!(rn_legacy_attempted_rape)
    )
  
  
  
}

#Check the dimension
log_dim(tbd_srs3)
log_dim(tbd_srs2)

#Create the tbd_srs data
tbd_srs <- tbd_srs3


#Using srs0 need to identify the ori that are in the final_imputed_srs and replace 
#their data with the imputed SRS data

#Do the merge by ORI
tbd_good_1 <- tbd_srs %>%
  inner_join(final_imputed_srs %>% select(ORI), by=c("ORI" = "ORI")) %>%
  #Create a temporary ORI variable for match
  mutate(ORI_MATCH = ORI)

tbd_bad_1 <- tbd_srs %>%
  anti_join(final_imputed_srs %>% select(ORI), by=("ORI" = "ORI"))

#Do the remaining merge by ORI_UNIV

tbd_good_2 <- tbd_bad_1 %>%
  inner_join(final_imputed_srs %>% select(ORI), by=c("ORI_UNIV" = "ORI")) %>%
  #Create a temporary ORI variable for match
  mutate(ORI_MATCH = ORI_UNIV)

tbd_bad_2 <- tbd_bad_1 %>%
  anti_join(final_imputed_srs %>% select(ORI), by=c("ORI_UNIV" = "ORI"))

#Create the dataset
tbd_match    <- bind_rows(tbd_good_1, tbd_good_2)
tbd_no_match <- tbd_bad_2

#Check the dimension
log_dim(tbd_srs)
log_dim(final_imputed_srs)
log_dim(tbd_match)
log_dim(tbd_no_match)


log_dim(tbd_good_1)
log_dim(tbd_bad_1)
log_dim(tbd_good_2)
log_dim(tbd_bad_2)

#Next using tbd_match, need to drop the v variables and mm flags and replace them
#with the imputed version

#Need to drop the variables in common
tbd_match2 <- tbd_match %>%
  select(!!!paste0("-", CONST_DROP_VARS) %>% rlang:::parse_exprs() )

log_dim(tbd_match)
log_dim(tbd_match2)

#Next need to merge on the imputed variables and create an indicator variable
tbd_match3 <- tbd_match2 %>%
  left_join(final_imputed_srs %>% 
              mutate(der_in_nibrs_imputed = 1), by=c("ORI_MATCH" = "ORI"))

#Check to see if everything merges
log_dim(tbd_match3)
sum(tbd_match3$der_in_nibrs_imputed)

#Using tbd_match3 and tbd_no_match, need to stack the dataset together to create
#the srs dataset 

srs <- bind_rows(tbd_match3, tbd_no_match)

#Check the dimension
log_dim(tbd_srs)
log_dim(srs)
log_dim(tbd_match3)
log_dim(tbd_no_match)

#Need to delete the tbd datasets
rm(list=ls(pattern="tbd_"))
invisible(gc())								


# Recode variables from character to numeric
srs <- srs %>% mutate(rpt_type  = 
                        fcase(
                          REPORTING_TYPE_UNIV =="I", 1,
                          REPORTING_TYPE_UNIV=="S", 2))

srs <- srs %>% mutate(suburb_flg  = 
                        fcase(
                          SUBURBAN_AREA_FLAG_UNIV=="Y", 1,
                          SUBURBAN_AREA_FLAG_UNIV=="N", 0))


srs <- srs %>% mutate(cover_flg  = 
                        fcase(
                          COVERED_FLAG_UNIV=="Y", 1,
                          COVERED_FLAG_UNIV=="N", 0))

srs <- srs %>% mutate(agn_status  = 
                        fcase(
                          AGENCY_STATUS_UNIV=="A", 1,
                          AGENCY_STATUS_UNIV=="D", 2,
                          AGENCY_STATUS_UNIV=="L", 3,
                          AGENCY_STATUS_UNIV=="F", 4))

srs <- srs %>% mutate(agn_type  = 
                        fcase(
                          AGENCY_TYPE_NAME_UNIV=="City", 1,
                          AGENCY_TYPE_NAME_UNIV=="County", 2,
                          AGENCY_TYPE_NAME_UNIV=="Federal", 3,
                          AGENCY_TYPE_NAME_UNIV=="Other", 4,
                          AGENCY_TYPE_NAME_UNIV=="Other State Agency", 5,
                          AGENCY_TYPE_NAME_UNIV=="State Police", 6,
                          AGENCY_TYPE_NAME_UNIV=="Tribal", 7,
                          AGENCY_TYPE_NAME_UNIV=="University or College", 8))

# Determine eligibility

states= c(
  "AL",     #Alabama
  "AK",     #Alaska
  "AZ",     #Arizona
  "AR",     #Arkansas
  "CA",     #California
  "CO",     #Colorado
  "CT",     #Connecticut
  "DE",     #Delaware
  "DC",     #District of Columbia
  "FL",     #Florida
  "GA",     #Georgia
  "HI",     #Hawaii
  "ID",     #Idaho
  "IL",     #Illinois
  "IN",     #Indiana
  "IA",     #Iowa
  "KS",     #Kansas
  "KY",     #Kentucky
  "LA",     #Louisiana
  "ME",     #Maine
  "MD",     #Maryland
  "MA",     #Massachusetts
  "MI",     #Michigan
  "MN",     #Minnesota
  "MS",     #Mississippi
  "MO",     #Missouri
  "MT",     #Montana
  "NB",     #Nebraska
  "NV",     #Nevada
  "NH",     #New Hampshire
  "NJ",     #New Jersey
  "NM",     #New Mexico
  "NY",     #New York
  "NC",     #North Carolina
  "ND",     #North Dakota
  "OH",     #Ohio
  "OK",     #Oklahoma
  "OR",     #Oregon
  "PA",     #Pennsylvania
  "RI",     #Rhode Island
  "SC",     #South Carolina
  "SD",     #South Dakota
  "TN",     #Tennessee
  "TX",     #Texas
  "UT",     #Utah
  "VT",     #Vermont
  "VA",     #Virginia
  "WA",     #Washington
  "WV",     #West Virginia
  "WI",     #Wisconsin
  "WY")     #Wyoming

trim_upper <- compose(toupper, partial(trimws, which="both"))

elig_recode <- function(data){
  
  returndata <- data %>% mutate(
    
    in_univ_elig_state = trim_upper(STATE_ABBR_UNIV) %in% states,
    
    der_in_univ_elig =  case_when(
      trim_upper(AGENCY_STATUS_UNIV) == "A" & 
        trim_upper(COVERED_FLAG_UNIV) == "N" &  
        trim_upper(DORMANT_FLAG_UNIV) == "N" &
        trim_upper(AGENCY_TYPE_NAME_UNIV) != "FEDERAL" &
        in_univ_elig_state == TRUE ~ 1,
      TRUE ~ 0)
  )
  
  #Return the data
  return(returndata)
}    

srs <- elig_recode(srs)

# Covering agencies - will be used to define imputation classes
covering <- srs %>% filter(!is.na(COVERED_BY_LEGACY_ORI_UNIV)) %>%
  select(COVERED_BY_LEGACY_ORI_UNIV) %>%
  rename(ORI_UNIV=COVERED_BY_LEGACY_ORI_UNIV) %>%
  mutate(coveringAgency=1) %>%
  distinct()

srs2 <- srs %>% left_join(covering,by="ORI_UNIV") %>% mutate(coveringAgency=coalesce(coveringAgency,0))


# Keep variables and records needed for imputation
#Remove year since it may cause issue, since it is not the partial reporter output																				  
#srs3 <- srs2 %>% filter(data_year==year & der_in_univ_elig==1) %>%
tbd_srs <- srs2 %>% filter(der_in_univ_elig==1) %>%												   
  select(ORI, #data_year,
         cover_flg, suburb_flg,
         rpt_type, agn_type, agn_status, coveringAgency,
         STATE_ID_UNIV, POPULATION_UNIV, REGION_CODE_UNIV, DIVISION_CODE_UNIV, POPULATION_GROUP_ID_UNIV,
         MALE_OFFICER_UNIV, MALE_CIVILIAN_UNIV, FEMALE_OFFICER_UNIV, FEMALE_CIVILIAN_UNIV,
         starts_with("v"), ends_with("mm_flag")) %>%
         #Need to drop the non-imputed officer variables
        select(-MALE_OFFICER_UNIV, -MALE_CIVILIAN_UNIV, -FEMALE_OFFICER_UNIV, -FEMALE_CIVILIAN_UNIV)

################New need to use the imputed officer counts here ##################################

#Next need to read in the pseudo ori file
tbd_universe <- read_csv(paste0(raw_srs_file_path, "ref_agency_", year, ".csv")) 
log_dim(tbd_universe)

#Next need to keep certain variables
tbd_universe2 <- tbd_universe %>%
  select(ORI, LEGACY_ORI, PE_MALE_OFFICER_COUNT, PE_FEMALE_OFFICER_COUNT, PE_MALE_CIVILIAN_COUNT, PE_FEMALE_CIVILIAN_COUNT) %>%
  #Need to deduplicate
  distinct(ORI, LEGACY_ORI, PE_MALE_OFFICER_COUNT, PE_FEMALE_OFFICER_COUNT, PE_MALE_CIVILIAN_COUNT, PE_FEMALE_CIVILIAN_COUNT)

#Check to see the dim
log_dim(tbd_universe2)

#Need to join tbd_srs and tbd_universe2
tbd_good <- tbd_srs %>%
  inner_join(tbd_universe2 %>% select(-LEGACY_ORI), by = c("ORI" = "ORI"))

tbd_bad <- tbd_srs %>%
  anti_join(tbd_universe2 %>% select(-LEGACY_ORI), by = c("ORI" ="ORI"))

tbd_good2 <- tbd_bad %>%
  inner_join(tbd_universe2 %>% select(-ORI), by = c("ORI" = "LEGACY_ORI"))

tbd_bad2 <- tbd_bad %>%
  anti_join(tbd_universe2 %>% select(-ORI), by = c("ORI" ="LEGACY_ORI"))

#Put the dataset together
tbd_srs2 <- bind_rows(tbd_good, tbd_good2, tbd_bad2)

#See the dim
log_dim(tbd_srs2)
log_dim(tbd_good)
log_dim(tbd_bad)
log_dim(tbd_good2)
log_dim(tbd_bad2)

#Drop the old police employment variables and rename them
tbd_srs3 <- tbd_srs2 %>%
  #Rename the police officer variables
  rename(
    MALE_OFFICER_UNIV    = PE_MALE_OFFICER_COUNT, 
    FEMALE_OFFICER_UNIV  = PE_FEMALE_OFFICER_COUNT, 
    MALE_CIVILIAN_UNIV    = PE_MALE_CIVILIAN_COUNT, 
    FEMALE_CIVILIAN_UNIV  = PE_FEMALE_CIVILIAN_COUNT
  )

#Create the srs3 to be consistent with rest of program
srs3 <- tbd_srs3

#Delete the tbd_objects
rm(list=ls(pattern="^tbd_"))
invisible(gc())

###################################################################################################




# Define factor variables
srs3 <- srs3 %>% mutate_at(c("cover_flg", "suburb_flg", "rpt_type", "agn_type", "REGION_CODE_UNIV",
                                   "agn_status", "coveringAgency", "STATE_ID_UNIV", "POPULATION_GROUP_ID_UNIV",
                                   "DIVISION_CODE_UNIV"), as.factor)


#NEW using srs3 need to make into missing the SRS's v variables using the MM flag variables
CONST_V_VARS  <- srs3 %>%
  colnames() %>%
  as_tibble() %>%
  mutate(
    #Keep the v variables
    der_keep = str_detect(value, pattern="^v\\d+$")
  ) %>%
  #Filter to the variables
  filter(der_keep == TRUE) %>%
  select(value) %>%
  pull()

CONST_MM_VARS <- srs3 %>%
  colnames() %>%
  as_tibble() %>%
  mutate(
    #Keep the mm flag variables
    der_keep2 = str_detect(value, pattern="_mm_flag$"),
  ) %>%
  #Filter to the variables
  filter(der_keep2 == TRUE) %>%
  select(value) %>%
  pull()


CONST_V_MM_VARS <- c(CONST_V_VARS, CONST_MM_VARS)
  

#See the list of variables
print(CONST_V_VARS)
print(CONST_MM_VARS)
print(CONST_V_MM_VARS)

#Declare the monthly variables
CONST_VARS_JAN <- c(70:95)
CONST_VARS_FEB <- c(188:213)
CONST_VARS_MAR <- c(306:331)

CONST_VARS_APR <- c(424:449)
CONST_VARS_MAY <- c(542:567)
CONST_VARS_JUN <- c(660:685)

CONST_VARS_JUL <- c(778:803)
CONST_VARS_AUG <- c(896:921)
CONST_VARS_SEP <- c(1014:1039)

CONST_VARS_OCT <- c(1132:1157)
CONST_VARS_NOV <- c(1250:1275)
CONST_VARS_DEC <- c(1368:1393)

CONST_VARS_ALL_MONTH <-paste0(
  "v", 
  c(CONST_VARS_JAN, CONST_VARS_FEB, CONST_VARS_MAR,
    CONST_VARS_APR, CONST_VARS_MAY, CONST_VARS_JUN,
    CONST_VARS_JUL, CONST_VARS_AUG, CONST_VARS_SEP,
    CONST_VARS_OCT, CONST_VARS_NOV, CONST_VARS_DEC
    )
)
  


#Declare the ID variables
CONST_ID <- c("ORI", "STATE_ID_UNIV")

#Using srs3 - split to two datasets
#tbd_final_vars contains all variables that are not the v variables
#tbd_srs0       contains the v variables

tbd_final_vars <- srs3 %>%
  #Drop the variables
  select(!!!(paste0("-", CONST_V_VARS) %>% rlang:::parse_exprs()))

tbd_srs0 <- srs3 %>%
  #Keep selected variables
  select(
    !!!(CONST_ID %>% rlang:::parse_exprs()),
    !!!(CONST_V_MM_VARS %>% rlang:::parse_exprs())
  )

#Check the dimension
log_dim(srs3)
log_dim(tbd_final_vars)
log_dim(tbd_srs0)

#Get the list of state_id to loop thru
CONST_STATE_ID_LOOP <- tbd_srs0 %>%
  distinct(STATE_ID_UNIV) %>%
  select(STATE_ID_UNIV) %>%
  pull()

#See the list of State ids
print(CONST_STATE_ID_LOOP)

#Using tbd_srs0, need to transpose the data from wide to long

final_edited_srs <- map_dfr(CONST_STATE_ID_LOOP, ~{
  
  print(paste0("Processing STATE_ID_UNIV ", .x))
  
  raw_srs1 <- tbd_srs0 %>%
    #Filter to current state
    filter(STATE_ID_UNIV == .x) %>%
    gather(
      #Identify the IDs
      !!! paste0("-", CONST_ID) %>% rlang:::parse_exprs(),
      #Name the v variables and mm flags and its current values
      key   = "variables",
      value = "value"
    )
  
  #Need to code the v variables from the mm flags
  raw_srs2 <- raw_srs1 %>%
    mutate(
      der_v_vars  = str_detect(variables, pattern="v\\d+"),
      der_mm_vars = str_detect(variables, pattern="_mm_flag$"),
      
    )
  
  #Check to see if all variables are accounted for
  log_dim(raw_srs2)
  print(table(raw_srs2$der_v_vars))
  print(table(raw_srs2$der_mm_vars))
  
  #Next split up the datasets
  raw_srs3_v_vars  <- raw_srs2 %>% filter(der_v_vars == TRUE) 
  raw_srs3_mm_vars <- raw_srs2 %>% filter(der_mm_vars == TRUE) 
  
  #Check to see if all variables are accounted for
  log_dim(raw_srs2)
  log_dim(raw_srs3_v_vars)
  log_dim(raw_srs3_mm_vars)
  
  #First process the raw_srs3_mm_vars
  raw_mm <- raw_srs3_mm_vars %>%
    mutate(
      der_month = fcase(
        trim_upper(variables) == "JAN_MM_FLAG", 1, 
        trim_upper(variables) == "FEB_MM_FLAG", 2, 
        trim_upper(variables) == "MAR_MM_FLAG", 3, 
        trim_upper(variables) == "APR_MM_FLAG", 4, 
        trim_upper(variables) == "MAY_MM_FLAG", 5, 
        trim_upper(variables) == "JUN_MM_FLAG", 6, 
        trim_upper(variables) == "JUL_MM_FLAG", 7, 
        trim_upper(variables) == "AUG_MM_FLAG", 8, 
        trim_upper(variables) == "SEP_MM_FLAG", 9, 
        trim_upper(variables) == "OCT_MM_FLAG", 10, 
        trim_upper(variables) == "NOV_MM_FLAG", 11, 
        trim_upper(variables) == "DEC_MM_FLAG", 12)
    )
  
  #Check the recodes
  table(raw_mm$der_month, raw_mm$variables)
  
  #Second process the raw_srs3_v_vars
  raw_v <- raw_srs3_v_vars %>%
    #Create the numeric version 
    mutate(
      der_v_num = str_match(string=variables, pattern="v(\\d+)")[,2] %>% as.numeric(),
      
      #Create the der_month variable to merge on the mm flag
      der_month = fcase(
        
        
        der_v_num %in% c(CONST_VARS_JAN), 1, 
        der_v_num %in% c(CONST_VARS_FEB), 2, 
        der_v_num %in% c(CONST_VARS_MAR), 3, 
        
        der_v_num %in% c(CONST_VARS_APR), 4, 
        der_v_num %in% c(CONST_VARS_MAY), 5, 
        der_v_num %in% c(CONST_VARS_JUN), 6, 
        
        der_v_num %in% c(CONST_VARS_JUL), 7, 
        der_v_num %in% c(CONST_VARS_AUG), 8, 
        der_v_num %in% c(CONST_VARS_SEP), 9, 
        
        der_v_num %in% c(CONST_VARS_OCT), 10,
        der_v_num %in% c(CONST_VARS_NOV), 11,
        der_v_num %in% c(CONST_VARS_DEC), 12
        
      )
    )
  
  #Check to see if der_month is non missing
  raw_v %>%
    group_by(der_month) %>%
    summarise(
      min_v = min(der_v_num),
      max_v = max(der_v_num)
    ) %>%
    print()
  
  #Next need to merge on raw_v and raw_mm
  raw_v_mm <- raw_v %>%
    select(ORI, STATE_ID_UNIV, der_month, variables,
            #Rename value to srs_value
            srs_value = value) %>%
    full_join(raw_mm  %>%
              select(ORI, STATE_ID_UNIV, der_month,
                     #Rename value to mm_flag_value
                     mm_flag_value= value
                     ), by=c("ORI", "STATE_ID_UNIV", "der_month"))
  
  #Check the dimension
  log_dim(raw_v_mm)
  log_dim(raw_v)
  log_dim(raw_mm)
  
  #Using raw_v_mm, need to make the srs_value that have values of 0 and mm_flag_value of 0 to missing
  raw_v_mm2 <- raw_v_mm %>%
    mutate(
      #Make a one variable to be always TRUE
      one = 1,
      
      final_srs_value = fcase(
        #Make the srs value to be missing if the srs value is 0 and mm flag is 0
        srs_value == 0 & mm_flag_value == 0, NA_real_, 
        one == 1,   srs_value
        
      )
  )
  
  #Next need to transpose the data back from long to wide 
  raw_v_mm3 <- raw_v_mm2 %>%
    #Keep selected variables
    select(
      #Identify the IDs
      !!!(CONST_ID %>% rlang:::parse_exprs()),
      
      #Identify the variables to transpose back
      variables,
      final_srs_value) %>%
    #Make from long to wide and provide back original variable names with final edited values
    spread(key=variables, value=final_srs_value) %>%
    #put in the correct order
    select(
      !!!(CONST_ID %>% rlang:::parse_exprs()),
      !!!(CONST_VARS_ALL_MONTH %>% rlang:::parse_exprs()),
      everything()
    )
  
  #Return the dataset
  return(raw_v_mm3)
    
})  



#Create the srs object
srs3_1 <- final_edited_srs %>%
  full_join(tbd_final_vars, by=CONST_ID)

#Check the joins
log_dim(srs3_1)
log_dim(final_edited_srs)
log_dim(tbd_final_vars)

# Keep the original state variable as numeric instead of factor for later use
srs3_1$STATE_ID_UNIV <- factor(srs3_1$STATE_ID_UNIV,
	levels=CONST_STATE_FACTOR %>% select(state_num) %>% pull(),
	labels=CONST_STATE_FACTOR %>% select(state_factor) %>% pull())

# Make sure only the variables of interest start with the month name as prefix and factors are defined properly
str(srs3_1)

###-------------------------------------------------------------------------------
### Staff count imputation 
###-------------------------------------------------------------------------------

# Specify prediction matrix and variables that need to be included in variable selection
init = mice(srs3_1, maxit=0)
meth = init$method
pred = init$predictorMatrix

incpreds  <- c("state","agn_type","POPULATION_GROUP_ID_UNIV", "suburb_flg")
predQuick <- quickpred(srs3_1, minpuc = 0.25, include = incpreds) 
predQuick[,c("ORI", "REGION_CODE_UNIV", "DIVISION_CODE_UNIV")] <- 0
# Need to convert matrix to DF first - set all the counts and mm_flag vars to 0 so not used for imputation of
# officer counts
predQuick2=as.data.frame(predQuick)
predQuick3 <- predQuick2 %>% mutate(across(
                                .cols = starts_with("v") | ends_with("mm_flag"),
                                .fns = ~ {.x=0},
                                .names = "{.col}"))
# And then convert back to matrix
predQuick4=data.matrix(predQuick3)


# Run the imputation
impLEA = mice(srs3_1, pred=predQuick4, meth="pmm", m=1, seed=254658, maxit=15)

# Plot variables of interest  
#plot(impLEA,c("MALE_OFFICER_UNIV","MALE_CIVILIAN_UNIV","FEMALE_OFFICER_UNIV","FEMALE_CIVILIAN_UNIV"))

# Create complete dataset that will be used to check imputations
LEAcomp <- complete(impLEA,"broad",1)
LEAcomp <- as.data.frame(LEAcomp)

# Create dataset with staff count imputed variables to be used in the next imputation section
ImputedVars <- complete(impLEA,1)

###-------------------------------------------------------------------------------
### Combine different sources of information and calculate CT for imputation
###-------------------------------------------------------------------------------

# Keep only the staff imputed variables and calculate total based on imputed values
ImputedVars <- ImputedVars %>% select(ORI, MALE_OFFICER_UNIV, FEMALE_OFFICER_UNIV, MALE_CIVILIAN_UNIV, FEMALE_CIVILIAN_UNIV)  %>% 
  mutate(TOTAL_OFFICERS=MALE_OFFICER_UNIV+FEMALE_OFFICER_UNIV)
names(ImputedVars)
dim(ImputedVars)


# Read JD's data and merge it to exclude outlier records
# out <- read_csv(file.path(outlier_detection_in,"outlier_data_file.csv"))
# 
# year_end = substr(year,3,4)
# 
# out <- out %>% select(ori, nSeqs, nBlueOutliers, nRedOutliers, nOrangeOutliers, ends_with(year_end)) %>%
#   rename(
#               p1=paste0("Jan-", year_end),
#               p2=paste0("Feb-", year_end),
#               p3=paste0("Mar-", year_end),
#               p4=paste0("Apr-", year_end),
#               p5=paste0("May-", year_end),
#               p6=paste0("Jun-", year_end),
#               p7=paste0("Jul-", year_end),
#               p8=paste0("Aug-", year_end),
#               p9=paste0("Sep-", year_end),
#               p10=paste0("Oct-", year_end),
#               p11=paste0("Nov-", year_end),
#               p12=paste0("Dec-", year_end)
#        )  
# 
# # High outliers - can't be donors
# vals <- c("brown","blue")
# out <- out %>% rowwise() %>% 
#         mutate(out_months=sum(p1 %in% vals, p2 %in% vals, p3 %in% vals, p4 %in% vals,
#                               p5 %in% vals, p6 %in% vals, p7 %in% vals, p8 %in% vals,
#                               p9 %in% vals, p10 %in% vals, p11 %in% vals, p12 %in% vals, 
#                               na.rm=TRUE)) %>%
#         mutate(outlier_elig_donor=fcase(out_months==0,1,
#                                         out_months>0,0)) %>%
#         ungroup()
# 
# out_final <- out %>% select(ori,outlier_elig_donor)
# 
# ImputedVars_1 <- ImputedVars %>% left_join(out_final,by=c("ORI"="ori")) %>% 
#                  mutate(outlier_elig_donor=replace_na(outlier_elig_donor,value=1))

#Create ImputedVars_1 dataset
ImputedVars_1 <- ImputedVars %>%
  mutate(Lowoutlier = 0, 
         Highoutlier = 0,
         low_p1 = 0,
         low_p2 = 0,
         low_p3 = 0,
         low_p4 = 0,
         low_p5 = 0,
         low_p6 = 0,
         low_p7 = 0,
         low_p8 = 0,
         low_p9 = 0,
         low_p10 = 0,
         low_p11 = 0,
         low_p12 = 0, 
         outlier_elig_donor = 1)


# Merge original file, excluding the original staff counts and state not being a factor
srs3_orig <- srs3 %>% select(-c(MALE_OFFICER_UNIV, MALE_CIVILIAN_UNIV, FEMALE_OFFICER_UNIV, FEMALE_CIVILIAN_UNIV))
srs4 <- left_join(ImputedVars_1, srs3_orig, by =c("ORI"))
names(srs4)
dim(srs4)

# Make sure there are no missing values
summary(srs4$MALE_OFFICER_UNIV)
summary(srs4$FEMALE_OFFICER_UNIV)
summary(srs4$TOTAL_OFFICERS)
summary(srs4$STATE_ID_UNIV)
summary(srs4$agn_type)
summary(srs4$REGION_CODE_UNIV)
summary(srs4$POPULATION_UNIV)

# Calculate crime totals across 12 months
srs4 <- srs4 %>% rowwise() %>%
         mutate(ct=sum(v95,v213,v331,v449,v567,v685,v803,v921,v1039,v1157,v1275,v1393)) %>%
         ungroup()

# Create a NR_flag for non-respondents (=1) and respondents (=0)

rpt <- c(1,9)
srs4 <- srs4 %>%
  rowwise() %>%
  mutate(mosNR = sum(jan_mm_flag==0,feb_mm_flag==0,mar_mm_flag==0,
                     apr_mm_flag==0,may_mm_flag==0,jun_mm_flag==0,
                     jul_mm_flag==0,aug_mm_flag==0,sep_mm_flag==0,
                     oct_mm_flag==0,nov_mm_flag==0,dec_mm_flag==0,na.rm=TRUE)) %>%
  mutate(mosRPT = sum(jan_mm_flag %in% rpt,feb_mm_flag %in% rpt,mar_mm_flag %in% rpt,
                      apr_mm_flag %in% rpt,may_mm_flag %in% rpt,jun_mm_flag %in% rpt,
                      jul_mm_flag %in% rpt,aug_mm_flag %in% rpt,sep_mm_flag %in% rpt,
                      oct_mm_flag %in% rpt,nov_mm_flag %in% rpt,dec_mm_flag %in% rpt,
                      na.rm=TRUE)) %>%
  mutate(mosNA = sum(is.na(jan_mm_flag),is.na(feb_mm_flag),is.na(mar_mm_flag),is.na(apr_mm_flag),
                     is.na(may_mm_flag),is.na(jun_mm_flag),is.na(jul_mm_flag),is.na(aug_mm_flag),
                     is.na(sep_mm_flag),is.na(oct_mm_flag),is.na(nov_mm_flag),is.na(dec_mm_flag)
                     )) %>%
  mutate(NR_flag=ifelse(mosRPT==12,0,1)) %>% #non-respondents
  mutate(partialRPTR=ifelse(NR_flag==1 & mosRPT > 2,1,0)) %>% #partial reporter
  mutate(POP0=ifelse(POPULATION_UNIV==0,1,0)) %>% #pop0 used for imputation classes
  ungroup()

table(srs4$NR_flag,srs4$partialRPTR,useNA="always")



###-------------------------------------------------------------------------------
### Imputation Method #3
###-------------------------------------------------------------------------------

# Define factor variables
srs4_2 <- srs4 %>% mutate_at(c("suburb_flg", "rpt_type", "agn_type", "agn_status", "STATE_ID_UNIV", "REGION_CODE_UNIV", "POP0", "coveringAgency"), as.factor)

# Split between donors and agencies that need imputation
don_m3 <- srs4_2 %>% filter(NR_flag==0 & outlier_elig_donor==1) %>%
                     filter(!(if_any(.cols=starts_with("v"), .fns = ~ .x < 0)))

# Run regression only on donors but no high/low outliers
fit <- lm(ct ~ 
            suburb_flg + agn_type+ STATE_ID_UNIV + POPULATION_UNIV + MALE_OFFICER_UNIV + FEMALE_OFFICER_UNIV + coveringAgency, data=don_m3)

fit2 <- MASS:::stepAIC(fit, direction="both")

pred_m3 <- predict(fit2, srs4_2)

srs4_2['pred'] <- pred_m3

# Split between donors and agencies that need imputation
imp_m3 <- srs4_2 %>% filter(NR_flag==1 & partialRPTR==1)
don_m3 <- srs4_2 %>% filter(NR_flag==0 & outlier_elig_donor==1) %>%
                     filter(!(if_any(.cols=starts_with("v"), .fns = ~ .x < 0)))

# Save the complete cases that can't be donors and agencies reporting < 3 months
don_m3_out <- srs4_2 %>% filter(NR_flag==0 & outlier_elig_donor==0) # outliers
don_m3_neg <- srs4_2 %>% filter(NR_flag==0 & outlier_elig_donor==1) %>%
                         filter((if_any(.cols=starts_with("v"), .fns = ~ .x < 0))) # cases with negative crime counts
non_reporters <- srs4_2 %>% filter(NR_flag==1 & partialRPTR==0) # will save non-reporters for later

imp_m3 <- data.frame(imp_m3)
don_m3 <- data.frame(don_m3)


imp_meth3 <- NND.hotdeck(imp_m3, don_m3, match.vars=c("pred"), don.class=c("POP0","coveringAgency"), dist.fun="Euclidean", k=5)

# Get a list of the donor variables we need
dummyd <- don_m3 %>% select("ORI","ct","pred",starts_with("v"))
donorvars <- colnames(dummyd)

dat_m3_grp1 <- create.fused(imp_m3, don_m3, imp_meth3$mtc.ids, dup.x=T, 
                            match.vars=donorvars, z.vars=NULL)



imp_dat <- dat_m3_grp1 %>% mutate(across(num_range("v", 70:95),
                                  .fns= ~ fcase(jan_mm_flag==0 , get(glue::glue("{cur_column()}.don")),
                                                jan_mm_flag %in% c(1,9) , .x,
                                                default = -9),
                                  .names="{.col}")) %>%
                           mutate(across(num_range("v", 188:213),
                                  .fns= ~ fcase(feb_mm_flag==0 , get(glue::glue("{cur_column()}.don")),
                                                feb_mm_flag %in% c(1,9) , .x,
                                                default = -9),
                                  .names="{.col}")) %>%
                           mutate(across(num_range("v", 306:331),
                                  .fns= ~ fcase(mar_mm_flag==0 , get(glue::glue("{cur_column()}.don")),
                                                mar_mm_flag %in% c(1,9) , .x,
                                                default = -9),
                                  .names="{.col}")) %>%
                           mutate(across(num_range("v", 424:449),
                                  .fns= ~ fcase(apr_mm_flag==0 , get(glue::glue("{cur_column()}.don")),
                                                apr_mm_flag %in% c(1,9) , .x,
                                                default = -9),
                                  .names="{.col}")) %>%
                           mutate(across(num_range("v", 542:567),
                                  .fns= ~ fcase(may_mm_flag==0 , get(glue::glue("{cur_column()}.don")),
                                                may_mm_flag %in% c(1,9) , .x,
                                                default = -9),
                                  .names="{.col}")) %>%
                           mutate(across(num_range("v", 660:685),
                                  .fns= ~ fcase(jun_mm_flag==0 , get(glue::glue("{cur_column()}.don")),
                                                jun_mm_flag %in% c(1,9) , .x,
                                                default = -9),
                                  .names="{.col}")) %>%
                           mutate(across(num_range("v", 778:803),
                                  .fns= ~ fcase(jul_mm_flag==0 , get(glue::glue("{cur_column()}.don")),
                                                jul_mm_flag %in% c(1,9) , .x,
                                                default = -9),
                                  .names="{.col}")) %>%
                           mutate(across(num_range("v", 896:921),
                                  .fns= ~ fcase(aug_mm_flag==0 , get(glue::glue("{cur_column()}.don")),
                                                aug_mm_flag %in% c(1,9) , .x,
                                                default = -9),
                                  .names="{.col}")) %>%
                           mutate(across(num_range("v", 1014:1039),
                                  .fns= ~ fcase(sep_mm_flag==0 , get(glue::glue("{cur_column()}.don")),
                                                sep_mm_flag %in% c(1,9) , .x,
                                                default = -9),
                                  .names="{.col}")) %>%
                           mutate(across(num_range("v", 1132:1157),
                                  .fns= ~ fcase(oct_mm_flag==0 , get(glue::glue("{cur_column()}.don")),
                                                oct_mm_flag %in% c(1,9) , .x,
                                                default = -9),
                                  .names="{.col}")) %>%
                           mutate(across(num_range("v", 1250:1275),
                                  .fns= ~ fcase(nov_mm_flag==0 , get(glue::glue("{cur_column()}.don")),
                                                nov_mm_flag %in% c(1,9) , .x,
                                                default = -9),
                                  .names="{.col}")) %>%
                           mutate(across(num_range("v", 1368:1393),
                                  .fns= ~ fcase(dec_mm_flag==0 , get(glue::glue("{cur_column()}.don")),
                                                dec_mm_flag %in% c(1,9) , .x,
                                                default = -9),
                                  .names="{.col}")) 


imp_dat2 <- imp_dat %>% select(!ends_with(".don"))

# Combine all of the agency records (do not include ineligible agencies)
all_dat <- imp_dat2 %>% # imputed cases
           bind_rows(don_m3) %>% # donors
           bind_rows(don_m3_out) %>% # outliers
           bind_rows(don_m3_neg) %>% # respondents with negative crime counts
           bind_rows(non_reporters) %>% # reported < 3 months
           rename(MALE_OFFICER_IMP=MALE_OFFICER_UNIV,FEMALE_OFFICER_IMP=FEMALE_OFFICER_UNIV,
                  MALE_CIVILIAN_IMP=MALE_CIVILIAN_UNIV,FEMALE_CIVILIAN_IMP=FEMALE_CIVILIAN_UNIV,
                  TOTAL_OFFICERS_IMP=TOTAL_OFFICERS) %>%
           select(ORI,starts_with("v"),ends_with("mm_flag"),ends_with("_IMP"),mosRPT,NR_flag,partialRPTR)

univ_vars <- srs %>% select(ORI,ends_with("_UNIV"),der_in_univ_elig) %>% filter(der_in_univ_elig==1)

final_imp_dat <- univ_vars %>% left_join(all_dat,by=c("ORI"))

write_csv(final_imp_dat,file.path(block_imputation_output, "SRS_Imputed_LR.csv"))

# Output the donor IDs for imputed cases
donorids <- dat_m3_grp1 %>% select("ORI","ORI.don")

write_csv(donorids,file.path(block_imputation_output, "donor_ids_srs_imp_LR.csv"))

