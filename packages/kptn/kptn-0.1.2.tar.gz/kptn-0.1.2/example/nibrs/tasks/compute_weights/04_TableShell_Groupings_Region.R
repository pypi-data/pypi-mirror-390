#########################################################################
#Program      : 04_TableShell_Groupings_Region
#Description  : Create table shell for Table A within Appendix for region-level by grouping
#
#Project      : NCS-X NIBRS Estimation Project
#Authors      : JD Bunker, Philip Lee, Taylor Lewis, Nicole Mack, Grant Swigart
#Date         :
#Modified     :
#Notes:
#########################################################################

#Groupings original
library(DescTools)
library(sampling)
library(data.table)
library(Hmisc)
library(mice)
library(party)
library(partykit)
library(tidyverse)
library(lubridate)
library(DBI)
library(readxl)
library(DT)
library(lubridate)
library(dplyr)
library(survey)
library(Hmisc)
library(openxlsx)
library(foreign)
library(srvyr)
library(haven)
library(rlang)
library(reshape2)
######################################

log_info("Running 04_TableShell_Groupings_Region.R")

##Get Weight Descriptions
regWgt <- "RegionWgt" #Region weight var
#stateWgt <-"calwt2_m3_1" #(Main) state-level weight variable
weight_descrip0 <- data.frame()
if (nrow(weight_descrip0)<1){
  if (!regWgt %in% weight_descrip0$Variable.Name){
    log_debug("Region Weight not in weight_descrip0")
    weight_descrip0 <- weight_descrip0 %>%
      bind_rows(data.frame(Weight.Number=1,
                           Variable.Name=regWgt,
                           Description="Region Weight"))%>%
      arrange(Weight.Number) %>%
      mutate(Weight.Number = row_number())
    log_debug("Added dummy description to weight_descrip0")
  }
  #if (!stateWgt %in% weight_descrip0$Variable.Name){
  #  print("State Weight not in weight_descrip0")
  #}
}

weight_list_descrip<-(weight_descrip0$Description%>%as.list()) #List of weight description, update as necessary
weight_lists<-(weight_descrip0$Variable.Name%>%as.list()) #List of weights, update as necessary

###All weight descriptions###
weight_descrip0_all <- data.frame()
if (nrow(weight_descrip0_all)<1){
  if (!regWgt %in% weight_descrip0_all$Variable.Name){
    log_debug("Region Weight not in weight_descrip0_all")
    weight_descrip0_all <- weight_descrip0_all %>%
      bind_rows(data.frame(Weight.Number=1,
                           Variable.Name=regWgt,
                           Description="Region Weight"))%>%
      arrange(Weight.Number) %>%
      mutate(Weight.Number = row_number())
    log_debug("Added dummy description to weight_descrip0_all")
  }
  #if (!stateWgt %in% weight_descrip0_all$Variable.Name){
  #  print("State Weight not in weight_descrip0_all")
  #}
}




##############################
#Pop groups
popGp_codes<-  data.frame(PARENT_POP_GROUP_DESC2=c("All cities 250,000 or over",
                                                   "Cities from 100,000 thru 249,999",
                                                   "Cities from 50,000 thru 99,999",
                                                   "Cities from 25,000 thru 49,999",
                                                   "Cities from 10,000 thru 24,999",
                                                   "Cities under 10,000",
                                                   "MSA Counties",
                                                   "Non-MSA Counties"
))

popGp_codes$nid <- seq.int(nrow(popGp_codes))+1

#Create Region Level Estimates row
nel <- data.frame("PARENT_POP_GROUP_DESC2" = "REGION LEVEL ESTIMATES", "nid" = 1)
popGp_codes_all<-dplyr::bind_rows (nel,popGp_codes)



curr_popGp<-c("REGION LEVEL ESTIMATES",
              "All cities 250,000 or over",
              "Cities from 100,000 thru 249,999",
              "Cities from 50,000 thru 99,999",
              "Cities from 25,000 thru 49,999",
              "Cities from 10,000 thru 24,999",
              "Cities under 10,000",
              "MSA Counties",
              "Non-MSA Counties"
)


#Replicate Weight Descriptions by Number of popGps+Region
di<-dim(popGp_codes_all)[1]
fin<-do.call("rbind", replicate(di, weight_descrip0, simplify = FALSE))
fin$nid<- as.numeric(ave(fin$Description, fin$Weight.Number, FUN = seq_along))


