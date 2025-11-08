## Arguments and Conventions 

The R tests take the following arguments, which you may want to set depending on your use case:

* The first argument to the R tests can be "all" to iterate over all available test folders, or optionally the user can specify one folder, ex: `tests/tests_partial_reporter` to only run the tests in that folder.
* Add the `-d` flag to delete the gold standard and test output files after the test run. By default these are retained. 

## Running Through Docker

When running in docker, the test setup and breakdown will be handled for you. Gold standard files needed for test output comparison and external files needed for tasks are pulled down from S3 automatically before tests run.

EXAMPLES:
   * To run all tests: `docker-compose run --rm -T prefect bash -c "./tests/run_tests.sh all"`
   * To run just the tests in the tests_partial_reporter folder: `docker-compose run --rm -T prefect bash -c "./tests/run_tests.sh tests/tests_partial_reporter"`
   * To run just the tests in the tests_partial_reporter folder and drop the gold_standard_output_full and test_output_files folders after the tests finish: `docker-compose run --rm -T prefect bash -c "./tests/run_tests.sh tests/tests_partial_reporter -d"`

**TODO: this part needs to be updated for directions for the new runner**
Gitlab's continuous integration (CI) system will run all R tests whenever a new commit is pushed. 



## Running Without Docker (Recommended for Windows Users)

To run the R tests outside of docker, follow these directions:

1. Within your local repository, make a directory `./tests/test_output_files/`
1. Inside that directory, make another directory `./tests/test_output_files/externals`
1. Copy the external file directory contents into the folder you just made. The directory structure should look like the following:

    ```
    tests /
      test_output_files /
        externals /
          2016 /
          2017 /
          ...
      ...
    ```
    **Note:** A copy of the external file directory may be obtained from the project share at: `NIBRS data/External_Files_for_Pipeline`
1. To acquire the gold standard files needed for the tests, you can copy them from the project share at `NIBRS data/gold_standard_output_full`. Copy this folder into the `tests` directory.
1. Make sure that the test database credentials are saved in environment variables (see `Running the R scripts outside of Docker` in main README).
1. Run the testing script with the same arguments specified above: `Rscript tests/run_r_tests.R "TEST" <all or test folder>`

## Writing R Tests


The test folder is set up so each task has a `tests_<taskname>` folder, and within that each subtask has a test file `test_<subtaskname>.R`. There is also one setup file which is shared by all subtasks in the task `setup_<taskname>.R`.

To set up a new test file with gold standard tests, follow these steps:

1. Create the task folder if not already existing
1. Create the setup file for the task, which should define:
  * The tests in the directory
  * The output folder where each test puts their outputs in. This can be found by looking at the task being run by the test. 
  * The list of output files which we intend to compare in each test.
1. Copy the following template into your test R file and fill in the <> sections with task-specific information. See previously created tasks for more details.
        ```
        context("<Name of Task> Tests")

        source("../utils.R")
        setEnvForTask("../../tasks/<path to inner task folder>")

        system("Rscript <Run task R script>")

        imputed_fields <- list(<list with inner lists corresponding to each output file. The inner list is the name of fields that we don't want to compare in the gold standard test>)

        compareOutputToGoldStandard(listOfFiles,imputed_fields, "/<path to output files once within gold standard folder>/")
        ```
      Helpful tips:
      * task-context environment variables like DATA_YEAR and INPUT_STATE are set in `run_r_tests.R` to be shared between all tasks which need them.
      * if an output file from the task is read in and used by a future task or step in the same task, then it should have a gold standard file.
1. Run the test without the `-d` flag the first time. They should fail as there are currently no gold standard files to compare against. The outputs of these runs should be reviewed and, if valid, saved as the new gold standards. 
1. Run the tests again. They should now pass as the outputs created should match the new gold standards.
1. Update the `gold_standard_output_full` folder on the share to include the new gold standards for Windows users and update the versions on S3 for the docker users.
