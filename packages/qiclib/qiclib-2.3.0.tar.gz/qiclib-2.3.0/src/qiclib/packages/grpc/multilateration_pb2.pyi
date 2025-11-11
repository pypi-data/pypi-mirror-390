import qiclib.packages.grpc.datatypes_pb2 as _datatypes_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class StatusFlags(_message.Message):
    __slots__ = ("data_available", "saving")
    DATA_AVAILABLE_FIELD_NUMBER: _ClassVar[int]
    SAVING_FIELD_NUMBER: _ClassVar[int]
    data_available: bool
    saving: bool
    def __init__(self, data_available: bool = ..., saving: bool = ...) -> None: ...

class AllCounters(_message.Message):
    __slots__ = ("values",)
    VALUES_FIELD_NUMBER: _ClassVar[int]
    values: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, values: _Optional[_Iterable[int]] = ...) -> None: ...

class CondMatrix(_message.Message):
    __slots__ = ("index", "ii", "iq", "qi", "qq")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    II_FIELD_NUMBER: _ClassVar[int]
    IQ_FIELD_NUMBER: _ClassVar[int]
    QI_FIELD_NUMBER: _ClassVar[int]
    QQ_FIELD_NUMBER: _ClassVar[int]
    index: _datatypes_pb2.EndpointIndex
    ii: float
    iq: float
    qi: float
    qq: float
    def __init__(self, index: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ..., ii: _Optional[float] = ..., iq: _Optional[float] = ..., qi: _Optional[float] = ..., qq: _Optional[float] = ...) -> None: ...

class CondOffset(_message.Message):
    __slots__ = ("index", "i", "q")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    I_FIELD_NUMBER: _ClassVar[int]
    Q_FIELD_NUMBER: _ClassVar[int]
    index: _datatypes_pb2.EndpointIndex
    i: int
    q: int
    def __init__(self, index: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ..., i: _Optional[int] = ..., q: _Optional[int] = ...) -> None: ...

class Timetrace(_message.Message):
    __slots__ = ("i", "q")
    I_FIELD_NUMBER: _ClassVar[int]
    Q_FIELD_NUMBER: _ClassVar[int]
    i: _containers.RepeatedScalarFieldContainer[int]
    q: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, i: _Optional[_Iterable[int]] = ..., q: _Optional[_Iterable[int]] = ...) -> None: ...