fin_all<-do.call("rbind", replicate(di, weight_descrip0_all, simplify = FALSE))
fin_all$nid<- as.numeric(ave(fin_all$Description, fin_all$Weight.Number, FUN = seq_along))


#Merge States and Weight Description for Summary Tables (for A, B, C,D)
popGp_codes_all_fin_a<-merge(popGp_codes_all,fin,by=c("nid"))
popGp_codes_all_fin_a$PARENT_POP_GROUP_DESC2_char<-ifelse(popGp_codes_all_fin_a$Weight.Number==1,as.character(popGp_codes_all_fin_a$PARENT_POP_GROUP_DESC2),"")
popGp_codes_all_fin<- popGp_codes_all_fin_a[order(popGp_codes_all_fin_a$nid,popGp_codes_all_fin_a$Weight.Number),]


popGp_codes_all_fin_all<-merge(popGp_codes_all,fin_all,by=c("nid"))
#popGp_codes_all_fin_all<-subset(popGp_codes_all_fin_all,PARENT_POP_GROUP_DESC2=="REGION LEVEL ESTIMATES" & Variable.Name %in% regWgt |PARENT_POP_GROUP_DESC2!="REGION LEVEL ESTIMATES"  & Variable.Name %in% regWgt)
popGp_codes_all_fin_all$GROUP_NAME_char<-#ifelse(
  #((popGp_codes_all_fin_all$Weight.Number==14 & popGp_codes_all_fin_all$state_name=="REGION LEVEL ESTIMATES")|
  # (popGp_codes_all_fin_all$Weight.Number==21 & popGp_codes_all_fin_all$state_name!="REGION LEVEL ESTIMATES")),
  as.character(popGp_codes_all_fin_all$PARENT_POP_GROUP_DESC2)#,"")

popGp_codes_all_fin_allt<-popGp_codes_all_fin_all
popGp_codes_all_fin_all<-subset(popGp_codes_all_fin_allt,PARENT_POP_GROUP_DESC2%in%curr_popGp)


##########For Summary Table A############
hcolNames_TabA=matrix(c("All Crime","All Violent",
                        "Murder", "Manslaughter", "Rape" ,"Robbery" ,"Assault" ,"Aggravated Assault", "Simple Assault", "All Property",
                        "Burglary", "Larceny",
                        "Vehicle Theft"),
                      ncol=13)
tableASummTitle=matrix(c("Relative Ratio Summary Table per Weight by State"))


hcolNames_TabA2=matrix(c("","Est.","SE","RSE(%)","Est.",""),nrow=1)
####Header Rows####
hcolNames_TabA1=matrix(c("Offense popGp","Weighted Total among NIBRS Reporters","SRS Total among all LEAs","Relaitve Bias(%)"),nrow=1)
hcolNames_TabA4_row<-data.frame("OffenseType"=c("   ", "All Crime","All Violent",
                                                "Murder", "Manslaughter", "Rape" ,"Robbery" ,"Assault" ,"   Aggravated Assault", "   Simple Assault", "All Property",
                                                "Burglary", "Larceny",
                                                "Vehicle Theft"),
                                Est=c("Est.",rep(" ",13)),
                                SE=c("SE",rep(" ",13)),
                                RSE=c("RSE(%)",rep(" ",13)),
                                Est2=c("Est.",rep(" ",13)),
                                BRC1=c(rep(" ",14)),
                                BRC2=c(rep(" ",14)))%>%mutate(RowValue = row_number())


hcolNames_TabA4_row<-data.frame("OffenseType"=c("   ", "All Crime","All Violent",
                                                "Murder", "Manslaughter", "Rape" ,"Robbery" ,"Assault" ,"   Aggravated Assault", "   Simple Assault", "All Property",
                                                "Burglary", "Larceny",
                                                "Vehicle Theft"),
                                Est=c("Est.",rep(" ",13)),
                                SE=c("SE",rep(" ",13)),
                                RSE=c("RSE(%)",rep(" ",13)),
                                Est2=c("Est.",rep(" ",13)),
                                BRC1=c(rep(" ",14)),
                                BRC2=c(rep(" ",14)))%>%mutate(RowValue = row_number())
