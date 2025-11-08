#title: 'NIBRS Partial Reporting'
#author: "Philip Lee"
#date: "May 22, 2019"


library(dplyr)
library(dbplyr)
library(tidyverse)
library(DT)
library(bit64)
library(rjson)

# read in logging functions
source(here::here("tasks/logging.R"))

outputPipelineDir <- Sys.getenv("OUTPUT_PIPELINE_DIR")
queried_data_path = paste0(outputPipelineDir, "/initial_tasks_output/database_queries/") # path where queried data is stored
year <- as.integer(Sys.getenv("DATA_YEAR"))
list_of_years <- seq(year - 4, year)

artifactPath <- sprintf("%s/artifacts", outputPipelineDir)

if (! dir.exists(artifactPath)) {
    dir.create(artifactPath, recursive = TRUE)
}

log_info("generate_partial_reporters.R starting...")

#Edit for 1993 - 2023 update, need to tweak the amount of files available for the early years
if(year == 1993){
  list_of_years <- list_of_years[3:5]
} else if(year == 1994){
  list_of_years <- list_of_years[2:5]
} else {
  list_of_years <- list_of_years 
}

# get the list of what years we have in the database
log_debug("first query")

# get the list of what years we have in the database
df1 <- read_csv(file=paste0(queried_data_path, "agencies_count_offenses_", year, ".csv.gz")) %>% as.data.table()

#Create a new function to trim and upcase to handle character variables
trim_upcase <- compose(toupper, partial(trimws, which="both"))
table_func <- partial(table, useNA="ifany")
sum_func <- partial(sum, na.rm=TRUE)
#sum_func <- partial(rowsum, na.rm=FALSE)

checkfunction <- function(data, ...){
  groupbyinput <- sapply(substitute(list(...))[-1], deparse)
  grouped_data <- data[, .(count = .N), by = groupbyinput]
  datatable(grouped_data)
  log_debug(twodlist_tostring(grouped_data))
}


df1_1 <- df1[, group_type_offense := fcase(
  # Do not count justifiable homicide as a crime
  trim_upcase(offense_code) %in% c("09C"), NA_real_, # Justifiable Homicide
  trim_upcase(offense_code) %in% c("13A", "09A", "09B", "11A", "11B", "11C", "120"), 1, # Part 1 Violent
  trim_upcase(offense_code) %in% c("200", "220", "23A", "23B", "23C", "23D", "23E", "23F", "23G", "23H", "240"), 2, # Part 1 Property
  !is.na(trim_upcase(offense_code)), 3,
  default = 4 # All missings
)]


#Check frequencies
df1_1 %>% checkfunction(group_type_offense, offense_code, offense_name, crime_against, offense_group)

#Group by ori, incident_year, incident_month,  group_type_offense to get the counts of records
summarisebyyear <- function(year, ingroup,...){
  log_debug("Running summarisebyyear")
  
  #inyear <- year %>% rlang::parse_expr()
  #ingroup <- ... %>% rlang::parse_exprs()
  
  #final <- df1_1 %>%
  #  filter(incident_year == !!inyear) %>%
  #  group_by(!!!ingroup) %>%
  #  summarise(count = sum(countofrecords) ) %>%
  #  ungroup()
  final <- df1_1[incident_year == year, .(count = sum(countofrecords)), by = ingroup]
  
  return(final)
}

#Get the list of variables
raw_variables <- c("ori", "incident_year", "incident_month", "group_type_offense")

raw_list <- map(list_of_years, ~ summarisebyyear(year = toString(.x), raw_variables))

df1_2 <- rbindlist(raw_list)

#Transpose the data to use the variable incident_month values to be the new columns and the count variable for the data
df1_3 <- dcast(setDT(df1_2), ... ~ incident_month, value.var = "count")

#Fix issue with known bug where NA's are assign values of 9218868437227407266
#Note when looking at the dataset it is shown as 0 and not as NA, the is.na function used in df1_5 recognizes this as NA
fix_na_cols <- paste0(1:12)
for (col in fix_na_cols) {
  # Use the := operator to modify the column in place
  df1_3[get(col) == "9218868437227407266", (col) := as.integer64(NA)]
}


#Rename the new columns to be the month
setnames(df1_3, old = c("1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"), 
         new = c("jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"))
