#Step 1: Read in files and imputation step 1
#Note (28Jun2023): Switching from agency-level pop to (agency X county)-level pop
#Note (28Jun2023): Switching from rates (back) to counts
nstacks <- 10
source("Copula_Imputation_Functions.R")
#Update (JDB 26APR2022): Remove any existing temp files at start
rm(list=ls() %>% str_subset("^temp($|2|3|4)"))
#Set the variables used throughout copula imputation
if (temp.subset=="popResidAgcyCounty_cbi>0 & nDemoMissing==0"){
  temp.popVar <- "popResidAgcyCounty_cbi"
  temp.demoVars <- c("ageLT5"
                     ,"age5to14"
                     ,"age15"
                     ,"age16"
                     ,"age17"
                     ,"age18to24"
                     ,"age25to34"
                     #,age35to64
                     ,"ageGTE65"
                     #,sexMale
                     ,"sexFemale"
                     #,raceWhite
                     ,"raceBlack"
                     ,"raceAIAN"
                     ,"raceAsian"
                     ,"raceNHPI")
  temp.subsetSuffix <- "Nonzero_Pop" #Used for file name at end
  #Note (JDB 31MAR2023): Adding support for other ACS vars
  temp.othACSVars <- c("incomeRatioLT1",
                       #"incomeRatio1to2",
                       "incomeRatioGTE2")
  
} else if (temp.subset=="popResidAgcyCounty_cbi>0 & nDemoMissing>0"){
  temp.popVar <- "popResidAgcyCounty_cbi"
  temp.demoVars <- NULL
  temp.subsetSuffix <- "Missing_Demo" #Used for file name at end
  #Note (JDB 31MAR2023): Adding support for other ACS vars
  temp.othACSVars <- NULL
  
} else if (temp.subset=="popResidAgcyCounty_cbi==0"){
  temp.popVar <- "TOT_OFFICER_COUNT_COUNTY"
  temp.demoVars <- NULL
  temp.subsetSuffix <- "Zero_Pop" #Used for file name at end
  #Note (JDB 31MAR2023): Adding support for other ACS vars
  temp.othACSVars <- NULL
  
}
temp.uid <- paste0(temp.table,"_",temp.perm,"_",temp.colnum,"_",temp.subsetSuffix,"_Rates_",temp.stratVar,"_",temp.stratLvl) #Unique ID (table X perm X col set # X subset X "Rates" X strat var X strat lvl) for temp files
#Get current permutation
#10Oct2023: due to growing file size of permutation file, select only the columns we care about
temp.permDatCols <- paste0(filepathin_initial, "POP_TOTALS_PERM_", year, ".csv") %>%
  read_csv(n_max=0) %>%
  colnames()
temp.permDatTypes <- ifelse(temp.permDatCols=="PERMUTATION_NUMBER",
							"d", #Double
                            ifelse(temp.permDatCols=="PERMUTATION_NUMBER_DESC",
							       "c", #Character
								   "_") #Skip rest
							)
names(temp.permDatTypes) <- temp.permDatCols
							       
temp.permDat <- paste0(filepathin_initial, "POP_TOTALS_PERM_", year, ".csv") %>%
  read_csv(col_types=temp.permDatTypes) %>% 
  filter(PERMUTATION_NUMBER == temp.perm)
temp.permDesc <- parse(text=temp.permDat$PERMUTATION_NUMBER_DESC)

#Get row specs for table
temp.rowSpecs <- read_csv("../data/Indicator_Table_Row_Specs.csv") %>%
  filter(table==temp.table)

#Note (JDB 04May2022): Supporting column sets
temp.colsets <- temp.rowSpecs %>%
  .$columns %>%
  unique() %>%
  str_split(pattern=",") %>%
  unlist()
temp.colset <- temp.colsets[temp.colnum]

#Note (JDB 09May2022): Adding in ttlCols support
temp.ttlCols <- temp.rowSpecs %>%
  .$ttlCols %>%
  unique() %>%
  str_split(pattern="\\|") %>%
  unlist()



temp.step1Specs <- temp.rowSpecs %>%
  subset(type==0)
temp.step1Rows <- temp.step1Specs$rows
temp.step1RowsRegEx <- str_flatten(temp.step1Rows,col="|")

temp.demographics <- temp.rowSpecs %>%
  .$demographics %>%
  unique()

