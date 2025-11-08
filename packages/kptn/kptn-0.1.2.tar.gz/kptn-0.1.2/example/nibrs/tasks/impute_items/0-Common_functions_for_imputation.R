
#Declare the functions used in the imputation task
tablena <- partial(table, useNA = "ifany")
table_func <- partial(table, useNA="ifany")
sum_func <- partial(sum, na.rm=TRUE)

trim_upper <- compose(toupper, partial(trimws, which="both"))
trim_upcase <- compose(toupper, partial(trimws, which="both"))
trim <- partial(trimws, which="both")

#read_csv <- partial(read_csv, guess_max = 100000) #For now, read thru the 1st 100,000 rows to determine variable type
#read_excel <- partial(read_excel, guess_max = 100000) #For now, read thru the 1st 100,000 rows to determine variable type

checkfunction <- function(data, ...){
  #log_debug(paste0("CHECKFUNCTION with args: ",toString(as.list(match.call())[-1])))
  groupbyinput <- rlang:::enquos(...)
  grouped_data <- data %>% group_by( !!!(groupbyinput) ) %>% summarise(count = n() )
  datatable( grouped_data)
  #datatable( grouped_data %>% print())
  #log_debug(twodlist_tostring(grouped_data))
}

#List of common states in NIBRS, maybe updated from year to year

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


recode_all_race_ints_to_char <- function(df) {
  # take all numeric race code columns and cast them to characters
  df %>% mutate(across(contains("race_code") & where(is.numeric),
    ~ case_when(
      . == 1 ~ "W",
      . == 2 ~ "B",
      . == 3 ~ "I",
      . == 4 ~ "A",
      . == 5 ~ "AP",
      . == 6 ~ "C",
      . == 7 ~ "J",
      . == 8 ~ "P",
      . == 9 ~ "O",
      . == 98 ~ "M",
      TRUE ~ "U" 
  ) %>%  as.character()))
}


recode_all_ethnicity_ints_to_char <- function(df){
  # take all numeric ethnicity code columns and cast them to characters
  df %>% mutate(across(contains("ethnicity_code") & where(is.numeric),
    ~ case_when(
      . == 1 ~ "H",
      . == 2 ~ "N",
      . == 3 ~ "U",
      . == 4 ~ "M",
      TRUE ~ "U"
   ) %>%  as.character()))
}