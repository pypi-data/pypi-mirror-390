#################################################
####Table A -UCR Data#####

#Overall
genAppA <- function(des){
  survey::svytotal(~ totcrime_imp+tot_violent_imp+
                     tot_murder_imp+tot_manslaughter_imp+tot_rape_imp+tot_rob_imp+
                     tot_assault_imp+tot_aggAssault_imp+tot_simpAssault_imp+
                     tot_property_imp+
                     tot_burglary_imp+tot_larceny_imp+tot_vhcTheft_imp,
                   design=des)
}




#By state
genAppA_state <- function(des){
  survey::svyby(~totcrime_imp+tot_violent_imp+
                  tot_murder_imp+tot_manslaughter_imp+tot_rape_imp+tot_rob_imp+
                  tot_assault_imp+tot_aggAssault_imp+tot_simpAssault_imp+
                  tot_property_imp+
                  tot_burglary_imp+tot_larceny_imp+tot_vhcTheft_imp, ~state_abbr, des, svytotal)
  
}

genAppA_region <- function(des){
  survey::svyby(~totcrime_imp+tot_violent_imp+
                  tot_murder_imp+tot_manslaughter_imp+tot_rape_imp+tot_rob_imp+
                  tot_assault_imp+tot_aggAssault_imp+tot_simpAssault_imp+
                  tot_property_imp+
                  tot_burglary_imp+tot_larceny_imp+tot_vhcTheft_imp, ~REGION_NAME, des, svytotal)
  
}

genAppA_jd <- function(des){
  survey::svyby(~totcrime_imp+tot_violent_imp+
                  tot_murder_imp+tot_manslaughter_imp+tot_rape_imp+tot_rob_imp+
                  tot_assault_imp+tot_aggAssault_imp+tot_simpAssault_imp+
                  tot_property_imp+
                  tot_burglary_imp+tot_larceny_imp+tot_vhcTheft_imp, ~JUDICIAL_DISTRICT_NAME, des, svytotal)
				  
}				  
				  
genAppA_msa <- function(des){
  survey::svyby(~totcrime_imp+tot_violent_imp+
                  tot_murder_imp+tot_manslaughter_imp+tot_rape_imp+tot_rob_imp+
                  tot_assault_imp+tot_aggAssault_imp+tot_simpAssault_imp+
                  tot_property_imp+
                  tot_burglary_imp+tot_larceny_imp+tot_vhcTheft_imp, ~MSA_NAME_COUNTY, des, svytotal)
  
}


		  
genAppA_fo <- function(des){
  survey::svyby(~totcrime_imp+tot_violent_imp+
                  tot_murder_imp+tot_manslaughter_imp+tot_rape_imp+tot_rob_imp+
                  tot_assault_imp+tot_aggAssault_imp+tot_simpAssault_imp+
                  tot_property_imp+
                  tot_burglary_imp+tot_larceny_imp+tot_vhcTheft_imp, ~FIELD_OFFICE_NAME, des, svytotal)
  
}
#################################################
####Table C -UCR Data#####


#Overall
genAppC <- function(des){
  svytotal(~ totarrest_imp+
             tot_property_imp+
             tot_othAssault_imp+
             tot_larcenyTheft_imp+
             tot_violent_imp+
             tot_aggAssault_imp+
             tot_burglary_imp+
             tot_robbery_imp+
             tot_MVT_imp+
             tot_rape_imp+
             tot_murderNNM_imp+
             tot_arson_imp+
             tot_drugAbuse_imp+
             tot_vandalism_imp+
             tot_weapons_imp+
             tot_fraud_imp+
             tot_offsFamAndChild_imp+
             tot_stolenProp_imp+
             tot_FCF_imp+
             tot_othSexOffs_imp+
             tot_PCV_imp+
             tot_embezzlement_imp+
             tot_gambling_imp+
             tot_allOthOffs_imp+
             tot_DUI_imp+
             tot_disorderlyConduct_imp+
             tot_drunkenness_imp+
             tot_liquorLaws_imp+
             tot_curfewLoitering_imp+
             tot_vagrancy_imp+
             tot_suspicion_imp
           
           
           ,
           design=des)
}

