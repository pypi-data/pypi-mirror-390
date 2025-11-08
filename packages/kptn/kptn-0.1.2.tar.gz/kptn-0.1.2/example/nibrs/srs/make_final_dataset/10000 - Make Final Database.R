# ---
# title: '10000 - Make Final Database'
# author: "Philip Lee"
# date: "October 1, 2021"
# output:
#   html_document: default
#   pdf_document:  default
# ---


library(tidyverse)
library(DT)
library(rjson)
library(data.table)


#Read in the common functions to be used in R
source(here::here("tasks/logging.R"))
source(paste0("../../tasks/impute_items/0-Common_functions_for_imputation.R"))

#input/output directories for pipeline artifacts
outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")
inputPipelineDir <- Sys.getenv("INPUT_PIPELINE_DIR")
external_path <- Sys.getenv("EXTERNAL_FILE_PATH")

filepathin_initial = paste0(inputPipelineDir, "/initial_tasks_output/")

year <- Sys.getenv("DATA_YEAR")

filepathout = paste0(outputPipelineDir, "/srs/final-estimates/")

if (! dir.exists(filepathout)) {
  dir.create(filepathout, recursive = TRUE)
}

filepathout_Indicator_Tables = paste0(filepathout,"Indicator_Tables/")
filepathout_Indicator_Tables_no_supp = paste0(filepathout,"Indicator_Tables_no_supp/")
filepathout_Indicator_Tables_flag_non_zero_estimates_with_no_prb = paste0(filepathout,"Indicator_Tables_flag_non_zero_estimates_with_no_prb/")


if (! dir.exists(filepathout_Indicator_Tables)) {
  dir.create(filepathout_Indicator_Tables, recursive = TRUE)
  dir.create(filepathout_Indicator_Tables_no_supp, recursive = TRUE)
  #dir.create(filepathout_Indicator_Tables_no_LEOKA, recursive = TRUE)
  #dir.create(filepathout_Indicator_Tables_no_supp_no_LEOKA, recursive = TRUE)
  dir.create(filepathout_Indicator_Tables_flag_non_zero_estimates_with_no_prb, recursive = TRUE)
}

file_locs <- fromJSON(file = sprintf("%s/external_file_locations.json", inputPipelineDir))

estimate_paths_after_variance = paste0(outputPipelineDir, "/srs/indicator_table_estimates_after_variance/")

read_csv1 <- partial(read_csv, guess_max = 1000000) #For now, read thru the 1st 1,000,000 rows to determine variable type
write.csv0 <- partial(write.csv, row.names = FALSE, na ="0")
write.csv1 <- partial(write.csv, row.names = FALSE, na ="")


#################################Set the DER_NA_CODE variables##############################################
DER_NA_CODE = -9
DER_NA_CODE_STRING = "-9"
PERMUTATION_NAME = Sys.getenv("PERMUTATION_NAME")
CONST_MAIN_PERMUTATION_MAX <- 859
CONST_NATIONAL_PERM <- c(1, 595:597)
CONST_REGIONAL_PERM <- c(2:5)
CONST_DIVISION_PERM <- c(6:14)						   			 							  
CONST_STATE_PERM    <- c(15:65, 598:750)
CONST_MSA_PERM      <- c(66:449, 788:859)
CONST_JD_PERM       <- c(450:539)
CONST_FO_PERM       <- c(540:594)								
CONST_MD_PERM       <- c(751:787)								 


#CONST_DEMO_PERMUTATION <- c(1:83)*1000

log_info(paste0("RUNNING 10000 - Make Final Database ",PERMUTATION_NAME))

#Get all of the csv files
  
    temp_list <- list.files(path=estimate_paths_after_variance, pattern=paste0("\\_",as.integer(PERMUTATION_NAME),"\\.csv"))
    raw_list_files <- c(temp_list)
  

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

#Stack all the files together
raw_1 <- vector("list", length(raw_list_files))

for(i in 1:length(raw_list_files)){

  #Get the current file name and the permutation number
  raw_perm_num <- str_match(raw_list_files[[i]], "(\\d+)\\.csv") %>%
    as_tibble() %>%
    select(V2) %>%
    pull()

  #Save the data to the list
  raw_1[[i]] <- read_csv1(paste0(estimate_paths_after_variance, raw_list_files[[i]]), col_types=raw_files_column_type) %>%
    mutate(PERMUTATION_NUMBER = as.numeric(raw_perm_num),
           FILE_NAME =  raw_list_files[[i]])

  #Delete the items
  rm(raw_perm_num)
  invisible(gc())

}


#raw_2 contains the combined data
raw_2 <- bind_rows(raw_1)

dim(raw_2)

#Make the LEOKA Table to be PERMUTATION_NUMBER = 1
# raw_2 <- raw_2 %>%
#   mutate(PERMUTATION_NUMBER = case_when(!is.na(PERMUTATION_NUMBER) ~ PERMUTATION_NUMBER,
#          TRUE ~ PERMUTATION_NUMBER))

#Check to see if PERMUTATION_NUMBER is correct
raw_2 %>%
  checkfunction(PERMUTATION_NUMBER, FILE_NAME)

#Create the der_variable_name variable, since some variables are not created if the estimate is zero (i.e. no counts)
raw_3 <- raw_2 %>%
  mutate(der_variable_name = paste0("t_",table,"_", section, "_", row, "_", column) )

#Check to see which variables have no counts and also make sure that the der_variable_name is created correctly
raw_3 %>%
  checkfunction(der_variable_name, variable_name)

