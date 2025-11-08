Sys.setenv(INPUT_PIPELINE_DIR="./Example/Data/location",
           OUTPUT_PIPELINE_DIR="./Example/Data/location",
           EXTERNAL_FILE_PATH="//rtpnfil02.rti.ns/0216153_NIBRS/NIBRS data/External_Files_for_Pipeline",
           PGDATABASE = "NIBRS_EXAMPLE_DATABASE",
           PGHOST= "localhost",
           PGPORT = 5432,
           PGUSER = "nibrs_user",
           PGPASSWORD = 'postgres',
           DATA_YEAR=2021,
           LOG_THRESHOLD = "DEBUG",
)

setwd("PATH/TO/NIBRS/TASK/FOLDER")