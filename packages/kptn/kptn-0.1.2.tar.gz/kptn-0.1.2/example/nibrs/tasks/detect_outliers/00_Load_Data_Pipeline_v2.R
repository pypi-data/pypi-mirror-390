########
#Overhauling outlier detection

# rm(list=ls() %>% subset(!. %in% c("outputPipelineDir","filepathout","inputPipelineDir","mainpath","mainpathdata")))


##############
# Load data
library(tidyverse)
library(reshape2)
library(data.table)

#####
#NIBRS
nibrsRaw <- fread(file=paste0(mainpathdata,"NIBRS_reporting_pattern_with_reta-mm.csv"))



nibrs <- nibrsRaw %>%   
  #subset(nibrs_missing_pattern_all != "000-000-000-000") %>%
  mutate(der_joiners=case_when(nibrs_agn_nibrs_start_date >= "2017-02-01" ~ 1, #New Joiners
                               !is.na(nibrs_agn_nibrs_start_date) ~ 2 #Experienced Joiners
  )) %>%
  select(ori,ucr_agency_name,matches("POP"),nibrs_agn_state_name,
         nibrs_agn_agency_type_name,incident_year,nibrs_agn_msa_name, 
         matches("_(part1(v|p)|otherc|all$)"),der_joiners)

# nibrs %>%
#   .$der_joiners %>%
#   table(useNA="ifany")


###########
# Assign each agency a group


group_code <- c(1:6,7.1,7.2,8:14)
group_desc <- c("Cities 250,000 and over", 
                "Cities 100,000 - 249,999", 
                "Cities 50,000 - 99,999", 
                "Cities 25,000 - 49,999", 
                "Cities 10,000 - 24,999", 
                "Cities 2,500 - 9,999", 
                "Cities under 2,500 (Pop>0)", 
                "Cities under 2,500 (Pop=0)",
                "Zero-Pop: Non-MSA counties & State Police", 
                "Non-Zero Pop: Non-MSA counties & State Police", 
                "Zero-Pop: MSA counties & State Police", 
                "Non-Zero Pop: MSA counties & State Police", 
                "Federal Police", 
                "Tribal Police", 
                "Other")

nibrs %>%
  group_by(nibrs_agn_agency_type_name) %>%
  dplyr::summarize(n=n())


nibrs_groups <- nibrs %>%
  mutate(rtiGroup_code=case_when(
    #City agencies
    nibrs_agn_agency_type_name=="City" & nibrs_agn_population >= 250000                               ~ 1,
    nibrs_agn_agency_type_name=="City" & nibrs_agn_population >= 100000 & nibrs_agn_population < 250000 ~ 2,
    nibrs_agn_agency_type_name=="City" & nibrs_agn_population >=  50000 & nibrs_agn_population < 100000 ~ 3,
    nibrs_agn_agency_type_name=="City" & nibrs_agn_population >=  25000 & nibrs_agn_population <  50000 ~ 4,
    nibrs_agn_agency_type_name=="City" & nibrs_agn_population >=  10000 & nibrs_agn_population <  25000 ~ 5,
    nibrs_agn_agency_type_name=="City" & nibrs_agn_population >=   2500 & nibrs_agn_population <  10000 ~ 6,
    nibrs_agn_agency_type_name=="City" & nibrs_agn_population >       0 & nibrs_agn_population <   2500 ~ 7.1,
    nibrs_agn_agency_type_name=="City" & nibrs_agn_population ==      0                               ~ 7.2,
    #Counties & SP
    nibrs_agn_agency_type_name %in% c("County","State Police") & nibrs_agn_msa_name=="Non-MSA"  & nibrs_agn_population==0 ~  8,
    nibrs_agn_agency_type_name %in% c("County","State Police") & nibrs_agn_msa_name=="Non-MSA"  & nibrs_agn_population >0 ~  9,
    nibrs_agn_agency_type_name %in% c("County","State Police") & nibrs_agn_msa_name!="Non-MSA" & nibrs_agn_population==0 ~ 10,
    nibrs_agn_agency_type_name %in% c("County","State Police") & nibrs_agn_msa_name!="Non-MSA" & nibrs_agn_population >0 ~ 11,
    #Federal
    nibrs_agn_agency_type_name=="Federal" ~ 12,
    #Tribal
    nibrs_agn_agency_type_name=="Tribal" ~ 13,
    #Other (includes nibrs_agn_agency_type_name='Other','Other State Agency','University or College',<NA>)
    TRUE ~ 14)) %>%
  mutate(rtiGroup_desc=factor(rtiGroup_code,levels=group_code,labels=group_desc))

