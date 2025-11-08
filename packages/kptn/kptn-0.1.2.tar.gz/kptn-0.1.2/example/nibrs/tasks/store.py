import shutil
from abc import ABC, abstractmethod
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Optional, Union

import boto3
from botocore import exceptions as boto_exceptions
from botocore.config import Config


class StorageAgent(ABC):
    @abstractmethod
    def get_file(self, store_file: Union[str, Path], to_file: Union[str, Path]) -> None:
        pass

    @abstractmethod
    def put_file(
        self, from_file: Union[str, Path], store_file: Union[str, Path]
    ) -> None:
        pass


class LocalStorageAgent(StorageAgent):
    def __init__(self, base_dir: Union[str, Path]):
        """Create a StorageAgent operating on a local directory."""
        self.base_dir = Path(base_dir)

    def get_file(self, store_file: Union[str, Path], to_file: Union[str, Path]) -> None:
        """Copy a file from the local store to a local file.

        store_file must be relative to the storage agent's base dir.
        """
        Path(to_file).parent.mkdir(exist_ok=True, parents=True)
        shutil.copy2(self.base_dir / store_file, to_file)

    def put_file(
        self, from_file: Union[str, Path], store_file: Union[str, Path]
    ) -> None:
        """Copy a local file to the local store.

        store_file must be relative to the storage agent's base dir.
        """
        to_file = self.base_dir / store_file
        to_file.parent.mkdir(exist_ok=True, parents=True)
        shutil.copy2(from_file, to_file)


class S3StorageAgent(StorageAgent):
    def __init__(self, bucket: str):
        """Create a StorageAgent operating on the given S3 bucket."""
        self.bucket = bucket

    def get_file(self, store_file: Union[str, Path], to_file: Union[str, Path]) -> None:
        """Copy a file from the S3 store to a local file."""
        Path(to_file).parent.mkdir(exist_ok=True, parents=True)
        s3 = boto3.client("s3", config=Config(retries={"max_attempts": 3}))
        try:
            s3.download_file(self.bucket, str(store_file), str(to_file))
        except boto_exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "404":
                raise FileNotFoundError(
                    f"ERROR: unable to find {str(store_file)} in S3 bucket."
                )
            else:
                raise e

    def put_file(
        self, from_file: Union[str, Path], store_file: Union[str, Path]
    ) -> None:
        """Copy a local file to the S3 store."""
        s3 = boto3.client("s3")
        s3.upload_file(str(from_file), self.bucket, str(store_file))


def build_external_dir(
    vintage_year: str,
    code_name: str,
    receipt_date: date,
    counter: int,
) -> Path:
    """Return the path to the external file with the given attributes, relative to the base of the file store."""
    return Path(vintage_year) / code_name / f"{receipt_date}-{counter}"


def build_artifact_dir(
    run_id: str,
    to_dir: Path,
) -> Path:
    """Return the path to the artifact with the given attributes, relative to the base of the file store."""
    return Path(run_id) / to_dir


class FileStoreError(Exception):
    pass


class FileStore:
    def __init__(
        self,
        external_location: str,
        artifact_location: str,
    ):
        """Create a new file store object.

        The file store manages two locations: one holding external files and
        another holding artifacts. If the location starts with "s3://", such as
        "s3://bucket-name", then it is assumed to be a bucket stored on S3.
        Otherwise, it is assumed to be a local path.
        """
        self.external_location = external_location
        is_external_s3 = self.external_location.startswith("s3://")
        if is_external_s3:
            bucket = self.external_location[len("s3://") :]
            self.external_agent: StorageAgent = S3StorageAgent(bucket)
        else:
            path = Path(external_location)
            if not path.is_dir():
                raise FileNotFoundError(f"External file base path {path} doesn't exist")
            self.external_agent = LocalStorageAgent(path)

        self.artifact_location = artifact_location
        is_artifact_s3 = self.artifact_location.startswith("s3://")
        if is_artifact_s3:
            bucket = self.artifact_location[len("s3://") :]
            self.artifact_agent: StorageAgent = S3StorageAgent(bucket)
        else:
            path = Path(artifact_location)
            if not path.is_dir():
                raise FileNotFoundError(f"Artifact base path {path} doesn't exist")
            self.artifact_agent = LocalStorageAgent(path)

        self.incoming_path = Path("__incoming")

    def add_external(
        self,
        code_name: str,
        vintage_year: str,
        receipt_date: date,
        counter: int,
        file_name: str,
        notes: Optional[str] = None,
    ) -> None:
        """Copy an external file from the file store's "incoming" area into the file store proper.

        file_name must exist in the file store's incoming directory, not a
        subdirectory of it. Furthermore, it must refer to an individual file, not
        a directory.
        """
        # TODO: Can we implement this more efficiently? The file starts on S3,
        # but we download it and then upload it back to a different S3 location.
        # Instead, can we simply copy it from one S3 location to another? At the
        # moment, our storage agent doesn't support copying from one location
        # within the store to another. It either copies into or out of the
        # store. Adding a copy_file method to handle within-store copies should
        # address this.
        #
        # TODO: Should we delete the file from __incoming after we've copied it
        # to the new location?

        with TemporaryDirectory() as tmp_dir_str:
            tmp_dir = Path(tmp_dir_str)
            incoming_store_file = self.incoming_path / file_name
            local_file = tmp_dir / file_name
            self.external_agent.get_file(
                store_file=incoming_store_file, to_file=local_file
            )

            store_dir = build_external_dir(
                vintage_year=vintage_year,
                code_name=code_name,
                receipt_date=receipt_date,
                counter=counter,
            )
            store_file = store_dir / file_name

            self.external_agent.put_file(from_file=local_file, store_file=store_file)

    def fetch_external(
        self,
        store_file: str,
        to_file: str,
    ) -> None:
        """Copy an external file from the file store to a local path."""
        self.external_agent.get_file(store_file=store_file, to_file=to_file)

    def add_artifact(
        self,
        run_id: str,
        from_file: Union[str, Path],
        to_dir: Union[str, Path],
    ) -> None:
        """Copy an artifact from a local path into the file store.

        to_dir is the subdirectory within the artifact space where the artifact
        should be stored. The subdirectory can include any number of levels of
        nesting, so for example both Path("qc") and Path("qc/imputation/block")
        are valid. Even Path(".") is OK.

        from_file must refer to an individual file, not a directory.
        """
        from_file = Path(from_file)

        if from_file.is_dir():
            raise ValueError(f"{from_file} is a directory")

        if not from_file.exists():
            raise FileNotFoundError(f"File {from_file} doesn't exist.")

        to_dir = Path(to_dir)
        store_dir = build_artifact_dir(
            to_dir=to_dir,
            run_id=run_id,
        )

        self.artifact_agent.put_file(
            from_file=from_file, store_file=store_dir / from_file.name
        )

    def fetch_artifact(
        self,
        store_file: Union[str, Path],
        to_file: Union[str, Path],
    ) -> None:
        """Copy an artifact from the file store to a local path."""
        self.artifact_agent.get_file(store_file=store_file, to_file=to_file)
