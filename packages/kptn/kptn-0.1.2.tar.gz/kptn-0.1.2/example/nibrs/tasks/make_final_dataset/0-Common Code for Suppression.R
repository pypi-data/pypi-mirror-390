library(tidyverse)
library(DT)
library(rjson)
library(data.table)


#Read in the common functions to be used in R
source(here::here("tasks/logging.R"))
source(paste0("../impute_items/0-Common_functions_for_imputation.R"))

#input/output directories for pipeline artifacts
outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")
inputPipelineDir <- Sys.getenv("INPUT_PIPELINE_DIR")
external_path <- Sys.getenv("EXTERNAL_FILE_PATH")

filepathin_initial = paste0(inputPipelineDir, "/initial_tasks_output/")

year <- Sys.getenv("DATA_YEAR")
PERMUTATION_NAME = Sys.getenv("PERMUTATION_NAME")
TABLE_NAME = Sys.getenv("TABLE_NAME")
TOP_FOLDER = Sys.getenv("TOP_FOLDER")
MID_FOLDER = Sys.getenv("MID_FOLDER")

create_if_doesnt_exist <- function(path){
  if (! dir.exists(path)){
  dir.create(path, recursive = TRUE)
  }
  return(path)
}

filepathout = create_if_doesnt_exist(paste0(outputPipelineDir, "/final-estimates/"))
filepathout_Momentum_Rule = create_if_doesnt_exist(paste0(filepathout,"Momentum_Rule/"))
filepathout_Indicator_Tables_flag_non_zero_estimates_with_no_prb = create_if_doesnt_exist(paste0(filepathout,"Indicator_Tables_flag_non_0_est_no_prb/"))
filepathout_for_validation = create_if_doesnt_exist(paste0(outputPipelineDir,"/validation_inputs/der_variable_name/"))

filepathout_Indicator_Tables_no_supp = create_if_doesnt_exist(paste0(filepathout,"Indicator_Tables_no_supp/",TOP_FOLDER,"/",MID_FOLDER,"/"))
filepathout_Indicator_Tables = create_if_doesnt_exist(paste0(filepathout,"Indicator_Tables/",TOP_FOLDER,"/",MID_FOLDER,"/"))

file_locs <- fromJSON(file = sprintf("%s/external_file_locations.json", inputPipelineDir))

estimate_paths_after_variance = paste0(outputPipelineDir, "/indicator_table_estimates_after_variance/")
estimate_path_skip_variance   = paste0(outputPipelineDir, "/variance_skip/")																			

read_csv1 <- partial(read_csv, guess_max = 1000000) #For now, read thru the 1st 1,000,000 rows to determine variable type
write.csv0 <- partial(write.csv, row.names = FALSE, na ="0")
write.csv1 <- partial(write.csv, row.names = FALSE, na ="")


#################################Set the DER_NA_CODE variables##############################################
DER_NA_CODE = -9
DER_NA_CODE_STRING = "-9"

#Demographic Tables
CONST_DEMOGRAPHIC_UPCASE_TABLES <- c(
  "3A",
  "3AUNCLEAR",
  "3ACLEAR",
  "3B",
  "3BUNCLEAR",
  "3BCLEAR",
  "4A",
  "4B",
  "5A",
  "5B",
  "DM7",
  "DM9",
  "DM10",
  "GV2A"
)

#Geographic permutations
CONST_MAIN_PERMUTATION_MAX <- 709

CONST_NATIONAL_PERM     <- c(1)
CONST_NATIONAL_AGN_PERM <- c(2:11)
CONST_REGIONAL_PERM     <- c(12:55)
CONST_STATE_PERM        <- c(56:106)
CONST_UNIV_PERM         <- c(107)
CONST_TRIBAL_PERM       <- c(108)
CONST_MSA_PERM          <- c(109:492, 638:709)
CONST_JD_PERM           <- c(493:582)
CONST_FO_PERM           <- c(583:637)

#Demographic permutations
CONST_DEMO_PERMUTATION_MAX <- 260