############
# Data prep

#Separating records by year, and generating long versions with 1 record per agency X month

#Month abbreviation (e.g., jan,feb,...) X month number crosswalk
monthsDF <- data.frame(month=tolower(month.abb),
                       month_num=1:12)
#Get years in NIBRS
#Update (12JUL2021): Allowing user to specify environment variable for years.
#                    Previously, always would pull automatically.
if (Sys.getenv("nibrsYrs")==""){
  nibrsYrs <- nibrs_groups %>%
    .$incident_year %>%
    unique() %>%
    sort() %>%
    as.list()
} else {
  nibrsYrs <- Sys.getenv("nibrsYrs") %>%
    parse(text=.) %>%
    eval() %>%
    as.list()
}
#Update (23JUL2021): use 5 most recent years
if (length(nibrsYrs)>5){
  nibrsYrs <- nibrsYrs[(length(nibrsYrs)-4):length(nibrsYrs)]
}
###########
#Separate records by year
rename_year <- function(dat,year){
  #Filter to year of interest
  return(dat %>% 
           filter(incident_year == year) %>%
           rename_at(vars(-c(ori,ucr_agency_name,incident_year,nibrs_agn_state_name,
                             nibrs_agn_agency_type_name,der_joiners,
                             nibrs_agn_population,nibrs_agn_parent_pop_group_code,
                             nibrs_agn_parent_pop_group_desc,rtiGroup_code,
                             rtiGroup_desc)),
                     ~ paste0(., "_", year) ) %>% 
           select(-incident_year) %>%
           select(ori,
                  ucr_agency_name,
                  der_joiners,
                  nibrs_agn_population,
                  nibrs_agn_parent_pop_group_code,
                  nibrs_agn_parent_pop_group_desc,
                  rtiGroup_code, 
                  rtiGroup_desc,
                  nibrs_agn_state_name, 
                  nibrs_agn_agency_type_name,
                  paste0("(",str_flatten(tolower(month.abb),collapse="|"),")_all") %>%
                    matches(.),
                  paste0("(",str_flatten(tolower(month.abb),collapse="|"),")_part1p") %>% 
                    matches(.),
                  paste0("(",str_flatten(tolower(month.abb),collapse="|"),")_part1v") %>% 
                    matches(.),
                  paste0("(",str_flatten(tolower(month.abb),collapse="|"),")_otherc") %>% 
                    matches(.)) %>% #,REGION_DESC
           reshape2::melt(.,id.vars=c("ori", "ucr_agency_name","der_joiners", "nibrs_agn_state_name", "nibrs_agn_parent_pop_group_code","nibrs_agn_parent_pop_group_desc", "nibrs_agn_population", "rtiGroup_code", "rtiGroup_desc", "nibrs_agn_agency_type_name")) %>% #,"REGION_DESC"
           mutate(crimeRate=value/nibrs_agn_population) %>%
           mutate(month_type_year=str_split(variable,"_")) %>%
           mutate(month=sapply(month_type_year,'[[',1),
                  type=sapply(month_type_year,'[[',2),
                  year=sapply(month_type_year,'[[',3)) %>%
           mutate(month_num=factor(month,levels=monthsDF$month,labels=monthsDF$month_num)) %>%
           arrange(ori,year,month_num,type) %>%
           select(-month_type_year) %>%
           mutate(variable2=variable) %>%
           mutate(variable="count") %>%
           reshape2::dcast(ori+ucr_agency_name+nibrs_agn_state_name+nibrs_agn_parent_pop_group_code+nibrs_agn_parent_pop_group_desc+nibrs_agn_population+rtiGroup_code+rtiGroup_desc+ nibrs_agn_agency_type_name+der_joiners+month+year+month_num~variable+type) %>%
           rename(count_allC=count_all) %>%
           mutate(crimeRate_allC=count_allC/nibrs_agn_population,
                  crimeRate_part1p=count_part1p/nibrs_agn_population,
                  crimeRate_part1v=count_part1v/nibrs_agn_population,
                  crimeRate_otherc=count_otherc/nibrs_agn_population))
}


