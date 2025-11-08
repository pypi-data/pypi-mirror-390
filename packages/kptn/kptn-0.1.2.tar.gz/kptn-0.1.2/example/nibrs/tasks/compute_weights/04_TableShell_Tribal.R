#########################################################################
#Program      : 04_TableShell_Tribal
#Description  : Create table shell for Table A within Appendix for tribal LEAs
#
#Project      : NCS-X NIBRS Estimation Project
#Authors      : JD Bunker, Philip Lee, Taylor Lewis, Nicole Mack, Grant Swigart
#Date         :
#Modified     :
#Notes:
#########################################################################
library(readxl)
library(datasets)
library(tidyverse)
library(survey)
library(Hmisc)
library(openxlsx)
library(foreign)
library(srvyr)
library(haven)
library(rlang)

######################################
# Text applicable to all tables
######################################

log_info("Running 04_TableShell_Tribal.R")

##Get Weight Descriptions
tribalWgt <- "TribalWgt" #Tribal weight var
weight_descrip0 <- data.frame()
if (nrow(weight_descrip0)<1){
  if (!tribalWgt %in% weight_descrip0$Variable.Name){
    log_debug("Tribal Weight not in weight_descrip0")
    weight_descrip0 <- weight_descrip0 %>%
      bind_rows(data.frame(Weight.Number=1,
                           Variable.Name=tribalWgt,
                           Description="Tribal Weight"))%>%
      arrange(Weight.Number)   %>%
      mutate(Weight.Number = row_number())
    log_debug("Added dummy description to weight_descrip0")
  }
}

weight_list_descrip<-(weight_descrip0$Description%>%as.list()) #List of weight description, update as necessary
weight_lists<-(weight_descrip0$Variable.Name%>%as.list()) #List of weights, update as necessary

###All weight descriptions###
weight_descrip0_all <- data.frame()
if (nrow(weight_descrip0_all)<1){
  if (!tribalWgt %in% weight_descrip0_all$Variable.Name){
    log_debug("Tribal Weight not in weight_descrip0_all")
    weight_descrip0_all <- weight_descrip0_all %>%
      bind_rows(data.frame(Weight.Number=1,
                           Variable.Name=tribalWgt,
                           Description="Tribal Weight")) %>%
      arrange(Weight.Number) %>%
      mutate(Weight.Number = row_number())
    log_debug("Added dummy description to weight_descrip0_all")
  }
}
#Create National Level Estimates row
nel <- data.frame("state_name" = "NATIONAL LEVEL ESTIMATES", "state_abbr" = "NEL", "nid" = 1)
state_name_abb<-dplyr::bind_rows (nel)


curr_state<-c("NATIONAL LEVEL ESTIMATES")



#Replicate Weight Descriptions by Number of States+National
di<-dim(state_name_abb)[1]
fin<-do.call("rbind", replicate(di, weight_descrip0, simplify = FALSE))
fin$nid<- as.numeric(ave(fin$Description, fin$Weight.Number, FUN = seq_along))


fin_all<-do.call("rbind", replicate(di, weight_descrip0_all, simplify = FALSE))
fin_all$nid<- as.numeric(ave(fin_all$Description, fin_all$Weight.Number, FUN = seq_along))


#Merge States and Weight Description for Summary Tables (for A, B, C,D)
state_name_abb_fin_a<-merge(state_name_abb,fin,by=c("nid"))
state_name_abb_fin_a$state_name_char<-ifelse(state_name_abb_fin_a$Weight.Number==1,as.character(state_name_abb_fin_a$state_name),"")
state_name_abb_fin<- state_name_abb_fin_a[order(state_name_abb_fin_a$nid,state_name_abb_fin_a$Weight.Number),]


state_name_abb_fin_all<-merge(state_name_abb,fin_all,by=c("nid"))
state_name_abb_fin_all<-subset(state_name_abb_fin_all,state_name=="NATIONAL LEVEL ESTIMATES" & Variable.Name %in% tribalWgt)
state_name_abb_fin_all$state_name_char<-#ifelse(
  #((state_name_abb_fin_all$Weight.Number==14 & state_name_abb_fin_all$state_name=="NATIONAL LEVEL ESTIMATES")|
  # (state_name_abb_fin_all$Weight.Number==21 & state_name_abb_fin_all$state_name!="NATIONAL LEVEL ESTIMATES")),
  as.character(state_name_abb_fin_all$state_name)#,"")

state_name_abb_fin_allt<-state_name_abb_fin_all
state_name_abb_fin_all<-subset(state_name_abb_fin_allt,state_name%in%curr_state)


##########For Summary Table A############
hcolNames_TabA=matrix(c("All Crime","All Violent",
                        "Murder", "Manslaughter", "Rape" ,"Robbery" ,"Assault" ,"Aggravated Assault", "Simple Assault", "All Property",
                        "Burglary", "Larceny",
                        "Vehicle Theft"),
                      ncol=13)
