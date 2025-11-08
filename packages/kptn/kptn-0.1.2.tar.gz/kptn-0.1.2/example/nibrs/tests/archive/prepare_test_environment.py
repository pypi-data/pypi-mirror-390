import json
import os
import pathlib
import shutil

from tasks.all import fetch_external_files
from tasks.store import FileStore

THIS_DIR = pathlib.Path(__file__).parent.resolve()

scratch_dir = THIS_DIR / "test_output_files"
scratch_dir.mkdir(exist_ok=True)

store = FileStore(
    external_location=os.environ["EXTERNAL_STORE"],
    artifact_location=str(scratch_dir),
)

gold_standard_dir = THIS_DIR / "gold_standard_output_full"
gold_standard_dir.mkdir(exist_ok=True)
external_config = gold_standard_dir / "external_file_locations.json"

shutil.copy("data/external_file_locations.json", external_config)

fetch_external_files.fn(store, external_config, scratch_dir)  # type: ignore [call-arg]

with open("tests/gs_files_to_copy.json", "r") as file_list:
    gs_list = json.load(file_list)
    for file in gs_list:
        print("Fetching gold standard file:", file)
        store.fetch_external(
            store_file=f"gold_standard_output_full{file}",
            to_file=str(THIS_DIR / f"gold_standard_output_full{file}"),
        )
