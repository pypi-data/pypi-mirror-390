from __future__ import annotations

from enum import Enum, auto
from typing import Type

from strenum import StrEnum


class CodeType(StrEnum):
    CLI = auto()
    APP = auto()
    MCP = auto()
    WEB = auto()
    LIB = auto()
    UNKNOWN = auto()

    def __repr__(self):
        return f"{self.__class__.__name__}.{self.name}"


class ExitType(StrEnum):
    NORMAL = auto()
    ERROR = auto()
    TIMEOUT = auto()
    TERMINATED = auto()

    def __repr__(self):
        return f"{self.__class__.__name__}.{self.name}"


class JobType(StrEnum):
    RUN_CLI = auto()
    RUN_APP = auto()
    RUN_MCP = auto()
    RUN_WEB = auto()
    INGEST = auto()
    PEXENV = auto()
    REQUIREMENTS = auto()

    @classmethod
    def from_code_type(cls, code_type: CodeType) -> JobType | None:
        """Maps CodeType to corresponding JobType for run operations.

        Args:
            code_type (CodeType): The code type to map.

        Returns:
            JobType | None: The corresponding job type, or None if no mapping exists.
        """
        mapping = {
            CodeType.CLI: cls.RUN_CLI,
            CodeType.APP: cls.RUN_APP,
            CodeType.MCP: cls.RUN_MCP,
            CodeType.WEB: cls.RUN_WEB,
            # CodeType.LIB has no corresponding run job type
        }
        return mapping.get(code_type)

    def __repr__(self):
        return f"{self.__class__.__name__}.{self.name}"


class JobStage(StrEnum):
    UNKNOWN = auto()
    PRE_RUNNING = auto()
    RUNNING = auto()
    POST_RUNNING = auto()

    def __repr__(self):
        return f"{self.__class__.__name__}.{self.name}"


class JobStatus(StrEnum):
    QUEUED = auto()
    SCHEDULED = auto()
    STARTED = auto()
    DEFERRED = auto()
    CANCELED = auto()
    STOPPED = auto()
    FAILED = auto()
    FINISHED = auto()
    TIMEOUT = auto()
    UNKNOWN = auto()

    @classmethod
    def from_rq(cls: Type[JobStatus], rq_status: Enum | None) -> JobStatus:
        if not rq_status:
            return cls.UNKNOWN
        return cls(str(rq_status.value).upper())

    @property
    def stage(self) -> JobStage:
        if self == JobStatus.UNKNOWN:
            return JobStage.UNKNOWN
        if self in [JobStatus.QUEUED, JobStatus.SCHEDULED, JobStatus.DEFERRED]:
            return JobStage.PRE_RUNNING
        if self == JobStatus.STARTED:
            return JobStage.RUNNING
        return JobStage.POST_RUNNING  # [CANCELED, STOPPED, FAILED, FINISHED, TIMEOUT]

    def __repr__(self):
        return f"{self.__class__.__name__}.{self.name}"


class HiveStatus(StrEnum):
    ALIVE = auto()
    IDLE = auto()
    BUSY = auto()
    DEAD = auto()

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            value = value.upper()
            if value in cls._value2member_map_:
                return cls._value2member_map_[value]
        return None


class WorkerDeployment(StrEnum):
    LOCAL = auto()
    HIVES = auto()

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            value = value.upper()
            if value in cls._value2member_map_:
                return cls._value2member_map_[value]
        return None

    def __repr__(self):
        return f"{self.__class__.__name__}.{self.name}"


class CodeAPIError(StrEnum):
    CODE_NOT_FOUND = auto()
    JOB_FAILED = auto()
    NO_JOB_META = auto()
    JOB_NOT_FINISHED = auto()
    JOB_NOT_FOUND = auto()
    JOB_POST_RUNNING = auto()
    JOB_STILL_QUEUED = auto()
    JOB_TIMED_OUT = auto()
    NO_ASSOCIATED_CODE_ID = auto()
    NO_STORAGE_BACKEND = auto()
    UNKNOWN = auto()

    def __repr__(self):
        return f"{self.__class__.__name__}.{self.name}"
