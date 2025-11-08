#Read in the current permutation_number
DER_CURRENT_PERMUTATION_NUM
#Get the National estimates
pop_data_NATIONAL <- read_csv(paste0(inputPipelineDir,"/weighting/Data/", "POP_TOTALS_PERM_", CONST_YEAR, "_FINAL.csv"),n_max=2) %>% filter(PERMUTATION_NUMBER == 1)

DER_POP_OFFICER_NUM_NATIONAL <- pop_data_NATIONAL$DER_POP_OFFICER_NUM_WEIGHTED
DER_POP_PCTAGELT5_NUM_NATIONAL <- pop_data_NATIONAL$DER_POP_PCTAGELT5_NUM_WEIGHTED
DER_POP_PCTAGE5TO14_NUM_NATIONAL <- pop_data_NATIONAL$DER_POP_PCTAGE5TO14_NUM_WEIGHTED
DER_POP_PCTAGE15_NUM_NATIONAL <- pop_data_NATIONAL$DER_POP_PCTAGE15_NUM_WEIGHTED
DER_POP_PCTAGE16_NUM_NATIONAL <- pop_data_NATIONAL$DER_POP_PCTAGE16_NUM_WEIGHTED
DER_POP_PCTAGE17_NUM_NATIONAL <- pop_data_NATIONAL$DER_POP_PCTAGE17_NUM_WEIGHTED
DER_POP_PCTAGE18TO24_NUM_NATIONAL <- pop_data_NATIONAL$DER_POP_PCTAGE18TO24_NUM_WEIGHTED
DER_POP_PCTAGE25TO34_NUM_NATIONAL <- pop_data_NATIONAL$DER_POP_PCTAGE25TO34_NUM_WEIGHTED
DER_POP_PCTAGE35TO64_NUM_NATIONAL <- pop_data_NATIONAL$DER_POP_PCTAGE35TO64_NUM_WEIGHTED
DER_POP_PCTAGEGTE65_NUM_NATIONAL <- pop_data_NATIONAL$DER_POP_PCTAGEGTE65_NUM_WEIGHTED
DER_POP_PCTSEXMALE_NUM_NATIONAL <- pop_data_NATIONAL$DER_POP_PCTSEXMALE_NUM_WEIGHTED
DER_POP_PCTSEXFEMALE_NUM_NATIONAL <- pop_data_NATIONAL$DER_POP_PCTSEXFEMALE_NUM_WEIGHTED
DER_POP_PCTRACEWHITE_NUM_NATIONAL <- pop_data_NATIONAL$DER_POP_PCTRACEWHITE_NUM_WEIGHTED
DER_POP_PCTRACEBLACK_NUM_NATIONAL <- pop_data_NATIONAL$DER_POP_PCTRACEBLACK_NUM_WEIGHTED
DER_POP_PCTRACEAIAN_NUM_NATIONAL <- pop_data_NATIONAL$DER_POP_PCTRACEAIAN_NUM_WEIGHTED
DER_POP_PCTRACEASIAN_NUM_NATIONAL <- pop_data_NATIONAL$DER_POP_PCTRACEASIAN_NUM_WEIGHTED
DER_POP_PCTRACENHPI_NUM_NATIONAL <- pop_data_NATIONAL$DER_POP_PCTRACENHPI_NUM_WEIGHTED
POP_TOTAL_NATIONAL <- pop_data_NATIONAL$POP_TOTAL_WEIGHTED

#Additional variables
DER_POP_PCTAGE_15_17_NUM_NATIONAL <- pop_data_NATIONAL$DER_POP_PCTAGE_15_17_NUM_WEIGHTED
DER_POP_PCTAGE_UNDER_18_NUM_NATIONAL <- pop_data_NATIONAL$DER_POP_PCTAGE_UNDER_18_NUM_WEIGHTED
DER_POP_PCTAGE_UNDER_12_NUM_NATIONAL <- pop_data_NATIONAL$DER_POP_PCTAGE_UNDER_12_NUM_WEIGHTED
DER_POP_PCTAGE_12_17_NUM_NATIONAL <- pop_data_NATIONAL$DER_POP_PCTAGE_12_17_NUM_WEIGHTED
DER_POP_PCTAGE_OVER_18_NUM_NATIONAL <- pop_data_NATIONAL$DER_POP_PCTAGE_OVER_18_NUM_WEIGHTED

DER_POP_PCTAGE_12_14_NUM_NATIONAL <- pop_data_NATIONAL$DER_POP_PCTAGE_12_14_NUM_WEIGHTED

DER_POP_PCT_HISP_NUM_NATIONAL <- pop_data_NATIONAL$DER_POP_PCT_HISP_NUM_WEIGHTED
DER_POP_PCT_NONHISP_NUM_NATIONAL <- pop_data_NATIONAL$DER_POP_PCT_NONHISP_NUM_WEIGHTED
DER_POP_PCT_NONHISP_WHITE_NUM_NATIONAL <- pop_data_NATIONAL$DER_POP_PCT_NONHISP_WHITE_NUM_WEIGHTED
DER_POP_PCT_NONHISP_BLACK_NUM_NATIONAL <- pop_data_NATIONAL$DER_POP_PCT_NONHISP_BLACK_NUM_WEIGHTED
DER_POP_PCT_NONHISP_AIAN_NUM_NATIONAL <- pop_data_NATIONAL$DER_POP_PCT_NONHISP_AIAN_NUM_WEIGHTED
DER_POP_PCT_NONHISP_ASIAN_NUM_NATIONAL <- pop_data_NATIONAL$DER_POP_PCT_NONHISP_ASIAN_NUM_WEIGHTED
DER_POP_PCT_NONHISP_NHOPI_NUM_NATIONAL <- pop_data_NATIONAL$DER_POP_PCT_NONHISP_NHOPI_NUM_WEIGHTED

#Subset to current row
pop_data <- read_csv(paste0(inputPipelineDir,"/weighting/Data/", "POP_TOTALS_PERM_", CONST_YEAR, "_FINAL.csv")) %>% filter(PERMUTATION_NUMBER == DER_CURRENT_PERMUTATION_NUM)

DER_POP_OFFICER_NUM <- pop_data$DER_POP_OFFICER_NUM_WEIGHTED
DER_POP_PCTAGELT5_NUM <- pop_data$DER_POP_PCTAGELT5_NUM_WEIGHTED
DER_POP_PCTAGE5TO14_NUM <- pop_data$DER_POP_PCTAGE5TO14_NUM_WEIGHTED
DER_POP_PCTAGE15_NUM <- pop_data$DER_POP_PCTAGE15_NUM_WEIGHTED
DER_POP_PCTAGE16_NUM <- pop_data$DER_POP_PCTAGE16_NUM_WEIGHTED
DER_POP_PCTAGE17_NUM <- pop_data$DER_POP_PCTAGE17_NUM_WEIGHTED
DER_POP_PCTAGE18TO24_NUM <- pop_data$DER_POP_PCTAGE18TO24_NUM_WEIGHTED
DER_POP_PCTAGE25TO34_NUM <- pop_data$DER_POP_PCTAGE25TO34_NUM_WEIGHTED
DER_POP_PCTAGE35TO64_NUM <- pop_data$DER_POP_PCTAGE35TO64_NUM_WEIGHTED
DER_POP_PCTAGEGTE65_NUM <- pop_data$DER_POP_PCTAGEGTE65_NUM_WEIGHTED
DER_POP_PCTSEXMALE_NUM <- pop_data$DER_POP_PCTSEXMALE_NUM_WEIGHTED
DER_POP_PCTSEXFEMALE_NUM <- pop_data$DER_POP_PCTSEXFEMALE_NUM_WEIGHTED
DER_POP_PCTRACEWHITE_NUM <- pop_data$DER_POP_PCTRACEWHITE_NUM_WEIGHTED
DER_POP_PCTRACEBLACK_NUM <- pop_data$DER_POP_PCTRACEBLACK_NUM_WEIGHTED
DER_POP_PCTRACEAIAN_NUM <- pop_data$DER_POP_PCTRACEAIAN_NUM_WEIGHTED
DER_POP_PCTRACEASIAN_NUM <- pop_data$DER_POP_PCTRACEASIAN_NUM_WEIGHTED
DER_POP_PCTRACENHPI_NUM <- pop_data$DER_POP_PCTRACENHPI_NUM_WEIGHTED
POP_TOTAL <- pop_data$POP_TOTAL_WEIGHTED

#Additional variables
DER_POP_PCTAGE_15_17_NUM <- pop_data$DER_POP_PCTAGE_15_17_NUM_WEIGHTED
DER_POP_PCTAGE_UNDER_18_NUM <- pop_data$DER_POP_PCTAGE_UNDER_18_NUM_WEIGHTED
DER_POP_PCTAGE_UNDER_12_NUM <- pop_data$DER_POP_PCTAGE_UNDER_12_NUM_WEIGHTED
DER_POP_PCTAGE_12_17_NUM <- pop_data$DER_POP_PCTAGE_12_17_NUM_WEIGHTED
DER_POP_PCTAGE_OVER_18_NUM <- pop_data$DER_POP_PCTAGE_OVER_18_NUM_WEIGHTED

DER_POP_PCTAGE_12_14_NUM <- pop_data$DER_POP_PCTAGE_12_14_NUM_WEIGHTED

DER_POP_PCT_HISP_NUM <- pop_data$DER_POP_PCT_HISP_NUM_WEIGHTED
DER_POP_PCT_NONHISP_NUM <- pop_data$DER_POP_PCT_NONHISP_NUM_WEIGHTED
DER_POP_PCT_NONHISP_WHITE_NUM <- pop_data$DER_POP_PCT_NONHISP_WHITE_NUM_WEIGHTED
DER_POP_PCT_NONHISP_BLACK_NUM <- pop_data$DER_POP_PCT_NONHISP_BLACK_NUM_WEIGHTED
DER_POP_PCT_NONHISP_AIAN_NUM <- pop_data$DER_POP_PCT_NONHISP_AIAN_NUM_WEIGHTED
DER_POP_PCT_NONHISP_ASIAN_NUM <- pop_data$DER_POP_PCT_NONHISP_ASIAN_NUM_WEIGHTED
DER_POP_PCT_NONHISP_NHOPI_NUM <- pop_data$DER_POP_PCT_NONHISP_NHOPI_NUM_WEIGHTED

#Add on the unweighted population totals

DER_POP_OFFICER_NUM_UNWEIGHTED <- pop_data$DER_POP_OFFICER_NUM
DER_POP_PCTAGELT5_NUM_UNWEIGHTED <- pop_data$DER_POP_PCTAGELT5_NUM
DER_POP_PCTAGE5TO14_NUM_UNWEIGHTED <- pop_data$DER_POP_PCTAGE5TO14_NUM
DER_POP_PCTAGE15_NUM_UNWEIGHTED <- pop_data$DER_POP_PCTAGE15_NUM
DER_POP_PCTAGE16_NUM_UNWEIGHTED <- pop_data$DER_POP_PCTAGE16_NUM
DER_POP_PCTAGE17_NUM_UNWEIGHTED <- pop_data$DER_POP_PCTAGE17_NUM
DER_POP_PCTAGE18TO24_NUM_UNWEIGHTED <- pop_data$DER_POP_PCTAGE18TO24_NUM
DER_POP_PCTAGE25TO34_NUM_UNWEIGHTED <- pop_data$DER_POP_PCTAGE25TO34_NUM
DER_POP_PCTAGE35TO64_NUM_UNWEIGHTED <- pop_data$DER_POP_PCTAGE35TO64_NUM
DER_POP_PCTAGEGTE65_NUM_UNWEIGHTED <- pop_data$DER_POP_PCTAGEGTE65_NUM
DER_POP_PCTSEXMALE_NUM_UNWEIGHTED <- pop_data$DER_POP_PCTSEXMALE_NUM
DER_POP_PCTSEXFEMALE_NUM_UNWEIGHTED <- pop_data$DER_POP_PCTSEXFEMALE_NUM
DER_POP_PCTRACEWHITE_NUM_UNWEIGHTED <- pop_data$DER_POP_PCTRACEWHITE_NUM
DER_POP_PCTRACEBLACK_NUM_UNWEIGHTED <- pop_data$DER_POP_PCTRACEBLACK_NUM
DER_POP_PCTRACEAIAN_NUM_UNWEIGHTED <- pop_data$DER_POP_PCTRACEAIAN_NUM
DER_POP_PCTRACEASIAN_NUM_UNWEIGHTED <- pop_data$DER_POP_PCTRACEASIAN_NUM
DER_POP_PCTRACENHPI_NUM_UNWEIGHTED <- pop_data$DER_POP_PCTRACENHPI_NUM
POP_TOTAL_UNWEIGHTED <- pop_data$POP_TOTAL

