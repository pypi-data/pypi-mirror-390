from pydantic import BaseModel
from strenum import StrEnum


class CustomBaseModel(BaseModel):
    def __str__(self):
        fields = self.__class__.__pydantic_fields__
        field_values = ", ".join(
            f"{k}={repr(v)}" for k, v in self.model_dump().items() if fields[k].repr
        )
        return f"{self.__class__.__name__}({field_values})"


class CaseInsensitiveStrEnum(StrEnum):
    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            value = value.upper()
            if value in cls._value2member_map_:
                return cls._value2member_map_[value]
        return None
