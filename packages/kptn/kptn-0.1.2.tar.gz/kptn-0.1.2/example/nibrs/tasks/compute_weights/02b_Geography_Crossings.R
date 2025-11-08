#This program will create the full list of potential geography crossings
library(tidyverse)
library(readxl)
library(openxlsx)

CONST_YEAR <- Sys.getenv("DATA_YEAR")


log_info("Started 02b_Geography_Crossings.R\n\n")

#Read in necessary data
if (as.numeric(CONST_YEAR)>=2021){
  test <- paste0(input_weighting_data_folder,"SF_county.csv") %>%
    read_csv_logging()
} else {
  test <- paste0(input_weighting_data_folder,"SF.csv") %>%
    read_csv_logging()
}
#First, define the weighting groups by geography type
#01May2024: bumping up # of state wgt groups from 9 to 10 due to addition of self-reporting LEAs
natWgtGps <- 1:20 #National
regWgtGps <- natWgtGps #Region (same as national)
stateWgtGps <- 1:12 #State

#16May2024: accounting for increased number of JD weight groups (from 3 to 4 due to self-representing LEAs)
if (as.numeric(CONST_YEAR)>=2021){
  jdWgtGps <- 1:4 #Judicial district (JD) (4 groups)
  msaWgtGps <- 1:3 #MSA (the number will be updated below for 2022 and later)
  foWgtGps <- 1:3 #Field office (FO) (3 groups)
}
#02May2024: vary # of MSA weighting groups by year
#			The formula used will be: (nWgtGp)*(nMDs+1)
#			where nWgtGp is the number of base weighting groups,
#			and nMDs is the number of metro divisions in the permutation file
#16May2024: adding 1 to # of MSA wgt groups (from 114 to 115 due to self-representing LEAs)
if (CONST_YEAR >= 2022){
  mdList <- test %>% 
    group_by(MSA_NAME_COUNTY,METRO_DIVISION_COUNTY) %>% 
    dplyr::summarize(n=n()) %>%
    group_by(MSA_NAME_COUNTY) %>% 
    mutate(nMD=n()) %>% 
    ungroup() %>%
    filter(nMD > 1) %>% 
    arrange(METRO_DIVISION_COUNTY) %>% 
    pull(METRO_DIVISION_COUNTY) 
  
  nMDs <- length(mdList)
  
  #24Jun2025: trying to build in fail-safe for repeatedly updating msaWgtGps...
  #           regarding the formula...
  #             -the 1st +1 is for MSAs without metro divisions
  #             -the 2nd +1 is bc self-representing LEAs get their own group
  if (max(msaWgtGps)==3){
    msaWgtGps <- 1:(max(msaWgtGps)*(nMDs+1)+1)
  }
}
natLvls <- "National"
natCrossings <- expand.grid(natLvl=natLvls,
                            natWgtGp=natWgtGps) %>%
  mutate(natCrossNum=1:nrow(.))

regLvls <- test %>%
  select(REGION_CODE,REGION_NAME) %>%
  unique() %>%
  arrange(REGION_CODE) %>%
  pull(REGION_NAME)
regCrossings <- expand.grid(regLvl=regLvls,
                            regWgtGp=regWgtGps) %>%
  arrange(regLvl,regWgtGp) %>%
  mutate(regCrossNum=max(natCrossings$natCrossNum)+(1:nrow(.)))

stateLvls <- test %>%
  pull(STATE_NAME) %>%
  unique() %>%
  sort()
stateCrossings <- expand.grid(stateLvl=stateLvls,
                              stateWgtGp=stateWgtGps) %>%
  arrange(stateLvl,stateWgtGp) %>%
  mutate(stateCrossNum=max(regCrossings$regCrossNum)+(1:nrow(.)))