#Additional variables
DER_POP_PCTAGE_15_17_NUM_UNWEIGHTED <- pop_data$DER_POP_PCTAGE_15_17_NUM
DER_POP_PCTAGE_UNDER_18_NUM_UNWEIGHTED <- pop_data$DER_POP_PCTAGE_UNDER_18_NUM
DER_POP_PCTAGE_UNDER_12_NUM_UNWEIGHTED <- pop_data$DER_POP_PCTAGE_UNDER_12_NUM
DER_POP_PCTAGE_12_17_NUM_UNWEIGHTED <- pop_data$DER_POP_PCTAGE_12_17_NUM
DER_POP_PCTAGE_OVER_18_NUM_UNWEIGHTED <- pop_data$DER_POP_PCTAGE_OVER_18_NUM

DER_POP_PCTAGE_12_14_NUM_UNWEIGHTED <- pop_data$DER_POP_PCTAGE_12_14_NUM

DER_POP_PCT_HISP_NUM_UNWEIGHTED <- pop_data$DER_POP_PCT_HISP_NUM
DER_POP_PCT_NONHISP_NUM_UNWEIGHTED <- pop_data$DER_POP_PCT_NONHISP_NUM
DER_POP_PCT_NONHISP_WHITE_NUM_UNWEIGHTED <- pop_data$DER_POP_PCT_NONHISP_WHITE_NUM
DER_POP_PCT_NONHISP_BLACK_NUM_UNWEIGHTED <- pop_data$DER_POP_PCT_NONHISP_BLACK_NUM
DER_POP_PCT_NONHISP_AIAN_NUM_UNWEIGHTED <- pop_data$DER_POP_PCT_NONHISP_AIAN_NUM
DER_POP_PCT_NONHISP_ASIAN_NUM_UNWEIGHTED <- pop_data$DER_POP_PCT_NONHISP_ASIAN_NUM
DER_POP_PCT_NONHISP_NHOPI_NUM_UNWEIGHTED <- pop_data$DER_POP_PCT_NONHISP_NHOPI_NUM

#Some code for program
DER_NA_CODE = -9
DER_NA_CODE_STRING = "-9"
DER_GEOGRAPHIC_LOCATION = trimws(pop_data$PERMUTATION_DESCRIPTION, which = "both")
DER_WEIGHT_VARIABLE_STRING = pop_data$WEIGHT_VAR
DER_WEIGHT_VARIABLE_SYMBOL = DER_WEIGHT_VARIABLE_STRING %>% rlang:::parse_expr()
DER_WEIGHT_VARIABLE_FORMULA = paste0("~", DER_WEIGHT_VARIABLE_STRING) %>% as.formula()
DER_TABLE_PATTERN_STRING = "t_(\\w+)_(\\d+)_(\\d+)_(\\d+)"


#Weight file information
DER_ORI_WEIGHT_FILE = "ORI_weights.csv.gz"
DER_ORI_VARIANCE_FILE = "ORI_VARIANCE.csv.gz"

DER_ORI_VARIABLE_STRING = "ori"
DER_ORI_VARIABLE_SYMBOL = DER_ORI_VARIABLE_STRING  %>% rlang:::parse_expr()
DER_ORI_VARIABLE_FORMULA = paste0("~", DER_ORI_VARIABLE_STRING)  %>% as.formula()

DER_ORI_WEIGHT_GROUP_STRING = pop_data$WEIGHT_GROUP_VAR
DER_ORI_WEIGHT_GROUP_SYMBOL = DER_ORI_WEIGHT_GROUP_STRING %>% rlang:::parse_expr()
DER_ORI_WEIGHT_GROUP_FORMULA = paste0("~", DER_ORI_WEIGHT_GROUP_STRING)  %>% as.formula()

DER_ORI_WEIGHT_DESCRIPT_GROUP_ALL_STRING = c("wgtGpNationalDesc", "wgtGpRegionDesc", "wgtGpStateDesc")
DER_ORI_WEIGHT_DESCRIPT_GROUP_ALL_SYMBOL = DER_ORI_WEIGHT_DESCRIPT_GROUP_ALL_STRING %>% rlang:::parse_exprs()

DER_ORI_WEIGHT_DESCRIPT_GROUP_STRING = pop_data$PERMUTATION_DESCRIPTION_VAR
DER_ORI_WEIGHT_DESCRIPT_GROUP_SYMBOL = DER_ORI_WEIGHT_DESCRIPT_GROUP_STRING %>% rlang:::parse_expr()
DER_ORI_WEIGHT_DESCRIPT_GROUP_FORMULA = paste0("~", DER_ORI_WEIGHT_DESCRIPT_GROUP_STRING)  %>% as.formula()

DER_PERMUTATION_SUBSET_STRING = pop_data$PERMUTATION_NUMBER_DESC
DER_PERMUTATION_SUBSET_SYMBOL = DER_PERMUTATION_SUBSET_STRING %>% rlang:::parse_expr()
DER_PERMUTATION_SUBSET_FORMULA = paste0("~", DER_PERMUTATION_SUBSET_STRING)  %>% as.formula()

#Process the DER_ORI_CALIBRATION_MODEL by reading in from workbook
DER_ORI_CALIBRATION_MODEL_STRING_RAW = pop_data$DER_ORI_CALIBRATION_MODEL
#Initial set the flag to false
DER_ORI_CALIBRATION_MODEL_PROCESS = FALSE

#If not missing then set variables
if(!is.na(trimws(DER_ORI_CALIBRATION_MODEL_STRING_RAW, which="both"))){
  #Set the flag to true and assign variables
  DER_ORI_CALIBRATION_MODEL_PROCESS = TRUE

  #Need to add on "_cal" to the variables
  DER_ORI_CALIBRATION_MODEL_STRING =  unlist(strsplit(DER_ORI_CALIBRATION_MODEL_STRING_RAW, split=","))

}else{
  DER_ORI_CALIBRATION_MODEL_STRING <- NA_character_

}

DER_ORI_CALIBRATION_MODEL_SYMBOL = DER_ORI_CALIBRATION_MODEL_STRING %>% rlang:::parse_exprs()
DER_ORI_CALIBRATION_MODEL_FORMULA <- paste0("~", paste(DER_ORI_CALIBRATION_MODEL_STRING, collapse = "+"),"-1")  %>% as.formula()

#New in the POP_TOTAL_PERM_YEAR_FINAL.csv file, there is a variable called DER_ORI_CALIBRATION_MODEL_PROCESS that has
#values of TRUE or FALSE on whether to use the calibration model or not
DER_ORI_USE_CALIBRATION_MODEL = pop_data$DER_ORI_CALIBRATION_MODEL_PROCESS




#Percent Relative Bias information
DER_PRB_FILE = "Relative_Bias_Estimates_Final.RData"
DER_PRB_FILE_NO_EXT = "Relative_Bias_Estimates_Final"
DER_PRB_FILE_SUBSET_STRING = paste0("permutation_number == ", pop_data$PERMUTATION_NUMBER)
DER_PRB_FILE_SUBSET_SYMBOL = DER_PRB_FILE_SUBSET_STRING %>% rlang:::parse_expr()
DER_PRB_VARIABLE_STRING = "percent_relative_bias"
DER_PRB_VARIABLE_SYMBOL <- DER_PRB_VARIABLE_STRING %>% rlang:::parse_expr()

DER_PRB_VARIABLE_IND_STRING = "PRB_ACTUAL"
DER_PRB_VARIABLE_IND_SYMBOL <- DER_PRB_VARIABLE_IND_STRING %>% rlang:::parse_expr()

#Create a function to zero filled the NAs for counts
NA_to_0_count <-function(data, list){
  log_debug("Running POP function NA_to_0_count")
  log_free()
  for(i in 1:length(list) ){
    invar <- list[[i]] %>% rlang:::parse_expr()

    data <- data %>%
      mutate(!!invar := case_when(is.na(!!invar) ~ 0,
                                  TRUE ~ as.double(!!invar)))

  }

  return(data)
}

#Create a function to zero filled the NAs for percentage and include which section to keep NA
NA_to_0_percent <-function(data, list, keepNA){
  log_debug("Running POP function NA_to_0_percent")
  log_free()
  for(i in 1:length(list) ){
    invar <- list[[i]] %>% rlang:::parse_expr()

    data <- data %>%
      mutate(!!invar := case_when(is.na(!!invar) & !(section %in% c(keepNA))  ~ 0,
                                  TRUE ~ as.double(!!invar)))

  }

  return(data)
}

#Add on the functions used for the indicator tables

############################Incident_Id functions##############################################

#Create a function to aggregate counts and calculate the percentages and merge on by incident_id

agg_percent_by_incident_id <- function(leftdata, rightdata, var, section){
  log_debug("Running functionagg_percent_by_incident_id")
  log_free()
  #Change to symbol
  invar <- enquo(var)
  varstring <- deparse(substitute(var))

  #Make a list
  returndata <- vector("list", 2)

  base <- as.data.table(leftdata) %>% merge(rightdata, by=c("incident_id"), all.x = TRUE)
  base <- base[!is.na(get(varstring))]

  #Get the estimates
  returndata[[1]] <- base %>%
    group_by(!!invar) %>%
    mutate(weighted_count = weight *count) %>%
    summarise(final_count = sum(weighted_count)) %>%
    mutate(percent = (final_count / sum(final_count)) * 100,
           section = section) %>%
    ungroup()

  #Create ori level counts - need unweighted counts
  returndata[[2]] <- base %>%
    group_by(ori, !!invar) %>%
    summarise(final_count = sum(count)) %>%
    mutate(#percent = (final_count / sum(final_count)) * 100,
           section = section) %>%
    ungroup()

  #Return the data
  return(returndata)

}

agg_percent_by_incident_id_CAA <- function(leftdata, rightdata, var, section, denom){
  log_debug("Running functionagg_percent_by_incident_id_CAA")
  log_free()
  #Change to symbol
  invar <- enquo(var)
  varstring <- deparse(substitute(var))

  #Make a list
  returndata <- vector("list", 2)

  base <- as.data.table(leftdata) %>% merge(rightdata, by=c("incident_id"), all.x = TRUE)
  base <- base[!is.na(get(varstring))]

  #Get the estimates
  returndata[[1]] <- base %>%
    group_by(!!invar) %>%
    mutate(weighted_count = weight *count) %>%
    summarise(final_count = sum(weighted_count)) %>%
    mutate(percent = (final_count / denom) * 100,
           section = section) %>%
    ungroup()

  #Create ori level counts  - need unweighted counts
  returndata[[2]] <- base %>%
    group_by(ori, !!invar) %>%
    summarise(final_count = sum(count)) %>%
    mutate(#percent = (final_count / denom) * 100,
           section = section) %>%
    ungroup()

  #Return the data
  return(returndata)

}

agg_rate_incident_id_CAA <- function(leftdata, rightdata, var, section, mergeby, denom){
  log_debug("Running POP function agg_rate_incident_id_CAA")
  log_debug(system("free -mh", intern = FALSE))
  #Change to symbol
  invar <- enquo(var)
  varstring <- deparse(substitute(var))

  #Make a list
  returndata <- vector("list", 2)

  base <- as.data.table(leftdata) %>% merge(rightdata, by=mergeby, all.x = TRUE)
  base <- base[!is.na(get(varstring))]
  #Deduplicate by Incident ID and unique invar categories - Need to do this to drop duplicate records cause by offense codes
  base <- base[, .SD[1], by = c("ori", "incident_id", varstring)]

  #Get the estimates
  returndata[[1]] <- base %>%
    group_by(!!invar) %>%
    mutate(weighted_count = weight *count) %>%
    summarise(final_count = (sum(weighted_count) / denom) * 100000) %>% #Multiply for rate:  (per 100k total population)
    mutate(percent = (final_count / denom) * 100,
      population_estimate = denom,
      section = section) %>%
	ungroup()

  #Create ori level counts  - need unweighted counts
  returndata[[2]] <- base %>%
    group_by(ori, !!invar) %>%
    summarise(final_count = sum(count)) %>%
    mutate(#percent = (final_count / denom) * 100,
           section = section) %>%
    ungroup()

  #Return the data
  return(returndata)

}


############################Victim_Id functions##############################################

agg_percent_victim <- function(leftdata, rightdata, var, section, mergeby){
  log_debug("Running POP function agg_percent_victim")
  log_free()
  #Change to symbol
  invar <- enquo(var)
  varstring <- deparse(substitute(var))

  #Make a list
  returndata <- vector("list", 2)

  base <- as.data.table(leftdata) %>% merge(rightdata, by=mergeby, all.x = TRUE)
  base <- base[!is.na(get(varstring))]
  #Deduplicate by Incident ID, victim ID, and unique invar categories - Need to do this to drop duplicate records cause by offense codes
  base <- base[, .SD[1], by = c("ori", "incident_id", "victim_id", varstring)]

  #Get the estimates
  returndata[[1]] <- base %>%
    group_by(!!invar) %>%
    mutate(weighted_count = weight *count) %>%
    summarise(final_count = sum(weighted_count)) %>%
    mutate(percent = (final_count / sum(final_count)) * 100,
           section = section) %>%
	ungroup()

  #Create ori level counts  - need unweighted counts
  returndata[[2]] <- base %>%
    group_by(ori, !!invar) %>%
    summarise(final_count = sum(count)) %>%
    mutate(#percent = (final_count / sum(final_count)) * 100,
           section = section) %>%
    ungroup()


  #Return the data
  return(returndata)

}



