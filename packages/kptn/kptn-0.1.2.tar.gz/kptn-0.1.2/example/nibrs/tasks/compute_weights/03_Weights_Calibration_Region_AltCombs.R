
maxAdj <- 10 #Max adjustment factor
maxIt <- 1000 #Max iterations during variable selection

### Purpose of program is to calibrate regional weights by region X grouping (e.g., All cities 250,000 or over)
### Author: JD Bunker
### Last updated: 29OCT2021
#Update (28OCT2021): Commenting out/removing unnecessary print statements and removing no longer needed commented-out code
#Update (29OCT2021): Continuing clean up efforts (commenting out / deleting commented-out code)
#Update (07OCT2022): Adding maxWgt and maxIt values for final weight
library(tidyverse)
library(openxlsx)
library(lubridate)
library(sampling)
library(data.table)
library(Hmisc)

log_info("Running 03_Weights_Calibration_Region_AltCombs.R")

# read in SF data

SF <- paste0(input_weighting_data_folder,"SF_postN.csv") %>%
  #read.csv(header=TRUE, sep=",") %>%
  fread() %>%
  mutate(totcrime_imp=totcrime_violent_imp+totcrime_property_imp)


crimeVars <- SF %>%
  colnames() %>%
  str_subset("^tot.*_imp")
#Crime variables for weight calibration
crimeVarsWgtAll <- c("totcrime_imp",
                     "totcrime_violent_imp",
                     "totcrime_property_imp")
crimeVarsWgtRest <- c("totcrime_murder_imp",
                      "totcrime_rape_imp","totcrime_aggAssault_imp",
                      "totcrime_burglary_imp","totcrime_rob_imp",
                      "totcrime_larceny_imp","totcrime_vhcTheft_imp")
crimeVarsWgt <- c(crimeVarsWgtAll,crimeVarsWgtRest)

#Update (28OCT2021): Comment out freqs
# SF %>%
#   group_by(REGION_NAME)%>%
#   dplyr::summarize(n=n())
# 
# 
# SF %>% .$POPULATION_GROUP_DESC %>% table()
# 
# SF %>% .$REGION_NAME %>% table()

regionGps <- SF %>%
  select(REGION_CODE,REGION_NAME) %>%
  unique() %>%
  arrange(REGION_CODE) %>%
  pull(REGION_NAME)
nRegionGps <- SF %>%
  select(REGION_NAME) %>%
  unique() %>%
  nrow()
#Update (28OCT2021): Comment out freqs
# SF %>%
#   subset(is.na(REGION_NAME)) %>%
#   nrow()
# SF %>%
#   subset(is.na(REGION_NAME)) %>%
#   select(ORI,UCR_AGENCY_NAME,AGENCY_TYPE_NAME,stratum_f,REGION_NAME,
#          POPULATION_GROUP_DESC,resp_ind_m3,matches("totcrime.*_imp")) %>%
#   head() %>%
#   DT::datatable()
# 
# SF %>%
#   subset(is.na(REGION_NAME)) %>%
#   group_by(REGION_NAME) %>%
#   dplyr::summarize(n=n())


srs_region_control_totals <- SF %>%
  group_by(REGION_NAME) %>%
  dplyr::summarize(across(.cols=all_of(crimeVarsWgt),
                          .fns=list("sum"=sum),
                          .names="{.fn}_{.col}",na.rm=TRUE))



#Remove Northeast, West
#Update (12AUG2021): Actually, include these
SF2 <- SF %>%
  #Note (01May2024): Drop all calibration variables that already exist (e.g., national)
  select(-matches("^V\\d+_\\w"))
regionGps2 <- SF2 %>%
  select(REGION_NAME) %>%
  unique() %>%
  .$REGION_NAME %>%
  sort()
nRegionGps2 <- SF2 %>%
  select(REGION_NAME) %>%
  unique() %>%
  nrow()


wgtGpDescs <-  c("All cities 1,000,000 or over",
                 "All cities 500,000 or over",
                 "All cities 250,000-499,999",
                 "Cities from 100,000 thru 249,999",
                 "Cities from 50,000 thru 99,999",
                 "Cities from 25,000 thru 49,999",
                 "Cities from 10,000 thru 24,999",
                 "Cities under 10,000",
                 "MSA counties 100,000 or over",
                 "MSA counties from 25,000 thru 99,999",
                 "MSA counties from 10,000 thru 24,999",
                 "MSA counties under 10,000",
                 "MSA State Police",
                 "Non-MSA counties 25,000 or over",
                 "Non-MSA counties from 10,000 thru 24,999",
                 "Non-MSA counties under 10,000",
                 "Non-MSA State Police",
                 "CITY AGENCY-ZERO POP",
                 "MSA COUNTY/STATE AGENCY-ZERO POP",
                 "NON-MSA COUNTY/STATE AGENCY-ZERO POP")
SF2 <- SF2 %>%
  mutate(totcrime_agg_rob_imp=totcrime_aggAssault_imp+totcrime_rob_imp)%>%
  mutate(wgtGp=case_when(POPULATION_GROUP_DESC=="Cities 1,000,000 or over" ~ 1,
                         POPULATION_GROUP_DESC=="Cities from 500,000 thru 999,999" ~ 2,
                         POPULATION_GROUP_DESC=="Cities from 250,000 thru 499,999" ~ 3,
                         POPULATION_GROUP_DESC=="Cities from 100,000 thru 249,999" ~ 4,
                         POPULATION_GROUP_DESC=="Cities from 50,000 thru 99,999" ~ 5,
                         POPULATION_GROUP_DESC=="Cities from 25,000 thru 49,999" ~ 6,
                         POPULATION_GROUP_DESC=="Cities from 10,000 thru 24,999" ~ 7,
                         POPULATION_GROUP_DESC %in% c("Cities from 2,500 thru 9,999","Cities under 2,500") & POPULATION> 0 ~ 8,
                         
                         POPULATION_GROUP_DESC=="MSA counties 100,000 or over" ~ 9,
                         POPULATION_GROUP_DESC=="MSA counties from 25,000 thru 99,999" ~ 10,
                         POPULATION_GROUP_DESC=="MSA counties from 10,000 thru 24,999" ~ 11,
                         POPULATION_GROUP_DESC=="MSA counties under 10,000" &  POPULATION> 0 ~ 12,
                         POPULATION_GROUP_DESC=="MSA State Police" & POPULATION>0 ~ 13,
                         
                         POPULATION_GROUP_DESC %in% c("Non-MSA counties from 25,000 thru 99,999","Non-MSA counties 100,000 or over") ~ 14,
                         POPULATION_GROUP_DESC=="Non-MSA counties from 10,000 thru 24,999" ~ 15,
                         POPULATION_GROUP_DESC=="Non-MSA counties under 10,000" & POPULATION >0 ~ 16,
                         POPULATION_GROUP_DESC=="Non-MSA State Police" & POPULATION>0 ~ 17,
                         
                         POPULATION_GROUP_DESC=="Cities under 2,500" & POPULATION==0 ~ 18,
                         POPULATION_GROUP_DESC %in% c("MSA counties under 10,000","MSA State Police") & POPULATION==0 ~ 19,
                         POPULATION_GROUP_DESC %in% c("Non-MSA counties under 10,000","Non-MSA State Police") & POPULATION==0 ~ 20),
         wgtGpDesc=factor(wgtGp,levels=1:20,labels=wgtGpDescs),
         totcrime_imp=totcrime_violent_imp+totcrime_property_imp)

wgtGps <- SF2 %>%
  select(wgtGp) %>%
  unique() %>%
  .$wgtGp %>%
  sort()
nWgtGps <- SF2 %>%
  select(wgtGp) %>%
  unique() %>%
  nrow()


#Detect and perform any necessary collapsing (number of respondents in non-empty region X grouping is 0)

SF2 <- SF2 %>%
  mutate(wgtGp2=case_when(wgtGp==2 ~ 1,
                          wgtGp==3 ~ 1,
                          wgtGp==12 ~ 11,
                          TRUE ~ wgtGp))


wgtGps2 <- SF2 %>%
  select(wgtGp2) %>%
  unique() %>%
  .$wgtGp2 %>%
  sort()


wgtGpDescs2 <- wgtGpDescs %>%
  as.character() %>%
  data.frame(wgtGpDesc=.) %>%
  inner_join(SF2 %>% select(wgtGpDesc),by=c("wgtGpDesc")) %>%
  #Update (27AUG2021): Convert to character
  mutate(wgtGpDesc=as.character(wgtGpDesc)) %>%
  mutate(wgtGpDesc2=case_when(wgtGpDesc=="All cities 1,000,000 or over" ~ "All cities 250,000 or over",
                              wgtGpDesc=="All cities 500,000 or over" ~ "All cities 250,000 or over",
                              wgtGpDesc=="All cities 250,000-499,999" ~ "All cities 250,000 or over",
                              wgtGpDesc=="MSA counties from 10,000 thru 24,999" ~ "MSA counties under 25,000",
                              wgtGpDesc=="MSA counties under 10,000" ~ "MSA counties under 25,000",
                              
                              TRUE ~ wgtGpDesc))

#wgtGpDescs2
wgtGpDescs2 <- wgtGpDescs2 %>%
  .$wgtGpDesc2 %>%
  unique()



SF2 <- SF2 %>%
  mutate(wgtGpDesc2=factor(wgtGp2,levels=wgtGps2,labels=wgtGpDescs2))

wgtGpRegionDescs <- wgtGpDescs2
wgtGpsRegion <- wgtGps2
#Update (28OCT2021): Reducing number of print statements - confirm with Dan/others?
collapseWgtGpsRegion <- function(dat){
  log_debug("Running function collapseWgtGpsRegion")
  SF_smoothed_temp <- dat %>%
    mutate(wgtGpRegion=wgtGp2,
           wgtGpRegionDesc=wgtGpDesc2,
           wgtGpRegion_col=wgtGpRegion,
           wgtGpRegionDesc_col=factor(wgtGpRegion_col,levels=wgtGpsRegion,labels=wgtGpRegionDescs))
  env <- environment()
  ct <- 0
  stop <- FALSE
  while (stop==FALSE){
    ct <- ct+1
    log_debug("##############################")
    log_debug(paste0("Round ",ct))
    log_debug("Cells 0 respondents:")
    (SF_smoothed_temp %>%
        group_by(REGION_NAME,wgtGpRegion_col) %>%
        dplyr::summarize(mean_crime=mean(totcrime_imp,na.rm=TRUE),
                         n_resp=sum(resp_ind_m3,na.rm=TRUE),
                         n=n()) %>%
        mutate(zero_resp=n_resp==0) %>%
        subset(zero_resp==TRUE)) %>%
      print()
    log_debug("n cells 0 respondents:")
    (SF_smoothed_temp %>%
        group_by(REGION_NAME,wgtGpRegion_col) %>%
        dplyr::summarize(mean_crime=mean(totcrime_imp,na.rm=TRUE),
                         n_resp=sum(resp_ind_m3,na.rm=TRUE),
                         n=n()) %>%
        mutate(zero_resp=n_resp==0) %>%
        subset(zero_resp==TRUE) %>%
        nrow()) %>%
      print()
    mean_crimes <- SF_smoothed_temp %>%
      group_by(REGION_NAME,wgtGpRegion_col) %>%
      dplyr::summarize(mean_crime=mean(totcrime_imp,na.rm=TRUE),
                       n_resp=sum(resp_ind_m3,na.rm=TRUE),
                       n=n()) %>%
      mutate(zero_resp=n_resp==0) %>%
      arrange(REGION_NAME,-zero_resp,mean_crime) %>%
      inner_join(SF_smoothed_temp %>% select(REGION_NAME,wgtGpRegion,wgtGpRegion_col) %>% subset(duplicated(.)==FALSE) ,
                 by=c("REGION_NAME","wgtGpRegion_col"))
    
    
    #To be collapsed
    first_zero_resp <- mean_crimes %>%
      ungroup() %>%
      subset(zero_resp==TRUE) %>%
      group_by(REGION_NAME) %>%
      select(REGION_NAME,wgtGpRegion_col,mean_crime) %>%
      mutate(row=row_number(REGION_NAME)) %>%
      subset(row==1) %>%
      inner_join(SF_smoothed_temp %>% select(REGION_NAME,wgtGpRegion,wgtGpRegion_col) %>% subset(duplicated(.)==FALSE) ,
                 by=c("REGION_NAME","wgtGpRegion_col")) %>%
      data.frame() %>%
      select(REGION_NAME,wgtGpRegion,wgtGpRegion_col,mean_crime)
    if (nrow(first_zero_resp)==0){
      stop <- TRUE
    }
    first_zero_resp %>% print()
    log_debug("first_zero_resp (pre col):")
    first_zero_resp %>%
      select(REGION_NAME,wgtGpRegion_col,mean_crime) %>%
      subset(duplicated(.)==FALSE) %>%
      as_tibble() %>%
      print()
    #To be collapsed INTO
    closest_group <- mean_crimes %>%
      anti_join(first_zero_resp %>% select(REGION_NAME,wgtGpRegion_col)) %>%
      inner_join(first_zero_resp %>%
                   select(REGION_NAME,wgtGpRegion_to_collapse=wgtGpRegion_col,mean_crime_to_collapse=mean_crime),
                 by=c("REGION_NAME")) %>%
      mutate(dPct=abs(mean_crime_to_collapse-mean_crime)/mean_crime_to_collapse) %>%
      arrange(REGION_NAME,dPct,mean_crime) %>%
      mutate(row=row_number(REGION_NAME)) %>%
      subset(row==1) #%>%
    closest_group %>%print()
    log_debug("closest_group:")
    print(closest_group)
    
    if (nrow(closest_group)==0){
      stop <- TRUE
    }
    
    first_zero_resp <- closest_group %>%
      select(REGION_NAME,wgtGpRegion_col) %>%
      inner_join(first_zero_resp %>%select(REGION_NAME,wgtGpRegion),by=c("REGION_NAME")) %>%
      select(REGION_NAME,wgtGpRegion,wgtGpRegion_col)
    log_debug("first_zero_resp (post col):")
    print(first_zero_resp)
    log_debug("nrow(first_zero_resp) (post col):")
    log_debug(nrow(first_zero_resp))
    log_debug("first_zero_resp:")
    first_zero_resp %>% print()
    post_col_gps <- anti_join(mean_crimes,first_zero_resp %>% select(REGION_NAME,wgtGpRegion)) %>%
      bind_rows(first_zero_resp)
    log_debug("nrow(post_col_gps):")
    log_debug(nrow(post_col_gps))
    SF_smoothed_temp <- SF_smoothed_temp %>%
      select(-wgtGpRegion_col) %>%
      full_join(post_col_gps %>% select(REGION_NAME,wgtGpRegion,wgtGpRegion_col),by=c("REGION_NAME","wgtGpRegion")) %>%
      #Adding condition for states that don't get weights
      mutate(wgtGpRegion_col=case_when(is.na(wgtGpRegion_col) ~ wgtGpRegion,
                                       TRUE ~ wgtGpRegion_col)) %>%
      mutate(wgtGpRegionDesc_col=factor(wgtGpRegion_col,levels=wgtGpsRegion,labels=wgtGpRegionDescs))
    
    log_debug("End of round")
    list2env(list("SF_smoothed_temp"=SF_smoothed_temp),envir=env)
    list2env(list("ct"=ct),envir=env)
    list2env(list("stop"=stop),envir=env)
  }
  return(SF_smoothed_temp)
}
test <- collapseWgtGpsRegion(SF2)

