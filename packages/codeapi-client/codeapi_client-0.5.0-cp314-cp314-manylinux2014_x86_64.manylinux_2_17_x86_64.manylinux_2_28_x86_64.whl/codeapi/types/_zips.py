from __future__ import annotations

import asyncio
import base64
import zipfile
from io import BytesIO, IOBase
from pathlib import Path
from typing import BinaryIO, Type, TypeVar

from pydantic import BaseModel, field_serializer, field_validator
from typing_extensions import Self

from codeapi.types import JsonData

from ._enums import ExitType

EMPTY_ZIP_BYTES = b"\x50\x4b\x05\x06" + b"\x00" * 18

DOTENV_FILE = ".env"
PEXENV_FILE = "venv.pex"
PEXENV_CMD = f"./{PEXENV_FILE}"
REQUIREMENTS_TXT = "requirements.txt"
RESULT_JSON = "result.json"

TZip = TypeVar("TZip", bound="ZipBytes")


class ZipBytes(BaseModel):
    zip_bytes: bytes = EMPTY_ZIP_BYTES

    @field_serializer("zip_bytes")
    def serialize_bytes(self, value: bytes) -> str:
        return base64.b64encode(value).decode()

    @field_validator("zip_bytes", mode="before")
    @classmethod
    def deserialize_bytes(cls, value: bytes | str) -> bytes:
        if isinstance(value, bytes):
            return value
        return base64.b64decode(value)

    @property
    def files(self) -> list[str]:
        return self.list_files()

    def list_files(self) -> list[str]:
        with zipfile.ZipFile(BytesIO(self.zip_bytes)) as zf:
            return zf.namelist()

    def has_file(self, file: str) -> bool:
        return file in self.list_files()

    def print_files(self) -> None:
        with zipfile.ZipFile(BytesIO(self.zip_bytes)) as zf:
            return zf.printdir()

    def read_file(self, file: str) -> str:
        with zipfile.ZipFile(BytesIO(self.zip_bytes)) as zf:
            return zf.read(name=file).decode()

    def read_file_bytes(self, file: str) -> bytes:
        with zipfile.ZipFile(BytesIO(self.zip_bytes)) as zf:
            return zf.read(name=file)

    def read_files(self, files: list[str]) -> list[str]:
        with zipfile.ZipFile(BytesIO(self.zip_bytes)) as zf:
            return [zf.read(name=file).decode() for file in files]

    def read_files_bytes(self, files: list[str]) -> list[bytes]:
        with zipfile.ZipFile(BytesIO(self.zip_bytes)) as zf:
            return [zf.read(name=file) for file in files]

    def add_empty_file(self, name: str, arcdir: str = ".") -> Self:
        return self.add_file(arcdir=arcdir, name=name, file=b"")

    def add_file(
        self, file: Path | str | bytes, name: str | None = None, arcdir: str = "."
    ) -> Self:
        names = [name] if name is not None else None
        return self.add_files(files=[file], names=names, arcdir=arcdir)

    def add_files(
        self,
        files: list[Path | str | bytes],
        names: list[str] | None = None,
        arcdir: str = ".",
    ) -> Self:
        if names is not None and len(files) != len(names):
            raise ValueError("files and names must have the same length")

        arcnames = set()
        mem_zip = BytesIO()
        with zipfile.ZipFile(BytesIO(self.zip_bytes), "r") as zf_old:
            with zipfile.ZipFile(mem_zip, "w") as zf_new:
                for i, file in enumerate(files):
                    if isinstance(file, bytes):
                        name = names[i] if names is not None else None
                        if not name:
                            raise ValueError("name required when file is of type bytes")
                        arcname = (arcdir.rstrip("/") + "/" + name).removeprefix("./")
                        arcnames.add(arcname)
                        zf_new.writestr(arcname, file)
                    else:
                        name = names[i] if names is not None else Path(file).name
                        if not name:
                            name = Path(file).name
                        arcname = (arcdir.rstrip("/") + "/" + name).removeprefix("./")
                        arcnames.add(arcname)
                        zf_new.write(str(file), arcname)
                for f in set(zf_old.namelist()) - arcnames:
                    zf_new.writestr(f, zf_old.read(f))

        self.zip_bytes = mem_zip.getvalue()
        return self

    def delete_file(self, file: str) -> Self:
        return self.delete_files(files=[file])

    def delete_files(self, files: list[str]) -> Self:
        mem_zip = BytesIO()
        with zipfile.ZipFile(BytesIO(self.zip_bytes), "r") as zf_old:
            with zipfile.ZipFile(mem_zip, "w") as zf_new:
                for f in zf_old.namelist():
                    if f not in files:
                        zf_new.writestr(f, zf_old.read(f))
        self.zip_bytes = mem_zip.getvalue()
        return self

    def extract_file(
        self, file: str, path: Path | str = ".", flatten: bool = False
    ) -> Self:
        with zipfile.ZipFile(BytesIO(self.zip_bytes)) as zf:
            if flatten:
                target_path = Path(path) / Path(file).name
                target_path.parent.mkdir(parents=True, exist_ok=True)
                target_path.write_bytes(zf.read(name=file))
            elif Path(file).name in str(path):
                target_path = Path(path)
                target_path.parent.mkdir(parents=True, exist_ok=True)
                target_path.write_bytes(zf.read(name=file))
            else:
                zf.extract(member=file, path=str(path))
        return self

    def extract(self, path: Path | str, files: list[str] | None = None) -> Self:
        with zipfile.ZipFile(BytesIO(self.zip_bytes)) as zf:
            for file_info in zf.infolist():
                if ".." in file_info.filename or file_info.filename.startswith("/"):
                    raise ValueError("invalid file paths in archive")
            zf.extractall(path=str(path), members=files)
        return self

    def to_zipfile(self, path: Path | str) -> None:
        Path(path).write_bytes(data=self.zip_bytes)

    def to_bytesio(self) -> BytesIO:
        return BytesIO(self.zip_bytes)

    def to_codezip(self) -> CodeZip:
        return CodeZip(zip_bytes=self.zip_bytes)

    def to_datazip(self) -> DataZip:
        return DataZip(zip_bytes=self.zip_bytes)

    @classmethod
    def from_zipfile(cls: Type[TZip], path: Path | str) -> TZip:
        path = Path(path)
        if not path.is_file():
            raise ValueError(f"{path} is not a file")

        zip_bytes = path.read_bytes()
        if not cls.is_valid_zip(zip_bytes=zip_bytes):
            raise ValueError(f"{path} is not a valid zip file")
        return cls(zip_bytes=zip_bytes)

    @classmethod
    def from_dir(
        cls: Type[TZip],
        dir: Path | str,
        include_dir: bool = False,
        exclude: list[str] = ["__pycache__", ".venv"],
    ) -> TZip:
        dir = Path(dir)
        if not dir.is_dir():
            raise ValueError(f"{dir} is not a directory")

        zip_dir = dir.parent if include_dir else dir
        mem_zip = BytesIO()
        with zipfile.ZipFile(mem_zip, "w") as zf:
            for file in dir.rglob("*"):
                if all(excl not in str(file) for excl in exclude):
                    zf.write(file, file.relative_to(zip_dir))

        return cls(zip_bytes=mem_zip.getvalue())

    @classmethod
    def from_bytes(cls: Type[TZip], zip_bytes: bytes | BinaryIO) -> TZip:
        if isinstance(zip_bytes, (BinaryIO, IOBase)):
            zip_bytes.seek(0)
            zip_bytes = zip_bytes.read()
        if not cls.is_valid_zip(zip_bytes=zip_bytes):
            raise ValueError("given bytes are not a valid zip-archive")
        return cls(zip_bytes=zip_bytes)

    @classmethod
    def from_file(cls: Type[TZip], file: Path | str, arcdir: str = ".") -> TZip:
        return cls().add_file(file=file, arcdir=arcdir)

    @classmethod
    def from_files(
        cls: Type[TZip],
        files: list[Path | str | bytes],
        names: list[str] | None = None,
        arcdir: str = ".",
    ) -> TZip:
        return cls().add_files(files=files, names=names, arcdir=arcdir)

    @staticmethod
    def is_valid_zip(zip_bytes: bytes) -> bool:
        try:
            with zipfile.ZipFile(BytesIO(zip_bytes)) as zf:
                return zf.testzip() is None
        except zipfile.BadZipFile:
            return False

    async def list_files_async(self) -> list[str]:
        return await asyncio.to_thread(self.list_files)

    async def print_files_async(self) -> None:
        return await asyncio.to_thread(self.print_files)

    async def read_file_async(self, file: str) -> str:
        return await asyncio.to_thread(self.read_file, file)

    async def read_file_bytes_async(self, file: str) -> bytes:
        return await asyncio.to_thread(self.read_file_bytes, file)

    async def read_files_async(self, files: list[str]) -> list[str]:
        return await asyncio.to_thread(self.read_files, files)

    async def read_files_bytes_async(self, files: list[str]) -> list[bytes]:
        return await asyncio.to_thread(self.read_files_bytes, files)

    async def add_file_async(self, file: Path | str, arcdir: str = ".") -> Self:
        return await asyncio.to_thread(self.add_file, file, arcdir)

    async def add_empty_file_async(self, name: str, arcdir: str = ".") -> Self:
        return await asyncio.to_thread(self.add_empty_file, name, arcdir)

    async def add_files_async(
        self,
        files: list[Path | str | bytes],
        names: list[str] | None = None,
        arcdir: str = ".",
    ) -> Self:
        return await asyncio.to_thread(
            self.add_files, files=files, names=names, arcdir=arcdir
        )

    async def delete_file_async(self, file: str) -> Self:
        return await asyncio.to_thread(self.delete_file, file)

    async def delete_files_async(self, files: list[str]) -> Self:
        return await asyncio.to_thread(self.delete_files, files)

    async def extract_file_async(
        self, file: str, path: Path | str, flatten: bool = False
    ) -> Self:
        return await asyncio.to_thread(self.extract_file, file, path, flatten)

    async def extract_async(
        self, path: Path | str, files: list[str] | None = None
    ) -> Self:
        return await asyncio.to_thread(self.extract, path, files)

    async def to_zipfile_async(self, path: Path | str) -> None:
        return await asyncio.to_thread(self.to_zipfile, path)

    async def to_bytesio_async(self) -> BytesIO:
        return await asyncio.to_thread(self.to_bytesio)

    async def to_codezip_async(self) -> CodeZip:
        return await asyncio.to_thread(self.to_codezip)

    async def to_datazip_async(self) -> DataZip:
        return await asyncio.to_thread(self.to_datazip)

    @classmethod
    async def from_zipfile_async(cls: Type[TZip], path: Path | str) -> TZip:
        return await asyncio.to_thread(cls.from_zipfile, path)

    @classmethod
    async def from_dir_async(
        cls: Type[TZip],
        directory: Path | str,
        include_dir: bool = False,
        exclude: list[str] = ["__pycache__", ".venv"],
    ) -> TZip:
        return await asyncio.to_thread(cls.from_dir, directory, include_dir, exclude)

    @classmethod
    async def from_bytes_async(cls: Type[TZip], zip_bytes: bytes | BinaryIO) -> TZip:
        return await asyncio.to_thread(cls.from_bytes, zip_bytes)

    @classmethod
    async def from_file_async(
        cls: Type[TZip], file: Path | str, arcdir: str = "."
    ) -> TZip:
        return await asyncio.to_thread(cls.from_file, file, arcdir)

    @classmethod
    async def from_files_async(
        cls: Type[TZip],
        files: list[Path | str | bytes],
        names: list[str] | None = None,
        arcdir: str = ".",
    ) -> TZip:
        return await asyncio.to_thread(
            cls.from_files, files=files, names=names, arcdir=arcdir
        )

    @staticmethod
    async def is_valid_zip_async(zip_bytes: bytes) -> bool:
        return await asyncio.to_thread(ZipBytes.is_valid_zip, zip_bytes)

    @property
    def n_bytes(self) -> int:
        return len(self.zip_bytes)

    @property
    def n_files(self) -> int:
        return len(self.files)

    def __str__(self):
        return f"{self.__class__.__name__}(n_bytes={self.n_bytes})"


