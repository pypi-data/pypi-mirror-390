from pydantic import BaseModel

API_KEY_HEADER = "CodeAPI-Key"


class TokenRequest(BaseModel):
    user: str
    ulid: str | None = None
    ttl: int = -1  # [s]


class TokenResponse(BaseModel):
    token: str


class ServerStatus(BaseModel):
    is_healthy: bool


class ServicesHealth(BaseModel):
    redis_healthy: bool
    storage_healthy: bool

    @property
    def all_healthy(self) -> bool:
        return all(
            getattr(self, attr)
            for attr in self.__dict__
            if isinstance(getattr(self, attr), bool)
        )
