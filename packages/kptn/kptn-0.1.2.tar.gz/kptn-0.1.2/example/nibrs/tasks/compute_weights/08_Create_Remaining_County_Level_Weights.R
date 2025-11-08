#08_Create_Remaining_County_Level_Weights.R
#22Jun2023: This program will create county-level versions of national/region/state/tribal/university weights

log_info("Started 08_Create_Remaining_County_Level_Weights.R")
##########
#Load data

#County-level frame data
SF_county_raw <- paste0(input_weighting_data_folder,"SF_county.csv") %>%
  read_csv_logging()

#National weights
weights_national <- paste0(output_weighting_data_folder,"weights_national.csv") %>%
  read_csv_logging()
  
#Region weights
weights_region <- paste0(output_weighting_data_folder,"weights_region.csv") %>%
  read_csv_logging()
  
#State weights
weights_state <- paste0(output_weighting_data_folder,"weights_state.csv") %>%
  read_csv_logging()

#Tribal weights
weights_tribal <- paste0(output_weighting_data_folder,"weights_tribal.csv") %>%
  read_csv_logging()

#University weights  
weights_university <- paste0(output_weighting_data_folder,"weights_university.csv") %>%
  read_csv_logging()
  
  
##########
#Prep for merging

#Only select required frame variables
#02May2024: swapping out propPOP1 for propMult
SF_county <- SF_county_raw %>%
  #select(ORI_universe,LEGACY_ORI,county,propPOP1)
  select(ORI_universe,LEGACY_ORI,county,propMult)
  

##########
#Merging weights and SF (county-level)
#02May2024: swapping out propPOP1 for propMult throughout

#National
weights_national_county <- SF_county %>%
  left_join(weights_national) %>%
  #mutate(NationalWgt=NationalWgt*propPOP1)
  mutate(NationalWgt=NationalWgt*propMult)

#Region
weights_region_county <- SF_county %>%
  left_join(weights_region)%>%
  #mutate(RegionWgt=RegionWgt*propPOP1)
  mutate(RegionWgt=RegionWgt*propMult)
  
#State
weights_state_county <- SF_county %>%
  left_join(weights_state)%>%
  #mutate(StateWgt=StateWgt*propPOP1)
  mutate(StateWgt=StateWgt*propMult)

#Tribal
weights_tribal_county <- SF_county %>%
  left_join(weights_tribal)%>%
  #mutate(TribalWgt=TribalWgt*propPOP1)
  mutate(TribalWgt=TribalWgt*propMult)
  
#University
weights_university_county <- SF_county %>%
  left_join(weights_university)%>%
  #mutate(UniWgt=UniversityWgt*propPOP1)
  mutate(UniversityWgt=UniversityWgt*propMult)
  
##########
#Output

#National
weights_national_county %>%
  write_csv_logging(paste0(output_weighting_data_folder,"weights_national_county.csv"))
  
#Region
weights_region_county %>%
  write_csv_logging(paste0(output_weighting_data_folder,"weights_region_county.csv"))
  
#State
weights_state_county %>%
  write_csv_logging(paste0(output_weighting_data_folder,"weights_state_county.csv"))

#Tribal 
weights_tribal_county %>%
  write_csv_logging(paste0(output_weighting_data_folder,"weights_tribal_county.csv"))

#University
weights_university_county %>%
  write_csv_logging(paste0(output_weighting_data_folder,"weights_university_county.csv"))

log_info("Finished 08_Create_Remaining_County_Level_Weights.R")
