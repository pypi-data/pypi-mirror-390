
final_processing <- function(
  raw_percentage_3,
  main,
  main_prb,
  main_reporting_db3,
  final_TOTAL_SE,
  der_list_of_variables_variance,
  final_RATE_SE,
  final_path_after_variance,
  DER_TABLE_NAME,
  DER_CURRENT_PERMUTATION_NUM
) {
  log_debug("After set_denominator_column, before der_list_of_variables_variance_percentage_list")
  #Need to split out the variables to loop thru 500 at a time to prevent an error message
  der_list_of_variables_variance_percentage_list <- raw_percentage_3 %>%
    #Assign a row to each variable
    mutate(row = row_number()) %>%
    #Get the quotient to split up processing by 500
    mutate(row_split = row %/% 500) %>%
    #Split by row_split to create a list 
    split(.$row_split) 

  #Use map to create a list object to hold results
  der_list_PERCENTAGE_SE <- map(der_list_of_variables_variance_percentage_list, ~ {

    #Call the function
    returndata <- PERCENTAGE_SE_FUNCTION(indata=main, 
                                          invar_denom=.x, 
                                          intotalse=final_TOTAL_SE, 
                                          inprb=main_prb)
              
    #Return the data
    return(returndata)
                          
  })


  #Combine the datasets together
  final_PERCENTAGE_SE <- der_list_PERCENTAGE_SE %>%
    bind_rows()
                          
    
  #Remove objects
  rm(raw_percentage_1, raw_percentage_2, raw_percentage_3, raw_percentage_drop,
    der_list_PERCENTAGE_SE, der_list_of_variables_variance_percentage_list)
  invisible(gc())

  #Use map to create a list object to hold results
  main_dt <- as.data.table(main)
  der_list_unweighted_counts <- map(der_list_of_variables_variance, ~ {

    #Call the function
    returndata <- TOTAL_COUNT_FUNCTION(indata=main_dt, invar=.x)

    #Return the data
    return(returndata)
  })
  #Combined the results
  final_UNWEIGHTED_COUNTS <- rbindlist(der_list_unweighted_counts)[, -"variable", with = FALSE]

   #Clean up the reporting database
  #The datasets to use are main_reporting_db3 for most recent database
  #final_TOTAL_SE - for final count SE
  #final_RATE_SE - for final rate SE
  #final_PERCENTAGE_SE - for final percentage SE

  #Combined the final SE datasets
  final_estimate <- bind_rows(final_TOTAL_SE, final_RATE_SE, final_PERCENTAGE_SE) %>%
    select(table, section, row, column, estimate_type_num, 
          estimate_standard_error, estimate_prb, estimate_bias, estimate_rmse,
          estimate_upper_bound, estimate_lower_bound, 
          relative_standard_error, relative_rmse, !!DER_PRB_VARIABLE_IND_SYMBOL,
          tbd_estimate, estimate_unweighted, population_estimate_unweighted)
      

  #Merge on the unweighted counts to all 3 estimate types
  final_estimate2 <- final_estimate %>%
    left_join(final_UNWEIGHTED_COUNTS, by=c("table", "section", "row", "column"))

  log_dim(final_estimate)
  log_dim(final_estimate2)

  final_main_reporting_db <- main_reporting_db3 %>%
    left_join(final_estimate2, by=c("table", "section", "row", "column", "estimate_type_num"))  %>%
      #Overwrite the estimate with tbd_estimate
      mutate(estimate = case_when(estimate == DER_NA_CODE ~  DER_NA_CODE,
                                  TRUE ~ tbd_estimate)) %>%
      mutate(estimate = case_when(is.na(estimate) ~  0,
                                  TRUE ~ estimate))

  #Look thru and fix estimates
  for(i in 1:length(final_variance_vars)){
    
    #Current variable
    invar <- final_variance_vars[[i]] %>% rlang:::parse_expr()
    
    final_main_reporting_db <- final_main_reporting_db %>%
      mutate(!!invar := case_when(estimate == DER_NA_CODE ~  DER_NA_CODE,
                                          TRUE ~ as.numeric(!!invar)))
    
    
  }


  log_dim(main_reporting_db3)
  log_dim(final_estimate2)
  log_dim(final_main_reporting_db)         


  final_error<- final_main_reporting_db %>%
    filter(round(tbd_estimate,2) != round(estimate,2))

  final_error %>%
    DT:::datatable()

  #Output any difference to file
  if(nrow(final_error) > 0 ){
    final_error %>%
    write.csv(paste0(final_path,"Table ", DER_TABLE_NAME, "_Reporting_Database_Estimate_no_match_variance_", DER_CURRENT_PERMUTATION_NUM,".csv"))
  }

  log_debug("Pre-write out")
  final_main_reporting_db %>%
    write.csv(paste0(final_path_after_variance,"Table ", DER_TABLE_NAME, "_Reporting_Database_After_Variance_", DER_CURRENT_PERMUTATION_NUM,".csv"))
  log_debug("Program end")
}