#Loop over years in NIBRS, then create separate dataframes
nibrs_byYr <- sapply(nibrsYrs,rename_year,dat=nibrs_groups,simplify=FALSE)
names(nibrs_byYr) <- paste0("nibrs_",nibrsYrs,"_long")
list2env(nibrs_byYr,envir=.GlobalEnv)
rm(nibrs_byYr)

#Combine all years
nibrs_allYrs_long <- bind_rows(mget(paste0("nibrs_",nibrsYrs,"_long"))) %>%
  
  mutate(year_num=as.numeric(year),
         month_num=as.numeric(month_num)) %>%
  #Create numeric month var for n months from beginning (e.g., Jan, 2016)
  mutate(month_num_abs=month_num+12*(year_num-min(as.numeric(nibrsYrs)))) %>%
  mutate(popGroup_code=case_when(
    nibrs_agn_population==0 ~ 1,
    nibrs_agn_population<2500 ~ 2,
    nibrs_agn_population<10000 ~ 3,
    nibrs_agn_population<25000 ~ 4,
    nibrs_agn_population<50000 ~ 5,
    nibrs_agn_population<100000 ~ 6,
    nibrs_agn_population<250000 ~ 7,
    nibrs_agn_population>=250000 ~ 8))



#################
#Get lists of: 
#>All LEAs per time period,
#>Minimum population over the years per LEA, and
#>Number of records per LEA where count_all > 0


####
#List of LEAs

getORIs <- function(dat){
  dat %>%
    pull(ori) %>%
    unique()
}
oris_allYrs <- nibrs_allYrs_long$ori %>% unique()

oris_byYr <- sapply(mget(paste0("nibrs_",nibrsYrs,"_long")),getORIs)
names(oris_byYr) <- paste0("oris_",nibrsYrs)
list2env(oris_byYr,env=.GlobalEnv)
rm(oris_byYr)


####
#Min pop by LEA

minPop_allYrs <- nibrs_allYrs_long %>%
  #subset(.,count_all>0) %>%
  group_by(ori) %>%
  dplyr::summarize(minPop_allYrs=min(nibrs_agn_population,na.rm=TRUE),
                   .groups="drop_last") %>%
  ungroup()
minPop_allYrs %>%
  pull(minPop_allYrs) %>%
  is.na() %>%
  table()

#Note: not doing by year, bc the 'minPop' is just that year's population...

####
#Sum of counts + percentiles

getStats <- function(yr){
  dat <- get(paste0("nibrs_",yr,"_long"))
  types <- c("allC","part1p","part1v","otherc")
  countVars <- paste0("count_",types)
  rateVars <- paste0("crimeRate_",types)
  statsORI <- dat %>%
    group_by(ori) %>%
    rename(allC=count_allC,
           part1p=count_part1p,
           part1v=count_part1v,
           otherc=count_otherc) %>%
    dplyr::summarize(across(all_of(types),~sum(!is.na(.x),na.rm=TRUE),.names="nMonths_{.col}"),#n months by crime type
                     across(all_of(types),~sum(.x>0,na.rm=TRUE),.names="nPosMonths_{.col}"),#n months > 0 by crime type
                     across(all_of(types),~sum(.x,na.rm=TRUE),.names="sumCounts_{.col}"), #sum (counts) by crime types
                     across(all_of(types),~median(.x,na.rm=TRUE),.names="medianCount_{.col}"), #median (counts) by crime type
                     #across(rateVars,~median(.x,na.rm=TRUE),.names="medianRate_{.col}"),#median (rates) by crime type
                     across(all_of(types),~max(.x,na.rm=TRUE),.names="maxCount_{.col}"),#max (counts) by crime type
                     across(all_of(types),~mean(.x,na.rm=TRUE),.names="meanCount_{.col}"),#mean (counts) by crime type
                     .groups="drop") %>%
    #Clean up cases with no non-missing crimes of each type
    mutate(across(paste0(c("sumCounts","medianCount","maxCount","meanCount"),"_allC"),
                  ~ifelse(nMonths_allC==0,NA_real_,.x)),
           across(paste0(c("sumCounts","medianCount","maxCount","meanCount"),"_part1p"),
                  ~ifelse(nMonths_part1p==0,NA_real_,.x)),
           across(paste0(c("sumCounts","medianCount","maxCount","meanCount"),"_part1v"),
                  ~ifelse(nMonths_part1v==0,NA_real_,.x)),
           across(paste0(c("sumCounts","medianCount","maxCount","meanCount"),"_otherc"),
                  ~ifelse(nMonths_otherc==0,NA_real_,.x)))
  
  #Percentiles across all ORIs
  pcts_allC <- statsORI %>%
    pull(sumCounts_allC) %>%
    quantile(probs=seq(0,0.6,0.2),na.rm=TRUE)
  
  pcts_part1p <- statsORI %>%
    pull(sumCounts_part1p) %>%
    quantile(probs=seq(0,0.6,0.2),na.rm=TRUE)
  
  pcts_part1v <- statsORI %>%
    pull(sumCounts_part1v) %>%
    quantile(probs=seq(0,0.6,0.2),na.rm=TRUE)
  
  pcts_otherc <- statsORI %>%
    pull(sumCounts_otherc) %>%
    quantile(probs=seq(0,0.6,0.2),na.rm=TRUE)
  
  #Tweak column names before outputting
  colnames(statsORI) <- colnames(statsORI) %>%
    str_replace("(?<=allC|part1p|part1v|otherc)$",paste0("_",yr)) %>%
    str_replace("(?<=medianCount_(allC|part1p|part1v|otherc))","_oneLEA")
  
  out <- list(statsORI,
              pcts_allC,pcts_part1p,pcts_part1v,pcts_otherc)
  
  names(out) <- paste0(c("statsORI",
                         paste0("percentiles_",types)),
                       "_",
                       yr)
  list2env(out,env=.GlobalEnv)
  return(NULL)
}