df1_4 <- df1_3[, c("jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec", setdiff(names(df1_3), c("jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"))), with = FALSE]

#Fix bug in R: Force the month variables to be numeric, so the counts can be sum properly and make the NA shows up
df1_4[, `:=`(jan = as.numeric(jan),
             feb = as.numeric(feb),
             mar = as.numeric(mar),
             apr = as.numeric(apr),
             may = as.numeric(may),
             jun = as.numeric(jun),
             jul = as.numeric(jul),
             aug = as.numeric(aug),
             sep = as.numeric(sep),
             oct = as.numeric(oct),
             nov = as.numeric(nov),
             dec = as.numeric(dec))]

#Create additional recodes

df1_5 <- df1_4 %>%
  mutate(nibrs_total_crime = select(.,jan, feb, mar, apr, may, jun, jul, aug, sep, oct, nov, dec)  %>% rowSums(.,na.rm=TRUE),
                          nibrs_jan_report = ifelse(is.na(jan), 0, 1 ),
                          nibrs_feb_report = ifelse(is.na(feb), 0, 1 ),
                          nibrs_mar_report = ifelse(is.na(mar), 0, 1 ),
                          nibrs_apr_report = ifelse(is.na(apr), 0, 1 ),
                          nibrs_may_report = ifelse(is.na(may), 0, 1 ),
                          nibrs_jun_report = ifelse(is.na(jun), 0, 1 ),
                          nibrs_jul_report = ifelse(is.na(jul), 0, 1 ),
                          nibrs_aug_report = ifelse(is.na(aug), 0, 1 ),
                          nibrs_sep_report = ifelse(is.na(sep), 0, 1 ),
                          nibrs_oct_report = ifelse(is.na(oct), 0, 1 ),
                          nibrs_nov_report = ifelse(is.na(nov), 0, 1 ),
                          nibrs_dec_report = ifelse(is.na(dec), 0, 1 ),
                          nibrs_missing_pattern = paste0(nibrs_jan_report, nibrs_feb_report, nibrs_mar_report, "-",
                                                       nibrs_apr_report, nibrs_may_report, nibrs_jun_report, "-",
                                                       nibrs_jul_report, nibrs_aug_report, nibrs_sep_report, "-",
                                                       nibrs_oct_report, nibrs_nov_report, nibrs_dec_report)
)

# create a copy of df1_4, assign to df1_5 
# (data.table ops can be done in place, need to explicitly define df1_5)
#df1_5 <- copy(df1_4)

# total crime 
#month_cols <- c("jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec")
#df1_5[, nibrs_total_crime := rowSums(.SD, na.rm = TRUE), .SDcols = month_cols]

# report flags for each month - uses lapply
#df1_5[, c(paste0("nibrs_", month_cols, "_report")) := lapply(.SD, function(x) as.integer(!is.na(x))), .SDcols = month_cols]

# report flags for each month - w/out lapply
#for (col in month_cols) {
#  # Perform the operation and assign it to the new column
#  df1_5[, (paste0("nibrs_", col, "_report")) := as.integer(!is.na(get(col)))]
#}

# define missing pattern
#df1_5[, nibrs_missing_pattern := paste0(nibrs_jan_report, nibrs_feb_report, nibrs_mar_report, "-",
#                                  nibrs_apr_report, nibrs_may_report, nibrs_jun_report, "-",
#                                  nibrs_jul_report, nibrs_aug_report, nibrs_sep_report, "-",
#                                  nibrs_oct_report, nibrs_nov_report, nibrs_dec_report)]

#Check the recodes
# df1_5 %>% checkfunction(ori, incident_year, group_type_offense, nibrs_total_crime, jan, feb, mar, apr, may, jun, jul, aug, sep, oct, nov, dec)
df1_5 %>% checkfunction(nibrs_jan_report, jan)
df1_5 %>% checkfunction(nibrs_feb_report, feb)
df1_5 %>% checkfunction(nibrs_mar_report, mar)
df1_5 %>% checkfunction(nibrs_apr_report, apr)
df1_5 %>% checkfunction(nibrs_may_report, may)
df1_5 %>% checkfunction(nibrs_jun_report, jun)
df1_5 %>% checkfunction(nibrs_jul_report, jul)
df1_5 %>% checkfunction(nibrs_aug_report, aug)
df1_5 %>% checkfunction(nibrs_sep_report, sep)
df1_5 %>% checkfunction(nibrs_oct_report, oct)
df1_5 %>% checkfunction(nibrs_nov_report, nov)
df1_5 %>% checkfunction(nibrs_dec_report, dec)