SF2 <- test %>%
  rename(wgtGpRegion_raw=wgtGpRegion,
         wgtGpRegionDesc_raw=wgtGpRegionDesc,
         wgtGpRegion=wgtGpRegion_col,
         wgtGpRegionDesc=wgtGpRegionDesc_col)
wgtGpsRegion <- SF2 %>%
  select(wgtGpRegion) %>%
  unique() %>%
  .$wgtGpRegion %>%
  sort()
nWgtGpsRegion <- SF2 %>%
  select(wgtGpRegion) %>%
  unique() %>%
  nrow()

#colnames(SF2)
wgtGpRegionDescs <- wgtGpRegionDescs %>%
  data.frame(wgtGpRegionDesc=.) %>%
  inner_join(SF2 %>% select(wgtGpRegionDesc),by=c("wgtGpRegionDesc")) %>%
  mutate(wgtGpRegionDesc=as.character(wgtGpRegionDesc)) %>%
  mutate(wgtGpRegionDesc2=case_when(wgtGpRegionDesc=="All cities 1,000,000 or over" ~ "All cities 250,000 or over",
                                    wgtGpRegionDesc=="All cities 500,000 or over" ~ "All cities 250,000 or over",
                                    wgtGpRegionDesc=="All cities 250,000-499,999" ~ "All cities 250,000 or over",
                                    wgtGpRegionDesc=="MSA counties from 10,000 thru 24,999" ~ "MSA counties under 25,000",
                                    wgtGpRegionDesc=="MSA counties under 10,000" ~ "MSA counties under 25,000",
                                    
                                    TRUE ~ wgtGpRegionDesc))

wgtGpRegionDescs <- wgtGpRegionDescs %>%
  .$wgtGpRegionDesc %>%
  unique()

SF2 <- SF2 %>%
  mutate(totcrime_agg_rob_imp=totcrime_aggAssault_imp+totcrime_rob_imp)


#Get totals by weighting group
srs_region_control_totals <- SF2 %>%
  group_by(REGION_NAME,wgtGpRegion) %>%
  dplyr::summarize(across(all_of(crimeVarsWgt),.fns=list("sum"=sum),.names="{fn}_{col}",na.rm=TRUE),
                   .groups="drop")

SF2 <- SF2 %>%
  left_join(srs_region_control_totals,by=c("REGION_NAME","wgtGpRegion")) %>%
  mutate(k=sum_totcrime_aggAssault_imp/sum_totcrime_rob_imp) %>%
  mutate(totcrime_agg_rob_imp=totcrime_aggAssault_imp+k*totcrime_rob_imp)

#Get totals by weighting group
srs_region_control_totals <- SF2 %>%
  group_by(REGION_NAME,wgtGpRegion) %>%
  dplyr::summarize(sum_totcrime_imp=sum(totcrime_imp,na.rm=TRUE),
                   sum_totcrime_murder_imp=sum(totcrime_murder_imp,na.rm=TRUE),
                   sum_totcrime_rape_imp=sum(totcrime_rape_imp,na.rm=TRUE),
                   sum_totcrime_aggAssault_imp=sum(totcrime_aggAssault_imp,na.rm=TRUE),
                   sum_totcrime_burglary_imp=sum(totcrime_burglary_imp,na.rm=TRUE),
                   sum_totcrime_rob_imp=sum(totcrime_rob_imp,na.rm=TRUE),
                   sum_totcrime_larceny_imp=sum(totcrime_larceny_imp,na.rm=TRUE),
                   sum_totcrime_vhcTheft_imp=sum(totcrime_vhcTheft_imp,na.rm=TRUE),
                   sum_totcrime_agg_rob_imp=sum(totcrime_agg_rob_imp,na.rm=TRUE),
                   #Note (08Jun2023): Also adding violent and property
                   sum_totcrime_violent_imp=sum(totcrime_violent_imp,na.rm=TRUE),
                   sum_totcrime_property_imp=sum(totcrime_property_imp,na.rm=TRUE),
                   .groups="drop")

#Get n NIBRS Reporters and n Eligible - used for base weights and lower bounds
ratio <- SF2 %>%
  group_by(REGION_NAME) %>%
  dplyr::summarize(n=sum(resp_ind_m3==1),
                   N=n(),
                   sum_totcrime_imp_all=sum(totcrime_imp,na.rm=TRUE),
                   sum_totcrime_imp_NIBRS=sum(totcrime_imp*resp_ind_m3,na.rm=TRUE)) %>%
  mutate(baseWgt=N/n,
         lowBound=n/N,
         ratio_totcrime_imp=sum_totcrime_imp_NIBRS/sum_totcrime_imp_all)
SF2 <- SF2 %>%
  select(-matches("sum_totcrime")) %>%
  inner_join(srs_region_control_totals) %>%
  select(-matches("^(n|N|baseWgt|lowBound)$")) %>%
  full_join(ratio,by="REGION_NAME")

#07Jun2023: skipping weighting groups with crime cvg of >=99%
crime_ratio <- SF2 %>%
  group_by(REGION_NAME,wgtGpRegion) %>%
  dplyr::summarize(n=sum(resp_ind_m3==1),
                   N=n(),
                   sum_totcrime_imp_all=sum(totcrime_imp,na.rm=TRUE),
                   sum_totcrime_imp_NIBRS=sum(totcrime_imp*resp_ind_m3,na.rm=TRUE)) %>%
  mutate(ratio_totcrime_imp=sum_totcrime_imp_NIBRS/sum_totcrime_imp_all)
crossings_skips <- crime_ratio %>%
  subset(ratio_totcrime_imp>=0.99) %>%
  select(REGION_NAME,wgtGpRegion)
#03Jul2024: only assign a weight of 1 when it's a respondent
SF2_skips <- SF2 %>%
  inner_join(crossings_skips) %>%
  mutate(RegionWgt=ifelse(resp_ind_m3==1,1,NA_real_))



#ratio <- ratio %>%
#  anti_join(crossings_skips)

#30Apr2025: don't drop the skipped crossings from SF2 - 
#           instead, handle during calibration of weights
#SF2 <- SF2 %>%
#  anti_join(crossings_skips)

#Get totals by weighting group
srs_region_control_totals <- SF2 %>%
  group_by(REGION_NAME,wgtGpRegion) %>%
  dplyr::summarize(sum_totcrime_imp=sum(totcrime_imp,na.rm=TRUE),
                   sum_totcrime_murder_imp=sum(totcrime_murder_imp,na.rm=TRUE),
                   sum_totcrime_rape_imp=sum(totcrime_rape_imp,na.rm=TRUE),
                   sum_totcrime_aggAssault_imp=sum(totcrime_aggAssault_imp,na.rm=TRUE),
                   sum_totcrime_burglary_imp=sum(totcrime_burglary_imp,na.rm=TRUE),
                   sum_totcrime_rob_imp=sum(totcrime_rob_imp,na.rm=TRUE),
                   sum_totcrime_larceny_imp=sum(totcrime_larceny_imp,na.rm=TRUE),
                   sum_totcrime_vhcTheft_imp=sum(totcrime_vhcTheft_imp,na.rm=TRUE),
                   sum_totcrime_agg_rob_imp=sum(totcrime_agg_rob_imp,na.rm=TRUE),
                   #Note (08Jun2023): Also adding violent and property
                   sum_totcrime_violent_imp=sum(totcrime_violent_imp,na.rm=TRUE),
                   sum_totcrime_property_imp=sum(totcrime_property_imp,na.rm=TRUE),
                   .groups="drop")

#######################
#Check convergence

#30Apr2025: switching from a section for 1st weighting group then the rest 
#           to now being a single section

wgtGpsRegion2 <- wgtGpsRegion
wgtGpRegionDescs2 <- wgtGpRegionDescs


#15May2025: create text file that will track any allow weights <1
cat("Initializing",
    file=str_c(output_weighting_data_folder,"weights_lt1_tracker_region.txt"))