agg_percent_CAA_victim <- function(leftdata, rightdata, var, section, mergeby, denom){
  log_debug("Running POP function agg_percent_CAA_victim")
  log_free()
  #Change to symbol
  invar <- enquo(var)
  varstring <- deparse(substitute(var))

  #Make a list
  returndata <- vector("list", 2)

  base <- as.data.table(leftdata) %>% merge(rightdata, by=mergeby, all.x = TRUE)
  base <- base[!is.na(get(varstring))]
  #Deduplicate by Incident ID, victim ID, and unique invar categories - Need to do this to drop duplicate records cause by offense codes
  base <- base[, .SD[1], by = c("ori", "incident_id", "victim_id", varstring)]

  #Get the estimates
  returndata[[1]] <- base %>%
    group_by(!!invar) %>%
    mutate(weighted_count = weight *count) %>%
    summarise(final_count = sum(weighted_count)) %>%
    mutate(percent = (final_count / denom) * 100,
           section = section) %>%
	ungroup()

  #Create ori level counts  - need unweighted counts
  returndata[[2]] <- base %>%
    group_by(ori, !!invar) %>%
    summarise(final_count = sum(count)) %>%
    mutate(#percent = (final_count / denom) * 100,
           section = section) %>%
    ungroup()


  #Return the data
  return(returndata)

}

agg_percent_CAA_victim_rate <- function(leftdata, rightdata, var, section, mergeby, denom){
  log_debug("Running POP function agg_percent_CAA_victim_rate")
  log_free()
  #Change to symbol
  invar <- enquo(var)
  varstring <- deparse(substitute(var))

  #Make a list
  returndata <- vector("list", 2)

  base <- as.data.table(leftdata) %>% merge(rightdata, by=mergeby, all.x = TRUE)
  base <- base[!is.na(get(varstring))]
  #Deduplicate by Incident ID, victim ID, and unique invar categories - Need to do this to drop duplicate records cause by offense codes
  base <- base[, .SD[1], by = c("ori", "incident_id", "victim_id", varstring)]

  #Get the estimates
  returndata[[1]] <- base %>%
    group_by(!!invar) %>%
    mutate(weighted_count = weight *count) %>%
    summarise(final_count = (sum(weighted_count) / denom) * 100000) %>% #Multiply for rate:  (per 100k total population)
    mutate(percent = (final_count / denom) * 100,
      population_estimate = denom,
      section = section) %>%
	ungroup()

  #Create ori level counts  - need unweighted counts
  returndata[[2]] <- base %>%
    group_by(ori, !!invar) %>%
    summarise(final_count = sum(count)) %>%
    mutate(#percent = (final_count / denom) * 100,
           section = section) %>%
    ungroup()

  #Return the data
  return(returndata)

}




keep_to_yes_victim <- function(data, yesstring){
  log_debug("Running POP function keep_to_yes_victim")
  log_free()
  inyesstring <- yesstring %>% rlang:::parse_expr()

  returndata <- data[, .(raw_count = .N), by = .(incident_id, victim_id)]
  returndata <- merge(data, returndata)
  returndata <- returndata[raw_count == 1 | eval(inyesstring)]
  returndata <- returndata[, raw_count := NULL]

  return(returndata)

}

############################Arrestee_Id functions##############################################

agg_percent_arrestee <- function(leftdata, rightdata, var, section, mergeby){
  log_debug("Running POP function agg_percent_arrestee")
  log_free()

  #Change to symbol
  invar <- enquo(var)
  varstring <- deparse(substitute(var))

  #Make a list
  returndata <- vector("list", 2)

  base <- as.data.table(leftdata) %>% merge(rightdata, by=mergeby, all.x = TRUE)
  base <- base[!is.na(get(varstring))]
  #Deduplicate by Incident ID, arrestee ID, and unique invar categories - Need to do this to drop duplicate records cause by offense codes
  base <- base[, .SD[1], by = c("ori", "incident_id", "arrestee_id", varstring)]

  #Get the estimates
  returndata[[1]] <- base %>%
    group_by(!!invar) %>%
    mutate(weighted_count = weight *count) %>%
    summarise(final_count = sum(weighted_count)) %>%
    mutate(percent = (final_count / sum(final_count)) * 100,
           section = section) %>%
    ungroup()

  #Create ori level counts  - need unweighted counts
  returndata[[2]] <- base %>%
    group_by(ori, !!invar) %>%
    summarise(final_count = sum(count)) %>%
    mutate(#percent = (final_count / sum(final_count)) * 100,
           section = section) %>%
    ungroup()

  #Return the data
  return(returndata)

}



agg_percent_CAA_arrestee <- function(leftdata, rightdata, var, section, mergeby, denom){
  log_debug("Running POP function agg_percent_CAA_arrestee")
  log_free()
  #Change to symbol
  invar <- enquo(var)
  varstring <- deparse(substitute(var))

  #Make a list
  returndata <- vector("list", 2)

  base <- as.data.table(leftdata) %>% merge(rightdata, by=mergeby, all.x = TRUE)
  base <- base[!is.na(get(varstring))]
  #Deduplicate by Incident ID, arrestee ID, and unique invar categories - Need to do this to drop duplicate records cause by offense codes
  base <- base[, .SD[1], by = c("ori", "incident_id", "arrestee_id", varstring)]

  #Get the estimates
  returndata[[1]] <- base %>%
    group_by(!!invar) %>%
    mutate(weighted_count = weight *count) %>%
    summarise(final_count = sum(weighted_count)) %>%
    mutate(percent = (final_count / denom) * 100,
           section = section) %>%
    ungroup()

  #Create ori level counts  - need unweighted counts
  returndata[[2]] <- base %>%
    group_by(ori, !!invar) %>%
    summarise(final_count = sum(count)) %>%
    mutate(#percent = (final_count / denom) * 100,
           section = section) %>%
    ungroup()

  #Return the data
  return(returndata)

}

agg_percent_CAA_arrestee_rate <- function(leftdata, rightdata, var, section, mergeby, denom){
  log_debug("Running POP function agg_percent_CAA_arrestee_rate")
  log_free()
  #Change to symbol
  invar <- enquo(var)
  varstring <- deparse(substitute(var))

  #Make a list
  returndata <- vector("list", 2)

  base <- as.data.table(leftdata) %>% merge(rightdata, by=mergeby, all.x = TRUE)
  base <- base[!is.na(get(varstring))]
  #Deduplicate by Incident ID, arrestee ID, and unique invar categories - Need to do this to drop duplicate records cause by offense codes
  base <- base[, .SD[1], by = c("ori", "incident_id", "arrestee_id", varstring)]

  #Get the estimates
  returndata[[1]] <- base %>%
    group_by(!!invar) %>%
    mutate(weighted_count = weight *count) %>%
    summarise(final_count = (sum(weighted_count) / denom) * 100000  ) %>% #Multiply for rate:  (per 100k total population)
    mutate(percent = (final_count / denom) * 100,
      population_estimate = denom,
      section = section) %>%
    ungroup()

  #Create ori level counts  - need unweighted counts
  returndata[[2]] <- base %>%
    group_by(ori, !!invar) %>%
    summarise(final_count = sum(count)) %>%
    mutate(#percent = (final_count / denom) * 100,
           section = section) %>%
    ungroup()

  #Return the data
  return(returndata)

}

keep_to_yes_arrestee <- function(data, yesstring){
  log_debug("Running POP function keep_to_yes_arrestee")
  log_free()
  inyesstring <- yesstring %>% rlang:::parse_expr()

  returndata <- data[, .(raw_count = .N), by = .(incident_id, arrestee_id)]
  returndata <- merge(data, returndata)
  returndata <- returndata[raw_count == 1 | eval(inyesstring)]
  returndata <- returndata[, raw_count := NULL]

  return(returndata)

}

############################Arrestee Group B functions##############################################

agg_percent_arrestee_groupb <- function(leftdata, rightdata, var, section, mergeby){
  log_debug("Running POP function agg_percent_arrestee")
  log_free()
  
  #Change to symbol
  invar <- enquo(var)
  varstring <- deparse(substitute(var))
  
  #Make a list
  returndata <- vector("list", 2)
  
  base <- as.data.table(leftdata) %>% merge(rightdata, by=mergeby, all.x = TRUE)
  base <- base[!is.na(get(varstring))]
  #Deduplicate by Incident ID, arrestee ID, and unique invar categories - Need to do this to drop duplicate records cause by offense codes
  base <- base[, .SD[1], by = c("ori",  "groupb_arrestee_id", varstring)]
  
  #Get the estimates
  returndata[[1]] <- base %>%
    group_by(!!invar) %>%
    mutate(weighted_count = weight *count) %>%
    summarise(final_count = sum(weighted_count)) %>%
    mutate(percent = (final_count / sum(final_count)) * 100,
           section = section) %>%
    ungroup()
  
  #Create ori level counts  - need unweighted counts
  returndata[[2]] <- base %>%
    group_by(ori, !!invar) %>%
    summarise(final_count = sum(count)) %>%
    mutate(#percent = (final_count / sum(final_count)) * 100,
      section = section) %>%
    ungroup()
  
  #Return the data
  return(returndata)
  
}



agg_percent_CAA_arrestee_groupb <- function(leftdata, rightdata, var, section, mergeby, denom){
  log_debug("Running POP function agg_percent_CAA_arrestee")
  log_free()
  #Change to symbol
  invar <- enquo(var)
  varstring <- deparse(substitute(var))
  
  #Make a list
  returndata <- vector("list", 2)
  
  base <- as.data.table(leftdata) %>% merge(rightdata, by=mergeby, all.x = TRUE)
  base <- base[!is.na(get(varstring))]
  #Deduplicate by Incident ID, arrestee ID, and unique invar categories - Need to do this to drop duplicate records cause by offense codes
  base <- base[, .SD[1], by = c("ori", "groupb_arrestee_id", varstring)]
  
  #Get the estimates
  returndata[[1]] <- base %>%
    group_by(!!invar) %>%
    mutate(weighted_count = weight *count) %>%
    summarise(final_count = sum(weighted_count)) %>%
    mutate(percent = (final_count / denom) * 100,
           section = section) %>%
    ungroup()
  
  #Create ori level counts  - need unweighted counts
  returndata[[2]] <- base %>%
    group_by(ori, !!invar) %>%
    summarise(final_count = sum(count)) %>%
    mutate(#percent = (final_count / denom) * 100,
      section = section) %>%
    ungroup()
  
  #Return the data
  return(returndata)
  
}

agg_percent_CAA_arrestee_rate_groupb <- function(leftdata, rightdata, var, section, mergeby, denom){
  log_debug("Running POP function agg_percent_CAA_arrestee_rate")
  log_free()
  #Change to symbol
  invar <- enquo(var)
  varstring <- deparse(substitute(var))
  
  #Make a list
  returndata <- vector("list", 2)
  
  base <- as.data.table(leftdata) %>% merge(rightdata, by=mergeby, all.x = TRUE)
  base <- base[!is.na(get(varstring))]
  #Deduplicate by Incident ID, arrestee ID, and unique invar categories - Need to do this to drop duplicate records cause by offense codes
  base <- base[, .SD[1], by = c("ori", "groupb_arrestee_id", varstring)]
  
  #Get the estimates
  returndata[[1]] <- base %>%
    group_by(!!invar) %>%
    mutate(weighted_count = weight *count) %>%
    summarise(final_count = (sum(weighted_count) / denom) * 100000  ) %>% #Multiply for rate:  (per 100k total population)
    mutate(percent = (final_count / denom) * 100,
           population_estimate = denom,
           section = section) %>%
    ungroup()
  
  #Create ori level counts  - need unweighted counts
  returndata[[2]] <- base %>%
    group_by(ori, !!invar) %>%
    summarise(final_count = sum(count)) %>%
    mutate(#percent = (final_count / denom) * 100,
      section = section) %>%
    ungroup()
  
  #Return the data
  return(returndata)
  
}


############################Generalized functions##############################################
#Create a function to aggregate counts and calculate the percentages and merge on by user supply ids

agg_percent <- function(leftdata, rightdata, var, section, mergeby){
  log_debug("Running POP function agg_percent")
  log_free()
  #Change to symbol
  invar <- enquo(var)
  varstring <- deparse(substitute(var))

  #Make a list
  returndata <- vector("list", 2)

  base <- as.data.table(leftdata) %>% merge(rightdata, by=mergeby, all.x = TRUE)
  base <- base[!is.na(get(varstring))]

  #Get the estimates
  returndata[[1]] <- base %>%
    group_by(!!invar) %>%
    mutate(weighted_count = weight *count) %>%
    summarise(final_count = sum(weighted_count)) %>%
    mutate(percent = (final_count / sum(final_count)) * 100,
           section = section) %>%
    ungroup()

  #Create ori level counts - need unweighted counts
  returndata[[2]] <- base %>%
    group_by(ori, !!invar) %>%
    summarise(final_count = sum(count)) %>%
    mutate(#percent = (final_count / sum(final_count)) * 100,
           section = section) %>%
    ungroup()

  #Return the data
  return(returndata)

}