log_debug(system("free -mh", intern = FALSE))
#Note (JDB 21APR2022): Don't process demographic permutations if not a demographic table
if (temp.demographics==0 & as.numeric(temp.perm)>1000){
  log_debug("Current permutation is a demographics-based permutation but table is not a demographics-based. Skip steps 1-3.")
  log_debug(system("free -mh", intern = FALSE))
  temp4 <- data.frame()
  statusStep1 <- data.frame(matrix(ncol=14,nrow=0))
  colnames(statusStep1) <- c("table","permutation","row","impVar",
                             "noNIBRSInd","constPopInd","constInd",
                             "tryFullLHS","tryRedLHS",
                             "tryIndTOCa","tryIndTOCb","tryIndTOCc",
                             "failInd","collapseInd")
  statusStep1 <- statusStep1 %>%
    mutate(table=as.character(table),
           permutation=as.character(permutation),
           row=as.character(row),
           impVar=as.character(impVar))
  statusStep2 <- data.frame(matrix(ncol=13,nrow=0))
  colnames(statusStep2) <- c("table","permutation","tier","column","section",
                             "zeroColInd","constRowGpInd",
                             "tryFullLHS","tryRedLHS",
                             "tryIndRowGp","tryIndRowGpa","tryIndRowGpb",
                             "failInd")
  statusStep3 <- data.frame(matrix(ncol=9,nrow=0))
  colnames(statusStep3) <- c("table","permutation","column","tier","section",
                             "nMatch","nDiffer",
                             "sumBenchmark","sumBenchmarkDiffer")
} else {
  
  temp.allVars <-file.path(output_copula_data_folder,
                           paste0("Table_",temp.table,"_ORI_all_",temp.perm,".csv")) %>%		   
    fread(nrows=0) %>%
    colnames()
  
  #For tables with demographics-related columns, keep only the correct set of variables
  #For rest, keep all of list of variables
  #Note (JDB 04May2022): Adding compatibility with column sets
  temp.tableVars <- temp.allVars %>% str_subset("^t_")
  if (temp.demographics==1){
    #Update (28Apr2022): Moving away from always reading in full dataset and then dropping
    #                   Instead, select reduced list of variables to read in
    #Note (10May2022): Adding variable number modifier to account for demographics
    if (as.numeric(temp.perm)<1000){
      temp.varNumMod <- 0
      temp.tableVarsDrop <- temp.tableVars %>%
        str_subset("_\\d{1,3}$",negate=TRUE)
    } else if (as.numeric(temp.perm)<10000){
      temp.varNumMod <- 1000*as.numeric(str_extract(temp.perm,"^\\d"))
      temp.tableVarsDrop <- temp.tableVars %>%
        str_subset(paste0("_",
                          str_extract(temp.perm,"^\\d"),
                          "\\d{3}$"),
                   negate=TRUE)
    } else if (as.numeric(temp.perm)<100000){
      temp.varNumMod <- 1000*as.numeric(str_extract(temp.perm,"^\\d{2}"))
      temp.tableVarsDrop <- temp.tableVars %>%
        str_subset(paste0("_",
                          str_extract(temp.perm,"^\\d{2}"),
                          "\\d{3}$"),
                   negate=TRUE)
    } else if (as.numeric(temp.perm)<1000000){
      temp.varNumMod <- 1000*as.numeric(str_extract(temp.perm,"^\\d{3}"))
      temp.tableVarsDrop <- temp.tableVars %>%
        str_subset(paste0("_",
                          str_extract(temp.perm,"^\\d{3}"),
                          "\\d{3}$"),
                   negate=TRUE)
    }
    
    #Note (12May2022): Adding support for DM7/DM9
    if (temp.colset!="\\d+"){
      temp.tableVarsRegEx <- eval(parse(text=temp.colset)) %>%
        `+`(temp.varNumMod) %>% #Add temp.varNumMod to column set
        str_flatten(col="|") %>%
        {paste0("_(",.,")$")}
      temp.tableVarsDrop <- c(temp.tableVarsDrop,
                              temp.tableVars %>% 
                                subset(!. %in% temp.tableVarsDrop) %>%
                                str_subset(temp.tableVarsRegEx,negate=TRUE))
    }
  } else if (temp.colset!="\\d+"){
    temp.varNumMod <- 0
    temp.tableVarsRegEx <- eval(parse(text=temp.colset)) %>%
      str_flatten(col="|") %>%
      {paste0("_(",.,")$")}
    temp.tableVarsDrop <- temp.tableVars %>% str_subset(temp.tableVarsRegEx,negate=TRUE)
  }else {
    temp.varNumMod <- 0
    temp.tableVarsDrop <- character(0)
  }
  temp.keepVars <- temp.allVars %>%
    subset(!. %in% temp.tableVarsDrop)
  temp.keepVarsTypes <- ifelse(str_detect(temp.keepVars,"^t_"),"d","?") %>%
    as.list()
  names(temp.keepVarsTypes) <- temp.keepVars
  
  
  tableDat <- file.path(output_copula_data_folder,
                        paste0("Table_",temp.table,"_ORI_all_",temp.perm,".csv")) %>%
    fread(select=temp.keepVars) %>%
    data.frame() # %>%
    # select(temp.keepVars)
  #Note (JDB 01Jun2022): Moving this up - originally was after step 2 specs
  columns <- colnames(tableDat) %>%
    str_subset(paste0("t_",temp.table,"_1_1_\\d+")) %>%
    str_extract("(?<=_)\\d+$") %>%
    as.numeric()
  #Note (JDB 02Oct2023): Remove any columns in temp.ttlCols that don't already exist
  temp.ttlColInds <- temp.ttlCols %>% str_extract("^\\d+(?=\\=)") %>% as.numeric() %>% `+`(temp.varNumMod) %in% columns
  if (length(which(temp.ttlColInds==FALSE))>0){
  temp.ttlCols <- temp.ttlCols[-which(temp.ttlColInds==FALSE)]
  }
  nCol <- columns %>%
    length()
  
  #Get temp.ttlVars
  temp.ttlVars <- colnames(tableDat) %>%
    str_subset(paste0("t_",temp.table,"_\\d+_(",temp.step1RowsRegEx,")_\\d+")) %>%
    str_sort(numeric=TRUE)
  #Note (JDB 01Jun2022): Adding code to create the total rows if none exist
  if (length(temp.ttlVars)==0){
    temp.ttlSect <- temp.tableVarsDrop %>%
      str_subset(paste0("t_",temp.table,"_\\d+_(",temp.step1RowsRegEx,")_\\d+")) %>%
      str_extract(paste0("(?<=",temp.table,"_)\\d+(?=_(",temp.step1RowsRegEx,")_)")) %>%
      unique()
    temp.ttlVars <- outer(paste0("t_",temp.table,"_",temp.ttlSect,"_",temp.step1Rows,"_"),
                          columns,
                          FUN=paste0) %>%
      as.character()
    tableDat[temp.ttlVars] <- list(rep(0,nrow(tableDat)))
    tableDat <- tableDat %>%
      mutate(across(all_of(temp.ttlVars),.fns = ~ifelse(sourceInd=="NIBRS",0,NA_real_)))
  }
  
  
  temp.step2Specs <- temp.rowSpecs %>%
    subset(tier %in% 1:2)
  temp.step2Tier1Sects <- temp.step2Specs %>%
    subset(tier==1) %>%
    .$section
  temp.step2Tier1Rows <- temp.step2Specs %>%
    subset(tier==1) %>%
    .$rows
  temp.step2Tier1Rows <- sapply(1:length(temp.step2Tier1Sects),function(i){
    colnames(tableDat) %>%
      str_subset(paste0("^t_",temp.table,"_",temp.step2Tier1Sects[i],"_",temp.step2Tier1Rows[i],"_\\d+$")) %>%
      str_extract(paste0("(?<=t_",temp.table,"_\\d{1,2}_)\\d+(?=_\\d+)")) %>%
      unique()
  },simplify=FALSE)
  names(temp.step2Tier1Rows) <- temp.step2Tier1Sects
  temp.step2Tier1Types <- temp.step2Specs %>%
    subset(tier==1) %>%
    .$type
  
  temp.step2Tier2Sects <- temp.step2Specs %>%
    subset(tier==2) %>%
    .$section
  temp.step2Tier2Rows <- temp.step2Specs %>%
    subset(tier==2) %>%
    .$rows
  temp.step2Tier2Rows <- sapply(1:length(temp.step2Tier2Sects),function(i){
    colnames(tableDat) %>%
      str_subset(paste0("^t_",temp.table,"_",temp.step2Tier2Sects[i],"_",temp.step2Tier2Rows[i],"_\\d+$")) %>%
      str_extract(paste0("(?<=t_",temp.table,"_\\d{1,2}_)\\d+(?=_\\d+)"))
  },simplify=FALSE)
  names(temp.step2Tier2Rows) <- temp.step2Tier2Sects
  temp.step2Tier2Types <- temp.step2Specs %>%
    subset(tier==2) %>%
    .$type
  
  
  tempEnv <- environment() #Store environment [useful during list2env]
  
  temp <- data.frame(tableDat) %>%
    subset(eval(parse(text=temp.permDesc))) %>%
    filter(eval(parse(text=temp.subset))) %>%
    subset(eval(sym(temp.stratVar))==temp.stratLvl)
  #Note (28Jun2023): No longer using counts - commenting out (for now)
  #if (temp.subset!="popResidAgcyCounty_cbi==0"){
  #  temp <- temp %>%
  #    mutate(across(matches("^t_"),~.x/popResidAgcyCounty_cbi))
  #}
  
  statusStep1 <- data.frame(matrix(ncol=14,nrow=0))
  colnames(statusStep1) <- c("table","permutation","row","impVar",
                             "noNIBRSInd","constPopInd","constInd",
                             "tryFullLHS","tryRedLHS",
                             "tryIndTOCa","tryIndTOCb","tryIndTOCc",
                             "failInd","collapseInd")
  statusStep1 <- statusStep1 %>%
    mutate(table=as.character(table),
           permutation=as.character(permutation),
           row=as.character(row),
           impVar=as.character(impVar))
  statusStep2 <- data.frame(matrix(ncol=13,nrow=0))
  colnames(statusStep2) <- c("table","permutation","tier","column","section",
                             "zeroColInd","constRowGpInd",
                             "tryFullLHS","tryRedLHS",
                             "tryIndRowGp","tryIndRowGpa","tryIndRowGpb",
                             "failInd")
  statusStep3 <- data.frame(matrix(ncol=9,nrow=0))
  colnames(statusStep3) <- c("table","permutation","column","tier","section",
                             "nMatch","nDiffer",
                             "sumBenchmark","sumBenchmarkDiffer")
  
  
  if (nrow(temp)==0){
    paste0("No LEAs for ",as.character(temp.permDesc),". Skip steps 1-3.") %>%
      log_debug()
    log_debug(system("free -mh", intern = FALSE))
    #temp2 <- data.frame()
    #temp3 <- data.frame()
    temp.benchmarks <- NULL #Added 25Oct2022
  } else if (nrow(temp)>0){
    log_debug("nrow(temp)>0")
    #Update (07Mar2022): Need to create SRS indicator for post imputation
    #Note (JDB 09May2022): sourceInd created in part 1 now, so commenting out below
    #log_debug("Create sourceInd")
    #sourceInd <- temp %>%
    #  mutate(sourceInd=ifelse(!is.na(eval(as.symbol(temp.ttlVars[1]))),
    #                          "NIBRS",
    #                          "SRS")) %>%
    #  dplyr::select(ORI,sourceInd)
    #Note (JDB 09May2022): Switch source from sourceInd dataframe to temp
    #if (!any(sourceInd$sourceInd=="SRS")){
    if (!any(temp$sourceInd=="SRS")){
      log_debug(paste0("No SRS LEAs in ",as.character(temp.permDesc),". Skip steps 1-3."))
      log_debug(system("free -mh", intern = FALSE))
      temp2 <- temp
      #Update (28Apr2022): Add sourceInd to temp3
      #Note (JDB 09May2022): Comment out join to sourceInd
      temp3 <- temp #%>%
      #inner_join(sourceInd)
      temp.benchmarks <- NULL #Added 25Oct2022
    } else {
      #Note (JDB 04May2022): Only allow single single total row -> remove loooping
      #Note (JDB 09May2022): Split out total step 1 variables (temp.step1TtlVars) from remaining step 1 variables (temp.step1RestVars)
      #Note (JDB 11May2022): Actually, looks like we need to support multiple total rows (e.g., 3c)... re introduce original looping
      sapply(1:nrow(temp.step1Specs),function(i){
        tempEnv2 <- environment()
        temp.step1Row <- temp.step1Specs[i,"rows"] %>% as.character()
        #temp.step1Row <- temp.step1Specs[1,"rows"] %>% as.character()
        temp.special <- temp.step1Specs[1,"special"] %>% as.character() %>% unique()
        temp.step1Vars <- colnames(temp) %>% 
          str_subset(paste0("^t_",temp.table,"_.*_",temp.step1Row,"_\\d+$")) %>%
          str_sort(numeric=TRUE)
        #Note (JDB 09May2022): Splitting out length(temp.step1Vars)>1 condition into those with/without temp.ttlCols
        if (!is.na(temp.special) & temp.special == "X"){
          #If a special table, take the sum of all the temp.step1Vars
          temp.step1TtlRow <- temp.step1Specs[1,"ttlRow"] %>% unique()
          temp.step1TtlVars <- colnames(temp) %>% 
            str_subset(paste0("^t_",temp.table,"_.*_",temp.step1TtlRow,"_\\d+$")) %>%
            str_sort(numeric=TRUE)
          #Note (JDB 01Jun2022): Create ttl row if doesn't exist
          if (length(temp.step1TtlVars)==0){
            temp.step1TtlSect <- temp.tableVarsDrop %>%
              str_subset(paste0("t_",temp.table,"_\\d+_",temp.step1TtlRow,"_\\d+")) %>%
              str_extract(paste0("(?<=",temp.table,"_)\\d+(?=_(",temp.step1TtlRow,")_)")) %>%
              unique()
            temp.step1TtlVars <- paste0("t_",temp.table,"_",temp.step1TtlSect,"_",temp.step1TtlRow,"_",columns)
            temp[temp.step1TtlVars] <- list(rep(0,nrow(temp)))
            temp <- temp %>%
              mutate(across(all_of(temp.step1TtlVars),.fns = ~ifelse(sourceInd=="NIBRS",0,NA_real_)))
            tableDat[temp.step1TtlVars] <- list(rep(0,nrow(tableDat)))
            tableDat <- tableDat %>%
              mutate(across(all_of(temp.step1TtlVars),.fns = ~ifelse(sourceInd=="NIBRS",0,NA_real_)))
          }
        } else if (length(temp.step1Vars)>1 & length(temp.ttlCols)>0){
          #If not a special table and # of step 1 variables > 1 & length(temp.ttlCols)>0 -> impute all but the total columns
          #Note (10May2022): Supporting temp.varNumMod
          temp.step1TtlCols <- as.numeric(str_extract(temp.ttlCols,".+(?=\\=)"))+temp.varNumMod
          temp.step1SubCols <- sapply(X=str_extract(temp.ttlCols,"(?<=\\=).+"),FUN=function(X)parse(text=X) %>% eval()+temp.varNumMod,simplify=FALSE)
		  #24Aug2023: changing temp.step1TtlVars to be in same order as temp.step1TtlCols
          #temp.step1TtlVars <- temp.step1Vars %>% str_subset(paste0("_(",str_flatten(temp.step1TtlCols,collapse="|"),")$"))
		  temp.step1TtlVars <- sapply(temp.step1TtlCols,function(temp.step1TtlCol){
		    temp.step1Vars %>% str_subset(paste0("_(",str_flatten(temp.step1TtlCol,collapse="|"),")$"))
		  })
          temp.step1RestVars <- temp.step1Vars %>% str_subset(paste0("_(",str_flatten(temp.step1TtlCols,collapse="|"),")$"),negate=TRUE)
        } else if (length(temp.step1Vars)>1 & length(temp.ttlCols)==0){
          #If not a special table and # of step 1 variables > 1 -> impute all but the 1st column
          temp.step1TtlCols <- columns[1]
          temp.step1SubCols <- columns[-1]
          temp.step1TtlVars <- temp.step1Vars[1]
          temp.step1RestVars <- temp.step1Vars[-1]
        } else {
          temp.step1TtlVars <- character(0)
          temp.step1RestVars <- temp.step1Vars
        }
        
        log_debug(paste0("Step 1 - row ",temp.step1Row))
        #log_debug("temp")
        # temp$t_1c_1_1_1 %>%
        #   is.na() %>%
        #   table() %>%
        #   print()
        
        #Note (JDB 02May2022): Handling single column tables differently vs. multi-column tables
        #Note (JDB 09May2022): Reorganizing code to support multiple total columns
        #Note (JDB 11May2022): Due to re-adding loop, let's push tempEnv2 to tempEnv3
        
        if (length(temp.step1TtlVars)>=1 & is.na(temp.special)){
          
          sapply(1:length(temp.step1TtlVars),function(i){
            tempEnv3 <- environment()
            temp.step1TtlVar <- temp.step1TtlVars[i]
            temp.step1SubCol <- temp.step1SubCols[i] %>% parse(text=.) %>% eval()
            temp.step1SubVars <- temp.step1Vars %>% str_subset(paste0("_(",str_flatten(temp.step1SubCol,collapse="|"),")$"))
            temp <- temp %>%
              ungroup() %>%
              mutate(den=ifelse(sourceInd=="NIBRS",
                                dplyr::select(.,temp.step1SubVars) %>% 
                                  rowSums(),
                                NA_real_)) %>%
              mutate(p=if_else(den==0,0,eval(as.symbol(temp.step1TtlVar))/den))
            #Update (JDB 02May2022): Including new collapseInd to track whether collapsing occurred
            #Note (JDB 09May2022): Only include temp.step1RestVars if 1st run
            if (temp.step1TtlVar==temp.step1TtlVars[1]){
              statusStep1 <- rbindlist(list(statusStep1,
                                            getStep1Imp(temp,
                                                        table=temp.table,
                                                        popVar=temp.popVar,
                                                        demoVars=temp.demoVars,
                                                        othACSVars=temp.othACSVars,#JDB 31MAR2023: Added support today
                                                        lhsTOCs=NULL,
                                                        impVars=c(temp.step1RestVars,"p"),
                                                        stacks=nstacks,
                                                        outEnv=tempEnv3) %>%
                                              mutate(row=temp.step1Row,
                                                     permutation=temp.perm,
                                                     collapseInd=FALSE) %>%
                                              select(table,permutation,row,impVar,
                                                     noNIBRSInd,constPopInd,constInd,
                                                     tryFullLHS,tryRedLHS,
                                                     tryIndTOCa,tryIndTOCb,tryIndTOCc,
                                                     failInd,collapseInd)),
                                       use.names=TRUE,
                                       fill=TRUE) %>%
                data.frame()
            } else {
              statusStep1 <- rbindlist(list(statusStep1,
                                            getStep1Imp(temp,
                                                        table=temp.table,
                                                        popVar=temp.popVar,
                                                        demoVars=temp.demoVars,
                                                        othACSVars=temp.othACSVars,#JDB 31MAR2023: Added support today
                                                        lhsTOCs=NULL,
                                                        impVars="p",
                                                        stacks=nstacks,
                                                        outEnv=tempEnv3) %>%
                                              mutate(row=temp.step1Row,
                                                     permutation=temp.perm,
                                                     collapseInd=FALSE) %>%
                                              select(table,permutation,row,impVar,
                                                     noNIBRSInd,constPopInd,constInd,
                                                     tryFullLHS,tryRedLHS,
                                                     tryIndTOCa,tryIndTOCb,tryIndTOCc,
                                                     failInd,collapseInd)),
                                       use.names=TRUE,
                                       fill=TRUE) %>%
                data.frame()
            }
            temp <- temp %>%
              mutate(!!temp.step1TtlVar := ifelse(sourceInd=="NIBRS",
                                                  eval(as.symbol(temp.step1TtlVar)),
                                                  p*rowSums(dplyr::select(.,all_of(temp.step1SubVars)),
                                                            na.rm=TRUE)))
            list2env(list("temp"=temp,"statusStep1"=statusStep1),envir=tempEnv2)
            return(NULL)
          })
          
        } else if (length(temp.step1Vars)>1 & !is.na(temp.special) & temp.special=="X"){
          temp <- temp %>%
            ungroup() %>%
            mutate(den=ifelse(sourceInd=="NIBRS",
                              dplyr::select(.,temp.step1Vars) %>% 
                                rowSums(),
                              NA_real_)) %>%
            mutate(p=if_else(den==0,0,eval(as.symbol(temp.step1TtlVars[1]))/den))
          #Update (JDB 02May2022): Including new collapseInd to track whether collapsing occurred
          statusStep1 <- rbindlist(list(statusStep1,
                                        getStep1Imp(temp,
                                                    table=temp.table,
                                                    popVar=temp.popVar,
                                                    demoVars=temp.demoVars,
                                                    othACSVars=temp.othACSVars,#JDB 31MAR2023: Added support today
                                                    lhsTOCs=NULL,
                                                    impVars=c(temp.step1Vars,"p"),
                                                    stacks=nstacks,
                                                    outEnv=tempEnv2) %>%
                                          mutate(row=temp.step1Row,
                                                 permutation=temp.perm,
                                                 collapseInd=FALSE) %>%
                                          select(table,permutation,row,impVar,
                                                 noNIBRSInd,constPopInd,constInd,
                                                 tryFullLHS,tryRedLHS,
                                                 tryIndTOCa,tryIndTOCb,tryIndTOCc,
                                                 failInd,collapseInd)),
                                   use.names=TRUE,
                                   fill=TRUE) %>%
            data.frame()
          
          temp <- temp %>%
            mutate(across(.cols=matches(temp.step1TtlVars),.fns=function(x){ifelse(sourceInd=="NIBRS",x,p*rowSums(dplyr::select(.,all_of(temp.step1Vars)),na.rm=TRUE))}))
        } else {
          statusStep1 <- rbindlist(list(statusStep1,
                                        getStep1Imp(temp,
                                                    table=temp.table,
                                                    popVar=temp.popVar,
                                                    demoVars=temp.demoVars,
                                                    othACSVars=temp.othACSVars,#JDB 31MAR2023: Added support today
                                                    lhsTOCs=NULL,
                                                    impVars=temp.step1Vars,
                                                    stacks=nstacks,
                                                    outEnv=tempEnv2) %>%
                                          mutate(row=temp.step1Row,
                                                 permutation=temp.perm,collapseInd=FALSE) %>%
                                          select(table,permutation,row,impVar,
                                                 noNIBRSInd,constPopInd,constInd,
                                                 tryFullLHS,tryRedLHS,
                                                 tryIndTOCa,tryIndTOCb,tryIndTOCc,
                                                 failInd,collapseInd)),
                                   use.names=TRUE,
                                   fill=TRUE) %>%
            data.frame()
        }
        if (length(temp.step1TtlVars)>=1 & is.na(temp.special)){
          temp.benchmarks <- c(temp.step1TtlVars,temp.step1RestVars)
        } else if (length(temp.step1Vars)>1 & temp.special=="X"){
          temp.benchmarks <- temp.step1Vars
        } else {
          
          temp.benchmarks <- temp.step1Vars
        }
        #Note (JDB 11MAY2022): Sorting and deduplicating benchmarks
        temp.benchmarks <- temp.benchmarks %>% unique() %>% str_sort(numeric=TRUE)
        #Note (JDB 20APR2022): Reorganize variables for status table 1
        if (nrow(statusStep1)>0){
          statusStep1 <- statusStep1 %>%
            dplyr::select(table,permutation,row,impVar,everything())
        }
        
        #temp[,temp.step1Vars[1]] %>% table(useNA="always") %>% print()
        #temp$p %>% is.na() %>% table() %>% print()
        #Check post step 1 results
        #temp$t_1b_1_1_1 %>%
        #  is.na() %>%
        #  table() %>% print()
        #temp$t_1b_1_1_2 %>%
        #  is.na() %>%
        #  table() %>% print()
        #Note (11May2022): Adding temp.benchmarks to output
        list2env(list("temp"=temp,"statusStep1"=statusStep1,"temp.benchmarks"=temp.benchmarks),tempEnv)#,"sourceInd"=sourceInd
        return(NULL)
      })
    }
    
  } 
  
}
#Set useful variables as environment variables
#Note (08Sep2022): Commenting-out for now
#Sys.setenv("columns"=columns %>% str_flatten(col=" "))
#Sys.setenv("nCol"=nCol)
#Sys.setenv("nstacks"=nstacks)
#Sys.setenv("temp.benchmarks"=temp.benchmarks %>% str_flatten(" "))
#Sys.setenv("temp.demoVars"=temp.demoVars %>% str_flatten(col=" "))
#Sys.setenv("temp.permDesc"=temp.permDesc)
#Sys.setenv("temp.popVar"=temp.popVar)
#Sys.setenv("temp.step1RowsRegEx"=temp.step1RowsRegEx %>% str_flatten(col=" "))
#Sys.setenv("temp.step2Tier1Sects"=temp.step2Tier1Sects %>% str_flatten(col=" "))
#Sys.setenv("temp.step2Tier1Types"=temp.step2Tier1Types %>% str_flatten(col=" "))
#Sys.setenv("temp.step2Tier2Sects"=temp.step2Tier2Sects %>% str_flatten(col=" "))
#Sys.setenv("temp.step2Tier2Types"=temp.step2Tier2Types %>% str_flatten(col=" "))
#Sys.setenv("temp.subsetSuffix"=temp.subsetSuffix)