CONST_DEMO_AGE <- c(
  
  1000, #Age: Under 5
  2000, #Age: 5-14
  3000, #Age:15
  4000, #Age:16
  5000, #Age:17
  6000, #Age: 18-24
  7000, #Age: 25-34
  8000, #Age: 35-64
  9000, #Age: 65+
  17000, #Age: 18+
  18000, #Age: Under 18
  19000, #Age: Under 15
  21000, #Age: Under 12
  22000, #Age: 12-17
  23000, #Age: 12-14
  24000, #Age: 15-17
  25000, #Age: 12 or older
  27000, #Age: 18-64
  
  136000, #Age: 5-11
  139000 #Age: 12-14
  
  
)
CONST_DEMO_SEX <- c(
  
  10000, #Sex: Male
  11000 #Sex: Female
  
)


CONST_DEMO_RACE <- c(
  
  12000, #Race: White
  13000, #Race: Black
  14000, #Race: American Indian or Alaska Native
  15000, #Race: Asian
  16000, #Race: Native Hawaiian or Other Pacific Islander
  20000, #Race: American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander
  26000,  #Race: Asian or Native Hawaiian or Other Pacific Islander
  
  142000, #Race: American Indian or Alaska Native and Native Hawaiian or Other Pacific Islander
  
  145000, #Race: Hispanic
  146000, #Race: Non-Hispanic
  147000, #Race: Non-Hispanic White
  148000, #Race: Non-Hispanic Black
  149000, #Race: Non-Hispanic American Indian or Alaska Native
  150000, #Race: Non-Hispanic Asian
  151000, #Race: Non-Hispanic Native Hawaiian or Other Pacific Islander
  152000, #Race: Non-Hispanic American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander
  153000, #Race: Non-Hispanic Asian or Native Hawaiian or Other Pacific Islander
  258000 #Race: Non-Hispanic American Indian or Alaska Native and Native Hawaiian or Other Pacific Islander
  
  
  
)
CONST_DEMO_SEX_RACE <- c(
  
  28000, #Sex and Race: Male and White
  29000, #Sex and Race: Male and Black
  30000, #Sex and Race: Male and American Indian or Alaska Native
  31000, #Sex and Race: Male and Asian
  32000, #Sex and Race: Male and Native Hawaiian or Other Pacific Islander
  33000, #Sex and Race: Male and American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander
  34000, #Sex and Race: Male and Asian or Native Hawaiian or Other Pacific Islander
  35000, #Sex and Race: Female and White
  36000, #Sex and Race: Female and Black
  37000, #Sex and Race: Female and American Indian or Alaska Native
  38000, #Sex and Race: Female and Asian
  39000, #Sex and Race: Female and Native Hawaiian or Other Pacific Islander
  40000, #Sex and Race: Female and American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander
  41000, #Sex and Race: Female and Asian or Native Hawaiian or Other Pacific Islander

  143000, #Sex and Race: Male and American Indian or Alaska Native and Native Hawaiian or Other Pacific Islander
  144000, #Sex and Race: Female and American Indian or Alaska Native and Native Hawaiian or Other Pacific Islander
  
  154000, #Sex and Race: Male and Hispanic
  155000, #Sex and Race: Male and Non-Hispanic White
  156000, #Sex and Race: Male and Non-Hispanic Black
  157000, #Sex and Race: Male and Non-Hispanic American Indian or Alaska Native
  158000, #Sex and Race: Male and Non-Hispanic Asian
  159000, #Sex and Race: Male and Non-Hispanic Native Hawaiian or Other Pacific Islander
  160000, #Sex and Race: Male and Non-Hispanic American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander
  161000, #Sex and Race: Male and Non-Hispanic Asian or Native Hawaiian or Other Pacific Islander
  162000, #Sex and Race: Female and Hispanic
  163000, #Sex and Race: Female and Non-Hispanic White
  164000, #Sex and Race: Female and Non-Hispanic Black
  165000, #Sex and Race: Female and Non-Hispanic American Indian or Alaska Native
  166000, #Sex and Race: Female and Non-Hispanic Asian
  167000, #Sex and Race: Female and Non-Hispanic Native Hawaiian or Other Pacific Islander
  168000, #Sex and Race: Female and Non-Hispanic American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander
  169000, #Sex and Race: Female and Non-Hispanic Asian or Native Hawaiian or Other Pacific Islander
  259000, #Sex and Race: Male and Non-Hispanic American Indian or Alaska Native and Native Hawaiian or Other Pacific Islander
  260000 #Sex and Race: Female and Non-Hispanic American Indian or Alaska Native and Native Hawaiian or Other Pacific Islander
  
  
)