#Update (28OCT2021): Reducing print statements
#Update (23MAR2022): Stop running after first successful convergence for weighting group
#Update (23MAR2022): Lowering max_iter from 10000 to 1000
SF2_wgts2_all <- sapply(regionGps2,function(i){#Loop over weight groupings - just gp 1 for test
  log_debug("Running function SF2_wgts2_all")
  log_debug("##################")
  log_debug(paste0("Region: ",i))
  #Note (09Jan2023): Removing totcrime_imp requirement
  #Note (30Apr2025): Converting wgtGpRegion to character variable
  #Note (04May2025): Dropping respondent requirement here
  SF_temp_region <- SF2 %>%
    subset(REGION_NAME==i) %>% #& resp_ind_m3==1) %>%
    mutate(wgtGpRegion=as.character(wgtGpRegion))
  srs_control_totals_temp_region <- srs_region_control_totals %>%
    subset(REGION_NAME==i) %>%
    mutate(wgtGpRegion=as.character(wgtGpRegion))
  ratio_region <- ratio %>% subset(REGION_NAME==i)
  
  #30Apr2025: Track the environment this is in - will use for exporting objects
  funcEnv <- environment()
  #30Apr2025: Initialize a rolling list of weight groups for the current region
  #           For instance, it will track any collapsing done
  temp.wgtGpsInfo <- data.frame(wgtGp=as.character(wgtGpsRegion2),
                                wgtGpDesc=wgtGpRegionDescs2) %>%
    full_join(crossings_skips %>% 
                ungroup() %>%
                subset(REGION_NAME==i)%>% 
                select(-REGION_NAME) %>%
                mutate(wgtGpRegion=as.character(wgtGpRegion)) %>%
                mutate(skip=TRUE),
              by=c("wgtGp"="wgtGpRegion")) %>%
    #Limit to weighting groups that occur in the region
    inner_join(SF_temp_region %>% 
                 subset(REGION_NAME==i)%>% 
                 select(wgtGp=wgtGpRegion) %>%
                 unique()) %>%
    mutate(#wgtGp=as.character(wgtGp),
      wgtGpSort=as.numeric(wgtGp),
      wgtGpSuper=case_when(
        #This will be super group which we prefer to collapse within
        as.numeric(wgtGp) %in% 1:8 ~ 1, #>0 pop cities
        as.numeric(wgtGp) %in% 9:11 ~ 2, #>0 pop MSA county/SP,
        as.numeric(wgtGp) %in% 14:16 ~ 3, #>0 pop non-MSA county/SP
        as.numeric(wgtGp) %in% 18 ~ 4, #0 pop cities
        as.numeric(wgtGp) %in% 19 ~ 5, #0 pop MSA county/SP
        as.numeric(wgtGp) %in% 20 ~ 6 #0 pop non-MSA county/SP
      ),
      wgtGpSuper=as.character(wgtGpSuper),
      skip=ifelse(is.na(skip),FALSE,skip),
      success=FALSE) %>%
    arrange(wgtGpSuper,wgtGpSort)
  
  SF2_wgts_region <- sapply(temp.wgtGpsInfo$wgtGp,function(j){#Loop over weight groupings
    log_debug("#########")
    log_debug(paste0("Region: ",i,". Weight group: ",j))
    
    #Take weighting group subset within regional subset
    #Note (09Jan2023): Removing totcrime_imp requirement
    SF_temp <- SF_temp_region %>%
      subset(wgtGpRegion==j & resp_ind_m3==1)
    
    #30Apr2025: extract info for current weighting group
    temp.wgtGpInfo <- temp.wgtGpsInfo %>%
      subset(wgtGp==j)
    
    #30Apr2025: add condition for if current weighting group set to be skipped
    temp.skip <- temp.wgtGpInfo$skip == TRUE
    if (length(temp.skip)==0){
      temp.skip <- FALSE
    }
    if (temp.skip == TRUE){
      #Set the (g-)weights equal to n/N (so that final weight will be 1)
      wgts_temp <- matrix(nrow=nrow(SF_temp),ncol=1) %>% as.data.frame() %>%
        mutate(!!paste0("RegionWgt_nVar",length(crimeVarsWgt),"_comb",1) := pull(SF_temp,lowBound)) %>%
        select(paste0("RegionWgt_nVar",length(crimeVarsWgt),"_comb",1))
      
      #Update temp.wgtGpsInfo to reflect success
      temp.wgtGpsInfo <- temp.wgtGpsInfo %>%
        mutate(success=ifelse(wgtGp==j,TRUE,success))
      list2env(list("temp.wgtGpsInfo"=temp.wgtGpsInfo),funcEnv)
      
      return(bind_cols(SF_temp,wgts_temp))
    } else if (nrow(SF_temp)>0){
      #30Apr2025: wrap this is a while loop - repeat until all groups converge, or even the fully collapsed version fails
      stopAll <- FALSE
      tempEnv <- environment() #Function environment
      while (stopAll==FALSE){
        #print("Start of while")
        temp.wgtGpsInfo <- get("temp.wgtGpsInfo",envir=tempEnv) %>%
          arrange(wgtGpSuper,wgtGpSort)
        
        SF_temp <- get("SF_temp_region",envir=tempEnv) %>%
          subset(wgtGpRegion==j & resp_ind_m3==1)
        
        #30Apr2025: extract info for current weighting group
        temp.wgtGpInfo <- temp.wgtGpsInfo %>%
          subset(wgtGp==j)
        
        temp.wgtGps <- temp.wgtGpsInfo$wgtGp
        #print(temp.wgtGpsInfo)
        stopInd <- 0 #Initialize stop indicator to 0
        
        #15May2024: changing variables to match other weighting groups for 2023 onward
        #30Apr2025: move this from before the calibration function to within
        if (as.numeric(year)<2023 & j=="1"){
          crimeVarsWgtRest <- c("totcrime_murder_imp","totcrime_rape_imp",
                                "totcrime_agg_rob_imp","totcrime_burglary_imp",
                                "totcrime_larceny_imp","totcrime_vhcTheft_imp")
        } else {
          crimeVarsWgtRest <- c("totcrime_murder_imp","totcrime_rape_imp",
                                "totcrime_aggAssault_imp","totcrime_burglary_imp",
                                "totcrime_rob_imp","totcrime_larceny_imp",  
                                "totcrime_vhcTheft_imp")
        }
        crimeVarsWgt <- c(crimeVarsWgtAll,crimeVarsWgtRest)
        
        #30Apr2025: Instead of looping until we hit 0, just do the full set of variables
        out_temp <- sapply(length(crimeVarsWgtRest),function(nVar){
          log_debug(paste0("Region: ",i,". Weight group: ",j,". n SRS Variables: ",nVar+length(crimeVarsWgtAll)))
          
          #14Nov2024: vary max # of iterations by number of variables (1-7=1K, 8=1M)
          if (nVar==length(crimeVarsWgtRest)){
            maxIt2 <- 1e3*maxIt
          } else {
            maxIt2 <- maxIt
          }
          varCombs_nVar <- combn(crimeVarsWgtRest,m=nVar,simplify=FALSE)
          #print(varCombs_nVar)
          nVarCombs <- length(varCombs_nVar) #Number of combinations
          #print(nVarCombs)
          sapply(1:nVarCombs,function(nComb){#Loop over variable combinations
            if (stopInd==0){
              log_debug("stopInd==0")
              ctrlVars <- c(crimeVarsWgtAll,varCombs_nVar[[nComb]])
              print(paste0("Combination ",nComb,"/",nVarCombs))
              #print(varCombs_nVar)
              print(ctrlVars)
              
              total_temp <- srs_control_totals_temp_region %>%
                subset(wgtGpRegion==j) %>%
                select(all_of(paste0("sum_",ctrlVars))) %>%
                as.numeric()
              
              #05May2025: due to # of times we'll try to calibrate the weights (with small tweaks), 
              #             let's create a function that will make this simpler
              calWgts <- function(dat,ctrlVars,totals=total_temp,
                                  lowBound=dat$lowBound %>% unique(),
                                  upBound=10,maxIter=maxIt){
                gencalib(Xs=select(dat,all_of(ctrlVars)),
                         Zs=select(dat,all_of(ctrlVars)),
                         #d=rep(ratio_temp$baseWgt,nrow(SF_temp)),
                         d=pull(dat,baseWgt),
                         total=totals,
                         method="logit",
                         bounds=c(lowBound,upBound),#1e6),
                         max_iter=maxIter,
                         C=1)
              }
              #print(total_temp)
              #Update (28OCT2021): Running invisibly (no messages)
              #Update (04NOV2021): Adding suppressWarnings() 
              #suppressWarnings(capture.output(
              #Update (02DEC2024): Updating max number of iterations to a 10th of maxIt2
              #Update (05Dec2024): As a first step, try a max adjustment factor of 2.5 (often works)
              #Update (05May2025): Plugging in new calibration function
              capture.output(
                wgts_temp <- calWgts(SF_temp,ctrlVars,upBound=2.5,maxIter=maxIt2/100)
              )
              #29Dec2024: confirm calibration before proceeding
              if (nVar==length(crimeVarsWgtRest) & !is.null(wgts_temp)){
                test <- checkcalibration(Xs=select(SF_temp,all_of(ctrlVars)),
                                         d=pull(SF_temp,baseWgt),
                                         total=total_temp,
                                         g=wgts_temp,
                                         EPS=ifelse(any(total_temp==0),1,1e-6))#EPS=1)
                if (test$result!=TRUE){
                  log_debug("Convergence, calibration failed")
                  wgts_temp <- NULL
                } else {
                  log_debug("Calibration succeeded")
                }
              }
              #Update (06Dec2024): Adding new step - try max adjustment factor of 1.5
              if (nVar==length(crimeVarsWgtRest) & is.null(wgts_temp)){
                log_debug("No convergence - trying again with upper bound of 1.5")
                cat(str_c("\nRegion ",i," X Weight group ",j,": Trying weight 1 with upper bound of 1.5 (",maxIt2/100/1000,"K iterations)"),
                    file=str_c(output_weighting_data_folder,"weights_lt1_tracker_region.txt"),
                    append=TRUE)
                #Update (05May2025): Plugging in new calibration function
                capture.output(
                  wgts_temp <- calWgts(SF_temp,ctrlVars,upBound=1.5,maxIter=maxIt2/100)
                )
                
                #02Jan2025: confirm calibration before proceeding
                if (nVar==length(crimeVarsWgtRest) & !is.null(wgts_temp)){
                  test <- checkcalibration(Xs=select(SF_temp,all_of(ctrlVars)),
                                           d=pull(SF_temp,baseWgt),
                                           total=total_temp,
                                           g=wgts_temp,
                                           EPS=ifelse(any(total_temp==0),1,1e-6))#EPS=1)
                  if (test$result!=TRUE){
                    log_debug("Convergence, calibration failed")
                    wgts_temp <- NULL
                  } else {
                    log_debug("Calibration succeeded")
                  }
                }
              }
              #Update (05Dec2024): If above didn't work, try with adj factor of 5
              if (nVar==length(crimeVarsWgtRest) & is.null(wgts_temp)){
                log_debug("No convergence - trying again with upper bound of 5")
                cat(str_c("\nRegion ",i," X Weight group ",j,": Trying weight 1 with upper bound of 5 (",maxIt2/100/1000,"K iterations)"),
                    file=str_c(output_weighting_data_folder,"weights_lt1_tracker_region.txt"),
                    append=TRUE)
                #Update (05May2025): Plugging in new calibration function
                capture.output(
                  wgts_temp <- calWgts(SF_temp,ctrlVars,upBound=5,maxIter=maxIt2/100)
                )
                
                #02Jan2025: confirm calibration before proceeding
                if (nVar==length(crimeVarsWgtRest) & !is.null(wgts_temp)){
                  test <- checkcalibration(Xs=select(SF_temp,all_of(ctrlVars)),
                                           d=pull(SF_temp,baseWgt),
                                           total=total_temp,
                                           g=wgts_temp,
                                           EPS=ifelse(any(total_temp==0),1,1e-6))#EPS=1)
                  if (test$result!=TRUE){
                    log_debug("Convergence, calibration failed")
                    wgts_temp <- NULL
                  } else {
                    log_debug("Calibration succeeded")
                  }
                }
              }
              
              #Update (06Feb2025): Initializing temp.text to NA_character_
              temp.text <- NA_character_
              
              #Update (05Dec2024): If above didn't work, then proceed with usual max adj factor (e.g., 10)
              if (nVar==length(crimeVarsWgtRest) & is.null(wgts_temp)){
                log_debug(str_c("No convergence - trying again with upper bound of ",maxAdj))
                cat(str_c("\nRegion ",i," X Weight group ",j,": Trying weight 1 with upper bound of ",maxAdj," (",maxIt2/100/1000,"K iterations)"),
                    file=str_c(output_weighting_data_folder,"weights_lt1_tracker_region.txt"),
                    append=TRUE)
                #Update (05May2025): Plugging in new calibration function
                temp.text <- capture.output(
                  wgts_temp <- calWgts(SF_temp,ctrlVars,upBound=maxAdj,maxIter=maxIt2/100)
                )
                #02Jan2025: confirm calibration before proceeding
                if (nVar==length(crimeVarsWgtRest) & !is.null(wgts_temp)){
                  test <- checkcalibration(Xs=select(SF_temp,all_of(ctrlVars)),
                                           d=pull(SF_temp,baseWgt),
                                           total=total_temp,
                                           g=wgts_temp,
                                           EPS=ifelse(any(total_temp==0),1,1e-6))#EPS=1)
                  if (test$result!=TRUE){
                    log_debug("Convergence, calibration failed")
                    wgts_temp <- NULL
                  } else {
                    log_debug("Calibration succeeded")
                  }
                }
              }
              #06Feb2025: if that fails (and no bounds were given by last run), try a variety of values bw 10 to 1.1 until we get bounds
              for (temp.maxAdj in seq(10,1.1,by=-0.1) %>% subset(!. %in% c(1.5,2.5,5,10))){
                if (length(temp.text)==0 & is.null(wgts_temp) & nVar==length(crimeVarsWgtRest)){
                  log_debug(str_c("No convergence - trying again with upper bound of ",temp.maxAdj))
                  cat(str_c("\nRegion ",i," X Weight group ",j,": Trying weight 1 with upper bound of ",temp.maxAdj," (",maxIt2/100/1000,"K iterations)"),
                      file=str_c(output_weighting_data_folder,"weights_lt1_tracker_region.txt"),
                      append=TRUE)
                  #Update (05May2025): Plugging in new calibration function
                  temp.text <- capture.output(
                    wgts_temp <- calWgts(SF_temp,ctrlVars,upBound=temp.maxAdj,maxIter=maxIt2/100)
                  )
                  
                  #02Jan2025: confirm calibration before proceeding
                  if (nVar==length(crimeVarsWgtRest) & !is.null(wgts_temp)){
                    test <- checkcalibration(Xs=select(SF_temp,all_of(ctrlVars)),
                                             d=pull(SF_temp,baseWgt),
                                             total=total_temp,
                                             g=wgts_temp,
                                             EPS=ifelse(any(total_temp==0),1,1e-6))#EPS=1)
                    if (test$result!=TRUE){
                      log_debug("Convergence, calibration failed")
                      wgts_temp <- NULL
                    } else {
                      log_debug("Calibration succeeded")
                    }
                  }
                }
              }
              
              #02Jan2025: initialize max adjustment factor variables
              temp.upper <- maxAdj
              maxAdj2 <- maxAdj
              temp.upper2 <- maxAdj
              maxAdj3 <- maxAdj
              temp.upper3 <- maxAdj
              maxAdj4 <- maxAdj
              #02Dec2024: if convergence fails for full (e.g., 8/8 vars) model, capture bounds of g weights 
              if (nVar==length(crimeVarsWgtRest) & is.null(wgts_temp)){
                log_debug("No convergence - capturing rolling upper bound for adj factor")
                temp.upper <- temp.text[2] %>%
                  str_extract("(?<=and\\s{1,2})(\\d|\\.)+(?=(|\\s{1,2})$)") %>%
                  as.numeric()
                log_debug(str_c("Rolling upper bound is ",temp.upper))
                #Add a bit of padding to rolling upper bound to get updated upper bound
                #30Apr2025: adding na.rm=TRUE to min()
                maxAdj2 <- min(maxAdj,temp.upper*1.25,temp.upper+0.5,na.rm=TRUE)
                #02Jan2024: if maxAdj2==maxAdj, go ahead and set it to half of maxAdj so we can try to find a solution - if it fails to provide even the bounds, revert back to maxAdj
                tempInd <- FALSE #Initialize indicator whether we're trying maxAdj/2
                if (maxAdj==maxAdj2){
                  log_debug("Testing convergence with half of maxAdj")
                  tempInd <- TRUE
                  maxAdj2 <- maxAdj/2
                }
                log_debug(str_c("Updated upper bound is ",maxAdj2))
                #02Dec2024: if updated upper bound < original upper bound, try again with weights of 1 but updated upper bound
                #           Use full maxIt2 this time
                if (maxAdj2<maxAdj){
                  log_debug(str_c("No convergence - trying again with upper bound of ",maxAdj2))
                  cat(str_c("\nRegion ",i," X Weight group ",j,": Trying weight 1 with upper bound of ",maxAdj2," (",maxIt2/10/1000,"K iterations)"),
                      file=str_c(output_weighting_data_folder,"weights_lt1_tracker_region.txt"),
                      append=TRUE)
                  #Update (05May2025): Plugging in new calibration function
                  temp.text2 <- capture.output(
                    wgts_temp <- calWgts(SF_temp,ctrlVars,upBound=maxAdj2,maxIter=maxIt2/10)
                  )
                  if (length(temp.text2)>=2){
                    temp.upper2 <- temp.text2[2] %>%
                      str_extract("(?<=and\\s{1,2})(\\d|\\.)+(?=(|\\s{1,2})$)") %>%
                      as.numeric()
                  } else if (tempInd==TRUE){
                    log_debug("Reverting back to original rolling upper bound")
                    temp.upper2 <- temp.upper
                    #30Apr2025: adding na.rm=TRUE to min()
                    maxAdj2 <- min(maxAdj,temp.upper*1.25,temp.upper+0.5,na.rm=TRUE)
                  }
                  #02Jan2025: confirm calibration before proceeding
                  if (nVar==length(crimeVarsWgtRest) & !is.null(wgts_temp)){
                    test <- checkcalibration(Xs=select(SF_temp,all_of(ctrlVars)),
                                             d=pull(SF_temp,baseWgt),
                                             total=total_temp,
                                             g=wgts_temp,
                                             EPS=ifelse(any(total_temp==0),1,1e-6))#EPS=1)
                    if (test$result!=TRUE){
                      log_debug("Convergence, calibration failed")
                      wgts_temp <- NULL
                    } else {
                      log_debug("Calibration succeeded")
                    }
                  }
                }
                #05Dec2024: one last try before moving onto final weights <1
                #02Jan2025: this is now the 2nd last try (added extra step today)
                #           also, including 2nd rolling upper bound minus half difference bw it and 1st rolling upper bound
                #24Apr2025: ensuring maxAdj3 is at least 1.05
                #30Apr2025: adding na.rm=TRUE to min()
                maxAdj3 <- min(temp.upper2*1.05,temp.upper2+0.1,1.5*temp.upper2-0.5*temp.upper,na.rm=TRUE) %>%
                  max(1.05)
                if (nVar==length(crimeVarsWgtRest) & is.null(wgts_temp) & maxAdj3<maxAdj){
                  log_debug(str_c("No convergence - trying again with upper bound of ",maxAdj3))
                  cat(str_c("\nRegion ",i," X Weight group ",j,": Trying weight 1 with upper bound of ",maxAdj3," (",maxIt2/10/1000,"K iterations)"),
                      file=str_c(output_weighting_data_folder,"weights_lt1_tracker_region.txt"),
                      append=TRUE)
                  #Update (05May2025): Plugging in new calibration function
                  temp.text3 <- capture.output(
                    wgts_temp <- calWgts(SF_temp,ctrlVars,upBound=maxAdj3,maxIter=maxIt2/10)
                  )
                  if (length(temp.text3)>=2){
                    temp.upper3 <- temp.text3[2] %>%
                      str_extract("(?<=and\\s{1,2})(\\d|\\.)+(?=(|\\s{1,2})$)") %>%
                      as.numeric()
                  } else {
                    temp.upper3 <- temp.upper2
                  }
                  #02Jan2025: confirm calibration before proceeding
                  if (nVar==length(crimeVarsWgtRest) & !is.null(wgts_temp)){
                    test <- checkcalibration(Xs=select(SF_temp,all_of(ctrlVars)),
                                             d=pull(SF_temp,baseWgt),
                                             total=total_temp,
                                             g=wgts_temp,
                                             EPS=ifelse(any(total_temp==0),1,1e-6))#EPS=1)
                    if (test$result!=TRUE){
                      log_debug("Convergence, calibration failed")
                      wgts_temp <- NULL
                    } else {
                      log_debug("Calibration succeeded")
                    }
                  }
                }
                #02Jan2025: adding one last try before moving onto final weights <1...
                #30Apr2025: adding na.rm=TRUE to min()
                maxAdj4 <- min(temp.upper3*0.99,1.5*temp.upper3-0.5*temp.upper2,na.rm=TRUE)
                #02Jan2025: just to ensure enough wiggle room
                maxAdj4 <- max(maxAdj4,1.02)
                log_debug(str_c("maxAdj4: ",maxAdj4))
                log_debug(str_c("temp.upper3: ",temp.upper3))
                if (nVar==length(crimeVarsWgtRest) & is.null(wgts_temp) & maxAdj4<maxAdj & temp.upper3 != maxAdj){
                  
                  log_debug(str_c("No convergence - trying again with upper bound of ",maxAdj4))
                  cat(str_c("\nRegion ",i," X Weight group ",j,": Trying weight 1 with upper bound of ",maxAdj4," (",maxIt2/10/1000,"K iterations)"),
                      file=str_c(output_weighting_data_folder,"weights_lt1_tracker_region.txt"),
                      append=TRUE)
                  #Update (05May2025): Plugging in new calibration function
                  capture.output(
                    wgts_temp <- calWgts(SF_temp,ctrlVars,upBound=maxAdj4,maxIter=maxIt2/10)
                  )
                  #02Jan2025: confirm calibration before proceeding
                  if (nVar==length(crimeVarsWgtRest) & !is.null(wgts_temp)){
                    test <- checkcalibration(Xs=select(SF_temp,all_of(ctrlVars)),
                                             d=pull(SF_temp,baseWgt),
                                             total=total_temp,
                                             g=wgts_temp,
                                             EPS=ifelse(any(total_temp==0),1,1e-6))#EPS=1)
                    if (test$result!=TRUE){
                      log_debug("Convergence, calibration failed")
                      wgts_temp <- NULL
                    } else {
                      log_debug("Calibration succeeded")
                    }
                  }
                }
              }
              #21Nov2024: if coverage fails again for full model, try 0.998 then 0.99 thru 0.9 min weight in increments of 0.01
              for (temp.minAdj in c(0.998,seq(0.99,0.9,by=-0.01))){
                if (is.null(wgts_temp) & nVar==length(crimeVarsWgtRest)){
                  log_debug(str_c("No convergence - trying again with min final weight of ",temp.minAdj,")"))
                  cat(str_c("\nRegion ",i," X Weight group ",j,": Trying weight ",temp.minAdj," (",maxIt2/10/1000,"K iterations)"),
                      file=str_c(output_weighting_data_folder,"weights_lt1_tracker_region.txt"),
                      append=TRUE)
                  #print()
                  #Update (05May2025): Plugging in new calibration function
                  temp.text2 <- capture.output(
                    wgts_temp <- calWgts(SF_temp,ctrlVars,
                                         lowBound=temp.minAdj*pull(SF_temp,
                                                                   lowBound) %>% 
                                           unique(),
                                         upBound=maxAdj2,
                                         maxIter=maxIt2/10)
                  )
                  #02Jan2025: confirm calibration before proceeding
                  if (nVar==length(crimeVarsWgtRest) & !is.null(wgts_temp)){
                    test <- checkcalibration(Xs=select(SF_temp,all_of(ctrlVars)),
                                             d=pull(SF_temp,baseWgt),
                                             total=total_temp,
                                             g=wgts_temp,
                                             EPS=ifelse(any(total_temp==0),1,1e-6))#EPS=1)
                    if (test$result!=TRUE){
                      log_debug("Convergence, calibration failed")
                      wgts_temp <- NULL
                    } else {
                      log_debug("Calibration succeeded")
                    }
                  }
                }
              }
              #Update (27AUG2021): Ensure model converges AND calibration totals can be hit
              if (is.null(wgts_temp)){
                log_debug("No convergence")
                wgts_temp <- matrix(nrow=nrow(SF_temp),ncol=1) %>% as.data.frame() %>%
                  mutate(!!paste0("RegionWgt_nVar",nVar+length(crimeVarsWgtAll),"_comb",nComb) := rep(NA,nrow(SF_temp))) %>%
                  select(paste0("RegionWgt_nVar",nVar+length(crimeVarsWgtAll),"_comb",nComb))
              } else {
                #Update (29OCT2021): Run calibration check silently
                capture.output(test <- checkcalibration(Xs=select(SF_temp,all_of(ctrlVars)),
                                                        #d=rep(1,nrow(SF_temp)),
                                                        d=pull(SF_temp,baseWgt),
                                                        total=total_temp,
                                                        g=wgts_temp,
                                                        EPS=ifelse(any(total_temp==0),1,1e-6)))#EPS=1))
                if (test$result==TRUE){
                  log_debug("Success!")
                  stopInd <- 1
                  
                  list2env(list("stopInd"=stopInd),tempEnv) #Update stopInd in function environment
                  
                  #Update stopAll in designated environment
                  list2env(list("stopAll"=TRUE),envir=tempEnv)
                  
                  #30Apr2025: update temp.wgtGpsInfo to reflect success
                  temp.wgtGpsInfo <- temp.wgtGpsInfo %>%
                    mutate(success=ifelse(wgtGp==j,TRUE,success))
                  list2env(list("temp.wgtGpsInfo"=temp.wgtGpsInfo),funcEnv)
                  list2env(list("temp.wgtGpsInfo"=temp.wgtGpsInfo),tempEnv)
                  
                  wgts_temp <- wgts_temp %>%
                    data.frame() %>%
                    dplyr::mutate(!!paste0("RegionWgt_nVar",nVar+length(crimeVarsWgtAll),"_comb",nComb) := .) %>%
                    select(paste0("RegionWgt_nVar",nVar+length(crimeVarsWgtAll),"_comb",nComb))
                } else {
                  log_debug("Convergence, calibration failed")
                  wgts_temp <- matrix(nrow=nrow(SF_temp),ncol=1) %>% as.data.frame() %>%
                    mutate(!!paste0("RegionWgt_nVar",nVar+length(crimeVarsWgtAll),"_comb",nComb) := rep(NA,nrow(SF_temp))) %>%
                    select(paste0("RegionWgt_nVar",nVar+length(crimeVarsWgtAll),"_comb",nComb))
                }
              }
            } else {
              #Skipping bc stopInd==1
              wgts_temp <- matrix(nrow=nrow(SF_temp),ncol=1) %>% as.data.frame() %>%
                mutate(!!paste0("RegionWgt_nVar",nVar+length(crimeVarsWgtAll),"_comb",nComb) := rep(NA,nrow(SF_temp))) %>%
                select(paste0("RegionWgt_nVar",nVar+length(crimeVarsWgtAll),"_comb",nComb))
            }
            return(wgts_temp)
            
          },simplify=FALSE) %>%
            bind_cols()
          
        },simplify=FALSE) %>%
          {bind_cols(SF_temp,.)}
        if (stopInd==0){
          #30Apr2025: Failed - time to collapse
          
          #Identify records in super group - 
          #  Prefer to collapse within same super group
          temp.wgtGpSuper <- temp.wgtGpInfo$wgtGpSuper
          # print("temp.wgtGpSuper:")
          # print(temp.wgtGpSuper)
          # print("temp.wgtGpInfo:")
          # print(temp.wgtGpInfo)
          # print("temp.wgtGpsInfo:")
          # print(temp.wgtGpsInfo)
          
          temp.wgtGpsSuper <- temp.wgtGpsInfo %>%
            subset(wgtGpSuper==temp.wgtGpSuper)
          
          temp.nWgtGpsSuper <- nrow(temp.wgtGpsSuper)
          if (temp.nWgtGpsSuper>1){#1+ other record in super group
            #Identify where the current weighting group falls within super group
            temp.whichGp <- which(temp.wgtGpsSuper$wgtGp == j)
            #If there's a weighting group below it, collapse with that one
            #Otherwise, collapse with one above it
            if (temp.whichGp < temp.nWgtGpsSuper){
              temp.colGpInfo <- temp.wgtGpsSuper[temp.whichGp+1,]
            } else {
              temp.colGpInfo <- temp.wgtGpsSuper[temp.whichGp-1,]
            }
          } else {#No other record in super group
            if (str_detect(temp.wgtGpSuper,"(^| )1($|;)")){#>0 pop city
              #Collapse with zero pop city - if it doesn't exist, fail
              #if ("4" %in% temp.wgtGpsInfo$wgtGpSuper){
              #  temp.colGpInfo <- temp.wgtGpsSuper %>% subset(wgtGpSuper=="4")
              #} if (temp.wgtGpsInfo %>% 
              if (temp.wgtGpsInfo %>% 
                  subset(str_detect(wgtGp,j,negate=TRUE)) %>% 
                  pull(wgtGpSuper) %>% 
                  str_detect("(^| )1($|;)") %>%
                  any()){
                temp.colGpInfo <- temp.wgtGpsInfo %>% 
                  subset(str_detect(wgtGp,j,negate=TRUE)) %>% 
                  subset(str_detect(wgtGpSuper,"(^| )1($|;)")) %>% 
                  .[1,]
              } else if (temp.wgtGpsInfo %>% 
                         subset(str_detect(wgtGp,j,negate=TRUE)) %>% 
                         pull(wgtGpSuper) %>% 
                         str_detect("(^| )4($|;)") %>%
                         any()){
                temp.colGpInfo <- temp.wgtGpsInfo %>% 
                  subset(str_detect(wgtGp,j,negate=TRUE)) %>% 
                  subset(str_detect(wgtGpSuper,"(^| )4($|;)")) %>% 
                  .[1,]
              } else if (temp.wgtGpsInfo %>% 
                         subset(str_detect(wgtGp,j,negate=TRUE)) %>% 
                         pull(wgtGpSuper) %>% 
                         str_detect("(^| )2($|;)") %>%
                         any()){
                temp.colGpInfo <- temp.wgtGpsInfo %>% 
                  subset(str_detect(wgtGp,j,negate=TRUE)) %>% 
                  subset(str_detect(wgtGpSuper,"(^| )2($|;)")) %>% 
                  .[1,]
              } else if (temp.wgtGpsInfo %>% 
                         subset(str_detect(wgtGp,j,negate=TRUE)) %>% 
                         pull(wgtGpSuper) %>% 
                         str_detect("(^| )3($|;)") %>%
                         any()){
                temp.colGpInfo <- temp.wgtGpsInfo %>% 
                  subset(str_detect(wgtGp,j,negate=TRUE)) %>% 
                  subset(str_detect(wgtGpSuper,"(^| )3($|;)")) %>% 
                  .[1,]
              } else if (temp.wgtGpsInfo %>% 
                         subset(str_detect(wgtGp,j,negate=TRUE)) %>% 
                         pull(wgtGpSuper) %>% 
                         str_detect("(^| )5($|;)") %>%
                         any()){
                temp.colGpInfo <- temp.wgtGpsInfo %>% 
                  subset(str_detect(wgtGp,j,negate=TRUE)) %>% 
                  subset(str_detect(wgtGpSuper,"(^| )5($|;)")) %>% 
                  .[1,]
              } else if (temp.wgtGpsInfo %>% 
                         subset(str_detect(wgtGp,j,negate=TRUE)) %>% 
                         pull(wgtGpSuper) %>% 
                         str_detect("(^| )6($|;)") %>%
                         any()){
                temp.colGpInfo <- temp.wgtGpsInfo %>% 
                  subset(str_detect(wgtGp,j,negate=TRUE)) %>% 
                  subset(str_detect(wgtGpSuper,"(^| )6($|;)")) %>% 
                  .[1,]
              }   else {
                stop("Couldn't find group to collapse with",call.=FALSE)
              }
            } else if (str_detect(temp.wgtGpSuper,"(^| )2($|;)")){#>0 pop MSA
              #For now, throw an error... eventually, I'll prob want to pick bw
              #  collapsing 1st with super group 3 or group 5
              if (temp.wgtGpsInfo %>% 
                  subset(str_detect(wgtGp,j,negate=TRUE)) %>% 
                  pull(wgtGpSuper) %>% 
                  str_detect("(^| )3($|;)") %>%
                  any()){
                temp.colGpInfo <- temp.wgtGpsInfo %>% 
                  subset(str_detect(wgtGp,j,negate=TRUE)) %>% 
                  subset(str_detect(wgtGpSuper,"(^| )3($|;)")) %>% 
                  .[1,]
              } else if (temp.wgtGpsInfo %>% 
                         subset(str_detect(wgtGp,j,negate=TRUE)) %>% 
                         pull(wgtGpSuper) %>% 
                         str_detect("(^| )5($|;)") %>%
                         any()){
                temp.colGpInfo <- temp.wgtGpsInfo %>% 
                  subset(str_detect(wgtGp,j,negate=TRUE)) %>% 
                  subset(str_detect(wgtGpSuper,"(^| )5($|;)")) %>% 
                  .[1,]
              } else if (temp.wgtGpsInfo %>% 
                         subset(str_detect(wgtGp,j,negate=TRUE)) %>% 
                         pull(wgtGpSuper) %>% 
                         str_detect("(^| )6($|;)") %>%
                         any()){
                temp.colGpInfo <- temp.wgtGpsInfo %>% 
                  subset(str_detect(wgtGp,j,negate=TRUE)) %>% 
                  subset(str_detect(wgtGpSuper,"(^| )6($|;)")) %>% 
                  .[1,]
              }  else if (temp.wgtGpsInfo %>% 
                          subset(str_detect(wgtGp,j,negate=TRUE)) %>% 
                          pull(wgtGpSuper) %>% 
                          str_detect("(^| )4($|;)") %>%
                          any()){
                temp.colGpInfo <- temp.wgtGpsInfo %>% 
                  subset(str_detect(wgtGp,j,negate=TRUE)) %>% 
                  subset(str_detect(wgtGpSuper,"(^| )4($|;)")) %>% 
                  .[1,]
              } else if (temp.wgtGpsInfo %>% 
                         subset(str_detect(wgtGp,j,negate=TRUE)) %>% 
                         pull(wgtGpSuper) %>% 
                         str_detect("(^| )1($|;)") %>%
                         any()){
                temp.colGpInfo <- temp.wgtGpsInfo %>% 
                  subset(str_detect(wgtGp,j,negate=TRUE)) %>% 
                  subset(str_detect(wgtGpSuper,"(^| )1($|;)")) %>% 
                  .[1,]
              }else {
                stop("Couldn't find group to collapse with",call.=FALSE)
              }
            } else if (str_detect(temp.wgtGpSuper,"(^| )3($|;)")){#>0 pop non-MSA
              #For now, throw an error... eventually, I'll prob want to pick bw
              #  collapsing 1st with super group 4 or group 6
              if (temp.wgtGpsInfo %>% 
                  subset(str_detect(wgtGp,j,negate=TRUE)) %>% 
                  pull(wgtGpSuper) %>% 
                  str_detect("(^| )2($|;)") %>%
                  any()){
                temp.colGpInfo <- temp.wgtGpsInfo %>% 
                  subset(str_detect(wgtGp,j,negate=TRUE)) %>% 
                  subset(str_detect(wgtGpSuper,"(^| )2($|;)")) %>% 
                  .[1,]
              }  else if (temp.wgtGpsInfo %>% 
                          subset(str_detect(wgtGp,j,negate=TRUE)) %>% 
                          pull(wgtGpSuper) %>% 
                          str_detect("(^| )6($|;)") %>%
                          any()){
                temp.colGpInfo <- temp.wgtGpsInfo %>% 
                  subset(str_detect(wgtGp,j,negate=TRUE)) %>% 
                  subset(str_detect(wgtGpSuper,"(^| )6($|;)")) %>% 
                  .[1,]
              } else if (temp.wgtGpsInfo %>% 
                         subset(str_detect(wgtGp,j,negate=TRUE)) %>% 
                         pull(wgtGpSuper) %>% 
                         str_detect("(^| )5($|;)") %>%
                         any()){
                temp.colGpInfo <- temp.wgtGpsInfo %>% 
                  subset(str_detect(wgtGp,j,negate=TRUE)) %>% 
                  subset(str_detect(wgtGpSuper,"(^| )5($|;)")) %>% 
                  .[1,]
              } else if (temp.wgtGpsInfo %>% 
                         subset(str_detect(wgtGp,j,negate=TRUE)) %>% 
                         pull(wgtGpSuper) %>% 
                         str_detect("(^| )4($|;)") %>%
                         any()){
                temp.colGpInfo <- temp.wgtGpsInfo %>% 
                  subset(str_detect(wgtGp,j,negate=TRUE)) %>% 
                  subset(str_detect(wgtGpSuper,"(^| )4($|;)")) %>% 
                  .[1,]
              } else if (temp.wgtGpsInfo %>% 
                         subset(str_detect(wgtGp,j,negate=TRUE)) %>% 
                         pull(wgtGpSuper) %>% 
                         str_detect("(^| )1($|;)") %>%
                         any()){
                temp.colGpInfo <- temp.wgtGpsInfo %>% 
                  subset(str_detect(wgtGp,j,negate=TRUE)) %>% 
                  subset(str_detect(wgtGpSuper,"(^| )1($|;)")) %>% 
                  .[1,]
              } else {
                stop("Couldn't find group to collapse with",call.=FALSE)
              }
            } else if (str_detect(temp.wgtGpSuper,"(^| )4($|;)")){#0 pop city
              #Collapse with whichever (other) group has the smallest city group
              #If no group available, fail (for now)
              temp.colGpsInfo <- temp.wgtGpsInfo %>%
                subset(str_detect(wgtGp,j,negate=TRUE) & 
                         wgtGpSuper == "1")
              if (nrow(temp.colGpsInfo)>0){
                temp.colGpInfo <- temp.colGpsInfo[nrow(temp.colGpsInfo),]
              } else {
                stop("Couldn't find group to collapse with",call.=FALSE)
              }
            } else if (str_detect(temp.wgtGpSuper,"(^| )5($|;)")){#0 pop MSA
              #Collapse with super gp 6 if present, then gp 4, otherwise fail
              if ("6" %in% temp.wgtGpsInfo$wgtGpSuper){
                temp.colGpInfo <- temp.wgtGpsInfo %>% subset(wgtGpSuper=="6")
              } else if ("4" %in% temp.wgtGpsInfo$wgtGpSuper){
                temp.colGpInfo <- temp.wgtGpsInfo %>% subset(wgtGpSuper=="4")
              } else {
                stop("Couldn't find group to collapse with",call.=FALSE)
              }
            } else if (str_detect(temp.wgtGpSuper,"(^| )6($|;)")){#0 pop non-MSA
              #Collapse with super gp 5 if present, then gp 4, otherwise fail
              if ("5" %in% temp.wgtGpsInfo$wgtGpSuper){
                temp.colGpInfo <- temp.wgtGpsInfo %>% subset(wgtGpSuper=="5")
              } else if ("4" %in% temp.wgtGpsInfo$wgtGpSuper){
                temp.colGpInfo <- temp.wgtGpsInfo %>% subset(wgtGpSuper=="4")
              } else {
                # log_debug("Current weighting groups:")
                # print(temp.wgtGpsInfo)
                stop("Couldn't find group to collapse with",call.=FALSE)
              }
            }
          }
          
          #Create a new group by combining info from current and collapsing gp
          log_debug(str_c("Collapsing group ",j," with ",temp.colGpInfo$wgtGp))
          # print("j:")
          # print(j)
          temp.wgtGpV <- j %>% str_split_1("; ")
          # print("temp.colGpInfo$wgtGp:")
          # print(temp.colGpInfo$wgtGp)
          temp.colGpV <- temp.colGpInfo$wgtGp %>% str_split_1("; ")
          temp.newGp <- c(temp.wgtGpV,temp.colGpV) %>% 
            unique() 
          #Before we sort this, store the proper order - 
          #  will use this later to make sure order of group descriptions
          #  matches the group numbers
          temp.order <- temp.newGp %>% str_rank(numeric=TRUE)
          temp.newGp <- temp.newGp %>%
            str_sort(numeric=TRUE) %>%
            str_flatten(collapse="; ")
          
          temp.wgtGpDesc <- temp.wgtGpInfo$wgtGpDesc
          # print("temp.wgtGpDesc:")
          # print(temp.wgtGpDesc)
          temp.wgtGpDescV <- temp.wgtGpDesc %>% str_split_1("; ")
          # print("temp.wgtGpDescV:")
          # print(temp.wgtGpDescV)
          temp.colGpDesc <- temp.colGpInfo$wgtGpDesc
          # print("temp.colGpDesc:")
          # print(temp.colGpDesc)
          temp.colGpDescV <- temp.colGpDesc %>% str_split_1("; ")
          # print("temp.colGpDescV:")
          # print(temp.colGpDescV)
          temp.newGpDesc <- c(temp.wgtGpDescV,temp.colGpDescV) %>%
            unique() %>%
            .[temp.order] %>% #Sort to match new group numbers
            str_flatten(collapse="; ")
          
          # print("temp.wgtGpSuper:")
          # print(temp.wgtGpSuper)
          temp.wgtGpSuperV <- temp.wgtGpSuper %>% str_split_1("; ")
          temp.colGpSuper <- temp.colGpInfo$wgtGpSuper
          # print("temp.colGpSuper:")
          # print(temp.colGpSuper)
          temp.colGpSuperV <- temp.colGpSuper %>% str_split_1("; ")
          temp.newGpSuper <- c(temp.wgtGpSuperV,temp.colGpSuperV) %>%
            unique() %>%
            str_sort(numeric=TRUE) %>%
            str_flatten(collapse="; ")
          
          # print("temp.newGp:")
          # print(temp.newGp)
          # print("temp.newGpDesc:")
          # print(temp.newGpDesc)
          # print("temp.newGpSuper:")
          # print(temp.newGpSuper)
          
          #Construct record for our newly formed group
          temp.newGpInfo <- data.frame(wgtGp=temp.newGp,
                                       wgtGpSort=min(as.numeric(temp.wgtGpV),
                                                     as.numeric(temp.colGpV)),
                                       wgtGpDesc=temp.newGpDesc,
                                       skip=FALSE,
                                       wgtGpSuper=temp.newGpSuper,
                                       success=FALSE)
          #Update our rolling weight group list (include new group and drop old)
          temp.wgtGpsInfo <- temp.wgtGpsInfo %>%
            subset(!wgtGp %in% c(j,temp.colGpInfo$wgtGp)) %>%
            bind_rows(temp.newGpInfo) %>%
            arrange(wgtGpSuper,wgtGpSort) %>%
            unique()
          
          #Move this rolling weight group list to our designated environment
          list2env(list("temp.wgtGpsInfo"=temp.wgtGpsInfo),envir=tempEnv)
          list2env(list("temp.wgtGpsInfo"=temp.wgtGpsInfo),envir=funcEnv)
          
          #In addition, let's update the data and control totals to reflect the collapsing
          SF_temp_region <- SF_temp_region %>%
            mutate(
              wgtGpRegion=case_when(
                wgtGpRegion %in% c(j,temp.colGpInfo$wgtGp) ~ temp.newGp,
                TRUE ~ wgtGpRegion),
              wgtGpRegionDesc=case_when(
                wgtGpRegionDesc == temp.wgtGpDesc ~ temp.newGpDesc,
                wgtGpRegionDesc == temp.colGpDesc ~ temp.newGpDesc,
                TRUE ~ wgtGpRegionDesc)
            )
          srs_control_totals_temp_region <- srs_control_totals_temp_region %>%
            mutate(wgtGpRegion=case_when(
              wgtGpRegion %in% c(j,temp.colGpInfo$wgtGp) ~ temp.newGp,
              TRUE ~ wgtGpRegion)) %>%
            group_by(REGION_NAME,wgtGpRegion) %>%
            dplyr::summarize(across(matches("^sum_"),sum),.groups="drop")
          
          #Move both of these objects to the desired environment
          list2env(
            list(
              "SF_temp_region"=SF_temp_region,
              "srs_control_totals_temp_region"=srs_control_totals_temp_region),
            envir = tempEnv)
          list2env(
            list(
              "SF_temp_region"=SF_temp_region,
              "srs_control_totals_temp_region"=srs_control_totals_temp_region),
            envir = funcEnv)
          
          #Adjust j for next iteration
          j <- temp.newGp
          list2env(list("j"=j),envir=tempEnv)
          
          
          wgts_temp <- matrix(nrow=nrow(SF_temp),ncol=1) %>% as.data.frame() %>%
            mutate(!!paste0("RegionWgt_nVar",1,"_comb",1) := rep(NA,nrow(SF_temp))) %>%
            select(paste0("RegionWgt_nVar",1,"_comb",1))
          
          #list2env(list("j"=j),envir=funcEnv)
          #return(NULL)
        } else {
          #Skipping bc stopInd==1
          wgts_temp <- matrix(nrow=nrow(SF_temp),ncol=1) %>% as.data.frame() %>%
            mutate(!!paste0("RegionWgt_nVar",1,"_comb",1) := rep(NA,nrow(SF_temp))) %>%
            select(paste0("RegionWgt_nVar",1,"_comb",1))
        }
        out_temp <- bind_cols(out_temp,
                              wgts_temp)
      }
      return(out_temp)
      
    }else {
      log_debug("No LEAs in region X weighting group")
      return(NULL)
    }
    
  },simplify=FALSE) %>%
    bind_rows()
  if (temp.wgtGpsInfo %>% subset(success==FALSE) %>% nrow() == 0){
    log_debug("No failures. Moving onto next region.")
    #Outputting temp.wgtGpsInfo to global environment
    temp.out <- temp.wgtGpsInfo %>%
      mutate(REGION_NAME=i) %>%
      list()
    
    names(temp.out) <- str_c("wgtGpsInfo_",i)
    
    list2env(temp.out,envir=.GlobalEnv)
    
  } else {
    log_debug("1+ failure remains. Running through weight groups again.")
  }
  
  #If cell not empty, merge on SF
  #01May2024: getting errors when merging in certain regions... modifying merge (only keep certain variables from SF2_wgts_region)
  #04May2025: changing from left to full join
  if (nrow(SF2_wgts_region)>0){
    #print("colnames(SF2_wgts_region):")
    #print(colnames(SF2_wgts_region))
    SF2_wgts_region <- SF2_wgts_region %>%
      select(ORI,matches("^RegionWgt_")) %>% #01May2024: added today
      #left_join(SF_temp_region,by=colnames(SF_temp_region))
      full_join(SF_temp_region,by=c("ORI"))
  }
  
  #04May2025: bc of how the collapsing algorithm works, some ORIs may appear 
  #             multiple times... in that case, always choose the last record
  SF2_wgts_region <- SF2_wgts_region %>%
    slice_tail(n=1,by=ORI)
  #print(out_temp)
},simplify=FALSE) %>%
  bind_rows()

