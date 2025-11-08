#runNovelMethod_v5.R
#Note (07Dec2022): Overhauling how novel method is run. For instance, switching from looping via sapply() to using group_by()

runNovelMethod_v5 <- function(inDat,
                              clustVars,
                              clustLab,
                              idVar,
                              idList,
                              indexVar,
                              run_novel = FALSE,
                              run_gapStat = FALSE,
                              cval_MAD = 3.5,
                              cval_MAD2 = 5, #14Apr2023: adding 2nd critical value
                              hc_meth="single",
                              minLength = 4L, #Min length to be considered a cluster
                              maxK = 2L, #Max number of clusters... only testing on maxK=2 for now
                              plot = FALSE,
                              verbose = FALSE) {
  idVar <- enquo(idVar)
  clustVars <- enquo(clustVars)
  nClustVars <- inDat %>% ungroup() %>% select(!!clustVars) %>% ncol()
  indexVar <- enquo(indexVar)
  #print(nClustVars)
  dat <- inDat %>%
    filter(!!quo(!!idVar %in% !!idList)) %>%
    group_by(!!idVar) %>%
    mutate(nMissing_all = sum(is.na(!!clustVars)),
           max_all = max(!!clustVars),
           min_all = min(!!clustVars),
           sd_all = sd(!!clustVars)) %>%
    filter(nMissing_all == 0L) %>%
    select(-nMissing_all) %>%
    mutate(nMonth_all = n())
  #Separate into 2 piles: IDs with/without min number of records
  #Update (09Dec2022): Including stddev of clustVars in decision 
  
  working <- dat %>%
    filter(nMonth_all>=minLength & sd_all > 0) %>%
    #Initializing pattern vars
    mutate(patternAB_novel=NA_character_,
           patternAB_gapStat=NA_character_)
  
  pause <- dat %>%
    filter(nMonth_all < minLength | sd_all == 0) %>%
    mutate(patternAB_novel=NA_character_,
           patternAB_gapStat=NA_character_)
  if (maxK>=2L){
    working <- working %>%
      mutate(cluster_k2 = !!clustVars %>%
               scale() %>%
               matrix(ncol = nClustVars) %>%
               hcut(k = maxK, hc_method = "single") %>%
               getElement("cluster") %>%
               as.integer())
    pause <- pause %>%
      mutate(cluster_k2=NA_integer_)
  }
  if (run_novel == TRUE) {
    if (maxK>=2L){
      #Step 1: Clustering
      #Get statistics by cluster 
      statsSame <- working %>%
        group_by(!!idVar, cluster_k2, nMonth_all) %>%
        #Note (07Dec2022): Assuming single cluster variable for median / MAD
        #Note (08Dec2022): Assuming 2 clusters... if using other maxK, need to look at max/min
        summarize(nMonth_k2 = n(),
                  min_k2 = min(!!clustVars),
                  max_k2 = max(!!clustVars),
                  median_k2 = median(!!clustVars),
                  mad_k2 = mad(!!clustVars))
      #Get median of other cluster
      statsOth <- statsSame %>%
        mutate(cluster_k2 = 3L - cluster_k2) %>%
        select(!!idVar, cluster_k2, medianOth_k2 = median_k2, nMonthOth_k2 = nMonth_k2)
      working <- working %>%
        left_join(statsSame) %>%
        left_join(statsOth)
      #print("closest")
      closest <- working %>%
        group_by(!!idVar, cluster_k2) %>%
        mutate(minDist = min(abs(!!clustVars - medianOth_k2))) %>%
        ungroup() %>%
        filter(abs(!!clustVars - medianOth_k2) == minDist) %>%
        mutate(cluster_k2 = 3L - cluster_k2) %>%
        select(!!idVar, cluster_k2, closest = !!clustVars) %>%
        subset(duplicated(.)==FALSE)
      #print("statsK2")
      statsK2 <- statsSame %>%
        left_join(closest) %>%
        mutate(ind = ifelse(mad_k2 > 0,
                            (abs(median_k2 - closest) / mad_k2) > cval_MAD,
                            TRUE),
               ind2 = ifelse(mad_k2 > 0,
                            (abs(median_k2 - closest) / mad_k2) > cval_MAD2,
                            TRUE)) %>%
        group_by(!!idVar) %>%
        summarize(nMonthMin_k2 = min(nMonth_k2),
                  nMonthMax_k2 = max(nMonth_k2),
                  wgtScore = sum(ind * nMonth_k2 / nMonth_all),
                  wgtScore2 = sum(ind2 * nMonth_k2 / nMonth_all)) %>%
        select(!!idVar, wgtScore, wgtScore2, nMonthMin_k2, nMonthMax_k2)
      #print(working)
      message("statsK2, top 10 weighted score:")
      print(statsK2 %>% arrange(-wgtScore) %>% head(n=10L))
      message("statsK2, top 10 weighted score (nMonthMax_k2>=minLength):")
      print(statsK2 %>% filter(nMonthMax_k2>=minLength) %>% arrange(-wgtScore) %>% head(n=10L))
      working <- working %>%
        left_join(statsK2) %>%
        mutate(cluster_k2 = case_when(max_k2==max_all & nMonth_k2>=max(minLength,nMonth_all/3) ~ 1, #High Cluster with at least minLength months or 1/3 of all the months, whichever is higher
                                      max_k2==max_all ~ 2, #High cluster with less than minLength months or 1/3 of all the months, whichever is higher
                                      max_k2 < max_all & nMonthOth_k2 < max(minLength,nMonth_all/3) ~ 1, #Low cluster whose corresponding high cluster has less than minLength months or 1/3 of all the months, whichever is higher
                                      max_k2 < max_all ~ 2 #Low cluster whose corresponding high cluster has at least minLength months or 1/3 of all the months, whichever is higher
        )) %>%
        #Determine if should use 2 clusters
        mutate(indNovel = wgtScore > 0.5 &
                 nMonthMax_k2 >= minLength & nMonth_all >= (minLength+1),
               indNovel2 = wgtScore2 > 0.5 &
                 nMonthMax_k2 >= minLength & nMonth_all >= (minLength+1)) %>%
        mutate(cluster_novel = ifelse(indNovel == TRUE, cluster_k2, 1L),
               nMonth_novel = ifelse(indNovel == TRUE, nMonth_k2, nMonth_all)) %>%
        group_by(!!idVar) %>%
        mutate(nCluster_novel = max(cluster_novel)) %>%#Get number of clusters
        ungroup()
      #Repeat clustering for pause dataset
      pause <- pause %>%
        mutate(nMonth_k2 = NA_integer_,
               min_k2 = NA_real_,
               max_k2 = NA_real_,
               median_k2 = NA_real_,
               mad_k2 = NA_real_,
               medianOth_k2=NA_real_,
               wgtScore=NA_real_,
               wgtScore2=NA_real_,
               indNovel=NA,
               indNovel2=NA,
               nMonthMin_k2=NA_integer_,
               nMonthMax_k2=NA_integer_,
               
               cluster_novel=1L,
               nMonth_novel=nMonth_all,
               nCluster_novel=1L) 
    } else if (maxK==1L){
      working <- working %>%
        mutate(cluster_novel = 1L,
               nMonth_novel = nMonth_all,
               nCluster_novel = 1L) %>%
        group_by(!!idVar) %>%
        mutate(median_novel=median(!!clustVars), #Get median of clusters
               max_novel=max(!!clustVars),
               min_novel=min(!!clustVars),
               mad_novel=mad(!!clustVars)) %>% #Get MAD of clusters
        ungroup()
      #Repeat clustering for pause dataset
      pause <- pause %>%
        mutate(cluster_novel=1L,
               nMonth_novel=nMonth_all,
               nCluster_novel=1L) 
    }
    #Step 2: Outlier Detection
    #Outlier test statistic and indicator
    working <- working %>%
      group_by(!!idVar,cluster_novel) %>%
      mutate(median_novel=median(!!clustVars), #Get median of clusters
             max_novel=max(!!clustVars),
             min_novel=min(!!clustVars),
             mad_novel=mad(!!clustVars)) %>% #Get MAD of clusters
      ungroup() %>%
      mutate(testStat_novel = ifelse(nMonth_novel >= minLength,
                                     ifelse(mad_novel>0,
                                            (!!clustVars - median_novel) / mad_novel,
                                            ifelse(!!clustVars==median_novel,
                                                   0,
                                                   Inf)),
                                     NA_real_)) %>%
	  group_by(!!idVar,cluster_novel) %>% #12Apr2024: need to group by id X cluster to make max() work within the mutate()
      mutate(outlier_novel = ifelse(cluster_novel==1L,
                                    #Main cluster
                                    ifelse(nMonth_novel >= minLength,
                                           case_when(testStat_novel <= -cval_MAD2 & median_novel-!!clustVars>=10~ "red (main)",
                                                     testStat_novel <= -cval_MAD & testStat_novel < -cval_MAD2 & !!clustVars <= 0.1*median_novel & median_novel-!!clustVars>=10 ~ "red (main)",
                                                     testStat_novel <= -cval_MAD & testStat_novel < -cval_MAD2 & !!clustVars  > 0.1*median_novel & median_novel-!!clustVars>=10 ~ "orange (main)",
                                                     testStat_novel >=  cval_MAD & testStat_novel >  cval_MAD2 & median_novel-!!clustVars>=10 ~ "blue (main)",
                                                     testStat_novel >=  cval_MAD2 & median_novel-!!clustVars>=10 ~ "brown (main)",
                                                     TRUE ~ "green (main)"),
                                           "!!!"), #Catch issues
                                    #Minor cluster
                                    case_when(abs(median_novel-medianOth_k2)<10 ~ "green (minor)",
                                              max_novel==max_all & nMonth_novel<max(minLength,nMonth_all/3) & median_novel-medianOth_k2>=10 ~ "blue (minor)",#High cluster with less than minLength months or 1/3 of all months, whichever is higher 
                                              #Low cluster whose corresponding high cluster has at least minLength months or 1/3 of all months, whichever is higher, and...
                                           max_novel<max_all & nMonthOth_k2>=max(minLength,nMonth_all/3) & indNovel2==TRUE & medianOth_k2-median_novel>=10 ~ "red (minor)",#this cluster can be detected as a separate cluster when nMAD>=5
                                           max_novel<max_all & nMonthOth_k2>=max(minLength,nMonth_all/3) & indNovel==TRUE & indNovel2==FALSE & median_novel<=0.1*medianOth_k2 & (medianOth_k2-median_novel)>=10 ~ "red (minor)", #3.5<=nMAD<5 and nM(low)<=10%*nM(high)
                                           max_novel<max_all & nMonthOth_k2>=max(minLength,nMonth_all/3) & indNovel==TRUE & indNovel2==FALSE & median_novel >0.1*medianOth_k2 & (medianOth_k2-median_novel)>=10 ~ "orange (minor)", #3.5<=nMAD<5 and nM(low)>10%*nM(high)
                                           TRUE ~ "!!") #Catch issues
                                    )) %>%
      group_by(!!idVar) %>%
      mutate(nOutlier_novel=sum(outlier_novel!="green",na.rm=TRUE) %>%
               as.integer()) %>%
      arrange(!!indexVar) 
    
    #Search for Pattern A / Pattern B
    if (maxK>=2L){
      working <- working %>%
        #Note (08Dec2022): Using rle() function to check if clusters occur in sequence (Pattern A) or not (Pattern B) 
        mutate(
          patternAB_novel = ifelse(
            nCluster_novel == 2L & nMonthMin_k2 >= minLength,
            ifelse(
              cluster_novel %>%
                rle() %>%
                getElement("values") %>%
                length() == 2L,
              "Pattern A",
              "Pattern B"
            ),
            "Misc"
          )
        ) %>%
        ungroup()
    } else if (maxK==1L){
      working <- working %>%
        mutate(patternAB_novel="Misc")
    }
    # print(working %>% 
    #         mutate(nMonthGTEMinLength=nMonth_all>=minLength,
    #                nOutlierGT0_novel=nOutlier_novel>0L) %>% 
    #         group_by(nMonthGTEMinLength,nOutlierGT0_novel,
    #                  nCluster_novel,nOutlier_novel,patternAB_novel) %>% 
    #         summarize(n=n()))
    #Repeat for pause dataset
    pause <- pause %>%
      mutate(median_novel=NA_real_,
             max_novel=NA_real_,
             min_novel=NA_real_,
             mad_novel=NA_real_,
             testStat_novel=NA_real_,
             outlier_novel="green (main)", #12Apr2024: set paused agencies' points to green
             nOutlier_novel=0L)
  }
  if (run_gapStat == TRUE) {
    message("Gap statistic")
    message("Get optimal k for each ID")
    updates <- seq(from=1,to=length(idList),length.out=min(length(idList),50)) %>% 
      round()
    if (maxK>=2L){
      nClusters_gapStat <- working %>%
        #select(ori,counts) %>%
        group_by(!!idVar) %>%
        #!!clustVars %>%
        group_modify(.f =  ~ {
          if (which(idList==pull(.y,!!idVar)) %in% updates){
            message(paste0("Progress: ",
                           which(idList==pull(.y,!!idVar)),
                           "/",
                           length(idList)))
          }
          #print(n())
          #print(nrow(.))
          gapStat <- cluster::clusGap(
            select(.x, !!clustVars) %>%
              scale() %>%
              matrix(ncol = nClustVars),
            hc_method = "single",
            FUNcluster = hcut,
            B = 500,
            K.max = min(nrow(.), maxK),
            verbose = FALSE)
          optK <- cluster::maxSE(gapStat$Tab[, 3], SE.f = gapStat$Tab[, 4])
          #print(optK)
          return(data.frame(nCluster_gapStat = as.integer(optK)))
        })
      working <- working %>%
        left_join(nClusters_gapStat) %>%
        group_by(!!idVar) %>%
        mutate(cluster_gapStat = ifelse(nCluster_gapStat>1L,cluster_k2,1L))
      
    } else if (maxK==1L){
      working <- working %>%
        mutate(nCluster_gapStat=1L,
               cluster_gapStat=1L)
    }
    #Repeat clustering for pause dataset
    pause <- pause %>%
      mutate(nCluster_gapStat=1L,
             cluster_gapStat=1L)
    
    working <- working %>%
      group_by(!!idVar, cluster_gapStat) %>%
      mutate(nMonth_gapStat = n(),
             median_gapStat = median(!!clustVars),
             mad_gapStat = mad(!!clustVars)) %>%
      ungroup() %>%
      mutate(testStat_gapStat = ifelse(
        nMonth_gapStat >= minLength,
        abs(!!clustVars - median_gapStat) / mad_gapStat,
        NA_real_)) %>%
      #Outlier detection
      #>If cluster meets minimum length, use MAD method to identify outliers
      #>Else if 2 clusters (1 meeting min length), treat short cluster as outliers
      #>Else don't identify outliers
      mutate(
        outlier_gapStat = ifelse(
          nMonth_gapStat >= minLength,
          testStat_gapStat > cval_MAD,
          nCluster_gapStat == 2 & nMonthMax_k2>=minLength
        )
      ) %>%
      group_by(!!idVar) %>%
      mutate(nOutlier_gapStat=sum(outlier_gapStat,na.rm=TRUE) %>%
               as.integer()) %>%
      arrange(!!indexVar) 
    
    #Search for Pattern A / Pattern B
    if (maxK>=2L){
      working <- working %>%
        #Note (08Dec2022): Using rle() function to check if clusters occur in sequence (Pattern A) or not (Pattern B) 
        mutate(
          patternAB_gapStat = ifelse(
            nCluster_gapStat == 2 & nMonthMin_k2 >= minLength,
            ifelse(
              cluster_gapStat %>%
                rle() %>%
                getElement("values") %>%
                length() == 2,
              "Pattern A",
              "Pattern B"
            ),
            "Misc"
          )
        ) %>%
        ungroup()
    } else if (maxK==1L){
      working <- working %>%
        mutate(patternAB_gapStat="Misc")
    }
    # print(working %>% 
    #         mutate(nMonthGTEMinLength=nMonth>=minLength,
    #                nOutlierGT0_gapStat=nOutlier_gapStat>0L) %>% 
    #         group_by(nMonthGTEMinLength,nOutlierGT0_gapStat,
    #                  nCluster_gapStat,nOutlier_gapStat,patternAB_gapStat) %>% 
    #         summarize(n=n()))
    
    pause <- pause %>%
      mutate(nMonth_gapStat=nMonth_all) %>% #05Jan2024: changed nMonth to nMonth_all
      group_by(!!idVar) %>%
      mutate(median_gapStat = median(!!clustVars),
             mad_gapStat = mad(!!clustVars)) %>%
      ungroup() %>%
      mutate(testStat_gapStat=NA_real_,
             outlier_gapStat=FALSE,
             nOutlier_gapStat=0)
  }
  #Stack working and pause datasets
  dat <- working %>%
    bind_rows(pause) %>%
    arrange(!!idVar,!!indexVar)
  
  if (plot==TRUE){
    message("Plotting")
    plotDat <- dat %>%
      filter(patternAB_novel %in% c("Pattern A", "Pattern B") |
               patternAB_gapStat %in% c("Pattern A", "Pattern B"))
    #print(plotDat %>% select(!!idVar,!!indexVar,!!clustVars,patternAB_novel,patternAB_gapStat))
    plotIDs <- plotDat %>% pull(!!idVar) %>% unique()
    if (run_novel==TRUE){
      plotDat <- plotDat %>%
        mutate(cluster_novel=as.factor(cluster_novel))
    }
    if (run_gapStat==TRUE){
      plotDat <- plotDat %>%
        mutate(cluster_gapStat=as.factor(cluster_gapStat))
    }
    print(plotIDs)
    updates <- seq(from=1,to=length(plotIDs),length.out=min(length(plotIDs),50)) %>% 
      round()
    print(updates)
    sapply(plotIDs,function(i){
      tempDat <- plotDat %>% filter(!!idVar == i)
      print(tempDat %>% pull(!!idVar) %>% unique())
      if (which(plotIDs==(pull(tempDat,!!idVar) %>% unique())) %in% updates){
        #print(which(plotIDs==(pull(tempDat,!!idVar) %>% unique())))
        message(paste0("Progress: ",
                       which(plotIDs==(pull(tempDat,!!idVar) %>% unique())),
                       "/",
                       length(plotIDs)))
      }
      if (run_novel==TRUE){
        #print(tempDat)
        hc <- tempDat %>%
          select(!!clustVars) %>%
          scale() %>%
          matrix(ncol = nClustVars) %>%
          dist() %>%
          hclust(method=hc_meth)
        plot(hc,
             main = paste0("Dendrogram: ", i, ", ",hc_meth,", ",clustLab))
        nSpaces <- tempDat %>%
          select(!!idVar) %>%
          unique() %>%
          str_length() + 2
        getPlot(
          dat = tempDat,
          idVar = idVar,
          clustVar = clustVars,
          clustLab = str_to_title(clustLab),
          groupVar = "rtiGroup_desc",
          groupsVar = "rtiGroups_allYrs_desc",
          indexVar = indexVar,
          nameVar = "ucr_agency_name",
          seqVar = "cluster_novel",
          seqLab = paste0(
            "Novel method: ",hc_meth,", ",clustLab," (cutoff: ",
            cval_MAD,
            ")"
          ),
          outVar = "outlier_novel",
          outLab = paste0("\n",str_dup(" ",nSpaces),"MAD Outlier Detection (cutoff: ", cval_MAD, ")")
        )
      }
      if (run_gapStat==TRUE){
        gapStat <- tempDat %>%
          select(!!clustVars) %>%
          scale() %>%
          matrix(ncol = nClustVars) %>%
          cluster::clusGap(hc_method=hc_meth,
                           FUNcluster=hcut,
                           B=500,
                           K.max=min(nrow(tempDat),2L),
                           verbose=verbose)
        plot(gapStat,
             main = paste0("k Plot: ", i, ", ",hc_meth,", ",clustLab))
        
        nSpaces <- tempDat %>%
          select(!!idVar) %>%
          unique() %>%
          str_length() + 2
        #print("nSpaces")
        #print(nSpaces)
        #print("Preview:")
        #print(str_dup(" ",nSpaces))
        getPlot(
          dat = tempDat,
          idVar = idVar,
          clustVar = clustVars,
          clustLab = str_to_title(clustLab),
          groupVar = "rtiGroup_desc",
          groupsVar = "rtiGroups_allYrs_desc",
          indexVar = indexVar,
          nameVar = "ucr_agency_name",
          seqVar = "cluster_gapStat",
          seqLab = paste0(
            "Gap Statistic: ",hc_meth,", ",clustLab,
            " (cutoff: ",cval_MAD,")"
          ),
          outVar = "outlier_gapStat",
          outLab = paste0("\n",str_dup(" ",nSpaces),"MAD Outlier Detection (cutoff: ", cval_MAD, ")")
        )
      }
    })
  }
  return(dat)
}
