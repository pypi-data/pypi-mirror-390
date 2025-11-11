import qiclib.packages.grpc.datatypes_pb2 as _datatypes_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TriggerSetIndex(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: int
    def __init__(self, value: _Optional[int] = ...) -> None: ...

class IndexSet(_message.Message):
    __slots__ = ("cindex", "tindex")
    CINDEX_FIELD_NUMBER: _ClassVar[int]
    TINDEX_FIELD_NUMBER: _ClassVar[int]
    cindex: _datatypes_pb2.EndpointIndex
    tindex: TriggerSetIndex
    def __init__(self, cindex: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ..., tindex: _Optional[_Union[TriggerSetIndex, _Mapping]] = ...) -> None: ...

class Frequency(_message.Message):
    __slots__ = ("cindex", "value")
    CINDEX_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    cindex: _datatypes_pb2.EndpointIndex
    value: float
    def __init__(self, cindex: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ..., value: _Optional[float] = ...) -> None: ...

class AmplitudeCalibration(_message.Message):
    __slots__ = ("cindex", "i_factor", "q_factor")
    CINDEX_FIELD_NUMBER: _ClassVar[int]
    I_FACTOR_FIELD_NUMBER: _ClassVar[int]
    Q_FACTOR_FIELD_NUMBER: _ClassVar[int]
    cindex: _datatypes_pb2.EndpointIndex
    i_factor: float
    q_factor: float
    def __init__(self, cindex: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ..., i_factor: _Optional[float] = ..., q_factor: _Optional[float] = ...) -> None: ...

class PhaseOffset(_message.Message):
    __slots__ = ("index", "value")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    index: IndexSet
    value: float
    def __init__(self, index: _Optional[_Union[IndexSet, _Mapping]] = ..., value: _Optional[float] = ...) -> None: ...

class Duration(_message.Message):
    __slots__ = ("index", "value")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    index: IndexSet
    value: float
    def __init__(self, index: _Optional[_Union[IndexSet, _Mapping]] = ..., value: _Optional[float] = ...) -> None: ...

class Address(_message.Message):
    __slots__ = ("index", "value")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    index: IndexSet
    value: int
    def __init__(self, index: _Optional[_Union[IndexSet, _Mapping]] = ..., value: _Optional[int] = ...) -> None: ...

class Pulse(_message.Message):
    __slots__ = ("index", "i", "q", "phase", "offset", "hold", "shift_phase")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    I_FIELD_NUMBER: _ClassVar[int]
    Q_FIELD_NUMBER: _ClassVar[int]
    PHASE_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    HOLD_FIELD_NUMBER: _ClassVar[int]
    SHIFT_PHASE_FIELD_NUMBER: _ClassVar[int]
    index: IndexSet
    i: _containers.RepeatedScalarFieldContainer[float]
    q: _containers.RepeatedScalarFieldContainer[float]
    phase: float
    offset: float
    hold: bool
    shift_phase: bool
    def __init__(self, index: _Optional[_Union[IndexSet, _Mapping]] = ..., i: _Optional[_Iterable[float]] = ..., q: _Optional[_Iterable[float]] = ..., phase: _Optional[float] = ..., offset: _Optional[float] = ..., hold: bool = ..., shift_phase: bool = ...) -> None: ...

class StatusFlags(_message.Message):
    __slots__ = ("cindex", "saturation")
    CINDEX_FIELD_NUMBER: _ClassVar[int]
    SATURATION_FIELD_NUMBER: _ClassVar[int]
    cindex: _datatypes_pb2.EndpointIndex
    saturation: bool
    def __init__(self, cindex: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ..., saturation: bool = ...) -> None: ...
