library(tidyverse)
library(openxlsx)
library(DBI)
library(DT)
library(lubridate)
library(readxl)
library(data.table)


#############################Need to create new victim imputed outputs#########################

source(here::here("tasks/impute_items/0-Common_functions_for_imputation.R"))

OUTPUT_PIPELINE_DIR <- Sys.getenv("OUTPUT_PIPELINE_DIR")

CONST_INPUT  <- paste0(OUTPUT_PIPELINE_DIR, "/srs/block_imputation/")
CONST_INPUT_WEIGHT  <- paste0(OUTPUT_PIPELINE_DIR, "/srs/weighting/Data/")
CONST_OUTPUT <- paste0(OUTPUT_PIPELINE_DIR, "/srs/indicator_table_extracts/")

if (! dir.exists(CONST_OUTPUT)) {
  dir.create(CONST_OUTPUT, recursive = TRUE)
}

###############################################################################################

########Read in the raw dataset###################################

raw_main <- fread(paste0(CONST_INPUT, "Raw_SRS_Using_Converted.csv"))

#See information on dataset
dim(raw_main)
glimpse(raw_main)

############################################################################

#######Create the derived variables#########################################

	CONST_murder <- c(	
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
					"v1368" #DEC: ACT NUM MURDER;
	)					

	CONST_rape <- c(	
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
					"v1370" #DEC: ACT NUM RAPE TOTL;
)
	
	CONST_robbery <- c( 
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
					"v1373" #DEC: ACT NUM ROBBRY TOT;
)
	
	CONST_assault <- c(	
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
						"v1378" #DEC: ACT NUM ASSLT TOTA;
)
	
	CONST_assault_gun <- c(	
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
							"v1379" #DEC: ACT NUM GUN ASSAUL;
)
	
	CONST_assault_knife <- c(	
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
							"v1380" #DEC: ACT NUM KNIFE ASSL;
)
	
	CONST_assault_other <- c(	
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
							"v1381" #DEC: ACT # OTH WPN ASSL;
)

	CONST_assault_unarm <- c(	
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
							"v1382" #DEC: ACT # HND/FEET ASL;
)

	CONST_simple_ass <- c(		
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
							"v1383" #DEC: ACT # SIMPLE ASSLT;
	)
	
	CONST_burglary <- c(		
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
							"v1384" #DEC: ACT # BURGLARY TOT;
)
	CONST_theft <- c(			
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
							"v1388" #DEC: ACT # LARCENY TOTA;
)
	CONST_mvt <- c(			
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
							"v1389" #DEC: ACT # VHC THEFT TO;							
)


############################################################################

raw_main2 <- raw_main %>%
	  #Do the sum by row
	  rowwise() %>%
    mutate(
      der_murder  = sum(!!!(CONST_murder %>% rlang:::parse_exprs()), na.rm=TRUE),
      der_rape    = sum(!!!(CONST_rape %>% rlang:::parse_exprs()), na.rm=TRUE),  
      der_robbery = sum(!!!(CONST_robbery %>% rlang:::parse_exprs()), na.rm=TRUE),  
      der_aggravated_assault = 
                    sum(!!!(c(CONST_assault_gun, 
                          CONST_assault_knife,
                          CONST_assault_other, 
                          CONST_assault_unarm) %>% rlang:::parse_exprs()) , na.rm=TRUE),
      
      der_violent_crime = sum(der_murder, der_rape, der_robbery, der_aggravated_assault, na.rm=TRUE),
      
      der_burglary      = sum(!!!(CONST_burglary %>% rlang:::parse_exprs()), na.rm=TRUE),
      der_larceny_theft = sum(!!!(CONST_theft %>% rlang:::parse_exprs()), na.rm=TRUE),
      der_mvt           = sum(!!!(CONST_mvt %>% rlang:::parse_exprs()), na.rm=TRUE),
      
      der_property_crime = sum(der_burglary, der_larceny_theft, der_mvt, na.rm=TRUE)
      ) %>%
    ungroup()
	