#Output useful datasets
save(temp.step2Tier1Rows,file=file.path(output_copula_temp_folder,
                                        paste0("temp.step2Tier1Rows_",temp.uid,".Rdata")))
save(temp.step2Tier2Rows,file=file.path(output_copula_temp_folder,
                                        paste0("temp.step2Tier2Rows_",temp.uid,".Rdata")))
#save(tempEnv,file=file.path(output_copula_temp_folder,
#                            paste0("tempEnv_",temp.uid,".Rdata")))
save(columns,file=file.path(output_copula_temp_folder,
                            paste0("columns_",temp.uid,".Rdata")))
save(nCol,file=file.path(output_copula_temp_folder,
                         paste0("nCol_",temp.uid,".Rdata")))
save(nstacks,file=file.path(output_copula_temp_folder,
                            paste0("nstacks_",temp.uid,".Rdata")))
save(temp.benchmarks,file=file.path(output_copula_temp_folder,
                                    paste0("temp.benchmarks_",temp.uid,".Rdata")))
save(temp.demoVars,file=file.path(output_copula_temp_folder,
                                  paste0("temp.demoVars_",temp.uid,".Rdata")))
save(temp.permDesc,file=file.path(output_copula_temp_folder,
                                  paste0("temp.permDesc_",temp.uid,".Rdata")))