hcolNames_TabA4_row<-subset(hcolNames_TabA4_row,RowValue>1)



finA<-do.call("rbind", replicate(di, hcolNames_TabA4_row, simplify = FALSE))
finA$nid<- ave(finA$RowValue, finA$RowValue, FUN = seq_along)


#Merge States and Weight Description for Summary Tables (for A, B, C,D)##
popGp_codes_all_fin_SummTabA1<-merge(popGp_codes_all,finA,by=c("nid"))
popGp_codes_all_fin_SummTabA1t<-popGp_codes_all_fin_SummTabA1
popGp_codes_all_fin_SummTabA1<-subset(popGp_codes_all_fin_SummTabA1t,PARENT_POP_GROUP_DESC2%in%curr_popGp)

popGp_codes_all_fin_SummTabA1$GROUP_NAME_char<-ifelse(popGp_codes_all_fin_SummTabA1$RowValue==2,as.character(popGp_codes_all_fin_SummTabA1$PARENT_POP_GROUP_DESC2),"")
popGp_codes_all_fin_SummTabA1<- popGp_codes_all_fin_SummTabA1[order(popGp_codes_all_fin_SummTabA1$nid,popGp_codes_all_fin_SummTabA1$RowValue),]

keepColsTabA<-c("GROUP_NAME_char", "OffenseType", "Est", "SE","RSE","Est2","BRC1","BRC2")
popGp_codes_all_fin_SummTabA<-popGp_codes_all_fin_SummTabA1[keepColsTabA]





##############################
#Types
type_codes<-  data.frame(AGENCY_TYPE_NAME=c(
  "City",
  "County",
  "University or College",
  "State Police",
  "Other State Agency",
  "Tribal",
  "Federal",
  "Other"))

type_codes$nid <- seq.int(nrow(type_codes))+max(popGp_codes_all_fin_SummTabA1$nid)

#Create Region Level Estimates row
nel <- data.frame("AGENCY_TYPE_NAME" = "REGION LEVEL ESTIMATES", "nid" = 1)
type_codes_all<-dplyr::bind_rows (nel,type_codes)


curr_type<-c("REGION LEVEL ESTIMATES",
             "City",
             "County",
             "University or College",
             "State Police",
             "Other State Agency",
             "Tribal",
             "Federal",
             "Other")


#Replicate Weight Descriptions by Number of Types+Region
di<-dim(type_codes_all)[1]
fin<-do.call("rbind", replicate(di, weight_descrip0, simplify = FALSE))
fin$nid<- as.numeric(ave(fin$Description, fin$Weight.Number, FUN = seq_along))
fin$nid<- case_when(fin$nid>1 ~ fin$nid+max(popGp_codes_all_fin_SummTabA1$nid)-1,
                    TRUE ~ fin$nid)


fin_all<-do.call("rbind", replicate(di, weight_descrip0_all, simplify = FALSE))
fin_all$nid<- as.numeric(ave(fin_all$Description, fin_all$Weight.Number, FUN = seq_along))
fin_all$nid<- case_when(fin_all$nid>1 ~ fin_all$nid+max(popGp_codes_all_fin_SummTabA1$nid)-1,
                        TRUE ~ fin_all$nid)


#Merge States and Weight Description for Summary Tables (for A, B, C,D)
type_codes_all_fin_a<-merge(type_codes_all,fin,by=c("nid"))
type_codes_all_fin_a$GROUP_NAME_char<-ifelse(type_codes_all_fin_a$Weight.Number==1,as.character(type_codes_all_fin_a$AGENCY_TYPE_NAME),"")
type_codes_all_fin<- type_codes_all_fin_a[order(type_codes_all_fin_a$nid,type_codes_all_fin_a$Weight.Number),]


type_codes_all_fin_all<-merge(type_codes_all,fin_all,by=c("nid"))
#type_codes_all_fin_all<-subset(type_codes_all_fin_all,AGENCY_TYPE_NAME=="REGION LEVEL ESTIMATES" & Variable.Name %in% regWgt |AGENCY_TYPE_NAME!="REGION LEVEL ESTIMATES"  & Variable.Name %in% regWgt)
type_codes_all_fin_all$GROUP_NAME_char<-#ifelse(
  #((type_codes_all_fin_all$Weight.Number==14 & type_codes_all_fin_all$state_name=="REGION LEVEL ESTIMATES")|
  # (type_codes_all_fin_all$Weight.Number==21 & type_codes_all_fin_all$state_name!="REGION LEVEL ESTIMATES")),
  as.character(type_codes_all_fin_all$AGENCY_TYPE_NAME)#,"")