#Next need to merge on the Population file
raw_pop <- read_csv1(paste0(filepathin_initial, "POP_TOTALS_PERM_", year, "_SRS.csv"))
#Add on a prefix so not to create duplicate variables
colnames(raw_pop) <- paste0("POPTOTAL_", colnames(raw_pop))


#########################Make 100% population coverage to have 0 rmse variables#############
tbd_pop_percent <-  raw_pop %>%
  filter(POPTOTAL_PERMUTATION_NUMBER == as.double(PERMUTATION_NAME)) %>%
  select(POPTOTAL_UNIV_POP_COV) %>%
  pull()

tbd_estimate_0 <- c(
  "estimate_standard_error", 
  "estimate_prb",
  "estimate_bias",
  "estimate_rmse",
  "relative_standard_error",
  "relative_rmse",
  "PRB_ACTUAL"
)

tbd_ci_same <- c(
  "estimate_upper_bound",
  "estimate_lower_bound"  
)

#Make edits if tbd_pop_percent == 1
if(tbd_pop_percent == 1){
  log_debug("100% population coverage detected, making edits to make rmse = 0")
  
  raw_3 <- raw_3 %>%
    mutate(
      #Make the estimates to 0 for the 100% population coverage, if not the NA code and not missing
      across(
        .cols = any_of(tbd_estimate_0),
        .fns = ~{
          fcase(
            .x == DER_NA_CODE, DER_NA_CODE,
            !is.na(.x), 0
            )}
      )
    )
  
    raw_3 <- raw_3 %>%
      mutate(
        #Make the confidence intervals to be the same as the estimate, if not the NA code and not missing
        across(
          .cols = any_of(tbd_ci_same),
          .fns = ~{
            fcase(
              .x == DER_NA_CODE, DER_NA_CODE,
              !is.na(.x), estimate
            )}
        )
      )  
  
}

#Delete the tbd variables
rm(tbd_pop_percent, tbd_estimate_0, tbd_ci_same)
invisible(gc())


############################################################################################


raw_4 <- raw_3 %>%
  left_join(raw_pop, by=c("PERMUTATION_NUMBER" = "POPTOTAL_PERMUTATION_NUMBER"))

dim(raw_3)
dim(raw_pop)
dim(raw_4)

#Fix the population variable population_estimate when estimate_type = "rate" and is.na(population_estimate)
raw_4 %>%
  filter(trim_upcase(estimate_type) == "RATE" & is.na(population_estimate) ) %>%
  checkfunction(estimate_type, population_estimate, estimate)

raw_5 <- raw_4 %>%
  mutate(

    #Create indicator variable
    population_estimate_na_ind = fcase(
      is.na(population_estimate),  1,
      default = 0),

    #Save original variable for QC
    population_estimate_org = population_estimate,

    #Fix the population_estimate variable
    population_estimate = fcase(
    #If population_estimate is not missing then it is fine
    !is.na(population_estimate),  population_estimate,

    #Code for fixes in this workbook Final_Clean_Up_Code.xlsx
    trim_upcase(table)=="SRS1A" & row == 1 & is.na(population_estimate) & trim_upcase(estimate_type) == "RATE", POPTOTAL_POP_TOTAL_WEIGHTED #Offense rate per 100,000 persons

  ) )

#Check to see if the numbers are unique(i.e. no wrong coding to fill in the population_estimate table)
raw_test <- raw_5 %>%
  filter(trim_upcase(estimate_type) == "RATE") %>%
  #Filter to PERMUTATION_NUMBER, table, row
  group_by(PERMUTATION_NUMBER, table, row) %>%
  summarise(final_count = n_distinct(floor(population_estimate))) %>%
  ungroup()


#Make sure that the population_estimate are unique
raw_test %>%
  filter(final_count > 1) %>%
  datatable()

#Clear the data
rm(raw_test)
invisible(gc())

#Need to fix the grey cells
raw_6 <- raw_5 %>%
  mutate(

# der_cleared_cells_qc = fcase(
#   
# ##############There is no grey out cell in SRS #################################
# default = 0
# )

der_cleared_cells_qc = 0
)


#Double check der_cleared_cells_qc has original values as der_cleared_cells, but der_cleared_cells could have missing values
raw_6 %>%
  filter(der_cleared_cells_qc != der_cleared_cells) %>%
  checkfunction(der_cleared_cells_qc, der_cleared_cells, POPTOTAL_PERMUTATION_DESCRIPTION, table, row, estimate_domain, column)

#See the full check
raw_6 %>%
  checkfunction(der_cleared_cells_qc, der_cleared_cells, table, row, column)

#See the added cleared cells
raw_6 %>%
  filter(is.na(der_cleared_cells)) %>%
  checkfunction(der_cleared_cells_qc, der_cleared_cells, table, row, column)

#Overal freqs
raw_6 %>%
  checkfunction(der_cleared_cells_qc, der_cleared_cells)

#Make the der_cleared_cells_qc cells to the DER_NA_CODE

raw_list_vars_to_na <- c(
  "population_estimate",
  "estimate",
  "estimate_standard_error",
  "estimate_prb",
  "estimate_bias",
  "estimate_rmse",
  "estimate_upper_bound",
  "estimate_lower_bound",
  "relative_standard_error",
  "relative_rmse",
  "PRB_ACTUAL",
  "tbd_estimate",
  "estimate_unweighted",
  "population_estimate_unweighted",
  "unweighted_counts",
  "agency_counts"
)


