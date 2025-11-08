#Description: This program holds key functions that will be called throughout the main instance program
#Author: JD Bunker & Lance Couzens
#Update (JDB 09MAY2023): Adding gcFirst=FALSE to system.time() calls
#Update (JDB 03JUL2023): Adding support for (ORI x county)-level file
#Update (JDB 22JAN2024): Applying tweaks to rankem1/rankem2 and quantile() calls based on feedback from Lance
#Update (JDB 30JAN2024): Using ties.method="min" for rankem1/rankem2
#################
#Rank function

#function to calculate proportional ranks
rankem1 <- function(i) {
  #10May2023: Setting seed
  set.seed(1)
  log_debug("Running function rankem1")
  log_debug(system("free -mh", intern = FALSE))
  #Note (22Jan2024): tweaking based on suggestions by Lance... leaving old code in for now, in case we end up reverting
  #rank(i,na.last="keep",ties.method="random")/(sum(is.na(i)==FALSE)+0.01)
  rank(i,na.last="keep",ties.method="min")/(sum(is.na(i)==FALSE)+1)
}
#################
#Low-level function for step 1 + 2

getCopImp <- function(dat,step,lhsVars,impVars,stacks=1,benchmark="",outEnv=parent.env(environment()),nLHSVars=length(lhsVars),nImpVars=length(impVars)){
  #10May2023: Setting seed
  set.seed(1)
  #Create working dataset
  log_debug("Running function getCopImp")
  log_debug(system("free -mh", intern = FALSE))
  log_debug("Prep")
  system.time({
    #25Sep2023: splitting step 1 into 2 if statements
    if (step==1 & any(impVars=="p")){
      temp.dat <- dat %>%
        dplyr::select(ORI,county,den,all_of(lhsVars),all_of(impVars)) #%>%
      #rowwise()
      temp.zero <- data.frame()
    } else if (step==1){
      temp.dat <- dat %>%
        dplyr::select(ORI,county,all_of(lhsVars),all_of(impVars)) #%>%
      #rowwise()
      temp.zero <- data.frame()
    } else if (step==2){
      temp.dat <- dat %>%
        subset(eval(as.symbol(benchmark))>0) #%>%
      #rowwise()
	  #Note (14Sep2023): switching from mutate_at() to mutate(across())
      temp.zero <- dat %>%
        subset(eval(as.symbol(benchmark))==0) %>%
        mutate(across(all_of(impVars),.fns=~0)) 
	  
      #log_debug("temp.zero %>% select(ORI,all_of(lhsVars),all_of(impVars)) %>% head()")
      #print(temp.zero %>% select(ORI,all_of(lhsVars),all_of(impVars)) %>% head())
    }
    log_debug("working")
	#14Sep2023: separating out which variables are selected in step 1 vs. step 2
	#25Sep2023: treating step 1 with/without p differently
	if (step==1 & any(impVars=="p")){
		working <- temp.dat %>%
		  dplyr::select(ORI,county,den,lhsVars,impVars)
	} else if (step==1|step==2){
		working <- temp.dat %>%
		  dplyr::select(ORI,county,lhsVars,impVars)
	}
    #Get ranks
    #Note (JDB 02May2022): Fixing bug related to 1-variable dataframes
	#Note (JDB 14Sep2023): Switching from starting from 3 to 4 in loop
	#Note (JDB 14Sep2023): Moving setting of colnames into specific step 1/2 chunks
	#Note (JDB 25Sep2023): Handling step 1 with/without p differently
    if (step==1 & any(impVars=="p")){
      all<-working[,"ORI"] %>%
        data.frame(ORI=.) %>%
        bind_cols(working[,"county"] %>%
		            data.frame(county=.),
				  sapply(data.frame(working[,4:ncol(working)]),rankem1,simplify=FALSE))
    colnames(all) <- c("ORI","county",colnames(working)[4:ncol(working)])
    } else if (step==1|step==2){
      all<-working[,"ORI"] %>%
        data.frame(ORI=.) %>%
        bind_cols(working[,"county"] %>%
		            data.frame(county=.),
				  sapply(data.frame(working[,3:ncol(working)]),rankem2,simplify=FALSE))
		colnames(all) <- c("ORI","county",colnames(working)[3:ncol(working)])
    }
    
    filterVar <- impVars[1] #This will be used to separate SRS-only vs. NIBRS LEAs
    log_debug("srs")
    srs<-all[is.na(all[,filterVar])==TRUE,1:(nLHSVars+2)] %>%#15]#16]
      data.frame()
    colnames(srs) <- colnames(all)[1:(nLHSVars+2)]
    #log_debug("dim(srs)")
    #print(dim(srs))
    #print(srs)
  },gcFirst=FALSE) %>% print()
  if (nrow(srs)>0){#Only proceed if more than 1 SRS-only LEA
    
    #Update (07FEB2022): Only include NIBRS cases where sum of row vars > 0
    nibrs<-all[is.na(all[,filterVar])==FALSE,]
    
    log_debug("Calibrating copula")
    system.time({
      log_debug("t_base")
      t_base<-nibrs[,3:ncol(nibrs)] %>%
        as.matrix() %>%
        corKendall(checkNA=FALSE)
		
      if (nLHSVars>0){
        t_aug<-all[,3:(nLHSVars+2)] %>% #2:15] %>% #2:16] %>%
          as.matrix(rownames.force=TRUE) %>%
          corKendall(checkNA=FALSE)
        colnames(t_aug) <- colnames(all)[3:(nLHSVars+2)]
		
        matchcols<-Reduce(intersect,list(colnames(t_base),colnames(t_aug)))
        t<-t_base
        t[matchcols,matchcols]<-t[matchcols,matchcols]*0+t_aug
      } else {
        t <- t_base
      }
      #this relationship between t (Kendall's tau) and p (covariance) holds for the multivariate standard normal dist
      p<-iTau(normalCopula(),tau=t)
      
      #convert the covariance matrix p to a vector that can be read by the normalCopula() function
      parms<-P2p(p)
      
      #the normal/Gaussian copula fit over all variables in nibrs (including those common to srs)
      #log_debug("cop")
      cop<-normalCopula(param=parms,dim=dim(t)[2],dispstr="un")
      #print(cop)
    },gcFirst=FALSE) %>% print()
    #matrix of -uncorrelated- random uniform variates of the same dimension as the block to be imputed...
    ##the cCopula() function transforms these into a conditional sample from the copula
    
    log_debug("oris")
    oris<-srs[,"ORI"] %>%
      as.matrix()
    
    oris_stack<-rbindlist(replicate(stacks,oris %>% data.frame(),simplify=FALSE),use.names=TRUE,fill=TRUE) %>%
      data.frame()
    colnames(oris_stack) <- "ORI"
	
    log_debug("counties")
    counties<-srs[,"county"] %>%
      as.matrix()
    
    counties_stack<-rbindlist(replicate(stacks,counties %>% data.frame(),simplify=FALSE),use.names=TRUE,fill=TRUE) %>%
      data.frame()
    colnames(counties_stack) <- "county"
    log_debug("c_sim section")
    if (nLHSVars>0){
      #Conditional sample from the copula
      srs_stack<-rbindlist(replicate(stacks,data.frame(srs[,3:ncol(srs)]),simplify=FALSE),use.names=TRUE,fill=TRUE) %>%
        as.matrix()
      colnames(srs_stack) <- colnames(srs)[3:ncol(srs)]
      log_debug("Simulation")
      system.time({
        uniblock<-matrix(runif(nrow(srs_stack)*(ncol(nibrs)-ncol(srs))),nrow=nrow(srs_stack))
        
        colnames(uniblock) <- colnames(nibrs)[(nLHSVars+3):ncol(nibrs)]
		
        pre<-cbind(srs_stack,uniblock)
        #conditional sample from the copula
        c_sim<-try(cCopula(pre, cop, indices=(nLHSVars+1):dim(pre)[2],
                           inverse = TRUE))
      },gcFirst=FALSE) %>% print()
      if (any(class(c_sim)=="try-error")){
        stop()
      }
      log_debug("colnames(c_sim)")
      colnames(c_sim)<-colnames(pre)[(nLHSVars+1):dim(pre)[2]]
      print(colnames(c_sim))
      c_sim <- data.frame(c_sim)
      srs_stack <- data.frame(srs_stack)
      # log_debug("nrow(oris_stack)")
      # log_debug(nrow(oris_stack))
      # log_debug("nrow(srs_stack)")
      # log_debug(nrow(srs_stack))
      # log_debug("nrow(c_sim)")
      # log_debug(nrow(c_sim))
      #log_debug("sapply(c_sim,summary)")
      #print(sapply(c_sim,summary))
      #combine the imputed and reported ranks
      log_debug("srs_imp")
      system.time({
        #Update (21Mar2022): Switching from cbind to bind_cols - much faster
        #srs_imp<-cbind(oris_stack,srs_stack,c_sim)
        srs_imp<-bind_cols(oris_stack,counties_stack,srs_stack,c_sim)
      },gcFirst=FALSE) %>% print()
    } else if (nLHSVars==0){
      #Random sample (not conditioned)
      log_debug("nLHSVars==0")
      
      log_debug("Simulation")
      system.time({
        #Update (03MAR2022): Multiply nrow by stacks
        c_sim<-try(rCopula(n=nrow(srs)*stacks, cop))
        if (any(class(c_sim)=="try-error")){
          stop()
        }
      },gcFirst=FALSE) %>% print()
      log_debug("colnames(c_sim)")
      colnames(c_sim)<-colnames(nibrs)[3:ncol(nibrs)]#15:dim(pre)[2]]#16:dim(pre)[2]])
      print(colnames(c_sim))
      
      #Add the imputed ranks
      srs_imp<-cbind(oris_stack,
	                 counties_stack,
                     c_sim)
    }
    log_debug("Check c_sim for NAs")
    system.time({
      #Update (21Mar2022): Updating if(...) for efficiency
      #Update (11Oct2022): Including check for NaN alongside NA
      # if (c_sim %>% sapply(is.na) %>% subset(.==TRUE) %>% nrow() > 0){
      if (c_sim %>% as.matrix() %>% matrix(ncol=1) %>% {is.na(.)|is.nan(.)} %>% any()){
        print("NAs detected in c_sim.")
        probIndex <- c_sim %>% as.matrix() %>% {is.na(.)|is.nan(.)} %>% data.frame() %>% mutate(nNA=dplyr::select(.,everything()) %>% rowSums()) %>% {which(.$nNA>0)}
        
        
        #log_debug("length(probIndex)")
        #system.time({
        print(length(probIndex))
        #}) %>% print()
        #log_debug("nrow(c_sim)")
        #system.time({
        log_debug(nrow(c_sim))
        #}) %>% print()
        #log_debug("probORI")
        #system.time({
        probORI <- oris_stack[probIndex,] %>% unique()
        #}) %>% print()
        log_debug("head(probORI,n=20L)")
        #system.time({
        print(head(probORI,n=20L))
		
        probCounty <- counties_stack[probIndex,] %>% unique()
		log_debug("head(probCounty,n=20L)")
        #system.time({
        print(head(probCounty,n=20L))
		
        #}) %>% print()
        log_debug("probRaw")
        #system.time({
		#Note (03Jul2023): Orig had a subset() here but addition of county made me switch to a merge.data.table() call
        probRaw <- dat %>% merge.data.table(data.table(ORI=probORI,county=probCounty))
        #}) %>% print()
        #If max population among problem cases is less than 50, set c_sim to 0
        #log_debug("if (max(probRaw$popResidAgcy_cbi)<50){...} else{...}")
        #system.time({
        #Note (JDB 15MAY2022): Switch from popResidAgcy_cbi to lhsVars[1] (if lhsVars not empty)
        if (length(lhsVars)!=0){
          if (max(probRaw %>% dplyr::select(all_of(lhsVars[1])))<50){
            log_debug("Set c_sim to 0")
            c_sim[probIndex,] <- 0 #Before 18MAR2022 was 0.01
          } else {
            log_debug("Population too large")
            stop()
          }
        } else {
          log_debug("No LHS vars. Stop due to detected NAs.")
          stop()
        }
        # }) %>% print()
        
        # }
        # #combine imputed srs ranks with nibrs ranks
        # log_debug("check")
        # check<-rbind(srs_imp,nibrs)
        # t2<-try({
        #   check[,2:ncol(check)] %>%
        #     as.matrix() %>%
        #     corKendall(checkNA=FALSE)
        # })
        # if (any(class(t2)=="try-error")){
        #   stop()
      }
    },gcFirst=FALSE) %>% print()#else {
    
    #tcompare<-t2-t
    
    #need to convert imputed ranks into draws from marginal ECDFs...
    ##use quantile() function where the margins of x define the distributions and the imputed ranks are the
    ##input probabilities
    
    ##i think quantile() would be way too slow over all the points necessary (in this example ~8kX65)...
    ##instead, i've fit a loess (local regression) model to the data on the ranks (i.e., the model is a
    ##smoothed empirical inverse CDF)... it seems pretty fast.
    #log_debug("nibrs_ranks + nibrs_data")
    #system.time({
    log_debug("nibrs_data")
    nibrs_data <- working %>%
      subset(!is.na(eval(as.symbol(filterVar))))
    #}) %>% print()
    #create matrix same shape as c_sim - will replace predicted ranks with predicted values
    #Update (18FEB2022): Renaming from 'preds' to 'predsDat' to distinguish from parameter 'preds' (predictors)
    predsDat<-c_sim
    #log_debug("head(predsDat)")
    #head(predsDat) %>% print()
    log_debug("Convert ranks back to counts")
    system.time({
      #loop over imputed variables and create predicted values on scale of original variable
	  #Note (14Sep2023): Adding 1 to nibrs_data col index to account for inclusion of den in step 1
	  #Note (22Jan2024): Tweaking quantile() calls based on feedback from Lance - leaving original code commented-out just in case we revert
	  for (i in 1:dim(c_sim)[2]){
		if (step==1 & any(impVars=="p")){
	
			if (names(c_sim)[i]=="p"){
				if (nrow(nibrs_data[nibrs_data$den>0,])>0){
					predsDat[,i]<-nibrs_data[nibrs_data$den>0,nLHSVars+3+i] %>%
					  as.matrix() %>%
					  #quantile(c_sim[,i],type=8,na.rm=TRUE)
				      quantile(c_sim[,i],type=1,na.rm=TRUE)
				} else {
					predsDat[,i]<- 0
				}
			} else {
			predsDat[,i]<-nibrs_data[,nLHSVars+3+i] %>%
			  as.matrix() %>%
			  #quantile(c_sim[,i],type=8,na.rm=TRUE)
			  quantile(c_sim[,i],type=1,na.rm=TRUE)
			}
		} else {
			predsDat[,i]<-nibrs_data[,nLHSVars+2+i] %>%
				  as.matrix() %>%
				  #quantile(c_sim[,i],type=8,na.rm=TRUE)
				  quantile(c_sim[,i],type=1,na.rm=TRUE)
		}
		
        # pctls <- c_sim[,i] %>% unique()
        # #head(pctls) %>% print()
        # vals <- nibrs_data[,nLHSVars+1+i] %>%
        #   as.matrix() %>%
        #   quantile(pctls,type=8)
        # #head(vals) %>% print()
        # mapPctls <- data.frame(pctl=pctls,val=vals)
        # #head(mapPctls) %>% print()
        # # print(length(predsDat[,i]))
        # # data.frame(pctl=c_sim[,i]) %>%
        # #   left_join(mapPctls) %>%
        # #   nrow() %>%
        # #   print()
        # # data.frame(pctl=c_sim[,i]) %>%
        # #   left_join(mapPctls) %>%
        # #   .$val %>%
        # #   length() %>%
        # #   print()
        # predsDat[,i]<-plyr::mapvalues(c_sim[,i],from=mapPctls$pctls,to=mapPctls$vals)
        #head(predsDat[,i]) %>% print()
        #log_debug("head(predsDat)")
        #head(predsDat) %>% print()
        # 100 stacks, old method:
        #   user  system elapsed
        # 24.47    0.44   24.90
        # 100 stacks, new method:
        #   user  system elapsed
        # 36.84    0.02   36.86
      }
    },gcFirst=FALSE) %>% print()
	#Note (14Sep2023): Drop den after no longer needed
	if (step==1 & any(impVars=="p")){
		temp.dat <- temp.dat %>% select(-den)
		working <- working %>% select(-den)
		nibrs_data <- nibrs_data %>% select(-den)
	}
    if (stacks>1){
      log_debug("stacks adjustment")
      system.time({
        #Update (01Mar2022): Don't drop ORI here - instead, use to merge wiht srs_data
        predsDat<-oris_stack %>%
          data.frame() %>%
          cbind(counties_stack %>%
                  data.frame()) %>%
		  cbind(predsDat) %>%
          data.frame()
        # log_debug("sapply(predsDat,class)")
        # print(sapply(predsDat,class))
        # print('predsDat %>% subset(ORI=="AK0010500")')
        # print(predsDat %>% subset(ORI=="AK0010500"))
        # log_debug("impVars")
        # print(impVars)
        predsDat <- predsDat %>%
          group_by(ORI,county) %>%
          summarise(across(all_of(impVars),.fns=mean,.names="{.col}")) #%>%
        #rowwise() #%>%
      },gcFirst=FALSE) %>% print()
      #dplyr::select(-ORI )
      # log_debug("predsDat %>% head()")
      # print(predsDat %>% head())
      log_debug("srs_data")
      srs_data<- working %>%
        subset(is.na(eval(as.symbol(filterVar)))) %>%
        dplyr::select(ORI,county,all_of(lhsVars)) %>%
        #cbind(predsDat)
        merge.data.table(predsDat,by=c("ORI","county"))
    } else {#Update (01Mar2022): Added else condition
      log_debug("srs_data")
      srs_data<- working %>%
        subset(is.na(eval(as.symbol(filterVar)))) %>%
        dplyr::select(ORI,county,all_of(lhsVars)) %>%
        cbind(predsDat)
    }
    #append predicted values on to nonmissing portion of original SRS data
    #Note (01Mar2022): Merge by ORI, don't cbind
    
    # log_debug("sapply(srs_data,class)")
    # print(sapply(srs_data,class))
    #derive overall crime as product of p and sum of reported and imputed TOCs
    log_debug("Output temp.out")
    system.time({
      dropVars <- colnames(c_sim) %>% subset(. %in% colnames(dat)) #Variables to drop from original dataset
	  
	  log_debug("colnames(srs_data)")
      print(colnames(srs_data))
      #Note (JDB 12May2022): For temp.zero, keep only same variables as srs_data/nibrs_data variables in step 2
      if (step==2){
        temp.zero <- temp.zero %>%
          dplyr::select(ORI,county,lhsVars,impVars)
      }
	  
      temp.out <- rbindlist(list(srs_data,nibrs_data,temp.zero),use.names=TRUE,fill=TRUE) %>%
        data.frame() %>%
        dplyr::select(colnames(srs_data)) %>% #Prevents additional predictor variables in temp.zero from being carried into merge
        merge.data.table(dat %>% dplyr::select(-dropVars)) %>% #Merge with original dataset (dropping imputed variables)
        list()
      log_debug("names(temp.out)")
      names(temp.out) <- deparse(substitute(dat)) #Sets name of output dataset to name of input dataset #Sets name of output dataset to name of input dataset
      print(names(temp.out))
      list2env(temp.out,envir=outEnv) #Move output dataset to function environment (allows us to keep progress on subsequent loops)
    },gcFirst=FALSE) %>% print()
    #Note (JDB 13May2022): Commenting out return NULL and moving elsewhere
    #return(NULL)
    #}
  } else {#No SRS records -> no imputation necessary
    log_debug("No SRS records")
    #Update (JDB 26APR2022): Still edit output data (e.g., to reflect setting of NAs to 0s)
    temp.out <- rbindlist(list(temp.dat,temp.zero),use.names=TRUE,fill=TRUE) %>%
      data.frame() %>%
      list()
    log_debug("names(temp.out)")
    names(temp.out) <- deparse(substitute(dat)) #Sets name of output dataset to name of input dataset #Sets name of output dataset to name of input dataset
    print(names(temp.out))
    list2env(temp.out,envir=outEnv) #Move output dataset to function environment (allows us to keep progress on subsequent loops)
    
    #Note (JDB 13May2022): Commenting out return NULL and moving elsewhere
    #return(NULL)
  }
  #Note (JDB 13May2022): Adding return NULL [replaces 2 return NULL statements]
  return(NULL)
}