tableASummTitle=matrix(c("Relative Ratio Summary Table per Weight by State"))


hcolNames_TabA2=matrix(c("","Est.","SE","RSE(%)","Est.",""),nrow=1)
####Header Rows####
hcolNames_TabA1=matrix(c("Offense Type","Weighted Total among NIBRS Reporters","SRS Total among all LEAs","Relaitve Bias(%)"),nrow=1)
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
state_name_abb_fin_SummTabA1<-merge(state_name_abb,finA,by=c("nid"))
state_name_abb_fin_SummTabA1t<-state_name_abb_fin_SummTabA1
state_name_abb_fin_SummTabA1<-subset(state_name_abb_fin_SummTabA1t,state_name%in%curr_state)

state_name_abb_fin_SummTabA1$state_name_char<-ifelse(state_name_abb_fin_SummTabA1$RowValue==2,as.character(state_name_abb_fin_SummTabA1$state_name),"")
state_name_abb_fin_SummTabA1<- state_name_abb_fin_SummTabA1[order(state_name_abb_fin_SummTabA1$nid,state_name_abb_fin_SummTabA1$RowValue),]

keepColsTabA<-c("state_name_char", "OffenseType", "Est", "SE","RSE","Est2","BRC1","BRC2")
state_name_abb_fin_SummTabA<-state_name_abb_fin_SummTabA1[keepColsTabA]

#output dummy file with all state by weight combos
#write.csv(file="//rtpnfil02/0216153_NIBRS/03_SamplingPlan/JD/22-Clean-Weighting-2020/TableShells/TableADummy.csv", x=state_name_abb_fin_SummTabA1)

#MAY CHANGE

write_dot_csv_logging(file=file.path(output_weighting_tableshell_folder,"TableATribalDummy.csv"),state_name_abb_fin_SummTabA1)




######################################
# Table A shell Tribal
######################################
#Merged Column Name
RelBiasCtype=matrix(c("Relative Bias by Crime Type"),ncol=1)


#Footnote
footnote=matrix(c("*Indicates Bias Ratio>5%", "--Crime type not applicable for applied weight"),nrow=2)

mystyle<-createStyle(fontSize = 11,border = c("top", "bottom", "left", "right"),borderStyle = "thin",halign = "center",valign = "center")
mystyleL<-createStyle(fontSize = 11,border = c("top", "bottom", "left", "right"),borderStyle = "thin",halign = "left",valign = "center")
headerStyle <- createStyle(fontSize = 11, fontColour = "#FFFFFF",  fgFill = "#4F81BD", border=c("top", "bottom", "left", "right"), borderColour = "#4F81BD", textDecoration = "bold")



fileoutTabA<-file.path(output_weighting_tableshell_folder,"TableA_Tribal_Shell.xlsx")

#RelBiasCtype
#state_name_abb_fin
#hcolNames_TabA



######Table A Workbook Creation######
wbShell_TabA_Tribal<- createWorkbook()



######Table A shell State -Summary######
log_debug("Writing sheet Summary_Tribal_TabA_Ex1")

addWorksheet(wbShell_TabA_Tribal,"Summary_Tribal_TabA_Ex1",gridLines = T) #comment out after creating

removeCellMerge(wbShell_TabA_Tribal,"Summary_Tribal_TabA_Ex1", cols = 3:15, rows = 6:6)


#Table Title
writeData(wbShell_TabA_Tribal,sheet="Summary_Tribal_TabA_Ex1", x=tableASummTitle,withFilter = F,colNames = FALSE, startRow =1, startCol=1, headerStyle=headerStyle )



#Header
writeData(wbShell_TabA_Tribal,sheet="Summary_Tribal_TabA_Ex1", x=RelBiasCtype,withFilter = F,colNames = FALSE, startRow =6, startCol=3)
mergeCells(wbShell_TabA_Tribal, "Summary_Tribal_TabA_Ex1", cols = 3:15, rows = 6:6)

#Crime Type
writeData(wbShell_TabA_Tribal,sheet="Summary_Tribal_TabA_Ex1", x=hcolNames_TabA,withFilter = F,colNames = FALSE, startRow =7,startCol=3)

#State by Weight
writeData(wbShell_TabA_Tribal,sheet="Summary_Tribal_TabA_Ex1", x=state_name_abb_fin_all[,c("state_name_char", "Description") ],withFilter = F,colNames = FALSE, startRow =8,startCol=1)


addStyle(wbShell_TabA_Tribal,sheet = "Summary_Tribal_TabA_Ex1",mystyle,rows =6:7 ,cols = 1:16,gridExpand = T) #Headers
addStyle(wbShell_TabA_Tribal,sheet = "Summary_Tribal_TabA_Ex1",mystyle,rows =8:319 ,cols = 1:1,gridExpand = T) #State Names
addStyle(wbShell_TabA_Tribal,sheet = "Summary_Tribal_TabA_Ex1",mystyleL,rows =8:319 ,cols = 2:16,gridExpand = T) #Weight Descriptions