#Look thru and fix estimates
for(i in 1:length(raw_list_vars_to_na)){

  #Current variable
  invar <- raw_list_vars_to_na[[i]] %>% rlang:::parse_expr()

  #If der_cleared_cells_qc, make sure the DER_NA_CODE overwrites the cells
  raw_6 <- raw_6 %>%
    mutate(!!invar := case_when(der_cleared_cells_qc == 1 ~  DER_NA_CODE,
                                        TRUE ~ !!invar))


}

#Quick QC to make sure that the DER_NA_CODE is used properly
raw_6 %>%
  filter(der_cleared_cells_qc == 1) %>%
  checkfunction(!!!(raw_list_vars_to_na %>% rlang:::parse_exprs()) )

raw_6 %>%
  filter(der_cleared_cells_qc == 0) %>%
  head(100) %>%
  datatable()

#Get list of main tables

der_main_tables <- c("TABLESRS1A-SRS OFFENSES",
                     "TABLESRS2A-SRS REGIONAL PERCENTAGES"
)

#Next add on the suppression code
raw_7 <- raw_6 %>%
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
      default = 0),

    #Need to get the main indicator tables and drop the drug modules
    der_main_indicator_tables = fcase(trim_upcase(full_table) %in% der_main_tables, 1,
                                          default = 0),

    #Write the code to identify Level 1 and 2 suppression criteria
    #For SRS, use all the estimates
    der_suppression_level = fcase(
      ###################################SRS1A###############################################
      #All rows
      trim_upcase(table) == "SRS1A", 1,


      ###################################SRS2A###############################################
      #Top row
      trim_upcase(table) == "SRS2A", 1


    )
)

#Check the recodes
raw_7 %>%
  checkfunction(der_na_agency_counts, agency_counts)

raw_7 %>%
  filter(estimate == DER_NA_CODE) %>%
  checkfunction(der_estimate_na_code, estimate)

raw_7 %>%
  checkfunction(der_elig_suppression, der_na_agency_counts, der_estimate_na_code)

raw_7 %>% checkfunction(der_main_indicator_tables, full_table)

#Check that the correct rows are selected
raw_7 %>%
  filter(!is.na(der_suppression_level)) %>%
  checkfunction(table, der_suppression_level, row, estimate_domain)


#Make sure that when der_na_agency_counts == 1 that the estimate makes sense
raw_7 %>%
  filter(der_na_agency_counts == 1) %>%
  checkfunction(estimate)