#By state
genAppC_state <- function(des){
  survey::svyby(~ totarrest_imp+
                  tot_property_imp+
                  tot_othAssault_imp+
                  tot_larcenyTheft_imp+
                  tot_violent_imp+
                  tot_aggAssault_imp+
                  tot_burglary_imp+
                  tot_robbery_imp+
                  tot_MVT_imp+
                  tot_rape_imp+
                  tot_murderNNM_imp+
                  tot_arson_imp+
                  tot_drugAbuse_imp+
                  tot_vandalism_imp+
                  tot_weapons_imp+
                  tot_fraud_imp+
                  tot_offsFamAndChild_imp+
                  tot_stolenProp_imp+
                  tot_FCF_imp+
                  tot_othSexOffs_imp+
                  tot_PCV_imp+
                  tot_embezzlement_imp+
                  tot_gambling_imp+
                  tot_allOthOffs_imp+
                  tot_DUI_imp+
                  tot_disorderlyConduct_imp+
                  tot_drunkenness_imp+
                  tot_liquorLaws_imp+
                  tot_curfewLoitering_imp+
                  tot_vagrancy_imp+
                  tot_suspicion_imp,~state_abbr, des, svytotal)
}


genAppC_region <- function(des){
  survey::svyby(~ totarrest_imp+
                  tot_property_imp+
                  tot_othAssault_imp+
                  tot_larcenyTheft_imp+
                  tot_violent_imp+
                  tot_aggAssault_imp+
                  tot_burglary_imp+
                  tot_robbery_imp+
                  tot_MVT_imp+
                  tot_rape_imp+
                  tot_murderNNM_imp+
                  tot_arson_imp+
                  tot_drugAbuse_imp+
                  tot_vandalism_imp+
                  tot_weapons_imp+
                  tot_fraud_imp+
                  tot_offsFamAndChild_imp+
                  tot_stolenProp_imp+
                  tot_FCF_imp+
                  tot_othSexOffs_imp+
                  tot_PCV_imp+
                  tot_embezzlement_imp+
                  tot_gambling_imp+
                  tot_allOthOffs_imp+
                  tot_DUI_imp+
                  tot_disorderlyConduct_imp+
                  tot_drunkenness_imp+
                  tot_liquorLaws_imp+
                  tot_curfewLoitering_imp+
                  tot_vagrancy_imp+
                  tot_suspicion_imp,~REGION_NAME, des, svytotal)
}



##Ouput Tables

write_files_xlsx<-function(listfile_name,infile_name,file_name,crime_type,blankOut,keepCols,inCol,inRow,stZ,typeTab){
  list_of_files<-listfile_name
  include_dash<-blankOut
  
  Z=0
  TZ=stZ
  wb <- loadWorkbook(file = infile_name)
  
  cellstyle <- createStyle(halign = "right",valign = "center",border = c("top", "bottom", "left", "right"),borderStyle = "thin")
  
  
  for(i in 1:length(list_of_files)){
    Z=Z+1
    TZ=TZ+1
    #Initially fill in all rows
    writeData(wb,TZ,list_of_files[[Z]][keepCols],withFilter = F,startCol = inCol, startRow = inRow, colNames = FALSE)
    
    
    K=0
    #Violent -Shade rows that are Property Crimes
    if (str_detect(weight_lists[[Z]],"viol")==1) {
      
      for(i in 1:length(crime_type)){
        K=K+1
        eval=K-1+inRow
        if (str_detect(crime_type[[K]],"P")==1) {
          
          if(typeTab==9999){
            writeData(wb,TZ,include_dash,withFilter = F,startCol = inCol, startRow = eval, colNames = FALSE)
          }
          else {
            writeData(wb,TZ,include_dash,withFilter = F,startCol = inCol, startRow = K+inRow, colNames = FALSE)
          }
        }
      }
      
      
    }
    #Property-Shade rows that are Violent Crime 
    if (str_detect(weight_lists[[Z]],"prop")==1) {
      color <- createStyle(fgFill = "#606060") #Gray
      for(i in 1:length(crime_type)){
        K=K+1
        eval=K-1+inRow
        if (str_detect(crime_type[[K]],"V")==1) {
          
          if(typeTab==9999){
            writeData(wb,TZ,include_dash,withFilter = F,startCol = inCol, startRow = eval, colNames = FALSE)
          }
          else {
            writeData(wb,TZ,include_dash,withFilter = F,startCol = inCol, startRow = K+inRow, colNames = FALSE)
          }
        }
      }
    }
    
  }
  if(Z==length(list_of_files)){
    suppressMessages(saveWorkbook(wb,file =file_name ,overwrite = T))
    message("Dataframes Generated!")
  }
}