save(temp.popVar,file=file.path(output_copula_temp_folder,
                                paste0("temp.popVar_",temp.uid,".Rdata")))
save(temp.step1RowsRegEx,file=file.path(output_copula_temp_folder,
                                        paste0("temp.step1RowsRegEx_",temp.uid,".Rdata")))
save(temp.step2Tier1Sects,file=file.path(output_copula_temp_folder,
                                         paste0("temp.step2Tier1Sects_",temp.uid,".Rdata")))
save(temp.step2Tier1Types,file=file.path(output_copula_temp_folder,
                                         paste0("temp.step2Tier1Types_",temp.uid,".Rdata")))
save(temp.step2Tier2Sects,file=file.path(output_copula_temp_folder,
                                         paste0("temp.step2Tier2Sects_",temp.uid,".Rdata")))
save(temp.step2Tier2Types,file=file.path(output_copula_temp_folder,
                                         paste0("temp.step2Tier2Types_",temp.uid,".Rdata")))
save(temp.subsetSuffix,file=file.path(output_copula_temp_folder,
                                      paste0("temp.subsetSuffix_",temp.uid,".Rdata")))
#Note (JDB 31Mar2023): Adding support for other ACS vars
save(temp.othACSVars,file=file.path(output_copula_temp_folder,
                                    paste0("temp.othACSVars_",temp.uid,".Rdata")))