#06Aug2025: reordering from JD -> MSA -> FO, to now FO -> JD -> MSA...
#           this reflects the order in which calibration is done
if (as.numeric(CONST_YEAR)>=2021){#Only process sub-states for 2021+
  
  foLvls <- test %>%
    pull(FIELD_OFFICE_NAME) %>%
    unique() %>%
    sort()
  foCrossings <- expand.grid(foLvl=foLvls,
                             foWgtGp=foWgtGps) %>%
    arrange(foLvl,foWgtGp) %>%
    #mutate(foCrossNum=max(msaCrossings$msaCrossNum)+(1:nrow(.)))
    mutate(foCrossNum=max(stateCrossings$stateCrossNum)+(1:nrow(.)))
  
  jdLvls <- test %>%
    pull(JUDICIAL_DISTRICT_NAME) %>%
    unique() %>%
    sort()
  jdCrossings <- expand.grid(jdLvl=jdLvls,
                             jdWgtGp=jdWgtGps) %>%
    arrange(jdLvl,jdWgtGp) %>%
    #mutate(jdCrossNum=max(stateCrossings$stateCrossNum)+(1:nrow(.)))
    mutate(jdCrossNum=max(foCrossings$foCrossNum)+(1:nrow(.)))
  
  msaLvls <- test %>%
    pull(MSA_NAME_COUNTY) %>%
    unique() %>%
    sort()
  
  #24Jun2025: reducing # of unnecessary rows for MSAs, by looking at data possible... leaving 2023 alone, since it's already been run, but including for >=2024
  #06Aug2025: switching to reducing # of MSA rows for 2022 onward...
  if (as.numeric(CONST_YEAR)>=2022){
    mdCW <- test %>%
      ungroup() %>%
      filter(METRO_DIVISION_COUNTY %in% mdList) %>%
      arrange(METRO_DIVISION_COUNTY) %>%
      select(msaLvl=MSA_NAME_COUNTY,METRO_DIVISION_COUNTY) %>%
      unique() %>%
      mutate(mdNum=row_number(),
             one=1) %>%
      select(msaLvl,mdNum) %>%
      bind_rows(test %>% 
                  filter(!METRO_DIVISION_COUNTY %in% mdList) %>%
                  select(msaLvl=MSA_NAME_COUNTY) %>%
                  unique() %>%
                  mutate(mdNum=0)) %>%
      mutate(one=1) 
    
    #Now, get our full MSA list by crossing with our # of groups per MSA (x MD)
    nMSAWgtGpsEach <- (length(msaWgtGps)-1)/(nMDs+1)
    msaCrossings <- data.frame(one=1,
                               msaWgtGp=1:nMSAWgtGpsEach) %>%
      full_join(mdCW,relationship='many-to-many') %>%
      #Tweak the weight group to reflect division
      #06Aug2025: switching from hard-coding # of wgt groups per MD from 3 to
      mutate(msaWgtGp=3*mdNum+msaWgtGp) %>%
      arrange(msaLvl,msaWgtGp) %>%
      mutate(msaCrossNum=max(jdCrossings$jdCrossNum)+(1:nrow(.))) %>%
      select(msaLvl,msaWgtGp,msaCrossNum)
  } else {
    msaCrossings <- expand.grid(msaLvl=msaLvls,
                                msaWgtGp=msaWgtGps) %>%
      arrange(msaLvl,msaWgtGp) %>%
      mutate(msaCrossNum=max(jdCrossings$jdCrossNum)+(1:nrow(.)))
  }
  
}

#Export
#06Aug2025: reordering sheets from JD -> MSA -> FO, to FO -> JD -> MSA

workbook<-paste0(output_weighting_data_folder,"Geography_Crossings.xlsx")

wb<-createWorkbook()
addWorksheet(wb,"National")
addWorksheet(wb,"Region")
addWorksheet(wb,"State")
if (as.numeric(CONST_YEAR)>=2021){
  addWorksheet(wb,"FO")
  addWorksheet(wb,"JD")
  addWorksheet(wb,"MSA")
}

writeData(wb,"National",
          natCrossings,
          rowNames=FALSE)
writeData(wb,"Region",
          regCrossings,
          rowNames=FALSE)
writeData(wb,"State",
          stateCrossings,
          rowNames=FALSE)
if (as.numeric(CONST_YEAR)>=2021){
  writeData(wb,"FO",
            foCrossings,
            rowNames=FALSE)
  writeData(wb,"JD",
            jdCrossings,
            rowNames=FALSE)
  writeData(wb,"MSA",
            msaCrossings,
            rowNames=FALSE)
}
saveWorkbook(wb, workbook, overwrite = TRUE)

log_info("Finished 02b_Geography_Crossings.R\n\n")
