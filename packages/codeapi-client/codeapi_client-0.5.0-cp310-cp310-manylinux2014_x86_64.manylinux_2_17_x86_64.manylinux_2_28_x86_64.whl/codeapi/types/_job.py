from pydantic import BaseModel, Field

from ._enums import JobStage, JobStatus, JobType


class Job(BaseModel):
    job_id: str
    job_type: JobType
    job_status: JobStatus
    job_error: str | None = Field(default=None)
    job_traceback: str | None = Field(default=None, repr=False)
    code_id: str | None = None

    @property
    def job_stage(self) -> JobStage:
        return self.job_status.stage

    @property
    def is_queued(self) -> bool:
        return self.job_stage == JobStatus.QUEUED

    @property
    def is_scheduled(self) -> bool:
        return self.job_stage == JobStatus.SCHEDULED

    @property
    def is_pre_running(self) -> bool:
        return self.job_stage == JobStage.PRE_RUNNING

    @property
    def is_running(self) -> bool:
        return self.job_stage == JobStage.RUNNING

    @property
    def is_post_running(self) -> bool:
        return self.job_stage == JobStage.POST_RUNNING

    @property
    def has_finished(self) -> bool:
        return self.job_status == JobStatus.FINISHED

    @property
    def has_failed(self) -> bool:
        return self.is_post_running and not self.has_finished

    @property
    def has_timed_out(self) -> bool:
        return self.job_status == JobStatus.TIMEOUT

    @property
    def has_been_stopped(self) -> bool:
        return self.job_status == JobStatus.STOPPED

    @property
    def has_been_canceled(self) -> bool:
        return self.job_status == JobStatus.CANCELED

    @property
    def has_been_deferred(self) -> bool:
        return self.job_status == JobStatus.DEFERRED

    def __str__(self):
        fields = self.__class__.__pydantic_fields__
        field_values = ", ".join(
            f"{k}={repr(v)}" for k, v in self.model_dump().items() if fields[k].repr
        )
        return f"{self.__class__.__name__}({field_values})"
