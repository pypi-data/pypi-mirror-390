DER_DEFINE_DEMO_TABLES <- c(
  "3a", "3aunclear", "3aclear", "3b", "3bunclear", "3bclear",  "4a", "4b", "5a", "5b", "DM7", "DM9", "DM10", "GV2a"
)

#This function takes a permutation number and determine the correct permutation number on the single level ORI file to return
find_demo_table_num <- function(inperm){
  
  if (inperm < 1000) {
    return_perm <- 1
  } else {
    return_perm <- inperm - (inperm %% 1000) + 1
  }
  
  #Return the permutation number
  return(return_perm)
  
}

#This function return the single level ORI file needed for processing
#Take as a parameter table for current table and perm for current permutation number

process_single_ori_tables <- function(intable, inpermutation, infilepath){
  
  #Make inpermutation into numeric
  inpermutation <- as.numeric(inpermutation)

  #If this is a demo table then choose the correct file to use
  if(intable %in% DER_DEFINE_DEMO_TABLES){
    
    tbd_current_perm = find_demo_table_num(inperm=inpermutation)
    
    log_debug("Using the demographic version of the ", "Table ", intable, " ORI_",tbd_current_perm ,".csv.gz")
    
    returndata <- tibble::as_tibble(fread(paste0(infilepath, "Table ", intable, " ORI_",tbd_current_perm ,".csv.gz"))) 
    
    
  }else{
    
    log_debug("Using the normal ", "Table ", intable, " ORI.csv.gz")
    
    returndata <- tibble::as_tibble(fread(paste0(infilepath, "Table ", intable, " ORI.csv.gz")))
    
  }
  
  #Return the object
  return(returndata)
  
}