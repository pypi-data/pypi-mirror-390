create_other_recodes <- function(indata){


	#Code new other agency variable
	returndata <- indata %>%
	  mutate(
	  #Create new variables   
	  PUB_AGENCY_NAME = PUB_AGENCY_NAME_UNIV,
	  NCIC_AGENCY_NAME = NCIC_AGENCY_NAME_UNIV,
	    
		der_other_agencies = fcase(
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="AIRPORT"), "1-AIRPORT",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="AIRPORT"), "1-AIRPORT",
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="AVIATION"), "1-AIRPORT",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="AVIATION"), "1-AIRPORT",      
					 
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="RAILWAY"), "2-RAILROAD",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="RAILWAY"), "2-RAILROAD",    
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="RAILROAD"), "2-RAILROAD",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="RAILROAD"), "2-RAILROAD",   
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="TRANSPORTATION"), "3-TRANSPORTATION",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="TRANSPORTATION"), "3-TRANSPORTATION",      
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="TRANSPORT POLICE"), "3-TRANSPORTATION",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="TRANSPORT POLICE"), "3-TRANSPORTATION",
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="TRANSIT"), "3-TRANSPORTATION",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="TRANSIT"), "3-TRANSPORTATION",      
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="RIVER AND BAY AUTHORITY"), "3-TRANSPORTATION",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="RIVER AND BAY AUTHORITY"), "3-TRANSPORTATION",      
		  
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="AGRICULTURE"), "4-AGRICULTURE",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="AGRICULTURE"), "4-AGRICULTURE",      
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="ANIMAL"), "4-AGRICULTURE",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="ANIMAL"), "4-AGRICULTURE", 
		  
		  ####################Need to code environment drug earlier#####################################
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="ENVIRONMENTAL .* DRUG"), "9-DRUG",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="ENVIRONMENTAL .* DRUG"), "9-DRUG", 
		  ###############################################################################################
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="ENVIRONMENTAL"), "5-ENVIRONMENTAL",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="ENVIRONMENTAL"), "5-ENVIRONMENTAL",  
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="ENVIRON"), "5-ENVIRONMENTAL",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="ENVIRON"), "5-ENVIRONMENTAL",    
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="ENVIRONMT"), "5-ENVIRONMENTAL",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="ENVIRONMT"), "5-ENVIRONMENTAL",        
				
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="CONSERVATION"), "5-ENVIRONMENTAL",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="CONSERVATION"), "5-ENVIRONMENTAL",  
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="CONSERVANCY"), "5-ENVIRONMENTAL",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="CONSERVANCY"), "5-ENVIRONMENTAL",   
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="WILDLIFE"), "5-ENVIRONMENTAL",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="WILDLIFE"), "5-ENVIRONMENTAL",   
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="FISHERIES"), "5-ENVIRONMENTAL",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="FISHERIES"), "5-ENVIRONMENTAL",     
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="FISH AND BOAT"), "5-ENVIRONMENTAL",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="FISH AND BOAT"), "5-ENVIRONMENTAL",    
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="MARINE"), "5-ENVIRONMENTAL",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="MARINE"), "5-ENVIRONMENTAL",        
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="WATER RECLAMATION"), "5-ENVIRONMENTAL",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="WATER RECLAMATION"), "5-ENVIRONMENTAL",  
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="NATURAL RESOURCE"), "5-ENVIRONMENTAL",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="NATURAL RESOURCE"), "5-ENVIRONMENTAL",        
			
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="STATE PARK"), "5-ENVIRONMENTAL",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="STATE PARK"), "5-ENVIRONMENTAL", 
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="STATE PARK"), "5-ENVIRONMENTAL",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="STATE PARK"), "5-ENVIRONMENTAL",  
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="METROPARK"), "5-ENVIRONMENTAL",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="METROPARK"), "5-ENVIRONMENTAL",    
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="PARK RANGER"), "5-ENVIRONMENTAL",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="PARK RANGER"), "5-ENVIRONMENTAL",   
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="RANGER"), "5-ENVIRONMENTAL",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="RANGER"), "5-ENVIRONMENTAL",    
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="PARK DISTRICT"), "5-ENVIRONMENTAL",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="PARK DISTRICT"), "5-ENVIRONMENTAL",

		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="PARK POLICE"), "5-ENVIRONMENTAL",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="PARK POLICE"), "5-ENVIRONMENTAL",
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="COUNTY PARK"), "5-ENVIRONMENTAL",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="COUNTY PARK"), "5-ENVIRONMENTAL",
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="PARKS AND RECREATION"), "5-ENVIRONMENTAL",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="PARKS AND RECREATION"), "5-ENVIRONMENTAL",
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="PARK PD"), "5-ENVIRONMENTAL",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="PARK PD"), "5-ENVIRONMENTAL",
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern=" PARKS$"), "5-ENVIRONMENTAL",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern=" PARKS$"), "5-ENVIRONMENTAL",      
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="PRESERVATION PARK"), "5-ENVIRONMENTAL",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="PRESERVATION PARK"), "5-ENVIRONMENTAL",        
		
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="FORESTRY"), "5-ENVIRONMENTAL",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="FORESTRY"), "5-ENVIRONMENTAL",      
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="FOREST PRESERVE"), "5-ENVIRONMENTAL",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="FOREST PRESERVE"), "5-ENVIRONMENTAL",
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="LAKE PATROL"), "5-ENVIRONMENTAL",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="LAKE PATROL"), "5-ENVIRONMENTAL",      
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="HURON-CLINTON METROPOLITAN AUTHORITY"), "5-ENVIRONMENTAL",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="HURON-CLINTON METROPOLITAN AUTHORITY"), "5-ENVIRONMENTAL",   
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="ARBORETUM"), "5-ENVIRONMENTAL",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="ARBORETUM"), "5-ENVIRONMENTAL",
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="UNITED STATES DEPARTMENT OF ENERGY SAVANNAH RIVER PLANT"), "5-ENVIRONMENTAL",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="UNITED STATES DEPARTMENT OF ENERGY SAVANNAH RIVER PLANT"), "5-ENVIRONMENTAL",      
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="PORT AUTHORITY"), "6-PORT POLICE",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="PORT AUTHORITY"), "6-PORT POLICE",  
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="PORTS AUTHORITY"), "6-PORT POLICE",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="PORTS AUTHORITY"), "6-PORT POLICE",  
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="PORT OF"), "6-PORT POLICE",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="PORT OF"), "6-PORT POLICE",  
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="^PORT "), "6-PORT POLICE",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="^PORT "), "6-PORT POLICE",  
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="ALCOHOL"), "7-ALCOHOL",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="ALCOHOL"), "7-ALCOHOL",      
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="LIQUOR"), "7-ALCOHOL",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="LIQUOR"), "7-ALCOHOL",   
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="EXCISE"), "7-ALCOHOL",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="EXCISE"), "7-ALCOHOL",      
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="GAMING"), "8-GAMING POLICE",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="GAMING"), "8-GAMING POLICE",        
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="GAMBLING"), "8-GAMING POLICE",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="GAMBLING"), "8-GAMING POLICE",        
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="RACING"), "8-GAMING POLICE",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="RACING"), "8-GAMING POLICE",
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="LOTTERY"), "8-GAMING POLICE",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="LOTTERY"), "8-GAMING POLICE",      
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="DRUG"), "9-DRUG",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="DRUG"), "9-DRUG", 
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="NARCOTIC"), "9-DRUG",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="NARCOTIC"), "9-DRUG",
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="MAJOR CRIME"), "9-DRUG",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="MAJOR CRIME"), "9-DRUG",      
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="FIRE"), "10-FIRE",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="FIRE"), "10-FIRE",  
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="ARSON"), "10-FIRE",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="ARSON"), "10-FIRE",       
		  
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="HEALTH"), "11-HEALTH",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="HEALTH"), "11-HEALTH",       
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="DEVELOPMENTAL"), "11-HEALTH",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="DEVELOPMENTAL"), "11-HEALTH",        

		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="HOSPITAL"), "11-HEALTH",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="HOSPITAL"), "11-HEALTH",   
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="MEDICAL CENTER"), "11-HEALTH",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="MEDICAL CENTER"), "11-HEALTH",  

		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="MEDICAL FACILITY"), "11-HEALTH",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="MEDICAL FACILITY"), "11-HEALTH",    
		
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="MEDICAL"), "11-HEALTH",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="MEDICAL"), "11-HEALTH",         
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="WAKEMED CAMPUS"), "11-HEALTH",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="WAKEMED CAMPUS"), "11-HEALTH",      
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="SCHOOL"), "12-SCHOOL",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="SCHOOL"), "12-SCHOOL",      
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="CAMPUS"), "12-SCHOOL",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="CAMPUS"), "12-SCHOOL",
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="EDUCATION"), "12-SCHOOL",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="EDUCATION"), "12-SCHOOL",      
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="REGENT"), "12-SCHOOL",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="REGENT"), "12-SCHOOL",      
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="CONSTABLE"), "13-CONSTABLE",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="CONSTABLE"), "13-CONSTABLE",        
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="CORRECTION"), "14-CORRECTION",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="CORRECTION"), "14-CORRECTION",
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="CRIMINAL JUSTICE"), "14-CORRECTION",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="CRIMINAL JUSTICE"), "14-CORRECTION",      
	  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="INVESTIGATION"), "15-INVESTIGATION",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="INVESTIGATION"), "15-INVESTIGATION",       
				 
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="INVESTIGATIVE"), "15-INVESTIGATION",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="INVESTIGATIVE"), "15-INVESTIGATION", 
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="CYBER CRIMES"), "15-INVESTIGATION",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="CYBER CRIMES"), "15-INVESTIGATION", 
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="INSPECTOR GENERAL"), "15-INVESTIGATION",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="INSPECTOR GENERAL"), "15-INVESTIGATION",          
		  
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="COURT"), "16-COURT",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="COURT"), "16-COURT",      
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="DISTRICT ATTORNEY"), "16-COURT",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="DISTRICT ATTORNEY"), "16-COURT",      
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="ATTORNEY GENERAL"), "16-COURT",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="ATTORNEY GENERAL"), "16-COURT",  
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="COUNTY DETECTIVE"), "16-COURT",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="COUNTY DETECTIVE"), "16-COURT",        
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="ATTORNEY"), "16-COURT",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="ATTORNEY"), "16-COURT",       
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="PROSECUTOR"), "16-COURT",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="PROSECUTOR"), "16-COURT",    
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="CAPITOL POLICE"), "17-CAPITOL POLICE",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="CAPITOL POLICE"), "17-CAPITOL POLICE",
			   
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="STATE CAPITOL"), "17-CAPITOL POLICE",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="STATE CAPITOL"), "17-CAPITOL POLICE",
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="GENERAL ASSEMBLY"), "17-CAPITOL POLICE",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="GENERAL ASSEMBLY"), "17-CAPITOL POLICE",
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="CAPITOL"), "17-CAPITOL POLICE",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="CAPITOL"), "17-CAPITOL POLICE",
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="PROTECTIVE SERVICE"), "17-CAPITOL POLICE",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="PROTECTIVE SERVICE"), "17-CAPITOL POLICE",
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="GENERAL SERVICE"), "17-CAPITOL POLICE",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="GENERAL SERVICE"), "17-CAPITOL POLICE",      
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="STATE FAIR"), "18-FAIRGROUND POLICE",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="STATE FAIR"), "18-FAIRGROUND POLICE",      
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="FAIRGROUND"), "18-FAIRGROUND POLICE",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="FAIRGROUND"), "18-FAIRGROUND POLICE",      

		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="HORSE PARK"), "18-FAIRGROUND POLICE",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="HORSE PARK"), "18-FAIRGROUND POLICE",      
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="COMMERCE"), "19-REVENUE",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="COMMERCE"), "19-REVENUE",
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="REVENUE"), "19-REVENUE",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="REVENUE"), "19-REVENUE",
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="TREASURY"), "19-REVENUE",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="TREASURY"), "19-REVENUE",
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="TAX"), "19-REVENUE",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="TAX"), "19-REVENUE",      
		  
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="PUBLIC SERVICE"), "20-PUBLIC SERVICE",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="PUBLIC SERVICE"), "20-PUBLIC SERVICE",       
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="HOUSING"), "20-PUBLIC SERVICE",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="HOUSING"), "20-PUBLIC SERVICE",
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="HUMAN SERVICE"), "20-PUBLIC SERVICE",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="HUMAN SERVICE"), "20-PUBLIC SERVICE",
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="LABOR"), "20-PUBLIC SERVICE",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="LABOR"), "20-PUBLIC SERVICE",
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="MOTOR VEHICLE"), "20-PUBLIC SERVICE",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="MOTOR VEHICLE"), "20-PUBLIC SERVICE",
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="PUBLIC SAFETY"), "20-PUBLIC SERVICE",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="PUBLIC SAFETY"), "20-PUBLIC SERVICE",
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="SOCIAL SERVICE"), "20-PUBLIC SERVICE",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="SOCIAL SERVICE"), "20-PUBLIC SERVICE",

		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="BEACH SAFETY"), "20-PUBLIC SERVICE",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="BEACH SAFETY"), "20-PUBLIC SERVICE",      
				
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="BEACH SAFETY"), "20-PUBLIC SERVICE",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="BEACH SAFETY"), "20-PUBLIC SERVICE", 
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="CRIMINAL APPREHENSION"), "20-PUBLIC SERVICE",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="CRIMINAL APPREHENSION"), "20-PUBLIC SERVICE",       
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="SECRETARY OF STATE"), "20-PUBLIC SERVICE",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="SECRETARY OF STATE"), "20-PUBLIC SERVICE",  
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="SECURITIES"), "20-PUBLIC SERVICE",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="SECURITIES"), "20-PUBLIC SERVICE",       
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="INSURANCE"), "20-PUBLIC SERVICE",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="INSURANCE"), "20-PUBLIC SERVICE",
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="MARSHAL"), "20-PUBLIC SERVICE",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="MARSHAL"), "20-PUBLIC SERVICE", 
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="LAW ENFORCEMENT"), "21-POLICE",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="LAW ENFORCEMENT"), "21-POLICE", 
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="ALL CRIMES ENFORCEMENT"), "21-POLICE",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="ALL CRIMES ENFORCEMENT"), "21-POLICE", 
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="POLICE"), "21-POLICE",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="POLICE"), "21-POLICE", 
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern=" PD"), "21-POLICE",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern=" PD"), "21-POLICE", 
		  
		  str_detect(string=trim_upcase(PUB_AGENCY_NAME), pattern="TASK FORCE"), "21-POLICE",
		  str_detect(string=trim_upcase(NCIC_AGENCY_NAME), pattern="TASK FORCE"), "21-POLICE", 
								
		  default = "21-POLICE"
		  
		  
		),
		
		der_agency_subtype = str_match(string=der_other_agencies, pattern="(\\d+)-")[,2] %>% as.numeric()
		
	  )
	  
		#Return the data
		return(returndata %>% select(-der_other_agencies, -PUB_AGENCY_NAME, -NCIC_AGENCY_NAME))
	  
}	  