#05May2025: compile summaries of weight groups after collapsing
wgtGpsInfo <- mget(str_c("wgtGpsInfo_",c("Midwest","Northeast","South","West"))) %>%
  bind_rows()

wgtGpsInfo %>%
  select(-wgtGpDesc) %>% #Could be very big - drop for printout
  select(REGION_NAME,wgtGp,everything()) %>%
  print()


#04May2025: need to account for any changes brought on by collapsing
SF2 <- SF2 %>%
  select(-c(wgtGpRegion,wgtGpRegionDesc)) %>%
  left_join(SF2_wgts2_all %>% select(ORI,wgtGpRegion,wgtGpRegionDesc))

#Get totals by weighting group
srs_region_control_totals <- SF2 %>%
  group_by(REGION_NAME,wgtGpRegion) %>%
  dplyr::summarize(sum_totcrime_imp=sum(totcrime_imp,na.rm=TRUE),
                   sum_totcrime_murder_imp=sum(totcrime_murder_imp,na.rm=TRUE),
                   sum_totcrime_rape_imp=sum(totcrime_rape_imp,na.rm=TRUE),
                   sum_totcrime_aggAssault_imp=sum(totcrime_aggAssault_imp,na.rm=TRUE),
                   sum_totcrime_burglary_imp=sum(totcrime_burglary_imp,na.rm=TRUE),
                   sum_totcrime_rob_imp=sum(totcrime_rob_imp,na.rm=TRUE),
                   sum_totcrime_larceny_imp=sum(totcrime_larceny_imp,na.rm=TRUE),
                   sum_totcrime_vhcTheft_imp=sum(totcrime_vhcTheft_imp,na.rm=TRUE),
                   sum_totcrime_agg_rob_imp=sum(totcrime_agg_rob_imp,na.rm=TRUE),
                   #Note (08Jun2023): Also adding violent and property
                   sum_totcrime_violent_imp=sum(totcrime_violent_imp,na.rm=TRUE),
                   sum_totcrime_property_imp=sum(totcrime_property_imp,na.rm=TRUE),
                   .groups="drop")
