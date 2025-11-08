#31Jan2024: check top line estimates after copula part 2 step 1 (individual table X permutation)
#Note (02Feb2024): I'm not sure where to find weighted estimates for demographic permutations, e.g. 3a perm 1001, that would be available before copula part 2 step 2 needs to be run... I think the files (e.g., Table 3a_Reporting_Database.csv) only has the non-demo national estimates... if they aren't available until later (e.g., variance), I could create them here. But I'd like confirmation before going through that hassle / duplicating effort.

#Assumed variables you'll already have:
#	>temp.table: Table
#	>temp.perm: Permutation
#	>output_copula_temp_folder: Temp folder for copula
#	>output_copula_data_folder: Data folder for copula
#	>final_path: Location of single estimate summary results (I'm naming this off what's used in single estimation programs I glanced over... if it were me, I would've used something more descriptive like output_estimates_folder...)

temp.perm <- as.numeric(temp.perm)
#Read in the total row from the copula parameter file
#Note: Some tables (e.g., 3c) have multiple total rows... let's just use the 1st
temp.ttlRow <- "../../copula_imputation/data/Indicator_Table_Row_Specs.csv" %>%
  fread_logging() %>%
  subset(table==temp.table & tier==0) %>%
  subset(row_number(table)==1) %>%
  pull(rows)
  

#Read in the weighted estimates 
#Note: I'm guessing this is the file to use... if needed, change name and/or subset to only the relevant permutation
#Note: This has to be a file available that exists before copula part 2, otherwise that defeats the purpose of this exercise

weighted_estimates <- paste0(final_path,"Table ",temp.table,"_Reporting_Database.csv") %>%
  fread_logging(select=c("table","section","row","column","full_table","estimate_domain","indicator_name","estimate_type","estimate")) %>%
  subset(row==temp.ttlRow & estimate_type=="count") %>%
  select(-estimate_type) 

#Update (05Feb2024): Need to obtain demo permutation estimates based on ORI-level file
#Update (14May2024): Need to do the same for the non-demo perm estimates (issues with reporting database, e.g., with violent and robbery in 2a) - just comment out the temp.perm condition
#if (temp.perm>1000){
  #If there are multiple file matches (e.g. both Table 3a ORI.csv.gz and Table 3a ORI_1.csv.gz), use the last one (which would be Table 3a ORI_1.csv.gz in this example)
  weighted_data_path <- list.files(final_path,full.names=TRUE) %>% 
    str_subset(paste0("Table ",temp.table," ORI(|_",temp.perm,").csv.gz")) %>% 
	.[length(.)]
  #Read in file, get weighted estimates, and transpose from wide to long
  weighted_data <- weighted_data_path %>% 
    fread_logging() %>% 
	summarize(across(matches("^t_\\w+"),~sum(.x*weight,na.rm=TRUE))) %>% 
	reshape2::melt() %>% 
	mutate(section=str_extract(variable,paste0("(?<=_",temp.table,"_)\\d+")) %>% as.integer(),
	       row=str_extract(variable,paste0("(?<=",temp.table,"_\\d{1,3}_)\\d+")) %>% as.integer(),
		   column=str_extract(variable,"(?<=_)\\d+$") %>% as.numeric() %>% `%%`(1000)) 
  #Merge new weighted estimates with existing national overall file
  weighted_estimates <- weighted_estimates %>%
	select(-estimate) %>%
	inner_join(weighted_data) %>%
	rename(estimate=value) %>%
	#Now that we have relevant variables from national overall file, have column reflect demo perm
	mutate(column=str_extract(variable,"(?<=_)\\d+$") %>% as.numeric())
#}

#Finish modifying weighted estimates
weighted_estimates <- weighted_estimates %>%
  mutate(variable=paste0("t_",table,"_",section,"_",row,"_",column)) %>%
  subset(column >= temp.perm & column < (temp.perm+1000)) %>%
  select(-c(table,section,row,column)) %>%
  rename(weighted_sum=estimate) %>%
  select(variable,everything())

#Read in the copula part 2 step 1 results
copula_files <- list.files(output_copula_temp_folder,full.names=TRUE) %>% str_subset(paste0("temp_",temp.table,"_",temp.perm,"_\\d+_\\w+_PARENT_POP_GROUP_CODE2_\\d+\\.Rdata"))

#Read in copula part 2 step 1 files, keeping only a subset of columns
copula_data <- map(copula_files,function(temp.copula_file){
  load(temp.copula_file)
  
  temp <- temp %>%
    select(ORI,county,sourceInd,matches(paste0("t_",temp.table,"_\\d+_",temp.ttlRow,"_\\d+")))
  return(temp)
}) %>% bind_rows()

#14Jul2025: any tables involving multiple column sets (currently only DM6-DM9) 
#             will have multiple copies of the same ORI x county... 
#           account for this by taking the max of each estimate by ORI x county
if (temp.table %in% c("DM6","DM7","DM8","DM9")){
  copula_data <- copula_data %>%
    group_by(ORI,county,sourceInd) %>%
    summarize(across(matches(paste0("t_",temp.table,"_\\d+_",temp.ttlRow,"_\\d+")),
                     ~max(ifelse(is.na(.x)|is.nan(.x),0,.x)))) %>%
    ungroup()
}

#Obtain n and sums by response type
copula_stats <- copula_data %>%
  summarize(across(matches(paste0("t_",temp.table)),
                   list("n_all"=~n(),
				        "n_rep"=~sum(sourceInd=="NIBRS"),
						"n_nr"=~sum(sourceInd=="SRS"),
						"sum_all"=~sum(.x,na.rm=TRUE),
						"sum_rep"=~sum(.x*ifelse(sourceInd=="NIBRS",1,0),na.rm=TRUE),
						"sum_nr"=~sum(.x*ifelse(sourceInd=="SRS",1,0),na.rm=TRUE)),
				   .names="{.col}_{.fn}")) %>%
  reshape2::melt() %>%
  mutate(stat_source=paste0("copula_",str_extract(variable,"(?<=_)(sum|n)_(all|rep|nr)")),
		 variable=str_remove(variable,"_(sum|n)_(all|rep|nr)")) %>%
  reshape2::dcast(variable ~ stat_source) %>%
  #pull(variable) %>%
  #str_order(numeric=TRUE)
  arrange(order(str_order(variable,numeric=TRUE))) 

#Nice little HTML table...
# copula_stats %>%
  # DT::datatable() %>%
  # formatCurrency(paste0("copula_",c('n_all','n_rep','n_nr')),currency = "", interval = 3, mark = ",",digits=0) %>%
  # formatCurrency(paste0("copula_",c('sum_all','sum_rep','sum_nr')),currency = "", interval = 3, mark = ",")
  
#Merge weighted estimates and copula estimates
merged_stats <- weighted_estimates %>%
  full_join(copula_stats)

#Nice little HTML table...
# merged_stats %>%
  # DT::datatable() %>%
  # formatCurrency("weighted_sum",currency = "", interval = 3, mark = ",",digits=0) %>%
  # formatCurrency(paste0("copula_",c('n_all','n_rep','n_nr')),currency = "", interval = 3, mark = ",",digits=0) %>%
  # formatCurrency(paste0("copula_",c('sum_all','sum_rep','sum_nr')),currency = "", interval = 3, mark = ",")
  
#Output results
merged_stats %>%
  fwrite_wrapper(file=paste0(validation_output_path,"Table_",temp.table,"_Perm_",temp.perm,"_Step1_Weighted_vs_Copula_Comparison.csv"))