type_codes_all_fin_allt<-type_codes_all_fin_all
type_codes_all_fin_all<-subset(type_codes_all_fin_allt,AGENCY_TYPE_NAME%in%curr_type)


##########For Summary Table A############
hcolNames_TabA=matrix(c("All Crime","All Violent",
                        "Murder", "Manslaughter", "Rape" ,"Robbery" ,"Assault" ,"Aggravated Assault", "Simple Assault", "All Property",
                        "Burglary", "Larceny",
                        "Vehicle Theft"),
                      ncol=13)
tableASummTitle=matrix(c("Relative Ratio Summary Table per Weight by State"))


hcolNames_TabA2=matrix(c("","Est.","SE","RSE(%)","Est.",""),nrow=1)
####Header Rows####
hcolNames_TabA1=matrix(c("Offense Type","Weighted Total among NIBRS Reporters","SRS Total among all LEAs","Relative Bias(%)"),nrow=1)
hcolNames_TabA4_row<-data.frame("OffenseType"=c("   ", "All Crime","All Violent",
                                                "Murder", "Manslaughter", "Rape" ,"Robbery" ,"Assault" ,"   Aggravated Assault", "   Simple Assault", "All Property",
                                                "Burglary", "Larceny",
                                                "Vehicle Theft"),
                                Est=c("Est.",rep(" ",13)),
                                SE=c("SE",rep(" ",13)),
                                RSE=c("RSE(%)",rep(" ",13)),
                                Est2=c("Est.",rep(" ",13)),
                                BRC1=c(rep(" ",14)),
                                BRC2=c(rep(" ",14)))%>%mutate(RowValue = row_number())


hcolNames_TabA4_row<-data.frame("OffenseType"=c("   ", "All Crime","All Violent",
                                                "Murder", "Manslaughter", "Rape" ,"Robbery" ,"Assault" ,"   Aggravated Assault", "   Simple Assault", "All Property",
                                                "Burglary", "Larceny",
                                                "Vehicle Theft"),
                                Est=c("Est.",rep(" ",13)),
                                SE=c("SE",rep(" ",13)),
                                RSE=c("RSE(%)",rep(" ",13)),
                                Est2=c("Est.",rep(" ",13)),
                                BRC1=c(rep(" ",14)),
                                BRC2=c(rep(" ",14)))%>%mutate(RowValue = row_number())
hcolNames_TabA4_row<-subset(hcolNames_TabA4_row,RowValue>1)



finA<-do.call("rbind", replicate(di, hcolNames_TabA4_row, simplify = FALSE))
finA$nid<- ave(finA$RowValue, finA$RowValue, FUN = seq_along)
finA$nid<- case_when(finA$nid>1 ~ finA$nid+as.integer(max(popGp_codes_all_fin_SummTabA1$nid))-1L,
                     TRUE ~ finA$nid)



#Merge States and Weight Description for Summary Tables (for A, B, C,D)##
type_codes_all_fin_SummTabA1<-merge(type_codes_all,finA,by=c("nid"))
type_codes_all_fin_SummTabA1t<-type_codes_all_fin_SummTabA1
type_codes_all_fin_SummTabA1<-subset(type_codes_all_fin_SummTabA1t,AGENCY_TYPE_NAME%in%curr_type)

type_codes_all_fin_SummTabA1$GROUP_NAME_char<-ifelse(type_codes_all_fin_SummTabA1$RowValue==2,as.character(type_codes_all_fin_SummTabA1$AGENCY_TYPE_NAME),"")
type_codes_all_fin_SummTabA1<- type_codes_all_fin_SummTabA1[order(type_codes_all_fin_SummTabA1$nid,type_codes_all_fin_SummTabA1$RowValue),]

keepColsTabA<-c("GROUP_NAME_char", "OffenseType", "Est", "SE","RSE","Est2","BRC1","BRC2")
type_codes_all_fin_SummTabA<-type_codes_all_fin_SummTabA1[keepColsTabA]

##############################
#Regions
region_codes<-  data.frame(REGION_NAME=c("Midwest",
                                         "Northeast",
                                         "South",
                                         "West"))