agg_percent_CAA <- function(leftdata, rightdata, var, section, mergeby, denom){
  log_debug("Running POP function agg_percent_CAA")
  log_free()
  #Change to symbol
  invar <- enquo(var)
  varstring <- deparse(substitute(var))

  #Make a list
  returndata <- vector("list", 2)

  base <- as.data.table(leftdata) %>% merge(rightdata, by=mergeby, all.x = TRUE)
  base <- base[!is.na(get(varstring))]

  #Get the estimates
  returndata[[1]] <- base %>%
    group_by(!!invar) %>%
    mutate(weighted_count = weight *count) %>%
    summarise(final_count = sum(weighted_count)) %>%
    mutate(percent = (final_count / denom) * 100,
           section = section) %>%
    ungroup()

  #Create ori level counts - need unweighted counts
  returndata[[2]] <- base %>%
    group_by(ori, !!invar) %>%
    summarise(final_count = sum(count)) %>%
    mutate(#percent = (final_count / denom) * 100,
           section = section) %>%
    ungroup()

  #Return the data
  return(returndata)

}

#Create a function to aggregate counts and calculate the percentages and merge on by user supply ids

agg_percent_add_weight <- function(leftdata, rightdata, var, section, mergeby, addweight){
  log_debug("Running POP function agg_percent_add_weight")
  log_free()

  #Change to symbol
  invar <- enquo(var)
  inweight <- addweight %>% rlang:::parse_expr()
  varstring <- deparse(substitute(var))

  #Make a list
  returndata <- vector("list", 2)

  base <- as.data.table(leftdata) %>% merge(rightdata, by=mergeby, all.x = TRUE)
  base <- base[!is.na(get(varstring))]

  #Get the estimates
  returndata[[1]] <- base %>%
    group_by(!!invar) %>%
    mutate(weighted_count = weight*!!inweight*count) %>%
    summarise(final_count = sum(weighted_count, na.rm=TRUE)) %>%
    mutate(percent = (final_count / sum(final_count)) * 100,
           section = section) %>%
    ungroup()

  #Create ori level counts - need unweighted counts
  returndata[[2]] <- base %>%
    group_by(ori, !!invar) %>%
    summarise(final_count = sum(!!inweight*count, na.rm=TRUE)) %>%
    mutate(#percent = (final_count / sum(final_count)) * 100,
           section = section) %>%
    ungroup()

  #Return the data
  return(returndata)

}

agg_percent_CAA_add_weight <- function(leftdata, rightdata, var, section, mergeby, denom, addweight){
  log_debug("Running POP function agg_percent_CAA_add_weight")
  log_free()
  #Change to symbol
  invar <- enquo(var)
  inweight <- addweight %>% rlang:::parse_expr()
  varstring <- deparse(substitute(var))

  #Make a list
  returndata <- vector("list", 2)

  base <- as.data.table(leftdata) %>% merge(rightdata, by=mergeby, all.x = TRUE)
  base <- base[!is.na(get(varstring))]

  #Get the estimates
  returndata[[1]] <- base %>%
    group_by(!!invar) %>%
    mutate(weighted_count = weight*!!inweight*count) %>%
    summarise(final_count = sum(weighted_count, na.rm=TRUE)) %>%
    mutate(percent = (final_count / denom) * 100,
           section = section) %>%
    ungroup()

  #Create ori level counts - need unweighted counts
  returndata[[2]] <- base %>%
    group_by(ori, !!invar) %>%
    summarise(final_count = sum(!!inweight*count, na.rm=TRUE)) %>%
    mutate(#percent = (final_count / denom) * 100,
           section = section) %>%
    ungroup()

  #Return the data
  return(returndata)

}



#Create function to deduplicate aggregated counts to recode any values greater than 1 to 1.

agg_to_1 <- function(data){
  log_debug("Running POP function agg_to_1")
  log_free()
  returndata <- data %>%
    mutate(count = case_when(count >= 1 ~ 1,
                            TRUE ~ as.double(count)))

  return(returndata)

}

#Create function to keep the Yes incident

keep_to_yes <- function(data, yesstring){
  log_debug("Running POP function keep_to_yes")
  log_free()
  inyesstring <- yesstring %>% rlang:::parse_expr()

  returndata <- data[, .(raw_count = .N), by = .(incident_id)]
  returndata <- merge(data, returndata)
  returndata <- returndata[raw_count == 1 | eval(inyesstring)]
  returndata <- returndata[, raw_count := NULL]

  return(returndata)

}

clean_main_part_1 <- function(returndata){
  log_debug("Running POP function clean_main_part_1")
  log_free()
  #Need to handle block imputation first

  raw_block_imputation <- fread(paste0(block_imp_path, "NIBRS_INCIDENT_PLUS_IMPUTED_BLOCK.csv.gz"))

  log_debug("After importing raw_block_imputation")
  log_free()

  log_debug("The dim of block imputation data is:")
  log_dim(raw_block_imputation)

  #Need to join by incident_id only, since raw_block_imputation have duplicate incident_id used by donee ORIs.
  #Dataset raw_block_imputation is unique by ori and incident_id
  #When raw_block_imputation is joined by indata by incident_id, there should be more cases since indata contains more than one record by incident_id
  returndata <- merge(raw_block_imputation, returndata[,ori:=NULL], by="incident_id", all.x = TRUE)

  log_debug("After merging raw_block_imputation")
  log_free()
  log_dim(returndata)

  #Removing raw_block_imputation and free up memory
  rm(list=c("raw_block_imputation"))
  gc()

  #print("The dim of input data is:")
  #log_dim(indata)

  log_debug("After GC")
  log_free()

  log_debug("And the number of regular and imputed are:")
  print(table(returndata$der_imputed_incident))

 #Read in the current weight dataset
  raw_weight <- fread(paste0(der_file_path, DER_ORI_WEIGHT_FILE)) %>%
    #Get selected variables needed - Note ori is the NIBRS CDE variable
    select(ori, !!DER_WEIGHT_VARIABLE_SYMBOL, PARENT_POP_GROUP_CODE,	AGENCY_TYPE_NAME,	REGION_CODE,	STATE_ABBR,	der_national)

  log_debug("After reading in the raw_weight dataset:")
  log_free()
  log_dim(raw_weight)

  #Next need to merge on the weight dataset
  returndata <- merge(returndata, raw_weight, by = "ori", all.x = TRUE)

  log_debug("after merging on the weight")
  log_free()
  log_dim(returndata)

  #Removing raw_weight and free up memory
  rm(list=c("raw_weight"))
  gc()

  log_debug("After GC")
  log_free()

  log_debug("Number of weight merges to return data:")
  print(table(returndata$der_national))

  return(returndata)
}


clean_main_part_2 <- function(returndata){
  log_debug("Running POP function clean_main_part_2")
  log_free()
  #Next need to do some subsetting
  returndata <- returndata %>%
	#Filter to the correct permutation
	filter(!!DER_PERMUTATION_SUBSET_SYMBOL)

  log_debug(paste0("after subsetting to ", DER_PERMUTATION_SUBSET_STRING))
  log_free()
  log_dim(returndata)

  gc()
  log_debug("After GC")
  log_free()

  # returndata <- returndata %>%
  #   #Filter to eligible agencies that are given a weight
  #   filter(!!DER_WEIGHT_VARIABLE_SYMBOL > 0) %>%
  #   #Create the weight variable
  #   mutate(
  #     #Create the one variable for unweighted counts
  #     one = 1
  #   )

  returndata <- returndata[eval(parse(text = DER_WEIGHT_VARIABLE_SYMBOL)) > 0]

  log_debug("After subsetting to agencies given weight")

  log_dim(returndata)
  log_free()
  # log_debug("And the number of regular and imputed are:")
  # print(table(returndata$der_imputed_incident))
  #Create the weights
  #returndata <- returndata %>%
  #  mutate(weight = !!DER_WEIGHT_VARIABLE_SYMBOL)

  gc()
  log_debug("After GC")
  log_free()

  returndata <- returndata[, one := 1]
  log_debug("After adding the one variable")
  log_free()

  gc()
  log_debug("After GC")
  log_free()

  returndata <- returndata[, weight := eval(parse(text = DER_WEIGHT_VARIABLE_SYMBOL))]

  log_debug("After calling mutate on weight = !!DER_WEIGHT_VARIABLE_SYMBOL")
  log_dim(returndata)
  log_free()

  gc()
  log_debug("After GC")
  log_free()

  #Return the dataset
  return(returndata)
}

clean_main_part_1_group_b_arrestee <- function(returndata){
  log_debug("Running POP function clean_main_part_1_group_b_arrestee")
  log_free()
  #Need to handle block imputation first
  
  raw_block_imputation <- fread(paste0(block_imp_path, "NIBRS_GROUP_B_ARRESTEE_PLUS_IMPUTED_BLOCK.csv.gz"))
  
  log_debug("After importing raw_block_imputation")
  log_free()
  
  log_debug("The dim of block imputation data is:")
  log_dim(raw_block_imputation)
  
  #Need to join by groupb_arrestee_id only, since raw_block_imputation have duplicate groupb_arrestee_id used by donee ORIs.
  #Dataset raw_block_imputation is unique by ori and groupb_arrestee_id
  #When raw_block_imputation is joined by indata by groupb_arrestee_id, there should be more cases since indata contains more than one record by groupb_arrestee_id
  returndata <- merge(raw_block_imputation, returndata[,ori:=NULL], by="groupb_arrestee_id", all.x = TRUE)
  
  log_debug("After merging raw_block_imputation")
  log_free()
  log_dim(returndata)
  
  #Removing raw_block_imputation and free up memory
  rm(list=c("raw_block_imputation"))
  gc()
  
  #print("The dim of input data is:")
  #log_dim(indata)
  
  log_debug("After GC")
  log_free()
  
  log_debug("And the number of regular and imputed are:")
  print(table(returndata$der_imputed_arrestee))
  
  #Read in the current weight dataset
  raw_weight <- fread(paste0(der_file_path, DER_ORI_WEIGHT_FILE)) %>%
    #Get selected variables needed - Note ori is the NIBRS CDE variable
    select(ori, !!DER_WEIGHT_VARIABLE_SYMBOL, PARENT_POP_GROUP_CODE,	AGENCY_TYPE_NAME,	REGION_CODE,	STATE_ABBR,	der_national)
  
  log_debug("After reading in the raw_weight dataset:")
  log_free()
  log_dim(raw_weight)
  
  #Next need to merge on the weight dataset
  returndata <- merge(returndata, raw_weight, by = "ori", all.x = TRUE)
  
  log_debug("after merging on the weight")
  log_free()
  log_dim(returndata)
  
  #Removing raw_weight and free up memory
  rm(list=c("raw_weight"))
  gc()
  
  log_debug("After GC")
  log_free()
  
  log_debug("Number of weight merges to return data:")
  print(table(returndata$der_national))
  
  return(returndata)
}



clean_main <- function(returndata){
  log_debug("Running POP function clean_main")
  log_free()
  #Need to handle block imputation first
  raw_block_imputation <- fread_logging(paste0(block_imp_path, "NIBRS_INCIDENT_PLUS_IMPUTED_BLOCK.csv.gz"))

  #convert to data tables
  raw_block_imputation <- data.table(raw_block_imputation)
  returndata <- data.table(returndata)

  log_debug("The dim of block imputation data is:")
  log_free()
  log_dim(raw_block_imputation)

  #Need to join by incident_id only, since raw_block_imputation have duplicate incident_id used by donee ORIs.
  #Dataset raw_block_imputation is unique by ori and incident_id
  #When raw_block_imputation is joined by indata by incident_id, there should be more cases since indata contains more than one record by incident_id
  returndata <- merge(raw_block_imputation, returndata[,ori:=NULL], by="incident_id", all.x = TRUE)

  #Removing raw_block_imputation and free up memory
  rm(list=c("raw_block_imputation"))
  gc()

  #print("The dim of input data is:")
  #log_dim(indata)

  log_debug("After merging block imputation by incident ID:")
  log_free()
  log_dim(returndata)

  log_debug("And the number of regular and imputed are:")
  print(table(returndata$der_imputed_incident))

  #Read in the current weight dataset
  raw_weight <- fread_logging(paste0(der_file_path, DER_ORI_WEIGHT_FILE)) %>%
    #Get selected variables needed - Note ori is the NIBRS CDE variable
    select(ori, !!DER_WEIGHT_VARIABLE_SYMBOL, PARENT_POP_GROUP_CODE,	AGENCY_TYPE_NAME,	REGION_CODE,	STATE_ABBR,	der_national)

  raw_weight <- data.table(raw_weight)

  log_debug("After reading in the raw_weight dataset:")
  log_free()
  log_dim(raw_weight)

  #Next need to merge on the weight dataset
  returndata <- merge(returndata, raw_weight, by = "ori", all.x = TRUE)

  #Removing raw_weight and free up memory
  rm(list=c("raw_weight"))
  gc()

  log_debug("after merging on the weight")
  log_free()
  log_dim(returndata)
  
  log_debug("Number of weight merges to return data:")
  print(table(returndata$der_national))

  #Next need to do some subsetting
  returndata <- returndata %>%
	#Filter to the correct permutation
	filter(!!DER_PERMUTATION_SUBSET_SYMBOL)

  log_debug(paste0("after subsetting to ", DER_PERMUTATION_SUBSET_STRING))
  log_free()
  log_dim(returndata)


  # returndata <- returndata %>%
  #   #Filter to eligible agencies that are given a weight
  #   filter(!!DER_WEIGHT_VARIABLE_SYMBOL > 0) %>%
  #   #Create the weight variable
  #   mutate(
  #     #Create the one variable for unweighted counts
  #     one = 1
  #   )

  returndata <- returndata[eval(parse(text = DER_WEIGHT_VARIABLE_SYMBOL)) > 0][, one := 1]

  log_debug("After subsetting to agencies given weight")

  log_dim(returndata)
  log_free()
  log_debug("And the number of regular and imputed are:")
  # print(table(returndata$der_imputed_incident))
  #Create the weights
  # returndata <- returndata %>%
  #   mutate(weight = !!DER_WEIGHT_VARIABLE_SYMBOL)

  returndata <- returndata[, weight := eval(parse(text = DER_WEIGHT_VARIABLE_SYMBOL))]

  log_debug("After calling mutate on weight = !!DER_WEIGHT_VARIABLE_SYMBOL")
  log_dim(returndata)
  log_free()
  #Return the dataset
  return(returndata)
}