#Save current layout of variables
raw_df1_5_order <- df1_5 %>% colnames() %>% rlang::parse_exprs()

#Create a new dataset to find out the most number of consecutive missing months
raw_cons_months <- df1_5 %>% select(ori, incident_year, group_type_offense,
                                                        nibrs_jan_report, nibrs_feb_report, nibrs_mar_report,
                                                        nibrs_apr_report, nibrs_may_report, nibrs_jun_report,
                                                        nibrs_jul_report, nibrs_aug_report, nibrs_sep_report,
                                                        nibrs_oct_report, nibrs_nov_report, nibrs_dec_report, everything() )

#Create a new dataset to find out the most number of consecutive missing months
#first_cols_ordered <- c("ori", "incident_year", "group_type_offense",
#                "nibrs_jan_report", "nibrs_feb_report", "nibrs_mar_report",
#                "nibrs_apr_report", "nibrs_may_report", "nibrs_jun_report",
#                "nibrs_jul_report", "nibrs_aug_report", "nibrs_sep_report",
#                "nibrs_oct_report", "nibrs_nov_report", "nibrs_dec_report")
#remaining_cols <- setdiff(names(df1_5), first_cols_ordered)
#raw_cons_months <- df1_5[, c(first_cols_ordered, remaining_cols), with=FALSE]

#Initialize the nibrs_max_consecutive_month_missing to be missing
# NOTE: initializing this as 0 instead of NA due to a
raw_cons_months$nibrs_max_consecutive_month_missing <- 0
raw_cons_months$nibrs_consecutive_pattern <- NA

#Loop through the variables nibrs_jan_report - nibrs_dec_report and keep count the number of largest consecutive month missing
numberofmissing<-NA
numberofmissing[1:12] <-0

# Define a function to calculate the maximum consecutive months missing
max_consecutive_missing <- function(x) {
  #make the array missing and variable for new row processing
  countmissing <- 0
  numberofmissing <- integer(12)
  
  #Loop through nibrs_jan_report - nibrs_dec_report and find if there are no crime reported
  for (j in 1:12) {
    #If found, increase the variable countmissing by 1 and store the cumculative count in the array numberofmissing
    if (x[j] == 0) {
      countmissing = countmissing + 1
      numberofmissing[j] = countmissing
    #If the count is not zero, then reset the variable countmissing to zero and report it back to the array
    } else {
      countmissing = 0
      numberofmissing[j] = 0
    }
  }
  return(max(numberofmissing))
}

# Apply the function to each row
raw_cons_months[, nibrs_max_consecutive_month_missing := max_consecutive_missing(unlist(.SD)), by = 1:nrow(raw_cons_months), .SDcols = 4:15]

df1_6 <- raw_cons_months %>% select(!!!raw_df1_5_order, everything() )

#Do a QC check on the new variable
df1_6 %>% checkfunction(nibrs_max_consecutive_month_missing,nibrs_jan_report, nibrs_feb_report, nibrs_mar_report,
                                                          nibrs_apr_report, nibrs_may_report, nibrs_jun_report,
                                                          nibrs_jul_report, nibrs_aug_report, nibrs_sep_report,
                                                          nibrs_oct_report, nibrs_nov_report, nibrs_dec_report )

#Dropping the extra grouping variables
#df1_7 <- df1_6 %>% select(-ori1, -incident_year1, -group_type_offense1  )
df1_7 <- df1_6

#Make the NA to 0 for the counts
df1_7$jan[is.na(df1_7$jan)] <- 0
df1_7$feb[is.na(df1_7$feb)] <- 0
df1_7$mar[is.na(df1_7$mar)] <- 0
df1_7$apr[is.na(df1_7$apr)] <- 0
df1_7$may[is.na(df1_7$may)] <- 0
df1_7$jun[is.na(df1_7$jun)] <- 0
df1_7$jul[is.na(df1_7$jul)] <- 0
df1_7$aug[is.na(df1_7$aug)] <- 0
df1_7$sep[is.na(df1_7$sep)] <- 0
df1_7$oct[is.na(df1_7$oct)] <- 0
df1_7$nov[is.na(df1_7$nov)] <- 0
df1_7$dec[is.na(df1_7$dec)] <- 0