SF2 <- SF2 %>%
  select(-matches("sum_totcrime")) %>%
  inner_join(srs_region_control_totals) %>%
  select(-matches("^(n|N|baseWgt|lowBound)$")) %>%
  full_join(ratio,by="REGION_NAME")

#07Jun2023: skipping weighting groups with crime cvg of >=99%
crime_ratio <- SF2 %>%
  group_by(REGION_NAME,wgtGpRegion) %>%
  dplyr::summarize(n=sum(resp_ind_m3==1),
                   N=n(),
                   sum_totcrime_imp_all=sum(totcrime_imp,na.rm=TRUE),
                   sum_totcrime_imp_NIBRS=sum(totcrime_imp*resp_ind_m3,na.rm=TRUE)) %>%
  mutate(ratio_totcrime_imp=sum_totcrime_imp_NIBRS/sum_totcrime_imp_all)
crossings_skips <- crime_ratio %>%
  subset(ratio_totcrime_imp>=0.99) %>%
  select(REGION_NAME,wgtGpRegion)

#03Jul2024: only assign a weight of 1 when it's a respondent
SF2_skips <- SF2 %>%
  inner_join(crossings_skips) %>%
  mutate(RegionWgt=ifelse(resp_ind_m3==1,1,NA_real_))

#ratio <- ratio %>%
#  anti_join(crossings_skips)

