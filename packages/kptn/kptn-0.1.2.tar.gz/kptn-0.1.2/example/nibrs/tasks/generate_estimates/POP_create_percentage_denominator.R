library(memoise)

# For performance, should not be called directly, but only via the _init function
CREATE_PERCENTAGE_DENOMINATOR_orig <- function(indata, inrow, incolumn){
  # log_debug("Running POP function CREATE_PERCENTAGE_DENOMINATOR")
  # log_debug(system("free -mh", intern = FALSE))
  returndata <- indata[
    column == incolumn
    & estimate_type_num == 2
    & row %in% inrow
    & !is.na(variable_name),
    .(variable_name)
  ]
  return(paste(returndata$variable_name, collapse = ', '))
}

# Call this function with an initial data.table; returns a fast memoized function
CREATE_PERCENTAGE_DENOMINATOR_init <- function(indata) {
  func <- function(inrow, incol) { CREATE_PERCENTAGE_DENOMINATOR_orig(indata, inrow, incol) }
  return (memoise(func))
}