region_codes$nid <- seq.int(nrow(region_codes))+max(type_codes_all_fin_SummTabA1$nid)#+max(popGp_codes_all_fin_SummTabA1$nid)

#Create Region Level Estimates row
nel <- data.frame("REGION_NAME" = "REGION LEVEL ESTIMATES", "nid" = 1)
region_codes_all<-dplyr::bind_rows (nel,region_codes)


curr_region<-c("Midwest",
               "Northeast",
               "South",
               "West")


#Replicate Weight Descriptions by Number of Types+Region
di<-dim(region_codes_all)[1]
fin<-do.call("rbind", replicate(di, weight_descrip0, simplify = FALSE))
fin$nid<- as.numeric(ave(fin$Description, fin$Weight.Number, FUN = seq_along))
fin$nid<- case_when(fin$nid>1 ~ fin$nid+max(type_codes_all_fin_SummTabA1$nid)-1,#+max(popGp_codes_all_fin_SummTabA1$nid)
                    TRUE ~ fin$nid)


fin_all<-do.call("rbind", replicate(di, weight_descrip0_all, simplify = FALSE))
fin_all$nid<- as.numeric(ave(fin_all$Description, fin_all$Weight.Number, FUN = seq_along))
fin_all$nid<- case_when(fin_all$nid>1 ~ fin_all$nid+max(type_codes_all_fin_SummTabA1$nid)-1,#+max(popGp_codes_all_fin_SummTabA1$nid)
                        TRUE ~ fin_all$nid)


#Merge States and Weight Description for Summary Tables (for A, B, C,D)
region_codes_all_fin_a<-merge(region_codes_all,fin,by=c("nid"))
region_codes_all_fin_a$GROUP_NAME_char<-ifelse(region_codes_all_fin_a$Weight.Number==1,as.character(region_codes_all_fin_a$REGION_NAME),"")
region_codes_all_fin<- region_codes_all_fin_a[order(region_codes_all_fin_a$nid,region_codes_all_fin_a$Weight.Number),]


region_codes_all_fin_all<-merge(region_codes_all,fin_all,by=c("nid"))
#type_codes_all_fin_all<-subset(type_codes_all_fin_all,REGION_NAME=="REGION LEVEL ESTIMATES" & Variable.Name %in% regWgt |REGION_NAME!="REGION LEVEL ESTIMATES"  & Variable.Name %in% regWgt)
region_codes_all_fin_all$GROUP_NAME_char<-#ifelse(
  #((type_codes_all_fin_all$Weight.Number==14 & type_codes_all_fin_all$state_name=="REGION LEVEL ESTIMATES")|
  # (type_codes_all_fin_all$Weight.Number==21 & type_codes_all_fin_all$state_name!="REGION LEVEL ESTIMATES")),
  as.character(region_codes_all_fin_all$REGION_NAME)#,"")

region_codes_all_fin_allt<-region_codes_all_fin_all
region_codes_all_fin_all<-subset(region_codes_all_fin_allt,REGION_NAME%in%curr_region)


##########For Summary Table A############
hcolNames_TabA=matrix(c("All Crime","All Violent",
                        "Murder", "Manslaughter", "Rape" ,"Robbery" ,"Assault" ,"Aggravated Assault", "Simple Assault", "All Property",
                        "Burglary", "Larceny",
                        "Vehicle Theft"),
                      ncol=13)
tableASummTitle=matrix(c("Relative Ratio Summary Table per Weight by State"))


hcolNames_TabA2=matrix(c("","Est.","SE","RSE(%)","Est.",""),nrow=1)
####Header Rows####
hcolNames_TabA1=matrix(c("Offense Type","Weighted Total among NIBRS Reporters","SRS Total among all LEAs","Relative Bias(%)"),nrow=1)
hcolNames_TabA4_row<-data.frame("OffenseType"=c("   ", "All Crime","All Violent",
                                                "Murder", "Manslaughter", "Rape" ,"Robbery" ,"Assault" ,"   Aggravated Assault", "   Simple Assault", "All Property",
                                                "Burglary", "Larceny",
                                                "Vehicle Theft"),
                                Est=c("Est.",rep(" ",13)),
                                SE=c("SE",rep(" ",13)),
                                RSE=c("RSE(%)",rep(" ",13)),
                                Est2=c("Est.",rep(" ",13)),
                                BRC1=c(rep(" ",14)),
                                BRC2=c(rep(" ",14)))%>%mutate(RowValue = row_number())


