#Note (08Dec2022): May need to play around with parameters to use outside NIBRS use-case
#Note (18Dec2024): modifying labels to handle years outside of the 21st century							
getPlot <- function(dat,idVar,nameVar,groupVar,groupsVar,indexVar,clustVar,clustLab,seqVar,seqLab,outVar=NA,outLab=NA){#,ori,gp_desc,crimeVar,type,outInd
  #print(outVar)
  if (!is.na(outVar)){
    plotDatTemp <- dat %>% 
      rename(seq=all_of(seqVar),
             outlier=all_of(outVar),
             shape=all_of(groupVar))
  } else {
    plotDatTemp <- dat %>% 
      rename(seq=all_of(seqVar),
             shape=all_of(groupVar))
  }
  #print("Created plotDatTemp")
  id <- plotDatTemp %>% select(!!idVar) %>% unique()
  name <- plotDatTemp[1,nameVar]
  #type <- plotDatTemp[1,"nibrs_agn_agency_type_name"]
  groups <- plotDatTemp[1,groupsVar] %>%
    str_replace_all(pattern=", ",replacement=paste0(",\n",str_flatten(rep(" ",times=13))))
  #group <- plotDatTemp %>% pull(groupVar) %>% unique()
  #print(group)
  #print(oriDat2)
  #print("Created LEA-specific vars")
  sizePlot <- dat %>%
    summarize(max=max(!!indexVar),
              min=min(!!indexVar)) %>%
    #print() %>%
    mutate(sizePlot=max-min+1) %>%
    pull(sizePlot)
  nBreaks <- ceiling(sizePlot/15)
  #18Dec2024: creating year labels here that will support years outside of 21st century
  yrs <- as.numeric(nibrsYrs) %% 100
  yrsLabel <- yrs %>% str_pad(width=2,side="left",pad="0")
  if (!is.na(outVar)){
    #print("Starting ggplot (with outliers)")
    {ggplot(plotDatTemp,aes(y=!!clustVar,x=!!indexVar,shape=shape)) + 
        geom_point(aes(colour=seq,size=1.5))+
        #scale_color_manual(values=c("red","black","blue","darkgreen"))  +
        scale_color_manual(values=c("blue","orange"))  +
        #scale_size_manual() +
        geom_line() +
        geom_point(data=subset(plotDatTemp,outlier %in% c("red (minor)","red (main)")),
                   pch=21,fill=NA,size=8,colour="red",stroke=1,show.legend=FALSE) +
        geom_point(data=subset(plotDatTemp,outlier %in% c("blue (minor)","blue (main")),
                   pch=21,fill=NA,size=8,colour="blue",stroke=1,show.legend=FALSE) +
        geom_point(data=subset(plotDatTemp,outlier %in% c("orange (minor)","orange (main)")),
                   pch=21,fill=NA,size=8,colour="orange",stroke=1,show.legend=FALSE) +
        geom_point(data=subset(plotDatTemp,outlier %in% c("brown (minor)","brown (main)")),
                   pch=21,fill=NA,size=8,colour="brown",stroke=1,show.legend=FALSE) +
        geom_point(data=subset(plotDatTemp,outlier %in% c("green (minor)","green (main)")),
                   pch=21,fill=NA,size=8,colour="green",stroke=1,show.legend=FALSE) +
        scale_x_continuous(breaks=seq(1,12*length(nibrsYrs),by=nBreaks),
                           labels=outer(seq(1,12,by=nBreaks),
						                #18Dec2024: use newly created year labels
                                        #(min(as.numeric(nibrsYrs))-2000):(max(as.numeric(nibrsYrs))-2000),
										yrsLabel,
                                        FUN = paste,
                                        sep="/") %>%
                             as.character())+
        xlab("Month") +
        ylab(clustLab) +
        theme(legend.position = "bottom",
              title=element_text(family="mono")) +
        ggtitle(paste0(id," (",seqLab,"; ",outLab,")",
                       ". \n >Agency name: ", name,
                       ". \n >RTI group: ", groups#,
                       #". \n >Manual review: Outlier==",outInd
        ))} %>%
      print()
  } else {
    #print("Starting ggplot (WITHOUT outliers)")
    print(groupVar)
    {ggplot(plotDatTemp,aes(y=!!clustVar,x=!!indexVar,shape=shape)) + 
        geom_point(aes(colour=seq,size=1.5))+
        scale_color_manual(values=c("blue","orange"))  +
        geom_line() +
        scale_x_continuous(breaks=seq(1,12*length(nibrsYrs),by=nBreaks),
                           labels=outer(seq(1,12,by=nBreaks),
						                #18Dec2024: use newly created year labels
										#(min(as.numeric(nibrsYrs))-2000):(max(as.numeric(nibrsYrs))-2000)
                                        yrsLabel,
                                        FUN = paste,
                                        sep="/") %>%
                             as.character())+
        xlab("Month") +
        ylab(clustLab) +
        theme(legend.position = "bottom",
              title=element_text(family="mono")) +
        ggtitle(paste0(id," (",seqLab,")",
                       ". \n >Agency name: ", name,
                       ". \n >RTI group: ", groups#,
                       #". \n >Manual review: Outlier==",outInd
        ))} %>%
      print()} 
}