CONST_DEMO_SEX_AGE <- c( 
  84000, #Sex and Age: Male and 18-24
  85000, #Sex and Age: Male and 25-34
  86000, #Sex and Age: Male and 35-64
  87000, #Sex and Age: Male and 65+
  88000, #Sex and Age: Male and 18+
  89000, #Sex and Age: Male and Under 18
  90000, #Sex and Age: Male and Under 12
  91000, #Sex and Age: Male and 12-17
  92000, #Sex and Age: Male and 12-14
  93000, #Sex and Age: Male and 15-17
  94000, #Sex and Age: Male and 12 or older
  95000, #Sex and Age: Female and 18-24
  96000, #Sex and Age: Female and 25-34
  97000, #Sex and Age: Female and 35-64
  98000, #Sex and Age: Female and 65+
  99000, #Sex and Age: Female and 18+
  100000, #Sex and Age: Female and Under 18
  101000, #Sex and Age: Female and Under 12
  102000, #Sex and Age: Female and 12-17
  103000, #Sex and Age: Female and 12-14
  104000, #Sex and Age: Female and 15-17
  105000, #Sex and Age: Female and 12 or older
  
  137000, #Sex and Age: Male and 5-11
  138000, #Sex and Age: Female and 5-11
  140000, #Sex and Age: Male and 12-14
  141000 #Sex and Age: Female and 12-14
  
  
)