hcolNames_TabA4_row<-data.frame("OffenseType"=c("   ", "All Crime","All Violent",
                                                "Murder", "Manslaughter", "Rape" ,"Robbery" ,"Assault" ,"   Aggravated Assault", "   Simple Assault", "All Property",
                                                "Burglary", "Larceny",
                                                "Vehicle Theft"),
                                Est=c("Est.",rep(" ",13)),
                                SE=c("SE",rep(" ",13)),
                                RSE=c("RSE(%)",rep(" ",13)),
                                Est2=c("Est.",rep(" ",13)),
                                BRC1=c(rep(" ",14)),
                                BRC2=c(rep(" ",14)))%>%mutate(RowValue = row_number())
hcolNames_TabA4_row<-subset(hcolNames_TabA4_row,RowValue>1)



finA<-do.call("rbind", replicate(di, hcolNames_TabA4_row, simplify = FALSE))
finA$nid<- ave(finA$RowValue, finA$RowValue, FUN = seq_along)
finA$nid<- case_when(finA$nid>1 ~ finA$nid+as.integer(max(type_codes_all_fin_SummTabA1$nid))-1L,
                     TRUE ~ finA$nid)



#Merge States and Weight Description for Summary Tables (for A, B, C,D)##
region_codes_all_fin_SummTabA1<-merge(region_codes_all,finA,by=c("nid"))
region_codes_all_fin_SummTabA1t<-region_codes_all_fin_SummTabA1
region_codes_all_fin_SummTabA1<-subset(region_codes_all_fin_SummTabA1t,REGION_NAME%in%curr_region)

region_codes_all_fin_SummTabA1$GROUP_NAME_char<-ifelse(region_codes_all_fin_SummTabA1$RowValue==2,as.character(region_codes_all_fin_SummTabA1$REGION_NAME),"")

region_codes_all_fin_SummTabA1<- region_codes_all_fin_SummTabA1[order(region_codes_all_fin_SummTabA1$nid,region_codes_all_fin_SummTabA1$RowValue),]

keepColsTabA<-c("GROUP_NAME_char", "OffenseType", "Est", "SE","RSE","Est2","BRC1","BRC2")
region_codes_all_fin_SummTabA<-region_codes_all_fin_SummTabA1[keepColsTabA]




#################
groupings_all_fin_SummTabA1 <- full_join(popGp_codes_all_fin_SummTabA1,type_codes_all_fin_SummTabA1) %>%
  full_join(region_codes_all_fin_SummTabA1)

groupings_all_fin_SummTabA1 <- bind_rows(groupings_all_fin_SummTabA1 %>%
                                     mutate(state_name="MIDWEST",
                                            state_abbr="MW"),
                                     groupings_all_fin_SummTabA1 %>%
                                       mutate(state_name="NORTHEAST",
                                              state_abbr="NE"),
                                   groupings_all_fin_SummTabA1 %>%
                                     mutate(state_name="SOUTH",
                                            state_abbr="S"),
                                   groupings_all_fin_SummTabA1 %>%
                                     mutate(state_name="WEST",
                                            state_abbr="W")) %>%
  mutate(state_name_char=ifelse(nid%%(nrow(.)/4)==1 & RowValue==2,state_name,""))
groupings_all_fin_SummTabA<-groupings_all_fin_SummTabA1[c("state_name_char",keepColsTabA)]


groupings_all_fin_all <- full_join(popGp_codes_all_fin_all,type_codes_all_fin_all) %>%
  full_join(region_codes_all_fin_all) %>%
  subset(Variable.Name==regWgt)

groupings_all_fin_all <- bind_rows(groupings_all_fin_all %>%
                                     mutate(state_name="MIDWEST",
                                            state_abbr="MW"),
                                   groupings_all_fin_all %>%
                                     mutate(state_name="NORTHEAST",
                                            state_abbr="NE"),
                                   groupings_all_fin_all %>%
                                     mutate(state_name="SOUTH",
                                            state_abbr="S"),
                                   groupings_all_fin_all %>%
                                     mutate(state_name="WEST",
                                            state_abbr="W")) %>%
  mutate(state_name_char=ifelse(nid%%(nrow(.)/4)==1,state_name,""))