class CodeZip(ZipBytes):
    @property
    def code_id(self) -> str | None:
        if ".code_id" not in self.list_files():
            return None
        return self.read_file(".code_id").strip()

    @code_id.setter
    def code_id(self, value):
        self.add_file(file=f"{value}".encode(), name=".code_id")

    @property
    def has_dotenv(self) -> bool:
        return DOTENV_FILE in self.list_files()

    @property
    def has_requirements(self) -> bool:
        return REQUIREMENTS_TXT in self.list_files()

    @property
    def requirements(self) -> list[str] | None:
        if not self.has_requirements:
            return None
        return self.read_file(REQUIREMENTS_TXT).splitlines()

    @property
    def has_pexenv(self) -> bool:
        return PEXENV_FILE in self.list_files()

    @property
    def pexenv_bytes(self) -> bytes | None:
        if not self.has_requirements:
            return None
        return self.read_file_bytes(PEXENV_FILE)


class DataZip(ZipBytes):
    @property
    def data_id(self) -> str | None:
        if ".data_id" not in self.list_files():
            return None
        return self.read_file(".data_id").strip()

    @data_id.setter
    def data_id(self, value):
        self.add_file(file=f"{value}".encode(), name=".data_id")


class JobResult(ZipBytes):
    @property
    def job_id(self) -> str | None:
        return self.result_json.get("job_id")

    @property
    def code_id(self) -> str | None:
        return self.result_json.get("code_id")

    @property
    def stdout(self) -> str:
        return self.result_json.get("stdout") or ""

    @property
    def stderr(self) -> str:
        return self.result_json.get("stderr") or ""

    @property
    def output(self) -> str:
        return self.result_json.get("output") or ""

    @property
    def exit_code(self) -> int:
        value = self.result_json.get("exit_code")
        return int(value) if value is not None else 0

    @property
    def cmd(self) -> str:
        cmd_value = self.result_json.get("cmd")
        if isinstance(cmd_value, list):
            return " ".join(cmd_value)
        return cmd_value or ""

    @property
    def cwd(self) -> str:
        return self.result_json.get("cwd") or ""

    @property
    def exit_type(self) -> ExitType:
        exit_type_value = self.result_json.get("exit_type")
        if exit_type_value:
            return ExitType(exit_type_value)
        return ExitType.NORMAL

    @property
    def result_json(self) -> JsonData:
        if RESULT_JSON in self.list_files():
            return JsonData(data=self.read_file_bytes(RESULT_JSON))
        return JsonData()

    @property
    def n_artifacts(self) -> int:
        return len(self.list_artifacts())

    @property
    def artifacts(self) -> list[str]:
        return self.list_artifacts()

    def list_artifacts(self) -> list[str]:
        return [x for x in self.list_files() if x.startswith("artifacts/")]

    def extract_artifact(self, artifact: str, directory: str = "."):
        path = f"{directory.rstrip('/')}/{artifact.lstrip('artifacts/')}"
        self.extract_file(file=artifact, path=path)

    def extract_artifacts(self, directory: str = "."):
        for artifact in self.list_artifacts():
            self.extract_artifact(artifact=artifact, directory=directory)