sapply(c("allYrs",nibrsYrs),getStats)

####
#RTI groups by LEA

#All years
rtiGroups_allYrs <- (
  nibrs_allYrs_long %>%
    group_by(ori,rtiGroup_code) %>%
    dplyr::summarize(n=n(),.groups="drop") %>%
    arrange(ori,rtiGroup_code) %>%
    group_by(ori) %>%
    summarize(nGroups=n(),
              rtiGroups_allYrs=str_flatten(rtiGroup_code,collapse=", "))  %>%
    mutate(rtiGroups_allYrs_desc=str_replace(rtiGroups_allYrs,"14","Other") %>%
             str_replace(.,"13","Tribal Police") %>%
             str_replace(.,"12","Federal Police") %>%
             str_replace(.,"11","Non-Zero Pop: MSA counties & State Police") %>%
             str_replace(.,"10","Zero-Pop: MSA counties & State Police") %>%
             str_replace(.,"(^|, )9","\\1Non-Zero Pop: Non-MSA counties & State Police") %>%
             str_replace(.,"8","Zero-Pop: Non-MSA counties & State Police") %>%
             str_replace(.,"7\\.2","Cities under 2,500 (Pop=0)") %>%
             str_replace(.,"7\\.1","Cities under 2,500 (Pop>0)") %>%
             str_replace(.,"6","Cities 2,500 - 9,999") %>%
             str_replace(.,"(^|, )5","\\1Cities 10,000 - 24,999") %>%
             str_replace(.,"(^|, )4","\\1Cities 25,000 - 49,999") %>%
             str_replace(.,"3","Cities 50,000 - 99,999") %>%
             str_replace(.,"(^|, )2","\\1Cities 100,000 - 249,999") %>%
             str_replace(.,"(^|, )1","\\1Cities 250,000 and over")) %>%
    ungroup())

#Same as above, but long instead of wide format
rtiGroups_allYrs_byGp <- nibrs_allYrs_long %>%
  group_by(ori,rtiGroup_code) %>%
  dplyr::summarize(n=n(),.groups="drop") %>%
  arrange(ori,rtiGroup_code) %>%
  select(.,ori,rtiGroup_code) %>%
  ungroup()

getRTIGroups <- function(yr){
  dat <- get(paste0("nibrs_",yr,"_long"))
  rtiGroup <- dat %>%
    group_by(ori,rtiGroup_code) %>%
    dplyr::summarize(n=n(),
                     .groups="drop") %>%
    rename(!!paste0("rtiGroup_",yr):=rtiGroup_code)
  return(rtiGroup)
  
}
rtiGroup_byYr <- sapply(nibrsYrs,getRTIGroups,simplify=FALSE)
names(rtiGroup_byYr) <- paste0("rtiGroup_",nibrsYrs)
list2env(rtiGroup_byYr,env=.GlobalEnv)
rm(rtiGroup_byYr)