#output dummy file with all groupings by weight combos
#write.csv(file="//rtpnfil02/0216153_NIBRS/03_SamplingPlan/JD/21-Clean-Weighting-2019/Output/TableADummy.csv", x=type_codes_all_fin_SummTabA1)

write_dot_csv_logging(file=file.path(output_weighting_tableshell_folder,"TableAGpRegionDummy.csv"),groupings_all_fin_SummTabA1)









#Merged Column Name
RelBiasCtype=matrix(c("Relative Bias by Crime Type"),ncol=1)


#Footnote
footnote=matrix(c("*Indicates Bias Ratio>5%", "--Crime type not applicable for applied weight"),nrow=2)


######################################
# Table A shell
######################################

mystyle<-createStyle(fontSize = 11,border = c("top", "bottom", "left", "right"),borderStyle = "thin",halign = "center",valign = "center")
mystyleL<-createStyle(fontSize = 11,border = c("top", "bottom", "left", "right"),borderStyle = "thin",halign = "left",valign = "center")
headerStyle <- createStyle(fontSize = 11, fontColour = "#FFFFFF",  fgFill = "#4F81BD", border=c("top", "bottom", "left", "right"), borderColour = "#4F81BD", textDecoration = "bold")



fileoutTabA<-file.path(output_weighting_tableshell_folder,"TableA_Groupings_Region_Shell.xlsx")

#RelBiasCtype
#state_name_abb_fin
#hcolNames_TabA



######Table A Workbook Creation######
wbShell_TabA_Region<- createWorkbook()



######Table A shell State -Summary######
log_debug("Writing sheet Summary_Region_TabA_Ex1")

addWorksheet(wbShell_TabA_Region,"Summary_Region_TabA_Ex1",gridLines = T) #comment out after creating

removeCellMerge(wbShell_TabA_Region,"Summary_Region_TabA_Ex1", cols = 4:15, rows = 6:6)


#Table Title
writeData(wbShell_TabA_Region,sheet="Summary_Region_TabA_Ex1", x=tableASummTitle,withFilter = F,colNames = FALSE, startRow =1, startCol=1, headerStyle=headerStyle )



#Header
writeData(wbShell_TabA_Region,sheet="Summary_Region_TabA_Ex1", x=RelBiasCtype,withFilter = F,colNames = FALSE, startRow =6, startCol=4)
mergeCells(wbShell_TabA_Region, "Summary_Region_TabA_Ex1", cols = 4:15, rows = 6:6)

#Crime Type
writeData(wbShell_TabA_Region,sheet="Summary_Region_TabA_Ex1", x=hcolNames_TabA,withFilter = F,colNames = FALSE, startRow =7,startCol=4)

#State by Weight
writeData(wbShell_TabA_Region,sheet="Summary_Region_TabA_Ex1", x=groupings_all_fin_all[,c("state_name_char","GROUP_NAME_char", "Description") ],withFilter = F,colNames = FALSE, startRow =8,startCol=1)


addStyle(wbShell_TabA_Region,sheet = "Summary_Region_TabA_Ex1",mystyle,rows =6:7 ,cols = 1:16,gridExpand = T) #Headers
addStyle(wbShell_TabA_Region,sheet = "Summary_Region_TabA_Ex1",mystyle,rows =8:319 ,cols = 1:1,gridExpand = T) #State Names
addStyle(wbShell_TabA_Region,sheet = "Summary_Region_TabA_Ex1",mystyleL,rows =8:319 ,cols = 2:16,gridExpand = T) #Weight Descriptions

setColWidths(wbShell_TabA_Region, sheet = "Summary_Region_TabA_Ex1", cols = 1:1,widths =30)
setColWidths(wbShell_TabA_Region, sheet = "Summary_Region_TabA_Ex1", cols = 2:2,widths =30)
setColWidths(wbShell_TabA_Region, sheet = "Summary_Region_TabA_Ex1", cols = 3:3,widths =30)
setColWidths(wbShell_TabA_Region, sheet = "Summary_Region_TabA_Ex1", cols = 4:16,widths =30)