#Version without SRS variables

#Version with SRS variables
#Note (19APR2022): Adding 'table' as a parameter (mostly for status table)
#Note (19APR2022): Adding imputation variables to status table as an explicit column (prior: as row name)
#Note (31MAR2023): Adding support for other ACS vars (e.g., income to poverty ratio)
getStep1Imp <- function(dat,table,popVar,demoVars,othACSVars,lhsTOCs,impVars,stacks,outEnv=.GlobalEnv,nImpVars=length(impVars)){
  log_debug("Running function getStep1Imp")
  log_debug(system("free -mh", intern = FALSE))
  #Setup - create indicators for what to include in copula
  noNIBRSInd <- FALSE #Are there no NIBRS LEAs?
  constPopInd <- FALSE #Is population variable constant for NIBRS LEAs but not for SRS LEAs?
  constInd <- rep.int(FALSE,nImpVars) #Is impuation column constant for NIBRS LEAs?
  tryFullLHS <- rep.int(FALSE,nImpVars) #1. Full LHS (overall pop served, demo distributions),
  tryRedLHS <- rep.int(FALSE,nImpVars) #2. Reduce LHS to overall pop only
  #tryIndTOC <- rep.int(FALSE,nImpVars) #3.	Target individual TOCs
  tryIndTOCa <- rep.int(FALSE,nImpVars) #a.	Individual TOC with full LHS (overall pop served, demo distributions)
  tryIndTOCb <- rep.int(FALSE,nImpVars) #b.	Individual TOC with reduced LHS (overall pop)
  tryIndTOCc <- rep.int(FALSE,nImpVars) #c.	Individual TOC with no LHS
  failInd <- rep.int(FALSE,nImpVars)
  funcEnv <- environment()
  
  temp.dat <- data.frame(dat)
  
  nNIBRS <- temp.dat %>%
    subset(!is.na(eval(as.symbol(impVars[1])))) %>%
    nrow()
  #log_debug("nNIBRS")
  #print(nNIBRS)
  if (nNIBRS==0){
    #log_debug("No NIBRS")
    noNIBRSInd <- TRUE
    failInd <- rep(TRUE,nImpVars)
  } else {
    # log_debug("sdPopNIBRS - feed-in data preview")
    # temp.dat %>%
    #   subset(!is.na(eval(as.symbol(impVars[1])))) %>%
    #   dplyr::select(popVar) %>%
    #   print()
    sdPopNIBRS <- temp.dat %>%
      subset(!is.na(eval(as.symbol(impVars[1])))) %>%
      dplyr::select(popVar) %>%
      sapply(sd,na.rm=TRUE)
    sdPopNIBRS[is.na(sdPopNIBRS)] <- 0
    sdPopSRS <- temp.dat %>%
      subset(is.na(eval(as.symbol(impVars[1])))) %>%
      dplyr::select(popVar) %>%
      sapply(sd,na.rm=TRUE)
    sdPopSRS[is.na(sdPopSRS)] <- 0
    
    meanPopNIBRS <- temp.dat %>%
      subset(!is.na(eval(as.symbol(impVars[1])))) %>%
      dplyr::select(popVar) %>%
      sapply(mean,na.rm=TRUE)
    meanPopSRS <- temp.dat %>%
      subset(is.na(eval(as.symbol(impVars[1])))) %>%
      dplyr::select(popVar) %>%
      sapply(mean,na.rm=TRUE)
    log_debug("sdPopNIBRS")
    print(sdPopNIBRS)
    log_debug("sdPopSRS")
    print(sdPopSRS)
    log_debug("meanPopNIBRS")
    print(meanPopNIBRS)
    log_debug("meanPopSRS")
    print(meanPopSRS)
    constPopInd <- (sdPopNIBRS==0 & ((sdPopSRS==0 & meanPopNIBRS != meanPopSRS)|sdPopSRS!=0))
    
    
    
    constInd <- temp.dat %>%
      subset(!is.na(eval(as.symbol(impVars[1])))) %>%
      dplyr::select(impVars) %>%
      sapply(sd,na.rm=TRUE) %>%
      {(. == 0)}
    constInd[is.na(constInd)] <- TRUE
    if (any(constInd==TRUE)){#Set imputed values for constant variables
      sapply(1:nImpVars,function(i){
        if (constInd[i]==TRUE){
          constVal <- temp.dat %>%
            subset(!is.na(eval(as.symbol(impVars[i])))) %>%
            dplyr::select(impVars[i]) %>%
            apply(mean,MARGIN=2)
          temp.dat <- temp.dat %>%
            mutate(!!impVars[i] := constVal)
        }
        list2env(list("temp.dat"=temp.dat),envir=funcEnv)
        return(NULL)
      })
    }
    if (constPopInd==FALSE){
      if (!(is.null(popVar)|is.null(demoVars)|is.null(othACSVars))){
        tryFullLHS <- !constInd
      } else if (!is.null(popVar)){
        tryFullLHS <- rep.int(FALSE,nImpVars)
        tryRedLHS <- !constInd
      } else {
        tryFullLHS <- rep.int(FALSE,nImpVars)
        tryRedLHS <- rep.int(FALSE,nImpVars)
        tryIndTOCa <- rep.int(FALSE,nImpVars)
        tryIndTOCb <- rep.int(FALSE,nImpVars)
        tryIndTOCc <- !constInd
      }
    } else {
      tryFullLHS <- rep.int(FALSE,nImpVars)
      tryRedLHS <- rep.int(FALSE,nImpVars)
      tryIndTOC <- rep.int(FALSE,nImpVars)
      tryIndTOCa <- rep.int(FALSE,nImpVars)
      tryIndTOCb <- rep.int(FALSE,nImpVars)
      tryIndTOCc <- rep.int(FALSE,nImpVars)
      tryIndTOCd <- rep.int(FALSE,nImpVars)
      failInd <- rep.int(TRUE,nImpVars)
      
    }
    
    ###############
    #Run reductionary steps 1-3
    if (any(tryFullLHS==TRUE)){
      log_debug("********************")
      log_debug("Try Step 1")
      result <- try(getCopImp(temp.dat,step=1,lhsVars=c(popVar,demoVars,othACSVars),impVars=impVars[tryFullLHS],stacks=stacks,outEnv=funcEnv))
      if (any(class(result)=="try-error")){
        tryRedLHS <- tryFullLHS
      } else {
        log_debug("Success!")
      }
    }
    if (any(tryRedLHS==TRUE)){
      log_debug("********************")
      log_debug("Try Step 2")
      result <- try(getCopImp(temp.dat,step=1,lhsVars=c(popVar),impVars=impVars[tryRedLHS],stacks=stacks,outEnv=funcEnv))
      if (any(class(result)=="try-error")){
        log_debug("Failed Step 2")
        if (!(is.null(popVar)|is.null(demoVars)|is.null(othACSVars))){
          tryIndTOCa <- tryRedLHS
        } else {
          tryIndTOCb <- tryRedLHS
        }
      } else {
        log_debug("Success!")
      }
    }
    if (any(tryIndTOCa==TRUE|tryIndTOCb==TRUE|tryIndTOCc==TRUE)){
      sapply(1:nImpVars,function(i){
        if (tryIndTOCa[i]==TRUE|tryIndTOCb[i]==TRUE|tryIndTOCc[i]==TRUE){
          log_debug("********************")
          log_debug(paste0("Imputation column: ",impVars[i]))
        }
        if (tryIndTOCa[i]==TRUE){
          log_debug("**********")
          log_debug("Try Step 3a")
          result <- try(getCopImp(temp.dat,step=1,lhsVars=c(popVar,demoVars,othACSVars),impVars=impVars[i],stacks=stacks,outEnv=funcEnv))
          
          if (any(class(result)=="try-error")){
            tryIndTOCb[i] <- TRUE
            
          } else {
            log_debug("Success!")
          }
        }
        if (tryIndTOCb[i]==TRUE){
          log_debug("**********")
          log_debug("Try Step 3b")
          result <- try(getCopImp(temp.dat,step=1,lhsVars=c(popVar),impVars=impVars[i],stacks=stacks,outEnv=funcEnv))
          if (any(class(result)=="try-error")){
            if (constInd==FALSE){
              tryIndTOCc[i] <- TRUE
            } else {
              
              log_debug("Total failure.")
              failInd[i] <- TRUE
            }
          } else {
            log_debug("Success!")
          }
        }
        if (tryIndTOCc[i]==TRUE){
          log_debug("**********")
          log_debug("Try Step 3c")
          result <- try(getCopImp(temp.dat,step=1,lhsVars=NULL,impVars=impVars[i],stacks=stacks,outEnv=funcEnv))
          if (any(class(result)=="try-error")){
            log_debug("Total failure.")
            failInd[i] <- TRUE
          } else {
            log_debug("Success!")
          }
        }
        list2env(list("tryIndTOCa"=tryIndTOCa,
                      "tryIndTOCb"=tryIndTOCb,
                      "tryIndTOCc"=tryIndTOCc,
                      "failInd"=failInd),
                 envir=funcEnv)
        #Note (JDB 13May2022): Adding return(NULL)
        return(NULL)
      })
    }
  }
  out <- data.frame(temp.dat) %>%
    list()
  #log_debug("names(out)")
  names(out) <- deparse(substitute(dat))
  #print(names(out))
  #list2env(out,.GlobalEnv)
  #log_debug("parent.frame()")
  #print(parent.frame())
  #log_debug("environment()")
  #print(environment())
  list2env(out,outEnv)
  
  
  log_debug("********************")
  log_debug("Final status:")
  
  #Note (20Apr2022): Ensuring that indicators are logicals / removing variable names
  noNIBRSInd <- as.logical(noNIBRSInd)
  constPopInd <- as.logical(constPopInd)
  constInd <- as.logical(constInd)
  tryFullLHS <- as.logical(tryFullLHS)
  tryRedLHS <- as.logical(tryRedLHS)
  tryIndTOCa <- as.logical(tryIndTOCa)
  tryIndTOCb <- as.logical(tryIndTOCb)
  tryIndTOCc <- as.logical(tryIndTOCc)
  failInd <- as.logical(failInd)
  
  status <- data.frame(table,
                       impVar=impVars,
                       noNIBRSInd,
                       constPopInd,
                       constInd,
                       tryFullLHS,
                       tryRedLHS,
                       tryIndTOCa,
                       tryIndTOCb,
                       tryIndTOCc,
                       failInd)
  status %>%
    print()
  return(status)
}