############################Variance functions##############################################
merge_on_weights_variance <- function(indata){
  log_debug("Running POP function merge_on_weights_variance")
  log_free()
  #Read in the variance dataset
  raw_variance <- tibble::as_tibble(fread(paste0(der_file_path, DER_ORI_VARIANCE_FILE)))
  
  log_debug("The variance dataset has the following dim:")
  log_dim(raw_variance) 
  
  #Need to subset on the current permutation
  raw_variance <- raw_variance %>%
    filter(!!DER_PERMUTATION_SUBSET_SYMBOL)  %>%
    #select(ori, !!DER_WEIGHT_VARIABLE_SYMBOL, !!DER_ORI_WEIGHT_GROUP_SYMBOL, !!DER_ORI_WEIGHT_DESCRIPT_GROUP_SYMBOL, !!!DER_ORI_CALIBRATION_MODEL_SYMBOL) %>%
    select(ori, county, !!DER_WEIGHT_VARIABLE_SYMBOL, !!DER_ORI_WEIGHT_GROUP_SYMBOL, !!DER_ORI_WEIGHT_DESCRIPT_GROUP_SYMBOL, matches("^V\\d+_\\w+")) %>%
    #Recreate the weight variable
    mutate(raw_weight = as.double(!!DER_WEIGHT_VARIABLE_SYMBOL))
  
  log_debug(paste0("The variance dataset has the following dim after subsetting to ", DER_PERMUTATION_SUBSET_STRING))
  log_dim(raw_variance)
  
  log_debug("The main dataset has the following dim:")
  log_dim(indata)
  
  #Need to merge on by the weight dataset first
  #Also the NIBRS database ori should be the full string current ORI in the Universe file from the weighting task
  returndata <- raw_variance %>%
    left_join(indata %>%
                #Drop the NATIONAL weight variable
                select(-weight) %>%
                #Create an indicator variable
                mutate(in_main_data = 1), by=c("ori")) 
  
  
  #Create new weight variable
  returndata <- returndata %>%
    #mutate(weight = case_when(in_main_data == 1 ~ raw_weight)) %>%
    #20240702 - Discovered that we need to assign weights to pseudo-oris that reports 0 counts
    #The code below will ensure that the original weights are being assigned to all ORIs
    mutate(weight = raw_weight) %>%	
    select(-raw_weight, -in_main_data)
  
  log_debug("After merging, the combined dataset has the following dim:")
  log_dim(returndata)
  
  raw_selected_vars <- returndata  %>%
    colnames() %>%
    str_match(pattern=DER_TABLE_PATTERN_STRING) %>%
    as_tibble() %>%
    #Make sure the variable is a match to the pattern name
    filter(!is.na(V1)) %>%
    #Make the derived variables from variable name
    select(V1) %>%
    pull() 
  
  
  #Zero fill the new den variables
  returndata <- returndata %>%
    mutate_at(all_of(raw_selected_vars), ~replace_na(.,0))
  
  
  #Return the data
  return(returndata)
}

create_table_variables <- function(indata){
  log_debug("Running POP function create_table_variables")
  log_free()
  returndata <- indata %>%
    colnames() %>%
    str_match(pattern=DER_TABLE_PATTERN_STRING) %>%
    as_tibble() %>%
    #Make sure the variable is a match to the pattern name
    filter(!is.na(V1)) %>%
    #Make the derived variables from variable name
    mutate(variable_name = V1,
           table = V2,
           section = as.numeric(V3),
           row = as.numeric(V4),
           column = as.numeric(V5)) %>%
    select(-V1,-V2,-V3,-V4,-V5)
    #select(variable_name, table, section, row, column)

  #Return the data
  return(returndata)

}

drop_rows_from_table <- function(indata, inrow){
  log_debug("Running POP function drop_rows_from_table")
  log_free()
  returndata <- indata %>%
    filter( !(row %in% inrow) )

  return(returndata)

}

clear_cells_from_table <- function(indata){
  log_debug("Running POP function clear_cells_from_table")
  log_free()

  returndata <- indata %>%
    mutate(
      #Non-missing
      population_estimate = case_when(der_cleared_cells == 1 ~ DER_NA_CODE,
                           TRUE ~ population_estimate),
      #Non-missing
      estimate = case_when(der_cleared_cells == 1 ~ DER_NA_CODE,
                           TRUE ~ estimate)
    )

  return(returndata)
}

TOTAL_SE_FUNCTION <- function(indata, invar, inmainprb){
  log_debug("Running POP function TOTAL_SE_FUNCTION")
  log_free()
  vars <- as.character(invar)[2] %>% str_split(" \\+ ") %>% unlist() %>% str_replace_all("(\\\n| )", "")
  if(DER_ORI_CALIBRATION_MODEL_FORMULA == "~NA - 1"){
    indata <- indata %>% select(ori,county,weight,all_of(vars),all_of(DER_ORI_WEIGHT_GROUP_SYMBOL))
  } else {
    indata <- indata %>% select(ori,county,weight,all_of(DER_ORI_CALIBRATION_MODEL_STRING),all_of(vars),all_of(DER_ORI_WEIGHT_GROUP_SYMBOL))
  }
  #Create symbol of invar
  INVAR_FORMULA <- invar
  
  
  #Need to use the dataset as a data.frame
  raw_data_frame <- indata %>%
    mutate(one = 1,
           !!DER_ORI_WEIGHT_GROUP_SYMBOL := as.factor(!!DER_ORI_WEIGHT_GROUP_SYMBOL)
    ) %>%
    as.data.frame()

  
  #Subset the data to respondents
  raw_data_frame_subset <- raw_data_frame %>%
    group_by(!!DER_ORI_WEIGHT_GROUP_SYMBOL) %>%
    mutate(simpwgt=sum(one)/sum(!is.na(weight))) %>%
    rowwise() %>%
    mutate(newfpc=simpwgt^(-1)) %>%					  
    ungroup() %>%
	  #Make sure that that is a positive weight
    filter(!is.na(weight) & weight > 0) %>%
    #Create new ori_county variable
    mutate(ori_county = case_when(
      #If county is na - then just keep ori
      is.na(county) ~ trimws(ori, which="both"),
      #Otherwise add on county
      TRUE ~ paste0(trimws(ori, which="both"),"_", trimws(county, which="both")))) %>%
    as.data.frame()
  
  
  #Test to see if there are any single unit within a stratum
  raw_test_single_unit <- raw_data_frame_subset %>%
    #Make sure group is not missing
    filter(!is.na(!!DER_ORI_WEIGHT_GROUP_SYMBOL)) %>%
    group_by(!!DER_ORI_WEIGHT_GROUP_SYMBOL) %>%
    summarise(raw_count = n() ) %>%
    ungroup() %>%
    #Select the count
    select(raw_count) %>%
    #Check if there are any single unit
    filter(raw_count == 1) %>%
    nrow()
  
  #Turn on option if there are single units
  if(raw_test_single_unit > 0){
    log_debug("Handle single PSU")
    old.op <- options("RG.lonely.psu"="average")    
  }
  
 
    #Method 2:  Using external calibrated weights and full model
    if(DER_ORI_CALIBRATION_MODEL_PROCESS == TRUE & DER_ORI_USE_CALIBRATION_MODEL == TRUE){

      raw_method_2 <- tryCatch(
        #Use the calibrated method
        {
          raw_method_2 <- ext.calibrated(data=raw_data_frame_subset, ids=~ori_county, strata=DER_ORI_WEIGHT_GROUP_FORMULA, weights=~simpwgt, fpc=~newfpc, weights.cal= ~weight, calmodel= DER_ORI_CALIBRATION_MODEL_FORMULA)
        },
        #If above fail, use the designed based
        error = function(cond){
          #Write message regarding fix
          paste0("") %>% as_tibble() %>%
            write_csv(paste0(file_switch_to_design, "TOTAL_SE_FUNCTION_", Sys.getenv("DER_CURRENT_PERMUTATION_NUM"), "_",  Sys.getenv("TABLE_PROGRAM"), ".csv"))

          raw_method_2 <- e.svydesign(   data=raw_data_frame_subset, ids=~ori_county, strata=DER_ORI_WEIGHT_GROUP_FORMULA, weights=~weight, fpc=~newfpc)

          #Return the object
          return(raw_method_2)
        }
      )
    }else{
      #Do not use calibration but use calibrated weights
      raw_method_2 <- e.svydesign(   data=raw_data_frame_subset, ids=~ori_county, strata=DER_ORI_WEIGHT_GROUP_FORMULA, weights=~weight, fpc=~newfpc)
    }

    raw_final <- svystatTM(design=raw_method_2, y=INVAR_FORMULA, estimator = "Total",  vartype= "se", conf.int=TRUE, conf.lev = 0.95)

  #Need to create the name variable
  raw_final2 <- raw_final %>%
    mutate(raw_variable = row.names(.)) %>%
    #Create the additional variables
    mutate(variable = str_match(string=raw_variable, pattern=DER_TABLE_PATTERN_STRING)[,1],
           table   = str_match(string=raw_variable, pattern=DER_TABLE_PATTERN_STRING)[,2],
           section = str_match(string=raw_variable, pattern=DER_TABLE_PATTERN_STRING)[,3] %>% as.numeric(),
           row     = str_match(string=raw_variable, pattern=DER_TABLE_PATTERN_STRING)[,4] %>% as.numeric(),
           column  = str_match(string=raw_variable, pattern=DER_TABLE_PATTERN_STRING)[,5] %>% as.numeric(),
           estimate_type_num = 1)
  

  #Get the PRB on the dataset
  raw_final3 <- raw_final2 %>%
    left_join(inmainprb, by = c("table", "section", "row", "column"))
  
  
  raw_final4 <- raw_final3 %>%
    mutate(
      #Create the standard errors, confidence intervals, and RSE
      estimate_standard_error = SE,
      estimate_prb = !!DER_PRB_VARIABLE_SYMBOL,
      estimate_bias = Total*(estimate_prb / 100),
      estimate_rmse = sqrt((estimate_standard_error^2) + (estimate_bias^2)),
      estimate_upper_bound = Total + 1.96*estimate_rmse,
      estimate_lower_bound = Total - 1.96*estimate_rmse,
      relative_standard_error = SE/Total,
      relative_rmse = estimate_rmse/Total,
      !!DER_PRB_VARIABLE_IND_SYMBOL := !!DER_PRB_VARIABLE_IND_SYMBOL,
      #For double checking totals
      tbd_estimate = Total
    ) %>%
    #Need to add on variables
    select(
      variable, table, section, row, column, estimate_type_num,
      estimate_standard_error, estimate_prb, estimate_bias, estimate_rmse,
      estimate_upper_bound, estimate_lower_bound, 
      relative_standard_error, relative_rmse, !!DER_PRB_VARIABLE_IND_SYMBOL,
      tbd_estimate)
  
  #Get list of variables to be summarized for unweighted counts
  raw_unweighted_vars <- raw_final4 %>%
    select(variable) %>%
    pull() 
  
  
  #New add on the unweighted estimates
  raw_total_estimate <- raw_data_frame_subset %>%
    #Filter to the weight variable of 1
    filter(one == 1) %>%
    #Need to add code to handle the pseudo-ori level
    group_by(ori) %>%
    mutate(der_ori_county_count = n() ) %>%
    ungroup() %>%
    #Create the proportions
    mutate(der_ori_prop = 1 / der_ori_county_count) %>%
    #Do the summarise counts taking account of proportations
    summarise(
      across(
        .cols = all_of(raw_unweighted_vars),
        .fns = ~ {
          sum(der_ori_prop * .x, na.rm=TRUE)
          },
        .names = "{.col}"
      )
    ) %>%
    #Change data from wide to long
    gather(key="variable", value="estimate_unweighted")
  
  
  raw_final5 <- raw_final4 %>%
    left_join(raw_total_estimate, by = c("variable"))
  
  return(raw_final5)
  
}  