#05May2025: now drop the skipped weighting groups from SF2 and SF2_wgts2_all
SF2 <- SF2 %>%
  anti_join(crossings_skips)
SF2_wgts2_all <- SF2_wgts2_all %>%
  anti_join(crossings_skips)

#Get totals by weighting group
srs_region_control_totals <- SF2 %>%
  group_by(REGION_NAME,wgtGpRegion) %>%
  dplyr::summarize(sum_totcrime_imp=sum(totcrime_imp,na.rm=TRUE),
                   sum_totcrime_murder_imp=sum(totcrime_murder_imp,na.rm=TRUE),
                   sum_totcrime_rape_imp=sum(totcrime_rape_imp,na.rm=TRUE),
                   sum_totcrime_aggAssault_imp=sum(totcrime_aggAssault_imp,na.rm=TRUE),
                   sum_totcrime_burglary_imp=sum(totcrime_burglary_imp,na.rm=TRUE),
                   sum_totcrime_rob_imp=sum(totcrime_rob_imp,na.rm=TRUE),
                   sum_totcrime_larceny_imp=sum(totcrime_larceny_imp,na.rm=TRUE),
                   sum_totcrime_vhcTheft_imp=sum(totcrime_vhcTheft_imp,na.rm=TRUE),
                   sum_totcrime_agg_rob_imp=sum(totcrime_agg_rob_imp,na.rm=TRUE),
                   #Note (08Jun2023): Also adding violent and property
                   sum_totcrime_violent_imp=sum(totcrime_violent_imp,na.rm=TRUE),
                   sum_totcrime_property_imp=sum(totcrime_property_imp,na.rm=TRUE),
                   .groups="drop")

#####
#Combination summaries

#Update (28OCT2021): Previously was copy-pasting code chunks by number of variables in model. Create tfunction that will streamline
combs_table_region_gps <- function(indat,crimeVarsWgt,crimeVarsWgtAll,crimeVarsWgtRest,inWgtGps,wgtVar,wgtGpVar,wgtGpDescVar,suffix="",nInWgtGps=length(inWgtGps),nVars=length(crimeVarsWgtRest)){
  log_debug("Running function combs_table_region_gps")
  #04May2025: rather than create all possible region X weighting groups, 
  #             just use those that exist in indat
  inGps <- indat %>%
    select(REGION_NAME,wgtGpRegion) %>%
    unique() %>%
    arrange(REGION_NAME,str_rank(wgtGpRegion,numeric=TRUE))
  colnames(inGps) <- c("REGION_NAME",wgtGpVar)
  nInGps <- nrow(inGps)
  
  #04May2025: build a group # to description crosswalk
  gpCW <- indat %>%
    select(wgtGpRegion,wgtGpRegionDesc) %>%
    unique() %>%
    arrange(str_rank(wgtGpRegion,numeric=TRUE))
  
  #04May2025: changing final loop from 0 to still being nVars
  out <- sapply(nVars:nVars,function(temp.nVar){ 
    #Combinations of crimeVarsWgt of size i
    temp.combs <- combn(crimeVarsWgtRest,m=temp.nVar,simplify=FALSE)
    
    temp.dat <- matrix(ncol=nVars+length(crimeVarsWgtAll),
                       nrow=length(temp.combs)) %>%
      data.frame()
    colnames(temp.dat) <- crimeVarsWgt
    temp.dat <- temp.dat %>%
      mutate(nVar=temp.nVar+length(crimeVarsWgtAll),
             comb=1:length(temp.combs)) %>%
      select(nVar,comb,everything()) %>%
      mutate(across(crimeVarsWgtAll,~"X",.names="{.col}"))
    #Create table
    temp.table <- sapply(1:length(temp.combs),function(i){#Loop over each combination in temp.combs
      temp.out <- temp.dat[i,]
      temp.env <- environment()
      sapply(crimeVarsWgtRest,function(temp.var){
        temp.out <- temp.out %>%
          mutate(!! temp.var:=case_when(temp.var %in% temp.combs[[i]] ~ "X",
                                        TRUE ~ ""))
        list2env(list("temp.out"=temp.out),temp.env)
        return(NULL)
      })
      
      #Stack row once per region X weighting group
      
      #04May2025: use the gp crosswalk from earlier
      temp.out <- temp.out[rep(seq_len(nrow(temp.out)), each = nInGps), ]  %>%
        bind_cols(inGps) %>%
        left_join(gpCW)
      
      #Note (09Jan2023): Removing totcrime_imp requirement
      temp.converge <- indat %>%
        subset(resp_ind_m3==1) %>%
        mutate(converge=!is.na(eval(as.symbol(paste0(wgtVar,"_nVar",temp.nVar+length(crimeVarsWgtAll),"_comb",i))))) %>%
        select(REGION_NAME,all_of(wgtGpVar),all_of(wgtGpDescVar),converge) %>%
        group_by_at(.vars=c("REGION_NAME",wgtGpVar,wgtGpDescVar)) %>%
        dplyr::summarize(converge=any(converge),
                         .groups="drop") %>%
        select(REGION_NAME,all_of(wgtGpVar),all_of(wgtGpDescVar),converge)
      
      temp.out <- temp.out %>% 
        left_join(temp.converge,by=c("REGION_NAME",wgtGpVar,wgtGpDescVar)) %>%
        left_join(crime_ratio %>% select(REGION_NAME,wgtGpVar,N,n,sum_totcrime_imp_all,sum_totcrime_imp_NIBRS))
    },simplify=FALSE) %>%
      bind_rows()
    return(temp.table)
  },simplify=FALSE)
  
  #04May2025: changing final value in range from 0 to nVars
  names(out) <- paste0("comb",(nVars:nVars)+length(crimeVarsWgtAll),"_table_",suffix)
  list2env(out,envir=.GlobalEnv)
  
  
  #Repeat for single SRS variable model
  #04May2025: no longer using
  # temp.dat <- matrix(ncol=nVars+length(crimeVarsWgtAll),
  #                    nrow=1) %>%
  #   data.frame()
  # colnames(temp.dat) <- crimeVarsWgt
  # temp.dat <- temp.dat %>%
  #   mutate(nVar=1,
  #          comb=1) %>%
  #   select(nVar,comb,everything()) %>%
  #   mutate(across(crimeVarsWgtAll[1],~"X",.names="{.col}"),
  #          across(crimeVarsWgtAll[2:length(crimeVarsWgtAll)],~"",.names="{.col}"),
  #          across(crimeVarsWgtRest,~"",.names="{.col}"))
  # #Create table
  # temp.out <- temp.dat[1,]
  # temp.env <- environment()
  # 
  # #Stack row once per judicial district X weighting group
  # 
  # temp.out <- temp.out[rep(seq_len(nrow(temp.out)), each = nInGps), ]  %>%
  #   bind_cols(inGps) %>%
  #   mutate(!!wgtGpDescVar:=factor(eval(as.symbol(wgtGpVar)),levels=wgtGpsRegion2,labels=wgtGpRegionDescs2))
  # print(temp.out)
  # #Note (09Jan2023): Removing totcrime_imp requirement
  # temp.converge <- indat %>%
  #   subset(resp_ind_m3==1) %>%
  #   mutate(converge=!is.na(eval(as.symbol(paste0(wgtVar,"_nVar",1,"_comb",1))))) %>%
  #   select(REGION_NAME,all_of(wgtGpVar),all_of(wgtGpDescVar),converge) %>%
  #   group_by_at(.vars=c("REGION_NAME",wgtGpVar,wgtGpDescVar)) %>%
  #   dplyr::summarize(converge=any(converge),
  #                    .groups="drop") %>%
  #   select(REGION_NAME,all_of(wgtGpVar),all_of(wgtGpDescVar),converge)
  # 
  # out <- temp.out %>% 
  #   left_join(temp.converge,
  #             by=c("REGION_NAME",wgtGpVar,wgtGpDescVar)) %>%
  #   left_join(crime_ratio %>% select(REGION_NAME,wgtGpVar,N,n,sum_totcrime_imp_all,sum_totcrime_imp_NIBRS)) %>%
  #   list()
  # colnames(out) %>% print()
  # names(out) <- paste0("comb",1,"_table_",suffix)
  # list2env(out,envir=.GlobalEnv)
  
  return(NULL)
}

#Do 1st group
#Set weight variables
if (as.numeric(year)<2023){
  crimeVarsWgtRest <- c("totcrime_murder_imp","totcrime_rape_imp",
                        "totcrime_agg_rob_imp","totcrime_burglary_imp",
                        "totcrime_larceny_imp","totcrime_vhcTheft_imp")
} else {
  crimeVarsWgtRest <- c("totcrime_murder_imp","totcrime_rape_imp",
                        "totcrime_aggAssault_imp","totcrime_burglary_imp",
                        "totcrime_rob_imp","totcrime_larceny_imp",  
                        "totcrime_vhcTheft_imp")
}
crimeVarsWgt <- c(crimeVarsWgtAll,crimeVarsWgtRest)

#Update (28OCT2021): Using function from above to streamline combination summaries
combs_table_region_gps(indat=SF2_wgts2_all %>% subset(wgtGpRegion=="1"),crimeVarsWgt,crimeVarsWgtAll,crimeVarsWgtRest,
                       inWgtGps=wgtGps2[1],
                       wgtVar="RegionWgt",wgtGpVar="wgtGpRegion",wgtGpDescVar="wgtGpRegionDesc",
                       suffix="firstGp")

#Now repeat for remaining groups
crimeVarsWgtRest <- c("totcrime_murder_imp","totcrime_rape_imp",
                      "totcrime_aggAssault_imp","totcrime_burglary_imp",
                      "totcrime_rob_imp","totcrime_larceny_imp",  
                      "totcrime_vhcTheft_imp")
crimeVarsWgt <- c(crimeVarsWgtAll,crimeVarsWgtRest)

combs_table_region_gps(indat=SF2_wgts2_all %>% subset(wgtGpRegion != "1"),crimeVarsWgt,crimeVarsWgtAll,crimeVarsWgtRest,
                       inWgtGps=wgtGps2[-1],
                       wgtVar="RegionWgt",wgtGpVar="wgtGpRegion",wgtGpDescVar="wgtGpRegionDesc",
                       suffix="rest")


#Update (08Jun2023): Some groups don't have a model that converges - for now, create row representing 0 variables (N/n)
comb0_table_firstGp <- SF2_wgts2_all %>% 
  subset(wgtGpRegion=="1") %>%
  select(REGION_NAME,wgtGpRegion,wgtGpRegionDesc) %>% 
  unique() %>%
  left_join(crime_ratio %>% select(REGION_NAME,wgtGpRegion,N,n,sum_totcrime_imp_all,sum_totcrime_imp_NIBRS)) %>%
  mutate(nVar=0,
         comb=1,
         converge=TRUE)
#Note (08May2023): Since RegionWgt_nVarX_combY is g-weight, need to divide by baseWgt
SF2_wgts2_firstGp <- SF2_wgts2_all %>%
  subset(wgtGpRegion == "1") %>%
  mutate(RegionWgt_nVar0_comb1=ifelse(resp_ind_m3==1 & rowSums(!is.na(select(.,matches("RegionWgt_nVar\\d"))),na.rm=TRUE)==0,
                                      1/(ratio_totcrime_imp*baseWgt),
                                      NA_real_))

comb0_table_rest <- SF2_wgts2_all %>% 
  subset(wgtGpRegion != "1") %>%
  select(REGION_NAME,wgtGpRegion,wgtGpRegionDesc) %>% 
  unique() %>%
  left_join(crime_ratio %>% select(REGION_NAME,wgtGpRegion,N,n,sum_totcrime_imp_all,sum_totcrime_imp_NIBRS)) %>%
  mutate(nVar=0,
         comb=1,
         converge=TRUE)
#Note (08May2023): Since RegionWgt_nVarX_combY is g-weight, need to divide by baseWgt
SF2_wgts2_rest <- SF2_wgts2_all %>%
  subset(wgtGpRegion != "1") %>%
  mutate(RegionWgt_nVar0_comb1=ifelse(resp_ind_m3==1 & rowSums(!is.na(select(.,matches("RegionWgt_nVar\\d"))),na.rm=TRUE)==0,
                                      1/(ratio_totcrime_imp*baseWgt),
                                      NA_real_))

