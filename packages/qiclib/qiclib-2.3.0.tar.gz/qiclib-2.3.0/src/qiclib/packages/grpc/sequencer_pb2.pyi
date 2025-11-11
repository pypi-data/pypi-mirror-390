import qiclib.packages.grpc.datatypes_pb2 as _datatypes_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Average(_message.Message):
    __slots__ = ("index", "value")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    index: _datatypes_pb2.EndpointIndex
    value: int
    def __init__(self, index: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ..., value: _Optional[int] = ...) -> None: ...

class RegisterIndex(_message.Message):
    __slots__ = ("endpoint", "index")
    ENDPOINT_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    endpoint: _datatypes_pb2.EndpointIndex
    index: int
    def __init__(self, endpoint: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ..., index: _Optional[int] = ...) -> None: ...

class Register(_message.Message):
    __slots__ = ("index", "value")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    index: RegisterIndex
    value: int
    def __init__(self, index: _Optional[_Union[RegisterIndex, _Mapping]] = ..., value: _Optional[int] = ...) -> None: ...

class RegisterList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, list: _Optional[_Iterable[int]] = ...) -> None: ...

class ProgramCounter(_message.Message):
    __slots__ = ("index", "value")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    index: _datatypes_pb2.EndpointIndex
    value: int
    def __init__(self, index: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ..., value: _Optional[int] = ...) -> None: ...

class Delay(_message.Message):
    __slots__ = ("index", "reg", "time", "cycles")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    REG_FIELD_NUMBER: _ClassVar[int]
    TIME_FIELD_NUMBER: _ClassVar[int]
    CYCLES_FIELD_NUMBER: _ClassVar[int]
    index: _datatypes_pb2.EndpointIndex
    reg: int
    time: float
    cycles: int
    def __init__(self, index: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ..., reg: _Optional[int] = ..., time: _Optional[float] = ..., cycles: _Optional[int] = ...) -> None: ...

class Program(_message.Message):
    __slots__ = ("index", "program_data", "description")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    PROGRAM_DATA_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    index: _datatypes_pb2.EndpointIndex
    program_data: _containers.RepeatedScalarFieldContainer[int]
    description: str
    def __init__(self, index: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ..., program_data: _Optional[_Iterable[int]] = ..., description: _Optional[str] = ...) -> None: ...

class StatusReport(_message.Message):
    __slots__ = ("busy", "relaxed", "wait_on_sync", "error", "warnings")
    BUSY_FIELD_NUMBER: _ClassVar[int]
    RELAXED_FIELD_NUMBER: _ClassVar[int]
    WAIT_ON_SYNC_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    WARNINGS_FIELD_NUMBER: _ClassVar[int]
    busy: bool
    relaxed: bool
    wait_on_sync: bool
    error: str
    warnings: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, busy: bool = ..., relaxed: bool = ..., wait_on_sync: bool = ..., error: _Optional[str] = ..., warnings: _Optional[_Iterable[str]] = ...) -> None: ...
