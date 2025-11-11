import json
from io import BytesIO, IOBase
from pathlib import Path
from typing import BinaryIO

import dotenv


class EnvVars(dict[str, str]):
    def __init__(self, env_vars: dict[str, str] | str | None = None):
        super().__init__()
        if isinstance(env_vars, str):
            self.update(json.loads(env_vars))
        elif env_vars:
            self.update(env_vars)

    def __setitem__(self, key, value) -> None:
        if not isinstance(key, str) or not isinstance(value, str):
            raise TypeError("EnvVars keys and values must be strings")
        super().__setitem__(key, value)

    @property
    def json_str(self) -> str:
        return json.dumps(self)

    def dump(self) -> str:
        return self.json_str

    def print(self) -> None:
        print("\n".join([f"{k}={v}" for k, v in self.items()]))

    @staticmethod
    def _replace_none_values(dotenv_values: dict[str, str | None]) -> dict[str, str]:
        return {k: ("" if v is None else v) for k, v in dotenv_values.items()}

    @classmethod
    def from_bytes(cls, data_bytes: bytes | BinaryIO) -> "EnvVars":
        if isinstance(data_bytes, (BinaryIO, IOBase)):
            data_bytes.seek(0)
            data_bytes = data_bytes.read()
        dotenv_values = json.loads(data_bytes)
        return cls(cls._replace_none_values(dotenv_values))

    @classmethod
    def from_str(cls, json_str: str) -> "EnvVars":
        return cls(json.loads(json_str))

    @classmethod
    def from_file(cls, path: Path | str) -> "EnvVars":
        dotenv_values = dotenv.dotenv_values(dotenv_path=path)
        return cls(cls._replace_none_values(dotenv_values))

    @classmethod
    def from_dict(cls, env_vars: dict[str, str]) -> "EnvVars":
        return cls(env_vars)

    def to_file(self, path: Path | str) -> None:
        data = [f"{k}={v}" for k, v in self.items()]
        Path(path).write_text("\n".join(data))

    def to_bytesio(self) -> BytesIO:
        return BytesIO(json.dumps(self).encode())

    def to_dict(self) -> dict[str, str]:
        return dict(self)