#Stack all tables together
#30May2024: realizing I didn't add the 10-variable combination for the 1st weighting group
#04May2025: only need the full versions at this point
if (as.numeric(year)<2023){
  combAll_table <- bind_rows(comb9_table_firstGp,
                             # comb8_table_firstGp,
                             # comb7_table_firstGp,
                             # comb6_table_firstGp,
                             # comb5_table_firstGp,
                             # comb4_table_firstGp,
                             # comb3_table_firstGp,
                             # comb1_table_firstGp,
                             # comb0_table_firstGp,
                             comb10_table_rest#,
                             # comb9_table_rest,
                             # comb8_table_rest,
                             # comb7_table_rest,
                             # comb6_table_rest,
                             # comb5_table_rest,
                             # comb4_table_rest,
                             # comb3_table_rest,
                             # comb1_table_rest,
                             # comb0_table_rest
  ) 
} else {
  combAll_table <- bind_rows(comb10_table_firstGp,
                             # comb9_table_firstGp,
                             # comb8_table_firstGp,
                             # comb7_table_firstGp,
                             # comb6_table_firstGp,
                             # comb5_table_firstGp,
                             # comb4_table_firstGp,
                             # comb3_table_firstGp,
                             # comb1_table_firstGp,
                             # comb0_table_firstGp,
                             comb10_table_rest#,
                             # comb9_table_rest,
                             # comb8_table_rest,
                             # comb7_table_rest,
                             # comb6_table_rest,
                             # comb5_table_rest,
                             # comb4_table_rest,
                             # comb3_table_rest,
                             # comb1_table_rest,
                             # comb0_table_rest
  ) 
}
combAll_table <- combAll_table %>%
  arrange(REGION_NAME,str_rank(wgtGpRegion,numeric=TRUE),wgtGpRegionDesc,-converge,-nVar,comb) %>%
  group_by(REGION_NAME,wgtGpRegion,wgtGpRegionDesc) %>%
  mutate(Select=ifelse(row_number(wgtGpRegion)==1 & converge==TRUE,"X","")) %>%
  ungroup() %>%
  arrange(REGION_NAME,str_rank(wgtGpRegion,numeric=TRUE),wgtGpRegionDesc,-nVar,comb) %>%
  mutate(Variables=ifelse(
    as.numeric(year)<2023,
    apply(.,FUN=function(i){
      c(ifelse(i["totcrime_imp"]=="X","totcrime_imp",""),
        ifelse(i["totcrime_violent_imp"]=="X","totcrime_violent_imp",""),
        ifelse(i["totcrime_property_imp"]=="X","totcrime_property_imp",""),
        ifelse(i["totcrime_murder_imp"]=="X","totcrime_murder_imp",""),
        ifelse(i["totcrime_rape_imp"]=="X","totcrime_rape_imp",""),
        ifelse(i["totcrime_aggAssault_imp"]=="X","totcrime_aggAssault_imp",""),
        ifelse(i["totcrime_burglary_imp"]=="X","totcrime_burglary_imp",""),
        ifelse(i["totcrime_rob_imp"]=="X","totcrime_rob_imp",""),
        ifelse(i["totcrime_larceny_imp"]=="X","totcrime_larceny_imp",""),
        ifelse(i["totcrime_vhcTheft_imp"]=="X","totcrime_vhcTheft_imp",""),
        ifelse(i["totcrime_agg_rob_imp"]=="X","totcrime_agg_rob_imp","")
      ) %>%
        subset(.!="") %>%
        str_flatten(collapse=",")},MARGIN=1),
    apply(.,FUN=function(i){
      c(ifelse(i["totcrime_imp"]=="X","totcrime_imp",""),
        ifelse(i["totcrime_violent_imp"]=="X","totcrime_violent_imp",""),
        ifelse(i["totcrime_property_imp"]=="X","totcrime_property_imp",""),
        ifelse(i["totcrime_murder_imp"]=="X","totcrime_murder_imp",""),
        ifelse(i["totcrime_rape_imp"]=="X","totcrime_rape_imp",""),
        ifelse(i["totcrime_aggAssault_imp"]=="X","totcrime_aggAssault_imp",""),
        ifelse(i["totcrime_burglary_imp"]=="X","totcrime_burglary_imp",""),
        ifelse(i["totcrime_rob_imp"]=="X","totcrime_rob_imp",""),
        ifelse(i["totcrime_larceny_imp"]=="X","totcrime_larceny_imp",""),
        ifelse(i["totcrime_vhcTheft_imp"]=="X","totcrime_vhcTheft_imp","")#,
        #ifelse(i["totcrime_agg_rob_imp"]=="X","totcrime_agg_rob_imp","")
      ) %>%
        subset(.!="") %>%
        str_flatten(collapse=",")},MARGIN=1))) %>%
  select(REGION_NAME,wgtGpRegion,wgtGpRegionDesc,nVar,comb,
         totcrime_imp,totcrime_violent_imp,
         totcrime_property_imp,totcrime_murder_imp,
         totcrime_rape_imp,matches("^totcrime_agg_rob_imp$"),
         totcrime_aggAssault_imp,
         totcrime_burglary_imp,totcrime_rob_imp,
         totcrime_larceny_imp,totcrime_vhcTheft_imp,
         Variables,everything())

#Update (14Jun2022): Switching Excel output functions (fixing overwrite bug)
#combAll_table %>%
#  list("All Combinations"=.) %>%
#  write.xlsx(file=paste0(output_weighting_data_folder,"SRS_Variable_Combination_Convergence_by_Region_X_Weighting_Group_Automatic.xlsx"))
log_debug("Writing excel workbook SRS_Variable_Combination_Convergence_by_Region_X_Weighting_Group_AltCombs_Automatic.xlsx")
workbook <- paste0(output_weighting_data_folder,
                   "SRS_Variable_Combination_Convergence_by_Region_X_Weighting_Group_AltCombs_Automatic.xlsx")
wb <- createWorkbook()
addWorksheet(wb,"All Combinations")
writeData(wb,"All Combinations",combAll_table)
saveWorkbook(wb,workbook,overwrite=TRUE) 

#04May2025: since a single weighting group could have multiple groups in it,
#             just use the 1st weighting group if multiple exist 
SF2 <- SF2 %>%
  arrange(ORI) %>%
  mutate(wgtGpRegion2=str_extract(wgtGpRegion,"^\\d+(?=;|$)") %>%
           as.numeric() %>%
           `+`(20*(REGION_CODE)))

#choosing best model that converges
ctrlVars <- combAll_table %>% subset(Select=="X")

