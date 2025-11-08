import os
from pathlib import Path
from tasks.store import FileStore


def _resolve_local_path(candidate: str) -> str:
    path = Path(candidate)
    if path.is_absolute():
        return str(path)
    pipeline_root = Path(__file__).resolve().parents[1]
    return str((pipeline_root / path).resolve())


def get_scratch_dir() -> str:
    output_pipeline_dir = os.getenv("SCRATCH_DIR")  # Should be /data/$branch in AWS container
    return output_pipeline_dir if output_pipeline_dir else "scratch"
    # storage_key = get_storage_key(pipeline_config)
    # if output_pipeline_dir:
    #     return Path(output_pipeline_dir) / storage_key
    # else:
    #     return Path(project_root) / "scratch" / storage_key


def get_store() -> FileStore:
    external_location = os.getenv("EXTERNAL_STORE", "s3://nibrs-estimation-externals")
    if not external_location.startswith("s3://"):
        external_location = _resolve_local_path(external_location)

    artifact_location = os.getenv("ARTIFACT_STORE", "artifacts")
    if not artifact_location.startswith("s3://"):
        artifact_location = _resolve_local_path(artifact_location)

    store = FileStore(
        external_location=external_location,
        artifact_location=artifact_location,
    )
    return store