raw_7_1 <- raw_7 %>%
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

  #Delete the old objects
  rm(list=c(paste0("raw_", 1:7)))
  invisible(gc())

  #Need to handle at each permutation/cell level using dataset raw_7_1 as a base

    
  # Alt 6
  # RMSE > 0.3 OR {
  # (estimate = 0 OR var(estimate) = 0) AND [
  # (agency type domain or permutation in (state police, other state agencies, tribal, federal) AND cell agency coverage < 80%) OR 
  # (^not that AND cell population coverage < 80%)
  # ]
  # }

  #Need to handle the Tribal permutation (i.e. 108) then 
  #Tribal agencies, State police, and Other state agencies

  #For SRS, we did not break out by agency type, so code everyone as 0
  raw_7_2 <- raw_7_1 %>%
    
    mutate(
      
      # der_cell_separate = fcase( 
      #   default = 0 #Here are the rest
      # ),
      
      der_cell_separate = 0, #Here are the rest
      
      
      #Create a row_number, so we can sort the data back once we stacked the rows
      tbd_row_number = row_number()
      )
  
  #QC the variable
  raw_7_2 %>% checkfunction(der_cell_separate, POPTOTAL_ORIG_PERMUTATION_NUMBER, estimate_domain)
  
  #Write a function to create the suppression indicator
  loopsuppressionrulecell <- function(indata, inder_cell_separate, inrule){
    
    returndata <- indata %>% 
      #Filter to the rows in the database
      filter(der_cell_separate == inder_cell_separate) %>%
      #Create the new variable with the condition %>%
      mutate(
        der_rrmse_gt_30_se_estimate_0_2_cond = fcase(
        !!(inrule %>% rlang:::parse_expr() ), 1,  
      	#Otherwise do not suppress if not the NA code
      	der_estimate_na_code == 0 , 0        
      ))
    
    #Return the data
    return(returndata)
    
  }
  
  
  raw_7_r0 <- loopsuppressionrulecell(indata=raw_7_2, 
                                      inder_cell_separate = 0, 
                                      inrule = '  
der_estimate_0_se_0 == 1 & 
der_estimate_na_code == 0  & 
POPTOTAL_UNIV_POP_COV < 0.80 
')  
  
  #Stack the data together and handle the RSE portion
  raw_8 <- bind_rows(raw_7_r0) %>%
    mutate(     
      #Handle the RSE portion  
      der_rrmse_gt_30_se_estimate_0_2_cond = case_when(
        der_rrmse_gt_30 == 1 ~ 1,
		    TRUE ~ der_rrmse_gt_30_se_estimate_0_2_cond)) %>%
    #Sort the data
    arrange(tbd_row_number)
  

  #Check the merge
  dim(raw_7_2)
  dim(raw_8)
  dim(raw_7_r0)

  #Delete the old objects
  rm(list=ls(pattern="raw_7_"))
  invisible(gc())  
  
  #################################################################################################################

 

#Check the recodes
raw_8 %>% head(1000) %>% checkfunction(der_rrmse_gt_30, relative_rmse, der_estimate_na_code)
raw_8 %>% head(1000) %>% checkfunction(der_estimate_0, estimate, der_estimate_na_code)
raw_8 %>% head(1000) %>% checkfunction(der_estimate_se_0, estimate_standard_error, der_estimate_na_code)
raw_8 %>% head(1000) %>% checkfunction(der_estimate_0_se_0, der_estimate_0, der_estimate_se_0, der_estimate_na_code)

#For Alt 6 check   

raw_8 %>% checkfunction(der_rrmse_gt_30_se_estimate_0_2_cond, der_rrmse_gt_30, der_estimate_0_se_0, POPTOTAL_ORIG_PERMUTATION_NUMBER)

raw_8 %>%
  checkfunction(der_na_estimate_prb , estimate_prb)


raw_8 %>%
  head(1000) %>%
  checkfunction(der_rrmse_30, relative_rmse)

# raw_8 %>%
#   head(1000) %>%
#   checkfunction(der_rrmse_50 , relative_rmse)

raw_8 %>%
  checkfunction(der_agency_count_10, agency_counts)

# raw_8 %>%
#   checkfunction(der_agency_count_3, agency_counts)

# raw_8 %>%
#   checkfunction(der_rrmse_30_agency_10, der_na_estimate_prb, der_elig_suppression, der_rrmse_30, der_agency_count_10)

# raw_8 %>%
#   checkfunction(der_rrmse_30_agency_3, der_na_estimate_prb, der_elig_suppression, der_rrmse_30, der_agency_count_3)

# raw_8 %>%
#   checkfunction(der_rrmse_50_agency_10, der_na_estimate_prb, der_elig_suppression, der_rrmse_50, der_agency_count_10)

# raw_8 %>%
#   checkfunction(der_rrmse_50_agency_3, der_na_estimate_prb, der_elig_suppression, der_rrmse_50, der_agency_count_3)

#See the cells where estimate_prb is missing
raw_8 %>%
  filter(is.na(estimate_prb) & der_elig_suppression == 1) %>%
  checkfunction(estimate_prb, PERMUTATION_NUMBER, POPTOTAL_PERMUTATION_DESCRIPTION, indicator_name)

raw_8 %>%
  checkfunction(der_orig_permutation , PERMUTATION_NUMBER)

#Next need to create each of the momentum rule
raw_8_top <-  raw_8 %>%
  #Filter to the main indicator tables only
  filter(der_main_indicator_tables == 1 & der_suppression_level %in% c(1)) %>%
  #For this program, main difference is to subset to the main permutation 
  filter(PERMUTATION_NUMBER %in% c(1:CONST_MAIN_PERMUTATION_MAX)) %>%
  #Need to use the overall permutation number
  group_by(POPTOTAL_ORIG_PERMUTATION_NUMBER) %>%
  summarise(
  
  # Alt 6
  # RMSE > 0.3 OR {
  # (estimate = 0 OR var(estimate) = 0) AND [
  # (agency type domain or permutation in (state police, other state agencies, tribal, federal) AND cell agency coverage < 80%) OR 
  # (^not that AND cell population coverage < 80%)
  # ]
  # }
  
    der_rrmse_gt_30_se_estimate_0_2_cond_top = sum(der_rrmse_gt_30_se_estimate_0_2_cond == 1 & der_estimate_na_code == 0, na.rm=TRUE) / sum(der_estimate_na_code == 0, na.rm=TRUE)
  
  

  ) %>%
  ungroup()


#Merge on the results
raw_9 <- raw_8 %>%
  left_join(raw_8_top, by=c("POPTOTAL_ORIG_PERMUTATION_NUMBER"))

print(dim(raw_9))
print(dim(raw_8))
print(dim(raw_8_top))

#Add on the additional variables for suppression
# raw_9_1 <- raw_8 %>%
#     group_by(estimate_geographic_location) %>%
#     mutate(
#       prop_30_10=sum(der_rrmse_30_agency_10==1 & relative_rmse>0,na.rm=TRUE)/sum(relative_rmse>0,na.rm=TRUE),
#       prop_30_3=sum(der_rrmse_30_agency_3==1 & relative_rmse>0,na.rm=TRUE)/sum(relative_rmse>0,na.rm=TRUE),
#       prop_50_10=sum(der_rrmse_50_agency_10==1 & relative_rmse>0,na.rm=TRUE)/sum(relative_rmse>0,na.rm=TRUE),
#       prop_50_3=sum(der_rrmse_50_agency_3==1 & relative_rmse>0,na.rm=TRUE)/sum(relative_rmse>0,na.rm=TRUE),
#       pop_cov=mean(POP_TOTAL_UNWEIGHTED,na.rm=TRUE)/mean(POP_TOTAL,na.rm=TRUE)
#     ) %>%
#   ungroup()
# 
# dim(raw_8)
# dim(raw_9_1)

#Add on new code for new suppression rules
# raw_9_2 <- raw_9_1 %>%
#   #Filter to the main indicator tables only
#   filter(der_main_indicator_tables == 1 & der_suppression_level %in% c(1)) %>%
#   group_by(estimate_geographic_location) %>%
#   #Want at the estimate_geographic_location or PERMUTATION_NUMBER level
#   summarise(
# 
#     prop_30_10_top=sum(der_rrmse_30_agency_10==1 & relative_rmse>0,na.rm=TRUE)/sum(relative_rmse>0,na.rm=TRUE)
# 
#   ) %>%
#   ungroup()
# 
# raw_9_org_pop_cov <- raw_9_1 %>%
#   #Filter to the main permutations
#   filter(PERMUTATION_NUMBER %in% c(1:CONST_MAIN_PERMUTATION_MAX) ) %>%
#   group_by(der_orig_permutation) %>%
#   #Want at the der_orig_permutation or PERMUTATION_NUMBER level
#   summarise(
# 
#     pop_cov_perm0=mean(POP_TOTAL_UNWEIGHTED,na.rm=TRUE)/mean(POP_TOTAL,na.rm=TRUE)
# 
#   ) %>%
#   ungroup()
# 
# #Merge the data together
# raw_9 <- raw_9_1 %>%
#   left_join(raw_9_2, by=c("estimate_geographic_location")) %>%
#   left_join(raw_9_org_pop_cov, by=c("der_orig_permutation"))
# 
# dim(raw_9)
# dim(raw_9_1)
# dim(raw_9_2)
# dim(raw_9_org_pop_cov)
# 
# #QC the revelant variables
# raw_9 %>%
#   checkfunction(estimate_geographic_location, prop_30_10)
# 
# raw_9 %>%
#   checkfunction(estimate_geographic_location, POP_TOTAL_UNWEIGHTED, POP_TOTAL, pop_cov)
# 
# raw_9 %>%
#   checkfunction(estimate_geographic_location, prop_30_10_top)
# 
# raw_9 %>%
#   checkfunction(estimate_geographic_location, pop_cov_perm0)


#From raw_9 use the following for suppression rule
#a.	Any estimate with > 30% %RRMSE OR 10 or fewer unweighted agencies with incidents get an estimate level suppression flag of 1; else 0:  der_rrmse_30_agency_10
#b.	Grouping by estimate_geographic_location, calculate the % of estimates with a value of 1 in the flag from 2.a above:  prop_30_10
#c. Grouping by estimate_geographic_location, calculate the population coverage for the permutation group:  pop_cov

raw_10 <- raw_9 %>%
  mutate(
    #d.	Any permutation group (estimate_geographic_location level) with a value from 2.b > 50% AND a value from 2.c < 80% gets a permutation group level suppression flag of 1; else 0.	This flag applies to all estimates in the permutation group

    # der_perm_group_suppression_flag = fcase(
    #     prop_30_10 > 0.50 & pop_cov < 0.8,  1,
    #     default = 0
    # ),

    #Update on 2022-07-19:
    #for the momentum rule use main tables and level 1 estimates only and use a cutoff of 75%
    #prop_30_10_top is the variable to use
    # der_perm_group_suppression_flag = fcase(
    #   prop_30_10_top > 0.75 & pop_cov < 0.8, 1,
    #   default = 0
    # ),
    
    #Update on 2023-02-10%:
    #	More than 75% of key estimates in the permutation are suppressed based on estimate-level criteria AND
    #	Permutation-level population coverage is less than 80%

    der_perm_group_suppression_flag = fcase(
      der_rrmse_gt_30_se_estimate_0_2_cond_top > 0.75 & (POPTOTAL_ORIG_PERMUTATION_NUMBER_COV) < 0.8, 1,
      default = 0
    ),
    

    #e.	Any permutation group (estimate_geographic_location level) with a value from 2.c > 95% gets a permutation group level force un-suppress flag of 1; else 0. This flag applies to all estimates in the permutation group

    # der_perm_group_unsuppression_flag = fcase(
    #     pop_cov > 0.95,  1,
    #     default = 0
    #  ),
    #Update on 2022-07-19
    #the 95%+ coverage rule is based on PERM 0 only (and all lower permutations follow if PERM 0 has coverage greater than 95%)
    # der_perm_group_unsuppression_flag = fcase(
    #   pop_cov_perm0 > 0.95, 1,
    #   default = 0
    # ),
    
    #Update on 2023-02-10
    #the 80%+ coverage rule is based on PERM 0 only (and all lower permutations follow if PERM 0 has coverage greater than 80%)
    der_perm_group_unsuppression_flag = fcase(
      POPTOTAL_ORIG_PERMUTATION_NUMBER_COV > 0.80, 1,
      default = 0
    ),    

     #Variable to create for database:  suppression_flag_indicator
	    
    #Create suppression flag for the national permutation
    #No 10% agency rule
    #No principal city
    #No momentum rule
    #Do the unsuppression rule
    suppression_flag_indicator_national = fcase(
      #i.	If the flag from 2.e=1 then the final estimate level suppression flag=0; else. Unsuppression rule
        der_perm_group_unsuppression_flag == 1 & !is.na(der_rrmse_gt_30_se_estimate_0_2_cond)  , 0,
      #iii.	Set the final estimate level suppression flag to the value from 2.a
        der_perm_group_unsuppression_flag == 0 ,  der_rrmse_gt_30_se_estimate_0_2_cond
    ),
    
    #Create suppression flag for our regular rules for non-MSA
    #10% agency rule
    #momentum rule
    #Do the unsuppression rule    
    suppression_flag_indicator_regular = fcase(
      #New.  Add on the Missing Certainty Agency Rule	
      POPTOTAL_ORIG_UNIV_ELIG_PERM_AGENCY_MISSING_OVER_10_PERCENT == TRUE , 1,	      
      #i.	If the flag from 2.e=1 then the final estimate level suppression flag=0; else.
      der_perm_group_unsuppression_flag == 1 & !is.na(der_rrmse_gt_30_se_estimate_0_2_cond)  , 0,
      #ii.	If the flag from 2.d=1 then the final estimate level suppression flag=1; else.
      der_perm_group_suppression_flag == 1 & !is.na(der_rrmse_gt_30_se_estimate_0_2_cond) , 1,
      #iii.	Set the final estimate level suppression flag to the value from 2.a
      der_perm_group_unsuppression_flag == 0 ,  der_rrmse_gt_30_se_estimate_0_2_cond
    ),    
    
    #Create suppression flag for our MSA only
    #principal city
    #momentum rule
    #Do the unsuppression rule    
    suppression_flag_indicator_msa = fcase(
      #New.  Add on the Missing Principal city Rule	
      POPTOTAL_ORIG_ELIG_PERM_AGENCY_MISSING_PRINCIPAL_CITY == TRUE , 1,	      
      #i.	If the flag from 2.e=1 then the final estimate level suppression flag=0; else.
      der_perm_group_unsuppression_flag == 1 & !is.na(der_rrmse_gt_30_se_estimate_0_2_cond)  , 0,
      #ii.	If the flag from 2.d=1 then the final estimate level suppression flag=1; else.
      der_perm_group_suppression_flag == 1 & !is.na(der_rrmse_gt_30_se_estimate_0_2_cond) , 1,
      #iii.	Set the final estimate level suppression flag to the value from 2.a
      der_perm_group_unsuppression_flag == 0 ,  der_rrmse_gt_30_se_estimate_0_2_cond
    ),        
    
    #List of geographic permutations 
	#CONST_NATIONAL_PERM <- c(1, 595:597)
	#CONST_REGIONAL_PERM <- c(2:5)
	#CONST_DIVISION_PERM <- c(6:14)						   			 							  
	#CONST_STATE_PERM    <- c(15:65, 598:750)
	#CONST_MSA_PERM      <- c(66:449, 788:859)
	#CONST_JD_PERM       <- c(450:539)
	#CONST_FO_PERM       <- c(540:594)								
	#CONST_MD_PERM       <- c(751:787)						  
    
    suppression_flag_indicator = fcase(
      #National permutation
      POPTOTAL_ORIG_PERMUTATION_NUMBER %in% c(CONST_NATIONAL_PERM), suppression_flag_indicator_national, 
      #MSA permutation
      POPTOTAL_ORIG_PERMUTATION_NUMBER %in% c(CONST_MSA_PERM, CONST_MD_PERM), suppression_flag_indicator_msa, 
      #Remaining permutations
      POPTOTAL_ORIG_PERMUTATION_NUMBER %in% c(
        CONST_REGIONAL_PERM,
        CONST_DIVISION_PERM,
        CONST_STATE_PERM,
        CONST_JD_PERM,
        CONST_FO_PERM), suppression_flag_indicator_regular
    )
)

#QC the variables
raw_10 %>%
  checkfunction(der_perm_group_suppression_flag, der_rrmse_gt_30_se_estimate_0_2_cond_top, POPTOTAL_ORIG_PERMUTATION_NUMBER_COV, PERMUTATION_NUMBER, POPTOTAL_PERMUTATION_DESCRIPTION)

raw_10 %>%
  checkfunction(der_perm_group_unsuppression_flag, POPTOTAL_ORIG_PERMUTATION_NUMBER_COV, PERMUTATION_NUMBER, POPTOTAL_PERMUTATION_DESCRIPTION)

#National permutation
raw_10 %>%
  filter(POPTOTAL_ORIG_PERMUTATION_NUMBER %in% c(CONST_NATIONAL_PERM)) %>%
  checkfunction(suppression_flag_indicator, der_perm_group_unsuppression_flag, der_rrmse_gt_30_se_estimate_0_2_cond)

#MSA permutation
raw_10 %>%
  filter(POPTOTAL_ORIG_PERMUTATION_NUMBER %in% c(CONST_MSA_PERM)) %>%
  checkfunction(suppression_flag_indicator, POPTOTAL_ORIG_ELIG_PERM_AGENCY_MISSING_PRINCIPAL_CITY, der_perm_group_unsuppression_flag, der_perm_group_suppression_flag, der_rrmse_gt_30_se_estimate_0_2_cond)

#Remaining permutations
raw_10 %>%
  filter(
  #Remaining permutations
  POPTOTAL_ORIG_PERMUTATION_NUMBER %in% c(
    CONST_REGIONAL_PERM,
    CONST_DIVISION_PERM,
    CONST_STATE_PERM,
    CONST_JD_PERM,
    CONST_FO_PERM)) %>%  
  checkfunction(suppression_flag_indicator, POPTOTAL_ORIG_UNIV_ELIG_PERM_AGENCY_MISSING_OVER_10_PERCENT, der_perm_group_unsuppression_flag, der_perm_group_suppression_flag, der_rrmse_gt_30_se_estimate_0_2_cond)


#Need to ask if suppression_flag_indicator missing for NA and missing agency_counts
raw_10 %>%
  filter(is.na(suppression_flag_indicator)) %>%
  checkfunction(estimate)

#Need to make the estimate_domain to become estimate_domain_1 and estimate_domain_2 and split by the ":"
raw_10 %>%
  checkfunction(estimate_domain)

raw_11  <- raw_10 %>%
  mutate(tbd_estimate_domain = estimate_domain) %>%
  separate(estimate_domain, c("estimate_domain_1", "estimate_domain_2"),  ":") %>%
  #Make sure that the blank spaces are removed
  mutate(estimate_domain_1 = trimws(estimate_domain_1, which="both"),
         estimate_domain_2 = trimws(estimate_domain_2, which="both"))

raw_11 %>%
  checkfunction(tbd_estimate_domain, estimate_domain_1, estimate_domain_2)

#Add code to unsuppress state estimates for violent crime offense and property crime offense

#Code for subset - For SRS State permutations are 15 to 65
off_violent_property_subset <- "    PERMUTATION_NUMBER %in% c(15:65)    & #State permutations
                                    der_perm_group_suppression_flag == 1 & #Suppress due to permutation
                                    suppression_flag_indicator == 1      & #Suppression
                                    der_rrmse_gt_30_se_estimate_0_2_cond == 0            #Not suppress by itself" %>% rlang:::parse_expr()


#Identify the offense crime indicators
off_violent_crime <- c("t_SRS1a_1_1_1")
off_property_crime <- c("t_SRS1a_1_1_6")

test_off_violent <- raw_11 %>%
  filter(
    der_variable_name %in% off_violent_crime[[1]]   & #Violent Crime Total at position 1
    !!off_violent_property_subset
    )  %>%
  #Need to process by Permutation only interested in state permutations:  PERMUTATION_NUMBER %in% c(56:106)
  group_by(PERMUTATION_NUMBER) %>%
  mutate(der_off_violent_crime_unsuppress = 1) %>%
  ungroup() %>%
  select(PERMUTATION_NUMBER, der_off_violent_crime_unsuppress)

dim(raw_11)
dim(test_off_violent)

test_off_property <- raw_11 %>%
  filter(
    der_variable_name %in% off_property_crime[[1]]  & #Property Crime Total at position 1
    !!off_violent_property_subset
    )  %>%
  #Need to process by Permutation only interested in state permutations:  PERMUTATION_NUMBER %in% c(56:106)
  group_by(PERMUTATION_NUMBER) %>%
  mutate(der_off_property_crime_unsuppress = 1) %>%
  ungroup() %>%
  select(PERMUTATION_NUMBER, der_off_property_crime_unsuppress)

dim(raw_11)
dim(test_off_property)

raw_12 <- reduce(list(raw_11, test_off_violent, test_off_property), left_join, by="PERMUTATION_NUMBER") %>%
  #Unsuppress the Offense Violent crime and property crime estimate
  mutate(
    suppression_flag_indicator = case_when(
      #Choose the offense violent crime and property variables
      der_variable_name %in% c( off_violent_crime,    #Violent Crime
                                off_property_crime) & #Property Crime)
      #When both the violent and property crime are unsuppress within the state permutations
      der_off_violent_crime_unsuppress  == 1 &
      der_off_property_crime_unsuppress == 1 &
      #If the estimate is not the NA code then make 0 and unsuppress
      estimate != DER_NA_CODE ~ 0,
      #Otherwise keep as is
      TRUE ~ suppression_flag_indicator
    )
  )

dim(raw_12)
dim(raw_11)
dim(test_off_violent)
dim(test_off_property)

#Check to see for the permutations that have unsuppress offenses violent and property crimes
raw_12 %>%
  filter(der_off_violent_crime_unsuppress == 1 & der_off_property_crime_unsuppress == 1) %>%
  checkfunction(estimate_geographic_location, suppression_flag_indicator, der_off_violent_crime_unsuppress, der_off_property_crime_unsuppress)

#Check to see for the permutations that have unsuppress offenses violent and property crimes the variables
raw_12 %>%
  filter(der_off_violent_crime_unsuppress == 1 & der_off_property_crime_unsuppress == 1 &
          der_variable_name %in% c( off_violent_crime,    #Violent Crime
                                    off_property_crime)  #Property Crime)
           ) %>%
  checkfunction(estimate_geographic_location, suppression_flag_indicator, der_variable_name, estimate, estimate_type,   der_off_violent_crime_unsuppress, der_off_property_crime_unsuppress)

#Remove the objects
rm(off_violent_property_subset, off_violent_crime, off_property_crime, test_off_violent, test_off_property)
invisible(gc())

#20220810: Need to swap out the old prop_30_10 with the new variable prop_30_10_top, but rename it to be prop_30_10
raw_12 <- raw_12 %>%
  #Drop the old prop_30_10 variable
  #select(-prop_30_10) %>%
  #Rename prop_30_10_top to prop_30_10
  rename(#prop_30_10 = prop_30_10_top,
         pop_cov = POPTOTAL_UNIV_POP_COV
         
         )

#Using the raw_12 dataset, need to make the following edits to the lower bound estimates (i.e. estimate_lower_bound)
#1.  When the table is SRS1a, need to make sure that the estimate_lower_bound is no lower than the SRS1araw estimate
#For all tables if the estimate_lower_bound is negative then change to 0

tbd_raw_estimate <- raw_12 %>%
  filter(trim_upcase(table) == "SRS1ARAW") %>%
  #Keep certain variables
  select(table, section, row, column, estimate_type_num, 
         estimate_rawsrs = estimate) %>%
  #Need to recreate the table variable to match the original
  mutate(
    table = "SRS1a",
    tbd_check_srs1araw = 1
  )

#Using tbd_raw_estimate and raw_12, need to merge the data
raw_13 <- raw_12 %>%
  left_join(tbd_raw_estimate, by=c("table", "section", "row", "column", "estimate_type_num")) %>%
  #rename the estimate_lower_bound
  rename(orig_estimate_lower_bound = estimate_lower_bound) %>%
  mutate(
    one = 1,
    
    #Need to edit the lower bounds
    estimate_lower_bound = fcase(
      #If the table is SRS1a and the estimate from SRS1araw is larger than the SRS1a's estimate_lower_bound, then
      #Use SRS1araw's estimate
      trim_upcase(table) == "SRS1A" & (estimate_rawsrs > orig_estimate_lower_bound), estimate_rawsrs,
      #else if the orig_estimate_lower_bound is negative and not the NA code then make 0
      (orig_estimate_lower_bound < 0) & (orig_estimate_lower_bound != DER_NA_CODE), 0, 
      #Otherwise keep the lower bound as is
      one == 1, orig_estimate_lower_bound
    )
  )


#Check the dim
log_dim(raw_13)
log_dim(raw_12)
log_dim(tbd_raw_estimate)

raw_13 %>% checkfunction(tbd_check_srs1araw)

#Check the estimate_lower_bound
raw_13 %>%
  filter(orig_estimate_lower_bound != estimate_lower_bound) %>%
  checkfunction(table, section, row, column, estimate_type_num, estimate_lower_bound, orig_estimate_lower_bound, estimate_rawsrs)

#New make sure that the raw estimate are not suppressed if not the NA code
raw_14 <- raw_13 %>%
  mutate(
    one = 1,
    
    #Make into missing if it is SRS1a raw and the estimate is not the NA code
    der_make_suppression_flag_indicator_0_ind = fcase(
      estimate == DER_NA_CODE, NA_real_,
      estimate != DER_NA_CODE & trim_upcase(full_table) == "TABLESRS1ARAW-SRS OFFENSES", 1, 
      default = 0
    ),
    
    #Recreate the suppression_flag_indicator
    tbd_suppression_flag_indicator = suppression_flag_indicator,
    
    suppression_flag_indicator = fcase(
      der_make_suppression_flag_indicator_0_ind == 1, 0,
      one == 1, tbd_suppression_flag_indicator
    )
  ) %>%
  select(-one)

#Check the recodes
raw_14 %>% checkfunction(der_make_suppression_flag_indicator_0_ind, full_table, estimate)
raw_14 %>% checkfunction(suppression_flag_indicator, der_make_suppression_flag_indicator_0_ind, tbd_suppression_flag_indicator)

#Need to make estimate_prb and PRB_ACTUAL to be all missing
#Need to create a estimate_copula.  Currently estimate_bias = estimate - estimate_copula
#So estimate_copula = estimate - estimate_bias for all estimate type

raw_15 <- raw_14 %>%
  mutate(
    #Make the one variable
    one = 1,
    
    #Make estimate_prb to all missing
    estimate_prb = NA_real_, 
	
    #Make PRB_ACTUAL to all missing
    PRB_ACTUAL = NA_real_, 		
    
    #Create estimate_copula
    estimate_copula = fcase(
      #Keep NA code as is
      estimate == DER_NA_CODE, DER_NA_CODE,
      #Otherwise apply the formula
      one == 1, estimate - estimate_bias
    )
  )

#Check the recodes
raw_15 %>% checkfunction(estimate_prb)
#raw_15 %>% checkfunction(estimate_copula, estimate, estimate_bias)

#Declare the final data
final_data_output <- raw_15




#Create a list of variables to output for each section
OUTPUT_VARS <- c(
  "indicator_name",
  "estimate",
  "estimate_unweighted",
  "estimate_geographic_location",
  "estimate_type",
  "estimate_type_num",
  "estimate_type_detail_percentage",
  "estimate_type_detail_rate",
  "estimate_domain_1",
  "estimate_domain_2",
  "estimate_standard_error",
  "estimate_upper_bound",
  "estimate_lower_bound",
  "relative_standard_error",
  "analysis_weight_name",
  "estimate_prb",
  "estimate_bias",
  "estimate_rmse",
  "relative_rmse",
  #poor_quality_indicator",
  "suppression_flag_indicator",
  "der_elig_suppression",
  "pop_cov",
  "agency_counts",
  "der_rrmse_30",
  #der_agency_count_10",
  "der_rrmse_gt_30_se_estimate_0_2_cond", #der_rrmse_30_agency_10",
  "der_rrmse_gt_30_se_estimate_0_2_cond_top", #prop_30_10",
  "der_perm_group_unsuppression_flag",
  "der_perm_group_suppression_flag",
  "population_estimate",
  "time_series_start_year",
  "full_table",
  "der_variable_name",
  "PERMUTATION_NUMBER",
  "PRB_ACTUAL",
  "POPTOTAL_ORIG_UNIV_ELIG_PERM_AGENCY_MISSING_OVER_10_PERCENT",
  "POPTOTAL_ORIG_ELIG_PERM_AGENCY_MISSING_PRINCIPAL_CITY", 
  "estimate_copula"
) %>% rlang:::parse_exprs()


final_data_output %>%
  mutate(time_series_start_year = year) %>%
  select(
  !!!OUTPUT_VARS
) %>%
  write.csv1(paste0(filepathout_Indicator_Tables, "Indicator_Tables_",PERMUTATION_NAME,"_", year, ".csv"))


  final_data_output %>%
    mutate(time_series_start_year = year) %>%
    filter(suppression_flag_indicator == 0) %>%
    select(
    !!!OUTPUT_VARS
  ) %>%
    write.csv1(paste0(filepathout_Indicator_Tables_no_supp, "Indicator_Tables_no_supp_",PERMUTATION_NAME,"_", year,".csv"))


#Identify any missing PRBs and non-zero estimates
final_data_output %>%
  filter(is.na(estimate_copula) & estimate > 0) %>%
  #Need to filter out the table when it is SRS1araw
  filter(trim_upcase(table) != "SRS1ARAW") %>%												   																		  
  mutate(time_series_start_year = year) %>%
  select(
  !!!OUTPUT_VARS
  ) %>%
  write.csv1(paste0(filepathout_Indicator_Tables_flag_non_zero_estimates_with_no_prb, "Indicator_Tables_flag_non_zero_estimates_with_no_prb_",PERMUTATION_NAME,".csv"))
