library("rmarkdown")
library("tidyverse")
library(readxl)
library(DT)
library(lubridate)
library(rjson)
library(reshape2)

source(here::here("tasks/logging.R"))

outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")
external_path <- Sys.getenv("EXTERNAL_FILE_PATH")
inputPipelineDir <- Sys.getenv("INPUT_PIPELINE_DIR")

input_folder <- sprintf("%s", inputPipelineDir)

file_locs <- fromJSON(file = sprintf("%s/external_file_locations.json", input_folder))

filepathout = paste0(outputPipelineDir, "/artifacts/")
input_files_folder <- paste0(inputPipelineDir, "/initial_tasks_output/")
queried_data_path = paste0(outputPipelineDir, "/initial_tasks_output/database_queries/")

if (! dir.exists(filepathout)) {
  dir.create(filepathout, recursive = TRUE)
}

DATA_YEAR <- Sys.getenv("DATA_YEAR")
print(DATA_YEAR)
########################
#read in nibrs_month data
months_raw <- read_csv(file=paste0(queried_data_path,"nibrs_month_agencies_",DATA_YEAR,".csv.gz")) %>% 
  distinct(.keep_all= TRUE) %>% mutate(month_num = as.double(month_num))

universe<- file.path(input_files_folder, paste0("ref_agency_", DATA_YEAR, ".csv")) %>%
  read_csv(guess_max=1e6)

########################
#Create reta-MM-like structure
months <- months_raw %>%
  mutate(variable="nibrs_month",
         one=1) %>%
  mutate(ORI=ori) %>%
  dcast(ORI~variable+month_num,value.var="one") %>%
  mutate_at(paste0("nibrs_month_",1:12),function(i){case_when(is.na(i)~0,
                                                              TRUE ~ i)}) %>%
  mutate(nibrs_month=paste0(nibrs_month_1,nibrs_month_2,nibrs_month_3,
                            "-",
                            nibrs_month_4,nibrs_month_5,nibrs_month_6,
                            "-",
                            nibrs_month_7,nibrs_month_8,nibrs_month_9,
                            "-",
                            nibrs_month_10,nibrs_month_11,nibrs_month_12)) %>%
  mutate(JAN_MM_FLAG=nibrs_month_1,
         FEB_MM_FLAG=nibrs_month_2,
         MAR_MM_FLAG=nibrs_month_3,
         APR_MM_FLAG=nibrs_month_4,
         MAY_MM_FLAG=nibrs_month_5,
         JUN_MM_FLAG=nibrs_month_6,
         JUL_MM_FLAG=nibrs_month_7,
         AUG_MM_FLAG=nibrs_month_8,
         SEP_MM_FLAG=nibrs_month_9,
         OCT_MM_FLAG=nibrs_month_10,
         NOV_MM_FLAG=nibrs_month_11,
         DEC_MM_FLAG=nibrs_month_12)  %>%
  select(ORI,
    JAN_MM_FLAG,
    FEB_MM_FLAG,
    MAR_MM_FLAG,
    APR_MM_FLAG,
    MAY_MM_FLAG,
    JUN_MM_FLAG,
    JUL_MM_FLAG,
    AUG_MM_FLAG,
    SEP_MM_FLAG,
    OCT_MM_FLAG,
    NOV_MM_FLAG,
    DEC_MM_FLAG,
    nibrs_month) %>%
  mutate(in_nibrs_month=1)

########################
#Merge onto main dataframe (final_1) by AGENCY_ID
#Merge on the extra information from the NIBRS database for help to identify agencies
maindata_1 <- inner_join(universe, months, by = c("ORI"="ORI"))
log_dim(maindata_1)

#Get the unmatched ones
maindata_1_anti_join <- universe %>%
  anti_join(months, by = c("ORI"="ORI")) %>%
  #Since not every LEA in nibrs_month, set all LEAs not in table as if didn't respond
  mutate(nibrs_month="000-000-000-000",
         in_nibrs_month=0,
         JAN_MM_FLAG=0,
         FEB_MM_FLAG=0,
         MAR_MM_FLAG=0,
         APR_MM_FLAG=0,
         MAY_MM_FLAG=0,
         JUN_MM_FLAG=0,
         JUL_MM_FLAG=0,
         AUG_MM_FLAG=0,
         SEP_MM_FLAG=0,
         OCT_MM_FLAG=0,
         NOV_MM_FLAG=0,
         DEC_MM_FLAG=0
       )