CONST_DEMO_SEX_RACE_AGE <- c(
  
  42000, #Sex and Race and Age: Male and White Under 12
  43000, #Sex and Race and Age: Male and Black Under 12
  44000, #Sex and Race and Age: Male and American Indian or Alaska Native Under 12
  45000, #Sex and Race and Age: Male and Asian Under 12
  46000, #Sex and Race and Age: Male and Native Hawaiian or Other Pacific Islander Under 12
  47000, #Sex and Race and Age: Male and American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander Under 12
  48000, #Sex and Race and Age: Male and Asian or Native Hawaiian or Other Pacific Islander Under 12
  49000, #Sex and Race and Age: Female and White Under 12
  50000, #Sex and Race and Age: Female and Black Under 12
  51000, #Sex and Race and Age: Female and American Indian or Alaska Native Under 12
  52000, #Sex and Race and Age: Female and Asian Under 12
  53000, #Sex and Race and Age: Female and Native Hawaiian or Other Pacific Islander Under 12
  54000, #Sex and Race and Age: Female and American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander Under 12
  55000, #Sex and Race and Age: Female and Asian or Native Hawaiian or Other Pacific Islander Under 12
  56000, #Sex and Race and Age: Male and White 12-17
  57000, #Sex and Race and Age: Male and Black 12-17
  58000, #Sex and Race and Age: Male and American Indian or Alaska Native 12-17
  59000, #Sex and Race and Age: Male and Asian 12-17
  60000, #Sex and Race and Age: Male and Native Hawaiian or Other Pacific Islander 12-17
  61000, #Sex and Race and Age: Male and American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander 12-17
  62000, #Sex and Race and Age: Male and Asian or Native Hawaiian or Other Pacific Islander 12-17
  63000, #Sex and Race and Age: Female and White 12-17
  64000, #Sex and Race and Age: Female and Black 12-17
  65000, #Sex and Race and Age: Female and American Indian or Alaska Native 12-17
  66000, #Sex and Race and Age: Female and Asian 12-17
  67000, #Sex and Race and Age: Female and Native Hawaiian or Other Pacific Islander 12-17
  68000, #Sex and Race and Age: Female and American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander 12-17
  69000, #Sex and Race and Age: Female and Asian or Native Hawaiian or Other Pacific Islander 12-17
  70000, #Sex and Race and Age: Male and White 18+
  71000, #Sex and Race and Age: Male and Black 18+
  72000, #Sex and Race and Age: Male and American Indian or Alaska Native 18+
  73000, #Sex and Race and Age: Male and Asian 18+
  74000, #Sex and Race and Age: Male and Native Hawaiian or Other Pacific Islander 18+
  75000, #Sex and Race and Age: Male and American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander 18+
  76000, #Sex and Race and Age: Male and Asian or Native Hawaiian or Other Pacific Islander 18+
  77000, #Sex and Race and Age: Female and White 18+
  78000, #Sex and Race and Age: Female and Black 18+
  79000, #Sex and Race and Age: Female and American Indian or Alaska Native 18+
  80000, #Sex and Race and Age: Female and Asian 18+
  81000, #Sex and Race and Age: Female and Native Hawaiian or Other Pacific Islander 18+
  82000, #Sex and Race and Age: Female and American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander 18+
  83000, #Sex and Race and Age: Female and Asian or Native Hawaiian or Other Pacific Islander 18+
  
  106000, #Sex and Race and Age: Male and White and 18-24
  107000, #Sex and Race and Age: Male and White and 25-34
  108000, #Sex and Race and Age: Male and White and 35-64
  109000, #Sex and Race and Age: Male and White and 65+
  110000, #Sex and Race and Age: Male and White and Under 18
  111000, #Sex and Race and Age: Male and Black and 18-24
  112000, #Sex and Race and Age: Male and Black and 25-34
  113000, #Sex and Race and Age: Male and Black and 35-64
  114000, #Sex and Race and Age: Male and Black and 65+
  115000, #Sex and Race and Age: Male and Black and Under 18
  116000, #Sex and Race and Age: Male and American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander and 18-24
  117000, #Sex and Race and Age: Male and American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander and 25-34
  118000, #Sex and Race and Age: Male and American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander and 35-64
  119000, #Sex and Race and Age: Male and American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander and 65+
  120000, #Sex and Race and Age: Male and American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander and Under 18
  121000, #Sex and Race and Age: Female and White and 18-24
  122000, #Sex and Race and Age: Female and White and 25-34
  123000, #Sex and Race and Age: Female and White and 35-64
  124000, #Sex and Race and Age: Female and White and 65+
  125000, #Sex and Race and Age: Female and White and Under 18
  126000, #Sex and Race and Age: Female and Black and 18-24
  127000, #Sex and Race and Age: Female and Black and 25-34
  128000, #Sex and Race and Age: Female and Black and 35-64
  129000, #Sex and Race and Age: Female and Black and 65+
  130000, #Sex and Race and Age: Female and Black and Under 18
  131000, #Sex and Race and Age: Female and American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander and 18-24
  132000, #Sex and Race and Age: Female and American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander and 25-34
  133000, #Sex and Race and Age: Female and American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander and 35-64
  134000, #Sex and Race and Age: Female and American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander and 65+
  135000, #Sex and Race and Age: Female and American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander and Under 18
  
  170000, #Sex and Race and Age: Male and Hispanic and Under 12
  171000, #Sex and Race and Age: Male and Non-Hispanic White and Under 12
  172000, #Sex and Race and Age: Male and Non-Hispanic Black and Under 12
  173000, #Sex and Race and Age: Male and Non-Hispanic American Indian or Alaska Native and Under 12
  174000, #Sex and Race and Age: Male and Non-Hispanic Asian and Under 12
  175000, #Sex and Race and Age: Male and Non-Hispanic Native Hawaiian or Other Pacific Islander and Under 12
  176000, #Sex and Race and Age: Male and Non-Hispanic American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander and Under 12
  177000, #Sex and Race and Age: Male and Non-Hispanic Asian or Native Hawaiian or Other Pacific Islander and Under 12
  178000, #Sex and Race and Age: Female and Hispanic and Under 12
  179000, #Sex and Race and Age: Female and Non-Hispanic White and Under 12
  180000, #Sex and Race and Age: Female and Non-Hispanic Black and Under 12
  181000, #Sex and Race and Age: Female and Non-Hispanic American Indian or Alaska Native and Under 12
  182000, #Sex and Race and Age: Female and Non-Hispanic Asian and Under 12
  183000, #Sex and Race and Age: Female and Non-Hispanic Native Hawaiian or Other Pacific Islander and Under 12
  184000, #Sex and Race and Age: Female and Non-Hispanic American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander and Under 12
  185000, #Sex and Race and Age: Female and Non-Hispanic Asian or Native Hawaiian or Other Pacific Islander and Under 12
  186000, #Sex and Race and Age: Male and Hispanic and 12-17
  187000, #Sex and Race and Age: Male and Non-Hispanic White and 12-17
  188000, #Sex and Race and Age: Male and Non-Hispanic Black and 12-17
  189000, #Sex and Race and Age: Male and Non-Hispanic American Indian or Alaska Native and 12-17
  190000, #Sex and Race and Age: Male and Non-Hispanic Asian and 12-17
  191000, #Sex and Race and Age: Male and Non-Hispanic Native Hawaiian or Other Pacific Islander and 12-17
  192000, #Sex and Race and Age: Male and Non-Hispanic American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander and 12-17
  193000, #Sex and Race and Age: Male and Non-Hispanic Asian or Native Hawaiian or Other Pacific Islander and 12-17
  194000, #Sex and Race and Age: Female and Hispanic and 12-17
  195000, #Sex and Race and Age: Female and Non-Hispanic White and 12-17
  196000, #Sex and Race and Age: Female and Non-Hispanic Black and 12-17
  197000, #Sex and Race and Age: Female and Non-Hispanic American Indian or Alaska Native and 12-17
  198000, #Sex and Race and Age: Female and Non-Hispanic Asian and 12-17
  199000, #Sex and Race and Age: Female and Non-Hispanic Native Hawaiian or Other Pacific Islander and 12-17
  200000, #Sex and Race and Age: Female and Non-Hispanic American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander and 12-17
  201000, #Sex and Race and Age: Female and Non-Hispanic Asian or Native Hawaiian or Other Pacific Islander and 12-17
  202000, #Sex and Race and Age: Male and Hispanic and 18+
  203000, #Sex and Race and Age: Male and Non-Hispanic White and 18+
  204000, #Sex and Race and Age: Male and Non-Hispanic Black and 18+
  205000, #Sex and Race and Age: Male and Non-Hispanic American Indian or Alaska Native and 18+
  206000, #Sex and Race and Age: Male and Non-Hispanic Asian and 18+
  207000, #Sex and Race and Age: Male and Non-Hispanic Native Hawaiian or Other Pacific Islander and 18+
  208000, #Sex and Race and Age: Male and Non-Hispanic American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander and 18+
  209000, #Sex and Race and Age: Male and Non-Hispanic Asian or Native Hawaiian or Other Pacific Islander and 18+
  210000, #Sex and Race and Age: Female and Hispanic and 18+
  211000, #Sex and Race and Age: Female and Non-Hispanic White and 18+
  212000, #Sex and Race and Age: Female and Non-Hispanic Black and 18+
  213000, #Sex and Race and Age: Female and Non-Hispanic American Indian or Alaska Native and 18+
  214000, #Sex and Race and Age: Female and Non-Hispanic Asian and 18+
  215000, #Sex and Race and Age: Female and Non-Hispanic Native Hawaiian or Other Pacific Islander and 18+
  216000, #Sex and Race and Age: Female and Non-Hispanic American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander and 18+
  217000, #Sex and Race and Age: Female and Non-Hispanic Asian or Native Hawaiian or Other Pacific Islander and 18+
  218000, #Sex and Race and Age: Male and Hispanic and 18-24
  219000, #Sex and Race and Age: Male and Hispanic and 25-34
  220000, #Sex and Race and Age: Male and Hispanic and 35-64
  221000, #Sex and Race and Age: Male and Hispanic and 65+
  222000, #Sex and Race and Age: Male and Hispanic and Under 18
  223000, #Sex and Race and Age: Male and Non-Hispanic White and 18-24
  224000, #Sex and Race and Age: Male and Non-Hispanic White and 25-34
  225000, #Sex and Race and Age: Male and Non-Hispanic White and 35-64
  226000, #Sex and Race and Age: Male and Non-Hispanic White and 65+
  227000, #Sex and Race and Age: Male and Non-Hispanic White and Under 18
  228000, #Sex and Race and Age: Male and Non-Hispanic Black and 18-24
  229000, #Sex and Race and Age: Male and Non-Hispanic Black and 25-34
  230000, #Sex and Race and Age: Male and Non-Hispanic Black and 35-64
  231000, #Sex and Race and Age: Male and Non-Hispanic Black and 65+
  232000, #Sex and Race and Age: Male and Non-Hispanic Black and Under 18
  233000, #Sex and Race and Age: Male and Non-Hispanic American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander and 18-24
  234000, #Sex and Race and Age: Male and Non-Hispanic American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander and 25-34
  235000, #Sex and Race and Age: Male and Non-Hispanic American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander and 35-64
  236000, #Sex and Race and Age: Male and Non-Hispanic American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander and 65+
  237000, #Sex and Race and Age: Male and Non-Hispanic American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander and Under 18
  238000, #Sex and Race and Age: Female and Hispanic and 18-24
  239000, #Sex and Race and Age: Female and Hispanic and 25-34
  240000, #Sex and Race and Age: Female and Hispanic and 35-64
  241000, #Sex and Race and Age: Female and Hispanic and 65+
  242000, #Sex and Race and Age: Female and Hispanic and Under 18
  243000, #Sex and Race and Age: Female and Non-Hispanic White and 18-24
  244000, #Sex and Race and Age: Female and Non-Hispanic White and 25-34
  245000, #Sex and Race and Age: Female and Non-Hispanic White and 35-64
  246000, #Sex and Race and Age: Female and Non-Hispanic White and 65+
  247000, #Sex and Race and Age: Female and Non-Hispanic White and Under 18
  248000, #Sex and Race and Age: Female and Non-Hispanic Black and 18-24
  249000, #Sex and Race and Age: Female and Non-Hispanic Black and 25-34
  250000, #Sex and Race and Age: Female and Non-Hispanic Black and 35-64
  251000, #Sex and Race and Age: Female and Non-Hispanic Black and 65+
  252000, #Sex and Race and Age: Female and Non-Hispanic Black and Under 18
  253000, #Sex and Race and Age: Female and Non-Hispanic American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander and 18-24
  254000, #Sex and Race and Age: Female and Non-Hispanic American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander and 25-34
  255000, #Sex and Race and Age: Female and Non-Hispanic American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander and 35-64
  256000, #Sex and Race and Age: Female and Non-Hispanic American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander and 65+
  257000 #Sex and Race and Age: Female and Non-Hispanic American Indian or Alaska Native, Asian, and Native Hawaiian or Other Pacific Islander and Under 18
  
  
  
)