#Quick QC to make sure everything looks good

df1_7 %>% select(ori, incident_year, group_type_offense, nibrs_missing_pattern, nibrs_max_consecutive_month_missing) %>% head(20) %>% print()


#Separate the dataset

final_p1violent <- df1_7 %>% filter(group_type_offense == 1) %>% select(
jan_part1v=jan,
feb_part1v=feb,
mar_part1v=mar,
apr_part1v=apr,
may_part1v=may,
jun_part1v=jun,
jul_part1v=jul,
aug_part1v=aug,
sep_part1v=sep,
oct_part1v=oct,
nov_part1v=nov,
dec_part1v=dec,
nibrs_total_crime_part1v=nibrs_total_crime,
nibrs_missing_pattern_part1v=nibrs_missing_pattern,
nibrs_max_consecutive_month_missing_part1v=nibrs_max_consecutive_month_missing,
ori,
incident_year
)

final_p1property <- df1_7 %>% filter(group_type_offense == 2) %>% select(
jan_part1p=jan,
feb_part1p=feb,
mar_part1p=mar,
apr_part1p=apr,
may_part1p=may,
jun_part1p=jun,
jul_part1p=jul,
aug_part1p=aug,
sep_part1p=sep,
oct_part1p=oct,
nov_part1p=nov,
dec_part1p=dec,
nibrs_total_crime_part1p=nibrs_total_crime,
nibrs_missing_pattern_part1p=nibrs_missing_pattern,
nibrs_max_consecutive_month_missing_part1p=nibrs_max_consecutive_month_missing,
ori,
incident_year
)

final_other <- df1_7 %>% filter(group_type_offense == 3) %>% select(

jan_otherc=jan,
feb_otherc=feb,
mar_otherc=mar,
apr_otherc=apr,
may_otherc=may,
jun_otherc=jun,
jul_otherc=jul,
aug_otherc=aug,
sep_otherc=sep,
oct_otherc=oct,
nov_otherc=nov,
dec_otherc=dec,
nibrs_total_crime_otherc=nibrs_total_crime,
nibrs_missing_pattern_otherc=nibrs_missing_pattern,
nibrs_max_consecutive_month_missing_otherc=nibrs_max_consecutive_month_missing,
ori,
incident_year
)

log_dim(df1_7)
log_dim(final_p1violent)
log_dim(final_p1property)
log_dim(final_other)
#merge the datasets together
final <- full_join(final_p1violent, final_p1property, by=c("ori", "incident_year"))
final <- full_join(final, final_other, by=c("ori", "incident_year") )

log_dim(final)

#Reorder the variables in the dataset
final <- final %>% select(ori, incident_year, ends_with("part1v"), ends_with("part1p"), ends_with("otherc")  )



#Fill in the missings after joining

final$jan_part1v[is.na(final$jan_part1v)] <- 0
final$feb_part1v[is.na(final$feb_part1v)] <- 0
final$mar_part1v[is.na(final$mar_part1v)] <- 0
final$apr_part1v[is.na(final$apr_part1v)] <- 0
final$may_part1v[is.na(final$may_part1v)] <- 0
final$jun_part1v[is.na(final$jun_part1v)] <- 0
final$jul_part1v[is.na(final$jul_part1v)] <- 0
final$aug_part1v[is.na(final$aug_part1v)] <- 0
final$sep_part1v[is.na(final$sep_part1v)] <- 0
final$oct_part1v[is.na(final$oct_part1v)] <- 0
final$nov_part1v[is.na(final$nov_part1v)] <- 0
final$dec_part1v[is.na(final$dec_part1v)] <- 0

final$nibrs_total_crime_part1v[is.na(final$nibrs_total_crime_part1v)] <- 0
final$nibrs_missing_pattern_part1v[is.na(final$nibrs_missing_pattern_part1v)] <- "000-000-000-000"
final$nibrs_max_consecutive_month_missing_part1v[is.na(final$nibrs_max_consecutive_month_missing_part1v)] <- 0



