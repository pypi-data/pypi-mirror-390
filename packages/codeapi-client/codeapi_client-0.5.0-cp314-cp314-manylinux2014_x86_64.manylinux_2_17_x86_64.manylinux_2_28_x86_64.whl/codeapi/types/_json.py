import json
from io import BytesIO, IOBase
from pathlib import Path
from typing import Any, BinaryIO, OrderedDict


class JsonData(dict):
    def __init__(self, data: dict | Path | str | bytes | None = None):
        super().__init__()
        if data is None:
            pass
        elif isinstance(data, (str, bytes)):
            self.update(json.loads(data))
        elif isinstance(data, Path):
            if data.is_file():
                self.update(json.loads(data.read_text()))
            else:
                raise ValueError(f"{data} is not a file")
        elif isinstance(data, dict):
            self.update(data)
        else:
            raise TypeError("Invalid data type for JsonData")

    @property
    def json_str(self) -> str:
        return json.dumps(self)

    def dump(self) -> str:
        return self.json_str

    def print(self, indent: int = 4) -> None:
        print(json.dumps(self, indent=indent))

    def add_key(self, key: Any, value: Any, prepend: bool = False) -> None:
        new_data = OrderedDict()
        if prepend:
            new_data[key] = value
            new_data.update(self)
        else:
            new_data.update(self)
            new_data[key] = value
        self.clear()
        self.update(new_data)

    def remove_key(self, key: Any) -> None:
        self.pop(key, None)

    @classmethod
    def from_file(cls, path: Path | str) -> "JsonData":
        return cls(json.loads(Path(path).read_text()))

    @classmethod
    def from_str(cls, json_str: str) -> "JsonData":
        return cls(json_str)

    @classmethod
    def from_bytes(cls, data_bytes: bytes | BinaryIO) -> "JsonData":
        if isinstance(data_bytes, (BinaryIO, IOBase)):
            data_bytes.seek(0)
            data_bytes = data_bytes.read()
        return cls(json.loads(data_bytes))

    def to_file(self, path: Path | str) -> None:
        Path(path).write_text(json.dumps(self, indent=4))

    def to_bytesio(self) -> BytesIO:
        return BytesIO(json.dumps(self).encode())
