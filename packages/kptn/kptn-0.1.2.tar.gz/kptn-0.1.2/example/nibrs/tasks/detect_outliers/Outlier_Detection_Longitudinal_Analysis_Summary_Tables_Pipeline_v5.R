
## Read in NIBRS data 

#```{r loadData,warning=FALSE,message=FALSE,results=FALSE}
library(tidyverse)
library(openxlsx)
library(ggplot2)
#library(dtw)
#install.packages('factoextra')
library(factoextra)
library(data.table)
library(fpc)
library(moments)
library(DT)


## Get task dataset
#```{r taskDat}

taskDat <- nibrs_allYrs_long2 %>%
  #subset(meanCount_allC_allYrs>50) %>%
  subset(!is.na(count_allC)) %>%
  subset(nMonths_allC_allYrs>=12) %>%
  select(ori,month_num_abs,repMonth_num,ucr_agency_name,nibrs_agn_population,
         rtiGroup_code,rtiGroup_desc,rtiGroups_allYrs_desc,
         popGroup_code,
         nibrs_agn_agency_type_name,
         matches("(count|crimeRate|percentile)_")) %>%
  #mutate(crimeVal=count_allC,
  #       crimeVar="count_allC") %>%
  #mutate(shape=rtiGroup_desc %>% as.character() %>% 
  #         str_replace_all(string=.,
  #                         pattern=c("(: |counties )"),
  #                         replacement=c("\\1\n"))) %>%
  arrange(ori,month_num_abs) %>%
  mutate(nibrs_agn_agency_type_name=factor(nibrs_agn_agency_type_name,
                                           levels=c("City","County","State Police",
                                                    "Other State Agency","University or College",
                                                    "Tribal","Federal","Other")))


oriList <- taskDat$ori %>% unique()

nORI <- length(oriList)
#```


#Dummy rows
dummyRows <- data.frame(rowGp="Dummy",
                        rowGpNum=c(1.5,2.5,3.5),
                        rowLvl="Dummy",
                        nORI_c1=NA_real_,
                        nORI_c2=NA_real_,
                        nORI_c3=NA_real_,
                        nORI_c4=NA_real_,
                        nORI_c5=NA_real_,
                        nORI_c6=NA_real_,
                        nORI_c7=NA_real_,
                        nORI_c8=NA_real_,
                        nORI_c9=NA_real_)

dummyRowsMonths <- data.frame(rowGp="Dummy",
                        rowGpNum=c(1.5,2.5,3.5),
                        rowLvl="Dummy",
                        nMonths_c1=NA_real_,
                        nMonths_c2=NA_real_,
                        nMonths_c3=NA_real_,
                        nMonths_c4=NA_real_,
                        nMonths_c5=NA_real_,
                        nMonths_c6=NA_real_)