final$jan_part1p[is.na(final$jan_part1p)] <- 0
final$feb_part1p[is.na(final$feb_part1p)] <- 0
final$mar_part1p[is.na(final$mar_part1p)] <- 0
final$apr_part1p[is.na(final$apr_part1p)] <- 0
final$may_part1p[is.na(final$may_part1p)] <- 0
final$jun_part1p[is.na(final$jun_part1p)] <- 0
final$jul_part1p[is.na(final$jul_part1p)] <- 0
final$aug_part1p[is.na(final$aug_part1p)] <- 0
final$sep_part1p[is.na(final$sep_part1p)] <- 0
final$oct_part1p[is.na(final$oct_part1p)] <- 0
final$nov_part1p[is.na(final$nov_part1p)] <- 0
final$dec_part1p[is.na(final$dec_part1p)] <- 0


final$nibrs_total_crime_part1p[is.na(final$nibrs_total_crime_part1p)] <- 0
final$nibrs_missing_pattern_part1p[is.na(final$nibrs_missing_pattern_part1p)] <- "000-000-000-000"
final$nibrs_max_consecutive_month_missing_part1p[is.na(final$nibrs_max_consecutive_month_missing_part1p)] <- 0



final$jan_otherc[is.na(final$jan_otherc)] <- 0
final$feb_otherc[is.na(final$feb_otherc)] <- 0
final$mar_otherc[is.na(final$mar_otherc)] <- 0
final$apr_otherc[is.na(final$apr_otherc)] <- 0
final$may_otherc[is.na(final$may_otherc)] <- 0
final$jun_otherc[is.na(final$jun_otherc)] <- 0
final$jul_otherc[is.na(final$jul_otherc)] <- 0
final$aug_otherc[is.na(final$aug_otherc)] <- 0
final$sep_otherc[is.na(final$sep_otherc)] <- 0
final$oct_otherc[is.na(final$oct_otherc)] <- 0
final$nov_otherc[is.na(final$nov_otherc)] <- 0
final$dec_otherc[is.na(final$dec_otherc)] <- 0

final$nibrs_total_crime_otherc[is.na(final$nibrs_total_crime_otherc)] <- 0
final$nibrs_missing_pattern_otherc[is.na(final$nibrs_missing_pattern_otherc)] <- "000-000-000-000"
final$nibrs_max_consecutive_month_missing_otherc[is.na(final$nibrs_max_consecutive_month_missing_otherc)] <- 0


#Calculate the crime composition ratio (Part 1 Violent crimes / Part 1 Property crime) for both monthly and annual totals
final <- final %>% mutate(
jan_ratio_v_p = ifelse(jan_part1p ==0, NA,  jan_part1v/jan_part1p),
feb_ratio_v_p = ifelse(feb_part1p ==0, NA,  feb_part1v/feb_part1p),
mar_ratio_v_p = ifelse(mar_part1p ==0, NA,  mar_part1v/mar_part1p),
apr_ratio_v_p = ifelse(apr_part1p ==0, NA,  apr_part1v/apr_part1p),
may_ratio_v_p = ifelse(may_part1p ==0, NA,  may_part1v/may_part1p),
jun_ratio_v_p = ifelse(jun_part1p ==0, NA,  jun_part1v/jun_part1p),
jul_ratio_v_p = ifelse(jul_part1p ==0, NA,  jul_part1v/jul_part1p),
aug_ratio_v_p = ifelse(aug_part1p ==0, NA,  aug_part1v/aug_part1p),
sep_ratio_v_p = ifelse(sep_part1p ==0, NA,  sep_part1v/sep_part1p),
oct_ratio_v_p = ifelse(oct_part1p ==0, NA,  oct_part1v/oct_part1p),
nov_ratio_v_p = ifelse(nov_part1p ==0, NA,  nov_part1v/nov_part1p),
dec_ratio_v_p = ifelse(dec_part1p ==0, NA,  dec_part1v/dec_part1p),
total_ratio_v_p = ifelse(nibrs_total_crime_part1p ==0, NA,  nibrs_total_crime_part1v/nibrs_total_crime_part1p)
)

#Free up memory by deleting some objects
remove(df1)
remove(df1_2)
remove(df1_3)
remove(df1_4)
remove(df1_5)
remove(raw_cons_months)
remove(numberofmissing)
remove(countmissing)
# remove(raw_cons_months2)
remove(df1_6)
remove(df1_7)
remove(final_p1violent)
remove(final_p1property)
remove(final_other)
remove(raw_df1_5_order)
remove(con)

