from pathlib import Path
import shutil

def external_config(scratch_dir: str) -> str:
    """Copies the external_file_locations file to the scratch dir.

    The external_file_locations file contains the file paths to specific versions
    of external files like reta-mm and universe which are needed for each year.
    This step copies the local repository version of this file into the pipeline
    folder so that there is a record of what versions of these files were used in
    the pipeline run.

    """
    # copy the input file ref into the pipeline directory so we can
    # record which dates were used

    Path(scratch_dir).mkdir(parents=True, exist_ok=True)
    to_file = Path(scratch_dir) / "external_file_locations.json"
    shutil.copyfile(
        "data/external_file_locations.json",
        to_file,
    )

    return str(to_file)