#Create the objects to hold the demographic information
CONST_ALL_AGE <- c(
  CONST_DEMO_AGE,
  CONST_DEMO_SEX_AGE,			
  CONST_DEMO_SEX_RACE_AGE
)

CONST_ALL_SEX <-  c(
  CONST_DEMO_SEX,
  CONST_DEMO_SEX_RACE,
  CONST_DEMO_SEX_AGE,
  CONST_DEMO_SEX_RACE_AGE
)

CONST_ALL_RACE <- c(
  CONST_DEMO_RACE,
  CONST_DEMO_SEX_RACE,
  CONST_DEMO_SEX_RACE_AGE
)

#For the momenturm rule, need to keep certain tables
CONST_MOMENTUM_RULE_TABLES  <- c(
  "1a",
  "1b",
  "1c",
  "2a",
  "2b",
  "2c",
  "3a",
  "3b",
  "3c",
  "4a",
  "4b",
  "5a",
  "5b"
)  

#Momentum Rule Tables Upcase
der_main_tables <- c("TABLE1A-PERSON INCIDENTS",
                     "TABLE1B-PROPERTY INCIDENTS",
                     "TABLE1C-SOCIETY INCIDENTS",
                     "TABLE2A-PERSON OFFENSES",
                     "TABLE2B-PROPERTY OFFENSES",
                     "TABLE2C-SOCIETY OFFENSES",
                     "TABLE3A-PERSON VICTIMS",
                     "TABLE3B-PERSON VICTIMS-RATES",
                     "TABLE3C-NON-PERSON VICTIMS",
                     "TABLE4A-ARRESTEES",
                     "TABLE4B-ARRESTEES-RATES",
                     "TABLE5A-ARRESTEES ARREST CODE",
                     "TABLE5B-ARRESTEES-RATES ARREST CODE"
)