invisible(gc())


#Get the total number of consecutive months where all crimes are 0
#Get the list of variables
raw_variables <- c("ori", "incident_year", "incident_month")

#Still use function summarisebyyear that uses dataset df1_1
raw_list2 <- map(list_of_years, ~ summarisebyyear(year = toString(.x), raw_variables))

df2_2 <- rbindlist(raw_list2)

#Transpose the data to use the variable incident_month values to be the new columns and the count variable for the data
df2_3 <- dcast(setDT(df2_2), ... ~ incident_month, value.var = "count")

#Fix issue with known bug where NA's are assign values of 9218868437227407266
#Note when looking at the dataset it is shown as 0 and not as NA, the is.na function used in df2_5 recognizes this as NA
fix_na_cols <- paste0(1:12)
for (col in fix_na_cols) {
  # Use the := operator to modify the column in place
  df2_3[get(col) == "9218868437227407266", (col) := as.integer64(NA)]
}

#Rename the new columns to be the month
#df2_4 <- df2_3 %>% select(jan= `1`, feb= `2`, mar= `3`, apr = `4`, may = `5`, jun = `6`, jul= `7`, aug= `8`, sep = `9`, oct= `10`, nov=`11`, dec = `12`, everything() )
setnames(df2_3, old = c("1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"), 
         new = c("jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"))

# Reorder columns to bring the new names to the front
df2_4 <- df2_3[, c("jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec", setdiff(names(df2_3), c("jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"))), with = FALSE]

#Fix bug in R: Force the month variables to be numeric, so the counts can be sum properly and make the NA shows up
df2_4[, c("jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec") := .(
  as.numeric(jan), 
  as.numeric(feb),
  as.numeric(mar), 
  as.numeric(apr),
  as.numeric(may), 
  as.numeric(jun),
  as.numeric(jul), 
  as.numeric(aug),
  as.numeric(sep), 
  as.numeric(oct),
  as.numeric(nov), 
  as.numeric(dec)
)]

df2_5 <- df2_4 %>%
  mutate(nibrs_total_crime = select(.,jan, feb, mar, apr, may, jun, jul, aug, sep, oct, nov, dec) %>% rowSums(.,na.rm=TRUE),
                          nibrs_jan_report = ifelse(is.na(jan), 0, 1 ),
                          nibrs_feb_report = ifelse(is.na(feb), 0, 1 ),
                          nibrs_mar_report = ifelse(is.na(mar), 0, 1 ),
                          nibrs_apr_report = ifelse(is.na(apr), 0, 1 ),
                          nibrs_may_report = ifelse(is.na(may), 0, 1 ),
                          nibrs_jun_report = ifelse(is.na(jun), 0, 1 ),
                          nibrs_jul_report = ifelse(is.na(jul), 0, 1 ),
                          nibrs_aug_report = ifelse(is.na(aug), 0, 1 ),
                          nibrs_sep_report = ifelse(is.na(sep), 0, 1 ),
                          nibrs_oct_report = ifelse(is.na(oct), 0, 1 ),
                          nibrs_nov_report = ifelse(is.na(nov), 0, 1 ),
                          nibrs_dec_report = ifelse(is.na(dec), 0, 1 ),
                          nibrs_missing_pattern = paste0(nibrs_jan_report, nibrs_feb_report, nibrs_mar_report, "-",
                                                       nibrs_apr_report, nibrs_may_report, nibrs_jun_report, "-",
                                                       nibrs_jul_report, nibrs_aug_report, nibrs_sep_report, "-",
                                                       nibrs_oct_report, nibrs_nov_report, nibrs_dec_report)
)

# df2_5 %>% checkfunction(ori, incident_year, nibrs_total_crime, jan, feb, mar, apr, may, jun, jul, aug, sep, oct, nov, dec)
df2_5 %>% checkfunction(nibrs_jan_report, jan)
df2_5 %>% checkfunction(nibrs_feb_report, feb)
df2_5 %>% checkfunction(nibrs_mar_report, mar)
df2_5 %>% checkfunction(nibrs_apr_report, apr)
df2_5 %>% checkfunction(nibrs_may_report, may)
df2_5 %>% checkfunction(nibrs_jun_report, jun)
df2_5 %>% checkfunction(nibrs_jul_report, jul)
df2_5 %>% checkfunction(nibrs_aug_report, aug)
df2_5 %>% checkfunction(nibrs_sep_report, sep)
df2_5 %>% checkfunction(nibrs_oct_report, oct)
df2_5 %>% checkfunction(nibrs_nov_report, nov)
df2_5 %>% checkfunction(nibrs_dec_report, dec)

