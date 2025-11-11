from fastapi import HTTPException

from ._enums import CodeAPIError


class CodeAPIException(HTTPException):
    def __init__(self, error: CodeAPIError, message: str = ""):
        self.error: CodeAPIError = error
        self.message: str = message

        status_code = self._get_status_code()
        detail = {"error": self.error.name, "message": message}
        super().__init__(status_code=status_code, detail=detail)

    def _get_status_code(self) -> int:
        if self.error == CodeAPIError.CODE_NOT_FOUND:
            return 404
        elif self.error == CodeAPIError.JOB_FAILED:
            return 500
        elif self.error == CodeAPIError.JOB_NOT_FINISHED:
            return 400
        elif self.error == CodeAPIError.JOB_NOT_FOUND:
            return 404
        elif self.error == CodeAPIError.JOB_STILL_QUEUED:
            return 503
        elif self.error == CodeAPIError.JOB_TIMED_OUT:
            return 408
        elif self.error == CodeAPIError.NO_ASSOCIATED_CODE_ID:
            return 404
        elif self.error == CodeAPIError.NO_JOB_META:
            return 404
        elif self.error == CodeAPIError.NO_STORAGE_BACKEND:
            return 501
        else:
            return 500
