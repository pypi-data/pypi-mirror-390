
### Purpose of program is to calibrate special agency weights by grouping (e.g., All cities 250,000 or over)
### Author: JD Bunker
### Last updated: 01FEB2022
log_info("Running 03_Weights_Calibration_Special.R")

# read in SF data
SF <- paste0(input_weighting_data_folder,"SF_postS.csv") %>%
  read_dot_csv_logging(header=TRUE, sep=",")

#Update (14FEB2022): Adding weight group
#Update (15FEB2022): Modify weight group
#Update (25JUL2024): No longer set resp_ind_m3=1 here (and modify how we merge ratioUni and ratioTribal onto SF)
ratioUni <-  SF %>%
  subset(AGENCY_TYPE_NAME=="University or College") %>%
  group_by(AGENCY_TYPE_NAME) %>%
  dplyr::summarize(nUniverse=n(),
                   nNIBRS=sum(resp_ind_m3,na.rm=TRUE),
                   .groups="drop") %>%
  mutate(UniversityWgt=nUniverse/nNIBRS,
         wgtGpUniversity=1,
         wgtGpUniversityDesc="All University LEAs") %>%#,
         #resp_ind_m3=1) %>%
    select(AGENCY_TYPE_NAME,#resp_ind_m3,
	       UniversityWgt,
           wgtGpUniversity,wgtGpUniversityDesc)
ratioTribal <- SF %>%
  subset(AGENCY_TYPE_NAME=="Tribal") %>%
  group_by(AGENCY_TYPE_NAME) %>%
  dplyr::summarize(nUniverse=n(),
                   nNIBRS=sum(resp_ind_m3,na.rm=TRUE),
                   .groups="drop") %>%
  mutate(TribalWgt=nUniverse/nNIBRS,
         wgtGpTribal=1,
         wgtGpTribalDesc="All Tribal LEAs") %>%#,
         #resp_ind_m3=1) %>%
  select(AGENCY_TYPE_NAME,#resp_ind_m3,
         TribalWgt,
         wgtGpTribal,wgtGpTribalDesc)

#25Jul2024: no longer merge ratioUni and ratioTribal on resp_ind_m3 (which inadvertently caused weighting group to be missing for tribal/university nonreporters)
#25Jul2024: also, wiping out the tribal/university weights for nonreporters
SF <- SF  %>%
  #left_join(ratioUni,by=c("AGENCY_TYPE_NAME","resp_ind_m3")) %>%
  #left_join(ratioTribal,by=c("AGENCY_TYPE_NAME","resp_ind_m3"))
  left_join(ratioUni,by=c("AGENCY_TYPE_NAME")) %>%
  left_join(ratioTribal,by=c("AGENCY_TYPE_NAME")) %>%
  mutate(UniversityWgt=ifelse(resp_ind_m3 != 1,
                              NA_real_,
							  UniversityWgt),
	     TribalWgt=ifelse(resp_ind_m3 != 1,
		                  NA_real_,
						  TribalWgt))


#Requested checks
#Note (06Jul2022): No longer store as text file - rather, calculate here and export as CSV, then include in HTML output later
#Note (16May2024): added min and max to checks

