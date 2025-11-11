from pydantic import BaseModel, ConfigDict, field_serializer, field_validator

from ._enums import CodeType
from ._json import JsonData


class CodeInfo(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    code_id: str
    code_name: str
    code_type: CodeType
    metadata: JsonData

    @field_serializer("metadata")
    def serialize_metadata(self, value: JsonData) -> dict:
        return dict(value)

    @field_validator("metadata", mode="before")
    @classmethod
    def deserialize_metadata(cls, value: JsonData | dict) -> JsonData:
        if isinstance(value, JsonData):
            return value
        return JsonData(value)

    def __str__(self):
        fields = self.__class__.__pydantic_fields__
        field_values = ", ".join(
            f"{k}={repr(v)}" for k, v in self.model_dump().items() if fields[k].repr
        )
        return f"{self.__class__.__name__}({field_values})"