CONST_DEMO_PERMUTATION <- c(1:CONST_DEMO_PERMUTATION_MAX)*1000

log_info(paste0("RUNNING 10000 - Make Final Database ",PERMUTATION_NAME))

#Example of string pattern 149_129_TableGV2a_Variance.Rmd.csv
#(Permutation Number)_Variance_Program.Rmd.csv                          
CONST_SKIP_VARIANCE_STRING <- "(\\d+)_\\d+_Table(\\w+)_Variance.R.csv"

#Check to see if the permutation is skip
raw_check_permutation_skip <- list.files(paste0(estimate_path_skip_variance), pattern = CONST_SKIP_VARIANCE_STRING) %>%
  as_tibble() %>%
  #Create variables to identify which files to keep
  mutate(
    der_permutation_number = str_match(string=value, pattern=CONST_SKIP_VARIANCE_STRING)[,2] %>% as.numeric(),
    der_file_table         = str_match(string=value, pattern=CONST_SKIP_VARIANCE_STRING)[,3] %>% as.character()
  ) %>%
  mutate(
    der_pn_file_table_detect = fcase(
      der_permutation_number %in% c(PERMUTATION_NAME) &
      der_file_table %in% c(TABLE_NAME) , 1,
      default = 0)
  )

#Check the recodes
#raw_check_permutation_skip %>% checkfunction(der_permutation_number, value)
#raw_check_permutation_skip %>% checkfunction(der_file_table, value)

