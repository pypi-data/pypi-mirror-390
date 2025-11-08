# NIBRS Estimation Pipeline

## Running data quality validation scripts outside of Docker

No additional environment variables are needed to run the data quality validation scripts outside of Docker. Once the environment variables from the main README have been defined and the working directory is set to `./nibrs-estimation-pipeline/tasks/validation/data_quality`, all that is required is running `1000_Run_DQ_Validation.R`.

Additionally if you do not already have the required input files for this task, please reference `./nibrs-estimation-pipeline/tasks/validation/extracts/README.md` for instructions on how to generate the inputs.

## Additional notes on the data quality validation scripts

Sections of the program:

	#Define reviewSearch() - function
	#Define finalSEARCH_log() -Function
	#Define keep - list  
	# Tab 3: Incident Time   
	# Tab 4: Cleared Exceptionally
	# Tab 6: Attempted Incidents
	# Tab 8*: Bias Motivation
	# Tab 9: Unknown Location Type
	# Tab 15: Unknown Property Type
	# Tab 26: Victim Age
	# Tab 27: Victim Sex
	# Tab 28: Victim Race
	# Tab 31: Unknown Agg Asslt Circ
	# Tab 32*: Additional Justifiable Homicide Circumstances
	# Tab 37: Offender Age
	# Tab 38: Offender Sex
	# Tab 39: Offender Race
	# Tab 47*: Age of Arrestee
	# Tab 49*: Race of Arrestee
	
*Deterministic threshold for flagging, no IQR plot/table


Data Processing Steps within each "tab" section:

	1. Import aggregated state crime csv file
	2a. Calculate "*_sum", counts by ucr_agency_name, ori, state_abbr, [crime var]
	2b. calculate "*_excel", transpose dataframe to "Agency Name", "ORI","State Abbreviation", "No", "Yes" columns
	2c. Caculate variable "Total" as colsum of "yes"
	3. Replace NA with 0's
	4a. calculate *_excel variable: "Proportion of Incidents*" as min(0, Yes/Total).
	4b. calculate *_iqr dataframe: *_excel subset by total > 15 & proportion not 1 or 0
	4c. calculate *_review dataframe: *_excel subset by total > 15 & proportion == 1
	5. Print datatables of *_review and *_iqr to console
	6. Print *_iqr density plot of proportion of incidents to console
	7. Run reviewSearch() function
	8. Calculate *_iqr$`Log Proportion`
	9. Run finalSEARCH_log() function
	10. Save *_excel to *_excel_final to be saved from global object removal.
	11. Repeat for each crime, aggregate as an excel file "* Search Validation.xlsx"
	12. Save df_flagged to "*_excel_final". Extreme values table saved as an global object.

Print to HTML/Rmd:

	Output datatables:
		*_review dataframe - Agencies with 100% of cases Unknown/unexpected values (0% or 100%)
		*_iqr dataframe - Agencies with proportion of cases(not 0 or 1)
		density plot *_iqr dataframe
	Output plot:
		"Proportion of Incidencts *"
	Output by Function finalSEARCH_log():
		p1/p2 - output -  ggplot density plots by IQR thresholds
		agencyTbl - output - agencies color coded by IQR thresholds
		critical_df - output - summary statistics defining IQR and K*IQR thresholds



