import qiclib.packages.grpc.datatypes_pb2 as _datatypes_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Window(_message.Message):
    __slots__ = ("name", "length", "offset", "param")
    NAME_FIELD_NUMBER: _ClassVar[int]
    LENGTH_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    PARAM_FIELD_NUMBER: _ClassVar[int]
    name: str
    length: int
    offset: int
    param: float
    def __init__(self, name: _Optional[str] = ..., length: _Optional[int] = ..., offset: _Optional[int] = ..., param: _Optional[float] = ...) -> None: ...

class WindowRequest(_message.Message):
    __slots__ = ("index", "properties")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    index: _datatypes_pb2.EndpointIndex
    properties: Window
    def __init__(self, index: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ..., properties: _Optional[_Union[Window, _Mapping]] = ...) -> None: ...

class Unsigned32Array(_message.Message):
    __slots__ = ("index", "value")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    index: _datatypes_pb2.EndpointIndex
    value: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, index: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ..., value: _Optional[_Iterable[int]] = ...) -> None: ...

class Signed32Array(_message.Message):
    __slots__ = ("index", "value")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    index: _datatypes_pb2.EndpointIndex
    value: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, index: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ..., value: _Optional[_Iterable[int]] = ...) -> None: ...

class NCOData(_message.Message):
    __slots__ = ("index", "frequencies", "phases", "offsets")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    FREQUENCIES_FIELD_NUMBER: _ClassVar[int]
    PHASES_FIELD_NUMBER: _ClassVar[int]
    OFFSETS_FIELD_NUMBER: _ClassVar[int]
    index: _datatypes_pb2.EndpointIndex
    frequencies: _containers.RepeatedScalarFieldContainer[float]
    phases: _containers.RepeatedScalarFieldContainer[float]
    offsets: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, index: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ..., frequencies: _Optional[_Iterable[float]] = ..., phases: _Optional[_Iterable[float]] = ..., offsets: _Optional[_Iterable[int]] = ...) -> None: ...

class DoubleArray(_message.Message):
    __slots__ = ("index", "value")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    index: _datatypes_pb2.EndpointIndex
    value: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, index: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ..., value: _Optional[_Iterable[float]] = ...) -> None: ...

class ChannelData(_message.Message):
    __slots__ = ("index", "channel", "value")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    CHANNEL_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    index: _datatypes_pb2.EndpointIndex
    channel: int
    value: int
    def __init__(self, index: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ..., channel: _Optional[int] = ..., value: _Optional[int] = ...) -> None: ...

class ChannelDouble(_message.Message):
    __slots__ = ("index", "channel", "value")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    CHANNEL_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    index: _datatypes_pb2.EndpointIndex
    channel: int
    value: float
    def __init__(self, index: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ..., channel: _Optional[int] = ..., value: _Optional[float] = ...) -> None: ...

class RampGenData(_message.Message):
    __slots__ = ("index", "rampperiodecycles", "rampsamplerate")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    RAMPPERIODECYCLES_FIELD_NUMBER: _ClassVar[int]
    RAMPSAMPLERATE_FIELD_NUMBER: _ClassVar[int]
    index: _datatypes_pb2.EndpointIndex
    rampperiodecycles: int
    rampsamplerate: float
    def __init__(self, index: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ..., rampperiodecycles: _Optional[int] = ..., rampsamplerate: _Optional[float] = ...) -> None: ...

class StartAndEnd(_message.Message):
    __slots__ = ("index", "start", "end")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    START_FIELD_NUMBER: _ClassVar[int]
    END_FIELD_NUMBER: _ClassVar[int]
    index: _datatypes_pb2.EndpointIndex
    start: int
    end: int
    def __init__(self, index: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ..., start: _Optional[int] = ..., end: _Optional[int] = ...) -> None: ...