# raw_check_permutation_skip %>% checkfunction(der_pn_file_table_detect, der_permutation_number, der_file_table)  

#Subset to any records where there is a match
raw_check_permutation_skip2 <- raw_check_permutation_skip %>%
  filter(der_pn_file_table_detect == 1) 
  
#Quit the program if permutation number and table are detected in the variance skip folder
if(nrow(raw_check_permutation_skip2) > 0){
  print("Permutation number and table detected in the variance skip folder. Quitting early.")
  quit(save="no")
}

#Delete the variables used for variance skip
rm(CONST_SKIP_VARIANCE_STRING, raw_check_permutation_skip, raw_check_permutation_skip2)

#Get all of the csv files
if(as.integer(PERMUTATION_NAME)==108)
{
  # don't grab any demographic permutations for permutation 108
  raw_list_files <- list.files(path=estimate_paths_after_variance, pattern=paste0("\\_",108,"\\.csv"))
} else {
  raw_list_files <- c()
  for(i in c(0,CONST_DEMO_PERMUTATION)){
    temp_list <- list.files(path=estimate_paths_after_variance, pattern=paste0("\\_",i + as.integer(PERMUTATION_NAME),"\\.csv"))
    raw_list_files <- c(raw_list_files,temp_list)
  }
}
print(raw_list_files)
if(length(raw_list_files)==0){
  print("No files for this permutation. Quitting early.")
  quit(save="no")
}


#Print out a datatable
raw_list_files %>%
  as_tibble() %>%
  datatable()

#Define the variable type

raw_files_column_type <- cols(
  #X1 = col_double(),
  full_table = col_character(),
  table = col_character(),
  section = col_double(),
  row = col_double(),
  estimate_domain = col_character(),
  column = col_double(),
  indicator_name = col_character(),
  population_estimate = col_double(),
  estimate_type = col_character(),
  estimate = col_double(),
  estimate_geographic_location = col_character(),
  analysis_weight_name = col_character(),
  estimate_type_num = col_double(),
  estimate_type_detail_percentage = col_character(),
  estimate_type_detail_rate = col_character(),
  POP_TOTAL = col_double(),
  POP_TOTAL_UNWEIGHTED = col_double(),
  variable_name = col_character(),
  der_cleared_cells = col_double(),
  estimate_standard_error = col_double(),
  estimate_prb = col_double(),
  estimate_bias = col_double(),
  estimate_rmse = col_double(),
  estimate_upper_bound = col_double(),
  estimate_lower_bound = col_double(),
  relative_standard_error = col_double(),
  relative_rmse = col_double(),
  PRB_ACTUAL = col_double(),
  tbd_estimate = col_double(),
  estimate_unweighted = col_double(),
  population_estimate_unweighted = col_double(),
  unweighted_counts = col_double(),
  agency_counts = col_double()
)


#Create the der_variable_name variable, since some variables are not created if the estimate is zero (i.e. no counts)
create_variables_for_id  <- function(indata){

  returndata <- indata %>%
    mutate(der_variable_name = paste0("t_",table,"_", section, "_", row, "_", column), 
           der_demographic_main_number = (PERMUTATION_NUMBER %/% 1000)*1000,
           der_geographic_main_number = (PERMUTATION_NUMBER %% 1000)
    )

  return(returndata)

}