RATE_SE_FUNCTION <- function(indatabase, intotalse, inmainprb){
  log_debug("Running POP function RATE_SE_FUNCTION")
  log_free()
  #Get the list of variables by table, section, row, column
  raw_rate_variables <- indatabase %>%
    filter(!is.na(estimate_type_detail_rate)) %>%
    filter(trim_upcase(estimate_type_detail_rate) != DER_NA_CODE_STRING) %>%
    #Keep variables identified for variance estimation
    filter(der_cleared_cells == 0) %>%
    select(table, section, row, column)

  #Merge on information from the TOTAL SE task
  raw_rate_variables2 <- intotalse %>%
    inner_join(raw_rate_variables, by=c("table", "section", "row", "column") ) %>%
    inner_join(inmainprb %>%
                select(table, section, row, column, !!DER_PRB_VARIABLE_SYMBOL) , by=c("table", "section", "row", "column"))


  #Merge on the denominator (i.e. population_estimate)
  raw_rate_variables3 <- raw_rate_variables2 %>%
  left_join(indatabase %>%
              filter(estimate_type_num == 3) %>% #rate
              filter(population_estimate != DER_NA_CODE) %>% #Drop any records with the NA code
              select(table, section, row, column, population_estimate),
              by=c("table", "section", "row", "column")
              ) %>%
  #Using the variables from the TOTAL SE task, divide by the population_estimate to get rates
  mutate(
    #Create tbd variables for QC:
    #Currently tbd_estimate is the total and estimate_standard_error is the total se
    tbd_total =  tbd_estimate,
    tbd_total_se =  estimate_standard_error,
	tbd_total_unweighted = estimate_unweighted,

	population_estimate_unweighted = case_when(
		floor(population_estimate) == floor(DER_POP_OFFICER_NUM) ~ DER_POP_OFFICER_NUM_UNWEIGHTED,
		floor(population_estimate) == floor(DER_POP_PCTAGELT5_NUM) ~ DER_POP_PCTAGELT5_NUM_UNWEIGHTED,
		floor(population_estimate) == floor(DER_POP_PCTAGE5TO14_NUM) ~ DER_POP_PCTAGE5TO14_NUM_UNWEIGHTED,
		floor(population_estimate) == floor(DER_POP_PCTAGE15_NUM) ~ DER_POP_PCTAGE15_NUM_UNWEIGHTED,
		floor(population_estimate) == floor(DER_POP_PCTAGE16_NUM) ~ DER_POP_PCTAGE16_NUM_UNWEIGHTED,
		floor(population_estimate) == floor(DER_POP_PCTAGE17_NUM) ~ DER_POP_PCTAGE17_NUM_UNWEIGHTED,
		floor(population_estimate) == floor(DER_POP_PCTAGE18TO24_NUM) ~ DER_POP_PCTAGE18TO24_NUM_UNWEIGHTED,
		floor(population_estimate) == floor(DER_POP_PCTAGE25TO34_NUM) ~ DER_POP_PCTAGE25TO34_NUM_UNWEIGHTED,
		floor(population_estimate) == floor(DER_POP_PCTAGE35TO64_NUM) ~ DER_POP_PCTAGE35TO64_NUM_UNWEIGHTED,
		floor(population_estimate) == floor(DER_POP_PCTAGEGTE65_NUM) ~ DER_POP_PCTAGEGTE65_NUM_UNWEIGHTED,
		floor(population_estimate) == floor(DER_POP_PCTSEXMALE_NUM) ~ DER_POP_PCTSEXMALE_NUM_UNWEIGHTED,
		floor(population_estimate) == floor(DER_POP_PCTSEXFEMALE_NUM) ~ DER_POP_PCTSEXFEMALE_NUM_UNWEIGHTED,
		floor(population_estimate) == floor(DER_POP_PCTRACEWHITE_NUM) ~ DER_POP_PCTRACEWHITE_NUM_UNWEIGHTED,
		floor(population_estimate) == floor(DER_POP_PCTRACEBLACK_NUM) ~ DER_POP_PCTRACEBLACK_NUM_UNWEIGHTED,
		floor(population_estimate) == floor(DER_POP_PCTRACEAIAN_NUM) ~ DER_POP_PCTRACEAIAN_NUM_UNWEIGHTED,
		floor(population_estimate) == floor(DER_POP_PCTRACEASIAN_NUM) ~ DER_POP_PCTRACEASIAN_NUM_UNWEIGHTED,
		floor(population_estimate) == floor(DER_POP_PCTRACENHPI_NUM) ~ DER_POP_PCTRACENHPI_NUM_UNWEIGHTED,
	
    #Add on additional variables
		floor(population_estimate) == floor(DER_POP_PCTAGE_15_17_NUM) ~ DER_POP_PCTAGE_15_17_NUM_UNWEIGHTED,
		floor(population_estimate) == floor(DER_POP_PCTAGE_UNDER_18_NUM) ~ DER_POP_PCTAGE_UNDER_18_NUM_UNWEIGHTED,
		floor(population_estimate) == floor(DER_POP_PCTAGE_UNDER_12_NUM) ~ DER_POP_PCTAGE_UNDER_12_NUM_UNWEIGHTED,
		floor(population_estimate) == floor(DER_POP_PCTAGE_12_17_NUM) ~ DER_POP_PCTAGE_12_17_NUM_UNWEIGHTED,
		floor(population_estimate) == floor(DER_POP_PCTAGE_OVER_18_NUM) ~ DER_POP_PCTAGE_OVER_18_NUM_UNWEIGHTED,
		floor(population_estimate) == floor(DER_POP_PCTAGE_12_14_NUM) ~ DER_POP_PCTAGE_12_14_NUM_UNWEIGHTED,
		
		floor(population_estimate) == floor(DER_POP_PCT_HISP_NUM) ~ DER_POP_PCT_HISP_NUM_UNWEIGHTED,
		floor(population_estimate) == floor(DER_POP_PCT_NONHISP_NUM) ~ DER_POP_PCT_NONHISP_NUM_UNWEIGHTED,
		floor(population_estimate) == floor(DER_POP_PCT_NONHISP_WHITE_NUM) ~ DER_POP_PCT_NONHISP_WHITE_NUM_UNWEIGHTED,
		floor(population_estimate) == floor(DER_POP_PCT_NONHISP_BLACK_NUM) ~ DER_POP_PCT_NONHISP_BLACK_NUM_UNWEIGHTED,
		floor(population_estimate) == floor(DER_POP_PCT_NONHISP_AIAN_NUM) ~ DER_POP_PCT_NONHISP_AIAN_NUM_UNWEIGHTED,
		floor(population_estimate) == floor(DER_POP_PCT_NONHISP_ASIAN_NUM) ~ DER_POP_PCT_NONHISP_ASIAN_NUM_UNWEIGHTED,
		floor(population_estimate) == floor(DER_POP_PCT_NONHISP_NHOPI_NUM) ~ DER_POP_PCT_NONHISP_NHOPI_NUM_UNWEIGHTED,

    floor(population_estimate) == floor(POP_TOTAL) ~ POP_TOTAL_UNWEIGHTED	
	))

	raw_rate_variables3 <- raw_rate_variables3 %>%
	mutate(

	estimate_unweighted = case_when(population_estimate_unweighted > 0 ~ (tbd_total_unweighted / population_estimate_unweighted) * 100000,
	                                TRUE ~ NA_real_),

    estimate_bias = case_when(population_estimate > 0 ~ tbd_total * (1000/population_estimate) * estimate_prb,
                              TRUE ~ NA_real_),

    #Change Total to rates
    tbd_estimate = case_when(population_estimate > 0 ~ (tbd_total / population_estimate) * 100000,
                             TRUE ~ NA_real_),
    estimate_standard_error = case_when(population_estimate > 0 ~ (tbd_total_se / population_estimate) * 100000,
                             TRUE ~ NA_real_),

    estimate_rmse = sqrt((estimate_standard_error^2) + (estimate_bias^2)),

    estimate_upper_bound = tbd_estimate + 1.96*estimate_rmse,
    estimate_lower_bound = tbd_estimate - 1.96*estimate_rmse,

    relative_standard_error = estimate_standard_error / tbd_estimate, #Should be the same as total since the constant factor should cancel out
    relative_rmse = estimate_rmse/tbd_estimate,

    estimate_type_num = 3
  )

  return(raw_rate_variables3)

}


