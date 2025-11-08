# NIBRS Estimation Pipeline

This repository contains a data pipeline for producing nationally-representative estimates using data from the National Incident-Based Reporting System (NIBRS).

The pipeline infrastructure is implemented using Prefect, and the pipeline tasks are implemented using R scripts or Python scripts. Input files and output files are stored either locally or on S3, depending on the use case.


## Supported use cases

We support running the pipeline under the following use cases:

- Production: Running in AWS using Prefect Server. Input and output files are stored on S3.
- Pipeline development and CI: Running in Docker locally. Input files are stored on S3, and output files are stored locally.
- Statistics development: Running only the R scripts, locally and without Docker or Python. Input and output files are stored locally.


## Running via Docker for pipeline development and CI:

Create a `.env` file. In order to connect to a database (testing or otherwise) and to S3, we use a `.env` file to store our secrets.  This file isn't committed to the code repository so every user must make it themselves. `.sample_env` is an example of what the file should look like and what variables are necessary.  **The env file is required to build the docker image**.  The secrets used in development can be found in the CI/CD Variables section of our repository.

Then you can build the image:

```
docker compose build
```

Decide which flow you want to run. See [flows.py](./flows.py) for a list of available flows, or run `docker compose run --rm prefect python flows.py run --help`.

Then you can run the pipeline:

```
docker compose run --rm prefect bash -c "python flows.py run <flow_name> <run_id>"
```

In the above command, replace `<flow_name>` with the name of the flow you want to run, and replace `<run_id>` with the ID you'd like to assign to the flow run.

Scratch files generated during the run will be stored in `./scratch/<run_id>/<flow_name>`. Artifacts generated during the run will be stored in `./artifacts/<run_id>`

The LOG_THRESHOLD environment variable controls the minimum level of logging which is outputted by the R scripts as the tasks run. This variable is set in `docker compose.yml` and defaults to DEBUG. Logs are saved in `.log` files for each unique task.

## Running the R scripts outside of Docker

The R scripts in this repository can be run outside of the docker containers without any modifications. To do this, environment variables need to be set and a copy of `.\data\external_file_locations.json` needs to be moved to the base level of the data input/output folder. `sample_set_env.R` is an example of what the R script should look like to set the environment variables. The following set of variables are needed for every task:

* DATA_YEAR: The year for which estimates should be generated.
* EXTERNAL_FILE_PATH: The path to the External_Files_for_Pipeline folder on the share or somewhere else. (See "Mounting a share drive for external files")
* INPUT_PIPELINE_DIR: The path to a directory which contains an external_file_locations.json file which indicates which file paths should be used for external files. It should also include any additional input files (like the output files of previous steps) used by the script.
* OUTPUT_PIPELINE_DIR: The path to where output files from the scripts should be placed. This is often the same as INPUT_PIPELINE_DIR, especially if you intend to use the output of one step as the input to the next.
* LOG_THRESHOLD: An optional environment variable which controls the level of logging information printed. Options include: TRACE, DEBUG, INFO

The environment variables used to find the database with NIBRS data used by the scripts also need to be set:

* PGHOST: Host location for the database
* PGPORT: Port the database is on
* PGUSER: Username for accessing the database
* PGPASSWORD: Password for accessing the database
* PGDATABASE: Database name

**NOTE:** the code assumes that your working directory is inside the folder for the task you are running and imports will break otherwise.

Each task has a README which describes any additional environment variables needed and has a summary of how to run the task.

The full list of R packages used and their version numbers can be found in the Dockerfile.

## Running tests and linting

Testing and linting are run automatically as part of our GitLab continuous integration script. If you want to test and lint on your own, you can run each tool individually with something like:

 ```
$ docker compose run --rm prefect isort .
$ docker compose run --rm prefect mypy .
$ ...
 ```

See [.github/workflows](./.github/workflows/) for all the testing and linting commands.

See [the README in the tests directory](tests/README.md) for directions for running the R tests.


## Dependency management in Python

We use [uv](https://docs.astral.sh/uv/) to manage Python dependencies. To change the dependencies:

1. Edit [pyproject.toml](./pyproject.toml) to add, remove, or edit a dependency. You only need to put primary dependencies here, that is, the ones explicitly needed by our source code. `uv` will take care of adding their dependencies.
1. Run `uv lock` to update `uv.lock` based on `pyproject.toml`


## Deployment

Deployment is a two-stage process with all relevant code found in the `cdk/` directory.

1. A one-time deployment stage of all AWS architecture using AWS Cloudformation.
    * Relevant information is in the `cdk/` directory.
    * This should be performed on a developer's machine and the developer will need follow the instructions in the `cdk/` directory.
1. Deployment of flow specifications to prefect-server & flow images to ECR. This stage is performed by the developer from their loal machine.
    * Relevant information is in the `cdk/` directory.