setColWidths(wbShell_TabA_Tribal, sheet = "Summary_Tribal_TabA_Ex1", cols = 1:1,widths =30)
setColWidths(wbShell_TabA_Tribal, sheet = "Summary_Tribal_TabA_Ex1", cols = 2:2,widths =50)
setColWidths(wbShell_TabA_Tribal, sheet = "Summary_Tribal_TabA_Ex1", cols = 3:16,widths =30)



######Table A shell State -State x OffenseType Table per Weight######
R=0 #Counter for loop
mystyleA<-createStyle(fontSize = 11,border = c("top", "bottom", "left", "right"),borderStyle = "thin",valign = "center") #Different styles for header vs rest of rows
mystyleA1<-createStyle(fontSize = 11,border = c("top", "bottom", "left", "right"),borderStyle = "thin",valign = "center",halign = "right") #Different styles for header vs rest of rows
mystyleA2<-createStyle(fontSize = 11,border = c("top", "bottom", "left", "right"),borderStyle = "thin",halign = "left",valign = "center")
headerStyle <- createStyle(fontSize = 11, fontColour = "#FFFFFF",  fgFill = "#4F81BD", border=c("top", "bottom", "left", "right"), borderColour = "#4F81BD", textDecoration = "bold")


for(i in 1:length(weight_lists)){
  R=R+1
  log_debug(paste0("Writing sheet ",weight_lists[R]))
  addWorksheet(wbShell_TabA_Tribal,weight_lists[R],gridLines = T)
  
  removeCellMerge(wbShell_TabA_Tribal, weight_lists[[R]], cols = 2:4, rows = 7:7) # removes any intersecting merges
  removeCellMerge(wbShell_TabA_Tribal, weight_lists[[R]], cols = 6:7, rows = 7:7)
  
  #Weight Description
  writeData(wbShell_TabA_Tribal,sheet=weight_lists[[R]], x=weight_list_descrip[[R]],withFilter = F,colNames = FALSE, startRow =1, startCol=1, headerStyle=headerStyle )
  
  #Footnotes
  writeData(wbShell_TabA_Tribal,sheet=weight_lists[[R]], x=footnote,withFilter = F,colNames = FALSE, startRow =3, startCol=1)
  
  #Header
  writeData(wbShell_TabA_Tribal,sheet=weight_lists[[R]], x=hcolNames_TabA1[,1],withFilter = F,colNames = FALSE, startRow =6, startCol=2, headerStyle=headerStyle )
  writeData(wbShell_TabA_Tribal,sheet=weight_lists[[R]], x=hcolNames_TabA1[,2],withFilter = F,colNames = FALSE, startRow =6, startCol=3, headerStyle=headerStyle)
  mergeCells(wbShell_TabA_Tribal, weight_lists[[R]], cols=3:5, rows=6:6)
  writeData(wbShell_TabA_Tribal,sheet=weight_lists[[R]], x=hcolNames_TabA1[,3],withFilter = F,colNames = FALSE, startRow =6,startCol=6, headerStyle=headerStyle)
  writeData(wbShell_TabA_Tribal,sheet=weight_lists[[R]], x=hcolNames_TabA1[,4],withFilter = F,colNames = FALSE, startRow =6,startCol=7, headerStyle=headerStyle)
  mergeCells(wbShell_TabA_Tribal, weight_lists[[R]], cols=7:8, rows=6:6)
  
  #Header2
  writeData(wbShell_TabA_Tribal,sheet=weight_lists[[R]], x=hcolNames_TabA2,withFilter = F,colNames = FALSE, startRow =7, startCol=2,headerStyle=headerStyle)
  
  
  #Data Labels
  if (str_detect(weight_lists[[R]],tribalWgt)){
    keepRows <- 1:13
  } #else if (str_detect(weight_lists[[R]],stateWgt)){
  #keepRows <- 14:nrow(state_name_abb_fin_SummTabA)
  #}
  
  writeData(wbShell_TabA_Tribal,sheet=weight_lists[[R]], x=state_name_abb_fin_SummTabA[keepRows,],withFilter = F,colNames = FALSE, startRow =8, headerStyle=headerStyle)
  
  addStyle(wbShell_TabA_Tribal,weight_lists[[R]],mystyleA2,rows =6:6 ,cols = 2:8,gridExpand = T) #Header
  addStyle(wbShell_TabA_Tribal,weight_lists[[R]],mystyleA2,rows =7:(7+length(keepRows)) ,cols = 1:8,gridExpand = T) #Header
  
  setColWidths(wbShell_TabA_Tribal, weight_lists[[R]], cols = 1:8,widths = c(40,30,20,20,20,30,10,10))
  
  
}
saveWorkbook(wbShell_TabA_Tribal,file =fileoutTabA ,overwrite = T)
log_info("Finished 04_TableShell_Tribal.R\n\n")