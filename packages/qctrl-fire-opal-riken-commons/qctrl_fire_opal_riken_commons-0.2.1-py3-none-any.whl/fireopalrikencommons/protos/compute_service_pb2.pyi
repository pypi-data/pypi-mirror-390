from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class PreprocessingRequest(_message.Message):
    __slots__ = ("task_id", "backend_configuration", "backend_properties", "pubs", "run_options")
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    BACKEND_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    BACKEND_PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    PUBS_FIELD_NUMBER: _ClassVar[int]
    RUN_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    task_id: str
    backend_configuration: str
    backend_properties: str
    pubs: str
    run_options: str
    def __init__(self, task_id: _Optional[str] = ..., backend_configuration: _Optional[str] = ..., backend_properties: _Optional[str] = ..., pubs: _Optional[str] = ..., run_options: _Optional[str] = ...) -> None: ...

class PreprocessingResponse(_message.Message):
    __slots__ = ("task_id", "success", "pubs", "error_message")
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    PUBS_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    task_id: str
    success: bool
    pubs: str
    error_message: str
    def __init__(self, task_id: _Optional[str] = ..., success: bool = ..., pubs: _Optional[str] = ..., error_message: _Optional[str] = ...) -> None: ...

class PostprocessingRequest(_message.Message):
    __slots__ = ("task_id", "pub_results", "pubs_original", "pubs_submitted")
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    PUB_RESULTS_FIELD_NUMBER: _ClassVar[int]
    PUBS_ORIGINAL_FIELD_NUMBER: _ClassVar[int]
    PUBS_SUBMITTED_FIELD_NUMBER: _ClassVar[int]
    task_id: str
    pub_results: str
    pubs_original: str
    pubs_submitted: str
    def __init__(self, task_id: _Optional[str] = ..., pub_results: _Optional[str] = ..., pubs_original: _Optional[str] = ..., pubs_submitted: _Optional[str] = ...) -> None: ...

class PostprocessingResponse(_message.Message):
    __slots__ = ("task_id", "success", "results", "error_message")
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    task_id: str
    success: bool
    results: str
    error_message: str
    def __init__(self, task_id: _Optional[str] = ..., success: bool = ..., results: _Optional[str] = ..., error_message: _Optional[str] = ...) -> None: ...

class HealthRequest(_message.Message):
    __slots__ = ("service",)
    SERVICE_FIELD_NUMBER: _ClassVar[int]
    service: str
    def __init__(self, service: _Optional[str] = ...) -> None: ...

class HealthResponse(_message.Message):
    __slots__ = ("status", "active_workers", "queue_size", "uptime_seconds")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_WORKERS_FIELD_NUMBER: _ClassVar[int]
    QUEUE_SIZE_FIELD_NUMBER: _ClassVar[int]
    UPTIME_SECONDS_FIELD_NUMBER: _ClassVar[int]
    status: str
    active_workers: int
    queue_size: int
    uptime_seconds: float
    def __init__(self, status: _Optional[str] = ..., active_workers: _Optional[int] = ..., queue_size: _Optional[int] = ..., uptime_seconds: _Optional[float] = ...) -> None: ...