#Function to create longitudinal table
#By LEA
longSummaryByType <- function(dat,countVar,dummy=dummyRows){
  ################################
  #Total column
  countVar <- enquo(countVar)
  tblDat <- dat %>% 
    mutate(one=1) %>%
    group_by(ori,cluster_novel) %>%
    mutate(minorHigh_novel_cy=cluster_novel==2 & median_novel>medianOth_k2,
           minorLow_novel_cy=cluster_novel==2 & median_novel<medianOth_k2) %>%
    group_by(ori) %>%
    mutate(minorHigh_novel_cy=any(minorHigh_novel_cy),
           minorLow_novel_cy=any(minorLow_novel_cy),
           nOutlier_novel_cy=sum(str_detect(outlier_novel,"green",negate=TRUE),na.rm=TRUE),
           nOutlier_red_novel_cy=sum(str_detect(outlier_novel,"red"),na.rm=TRUE),
           nOutlier_orange_novel_cy=sum(str_detect(outlier_novel,"orange"),na.rm=TRUE),
           nOutlier_blue_novel_cy=sum(str_detect(outlier_novel,"blue"),na.rm=TRUE),
           nOutlier_brown_novel_cy=sum(str_detect(outlier_novel,"brown"),na.rm=TRUE)) %>%
    ungroup() %>%
    mutate(c1=TRUE,
           c2=nCluster_novel>1,
           c3=minorHigh_novel_cy,
           c4=minorLow_novel_cy,
           c5=nOutlier_novel_cy==0,
           c6=nOutlier_red_novel_cy>=1,
           c7=nOutlier_orange_novel_cy>=1,
           c8=nOutlier_blue_novel_cy>=1,
           c9=nOutlier_brown_novel_cy>=1) %>%
    select(ori,one,nibrs_agn_agency_type_name,popGroup_code,
           #sum_count_allC_cat_cy,
           mean_count_allC_cat_cy,
           nMonth_all,
           matches("^c\\d$")) %>%
    subset(duplicated(.)==FALSE)
  
  #Overall
  table_r1 <- tblDat %>% 
    select(ori,one,matches("^c\\d$")) %>%
    subset(duplicated(.)==FALSE) %>%
    group_by(one,.drop=FALSE) %>%
    dplyr::summarize(across(matches("^c\\d$"),
                            sum,
                            .names="nORI_{.col}")) %>%
    mutate(rowGp="Overall",
           rowGpNum=1,
           rowLvl="Overall") %>%
    select(rowGp,rowGpNum,rowLvl,matches("^nORI_c\\d$"))
  
  #Agency type rows
  table_r2 <- tblDat %>% 
    select(ori,nibrs_agn_agency_type_name,matches("^c\\d$")) %>%
    subset(duplicated(.)==FALSE) %>%
    group_by(nibrs_agn_agency_type_name,.drop=FALSE) %>%
    dplyr::summarize(across(matches("^c\\d$"),
                            sum,
                            .names="nORI_{.col}")) %>%
    mutate(rowGp="Agency type",
           rowGpNum=2,
           rowLvl=as.character(nibrs_agn_agency_type_name))%>%
    select(rowGp,rowGpNum,rowLvl,matches("^nORI_c\\d$"))
  
  table_r3 <- tblDat %>% 
    select(ori,popGroup_code,matches("^c\\d$")) %>%
    subset(duplicated(.)==FALSE) %>%
    group_by(popGroup_code,.drop=FALSE) %>%
    dplyr::summarize(across(matches("^c\\d$"),
                            sum,
                            .names="nORI_{.col}")) %>%
    mutate(rowGp="Population",
           rowGpNum=3,
           rowLvl=as.character(popGroup_code))%>%
    select(rowGp,rowGpNum,rowLvl,matches("^nORI_c\\d$"))
  
  table_r4 <- tblDat %>% 
    #select(ori,sum_count_allC_cat_cy,matches("^c\\d$")) %>%
    select(ori,mean_count_allC_cat_cy,matches("^c\\d$")) %>%
    subset(duplicated(.)==FALSE) %>%
    #group_by(sum_count_allC_cat_cy,.drop=FALSE) %>%
    group_by(mean_count_allC_cat_cy,.drop=FALSE) %>%
    dplyr::summarize(across(matches("^c\\d$"),
                            sum,
                            .names="nORI_{.col}")) %>%
    mutate(rowGp="Total Crime",
           rowGpNum=4,
           #rowLvl=as.character(sum_count_allC_cat_cy))%>%
           rowLvl=as.character(mean_count_allC_cat_cy))%>%
    select(rowGp,rowGpNum,rowLvl,matches("^nORI_c\\d$"))
  
  table_r5 <- tblDat %>% 
    subset(nMonth_all<24) %>%
    #select(ori,sum_count_allC_cat_cy,matches("^c\\d$")) %>%
    select(ori,one,matches("^c\\d$")) %>%
    subset(duplicated(.)==FALSE) %>%
    #group_by(sum_count_allC_cat_cy,.drop=FALSE) %>%
    group_by(one,.drop=FALSE) %>%
    dplyr::summarize(across(matches("^c\\d$"),
                            sum,
                            .names="nORI_{.col}")) %>%
    mutate(rowGp="Late Joiners",
           rowGpNum=5,
           #rowLvl=as.character(sum_count_allC_cat_cy))%>%
           rowLvl=1)%>%
    select(rowGp,rowGpNum,rowLvl,matches("^nORI_c\\d$"))
  
  table_rA <- mget(c(paste0("table_r",1:5),
                     "dummy")) %>%
    rbindlist() %>%
    arrange(rowGpNum)
  #head(table_rA,n=10L) %>%
  #  print()
  
  return(table_rA)
}
#test <- longSummaryByType(novelCounts_long_allC,count_allC)
#Adding function for by months counts
longSummaryByTypeMonths <- function(dat,countVar,dummy=dummyRows){
  ################################
  #Total column
  countVar <- enquo(countVar)
  tblDat <- dat %>% 
    mutate(one=1) %>%
    subset(month_num_abs>48) %>%
    group_by(ori) %>%
    mutate(minorHigh_novel_cy=cluster_novel==2 & median_novel>medianOth_k2,
           minorLow_novel_cy=cluster_novel==2 & median_novel<medianOth_k2) %>%
    ungroup() %>%
    mutate(outlier_green_novel_cy=str_detect(outlier_novel,"green"),
           outlier_red_novel_cy=str_detect(outlier_novel,"red"),
           outlier_orange_novel_cy=str_detect(outlier_novel,"orange"),
           outlier_blue_novel_cy=str_detect(outlier_novel,"blue"),
           outlier_brown_novel_cy=str_detect(outlier_novel,"brown")) %>%
    mutate(c1=TRUE,
           c2=outlier_green_novel_cy,
           c3=outlier_red_novel_cy,
           c4=outlier_orange_novel_cy,
           c5=outlier_blue_novel_cy,
           c6=outlier_brown_novel_cy) %>%
    select(ori,month_num_abs,one,nibrs_agn_agency_type_name,popGroup_code,
           #sum_count_allC_cat_cy,
           mean_count_allC_cat_cy,
           nMonth_all,
           matches("^c\\d$")) %>%
    subset(duplicated(.)==FALSE)
  
  #Overall
  table_r1 <- tblDat %>% 
    select(ori,month_num_abs,one,matches("^c\\d$")) %>%
    subset(duplicated(.)==FALSE) %>%
    group_by(one,.drop=FALSE) %>%
    dplyr::summarize(across(matches("^c\\d$"),
                            sum,
                            .names="nMonths_{.col}")) %>%
    mutate(rowGp="Overall",
           rowGpNum=1,
           rowLvl="Overall") %>%
    select(rowGp,rowGpNum,rowLvl,matches("^nMonths_c\\d$"))
  
  #Agency type rows
  table_r2 <- tblDat %>% 
    select(ori,month_num_abs,nibrs_agn_agency_type_name,matches("^c\\d$")) %>%
    subset(duplicated(.)==FALSE) %>%
    group_by(nibrs_agn_agency_type_name,.drop=FALSE) %>%
    dplyr::summarize(across(matches("^c\\d$"),
                            sum,
                            .names="nMonths_{.col}")) %>%
    mutate(rowGp="Agency type",
           rowGpNum=2,
           rowLvl=as.character(nibrs_agn_agency_type_name))%>%
    select(rowGp,rowGpNum,rowLvl,matches("^nMonths_c\\d$"))
  #Population
  table_r3 <- tblDat %>% 
    select(ori,month_num_abs,popGroup_code,matches("^c\\d$")) %>%
    subset(duplicated(.)==FALSE) %>%
    group_by(popGroup_code,.drop=FALSE) %>%
    dplyr::summarize(across(matches("^c\\d$"),
                            sum,
                            .names="nMonths_{.col}")) %>%
    mutate(rowGp="Population",
           rowGpNum=3,
           rowLvl=as.character(popGroup_code))%>%
    select(rowGp,rowGpNum,rowLvl,matches("^nMonths_c\\d$"))
  
  table_r4 <- tblDat %>% 
    #select(ori,month_num_abs,sum_count_allC_cat_cy,matches("^c\\d$")) %>%
    select(ori,month_num_abs,mean_count_allC_cat_cy,matches("^c\\d$")) %>%
    subset(duplicated(.)==FALSE) %>%
    #group_by(sum_count_allC_cat_cy,.drop=FALSE) %>%
    group_by(mean_count_allC_cat_cy,.drop=FALSE) %>%
    dplyr::summarize(across(matches("^c\\d$"),
                            sum,
                            .names="nMonths_{.col}")) %>%
    mutate(rowGp="Total Crime",
           rowGpNum=4,
           #rowLvl=as.character(sum_count_allC_cat_cy))%>%
           rowLvl=as.character(mean_count_allC_cat_cy))%>%
    select(rowGp,rowGpNum,rowLvl,matches("^nMonths_c\\d$"))
  
  table_r5 <- tblDat %>% 
    subset(nMonth_all<24) %>%
    #select(ori,sum_count_allC_cat_cy,matches("^c\\d$")) %>%
    select(ori,month_num_abs,one,matches("^c\\d$")) %>%
    subset(duplicated(.)==FALSE) %>%
    #group_by(sum_count_allC_cat_cy,.drop=FALSE) %>%
    group_by(one,.drop=FALSE) %>%
    dplyr::summarize(across(matches("^c\\d$"),
                            sum,
                            .names="nMonths_{.col}")) %>%
    mutate(rowGp="Late Joiners",
           rowGpNum=5,
           #rowLvl=as.character(sum_count_allC_cat_cy))%>%
           rowLvl=1)%>%
    select(rowGp,rowGpNum,rowLvl,matches("^nMonths_c\\d$"))
  table_rA <- mget(c(paste0("table_r",1:5),
                     "dummy")) %>%
    rbindlist() %>%
    arrange(rowGpNum)
  #head(table_rA,n=10L) %>%
  #  print()
  
  return(table_rA)
}