#Median - Grouped/Cross-sectional
medianCounts_cs_allYrs <- (
  nibrs_allYrs_long %>%
    group_by(rtiGroup_code) %>%
    dplyr::summarize(
      medianCount_allC_cs_allYrs=median(count_allC,na.rm=TRUE),
      medianRate_allC_cs_allYrs=median(crimeRate_allC,na.rm=TRUE),
      .groups="drop") %>%
    ungroup()) 



############
# Merge on new variables

####
#Merge on minPop + number of positive records + create indicators for month number

nibrs_allYrs_long2 <- nibrs_allYrs_long %>%
  subset(!is.na(count_allC)) %>%
  group_by(ori) %>%
  arrange(ori,year,month_num) %>%
  mutate(repMonth_num=row_number()) %>%
  ungroup() %>%
  select(ori,year,month_num,repMonth_num) %>%
  full_join(nibrs_allYrs_long,by=c("ori","year","month_num")) %>%
  full_join(rtiGroups_allYrs,by="ori") %>%
  full_join(minPop_allYrs,by="ori") %>%
  #inner_join(statsORI_allYrs,by=c("ori")) %>%
  full_join(medianCounts_cs_allYrs,by="rtiGroup_code")

mergeStats <- function(dat,yr){
  temp.statsORI <- get(paste0("statsORI_",yr))
  temp.pctAllC <- get(paste0("percentiles_allC_",yr))
  temp.pctP1P <- get(paste0("percentiles_part1p_",yr))
  temp.pctP1V <- get(paste0("percentiles_part1v_",yr))
  temp.pctOthC <- get(paste0("percentiles_otherc_",yr))
  
  temp.sumCtsAllCVar <- as.symbol(paste0("sumCounts_allC_",yr))
  temp.sumCtsP1PVar <- as.symbol(paste0("sumCounts_part1p_",yr))
  temp.sumCtsP1VVar <- as.symbol(paste0("sumCounts_part1v_",yr))
  temp.sumCtsOthCVar <- as.symbol(paste0("sumCounts_otherc_",yr))
  
  out <- dat %>%
    full_join(temp.statsORI,by="ori") %>%
    mutate(!!paste0("percentile_allC_",yr):=case_when(
      eval(temp.sumCtsAllCVar)<=temp.pctAllC[2] ~ 1,
      eval(temp.sumCtsAllCVar)<=temp.pctAllC[3] ~ 2,
      eval(temp.sumCtsAllCVar)<=temp.pctAllC[4] ~ 3,
      eval(temp.sumCtsAllCVar)> temp.pctAllC[4] ~ 4)) %>%
    mutate(!!paste0("percentile_part1p_",yr):=case_when(
      eval(temp.sumCtsP1PVar)<=temp.pctP1P[2] ~ 1,
      eval(temp.sumCtsP1PVar)<=temp.pctP1P[3] ~ 2,
      eval(temp.sumCtsP1PVar)<=temp.pctP1P[4] ~ 3,
      eval(temp.sumCtsP1PVar)> temp.pctP1P[4] ~ 4)) %>%
    mutate(!!paste0("percentile_part1v_",yr):=case_when(
      eval(temp.sumCtsP1VVar)<=temp.pctP1V[2] ~ 1,
      eval(temp.sumCtsP1VVar)<=temp.pctP1V[3] ~ 2,
      eval(temp.sumCtsP1VVar)<=temp.pctP1V[4] ~ 3,
      eval(temp.sumCtsP1VVar)> temp.pctP1V[4] ~ 4)) %>%
    mutate(!!paste0("percentile_otherc_",yr):=case_when(
      eval(temp.sumCtsOthCVar)<=temp.pctOthC[2] ~ 1,
      eval(temp.sumCtsOthCVar)<=temp.pctOthC[3] ~ 2,
      eval(temp.sumCtsOthCVar)<=temp.pctOthC[4] ~ 3,
      eval(temp.sumCtsOthCVar)> temp.pctOthC[4] ~ 4)) %>%
    select(matches("(max|mean|sum)Count_"),
           matches(paste0("medianCount_.*_oneLEA")),
           matches("n(Pos|)Months_.*_allYrs"),
           matches("percentile_"))
  return(out)
  
}
nibrs_allYrs_long2 <- bind_cols(nibrs_allYrs_long2,
                                sapply(c("allYrs",nibrsYrs),mergeStats,dat=nibrs_allYrs_long2,simplify=FALSE))

