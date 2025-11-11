import qiclib.packages.grpc.datatypes_pb2 as _datatypes_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class StatusReply(_message.Message):
    __slots__ = ("chip_id", "firmware_hash", "build_date", "build_commit", "task_name", "task_state", "task_progress", "databoxes_available")
    CHIP_ID_FIELD_NUMBER: _ClassVar[int]
    FIRMWARE_HASH_FIELD_NUMBER: _ClassVar[int]
    BUILD_DATE_FIELD_NUMBER: _ClassVar[int]
    BUILD_COMMIT_FIELD_NUMBER: _ClassVar[int]
    TASK_NAME_FIELD_NUMBER: _ClassVar[int]
    TASK_STATE_FIELD_NUMBER: _ClassVar[int]
    TASK_PROGRESS_FIELD_NUMBER: _ClassVar[int]
    DATABOXES_AVAILABLE_FIELD_NUMBER: _ClassVar[int]
    chip_id: int
    firmware_hash: str
    build_date: str
    build_commit: str
    task_name: str
    task_state: int
    task_progress: int
    databoxes_available: int
    def __init__(self, chip_id: _Optional[int] = ..., firmware_hash: _Optional[str] = ..., build_date: _Optional[str] = ..., build_commit: _Optional[str] = ..., task_name: _Optional[str] = ..., task_state: _Optional[int] = ..., task_progress: _Optional[int] = ..., databoxes_available: _Optional[int] = ...) -> None: ...

class TaskStateReply(_message.Message):
    __slots__ = ("busy", "done", "loaded", "looping", "error_msg_available", "error_msg_queue_full")
    BUSY_FIELD_NUMBER: _ClassVar[int]
    DONE_FIELD_NUMBER: _ClassVar[int]
    LOADED_FIELD_NUMBER: _ClassVar[int]
    LOOPING_FIELD_NUMBER: _ClassVar[int]
    ERROR_MSG_AVAILABLE_FIELD_NUMBER: _ClassVar[int]
    ERROR_MSG_QUEUE_FULL_FIELD_NUMBER: _ClassVar[int]
    busy: bool
    done: bool
    loaded: bool
    looping: bool
    error_msg_available: bool
    error_msg_queue_full: bool
    def __init__(self, busy: bool = ..., done: bool = ..., loaded: bool = ..., looping: bool = ..., error_msg_available: bool = ..., error_msg_queue_full: bool = ...) -> None: ...

class DataboxReplyINT32(_message.Message):
    __slots__ = ("index", "data")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    index: int
    data: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, index: _Optional[int] = ..., data: _Optional[_Iterable[int]] = ...) -> None: ...

class DataboxReplyUINT32(_message.Message):
    __slots__ = ("index", "data")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    index: int
    data: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, index: _Optional[int] = ..., data: _Optional[_Iterable[int]] = ...) -> None: ...

class DataboxReplyINT64(_message.Message):
    __slots__ = ("index", "data")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    index: int
    data: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, index: _Optional[int] = ..., data: _Optional[_Iterable[int]] = ...) -> None: ...

class DataboxReplyUINT64(_message.Message):
    __slots__ = ("index", "data")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    index: int
    data: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, index: _Optional[int] = ..., data: _Optional[_Iterable[int]] = ...) -> None: ...

class GetTaskErrorMessagesReply(_message.Message):
    __slots__ = ("message",)
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, message: _Optional[_Iterable[str]] = ...) -> None: ...

class ParameterRequest(_message.Message):
    __slots__ = ("parameters",)
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    parameters: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, parameters: _Optional[_Iterable[int]] = ...) -> None: ...

class StartTaskRequest(_message.Message):
    __slots__ = ("looping", "stop_running")
    LOOPING_FIELD_NUMBER: _ClassVar[int]
    STOP_RUNNING_FIELD_NUMBER: _ClassVar[int]
    looping: bool
    stop_running: bool
    def __init__(self, looping: bool = ..., stop_running: bool = ...) -> None: ...

class StopTaskRequest(_message.Message):
    __slots__ = ("reset",)
    RESET_FIELD_NUMBER: _ClassVar[int]
    reset: bool
    def __init__(self, reset: bool = ...) -> None: ...

class ProgramTaskRequest(_message.Message):
    __slots__ = ("name", "task")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TASK_FIELD_NUMBER: _ClassVar[int]
    name: str
    task: bytes
    def __init__(self, name: _Optional[str] = ..., task: _Optional[bytes] = ...) -> None: ...