#Create a new dataset to find out the most number of consecutive missing months

raw_df2_5_order <- df2_5 %>% colnames() %>% rlang::parse_exprs()


raw_cons_months <- df2_5 %>% select(ori, incident_year,
                                                        nibrs_jan_report, nibrs_feb_report, nibrs_mar_report,
                                                        nibrs_apr_report, nibrs_may_report, nibrs_jun_report,
                                                        nibrs_jul_report, nibrs_aug_report, nibrs_sep_report,
                                                        nibrs_oct_report, nibrs_nov_report, nibrs_dec_report, everything() )

#Initialize the nibrs_max_consecutive_month_missing to be missing
raw_cons_months$nibrs_max_consecutive_month_missing <- 0
raw_cons_months$nibrs_consecutive_pattern <- NA

#Loop through the variables nibrs_jan_report - nibrs_dec_report and keep count the number of largest consecutive month missing
numberofmissing<-NA
numberofmissing[1:12] <-0

# apply max_consecutive_missing function, adjust cols
raw_cons_months[, nibrs_max_consecutive_month_missing := max_consecutive_missing(unlist(.SD)), by = 1:nrow(raw_cons_months), .SDcols = 3:14]


df2_6 <-raw_cons_months %>% select(!!!raw_df2_5_order, everything() )

df2_6 %>% checkfunction(nibrs_max_consecutive_month_missing,nibrs_jan_report, nibrs_feb_report, nibrs_mar_report,
                                                          nibrs_apr_report, nibrs_may_report, nibrs_jun_report,
                                                          nibrs_jul_report, nibrs_aug_report, nibrs_sep_report,
                                                          nibrs_oct_report, nibrs_nov_report, nibrs_dec_report )

#Assign to new object to be consistent with old program set up
df2_7 <- df2_6


#Make the NA to 0 for the counts
df2_7$jan[is.na(df2_7$jan)] <- 0
df2_7$feb[is.na(df2_7$feb)] <- 0
df2_7$mar[is.na(df2_7$mar)] <- 0
df2_7$apr[is.na(df2_7$apr)] <- 0
df2_7$may[is.na(df2_7$may)] <- 0
df2_7$jun[is.na(df2_7$jun)] <- 0
df2_7$jul[is.na(df2_7$jul)] <- 0
df2_7$aug[is.na(df2_7$aug)] <- 0
df2_7$sep[is.na(df2_7$sep)] <- 0
df2_7$oct[is.na(df2_7$oct)] <- 0
df2_7$nov[is.na(df2_7$nov)] <- 0
df2_7$dec[is.na(df2_7$dec)] <- 0


#Quick QC to make sure everything looks good

df2_7 %>% select(ori, incident_year, nibrs_missing_pattern, nibrs_max_consecutive_month_missing) %>% head(20) %>% print()


#Separate the dataset

final_all <- df2_7  %>% select(
jan_all=jan,
feb_all=feb,
mar_all=mar,
apr_all=apr,
may_all=may,
jun_all=jun,
jul_all=jul,
aug_all=aug,
sep_all=sep,
oct_all=oct,
nov_all=nov,
dec_all=dec,
nibrs_total_crime_all=nibrs_total_crime,
nibrs_missing_pattern_all=nibrs_missing_pattern,
nibrs_max_consecutive_month_missing_all=nibrs_max_consecutive_month_missing,
ori,
incident_year
)




#Merge on to final dataset
#merge the datasets together
log_dim(final)
log_dim(final_all)
final <- full_join(final, final_all, by=c("ori", "incident_year"))
log_dim(final)

#Fix variable ori for selected LEA
#final$ori[final$ori == "SC0409E00"] <- "SC040219E" #Change Legacy ORI (SC0409E00) to current ORI (SC040219E)


#Output the dataset to the share
final %>% write_csv(sprintf("%s/NIBRS_reporting_pattern.csv", artifactPath), na = "")