PERCENTAGE_SE_FUNCTION <- function(indata, invar_denom, intotalse, inprb){

  log_debug("Running POP function PERCENTAGE_SE_FUNCTION")
  log_free()
  
  #Create a list to hold results
  raw_summarise_list <- vector("list", nrow(invar_denom))
  
  
  #Loop thru and create the variables
  indata_dt <- as.data.table(indata)
  for(i in 1:nrow(invar_denom)){
    #Create the variables
    innewvar_str    <- invar_denom[i,"variable"] %>% pull() %>% paste0(.,"_den")
    #Get the variables of the denominator
    indemovarstring <- invar_denom[i,"raw_denominator"] %>% pull() %>% strsplit(split=", ") %>% unlist()

    indata_dt_selected <- indata_dt[,
      # select cols
      c("ori", "county", indemovarstring), with = FALSE]

    indata_dt_filtered <- indata_dt_selected[
      # filter to the ori that is not missing
      !is.na(trimws(ori, which = "both"))]
    
    indata_dt_mutated <- indata_dt_filtered[,
      c(innewvar_str) := rowSums(.SD, na.rm = TRUE), .SDcols = indemovarstring]

    indata_dt_reselected <- indata_dt_mutated[,
      .SD, .SDcols = c("ori", "county", innewvar_str)]

    raw_summarise_list[[i]] <- tibble::as_tibble(indata_dt_reselected)
  }
  
  #Merge on the results
  raw_summarise <- reduce(raw_summarise_list, full_join, by=c("ori", "county"))
  
  #Join the new variables together
  raw_summarise2 <- indata %>%
    select(-(colnames(indata) %>% str_subset("^(?!GV)V\\d+") %>% subset(!. %in% DER_ORI_CALIBRATION_MODEL_STRING))) %>%
    select(-(colnames(indata) %>% str_subset(DER_TABLE_PATTERN_STRING) %>% subset(!. %in% invar_denom$variable))) %>%
    left_join(raw_summarise, by=c("ori", "county"))
  
  
  #Need to zero fill the "t_x_x_x_x_den" variables
  raw_0_var_den_list <- raw_summarise2 %>%
    #Get one row
    head(1) %>%
    #Select the variables that ends in _den
    select(ends_with("_den")) %>%
    #Select the variables that starts with t
    select(starts_with("t_")) %>%
    #Get the column names
    colnames() %>%
    as_tibble() %>%
    pull()
  
  #Zero fill the new den variables
  raw_summarise3 <- raw_summarise2 %>%
    mutate_at(all_of(raw_0_var_den_list), ~replace_na(.,0))
  
  #Next need to create the formula to compute percentages
  raw_variable_numerator     <- paste0("~", paste(invar_denom %>% select(variable) %>% pull(), collapse="+")) %>% as.formula()
  raw_variable_denominator   <- paste0("~", paste( paste0(invar_denom %>% select(variable) %>% pull(),"_den"), collapse="+")) %>% as.formula()
  
  
  #Create the Regenesees version
  
  #Need to use the dataset as a data.frame
  raw_data_frame <- raw_summarise3 %>%
    mutate(one = 1,
           !!DER_ORI_WEIGHT_GROUP_SYMBOL := as.factor(!!DER_ORI_WEIGHT_GROUP_SYMBOL)
    ) %>%
    as.data.frame()
  
  #Subset the data to respondents
  raw_data_frame_subset <- raw_data_frame %>%
    group_by(!!DER_ORI_WEIGHT_GROUP_SYMBOL) %>%
    mutate(simpwgt=sum(one)/sum(!is.na(weight))) %>%
    rowwise() %>%
    mutate(newfpc=simpwgt^(-1)) %>%
    ungroup() %>%
    #Make sure that that is a positive weight
    filter(!is.na(weight) & weight > 0) %>%
    #Create new ori_county variable
    mutate(ori_county = case_when(
      #If county is na - then just keep ori
      is.na(county) ~ trimws(ori, which="both"),
      #Otherwise add on county
      TRUE ~ paste0(trimws(ori, which="both"),"_", trimws(county, which="both")))) %>%
    #Need to add code to handle the pseudo-ori level
    group_by(ori) %>%
    mutate(der_ori_county_count = n() ) %>%
    ungroup() %>%
    #Create the proportions
    mutate(der_ori_prop = 1 / der_ori_county_count) %>%
    as.data.frame()

  
  #Test to see if there are any single unit within a stratum
  raw_test_single_unit <- raw_data_frame_subset %>%
    #Make sure group is not missing
    filter(!is.na(!!DER_ORI_WEIGHT_GROUP_SYMBOL)) %>%
    group_by(!!DER_ORI_WEIGHT_GROUP_SYMBOL) %>%
    summarise(raw_count = n() ) %>%
    ungroup() %>%
    #Select the count
    select(raw_count) %>%
    #Check if there are any single unit
    filter(raw_count == 1) %>%
    nrow()
  
  #Turn on option if there are single units
  if(raw_test_single_unit > 0){
    log_debug("Handle single PSU")
    old.op <- options("RG.lonely.psu"="average")    
  }  
  
      #Method 2:  Using external calibrated weights and full model
    if(DER_ORI_CALIBRATION_MODEL_PROCESS == TRUE & DER_ORI_USE_CALIBRATION_MODEL == TRUE){
      raw_method_2 <- tryCatch(
        #Use the calibrated method
        {
          raw_method_2 <- ext.calibrated(data=raw_data_frame_subset, ids=~ori_county, strata=DER_ORI_WEIGHT_GROUP_FORMULA, weights=~simpwgt, fpc=~newfpc, weights.cal= ~weight, calmodel= DER_ORI_CALIBRATION_MODEL_FORMULA)
        },
        #If above fail, use the designed based
        error = function(cond){
          #Write message regarding fix
          paste0("") %>% as_tibble() %>%
            write_csv(paste0(file_switch_to_design, "PERCENTAGE_SE_FUNCTION_", Sys.getenv("DER_CURRENT_PERMUTATION_NUM"), "_",  Sys.getenv("TABLE_PROGRAM"), ".csv"))

          raw_method_2 <- e.svydesign(   data=raw_data_frame_subset, ids=~ori_county, strata=DER_ORI_WEIGHT_GROUP_FORMULA, weights=~weight, fpc=~newfpc)

          #Return the object
          return(raw_method_2)
        }
      )
    }else{
      #Do not use calibration but use calibrated weights
      raw_method_2 <- e.svydesign(   data=raw_data_frame_subset, ids=~ori_county, strata=DER_ORI_WEIGHT_GROUP_FORMULA, weights=~weight, fpc=~newfpc)
    }
    
    #Calculate the weighted estimates
    raw_final <- svystatR(design=raw_method_2, num=raw_variable_numerator, den=raw_variable_denominator, vartype= "se") %>%
      mutate(tbd_estimate = Ratio * 100,
             estimate_standard_error = SE * 100, 
             #Split between the numerator and denominator variables
             raw_variable =str_split(row.names(.), pattern="/", n=1)) %>%
      #Create the two variables
      separate(raw_variable, c("raw_variable_num", "raw_variable_den"), "/") %>%
      mutate(variable = str_match(string=raw_variable_num, pattern=DER_TABLE_PATTERN_STRING)[,1],
             table   = str_match(string=raw_variable_num, pattern=DER_TABLE_PATTERN_STRING)[,2],
             section = str_match(string=raw_variable_num, pattern=DER_TABLE_PATTERN_STRING)[,3] %>% as.numeric(),
             row     = str_match(string=raw_variable_num, pattern=DER_TABLE_PATTERN_STRING)[,4] %>% as.numeric(),
             column  = str_match(string=raw_variable_num, pattern=DER_TABLE_PATTERN_STRING)[,5] %>% as.numeric(),
             estimate_type_num = 2)
    
    
    
    #New set up for unweighted counts
    #Use variable der_ori_prop for proportions
    raw_method_unweighted <- e.svydesign(   data=raw_data_frame_subset %>% select(-(colnames(raw_data_frame_subset) %>% str_subset("^(?!GV)V\\d+"))), ids=~ori_county, strata=DER_ORI_WEIGHT_GROUP_FORMULA, weights=~der_ori_prop, fpc=~newfpc)
    
    #Calculate the unweighted estimates
    raw_final_unweighted <- svystatR(design=raw_method_unweighted, num=raw_variable_numerator, den=raw_variable_denominator) %>%
      mutate(estimate_unweighted = Ratio * 100,
             #Split between the numerator and denominator variables
             raw_variable =str_split(row.names(.), pattern="/", n=1)) %>%
      #Create the two variables
      separate(raw_variable, c("raw_variable_num", "raw_variable_den"), "/") %>%
      mutate(variable = str_match(string=raw_variable_num, pattern=DER_TABLE_PATTERN_STRING)[,1],
             table   = str_match(string=raw_variable_num, pattern=DER_TABLE_PATTERN_STRING)[,2],
             section = str_match(string=raw_variable_num, pattern=DER_TABLE_PATTERN_STRING)[,3] %>% as.numeric(),
             row     = str_match(string=raw_variable_num, pattern=DER_TABLE_PATTERN_STRING)[,4] %>% as.numeric(),
             column  = str_match(string=raw_variable_num, pattern=DER_TABLE_PATTERN_STRING)[,5] %>% as.numeric(),
             estimate_type_num = 2) %>%
      select(variable, estimate_unweighted)
    
    #Create object raw_percentage4 to be consistent with previous code
    raw_percentage4 <- raw_final %>%
      left_join(raw_final_unweighted, by=c("variable"))
    
  
  #Need to get the percent relative bias and Total using intotalse
  #Get the PRB on the dataset:  inprb
  raw_prb_trans <- inprb %>%
    mutate(variable = paste0("t_",table,"_",section,"_",row,"_",column)) %>%
    select(variable,der_all_counts) %>%
    spread(key=variable, value=der_all_counts)
  
  #Create a list to hold results
  raw_summarise_prb_list <- vector("list", nrow(invar_denom))
  
  
  #Loop thru and create the variables
  setDT(raw_prb_trans)
  for(i in 1:nrow(invar_denom)){
    #Create the variables
    invar          <- invar_denom[i,"variable"] %>% pull() %>% rlang:::parse_expr()
    #Get the variables of the denominator
    indemovarstring <- invar_denom[i,"raw_denominator"] %>% pull() %>% strsplit(split=", ") %>% unlist()
    invarstring     <- invar_denom[i,"variable"] %>% pull()
    
    #Save the results to the list.
    selected_raw_prb_trans <- raw_prb_trans[, unique(c(invarstring, indemovarstring)), with = FALSE]

    mutated_raw_prb_trans <- selected_raw_prb_trans[,
      `:=`(raw_ALL_bias_num = get(invar),
          raw_ALL_bias_den = rowSums(.SD, na.rm = TRUE),
          variable = invarstring), .SDcols = indemovarstring]

    raw_summarise_prb_list[[i]] <- mutated_raw_prb_trans[,
      .SD, .SDcols = c("variable", "raw_ALL_bias_num", "raw_ALL_bias_den")]    
  }
  
  #Merge on the results for the estimate_bias estimate
  raw_prb_summarise <- bind_rows(raw_summarise_prb_list)
  
  
  
  #Merge on the results
  raw_percentage5 <- raw_percentage4 %>%
    left_join(raw_prb_summarise, by=c("variable"))
  
  
  #Next need to use the intotalse to get the following:  
  #tbd_estimate -> raw_total
  #estimate_prb -> raw_prb_value
  #!!DER_PRB_VARIABLE_IND_SYMBOL -> raw_prb_ind_value
  
  raw_total_se <- intotalse %>%
    select(variable,
           raw_total = tbd_estimate,
           raw_prb_value = estimate_prb,
           raw_prb_ind_value = !!DER_PRB_VARIABLE_IND_SYMBOL)
  
  
  raw_percentage6 <- raw_percentage5 %>%
    left_join(raw_total_se, by=c("variable"))
  
  
  raw_percentage7 <- raw_percentage6 %>%
    mutate(
      #Create the standard errors, confidence intervals, and RSE
      #estimate_standard_error = SE, Create above
      tbd_total = raw_total,
      estimate_prb = raw_prb_value,
      estimate_bias = (tbd_estimate) - ((raw_ALL_bias_num/raw_ALL_bias_den) *100),
      estimate_rmse = sqrt((estimate_standard_error^2) + (estimate_bias^2)),
      estimate_upper_bound = tbd_estimate + 1.96*estimate_rmse,
      estimate_lower_bound = tbd_estimate - 1.96*estimate_rmse,
      relative_standard_error = estimate_standard_error/tbd_estimate,
      relative_rmse = estimate_rmse/tbd_estimate,  
      
      !!DER_PRB_VARIABLE_IND_SYMBOL := raw_prb_ind_value,
      
      estimate_type_num = 2 # For percentages
    )
  
  return(raw_percentage7)
  
}

TOTAL_COUNT_FUNCTION <- function(indata, invar){
  log_debug("Running POP function TOTAL_COUNT_FUNCTION")
  log_free()
  indata <- indata %>% select(ori,weight,all_of(invar))
  invarsymbol <- invar %>% rlang:::parse_expr()
  
  # Filter to rows that have have weights greater than 0
  indata <- indata[weight > 0]
  
  # Count the number of counties that have the same ORI by grouping; then ungroup to two columns
  indata <- indata[, der_ori_county_count := .N, by = ori][,
                 .SD, 
                 .SDcols = c(invar, "der_ori_county_count")][]
  
  # Create a proportion column by dividing 1 by the number of counties associated with an ori
  indata <- indata[, der_ori_prop := 1 / der_ori_county_count]
  
  # Confirm that the counts should be the pseduo-ori (i.e. ori counts multiple times if in more than one county)
  indata <- indata[, raw_agency_counts := fcase(
    eval(invarsymbol) > 0, 1,
    default = 0
  )]
  
  print(str_match(string=invar, pattern=DER_TABLE_PATTERN_STRING)[,1])
  # Summarise the unweighted counts and agency counts
  # Extract the components from the invar string
  components <- strsplit(invar, "_")[[1]]
  # If there are not enough components, pad the vector with NAs
  if (length(components) < 5) {
    components <- c(components, rep(NA, 5 - length(components)))
  }
  
  # Summarise the unweighted counts and agency counts
  # indata <- indata[, .(unweighted_counts = sum(der_ori_prop * ifelse(!is.null(get(invarstr)), get(invarstr), 0), na.rm = TRUE),
  indata <- indata[, .(unweighted_counts = sum(der_ori_prop * eval(invarsymbol), na.rm = TRUE),
                       agency_counts = sum(raw_agency_counts, na.rm = TRUE)),
                   by = .(
                          variable = rep(str_match(string=invar, pattern=DER_TABLE_PATTERN_STRING)[,1], nrow(indata)),
                          table = rep(str_match(string=invar, pattern=DER_TABLE_PATTERN_STRING)[,2], nrow(indata)),
                          section = rep(str_match(string=invar, pattern=DER_TABLE_PATTERN_STRING)[,3] %>% as.numeric(), nrow(indata)),
                          row = rep(str_match(string=invar, pattern=DER_TABLE_PATTERN_STRING)[,4] %>% as.numeric(), nrow(indata)),
                          column = rep(str_match(string=invar, pattern=DER_TABLE_PATTERN_STRING)[,5] %>% as.numeric(), nrow(indata)))]
  
  return(indata)
}