#```{r get_longitudinal_allC}

set.seed(1)
novelCounts_long_allC <- runNovelMethod_v5(taskDat,
                                           clustVars=count_allC,
                                           clustLab="overall crime counts",
                                           idVar=ori,oriList,indexVar=month_num_abs,
                                           cval_MAD=3.5,run_novel=TRUE,
                                           plot=FALSE)

novelCounts_long_allC <- novelCounts_long_allC %>%
  subset(month_num_abs>48) %>%
  group_by(ori) %>%
  mutate(#sum_count_allC_cy=sum(count_allC,na.rm=TRUE),
         #sum_count_allC_cat_cy=case_when(sum_count_allC_cy <= 120 ~ 1L,
        #                                 sum_count_allC_cy <= 240 ~ 2L,
        #                                 sum_count_allC_cy <= 360 ~ 3L,
        #                                 sum_count_allC_cy <= 480 ~ 4L,
        #                                 sum_count_allC_cy <= 600 ~ 5L,
        #                                 sum_count_allC_cy  > 600 ~ 6L),
         mean_count_allC_cy=mean(count_allC,na.rm=TRUE),
         mean_count_allC_cat_cy=case_when(mean_count_allC_cy  < 10 ~ 1L,
                                          mean_count_allC_cy  < 20 ~ 2L,
                                          mean_count_allC_cy  < 30 ~ 3L,
                                          mean_count_allC_cy  < 40 ~ 4L,
                                          mean_count_allC_cy  < 50 ~ 5L,
                                          mean_count_allC_cy >= 50 ~ 6L)) %>%
  ungroup()
  