log_dim(maindata_1_anti_join)



#Stack all the datasets together
final_1 <- bind_rows(maindata_1, maindata_1_anti_join)
log_dim(final_1)
log_dim(months)

#Delete the dataset
rm(list=c("maindata_1", "maindata_1_anti_join" ))


final_1 <- final_1 %>% mutate(nTimes=month(as_date(NIBRS_START_DATE,format="%d-%B-%y"))-1L) %>%
    mutate(nTimes=ifelse(is.na(nTimes),0, nTimes)) %>%
    mutate(nibrs_month_adj=case_when(year(as_date(NIBRS_START_DATE,format="%d-%B-%y"))==DATA_YEAR ~  str_remove_all(nibrs_month,"-") %>%
                           str_replace(pattern=paste0("^.{",nTimes,"}"),replacement=str_dup("0",times=nTimes)),
                           year(as_date(NIBRS_START_DATE,format="%d-%B-%y")) > DATA_YEAR ~ str_remove_all(nibrs_month,"-") %>%
                             str_replace(pattern=paste0("^.{",12,"}"),
                             replacement=str_dup("0",times=12)),
                             is.na(NIBRS_START_DATE) ~ str_dup("0",times=12),
                             TRUE ~ nibrs_month %>% str_remove_all("-"))
                           )

#New code to use the adjusted MM flags
final_2 <- final_1 %>%
  #Drop the current MM flags
  select(-ends_with("_MM_FLAG")) %>%
  mutate(JAN_MM_FLAG = substr(nibrs_month_adj, 1, 1),
         FEB_MM_FLAG = substr(nibrs_month_adj, 2, 2),
         MAR_MM_FLAG = substr(nibrs_month_adj, 3, 3),
         APR_MM_FLAG = substr(nibrs_month_adj, 4, 4),
         MAY_MM_FLAG = substr(nibrs_month_adj, 5, 5),
         JUN_MM_FLAG = substr(nibrs_month_adj, 6, 6),
         JUL_MM_FLAG = substr(nibrs_month_adj, 7, 7),
         AUG_MM_FLAG = substr(nibrs_month_adj, 8, 8),
         SEP_MM_FLAG = substr(nibrs_month_adj, 9, 9),
         OCT_MM_FLAG = substr(nibrs_month_adj, 10, 10),
         NOV_MM_FLAG = substr(nibrs_month_adj, 11, 11),
         DEC_MM_FLAG = substr(nibrs_month_adj, 12, 12)
)

#Get list of RETA-MM variables
CONST_RETA_MM_VARS <- c(
  "STATE_NAME",
  "ORI",
  "UCR_AGENCY_NAME",
  "AGENCY_STATUS",
  "PUBLISHABLE_FLAG",
  "COVERED_FLAG",
  "DORMANT_FLAG",
  "AGENCY_TYPE_NAME",
  "POPULATION",
  "PARENT_POP_GROUP_CODE",
  "DATA_YEAR",
  "JAN_MM_FLAG",
  "FEB_MM_FLAG",
  "MAR_MM_FLAG",
  "APR_MM_FLAG",
  "MAY_MM_FLAG",
  "JUN_MM_FLAG",
  "JUL_MM_FLAG",
  "AUG_MM_FLAG",
  "SEP_MM_FLAG",
  "OCT_MM_FLAG",
  "NOV_MM_FLAG",
  "DEC_MM_FLAG") %>% rlang:::parse_exprs()

#Need to capitalize all the variables to be consistent with RETA-MM file
colnames(final_2) <- toupper(colnames(final_2))


final_2 %>%
  select(!!!CONST_RETA_MM_VARS) %>%
  mutate(AGENCY_STATUS = case_when(
                         toupper(trimws(AGENCY_STATUS)) == "A" ~ "Active",
#Confirmed in previous checks that in the Universe file, dormant agencies have blanks for AGENCY_STATUS in Reta-MM
                         toupper(trimws(AGENCY_STATUS)) == "D" ~ NA_character_,
                         toupper(trimws(AGENCY_STATUS)) == "F" ~ "Federal",
                         toupper(trimws(AGENCY_STATUS)) == "L" ~ "LEOKA")

         ) %>%
		 write_csv(file=file.path(filepathout, paste0("missing_months_",DATA_YEAR,".csv")),  na = "", append=FALSE)