#Output Step 1 results
outName <- paste0("Table_",temp.table,"_Imputation_Step1_Summary_Perm_",temp.perm,"_ColNum_",temp.colnum,"_",temp.subsetSuffix,"_Rates_",temp.stratVar,"_",temp.stratLvl)

if (nrow(statusStep1) > 0) {
  fwrite(statusStep1,
       file=file.path(output_copula_data_folder,
                      paste0(outName,".csv")))
} else {
  write_csv(statusStep1,
       file.path(output_copula_data_folder,
                      paste0(outName,".csv")))
}


#Save temp results
save(temp,file=file.path(output_copula_temp_folder,
                         paste0("temp_",temp.uid,".Rdata")))


#Output Step 2 results (initializing)
outName <- paste0("Table_",temp.table,"_Imputation_Step2_Summary_Perm_",temp.perm,"_ColNum_",temp.colnum,"_",temp.subsetSuffix,"_Rates_",temp.stratVar,"_",temp.stratLvl)

# file.remove(file=file.path(output_copula_data_folder,
#                            paste0(outName,".csv")))

if (nrow(statusStep2) > 0) {
  fwrite(statusStep2,
       file=file.path(output_copula_data_folder,
                      paste0(outName,".csv")))
} else {
  write_csv(statusStep2,
       file.path(output_copula_data_folder,
                      paste0(outName,".csv")))
}

#Output Step 3 results (initializing)
outName <- paste0("Table_",temp.table,"_Ratio_Adjustment_Summary_Perm_",temp.perm,"_ColNum_",temp.colnum,"_",temp.subsetSuffix,"_Rates_",temp.stratVar,"_",temp.stratLvl)

# file.remove(file=file.path(output_copula_data_folder,
#                            paste0(outName,".csv")))

if (nrow(statusStep3) > 0) {
  fwrite(statusStep3,
       file=file.path(output_copula_data_folder,
                      paste0(outName,".csv")))
} else {
  write_csv(statusStep3,
       file.path(output_copula_data_folder,
                      paste0(outName,".csv")))
}