#Repeat, by year
# mergeStatsYr <- function(yr){
#   dat <- get(paste0("nibrs_",yr,"_long"))
#   temp.statsORI <- get(paste0("statsORI_",yr))
#   temp.pctAllC <- get(paste0("percentiles_allC_",yr))
#   temp.pctP1P <- get(paste0("percentiles_part1p_",yr))
#   temp.pctP1V <- get(paste0("percentiles_part1v_",yr))
#   temp.pctOthC <- get(paste0("percentiles_otherc_",yr))
#   
#   temp.sumCtsAllCVar <- as.symbol(paste0("sumCounts_allC_",yr))
#   temp.sumCtsP1PVar <- as.symbol(paste0("sumCounts_part1p_",yr))
#   temp.sumCtsP1VVar <- as.symbol(paste0("sumCounts_part1v_",yr))
#   temp.sumCtsOthCVar <- as.symbol(paste0("sumCounts_otherc_",yr))
#   
#   out <- dat %>%
#     full_join(temp.statsORI,by="ori") %>%
#     mutate(!!paste0("percentile_allC_",yr):=case_when(
#       eval(temp.sumCtsAllCVar)<=temp.pctAllC[2] ~ 1,
#       eval(temp.sumCtsAllCVar)<=temp.pctAllC[3] ~ 2,
#       eval(temp.sumCtsAllCVar)<=temp.pctAllC[4] ~ 3,
#       eval(temp.sumCtsAllCVar)> temp.pctAllC[4] ~ 4)) %>%
#     mutate(!!paste0("percentile_part1p_",yr):=case_when(
#       eval(temp.sumCtsP1PVar)<=temp.pctP1P[2] ~ 1,
#       eval(temp.sumCtsP1PVar)<=temp.pctP1P[3] ~ 2,
#       eval(temp.sumCtsP1PVar)<=temp.pctP1P[4] ~ 3,
#       eval(temp.sumCtsP1PVar)> temp.pctP1P[4] ~ 4)) %>%
#     mutate(!!paste0("percentile_part1v_",yr):=case_when(
#       eval(temp.sumCtsP1VVar)<=temp.pctP1V[2] ~ 1,
#       eval(temp.sumCtsP1VVar)<=temp.pctP1V[3] ~ 2,
#       eval(temp.sumCtsP1VVar)<=temp.pctP1V[4] ~ 3,
#       eval(temp.sumCtsP1VVar)> temp.pctP1V[4] ~ 4)) %>%
#     mutate(!!paste0("percentile_otherc_",yr):=case_when(
#       eval(temp.sumCtsOthCVar)<=temp.pctOthC[2] ~ 1,
#       eval(temp.sumCtsOthCVar)<=temp.pctOthC[3] ~ 2,
#       eval(temp.sumCtsOthCVar)<=temp.pctOthC[4] ~ 3,
#       eval(temp.sumCtsOthCVar)> temp.pctOthC[4] ~ 4))
#   return(out)
#   
# }

#Compare to old version (only run after running above lines and then old program)
#nibrs_byYr_long2 <- sapply(nibrsYrs,mergeStatsYr,simplify=FALSE)
#names(nibrs_byYr_long2) <- paste0("nibrs_",nibrsYrs,"_long2")
#list2env(nibrs_byYr_long2,env=.GlobalEnv)
#rm(nibrs_byYr_long2)

# all.equal(nibrs_allYrs_long2 %>% 
#             arrange(ori,month_num_abs) %>%
#             subset(!is.na(count_allC)) %>% 
#             select(colnames(nibrs_allYrs_long2)),
#           nibrs_allYrs_long2 %>% 
#             arrange(ori,month_num_abs) %>%
#             subset(!is.na(count_allC)),
#           countEQ=TRUE)
# old <- nibrs_allYrs_long2 %>% 
#   subset(!is.na(count_allC)) %>% 
#   select(ori,month_num_abs,old=percentile_allC_2018)%>%
#   subset(duplicated(.)==FALSE)
# new <- nibrs_allYrs_long2 %>% 
#   subset(!is.na(count_allC)) %>% 
#   select(ori,month_num_abs,new=percentile_allC_2018)%>%
#   subset(duplicated(.)==FALSE)
# full_join(old,new) %>% subset(new != old | (is.na(new)!=is.na(old))) %>% nrow()
# full_join(old,new) %>% subset(new != old|is.na(new)!=is.na(old)) %>% head()