######Table A shell State -State x OffenseType Table per Weight######
R=0 #Counter for loop
mystyleA<-createStyle(fontSize = 11,border = c("top", "bottom", "left", "right"),borderStyle = "thin",valign = "center") #Different styles for header vs rest of rows
mystyleA1<-createStyle(fontSize = 11,border = c("top", "bottom", "left", "right"),borderStyle = "thin",valign = "center",halign = "right") #Different styles for header vs rest of rows
mystyleA2<-createStyle(fontSize = 11,border = c("top", "bottom", "left", "right"),borderStyle = "thin",halign = "left",valign = "center")
headerStyle <- createStyle(fontSize = 11, fontColour = "#FFFFFF",  fgFill = "#4F81BD", border=c("top", "bottom", "left", "right"), borderColour = "#4F81BD", textDecoration = "bold")


for(i in 1:length(weight_lists)){
  R=R+1
  log_debug(paste0("Writing sheet ",weight_lists[R]))
  addWorksheet(wbShell_TabA_Region,weight_lists[R],gridLines = T)

  removeCellMerge(wbShell_TabA_Region, weight_lists[[R]], cols = 2:4, rows = 7:7) # removes any intersecting merges
  removeCellMerge(wbShell_TabA_Region, weight_lists[[R]], cols = 6:7, rows = 7:7)

  #Weight Description
  writeData(wbShell_TabA_Region,sheet=weight_lists[[R]], x=weight_list_descrip[[R]],withFilter = F,colNames = FALSE, startRow =1, startCol=1, headerStyle=headerStyle )

  #Footnotes
  writeData(wbShell_TabA_Region,sheet=weight_lists[[R]], x=footnote,withFilter = F,colNames = FALSE, startRow =3, startCol=1)

  #Header
  writeData(wbShell_TabA_Region,sheet=weight_lists[[R]], x=hcolNames_TabA1[,1],withFilter = F,colNames = FALSE, startRow =6, startCol=3, headerStyle=headerStyle )
  writeData(wbShell_TabA_Region,sheet=weight_lists[[R]], x=hcolNames_TabA1[,2],withFilter = F,colNames = FALSE, startRow =6, startCol=4, headerStyle=headerStyle)
  mergeCells(wbShell_TabA_Region, weight_lists[[R]], cols=4:6, rows=6:6)
  writeData(wbShell_TabA_Region,sheet=weight_lists[[R]], x=hcolNames_TabA1[,3],withFilter = F,colNames = FALSE, startRow =6,startCol=7, headerStyle=headerStyle)
  writeData(wbShell_TabA_Region,sheet=weight_lists[[R]], x=hcolNames_TabA1[,4],withFilter = F,colNames = FALSE, startRow =6,startCol=8, headerStyle=headerStyle)
  mergeCells(wbShell_TabA_Region, weight_lists[[R]], cols=8:9, rows=6:6)

  #Header2
  writeData(wbShell_TabA_Region,sheet=weight_lists[[R]], x=hcolNames_TabA2,withFilter = F,colNames = FALSE, startRow =7, startCol=3,headerStyle=headerStyle)


  #Data Labels
  if (str_detect(weight_lists[[R]],regWgt)){
    keepRows <- 1:nrow(groupings_all_fin_SummTabA)#14:nrow(groupings_all_fin_SummTabA)
  } #else if (str_detect(weight_lists[[R]],stateWgt)){
  #keepRows <- 1:nrow(groupings_all_fin_SummTabA)#14:nrow(groupings_all_fin_SummTabA)
  #}

  writeData(wbShell_TabA_Region,sheet=weight_lists[[R]], x=groupings_all_fin_SummTabA[keepRows,],withFilter = F,colNames = FALSE, startRow =8, headerStyle=headerStyle)

  addStyle(wbShell_TabA_Region,weight_lists[[R]],mystyleA2,rows =6:6 ,cols = 2:9,gridExpand = T) #Header
  addStyle(wbShell_TabA_Region,weight_lists[[R]],mystyleA2,rows =7:(7+length(keepRows)) ,cols = 1:9,gridExpand = T) #Header

  setColWidths(wbShell_TabA_Region, weight_lists[[R]], cols = 1:9,widths = c(40,30,30,20,20,20,30,10,10))


}
saveWorkbook(wbShell_TabA_Region,file =fileoutTabA ,overwrite = T)
log_info("Finished 04_TableShell_Groupings_Region.R\n\n")
