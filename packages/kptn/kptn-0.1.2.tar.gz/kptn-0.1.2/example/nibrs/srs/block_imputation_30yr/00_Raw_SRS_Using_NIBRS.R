###-------------------------------------------------------------------------------
### Define libraries
###-------------------------------------------------------------------------------

library(tidyverse)
# library(openxlsx)
# library(haven)
# library(mice)
# library(miceadds)
# library(VIM)
# library(naniar)
# library(visdat)
# library(ggplot2)
# library(StatMatch)
# library(writexl)
# library(sas7bdat)
# library(sjmisc)
# library(gtools)
# library(zoo)
# library(reshape2)
# library(lazyeval)
library(data.table)

set.seed(5242023)


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

#New bring in legacy rape since some SRS only agencies can report to this field only#


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

#Create the crosswalk for the rape variables
CROSSWALK_RAPE <- bind_rows(
  data.frame(crosswalk_rape = CONST_SRS_TOTAL_RAPE,     crosswalk_legacy_rape = CONST_SRS_TOTAL_LEGACY_RAPE),
  data.frame(crosswalk_rape = CONST_SRS_FORC_RAPE,      crosswalk_legacy_rape = CONST_SRS_FORC_LEGACY_RAPE),
  data.frame(crosswalk_rape = CONST_SRS_ATTEMPTED_RAPE, crosswalk_legacy_rape = CONST_SRS_ATTEMPTED_LEGACY_RAPE)
) %>%
  as_tibble()

###############################################################################


###-------------------------------------------------------------------------------
### Data preparation: Read in the imputed SRS file
###-------------------------------------------------------------------------------

#Okay to use read_csv as is since it is just a character ori variable and all numeric v variables
raw_converted_srs <- read_csv(paste0(filepathin, "SRS_Original_Combined.csv"))
log_dim(raw_converted_srs)


#Next need to create the final dataset and keep certain variables
final_converted_srs <- raw_converted_srs %>%
  select(ori, matches("v\\d+")) %>%
  #Note need to zero filled the NA v variables, the reasoning is that these agencies did not report
  #any incidents to NIBRS, so they are our 0 reporters
  mutate(
    across(
      .cols = matches("v\\d+"),
      .fns = ~ {
        replace_na(.x, replace = 0) 
        },
      .names="{.col}")
  )  %>%
  #Make ori into upper case
  rename(ORI = ori)

#Delete all the raw and tbd datasets
rm(list=c(ls(pattern="tbd"), setdiff(ls(pattern="raw"), "raw_srs_file_path")))

#Create a list or variables to be drop from the srs
CONST_DROP_VARS <- colnames(final_converted_srs) %>%
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

#Using tbd_srs1, need to fix agencies where agencies reported their rape values to the legacy rape variables only
#The crosswalk is in the following object CROSSWALK_RAPE
tbd_srs2 <- tbd_srs1

for(i in 1:nrow(CROSSWALK_RAPE)){
  
  #Get the current variables
  tbd_revised_var <- CROSSWALK_RAPE[i, "crosswalk_rape"] %>% pull() 
  tbd_legacy_var  <- CROSSWALK_RAPE[i, "crosswalk_legacy_rape"] %>% pull()
  
  #Create the symbols
  tbd_revised_var_sym <- tbd_revised_var %>% rlang:::parse_expr()
  tbd_legacy_var_sym  <- tbd_legacy_var %>% rlang:::parse_expr()  
  
  #Print to screen
  log_debug(paste0("Processing revised rape: ", tbd_revised_var, " and legacy rape: ", tbd_legacy_var))
  
  #Get the values from legacy rape if revised rape is 0
  tbd_srs2 <- tbd_srs2 %>%
    mutate(
      
      !!(tbd_revised_var_sym) := fcase(
        
        #If revised rape is 0 and legacy rape is greater than 0, then use value from legacy rape
        !!(tbd_revised_var_sym) == 0 & !!(tbd_legacy_var_sym) > 0, !!(tbd_legacy_var_sym),
        #Otherwise use revised
        !is.na(!!(tbd_revised_var_sym)),  !!(tbd_revised_var_sym)
      )
    )
  
  #Delete the objects not needed
  rm(tbd_revised_var, tbd_legacy_var, tbd_revised_var_sym, tbd_legacy_var_sym)
  invisible(gc())
}