#University
#capture.output({
  #Weight checks - summary, UWE, etc.
  #print("Distribution of weights:")
  #describe(SF$UniversityWgt) %>%
  #  print()
  #print("Number of missing weights:")
  #sum(is.na(SF$UniversityWgt))%>%
  #  print()
  #print("Number of weights equal to 1:")
  #sum(SF$UniversityWgt == 1, na.rm=TRUE) %>%
  #  print()
  #print("Number of weights greater than 1:")
  #sum(SF$UniversityWgt > 1, na.rm=TRUE) %>%
  #  print()
  #print("Number of weights less than 1:")
  #sum(SF$UniversityWgt < 1, na.rm=TRUE) %>%
  #  print()
  #print("Number of weights greater than 100:")
  #sum(SF$UniversityWgt > 100, na.rm=TRUE) %>%
  #  print()
  #print("UWE:")
  #UWE_UniversityWgt <- 1+var(SF$UniversityWgt,na.rm=TRUE)/(mean(SF$UniversityWgt,na.rm=TRUE)^2)
  #UWE_UniversityWgt %>%
  #  print()
	
  out_temp <- SF %>%
    subset(AGENCY_TYPE_NAME=="University or College" & resp_ind_m3==1)
  #Note (26Jul2022): Adding n Eligible LEAs
  temp.nElig <- SF %>%
    subset(AGENCY_TYPE_NAME=="University or College") %>%
    nrow()
  if (out_temp %>% nrow()>0){
    
    temp.describe <- describe(out_temp$UniversityWgt)
    temp.quantiles <- quantile(out_temp$UniversityWgt,
                               probs=c(0,0.05,0.1,0.25,0.5,0.75,0.9,0.95,1),
                               na.rm=TRUE)
    temp.nLT1 <- sum(out_temp$UniversityWgt < 1 & out_temp$UniversityWgt>0, na.rm=TRUE)
    #Note (29Jul2022): Switching from >100 to >20
    #temp.nGT100 <- sum(out_temp$UniversityWgt > 100, na.rm=TRUE)
    temp.nGT20 <- sum(out_temp$UniversityWgt > 20, na.rm=TRUE)
    temp.UWE <- 1+var(out_temp$UniversityWgt,na.rm=TRUE)/(mean(out_temp$UniversityWgt,na.rm=TRUE)^2)
    temp.out <- data.frame(wgtGpUniversityDesc="All University LEAs",
                           #Note (26Jul2022): Changing counts - include n Eligible LEAs, n NIBRS LEAs, n NIBRS LEAs missing weights
                           #nOverall=as.numeric(temp.describe$counts["n"])+as.numeric(temp.describe$counts["missing"]),
                           nElig=temp.nElig,
                           nNIBRS=as.numeric(temp.describe$counts["n"])+as.numeric(temp.describe$counts["missing"]),
                           nMissing=as.numeric(temp.describe$counts["missing"]),
                           nLT1=temp.nLT1,
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
  } else {
    temp.out <- data.frame(wgtGpUniversityDesc="All University LEAs",
                           #nOverall=nrow(out_temp),
                           #nMissing=nrow(out_temp),
                           nElig=temp.nElig,
                           nNIBRS=0,
                           nMissing=0,
                           nLT1=0,
                           #nGT100=0,
                           nGT20=0,
                           UWE=NA_character_,
                           Mean=NA_character_,
                           Min=NA_character_,
                           pt05=NA_character_,
                           pt10=NA_character_,
                           pt25=NA_character_,
                           pt50=NA_character_,
                           pt75=NA_character_,
                           pt90=NA_character_,
                           pt95=NA_character_,
                           Max=NA_character_)
  }
  colnames(temp.out) <- c("Weighting group",
                          "n Eligible LEAs","n NIBRS LEAs, Overall","n NIBRS LEAs, Missing Weight",
                          "n LT 1","n GT 20","UWE",#"n GT 100","UWE",
                          "Mean","Minimum","5th Pctl","10th Pctl","25th Pctl","50th Pctl",
                          "75th Pctl","90th Pctl","95th Pctl","Maximum")
  temp.out <- temp.out %>%
    list()
  names(temp.out) <- "results_university"
  list2env(temp.out,.GlobalEnv)
  rm(temp.out)
#},file=paste0(output_weighting_data_folder,'weights_university_checks.txt'))

#Tribal
#capture.output({
  #Weight checks - summary, UWE, etc.
  #print("Distribution of weights:")
  #describe(SF$TribalWgt) %>%
  #  print()
  #print("Number of missing weights:")
  #sum(is.na(SF$TribalWgt))%>%
  #  print()
  #print("Number of weights equal to 1:")
  #sum(SF$TribalWgt == 1, na.rm=TRUE) %>%
  #  print()
  #print("Number of weights greater than 1:")
  #sum(SF$TribalWgt > 1, na.rm=TRUE) %>%
  #  print()
  #print("Number of weights less than 1:")
  #sum(SF$TribalWgt < 1, na.rm=TRUE) %>%
  #  print()
  #print("Number of weights greater than 100:")
  #sum(SF$TribalWgt > 100, na.rm=TRUE) %>%
  #  print()
  #print("UWE:")
  #UWE_TribalWgt <- 1+var(SF$TribalWgt,na.rm=TRUE)/(mean(SF$TribalWgt,na.rm=TRUE)^2)
  #UWE_TribalWgt %>%
  #  print()
	
  out_temp <- SF %>%
    subset(AGENCY_TYPE_NAME=="Tribal" & resp_ind_m3==1)
  
  #Note (26Jul2022): Adding n Eligible LEAs
  temp.nElig <- SF %>%
    subset(AGENCY_TYPE_NAME=="Tribal") %>%
    nrow()
  if (out_temp %>% nrow()>0){
    
    temp.describe <- describe(out_temp$TribalWgt)
    temp.quantiles <- quantile(out_temp$TribalWgt,
                               probs=c(0,0.05,0.1,0.25,0.5,0.75,0.9,0.95,1),
                               na.rm=TRUE)
    temp.nLT1 <- sum(out_temp$TribalWgt < 1 & out_temp$TribalWgt>0, na.rm=TRUE)
    #Note (29Jul2022): Switching from >100 to >20
    #temp.nGT100 <- sum(out_temp$TribalWgt > 100, na.rm=TRUE)
    temp.nGT20 <- sum(out_temp$TribalWgt > 20, na.rm=TRUE)
    temp.UWE <- 1+var(out_temp$TribalWgt,na.rm=TRUE)/(mean(out_temp$TribalWgt,na.rm=TRUE)^2)
    temp.out <- data.frame(wgtGpTribalDesc="All Tribal LEAs",
                           #Note (26Jul2022): Changing counts - include n Eligible LEAs, n NIBRS LEAs, n NIBRS LEAs missing weights
                           #nOverall=as.numeric(temp.describe$counts["n"])+as.numeric(temp.describe$counts["missing"]),
                           nElig=temp.nElig,
                           nNIBRS=as.numeric(temp.describe$counts["n"])+as.numeric(temp.describe$counts["missing"]),
                           nMissing=as.numeric(temp.describe$counts["missing"]),
                           nLT1=temp.nLT1,
                           #nGT100=temp.nGT100,
                           nGT100=temp.nGT20,
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
  } else {
    temp.out <- data.frame(wgtGpTribalDesc="All Tribal LEAs",
                           #nOverall=nrow(out_temp) ,
                           #nMissing=nrow(out_temp),
                           nElig=temp.nElig,
                           nNIBRS=0,
                           nMissing=0,
                           nLT1=0,
                           #nGT100=0,
                           nGT20=0,
                           UWE=NA_character_,
                           Mean=NA_character_,
                           Min=NA_character_,
                           pt05=NA_character_,
                           pt10=NA_character_,
                           pt25=NA_character_,
                           pt50=NA_character_,
                           pt75=NA_character_,
                           pt90=NA_character_,
                           pt95=NA_character_,
                           Max=NA_character_)
  }
  colnames(temp.out) <- c("Weighting group",
                          "n Eligible LEAs","n NIBRS LEAs, Overall","n NIBRS LEAs, Missing Weight",
                          "n LT 1","n GT 20","UWE",#"n GT 100","UWE",
                          "Mean","Minimum","5th Pctl","10th Pctl","25th Pctl","50th Pctl",
                          "75th Pctl","90th Pctl","95th Pctl","Maximum")
  temp.out <- temp.out %>%
    list()
  names(temp.out) <- "results_tribal"
  list2env(temp.out,.GlobalEnv)
  rm(temp.out)
#},file=paste0(output_weighting_data_folder,'weights_tribal_checks.txt'))


### export for others to start writing functions to analyze bias, MSE, etc.
SF[,c("ORI_universe","LEGACY_ORI", "wgtGpUniversityDesc",
      "UniversityWgt","wgtGpUniversity")] %>%
  write_dot_csv_logging(paste0(output_weighting_data_folder,'weights_university.csv'),
            row.names = FALSE)

### export for others to start writing functions to analyze bias, MSE, etc.
SF[,c("ORI_universe","LEGACY_ORI", "wgtGpTribalDesc",
      "TribalWgt","wgtGpTribal")] %>%
  write_dot_csv_logging(paste0(output_weighting_data_folder,'weights_tribal.csv'),
                        row.names = FALSE)


#Update (26AUG2021): Add wgtGpState and wgtGpStateDesc to SF file from 02_Weights_Data_Setup
oldSF <- read_csv_logging(paste0(input_weighting_data_folder,"SF_postS.csv"),
                          guess_max=1e6) %>%
  #Adding just in case already on file...
  select(-matches("wgtGp(University|Tribal)"))
newSF <- oldSF %>%
  left_join(SF %>% 
              select(ORI_universe,
                     wgtGpUniversity,wgtGpUniversityDesc,
                     wgtGpTribal,wgtGpTribalDesc),
            by=c("ORI_universe"))

write_csv_logging(newSF,file=paste0(output_weighting_data_folder,"SF_postSP.csv"))


#Note (JDB 06Jul2022): Export weight check results
write_csv_logging(results_university,
                  file=paste0(output_weighting_data_folder,"weights_university_checks.csv"))
write_csv_logging(results_tribal,
                  file=paste0(output_weighting_data_folder,"weights_tribal_checks.csv"))
					  
log_info("Finished 03_Weights_Calibration_Special.R\n\n")