tableAll_long_rAcA <- longSummaryByType(novelCounts_long_allC,count_allC)

#Note: Will drop the row indicators when exporting to Excel (table shell)
tableAll_long_rAcA %>%
  data.frame() %>%
  DT::datatable()



tableAll_long_rAcA_months <- longSummaryByTypeMonths(novelCounts_long_allC,count_allC,dummy=dummyRowsMonths)

#Note: Will drop the row indicators when exporting to Excel (table shell)
tableAll_long_rAcA_months %>%
  data.frame() %>%
  DT::datatable()

#```


#```{r output}
infile_name <- "TableShell/Outlier Detection_Longitudinal Analysis_Summary_Tables_2023_v2.xlsx"
file_name <- paste0(mainpath,"Outlier Detection_Longitudinal Analysis_Summary_Tables.xlsx")
inCol <- "B"
inRow <- 7
wb <- loadWorkbook(file = infile_name)
writeData(wb,sheet="Number of Agencies",
          tableAll_long_rAcA %>%
            select(matches("nORI_c\\d")),
          withFilter = F,startCol = inCol, startRow = inRow, colNames = FALSE,na.string="")
writeData(wb,sheet="Number of Months",
          tableAll_long_rAcA_months %>%
            select(matches("nMonths_c\\d")),
          withFilter = F,startCol = inCol, startRow = inRow, colNames = FALSE,na.string="")
suppressMessages(saveWorkbook(wb,file =file_name ,overwrite = T))

#```
