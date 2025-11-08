###########
## Read in NIBRS data 
library(tidyverse)
library(openxlsx)
library(ggplot2)
#install.packages('factoextra')
library(factoextra)
#install.packages("data.table")
library(data.table)
library(fpc)
library(moments)
library(DT)


oriListLatest <- nibrs_allYrs_long2 %>% #nibrsRaw %>%
  subset(year==max(as.numeric(nibrsYrs))) %>%
  .$ori %>%
  unique()

#Get rid of unneeded datasets/values
rm(nibrs,nibrs_allYrs_long,nibrs_groups,nibrsRaw,
   medianCounts_cs_allYrs,
   minPop_allYrs,
   statsORI_allYrs,
   monthsDF,
   rtiGroups_allYrs,rtiGroups_allYrs_byGp,
   percentiles_allC_allYrs,percentiles_otherc_allYrs,
   percentiles_part1p_allYrs,percentiles_part1v_allYrs,
   oris_allYrs,nMonths_allYrs,meanCounts_allYrs)
rm(list=c(paste0("nibrs_",nibrsYrs,"_long"),
          paste0("statsORI_",nibrsYrs),
          paste0("rtiGroup_",nibrsYrs),
          paste0("percentiles_allC_",nibrsYrs),
          paste0("percentiles_part1p_",nibrsYrs),
          paste0("percentiles_part1v_",nibrsYrs),
          paste0("percentiles_otherc_",nibrsYrs),
          paste0("oris_",nibrsYrs)))


#################
#Create task dataframe
taskDat <- nibrs_allYrs_long2 %>%
  subset(!is.na(count_allC)) %>%
  select(ori,month_num_abs,repMonth_num,ucr_agency_name,nibrs_agn_population,
         rtiGroup_code,rtiGroup_desc,rtiGroups_allYrs_desc,matches("percentile.*"),
         nibrs_agn_agency_type_name,count_allC,crimeRate_allC,
         medianCount_allC_oneLEA_allYrs,der_joiners) %>%
  mutate(crimeVal=count_allC,
         crimeVar="count_allC") %>%
  mutate(shape=rtiGroup_desc %>% as.character() %>% 
           str_replace_all(string=.,
                           pattern=c("(: |counties )"),
                           replacement=c("\\1\n"))) %>%
  arrange(ori,month_num_abs)

oriList <- taskDat$ori %>% unique()

nORI <- length(oriList)


#############
#Run multi-step process
novelCounts_allLEAs <- runNovelMethod_v5(taskDat,
                                         clustVars=count_allC,
                                         clustLab="overall crime counts",
                                         idVar=ori,oriList,indexVar=month_num_abs,
                                         cval_MAD=3.5,run_novel=TRUE,
                                         plot=FALSE)


novelCounts_allLEAs %>%
  select(ori,patternAB_novel) %>%
  subset(duplicated(.)==FALSE) %>%
  group_by(patternAB_novel) %>%
  summarize(n=n())

##############
## Create data file

#Here we'll create the data file according to the 'data file structure' tab.

#Month crosswalk
#18Dec2024: using year labels that support years outside of 21st century
yrs <- as.numeric(nibrsYrs) %% 100
yrsLabel <- yrs %>% str_pad(width=2,side="left",pad="0")
monthCW <- data.frame(month_num_abs=1:(12*length(nibrsYrs)),
                      #month_name_abs=outer(month.abb,(min(as.numeric(nibrsYrs))-2000):(max(as.numeric(nibrsYrs))-2000),FUN=paste,sep="-") %>%
					  month_name_abs=outer(month.abb,yrsLabel,FUN=paste,sep="-") %>%
					    as.character())

monthCW %>% head()

#18Dec2024: supporting cases where we have <5 years of data
monthFilter <- monthCW %>% pull(month_num_abs) %>% max() - 12
monthCW_CY <- monthCW %>%
  #filter(month_num_abs > 48)
  filter(month_num_abs > monthFilter)

outlierDF <- novelCounts_allLEAs %>%
  #18Dec2024: changing filtering condition
  #subset(month_num_abs>48) %>% #Only keep current year
  subset(month_num_abs>monthFilter) %>% #Only keep current year
  group_by(ori) %>%
  mutate(nGreen_cy=sum(outlier_novel %in% c("green (main)","green (minor)")),
         nMonth_cy=n()) %>%
  ungroup() %>%
  mutate(outlier_novel=case_when(nMonth_cy<nMonth_all & nGreen_cy<4 ~ paste0("green ",str_extract(outlier_novel,"\\(.+\\)")),
                                 TRUE ~ outlier_novel)) %>%
  mutate(outlier_novel=str_remove(outlier_novel," \\((main|minor)\\)")) %>%
  select(ori,month_num_abs,nCluster_novel,cluster_novel,outlier_novel) %>%
  left_join(monthCW,by="month_num_abs") %>%
  mutate(value=outlier_novel,variable=month_name_abs) %>%
  arrange(month_num_abs) %>%
  select(ori,nCluster_novel,variable,value) %>%
  group_by(ori) %>%
  mutate(nSeqs=nCluster_novel,
         nBrownOutliers=sum(value=="brown",na.rm=TRUE),
         nBlueOutliers=sum(value=="blue",na.rm=TRUE),
         nRedOutliers=sum(value=="red",na.rm=TRUE),
         nOrangeOutliers=sum(value=="orange",na.rm=TRUE)) %>%
  ungroup() %>%
  reshape2::dcast(formula=ori+nSeqs+nBlueOutliers+nRedOutliers+nOrangeOutliers ~ variable,value.var="value") %>%
  select(ori,nSeqs,nBlueOutliers,nRedOutliers,nOrangeOutliers,monthCW_CY$month_name_abs)



#subset(nibrs_allYrs_long2,ori=="AR0181000") %>%
#  select(ori,year,month_num) %>%
#  data.frame()
outlierDF %>%
  head() %>%
  DT::datatable()

outlierDF %>% 
  group_by(nBlueOutliers) %>%
  summarize(n=n()) %>%
  DT::datatable()

outlierDF %>% 
  group_by(nRedOutliers) %>%
  summarize(n=n()) %>%
  DT::datatable()

outlierDF %>% 
  group_by(nOrangeOutliers) %>%
  summarize(n=n()) %>%
  DT::datatable()


outlierDF %>%
  group_by(nSeqs) %>%
  summarize(n=n())


fwrite_wrapper(outlierDF,paste0(mainpath,"outlier_data_file.csv"))
