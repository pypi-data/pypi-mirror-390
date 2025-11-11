from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, field_validator


class StreamOutput(BaseModel):
    sid: str
    stream: Literal["stdout", "stderr"]
    text: str

    @property
    def timestamp(self) -> float:
        return int(self.sid.split("-")[0]) / 1000

    @property
    def datetime(self) -> datetime:
        return datetime.fromtimestamp(self.timestamp)

    @property
    def seq_number(self) -> int:
        return int(self.sid.split("-")[1])

    @field_validator("stream", "text", mode="before")
    @classmethod
    def decode_bytes(cls, v: Any) -> str:
        if isinstance(v, bytes):
            return v.decode()
        return v

    def __str__(self):
        fields = self.__class__.__pydantic_fields__
        field_values = ", ".join(
            f"{k}={repr(v)}" for k, v in self.model_dump().items() if fields[k].repr
        )
        return f"{self.__class__.__name__}({field_values})"