#Create variables for suppression
create_variables_suppression1 <- function(indata){
  
  returndata <- indata %>%
    mutate(
      der_na_agency_counts = fcase(
        is.na(agency_counts),  1,
        default = 0),
      
      der_estimate_na_code = fcase(
        estimate == DER_NA_CODE ,  1,
        default = 0),
      
      #Create new variable to exclude the estimate that would not be in consideration for suppression
      der_elig_suppression = fcase(
        
        #Want variable to be created in the LEA file (i.e. the denominator is not missing - !is.na(agency_counts)) and
        der_na_agency_counts == 0 &
          #Want the estimate that is not grey out (i.e. estimate != DER_NA_CODE) and
          der_estimate_na_code == 0,  1,
        default = 0)	      
      
    )
  
  return(returndata)
  
}

#Create additional variables for suppression
create_variables_suppression2 <- function(indata){
  returndata <- indata %>%
    mutate(
      
      ##########20230209 Add on new recodes for new suppression rule##############################
      #RMSE > 0.3
      der_rrmse_gt_30 = fcase(relative_rmse  > 0.30 , 1,
                              der_estimate_na_code == 0 , 0),
      
      der_estimate_0 = fcase(
        estimate ==0, 1,
        der_estimate_na_code == 0, 0),
      
      der_estimate_se_0 = fcase(
        estimate_standard_error ==0, 1,
        der_estimate_na_code == 0, 0),
      
      der_estimate_0_se_0 = fcase(
        der_estimate_0 == 1 | der_estimate_se_0 ==1, 1,
        der_estimate_na_code == 0, 0),
      
      #der_na_estimate_prb
      der_na_estimate_prb = fcase(
        is.na(estimate_prb),  1,
        estimate_prb != DER_NA_CODE,  0),
      
      #Set up the rmse criteria
      der_rrmse_30 = fcase(
        relative_rmse > .30,  1,
        !is.na(relative_rmse) & relative_rmse != DER_NA_CODE ,  0),
      # der_rrmse_50 = fcase(
      #   relative_rmse > .50,  1,
      #   !is.na(relative_rmse) & relative_rmse != DER_NA_CODE ,  0),
      
      #Set up the unweighted agency count criteria
      der_agency_count_10 = fcase(
        agency_counts <= 10 & agency_counts != DER_NA_CODE,  1,
        !is.na(agency_counts) & agency_counts != DER_NA_CODE,  0),
      
      # der_agency_count_3 = fcase(
      #   agency_counts <= 3 & agency_counts != DER_NA_CODE,  1,
      #   !is.na(agency_counts) & agency_counts != DER_NA_CODE,  0),
      
      #Create the 4 indicator variables
      # der_rrmse_30_agency_10 = fcase(
      #   #The criteria
      #   der_elig_suppression == 1 & (der_rrmse_30 == 1 | der_agency_count_10 == 1),  1,
      #
      #   #Keep in denominator if it is eligible
      #   der_elig_suppression == 1,  0,
      #
      #   #Otherwise missing
      #   default = NA_real_
      # ),
      
      # der_rrmse_30_agency_3 = fcase(
      #   #The criteria
      #   der_elig_suppression == 1 & (der_rrmse_30 == 1 | der_agency_count_3 == 1),  1,
      #
      #   #Keep in denominator if it is eligible
      #   der_elig_suppression == 1,  0,
      #
      #   #Otherwise missing
      #   default = NA_real_
      # ),
      
      # der_rrmse_50_agency_10 = fcase(
      #   #The criteria
      #   der_elig_suppression == 1 & (der_rrmse_50 == 1 | der_agency_count_10 == 1),  1,
      #
      #   #Keep in denominator if it is eligible
      #   der_elig_suppression == 1,  0,
      #
      #   #Otherwise missing
      #   default = NA_real_
      # ),
      
      # der_rrmse_50_agency_3 = fcase(
      #   #The criteria
      #   der_elig_suppression == 1 & (der_rrmse_50 == 1 | der_agency_count_3 == 1),  1,
      #
      #   #Keep in denominator if it is eligible
      #   der_elig_suppression == 1,  0,
      #
      #   #Otherwise missing
      #   default = NA_real_
      # ),
      
      der_orig_permutation = PERMUTATION_NUMBER %% 1000
    )
  
  return(returndata)
  
}