#Create new POPULATION variables that maybe used for coverage ratio
POPUALATION_VARIABLE_FUNCTION <- function(indata){
  log_debug("Running POP function POPUALATION_VARIABLE_FUNCTION")
  log_free()
  final_data <- indata %>%
    mutate(
      POP_TOTAL = pop_data$POP_TOTAL_WEIGHTED,
      POP_TOTAL_UNWEIGHTED = pop_data$POP_TOTAL,

	  #Need to update the population_estimate variable from National to subnational specfic
	  population_estimate = case_when(
		floor(population_estimate) == floor(DER_POP_OFFICER_NUM_NATIONAL) ~ DER_POP_OFFICER_NUM,
		floor(population_estimate) == floor(DER_POP_PCTAGELT5_NUM_NATIONAL) ~ DER_POP_PCTAGELT5_NUM,
		floor(population_estimate) == floor(DER_POP_PCTAGE5TO14_NUM_NATIONAL) ~ DER_POP_PCTAGE5TO14_NUM,
		floor(population_estimate) == floor(DER_POP_PCTAGE15_NUM_NATIONAL) ~ DER_POP_PCTAGE15_NUM,
		floor(population_estimate) == floor(DER_POP_PCTAGE16_NUM_NATIONAL) ~ DER_POP_PCTAGE16_NUM,
		floor(population_estimate) == floor(DER_POP_PCTAGE17_NUM_NATIONAL) ~ DER_POP_PCTAGE17_NUM,
		floor(population_estimate) == floor(DER_POP_PCTAGE18TO24_NUM_NATIONAL) ~ DER_POP_PCTAGE18TO24_NUM,
		floor(population_estimate) == floor(DER_POP_PCTAGE25TO34_NUM_NATIONAL) ~ DER_POP_PCTAGE25TO34_NUM,
		floor(population_estimate) == floor(DER_POP_PCTAGE35TO64_NUM_NATIONAL) ~ DER_POP_PCTAGE35TO64_NUM,
		floor(population_estimate) == floor(DER_POP_PCTAGEGTE65_NUM_NATIONAL) ~ DER_POP_PCTAGEGTE65_NUM,
		floor(population_estimate) == floor(DER_POP_PCTSEXMALE_NUM_NATIONAL) ~ DER_POP_PCTSEXMALE_NUM,
		floor(population_estimate) == floor(DER_POP_PCTSEXFEMALE_NUM_NATIONAL) ~ DER_POP_PCTSEXFEMALE_NUM,
		floor(population_estimate) == floor(DER_POP_PCTRACEWHITE_NUM_NATIONAL) ~ DER_POP_PCTRACEWHITE_NUM,
		floor(population_estimate) == floor(DER_POP_PCTRACEBLACK_NUM_NATIONAL) ~ DER_POP_PCTRACEBLACK_NUM,
		floor(population_estimate) == floor(DER_POP_PCTRACEAIAN_NUM_NATIONAL) ~ DER_POP_PCTRACEAIAN_NUM,
		floor(population_estimate) == floor(DER_POP_PCTRACEASIAN_NUM_NATIONAL) ~ DER_POP_PCTRACEASIAN_NUM,
		floor(population_estimate) == floor(DER_POP_PCTRACENHPI_NUM_NATIONAL) ~ DER_POP_PCTRACENHPI_NUM,
				#Additional rates
		floor(population_estimate) == floor(DER_POP_PCTAGE_15_17_NUM_NATIONAL) ~ DER_POP_PCTAGE_15_17_NUM,
		floor(population_estimate) == floor(DER_POP_PCTAGE_UNDER_18_NUM_NATIONAL) ~ DER_POP_PCTAGE_UNDER_18_NUM,
		floor(population_estimate) == floor(DER_POP_PCTAGE_UNDER_12_NUM_NATIONAL) ~ DER_POP_PCTAGE_UNDER_12_NUM,
		floor(population_estimate) == floor(DER_POP_PCTAGE_12_17_NUM_NATIONAL) ~ DER_POP_PCTAGE_12_17_NUM,
		floor(population_estimate) == floor(DER_POP_PCTAGE_OVER_18_NUM_NATIONAL) ~ DER_POP_PCTAGE_OVER_18_NUM,
		floor(population_estimate) == floor(DER_POP_PCTAGE_12_14_NUM_NATIONAL) ~ DER_POP_PCTAGE_12_14_NUM,
		
		floor(population_estimate) == floor(DER_POP_PCT_HISP_NUM_NATIONAL) ~ DER_POP_PCT_HISP_NUM,
		floor(population_estimate) == floor(DER_POP_PCT_NONHISP_NUM_NATIONAL) ~ DER_POP_PCT_NONHISP_NUM,
		floor(population_estimate) == floor(DER_POP_PCT_NONHISP_WHITE_NUM_NATIONAL) ~ DER_POP_PCT_NONHISP_WHITE_NUM,
		floor(population_estimate) == floor(DER_POP_PCT_NONHISP_BLACK_NUM_NATIONAL) ~ DER_POP_PCT_NONHISP_BLACK_NUM,
		floor(population_estimate) == floor(DER_POP_PCT_NONHISP_AIAN_NUM_NATIONAL) ~ DER_POP_PCT_NONHISP_AIAN_NUM,
		floor(population_estimate) == floor(DER_POP_PCT_NONHISP_ASIAN_NUM_NATIONAL) ~ DER_POP_PCT_NONHISP_ASIAN_NUM,
		floor(population_estimate) == floor(DER_POP_PCT_NONHISP_NHOPI_NUM_NATIONAL) ~ DER_POP_PCT_NONHISP_NHOPI_NUM,
		
		
		
		#Default
		floor(population_estimate) == floor(POP_TOTAL_NATIONAL) ~ POP_TOTAL,


		TRUE ~ population_estimate #For the remaining cases (i.e. the DER_NA_CODE)
	),

	#Update estimate_geographic_location
	estimate_geographic_location = DER_GEOGRAPHIC_LOCATION,

	#Update analysis_weight_name
	analysis_weight_name = DER_WEIGHT_VARIABLE_STRING


	  )

   return(final_data)
}



#Define the list of final estimates
final_variance_vars <- c(
  "estimate_standard_error",
  "estimate_prb",
  "estimate_bias",
  "estimate_rmse",
  "estimate_upper_bound",
  "estimate_lower_bound",
  "relative_standard_error",
  "relative_rmse",
  "tbd_estimate",
  "unweighted_counts",
  "agency_counts",
  "estimate_unweighted",
  "population_estimate_unweighted",
  DER_PRB_VARIABLE_IND_STRING
)

#Handle the permutation series of Race, Age Groups, and Gender for selected tables
process_permutation_series <- function(indata, IN_DER_CURRENT_PERMUTATION_NUM){
  log_debug("Running POP function process_permutation_series")
  log_free()
	raw_variable_name_dataset <- indata %>%
		colnames() %>%
		str_match(pattern="t_(\\w+)_(\\d+)_(\\d+)_(\\d+)") %>%
		as_tibble() %>%
		#Make sure the variable is a match to the pattern name
		filter(!is.na(V1)) %>%
		#Make the derived variables from variable name
		mutate(variable_name = V1,
			   table = V2,
			   section = as.numeric(V3),
			   row = as.numeric(V4),
			   column = as.numeric(V5)) %>%
		#Drop the raw variable names
		select(-V1,-V2,-V3,-V4,-V5) %>%
		#Find out the current permutation number
		mutate(	tbd_keep_column_series =
				#x divided by y but rounded down (integer divide)
				IN_DER_CURRENT_PERMUTATION_NUM %/% 1000) %>%
		#Keep the columns in the permutation series
		filter(column %/% 1000 == tbd_keep_column_series) %>%
		#Create the new column
		mutate(	tbd_new_column = column - (tbd_keep_column_series*1000),
				tbd_new_variable = paste0("t_", table, "_", section, "_", row, "_", tbd_new_column)
		)

	#Need to keep the variable of interest
	raw_keep_vars <- raw_variable_name_dataset %>%
	  select(variable_name, tbd_new_variable)

	#Keep the variables for selected permutation series
	raw_keep_vars_column <- raw_variable_name_dataset %>%
	  select(variable_name) %>%
	  pull() %>%
	  rlang:::parse_exprs()


	#Keep the variables of interest
	raw_variable_name_dataset2 <- indata %>%
	  select(
	  #Usual variables
		ori, weight,
		#Selected variables
		!!!raw_keep_vars_column)

	#Need to do the rename
  for(i in 1:nrow(raw_keep_vars)){

    #Get the old variable name
    in_old_name <- raw_keep_vars[i,] %>% select(variable_name)    %>% pull() %>% rlang:::parse_expr()
    in_new_name <- raw_keep_vars[i,] %>% select(tbd_new_variable) %>% pull() %>% rlang:::parse_expr()

    #Do the rename for each loop
    raw_variable_name_dataset2 <- raw_variable_name_dataset2 %>%
      rename(!!in_new_name := !!in_old_name)
  }


	#Return the object
	return(raw_variable_name_dataset2)


}


#Get the list of variables without the column number
gettable_section_row <- function(indata){
  log_debug("Running POP function gettable_section_row")
  log_free()
  returndata <- colnames(indata)  %>%
    as_tibble() %>%
    pull()%>%
    str_match(pattern="t_(\\w+)_(\\d+)_(\\d+)_(\\d+)") %>%
    as_tibble() %>%
    filter(!is.na(V1)) %>%
    set_names("variable_name", "table", "section", "row", "column") %>%
    mutate(key_var = paste0("t_", table, "_", section, "_", row, "_")) %>%
    select(key_var)

  return(returndata)

}

#This function will aggregate at the ORI level dataset indicators in two different columns in the Indicator Tables
#incombined is the "data" object that contains the ORI dataset that needs the counts to be increased by the "inadditional" data object.
#Just need to update the ORI file only - which is in the 3rd object that needs to be pass in

combinedoris <- function(incombined, inadditional, incombinednum, inadditionalnum){
  log_debug("Running POP function combinedoris")
  log_free()
  #Just need to update the ORI file only
  raw_data_combined <- incombined
  raw_data_add      <- inadditional


  #Get the variables
  raw_data_add_names <-      raw_data_add      %>% gettable_section_row()
  raw_data_combined_names <- raw_data_combined %>% gettable_section_row()

  #Do the joins to get the names
  raw_data_combined_names_full <- raw_data_add_names %>%
    full_join(raw_data_combined_names, by="key_var") %>%
    pull()

  #Merge on the ORI dataset
  raw_data_combined_ori <- raw_data_add %>%
    full_join(raw_data_combined, by=c("ori"))

  log_dim(raw_data_add)
  log_dim(raw_data_combined)
  log_dim(raw_data_combined_ori)

  #Need to loop thru and edit the counts
  #purrr:::walk(raw_data_combined_names_full, ~{
  for(i in 1:length(raw_data_combined_names_full)){

    #Declare the variable
    .x <- raw_data_combined_names_full[[i]]

    #The variable that is going to receive the aggregate value from inadditional
    infinalvar = paste0(.x,incombinednum) %>% rlang:::parse_expr()

    #Initialize combined variable
    insum = vector("list", 2)
    incounter = 1

    #Need to check if variable exists
    if(paste0(.x,incombinednum) %in% paste0(raw_data_combined_names %>% pull(),incombinednum)){
      insum[[incounter]] <- paste0(.x,incombinednum)
      incounter = incounter + 1
    }else{
      log_debug(paste0("Note Variable ", .x, incombinednum, " does not exist."))
    }

    if(paste0(.x,inadditionalnum) %in% paste0(raw_data_add_names %>% pull(),inadditionalnum)){
      insum[[incounter]] <- paste0(.x,inadditionalnum)
      incounter = incounter + 1
    }else{
      log_debug(paste0("Note Variable ", .x, inadditionalnum, " does not exist."))
    }

    #Create combined variable
    insum2 <- insum %>% unlist() %>% rlang:::parse_exprs()

  #Overwrite the ORI file to add up the new counts
  raw_data_combined_ori <- raw_data_combined_ori %>%
    #Add up the results
    rowwise() %>%
    mutate(!!infinalvar := sum(!!!insum2, na.rm=TRUE))

  }
  #Return the ori file and drop the variables from the inadditional data object
  return(raw_data_combined_ori %>% select(-ends_with(paste0("_", inadditionalnum %>% as.character() ))))
}

#Create a 2nd version that doesn't depend on estimate_type_num
CREATE_PERCENTAGE_DENOMINATOR2 <- function(indata, inrow, incolumn){
  log_debug("Running POP function CREATE_PERCENTAGE_DENOMINATOR2")
  log_free()
  returndata <- indata %>%
    filter(column == incolumn) %>%
    #filter(estimate_type_num == 2) %>%
    filter(row %in% inrow) %>%
    select(variable_name) %>%
    filter(!is.na(variable_name) ) %>%
    pull()

  return(returndata)

}

#This new function will add on additional columns when transposing the data fails to produce
#all variables from instartnum to inmaxnum
add_new_columns_to_extract <- function(indata, inprefix, instartnum, inmaxnum){

  log_debug("Running add_new_columns_to_extract function")

  #Create the return data
  return_data <- indata
  
  
  #Get the columns
  tbd_1 <- colnames(indata) %>%
    as_tibble() %>%
    mutate(
      der_keep = str_detect(string=value, pattern=inprefix),
      der_col_num = str_match(string=value, pattern="_(\\d+)$")[,2] %>% as.numeric(),
      der_in_column = 1
    ) %>%
    #Keep variables of interest
    filter(der_keep == TRUE)
  
  #Create the filler dataset
  tbd_filler <- data.frame(
    der_col_num = c(instartnum:inmaxnum)
  ) %>% mutate(
    der_new_var = paste0(inprefix, "_", der_col_num), 
    der_in_filler = 1
  )
  
  
  #Combine the dataset
  tbd_create_vars <- tbd_1 %>%
    full_join(tbd_filler, by=c("der_col_num")) %>%
    mutate(
      der_new_var = paste0(inprefix, "_", der_col_num)
    ) %>%
    #Keep the new variables
    filter(der_in_filler == 1 & is.na(der_in_column) ) %>%
    select(der_new_var) %>%
    pull()
  
  #Run if TRUE to create additional variables
  if(length(tbd_create_vars) > 0 ){
    
    for(i in 1:length(tbd_create_vars)){
      
      log_debug(paste0("add_new_columns_to_extract:  Creating new variable:  ", tbd_create_vars[[i]]))
      
      #Create the symbol
      tbd_current_var_sym = tbd_create_vars[[i]] %>% rlang:::parse_expr()
      
      #Create the new variables
      return_data <- return_data %>%
        mutate(
          #Create zero counts for new variables
          !!(tbd_current_var_sym) := 0
        )
      
      #Delete the tbd_current_var_sym for next cycle
      rm(tbd_current_var_sym)
      
    }
  }
  
  #Return the data
  return(return_data)

}
