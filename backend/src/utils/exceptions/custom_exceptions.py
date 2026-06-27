class ApplicationException(Exception):
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class AgentException(ApplicationException):
    def __init__(self, detail: str = "Agent failed to process the request."):
        super().__init__(message=detail, status_code=500)


class OrchestrationException(ApplicationException):
    def __init__(self, detail: str = "Workflow orchestration failed."):
        super().__init__(message=detail, status_code=500)


class InvalidRequestException(ApplicationException):
    def __init__(self, detail: str = "Invalid request."):
        super().__init__(message=detail, status_code=400)


class ResourceNotFoundException(ApplicationException):
    def __init__(self, detail: str = "Requested resource not found."):
        super().__init__(message=detail, status_code=404)


class DatabaseException(ApplicationException):
    def __init__(self, detail: str = "A database error occurred."):
        super().__init__(message=detail, status_code=500)


class ExternalServiceException(ApplicationException):
    def __init__(self, detail: str = "External service error occurred."):
        super().__init__(message=detail, status_code=502)