########
#Imputation step 2 function
#function to calculate proportional ranks
rankem2 <- function(i) {
  #10May2023: Setting seed
  set.seed(1)
  log_debug("Running function rankem2")
  log_debug(system("free -mh", intern = FALSE))
  #Note (22Jan2024): tweaking based on suggestions by Lance... leaving old code in for now, in case we end up reverting
  #rank(i,na.last="keep",ties.method="random")/(sum(is.na(i)==FALSE)+0.01)
  rank(i,na.last="keep",ties.method="min")/(sum(is.na(i)==FALSE)+1)
}
#Note (19APR2022): Including 'table' in status table
#Note (31MAR2023): Adding support for other ACS vars (e.g., income to poverty ratio)
getStep2Imp <- function(dat,tier,types,table,sections,rows,popVar,demoVars,othACSVars,benchmark,stacks,outEnv=.GlobalEnv,nsections=length(sections)){
  log_debug("Running function getStep2Imp")
  log_debug(system("free -mh", intern = FALSE))
  #Extract column
  column <- str_extract(benchmark,"(?<=_)\\d{1,5}$")
  log_debug(paste0("Start column #", column))
  
  #log_debug("nsections (Start)")
  #print(nsections)
  
  #Update (12APR2022): Remove any sections where 'rows' is empty and update section-related variables
  delSections <- which(lengths(rows)==0)
  if (length(delSections)>0){
    types <- types[-delSections]
    sections <- sections[-delSections]
    nsections <- length(sections)
    rows <- rows[-delSections]
  }
  
  #log_debug("nsections (Update #1)")
  #print(nsections)
  log_debug("Constructing row variables (impVars)")
  if (nsections>1 & length(rows)>1){
    impVars <- sapply(1:nsections,function(j){
      print(rows[[j]])
      #Update (11Mar2022): Alter variable list construction to allow treating 9 and 10 as same section
      #return(paste0("t_",table,"_",sections[[j]],"_",rows[[j]],"_",column))
      return(colnames(dat) %>%
               str_subset(paste0("^t_",table,"_.*_(",str_flatten(rows[[j]],col="|"),")_",column,"$")))
    },simplify=FALSE)
    
  } else if (nsections==1){ #Single section
    impVars <- colnames(dat) %>%
      str_subset(paste0("^t_",table,"_.*_(",str_flatten(rows[[1]],col="|"),")_",column,"$")) %>%
      list()
  } else {
    impVars <- character(0) %>% list()
  }
  
  #Look for empty variable lists
  delSections <- which(lengths(impVars)==0)
  if (length(delSections)>0){
    types <- types[-delSections]
    sections <- sections[-delSections]
    nsections <- length(sections)
    rows <- rows[-delSections]
    impVars <- impVars[-delSections]
  }
  #log_debug("nsections (Update #2)")
  #print(nsections)
  #Update (12APR2022): Only run code if nsections>0
  if (nsections>0){
    
    #Setup - create indicators for what to include in copula
    
    zeroColInd <- rep.int(FALSE,nsections)
    constRowGpInd <- rep.int(FALSE,nsections)
    tryFullLHS <- rep.int(TRUE,nsections) #1. Full LHS (overall pop served, demo distributions),
    tryRedLHS <- rep.int(FALSE,nsections) #2. Reduce LHS to just pop served
    tryIndRowGp <- rep.int(FALSE,nsections) #3.	Target individual row groups with full LHS (overall pop served, demo distributions), then, within individual columns that still don’t work
    tryIndRowGpa <- rep.int(FALSE,nsections) #a.	Individual row groups with reduced LHS (nonmissing TOCs)
    tryIndRowGpb <- rep.int(FALSE,nsections) #b.	Individual row groups with no LHS (overall)
    #tryIndRowGpc <- rep.int(0,nImpVars) #c.	???
    failInd <- rep.int(FALSE,nsections)
    
    funcEnv <- environment()
    
    
    temp.dat <- data.frame(dat)
    
    
    print(impVars)
    sapply(1:nsections,function(j){
      temp.type <- types[j]
      temp.section <- sections[j]
      if (temp.type==2){
        paste0("Section ",temp.section,": Creating category so that rows will sum to the toc total") %>%
          print()
        temp.balVar <- paste0("t_",table,"_",temp.section,"_999_",column)
        temp.dat <- temp.dat %>%
          mutate(temp.sumImpVars=dplyr::select(.,all_of(impVars[[j]])) %>%
                   rowSums(na.rm=TRUE),
                 !!temp.balVar := case_when(is.na(eval(as.symbol(impVars[[j]][1])))==FALSE ~ eval(as.symbol(benchmark))-temp.sumImpVars,
                                            TRUE ~ NA_real_)) %>%
          dplyr::select(-temp.sumImpVars)
        
        impVars[[j]] <- c(impVars[[j]],temp.balVar)
        list2env(list("temp.dat"=temp.dat,"impVars"=impVars),envir=funcEnv) #Move updated temp.dat and rowVars outside sapply
        
      } else if (temp.type==3){
        paste0("Section ",temp.section,": Creating p variable for non-mutually-exclusive variables") %>%
          print()
        #Note (23Jun2022): Ensure 1 'p' variable per subsection if multiple subsections
        temp.index <- data.frame(section=sections,type=types) %>%
          mutate(rowAll=1:nrow(.)) %>%
          subset(section==temp.section) %>%
          subset(type==3) %>%
          mutate(rowType=1:nrow(.)) %>%
          subset(rowAll==j) %>%
          .$rowType
        #log_debug("temp.pVar")
        temp.pVar <- paste0("t_",table,"_",temp.section,"_p",temp.index,"_",column)
        # print(temp.pVar)
        # log_debug("impVars[[j]]")
        # print(impVars[[j]])
        # log_debug("temp.dat %>% dplyr::select(benchmark) %>% head()")
        # print(temp.dat %>% dplyr::select(benchmark) %>% head())
        temp.dat <- temp.dat %>%
          mutate(temp.sumImpVars=dplyr::select(.,all_of(impVars[[j]])) %>%
                   rowSums(na.rm=TRUE),
                 !!temp.pVar := case_when(is.na(eval(as.symbol(impVars[[j]][1])))==FALSE ~ temp.sumImpVars/eval(as.symbol(benchmark)),
                                          TRUE ~ NA_real_)) %>%
          dplyr::select(-temp.sumImpVars)
        
        impVars[[j]] <- c(impVars[[j]],temp.pVar)
        #log_debug("All NIBRS preview")
        #head(temp.dat %>% subset(is.na(eval(as.symbol(impVars[[j]][1])))==FALSE) %>% dplyr::select(benchmark,impVars[[j]])) %>% print()
        #log_debug("NIBRS, benchmark >0 preview")
        #head(temp.dat %>% subset(is.na(eval(as.symbol(impVars[[j]][1])))==FALSE & eval(as.symbol(benchmark))>0) %>% dplyr::select(benchmark,impVars[[j]])) %>% print()
        list2env(list("temp.dat"=temp.dat,"impVars"=impVars),envir=funcEnv) #Move updated temp.dat and rowVars outside sapply
      }
      #Note (JDB 13May2022): return NULL
      return(NULL)
    })
    nZero <- temp.dat %>%
      subset(eval(as.symbol(benchmark))==0) %>%
      nrow()
    if (nZero==nrow(temp.dat)){
      log_debug("All LEAs have benchmark=0. Setting all imputation variables to 0")
      zeroColInd <- rep.int(TRUE,nsections)
      tryFullLHS <- !zeroColInd
      temp.dat <- temp.dat %>%
        mutate_at(.vars=impVars %>% unlist,.funs=~0)
    } else {
      
      #Check for constant imputation variables
      
      sapply(1:nsections,function(i){
        temp.constInd <- temp.dat %>%
          subset(eval(as.symbol(benchmark))>0 & !is.na(eval(as.symbol(impVars[[i]][1])))) %>%
          dplyr::select(impVars[[i]]) %>%
          sapply(sd,na.rm=TRUE) %>%
          {(. == 0)}
        #log_debug("temp.constInd")
        #print(temp.constInd)
        temp.constInd[is.na(temp.constInd)] <- TRUE #In case only single LEA non-missing for variable
        #log_debug("temp.constInd (after fixing NAs)")
        #print(temp.constInd)
        if (any(temp.constInd==TRUE)){#Set imputed values for constant variables
          sapply(1:length(impVars[[i]]),function(j){
            #log_debug("temp.constInd")
            #print(temp.constInd)
            if (temp.constInd[j]==TRUE){
              temp.constVal <- temp.dat %>%
                subset(eval(as.symbol(benchmark))>0 & !is.na(eval(as.symbol(impVars[[i]][j])))) %>%
                dplyr::select(impVars[[i]][j]) %>%
                apply(mean,MARGIN=2)
              temp.dat <- temp.dat %>%
                mutate(!!impVars[[i]][j] := case_when(!is.na(eval(as.symbol(benchmark))) ~ temp.constVal,
                                                      TRUE ~ 0))
            }
            list2env(list("temp.dat"=temp.dat),envir=funcEnv)
            return(NULL)
          })
        }
        impVars[[i]] <- impVars[[i]][!temp.constInd] #Edit list of imputation variables
        constRowGpInd[i] <- length(impVars[[i]])==0
        if (!(is.null(popVar)|is.null(demoVars)|is.null(othACSVars))){
          tryFullLHS[i] <- !length(impVars[[i]])==0
          #Move updated temp.dat and indicators outside sapply
          list2env(list("impVars"=impVars,
                        "constRowGpInd"=constRowGpInd,
                        "tryFullLHS"=tryFullLHS),
                   envir=funcEnv)
        } else if (!is.null(popVar)){
          tryFullLHS[i] <- FALSE
          tryRedLHS[i] <- !length(impVars[[i]])==0
          list2env(list("impVars"=impVars,
                        "constRowGpInd"=constRowGpInd,
                        "tryFullLHS"=tryFullLHS,
                        "tryRedLHS"=tryRedLHS),
                   envir=funcEnv)
        } else {
          tryFullLHS[i] <- FALSE
          tryIndRowGpb[i] <- !length(impVars[[i]])==0
          list2env(list("impVars"=impVars,
                        "constRowGpInd"=constRowGpInd,
                        "tryFullLHS"=tryFullLHS,
                        "tryIndRowGpb"=tryIndRowGpb),
                   envir=funcEnv)
        }
        #Note (JDB 13May2022): return NULL
        return(NULL)
      })
      #log_debug("impVars")
      #print(impVars)
      ###############
      #Run reductionary steps 1-3
      if (any(tryFullLHS==TRUE)){
        log_debug("Try Step 1")
        #Note (JDB 13May2022): creating reduced dataset to reduce size of output dataset... only merge new results if step successful
        temp.working <- data.frame(temp.dat) %>%
          dplyr::select(ORI,county,popVar,demoVars,othACSVars,all_of(benchmark),impVars[tryFullLHS] %>% unlist())
        result <- try(getCopImp(temp.working,step=2,lhsVars=c(popVar,demoVars,othACSVars),impVars=impVars[tryFullLHS] %>% unlist(),benchmark=benchmark,stacks=stacks,outEnv=funcEnv))
        if (any(class(result)=="try-error")){
          paste0("Failed Step 1") %>%
            print()
          #tryRedLHS <- 1
          tryIndRowGp <- tryFullLHS
        } else {
          print("temp.working")
          temp.working <- temp.working %>%
            dplyr::select(ORI,county,impVars[tryFullLHS] %>% unlist())
          print("temp.dat")
          temp.dat <- temp.dat %>%
            dplyr::select(-(impVars[tryFullLHS] %>% unlist())) %>%
            merge.data.table(temp.working,by=c("ORI","county"))
        }
      }
      if (any(tryRedLHS==1)){
        log_debug("Try Step 2")
        #Note (JDB 13May2022): creating reduced dataset to reduce size of output dataset... only merge new results if step successful
        temp.working <- data.frame(temp.dat) %>%
          dplyr::select(ORI,county,popVar,all_of(benchmark),impVars[tryRedLHS] %>% unlist())
        result <- try(getCopImp(temp.working,step=2,lhsVars=c(popVar),impVars=impVars[tryRedLHS] %>% unlist(),benchmark=benchmark,stacks=stacks,outEnv=funcEnv))
        if (any(class(result)=="try-error")){
          log_debug("Failed Step 2")
          tryIndRowGpa <- tryRedLHS
        } else {
          temp.working <- temp.working %>%
            dplyr::select(ORI,county,impVars[tryRedLHS] %>% unlist())
          temp.dat <- temp.dat %>%
            dplyr::select(-(impVars[tryRedLHS] %>% unlist())) %>%
            merge.data.table(temp.working,by=c("ORI","county"))
        }
      }
      #print(tryIndTOC)
      #print(any(tryIndTOC==1))
      if (any(tryIndRowGp==TRUE|tryIndRowGpa==TRUE|tryIndRowGpb==TRUE)){
        sapply(1:nsections,function(i){
          #Note (JDB 13May2022): Tracking current environment within sapply - will use this instead of funcEnv for step 3/3a/3b
          funcEnv2 <- environment()
          #print(tryIndRowGp[i])
          if (tryIndRowGp[i]==TRUE|tryIndRowGpa[i]==TRUE|tryIndRowGpb[i]==TRUE){
            log_debug("********************")
            log_debug(paste0("Row section: ",sections[i]))
          }
          if (tryIndRowGp[i]==TRUE){
            log_debug("Try Step 3")
            #Note (JDB 13May2022): creating reduced dataset to reduce size of output dataset... only merge new results if step successful
            temp.working <- data.frame(temp.dat) %>%
              dplyr::select(ORI,county,popVar,demoVars,othACSVars,all_of(benchmark),impVars[[i]])
            result <- try(getCopImp(temp.working,step=2,lhsVars=c(popVar,demoVars,othACSVars),impVars=impVars[[i]],benchmark=benchmark,stacks=stacks,outEnv=funcEnv2))
            if (any(class(result)=="try-error")){
              tryIndRowGpa[i] <- TRUE
            } else {
              temp.working <- temp.working %>%
                dplyr::select(ORI,county,impVars[[i]])
              temp.dat <- temp.dat %>%
                dplyr::select(-impVars[[i]]) %>%
                merge.data.table(temp.working,by=c("ORI","county"))
            }
          }
          if (tryIndRowGpa[i]==TRUE){
            log_debug("Try Step 3a")
            #Note (JDB 13May2022): creating reduced dataset to reduce size of output dataset... only merge new results if step successful
            temp.working <- data.frame(temp.dat) %>%
              dplyr::select(ORI,county,popVar,all_of(benchmark),impVars[[i]])
            result <- try(getCopImp(temp.working,step=2,lhsVars=c(popVar),impVars=impVars[[i]],benchmark=benchmark,stacks=stacks,outEnv=funcEnv2))
            
            if (any(class(result)=="try-error")){
              tryIndRowGpb[i] <- TRUE
            } else {
              temp.working <- temp.working %>%
                dplyr::select(ORI,county,impVars[[i]])
              temp.dat <- temp.dat %>%
                dplyr::select(-impVars[[i]]) %>%
                merge.data.table(temp.working,by=c("ORI","county"))
            }
          }
          if (tryIndRowGpb[i]==TRUE){
            log_debug("Try Step 3b")
            #log_debug("impVars[[i]]")
            #print(impVars[[i]])
            #Note (JDB 13May2022): creating reduced dataset to reduce size of output dataset... only merge new results if step successful
            temp.working <- data.frame(temp.dat) %>%
              dplyr::select(ORI,county,all_of(benchmark),impVars[[i]])
            #Note (21Jun2022): Changing from temp.dat as function input to temp.working
            result <- try(getCopImp(temp.working,step=2,lhsVars=NULL,impVars=impVars[[i]],benchmark=benchmark,stacks=stacks,outEnv=funcEnv2))
            if (any(class(result)=="try-error")){
              #tryIndTOCc[i] <- 1
              log_debug("Total failure.")
              failInd[i] <- TRUE
              
            }  else {
              temp.working <- temp.working %>%
                dplyr::select(ORI,county,impVars[[i]])
              temp.dat <- temp.dat %>%
                dplyr::select(-impVars[[i]]) %>%
                merge.data.table(temp.working,by=c("ORI","county"))
            }
          }
          # if (tryIndTOCc[i]==1){
          #   log_debug("Try Step 3c")
          #   result <- try(getCopImp(temp.dat,step=1,lhsVars=c(popVar),impVars=impVars[i],stacks=stacks,outEnv=funcEnv2))
          #   if (any(class(result)=="try-error")){
          #     log_debug("Total failure.")
          #   }
          #}
          #Note (JDB 13May2022): Only run list2env() if actually ran step 3/3a/3b for column
          #Note (JDB 13May2022): Include updated temp.dat in list2env()
          if (any(tryIndRowGp[i]==TRUE|tryIndRowGpa[i]==TRUE|tryIndRowGpb[i]==TRUE)){
            list2env(list("tryIndRowGp"=tryIndRowGp,
                          "tryIndRowGpa"=tryIndRowGpa,
                          "tryIndRowGpb"=tryIndRowGpb,
                          #"tryIndTOCc"=tryIndTOCc,
                          "failInd"=failInd,
                          "temp.dat"=temp.dat),
                     envir=funcEnv)
            
          }
          #Note (JDB 13May2022): Return NULL
          return(NULL)
        })
      }
    }
    
    out <- data.frame(temp.dat) %>%
      list()
    #log_debug("names(out)")
    names(out) <- deparse(substitute(dat))
    #print(names(out))
    list2env(out,outEnv)
    #log_debug("parent.frame() [Step 2]")
    #print(parent.frame())
    #list2env(out,parent.frame())
    log_debug("Final status:")
    status <- data.frame(table,
                         column,
                         tier,
                         section=sections,
                         zeroColInd,
                         constRowGpInd,
                         tryFullLHS,
                         tryRedLHS,
                         tryIndRowGp,
                         tryIndRowGpa,
                         tryIndRowGpb,
                         #tryIndTOCc,
                         failInd
    )
    status %>%
      print()
  } else {#No sections after removing empty sections
    log_debug("No sections to process. Skip.")
    status <- data.frame()
  }
  return(status)
}


