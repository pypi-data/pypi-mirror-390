#Need to handle at each permutation/cell level using dataset raw_7_1 as a base


# Alt 6
# RMSE > 0.3 OR {
# (estimate = 0 OR var(estimate) = 0) AND [
# (agency type domain or permutation in (state police, other state agencies, tribal, federal) AND cell agency coverage < 80%) OR
# (^not that AND cell population coverage < 80%)
# ]
# }

#Need to handle the Tribal permutation (i.e. 108) then
#Tribal agencies, State police, an dOther state agencies

raw_7_2 <- raw_7_1 %>%
  mutate(der_cell_separate = fcase(
    POPTOTAL_ORIG_PERMUTATION_NUMBER == 108, 1, #Need to handle the Tribal permutation (i.e. 108)
    trimws(estimate_domain, which="both") =="Agency indicator: Tribal agencies", 2,
    trimws(estimate_domain, which="both") =="Agency indicator: State police", 3,
    trimws(estimate_domain, which="both") =="Agency indicator: Other state agencies", 4,
    
    default = 0 #Here are the rest
  ),
  
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

#Make the new suppression rule variable

#For reference from above
# mutate(der_cell_separate = fcase(
#   POPTOTAL_ORIG_PERMUTATION_NUMBER == 108, 1, #Need to handle the Tribal permutation (i.e. 108)
#   trimws(estimate_domain, which="both") =="Agency indicator: Tribal agencies", 2,
#   trimws(estimate_domain, which="both") =="Agency indicator: State police", 3,
#   trimws(estimate_domain, which="both") =="Agency indicator: Other state agencies", 4,
#   default = 0 #Here are the rest
#Need to handle the Tribal permutation (i.e. 108)
raw_7_r1 <- loopsuppressionrulecell(indata=raw_7_2,
                                    inder_cell_separate = 1,
                                    inrule = '
der_estimate_0_se_0 == 1 &
(POPTOTAL_ORIG_PERMUTATION_NUMBER == 108 &
(POPTOTAL_UNIV_COV_AGENCY_TRIBAL < 80 | is.na(POPTOTAL_UNIV_COV_AGENCY_TRIBAL)))
')

raw_7_r2 <- loopsuppressionrulecell(indata=raw_7_2,
                                    inder_cell_separate = 2,
                                    inrule='
der_estimate_0_se_0 == 1 &
(trimws(estimate_domain, which="both") =="Agency indicator: Tribal agencies" &
(POPTOTAL_UNIV_COV_AGENCY_TRIBAL < 80 | is.na(POPTOTAL_UNIV_COV_AGENCY_TRIBAL)))
')


raw_7_r3 <- loopsuppressionrulecell(indata=raw_7_2,
                                    inder_cell_separate = 3,
                                    inrule='
der_estimate_0_se_0 == 1 &
(trimws(estimate_domain, which="both") =="Agency indicator: State police" &
(POPTOTAL_UNIV_COV_AGENCY_STATE_POLICE < 80 | is.na(POPTOTAL_UNIV_COV_AGENCY_STATE_POLICE)))
')

raw_7_r4 <- loopsuppressionrulecell(indata=raw_7_2,
                                    inder_cell_separate = 4,
                                    inrule = '
der_estimate_0_se_0 == 1 &
(trimws(estimate_domain, which="both") =="Agency indicator: Other state agencies" &
(POPTOTAL_UNIV_COV_AGENCY_OTHER < 80 | is.na(POPTOTAL_UNIV_COV_AGENCY_OTHER)))
')

raw_7_r0 <- loopsuppressionrulecell(indata=raw_7_2,
                                    inder_cell_separate = 0,
                                    inrule = '
der_estimate_0_se_0 == 1 &
der_estimate_na_code == 0  &
POPTOTAL_UNIV_POP_COV < 0.80
')

#Stack the data together and handle the RSE portion
raw_8 <- bind_rows(raw_7_r0, raw_7_r1, raw_7_r2, raw_7_r3, raw_7_r4) %>%
  mutate(
    #Handle the RSE portion
    der_rrmse_gt_30_se_estimate_0_2_cond = case_when(
      der_rrmse_gt_30 == 1 ~ 1,
      TRUE ~ der_rrmse_gt_30_se_estimate_0_2_cond)) %>%
  #Sort the data
  arrange(tbd_row_number)