#04May2025: using srs_region_control_totals in if() instead of SF2
if (nrow(ctrlVars)==srs_region_control_totals %>% select(REGION_NAME,wgtGpRegion) %>% subset(duplicated(.)==FALSE) %>% nrow()){
  
  #capture.output({
  SF2_wgts2 <- sapply(regionGps2[1:length(regionGps2)],function(i){#Loop over weight groupings - just gp 1 for test
    print("##############################")
    print(paste0("Region: ",i))
    SF_region <- SF2 %>%
      subset(REGION_NAME==i) #%>%
    #select(-matches("V\\d+_\\w"))
    #Note (10Jan2023): Removing totcrime_imp requirement
    SF_temp_region <- SF_region %>%
      subset(resp_ind_m3==1)
    temp_region_code <- SF2 %>% subset(REGION_NAME==i) %>% getElement("REGION_CODE") %>% unique()
    #choosing best model that converges
    ctrlInds_region <- combAll_table %>% 
      subset(Select=="X" & REGION_NAME==i) %>% 
      rename_at(.vars=vars(matches("^totcrime")),.funs=~paste0(.x,"_ind")) %>%
      #04May2025: again, just use the 1st weighting group if multiple are listed
      mutate(wgtGpRegion2=str_extract(wgtGpRegion,"^\\d+(?=;|$)") %>%
               as.numeric() %>%
               `+`(20*(temp_region_code))) %>%
      select(wgtGpRegion2,matches("_ind")) %>%
      mutate(across(matches("_ind"),~ifelse(.x!="X",0,1))) %>%
      mutate(across(matches("_ind"),~ifelse(is.na(.x),0,.x))) %>%
      arrange(wgtGpRegion2) %>%
      mutate(totcrime_agg_rob_imp_ind=0) %>% #Creating dummy variable to retain same names as national & region
      select(wgtGpRegion2,
             totcrime_imp_ind,totcrime_murder_imp_ind,
             totcrime_rape_imp_ind,matches("^totcrime_agg_rob_imp_ind$"),
             totcrime_aggAssault_imp_ind,totcrime_burglary_imp_ind,
             totcrime_rob_imp_ind,totcrime_larceny_imp_ind,
             totcrime_vhcTheft_imp_ind)
    
    
    ctrlIndsM_region <- ctrlInds_region %>%
      select(colnames(ctrlInds_region)) %>%
      select(-wgtGpRegion2) %>%
      as.matrix()
    
    ctrlTtlsM_region <- srs_region_control_totals %>%
      subset(REGION_NAME==i) %>%
      #04May2025: again, just use the 1st weighting group if multiple are listed
      mutate(wgtGpRegion2=str_extract(wgtGpRegion,"^\\d+(?=;|$)") %>%
               as.numeric() %>%
               `+`(20*(temp_region_code))) %>%
      arrange(str_rank(wgtGpRegion,numeric=TRUE)) %>%
      select(sum_totcrime_imp,sum_totcrime_murder_imp,
             sum_totcrime_rape_imp,matches("^sum_totcrime_agg_rob_imp$"),
             sum_totcrime_aggAssault_imp,sum_totcrime_burglary_imp,
             sum_totcrime_rob_imp,sum_totcrime_larceny_imp,
             sum_totcrime_vhcTheft_imp) %>%
      as.matrix()
    
    ctrlTtlsM2_region <- ctrlTtlsM_region*ctrlIndsM_region #Element-wise multiplication
    colnames(ctrlTtlsM2_region) <- LETTERS[1:ncol(ctrlTtlsM2_region)] #Would normally include 'sum_' before, but will add that later
    
    ctrlTtls2_region <- ctrlTtlsM2_region %>%
      data.frame() %>%
      mutate(wgtGpRegion2=ctrlInds_region %>% getElement("wgtGpRegion2")) %>%
      reshape2::melt(id.vars="wgtGpRegion2") %>%
      reshape2::dcast(formula=.~wgtGpRegion2+variable) %>%
      select(-.) #Drop dummy variable
    colnames(ctrlTtls2_region) <- paste0("sum_V",colnames(ctrlTtls2_region))
    #print("colnames(ctrlTtls2_region):")
    #print(colnames(ctrlTtls2_region))
    
    colnames(ctrlTtls2_region) <- colnames(ctrlTtls2_region) %>% str_replace("^(\\w)$","sum_\\1")
    
    #Control variables
    #Note (10Jan2023): Removing totcrime_imp requirement
    ctrlIndsM_region <- ctrlInds_region %>%
      inner_join(SF_region) %>%
      subset(REGION_NAME==i & resp_ind_m3==1) %>%
      arrange(ORI) %>%
      select(colnames(ctrlInds_region)) %>%
      select(-wgtGpRegion2) %>%
      as.matrix()
    #Note (10Jan2023): Removing totcrime_imp requirement
    ctrlVarsM_region <- SF2%>%
      subset(REGION_NAME==i & resp_ind_m3==1) %>%
      arrange(ORI) %>%
      select(totcrime_imp,totcrime_murder_imp,
             totcrime_rape_imp,matches("^totcrime_agg_rob_imp$"),
             totcrime_aggAssault_imp,totcrime_burglary_imp,
             totcrime_rob_imp,totcrime_larceny_imp,
             totcrime_vhcTheft_imp) %>%
      as.matrix()
    
    ctrlVarsM2_region <- ctrlVarsM_region*ctrlIndsM_region
    colnames(ctrlVarsM2_region) <- LETTERS[1:ncol(ctrlVarsM2_region)]
    
    #print("ctrVars2_region")
    ctrlVars2_region <- ctrlVarsM2_region %>%
      data.frame() %>%
      #Note (10Jan2023): Removing totcrime_imp requirement
      mutate(ORI=SF_region %>% arrange(ORI) %>% subset(REGION_NAME==i & resp_ind_m3==1) %>% getElement("ORI"),
             wgtGpRegion2=SF_region %>% arrange(ORI) %>% subset(REGION_NAME==i & resp_ind_m3==1) %>% getElement("wgtGpRegion2")) %>%
      mutate(across(matches("^\\w{1}$"),
                    .fns=~.x*ifelse(wgtGpRegion2==1+20*temp_region_code,1,0),
                    .names=paste0("V",1+20*temp_region_code,"_{col}")),
             across(matches("^\\w{1}$"),
                    .fns=~.x*ifelse(wgtGpRegion2==4+20*temp_region_code,1,0),
                    .names=paste0("V",4+20*temp_region_code,"_{col}")),
             across(matches("^\\w{1}$"),
                    .fns=~.x*ifelse(wgtGpRegion2==5+20*temp_region_code,1,0),
                    .names=paste0("V",5+20*temp_region_code,"_{col}")),
             across(matches("^\\w{1}$"),
                    .fns=~.x*ifelse(wgtGpRegion2==6+20*temp_region_code,1,0),
                    .names=paste0("V",6+20*temp_region_code,"_{col}")),
             across(matches("^\\w{1}$"),
                    .fns=~.x*ifelse(wgtGpRegion2==7+20*temp_region_code,1,0),
                    .names=paste0("V",7+20*temp_region_code,"_{col}")),
             across(matches("^\\w{1}$"),
                    .fns=~.x*ifelse(wgtGpRegion2==8+20*temp_region_code,1,0),
                    .names=paste0("V",8+20*temp_region_code,"_{col}")),
             across(matches("^\\w{1}$"),
                    .fns=~.x*ifelse(wgtGpRegion2==9+20*temp_region_code,1,0),
                    .names=paste0("V",9+20*temp_region_code,"_{col}")),
             across(matches("^\\w{1}$"),
                    .fns=~.x*ifelse(wgtGpRegion2==10+20*temp_region_code,1,0),
                    .names=paste0("V",10+20*temp_region_code,"_{col}")),
             across(matches("^\\w{1}$"),
                    .fns=~.x*ifelse(wgtGpRegion2==11+20*temp_region_code,1,0),
                    .names=paste0("V",11+20*temp_region_code,"_{col}")),
             across(matches("^\\w{1}$"),
                    .fns=~.x*ifelse(wgtGpRegion2==14+20*temp_region_code,1,0),
                    .names=paste0("V",14+20*temp_region_code,"_{col}")),
             across(matches("^\\w{1}$"),
                    .fns=~.x*ifelse(wgtGpRegion2==15+20*temp_region_code,1,0),
                    .names=paste0("V",15+20*temp_region_code,"_{col}")),
             across(matches("^\\w{1}$"),
                    .fns=~.x*ifelse(wgtGpRegion2==16+20*temp_region_code,1,0),
                    .names=paste0("V",16+20*temp_region_code,"_{col}")),
             across(matches("^\\w{1}$"),
                    .fns=~.x*ifelse(wgtGpRegion2==18+20*temp_region_code,1,0),
                    .names=paste0("V",18+20*temp_region_code,"_{col}")),
             across(matches("^\\w{1}$"),
                    .fns=~.x*ifelse(wgtGpRegion2==19+20*temp_region_code,1,0),
                    .names=paste0("V",19+20*temp_region_code,"_{col}")),
             across(matches("^\\w{1}$"),
                    .fns=~.x*ifelse(wgtGpRegion2==20+20*temp_region_code,1,0),
                    .names=paste0("V",20+20*temp_region_code,"_{col}")))
    
    
    #Add on the new control totals/variables
    SF_region <- SF_region %>%
      full_join(ctrlVars2_region) %>%
      #select(-matches("^sum_\\w+_imp$")) %>%
      #full_join(ctrlTtls2) %>%
      arrange(ORI)
    #Note (10Jan2023): Removing totcrime_imp requirement
    SF_temp <- SF_region %>%
      subset(resp_ind_m3==1)
    
    
    #21Mar2023: adding requirement that columns are in ctrlTtls2_region
    temp.ctrlVars <- colnames(ctrlVars2_region) %>% 
      str_subset("^V\\d+_\\w$") %>% 
      subset(. %in% (colnames(ctrlTtls2_region) %>% str_remove("sum_")))
    #Update (28OCT2021): Comment out print statement
    #print(temp.ctrlVars)
    #05May2025: create set of control variables just for calibration check - 
    #             these will use same variables in the original calibration
    #Always drop the agg assault + robbery derived variable for all but 1st gp
    temp.ctrlVars2 <- temp.ctrlVars %>%
      str_subset(str_c("(",
                       str_c("V",20*temp_region_code+2:20,"_","D") %>%
                         str_flatten(collapse="|"),
                       ")"),
                 negate=TRUE)
    if (as.numeric(year)>=2023 | !("1" %in% SF_temp$wgtGpRegion)){
      temp.ctrlVars2 <- temp.ctrlVars2 %>% 
        #Drop agg assault + robbery derived variables for even the 1st group
        str_subset("V\\d+_D",negate=TRUE)
    } else {
      temp.ctrlVars2 <- temp.ctrlVars2 %>% 
        #Drop the individual agg assault and robbbery variables for 1st group
        str_subset(str_c("(",
                         str_c("V",20*temp_region_code+1,"_",c("E","G")) %>%
                           str_flatten(collapse="|"),
                         ")"),
                   negate=TRUE)
    }
    #05May2025: use this new set of control variables for the control totals
    total_temp <- ctrlTtls2_region %>%
      select(all_of(paste0("sum_",temp.ctrlVars2))) %>%
      as.numeric()
    #names(total_temp) <- NULL
    
    #05May2025: below not actually used for anything - commenting out
    #vars_temp <- SF_temp %>%
    #  select(all_of(temp.ctrlVars)) 
    
    ratio_region <- ratio %>% subset(REGION_NAME==i)
    #names(vars_temp) <- NULL
    #Update (10Oct2022): Don't redo calibration, juse use weights from earlier
    #print("gencalib(Xs=select(SF_temp,all_of(temp.ctrlVars)), ...:")
    # SF_temp_wgts2 <- gencalib(Xs=vars_temp,
    #                       Zs=vars_temp,
    #                       #d=rep(1,nrow(SF_temp)),
    #                       d=rep(ratio_region$baseWgt,nrow(SF_temp)),
    #                       total=total_temp,
    #                       method="logit",
    #                       #bounds=c(low=1,1e6),
    #                       bounds=c(low=ratio_region$lowBound,maxWgt/ratio_region$baseWgt),#1e6),
    #                       max_iter=5*maxIt,#10000
    #                       C=1,
    #                       description=TRUE) %>%
    #   data.frame(gWgt=.) %>%
    #   mutate(RegionWgt=gWgt*ratio_region$baseWgt) %>%
    #   {bind_cols(SF_temp,.)} %>%
    #   full_join(SF_region,by=colnames(SF_region))
    #Note (10Jan2023): Removing totcrime_imp requirement
    SF_temp_wgts2 <- SF2_wgts2_firstGp %>%
      bind_rows(SF2_wgts2_rest) %>%
      subset(resp_ind_m3==1 & REGION_NAME==i) %>%
      mutate(gWgt=select(.,matches("RegionWgt_nVar\\d")) %>% rowMeans(na.rm=TRUE)) %>%
      mutate(RegionWgt=gWgt*baseWgt) %>%
      select(ORI,gWgt,RegionWgt) %>%
      right_join(SF_temp)
    
    print("Check calibration on full model")
    #05May2025: use the new set of control variables
    checkcalibration(Xs=select(SF_temp_wgts2,all_of(temp.ctrlVars2)) %>% as.matrix(),
                     d=rep(ratio_region$baseWgt,nrow(SF_temp_wgts2)),
                     total=total_temp,
                     g=SF_temp_wgts2$gWgt,
                     EPS=ifelse(any(total_temp==0),1,1e-6)) %>% #EPS=1) %>%
      print()
    temp.wgtGpsRegion <- SF_region %>% pull(wgtGpRegion) %>% unique() %>% str_sort(numeric=TRUE)
    
    SF2_wgts_region <- sapply(temp.wgtGpsRegion,function(j){#Loop over weight groupings
      print("##############")
      print(paste0("Region: ",i,". Weight group: ",j))
      #Take weighting group subset within regional subset
      #Note (10Jan2023): Removing totcrime_imp requirement
      SF_temp <- SF_temp_wgts2 %>%
        subset(wgtGpRegion==j & resp_ind_m3==1)
      if (nrow(SF_temp)>0){
        #04May2025: again, if multiple weighting groups included, just use 1st
        #05May2025: simply subset the new control variables to get vars for gp
        temp.ctrlVars3 <- temp.ctrlVars2 %>%
          str_subset(paste0("^V",
                            j%>%
                              str_extract("^\\d+(?=;|$)") %>%
                              as.numeric() %>%
                              `+`(20*(temp_region_code)),
                            "_\\w$"))
        
        #05May2025: use the new control variables for gp
        total_temp_region <- ctrlTtls2_region %>%
          select(all_of(paste0("sum_",temp.ctrlVars3))) %>%
          as.numeric()
        print(total_temp_region)
        out_temp <- SF_temp
        
        #Update (20AUG2021): Adding requested checks
        #Update (05Jul2022): Switch to table format (1 row per weight group) - commenting out old cold
        #Update (16May2024): added min and max to checks
        #Update (14May2025): added check for weights <0.9
        
        # #Check calibration
        # print("checkcalibration(Xs=select(SF_temp,all_of(temp.ctrlVars)), ...:")
        # checkcalibration(Xs=select(SF_temp,all_of(temp.ctrlVars)),
        #                  d=rep(1,nrow(SF_temp)),
        #                  total=total_temp,
        #                  g=out_temp$RegionWgt,
        #                  EPS=1) %>%
        #   print()
        # #Weight checks - summary, UWE, etc.
        # print("Distribution of weights:")
        # describe(out_temp$RegionWgt) %>%
        #   print()
        # print("Number of missing weights:")
        # sum(is.na(out_temp$RegionWgt))%>%
        #   print()
        # print("Number of weights equal to 1:")
        # sum(out_temp$RegionWgt == 1, na.rm=TRUE) %>%
        #   print()
        # print("Number of weights greater than 1:")
        # sum(out_temp$RegionWgt > 1, na.rm=TRUE) %>%
        #   print()
        # print("Number of weights less than 1:")
        # sum(out_temp$RegionWgt < 1, na.rm=TRUE) %>%
        #   print()
        # print("Number of weights greater than 100:")
        # sum(out_temp$RegionWgt > 100, na.rm=TRUE) %>%
        #   print()
        # print("UWE:")
        # UWE_RegionWgt <- 1+var(out_temp$RegionWgt,na.rm=TRUE)/(mean(out_temp$RegionWgt,na.rm=TRUE)^2)
        # UWE_RegionWgt %>%
        #   print()
        
        #Calibration worked (T/F)?
        #05May2025: use new control vars for group
        temp.cal <- checkcalibration(Xs=select(SF_temp,all_of(temp.ctrlVars3)) %>% as.matrix(),
                                     d=rep(ratio_region$baseWgt,nrow(SF_temp)),
                                     total=total_temp_region,
                                     g=out_temp$gWgt,
                                     EPS=ifelse(any(total_temp_region==0),1,1e-6))%>%#EPS=1) %>%
          .$result
        temp.describe <- describe(out_temp$RegionWgt)
        temp.quantiles <- quantile(out_temp$RegionWgt,
                                   probs=c(0,0.05,0.1,0.25,0.5,0.75,0.9,0.95,1),
                                   na.rm=TRUE)
        #Note (26Jul2022): Adding n Eligible LEAs
        temp.nElig <- SF2 %>%
          subset(REGION_NAME==i & wgtGpRegion==j) %>%
          nrow()
        #Note (16May2024): rounding weight to 6 digits before checking if <1 (to avoid false flags)
        temp.nLT1 <- sum(round(out_temp$RegionWgt,digits=6) < 1 & out_temp$RegionWgt>0, na.rm=TRUE)
        temp.nLT0pt9 <- sum(round(out_temp$RegionWgt,digits=6) < 0.9 & out_temp$RegionWgt>0, na.rm=TRUE)
        #Note (29Jul2022): Switching from >100 to >20
        #temp.nGT100 <- sum(out_temp$RegionWgt > 100, na.rm=TRUE)
        temp.nGT20 <- sum(out_temp$RegionWgt > 20, na.rm=TRUE)
        temp.UWE <- 1+var(out_temp$RegionWgt,na.rm=TRUE)/(mean(out_temp$RegionWgt,na.rm=TRUE)^2)
        #04May2025: merge on the wgtGpRegionDesc for this region
        temp.out <- data.frame(regionGp=i,
                               wgtGpRegion=j) %>% 
          left_join(SF2 %>% select(wgtGpRegion,wgtGpRegionDesc) %>% unique()) %>%
          select(-wgtGpRegion) %>%
          mutate(calibrated=temp.cal,
                 #Note (26Jul2022): Changing counts - include n Eligible LEAs, n NIBRS LEAs, n NIBRS LEAs missing weights
                 #nOverall=as.numeric(temp.describe$counts["n"])+as.numeric(temp.describe$counts["missing"]),
                 nElig=temp.nElig,
                 nNIBRS=as.numeric(temp.describe$counts["n"])+as.numeric(temp.describe$counts["missing"]),
                 nMissing=as.numeric(temp.describe$counts["missing"]),
                 nLT1=temp.nLT1,
                 nLT0pt9=temp.nLT0pt9,
                 #nGT100=temp.nGT100,
                 nGT20=temp.nGT20,
                 UWE=sprintf(temp.UWE,fmt="%1.3f"),
                 Mean=sprintf(as.numeric(temp.describe$counts["Mean"]),fmt="%1.3f"),
                 Min=sprintf(temp.quantiles["0%"],fmt="%1.3f"),
                 pt05=sprintf(temp.quantiles["5%"],fmt="%1.3f"),
                 pt10=sprintf(temp.quantiles["10%"],fmt="%1.3f"),
                 pt25=sprintf(temp.quantiles["25%"],fmt="%1.3f"),
                 pt50=sprintf(temp.quantiles["50%"],fmt="%1.3f"),
                 pt75=sprintf(temp.quantiles["75%"],fmt="%1.3f"),
                 pt90=sprintf(temp.quantiles["90%"],fmt="%1.3f"),
                 pt95=sprintf(temp.quantiles["95%"],fmt="%1.3f"),
                 Max=sprintf(temp.quantiles["100%"],fmt="%1.3f"))
        colnames(temp.out) <- c("Region","Weight Group","Calibrated",
                                "n Eligible LEAs","n NIBRS LEAs, Overall","n NIBRS LEAs, Missing Weight",
                                "n LT 1","n LT 0.9","n GT 20","UWE",#"n GT 100","UWE",
                                "Mean","Minimum","5th Pctl","10th Pctl","25th Pctl","50th Pctl",
                                "75th Pctl","90th Pctl","95th Pctl","Maximum")
        temp.out <- temp.out %>%
          list()
        #04May2025: again, if multiple weighting groups included, just use 1st
        names(temp.out) <- paste0("results_",
                                  i,
                                  "_",
                                  j %>% 
                                    str_extract("^\\d+(?=;|$)") %>%
                                    as.numeric())
        list2env(temp.out,.GlobalEnv)
        return(out_temp)
      } else {
        return(NULL)
      }
      
    },simplify=FALSE) %>%
      bind_rows()
    
    
  },simplify=FALSE) %>%
    bind_rows()%>%
    #01May2024: issues during merge... reducing number of variables to only ID variables plus new variables (gWgt, RegionWgt, and calibration variables
    select(ORI,gWgt,RegionWgt,matches("V\\d+_\\w")) %>%
    #full_join(SF2,by=colnames(SF2))
    full_join(SF2,by=c("ORI"))
  #},file=paste0(output_weighting_data_folder,'weights_region_checks.txt'))
  #Note (JDB 06Jul2022): Combine weight check results
  #Note (JDB 08Jun2023): Only pull results for crossings that exist
  # results_region <- outer(paste0("results_",regionGps2,"_"),wgtGpsRegion,FUN=paste0) %>%
  #   as.character() %>%
  #   mget(envir=.GlobalEnv) %>%
  #   bind_rows()
  results_region <-SF2 %>% 
    select(REGION_NAME,wgtGpRegion) %>% 
    unique() %>% 
    #14May2025: sort by region, then weight group
    arrange(REGION_NAME,str_rank(wgtGpRegion,numeric=TRUE)) %>%
    #04May2025: again, if multiple weighting groups included, just use 1st
    mutate(name=paste0("results_",
                       REGION_NAME,
                       "_",
                       wgtGpRegion %>%
                         str_extract("^\\d+(?=;|$)"))) %>% 
    pull(name) %>%
    mget(envir=.GlobalEnv) %>%
    bind_rows()
  
  
  
  ###############
  #Output
  #03Jul2024: adding back in the skipped weighting groups
  new_weights <- SF2_wgts2 %>%
    bind_rows(SF2_skips)
  
  ### export for others to start writing functions to analyze bias, MSE, etc.
  new_weights[,c("ORI_universe","LEGACY_ORI","wgtGpRegion","wgtGpRegionDesc","REGION_NAME",
                 #Update (27AUG2021): Add raw weight group variable
                 "wgtGpRegion_raw","wgtGpRegionDesc_raw",
                 "RegionWgt")] %>%
    #write.csv(paste0(output_weighting_data_folder,'weights_region.csv'),
    fwrite_wrapper(paste0(output_weighting_data_folder,'weights_region.csv'))
  
  #Update (26AUG2021): Add wgtGpRegion and wgtGpRegionDesc to SF file from 02_Weights_Data_Setup
  # oldSF <- read_csv(paste0(input_weighting_data_folder,"SF_postN.csv"),
  #                   guess_max=1e6)%>%
  #   #Adding just in case already on file...
  #   select(-matches("wgtGpRegion"))
  calVars <- colnames(SF2_wgts2) %>%
    str_subset("^V\\d+_\\w") %>% #All calibration vars
    str_subset("^V(\\d|1\\d|20)_\\w$",negate=TRUE) #Remove national calibration vars
  calVarsRegEx <- str_flatten(calVars,collapse="|")
  #02May2024: no longer drop variables from old SF
  oldSF <- fread(paste0(input_weighting_data_folder,"SF_postN.csv"))#%>%
  #Adding just in case already on file...
  #select(-matches(paste0("(wgtGpRegion|",calVars,")")))
  #19Jun2023: binding SF2 and SF2_skips in 1st left_join
  newSF <- oldSF %>%
    left_join(bind_rows(SF2,SF2_skips) %>% 
                select(ORI_universe,wgtGpRegion,wgtGpRegionDesc,
                       #Update (27AUG2021): Add raw weight group variable
                       wgtGpRegion_raw,wgtGpRegionDesc_raw),
              by=c("ORI_universe")) %>%
    #Update (18Jan2023): adding new calibration variables
    left_join(SF2_wgts2 %>%
                select(ORI_universe,all_of(calVars)),
              by=c("ORI_universe"))
  
  #write_csv(newSF,file=paste0(output_weighting_data_folder,"SF_postR.csv"))
  fwrite_wrapper(newSF,paste0(output_weighting_data_folder,"SF_postR.csv"))
  
  #Note (JDB 06Jul2022): Export weight check results
  #write_csv(results_region,
  fwrite_wrapper(results_region, paste0(output_weighting_data_folder,"weights_region_checks.csv"))
} else {
  stop("No calibration model converged for 1+ (region X weighting group) crossing")
}
log_info("Finished 03_Weights_Calibration_Region_AltCombs.R\n\n")