#Check the recodes
raw_main2 %>% checkfunction(der_murder, !!!(CONST_murder %>% rlang:::parse_exprs()))
raw_main2 %>% checkfunction(der_rape, !!!(CONST_rape %>% rlang:::parse_exprs()))
raw_main2 %>% checkfunction(der_robbery, !!!(CONST_robbery %>% rlang:::parse_exprs()))
raw_main2 %>% checkfunction(der_aggravated_assault, !!!(c(CONST_assault_gun, CONST_assault_knife, CONST_assault_other, CONST_assault_unarm) %>% rlang:::parse_exprs()))

raw_main2 %>% checkfunction(der_violent_crime, der_murder, der_rape, der_robbery, der_aggravated_assault)

raw_main2 %>% checkfunction(der_burglary, !!!(CONST_burglary %>% rlang:::parse_exprs()))
raw_main2 %>% checkfunction(der_larceny_theft, !!!(CONST_theft %>% rlang:::parse_exprs()))
raw_main2 %>% checkfunction(der_mvt, !!!(CONST_mvt %>% rlang:::parse_exprs()))
raw_main2 %>% checkfunction(der_property_crime, der_burglary, der_larceny_theft, der_mvt)

##########Create any additional variables#################################

raw_main3 <- raw_main2 %>%
  mutate(
    der_region = fcase(
      REGION_CODE_UNIV == 1, 1, # Northeast
      REGION_CODE_UNIV == 2, 2, # Midwest
      REGION_CODE_UNIV == 3, 3, # South
      REGION_CODE_UNIV == 4, 4 # West
  )
)

#QC the variable
raw_main3 %>% checkfunction(der_region, REGION_CODE_UNIV, REGION_NAME_UNIV)

################Add on the national weight variable and call it weight####################

raw_weight <- fread(paste0(CONST_INPUT_WEIGHT, "weights_jd_cal_srs_altcombs_col_srs.csv"))

#Need to create the national weight variable for single level estimation
raw_weight2 <- raw_weight %>%
  group_by(ORI_universe) %>%
  summarise(weight_JD = sum(JDWgt, na.rm=TRUE)) %>%
  ungroup() %>%
  #Create the raw weight variable
  mutate(
    weight = fcase(
      weight_JD > 0, 1,
      default = 0
    )
  )
  
#Check the recodes
raw_weight2 %>% checkfunction(weight, weight_JD)  

#See the dimension
dim(raw_weight)
dim(raw_weight2)

#Merge to the main file

#Do the merge between the weighting file and the universe file
#Merge by ORI first
tbd_good_1 <- raw_main3 %>%
  inner_join(raw_weight2, by=c("ORI_UNIV" = "ORI_universe")) %>%
  #Create the ori variable
  mutate(ori = ORI_UNIV)

tbd_bad_1 <- raw_main3 %>%
  anti_join(raw_weight2, by=c("ORI_UNIV" = "ORI_universe"))

#Merge by LEGACY ORI next
tbd_good_2 <- tbd_bad_1 %>%
  inner_join(raw_weight2, by=c("ORI" = "ORI_universe")) %>%
  #Create the ori variable
  mutate(ori = ORI)

tbd_bad_2 <- tbd_bad_1 %>%
  anti_join(raw_weight2, by=c("ORI" = "ORI_universe")) %>%
  #Create the ori variable
  mutate(ori = ORI)

#Stack the data together
raw_main4 <- bind_rows(tbd_good_1, tbd_good_2, tbd_bad_2)

#See the dimension
dim(raw_weight2)
dim(raw_main4)
dim(tbd_good_1)
dim(tbd_good_2)
dim(tbd_bad_2)


#Output dataset to share
raw_main4 %>% 
    write_csv(gzfile(paste0(CONST_OUTPUT,"/raw_recoded_SRS.csv.gz")), na="") 
