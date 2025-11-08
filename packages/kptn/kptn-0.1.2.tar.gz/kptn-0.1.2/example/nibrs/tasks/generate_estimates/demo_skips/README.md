# NIBRS Estimation Pipeline

## Demo skips scripts outside of Docker

### Part 1 - Find

No additional environment variables are needed to run the find demo script outside of Docker. Once the environment variables from the main README have been defined and the working directory is set to `./nibrs-estimation-pipeline/tasks/demo_skips`, all that is required is running `100_Find_Demo_Skips.R`.

### Part 2 - Fill missing

The second demo skip script (which creates the missing variance outputs) require 2 additional environment variables. Each variable is described below:

 - `TABLE_NAME`: Expected values are 1a - 1c, 2a - 2c, 3a - 3c, 4a - 4b, LEOKA, DM1 - DM10, 5a - 5b, GV1a, GV2a, YT1, YT2, 
                 3aclear, 3aunclear, 3bclear, & 3bunclear
 - `DEMO_PERM`: The demographic permutation which was skipped: 21000, 54000, 135000, etc.

The example below uses all of the arguments to run DM7 for 74000.

```
source('../../logging.R')

Sys.setenv(TABLE_NAME = "DM7",
           DEMO_PERM = 74000)

source('200_Fill_Demo_Skips.R')
```