#Create dataset tbd_srs
tbd_srs <- tbd_srs2

#Using srs0 need to identify the ori that are in the final_converted_srs and replace 
#their data with the converted SRS data

#Do the merge by ORI
tbd_good_1 <- tbd_srs %>%
  inner_join(final_converted_srs %>% select(ORI), by=c("ORI" = "ORI")) %>%
  #Create a temporary ORI variable for match
  mutate(ORI_MATCH = ORI)

tbd_bad_1 <- tbd_srs %>%
  anti_join(final_converted_srs %>% select(ORI), by=("ORI" = "ORI"))

#Do the remaining merge by ORI_UNIV

tbd_good_2 <- tbd_bad_1 %>%
  inner_join(final_converted_srs %>% select(ORI), by=c("ORI_UNIV" = "ORI")) %>%
  #Create a temporary ORI variable for match
  mutate(ORI_MATCH = ORI_UNIV)

tbd_bad_2 <- tbd_bad_1 %>%
  anti_join(final_converted_srs %>% select(ORI), by=c("ORI_UNIV" = "ORI"))

#Create the dataset
tbd_match    <- bind_rows(tbd_good_1, tbd_good_2)
tbd_no_match <- tbd_bad_2

#Check the dimension
log_dim(tbd_srs)
log_dim(final_converted_srs)
log_dim(tbd_match)
log_dim(tbd_no_match)


log_dim(tbd_good_1)
log_dim(tbd_bad_1)
log_dim(tbd_good_2)
log_dim(tbd_bad_2)

#Next using tbd_match, need to drop the v variables and mm flags and replace them
#with the converted version

#Need to drop the variables in common
tbd_match2 <- tbd_match %>%
  select(!!!paste0("-", CONST_DROP_VARS) %>% rlang:::parse_exprs() )

log_dim(tbd_match)
log_dim(tbd_match2)

#Next need to merge on the converted variables and create an indicator variable
tbd_match3 <- tbd_match2 %>%
  left_join(final_converted_srs %>% 
              mutate(der_in_nibrs_converted = 1), by=c("ORI_MATCH" = "ORI"))

#Check to see if everything merges
log_dim(tbd_match2)
log_dim(tbd_match3)
sum(tbd_match3$der_in_nibrs_converted)

#Using tbd_match3 and tbd_no_match, need to stack the dataset together to create
#the srs dataset 

srs <- bind_rows(tbd_match3, tbd_no_match)

#Check the dimension
log_dim(tbd_srs)
log_dim(srs)
log_dim(tbd_match3)
log_dim(tbd_no_match)


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
srs3 <- srs2 %>% filter(data_year==year & der_in_univ_elig==1) %>%
  select(ORI,ORI_UNIV,ORI_MATCH,data_year,
         cover_flg, suburb_flg,
         rpt_type, agn_type, agn_status, coveringAgency,
         STATE_ID_UNIV, POPULATION_UNIV, REGION_CODE_UNIV, DIVISION_CODE_UNIV, POPULATION_GROUP_ID_UNIV,
         MALE_OFFICER_UNIV, MALE_CIVILIAN_UNIV, FEMALE_OFFICER_UNIV, FEMALE_CIVILIAN_UNIV, ends_with("_UNIV"),
         starts_with("v"), ends_with("mm_flag"))

#Output to the share
srs3 %>%
  write_csv(paste0(block_imputation_output, "Raw_SRS_Using_Converted.csv"), na="")