#Ratio adjustment function (to pair with copula imputation)

#Update (01Mar2022): Bringing function parameters in line with step 2 imputation
#                    We don't be using some of them (e.g., popVar, demoVars) but leave for now in case merge with imp function
#Note (19APR2022): Adding 'table' to status table
#Note (31MAR2023): Adding support for other ACS vars (e.g., income to poverty ratio)
#getRatAdj <- function(dat,rowVars,types,benchmark){
getRatAdj <- function(dat,tier,types,table,sections,rows,popVar,demoVars,othACSVars,benchmark,stacks,eps=0.0001,outEnv=.GlobalEnv,nsections=length(sections)){
  log_debug("Running function getRatAdj")
  log_debug(system("free -mh", intern = FALSE))
  #Retrieve name of dat dataframe
  datName <- deparse(substitute(dat))
  
  #log_debug("datName")
  #print(datName)
  
  funcEnv <- environment()
  column <- str_extract(benchmark,"(?<=_)\\d{1,5}$")
  log_debug(paste0("Start column #", column))
  
  #Update (12MAR2022): Remove any sections where 'rows' is empty and update section-related variables
  delSections <- which(lengths(rows)==0)
  if (length(delSections)>0){
    types <- types[-delSections]
    sections <- sections[-delSections]
    nsections <- length(sections)
    rows <- rows[-delSections]
  }
  
  temp.dat <- data.frame(dat)
  #Note (01Feb2022): Switching here on down from 'rowVars' to 'impVars' (in line with step 2 imp function)
  log_debug("Constructing row variables (impVars)")
  if (nsections>1 & length(rows)>1){
    impVars <- sapply(1:nsections,function(j){
      #Update (11Mar2022): Alter variable list construction to allow treating 9 and 10 as same section
      #temp.impVars <- paste0("t_",table,"_",sections[j],"_",rows[[j]],"_",column)
      temp.impVars <- colnames(dat) %>%
        str_subset(paste0("^t_",table,"_.*_(",str_flatten(rows[[j]],col="|"),")_",column,"$"))
      if (types[[j]]==2 & length(temp.impVars)>0){
        temp.impVars <- c(temp.impVars,paste0("t_",table,"_",sections[j],"_999_",column))
      } else if (types[[j]]==3 & length(temp.impVars)>0){
        temp.index <- data.frame(section=sections,type=types) %>%
          mutate(rowAll=1:nrow(.)) %>%
          subset(section==sections[j]) %>%
          subset(type==3) %>%
          mutate(rowType=1:nrow(.)) %>%
          subset(rowAll==j) %>%
          .$rowType
        
        temp.impVars <- c(temp.impVars,paste0("t_",table,"_",sections[j],"_p",temp.index,"_",column))
      }
      return(temp.impVars)
    },simplify=FALSE)
    
  } else if (nsections==1){ #Single section
    impVars <- colnames(dat) %>%
      str_subset(paste0("^t_",table,"_.*_(",str_flatten(rows[[1]],col="|"),")_",column,"$"))
    if (types==2 & length(impVars)>0){
      impVars <- c(impVars,paste0("t_",table,"_",sections,"_999_",column))
    } else if (types==3 & length(impVars)>0){
      #Note (23Jun2022): Ensure 1 'p' variable per subsection if multiple subsections
      temp.index <- data.frame(section=sections,type=types) %>%
        mutate(rowAll=1:nrow(.)) %>%
        subset(section==sections[1]) %>%
        subset(type==3) %>%
        mutate(rowType=1:nrow(.)) %>%
        subset(rowAll==1) %>%
        .$rowType
      
      impVars <- c(impVars,paste0("t_",table,"_",sections[1],"_p",temp.index,"_",column))
    }
    impVars <- impVars %>% list()
  } else {
    impVars <- character(0) %>% list()
  }
  
  #Look for empty variable lists
  delSections <- which(lengths(impVars)==0)
  if (length(delSections)>0){
    types <- types[-delSections]
    sections <- sections[-delSections]
    nsections <- length(sections)
    rows <- rows[-delSections]
    impVars <- impVars[-delSections]
  }
  
  if (nsections>0){#only run code if nsections>0
    
    failInd <- rep.int(FALSE,nsections)
    
    #log_debug("dat %>% subset(is.na(eval(as.symbol(impVars[[1]][1])))) %>% nrow()")
    #print(dat %>% subset(is.na(eval(as.symbol(impVars[[1]][1])))) %>% nrow())
    status <- sapply(1:length(rows),function(i){
      temp.impVars <- impVars[[i]]
      temp.type <- types[i]
      log_debug("temp.impVars")
      print(temp.impVars)
      if (temp.type %in% c(1,2)){
        #log_debug("temp.dat")
        #temp.dat %>% subset(ORI %in% c("GA1360100","TX1120000")) %>% dplyr::select(ORI,benchmark,all_of(temp.impVars)) %>% print()
        #Update (07MAR2022): Adding new 'bench' variable
        temp.dat <- temp.dat %>%
          mutate(bench=eval(as.symbol(benchmark))) %>%
          
          mutate(sumImpVars=dplyr::select(.,temp.impVars) %>%
                   rowSums(na.rm=TRUE),
                 ratio=ifelse(sourceInd=="NIBRS",
                              1,
                              ifelse(sumImpVars>0,
                                     #eval(as.symbol(benchmark))/sumImpVars,
                                     bench/sumImpVars,
                                     NA_real_)
                 )
          )
        #log_debug("summary(temp.dat$ratio)")
        #print(summary(temp.dat$ratio))
        #log_debug("Records where ratio==Inf (before ratio adjustment)")
        #temp.dat %>% subset(ratio==Inf) %>% dplyr::select(benchmark,all_of(temp.impVars)) %>% head() %>% print()
        #log_debug("temp.dat [v1]")
        #temp.dat %>% subset(ORI %in% c("GA1360100","TX1120000")) %>% dplyr::select(ORI,benchmark,all_of(temp.impVars)) %>% print()
        #Update (03MAR2022): Switching from mutate_each() to mutate(across())
        temp.dat <- temp.dat %>%
          #mutate_each(funs(.*ratio),temp.impVars) %>%
          mutate(across(all_of(temp.impVars),.fns=~.*ratio)) %>%
          mutate(sumImpVarsNew=dplyr::select(.,all_of(temp.impVars)) %>%
                   rowSums(na.rm=TRUE)) %>%
          mutate(match=ifelse(sourceInd=="NIBRS",
                              TRUE,
                              #abs(sumImpVarsNew-eval(as.symbol(benchmark)))<eps
                              abs(sumImpVarsNew-bench)<eps
          )
          )
        
        #temp.dat$sumImpVars %>% summary() %>% print()
        #temp.dat$ratio %>% summary() %>% print()
        #log_debug("Records where ratio==Inf (after ratio adjustment)")
        #temp.dat %>% subset(ratio==Inf) %>% dplyr::select(benchmark,all_of(temp.impVars)) %>% head() %>% print()
        #log_debug("temp.dat [v2]")
        #temp.dat %>% subset(ORI %in% c("GA1360100","TX1120000")) %>% dplyr::select(ORI,benchmark,all_of(temp.impVars)) %>% print()
        temp.dat %>% group_by(match) %>% summarize(n=n()) %>% print()
        if (temp.dat %>% subset(match == FALSE|is.na(match)) %>% nrow() > 0 ){
          log_debug("Discrepancies / match is missing")
          temp.dat %>% subset(match != TRUE|is.na(match)) %>% dplyr::select(ORI,county,benchmark,all_of(temp.impVars)) %>% head() %>% print()
          #if (temp.dat %>% subset(match==TRUE & eval(as.symbol(benchmark))>0) %>% nrow() > 0){
          if (temp.dat %>% subset(match==TRUE & bench>0) %>% nrow() > 0){
            #log_debug("temp.dat %>% subset(match==TRUE & eval(as.symbol(benchmark))>0) %>% dplyr::select(benchmark,all_of(temp.impVars)) %>% head(n=3000L)")
            # write_csv(temp.dat %>% subset(match==TRUE & eval(as.symbol(benchmark))>0)%>% dplyr::select(ORI,benchmark,all_of(temp.impVars)),
            #           file="C:/Users/jbunker/Documents/Temp/test.csv")
            temp.dist <- temp.dat %>%
              #subset(match==TRUE & eval(as.symbol(benchmark))>0) %>%
              subset(match==TRUE & bench>0) %>%
              mutate(across(all_of(temp.impVars),
                            #.fns=~./eval(as.symbol(benchmark)),
                            .fns=~./bench,
                            .names="prop{.col}")) %>%
              summarize(across(paste0("prop",temp.impVars),mean)) %>%
              as.matrix()
            log_debug("temp.dist")
            print(temp.dist)
            #For each row - do row variables not match benchmark?
            indexNoMatch <- temp.dat %>%
              evalq(match==FALSE|is.na(match),envir=.)
            #log_debug("temp.dat[indexNoMatch,temp.impVars]")
            #print(temp.dat[indexNoMatch,temp.impVars])
            #log_debug("benchmark")
            #print(benchmark)
            #log_debug("temp.dat[indexNoMatch,benchmark]")
            #print(temp.dat[indexNoMatch,benchmark])
            #For cases where they don't match - assign row variables based on benchmark and proportions from above
            #temp.dat[indexNoMatch,temp.impVars] <- as.matrix(temp.dat[indexNoMatch,benchmark])%*%temp.dist
            temp.dat[indexNoMatch,(temp.impVars)] <- data.table(as.matrix(temp.dat[indexNoMatch,"bench"])%*%temp.dist)
            #Repeat sum / match with new counts
            #Update (07MAR2022): Use explicit variable called 'bench'
            temp.dat <- temp.dat %>%
              mutate(sumImpVarsNew=dplyr::select(.,all_of(temp.impVars)) %>%
                       rowSums(na.rm=TRUE)) %>%
              mutate(match=ifelse(sourceInd=="NIBRS",
                                  TRUE,
                                  #abs(sumImpVarsNew-eval(as.symbol(benchmark)))<eps
                                  abs(sumImpVarsNew-bench)<eps
              )
              )
            if (temp.dat %>% subset(match == FALSE|is.na(match)) %>% nrow()>0){
              log_debug("Discrepancies / match is missing [round 2]")
              temp.dat %>% subset(match == FALSE|is.na(match)) %>% dplyr::select(ORI,county,benchmark,match,sumImpVarsNew,all_of(temp.impVars)) %>% head() %>% print()
            }
          }
        }
        #temp.dat %>% subset(!is.na(eval(as.symbol(temp.impVars[1])))) %>% group_by(match) %>% summarize(n=n()) %>% print()
        #colnames(temp.dat) %>% subset(!. %in% colnames(dat)) %>% print()
        #temp.dat %>% subset(!is.na(eval(as.symbol(temp.impVars[1])))) %>% subset(match !=TRUE) %>% dplyr::select(ORI,benchmark,temp.impVars,ratio,match,sumImpVars,sumImpVarsNew) %>% head() %>% print()
      } else if (temp.type==3){
        temp.index <- data.frame(section=sections,type=types) %>%
          mutate(rowAll=1:nrow(.)) %>%
          subset(section==sections[i]) %>%
          subset(type==3) %>%
          mutate(rowType=1:nrow(.)) %>%
          subset(rowAll==i) %>%
          .$rowType
        
        temp.pVar <- paste0("t_",table,"_",sections[i],"_p",temp.index,"_",column)
        #print(temp.pVar)
        temp.impVars <- temp.impVars %>% subset(!. %in% temp.pVar)
        
        #log_debug("temp.dat")
        #temp.dat %>% subset(ORI %in% c("GA1360100","TX1120000")) %>% dplyr::select(ORI,benchmark,temp.pVar,all_of(temp.impVars)) %>% print()
        #Update (03MAR2022): Switching from mutate_each() to mutate(across())
        #Update (07MAR2022): Create explicit variable called 'bench'
        #Update (JDB 16May2022): Update variable 'bench' so that 0 if benchmark is 0
        temp.dat <- temp.dat %>%
          mutate(bench=ifelse(eval(as.symbol(benchmark))==0,
                              0,
                              eval(as.symbol(benchmark))*eval(as.symbol(temp.pVar)))) %>%
          mutate(sumImpVars=dplyr::select(.,temp.impVars) %>%
                   rowSums(na.rm=TRUE),
                 ratio=ifelse(sourceInd=="NIBRS",
                              1,
                              ifelse(sumImpVars>0,
                                     #eval(as.symbol(benchmark))*eval(as.symbol(temp.pVar))/sumImpVars,
                                     bench/sumImpVars,
                                     #Update (11Mar2022): Add condition that if bench==0 --> ratio=0
                                     ifelse(eval(as.symbol(temp.pVar))==0|bench==0,
                                            0,
                                            NA_real_)
                              )
                 )
          )
        
        #log_debug("temp.dat [v1]")
        #temp.dat %>% subset(ORI %in% c("GA1360100","TX1120000")) %>% dplyr::select(ORI,benchmark,temp.pVar,all_of(temp.impVars)) %>% print()
        #Update (07Mar2022): Incorporating new 'bench' variable
        temp.dat <- temp.dat %>%
          #mutate_each(funs(.*ratio),temp.impVars) %>%
          mutate(across(all_of(temp.impVars),.fns=~.*ratio)) %>%
          mutate(sumImpVarsNew=dplyr::select(.,all_of(temp.impVars)) %>%
                   rowSums(na.rm=TRUE)) %>%
          mutate(match=ifelse(sourceInd=="NIBRS",
                              TRUE,
                              #ifelse(eval(as.symbol(benchmark))==0,
                              ifelse(bench==0,
                                     TRUE,
                                     #abs(sumImpVarsNew-eval(as.symbol(benchmark))*eval(as.symbol(temp.pVar)))<eps & !(sumImpVarsNew==0 & eval(as.symbol(benchmark))>0)
                                     abs(sumImpVarsNew-bench)<eps & !(sumImpVarsNew==0 & bench>0)
                              )
          )
          )
        #log_debug("temp.dat [v2]")
        #temp.dat %>% subset(ORI %in% c("GA1360100","TX1120000")) %>% dplyr::select(ORI,benchmark,sumImpVarsNew,match,temp.pVar,all_of(temp.impVars)) %>% print()
        temp.dat %>% group_by(match) %>% summarize(n=n()) %>% print()
        if (temp.dat %>% subset(match == FALSE|is.na(match)) %>% nrow() > 0 ){
          log_debug("Discrepancies / match is missing")
          temp.dat %>% subset(match == FALSE|is.na(match)) %>% dplyr::select(ORI,county,benchmark,match,temp.pVar,sumImpVarsNew,all_of(temp.impVars)) %>% head() %>% print()
          #Update (03Mar2022): Pull proportion for row variable among matches
          #Update (07Mar2022): Incorporating new 'bench' variable
          #if (temp.dat %>% subset(match==TRUE & eval(as.symbol(benchmark))>0) %>% nrow() > 0){
          if (temp.dat %>% subset(match==TRUE & bench>0) %>% nrow() > 0){
            #log_debug("temp.dat %>% subset(match==TRUE & eval(as.symbol(benchmark))>0) %>% dplyr::select(benchmark,all_of(temp.impVars)) %>% head(n=3000L)")
            # write_csv(temp.dat %>% subset(match==TRUE & eval(as.symbol(benchmark))>0)%>% dplyr::select(ORI,benchmark,all_of(temp.impVars)),
            #           file="C:/Users/jbunker/Documents/Temp/test.csv")
            temp.dist <- temp.dat %>%
              #subset(match==TRUE & eval(as.symbol(benchmark))>0) %>%
              subset(match==TRUE & bench>0) %>%
              mutate(across(all_of(temp.impVars),
                            #.fns=~./eval(as.symbol(benchmark)),
                            .fns=~./bench,
                            .names="prop{.col}")) %>%
              summarize(across(paste0("prop",temp.impVars),mean)) %>%
              as.matrix()
            log_debug("temp.dist")
            print(temp.dist)
            #For each row - do row variables not match benchmark?
            indexNoMatch <- temp.dat %>%
              evalq(match==FALSE|is.na(match),envir=.)
            #log_debug("temp.dat[indexNoMatch,temp.impVars]")
            #print(temp.dat[indexNoMatch,temp.impVars])
            #log_debug("benchmark")
            #print(benchmark)
            #log_debug("temp.dat[indexNoMatch,benchmark]")
            #print(temp.dat[indexNoMatch,benchmark])
            #For cases where they don't match - assign row variables based on benchmark and proportions from above
            #Update (07Mar2022): Use variable called 'bench', not parameter benchmark
            #temp.dat[indexNoMatch,temp.impVars] <- as.matrix(temp.dat[indexNoMatch,benchmark])%*%temp.dist
            temp.dat[indexNoMatch,(temp.impVars)] <- data.table(as.matrix(temp.dat[indexNoMatch,"bench"])%*%temp.dist)
            #log_debug("temp.dat[indexNoMatch,temp.impVars]")
            #print(temp.dat[indexNoMatch,temp.impVars])
            #Repeat sum / match with new counts
            #Update (07Mar2022): Incorporate new 'bench' variable
            temp.dat <- temp.dat %>%
              mutate(sumImpVarsNew=dplyr::select(.,all_of(temp.impVars)) %>%
                       rowSums(na.rm=TRUE)) %>%
              mutate(match=ifelse(sourceInd=="NIBRS",
                                  TRUE,
                                  #ifelse(eval(as.symbol(benchmark))==0,
                                  ifelse(bench==0,
                                         TRUE,
                                         #abs(sumImpVarsNew-eval(as.symbol(benchmark))*eval(as.symbol(temp.pVar)))<eps & !(sumImpVarsNew==0 & eval(as.symbol(benchmark))>0)
                                         abs(sumImpVarsNew-bench)<eps & !(sumImpVarsNew==0 & bench>0)
                                  )
              )
              )
            if (temp.dat %>% subset(match == FALSE|is.na(match)) %>% nrow()>0){
              log_debug("Discrepancies / match is missing [round 2]")
              temp.dat %>% subset(match == FALSE|is.na(match)) %>% dplyr::select(ORI,county,benchmark,match,temp.pVar,sumImpVarsNew,all_of(temp.impVars)) %>% head() %>% print()
            }
            
          }
        }
        
        #temp.dat %>% subset(match==FALSE)
        #temp.dat$sumImpVarsNew %>% summary() %>% print()
        #temp.dat %>% subset(!is.na(eval(as.symbol(temp.impVars[1])))) %>% subset(match !=TRUE) %>% dplyr::select(ORI,benchmark,temp.impVars,ratio,match,sumImpVars,sumImpVarsNew,temp.pVar) %>% head() %>% print()
        
      }
      #Update (07Mar2022): Incorporate new 'benchmark' variable
      temp.status <- temp.dat %>%
        summarize(nMatch=sum(match),
                  nDiffer=sum(match==FALSE|is.na(match)),
                  #sumBenchmark=sum(eval(as.symbol(benchmark))),
                  sumBenchmark=sum(bench),
                  #sumBenchmarkDiffer=sum(ifelse(match==FALSE|is.na(match),eval(as.symbol(benchmark)),0))
                  sumBenchmarkDiffer=sum(ifelse(match==FALSE|is.na(match),bench,0))
        )
      # log_debug("names(temp.dat)")
      # print(names(temp.dat))
      # log_debug("temp.dat")
      # print(temp.dat)
      
      #Update (12Apr2022): As a final step, if total for a column is 0, set detailed rows to 0
      temp.zero <- temp.dat %>%
        subset(bench==0) %>%
        mutate(across(all_of(temp.impVars),.fns=~0))
      temp.rest <- temp.dat %>%
        subset(bench!=0)
      temp.dat <- rbindlist(list(temp.zero,temp.rest),use.names=TRUE,fill=TRUE) %>% 
        data.frame()
      
      list2env(list("temp.dat"=temp.dat),funcEnv)
      
      
      return(temp.status)
    },simplify=FALSE) %>%
      rbindlist(use.names=TRUE,fill=TRUE) %>%
      data.frame() %>%
      mutate(table=table,
             column=column,
             tier=tier,
             section=sections) %>%
      #Reorder columns
      dplyr::select(table,tier,column,section,everything())
    
    #print(temp.dat)
    out <- temp.dat %>%
      dplyr::select(all_of(colnames(dat))) %>%
      list()
    names(out) <- datName
    log_debug("datName")
    print(datName)
    list2env(out,outEnv)
    
    #log_debug("dat %>% subset(is.na(eval(as.symbol(impVars[[1]][1])))) %>% nrow() [AFTER]")
    #print(dat %>% subset(is.na(eval(as.symbol(impVars[[1]][1])))) %>% nrow())
    #log_debug("Final status:")
    #status %>% print()
  } else{
    status <- data.frame()
  }
  return(status)
}
