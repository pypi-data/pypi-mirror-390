import qiclib.packages.grpc.datatypes_pb2 as _datatypes_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ToneSpecs(_message.Message):
    __slots__ = ("frequency", "amplitude", "phase", "phaseIQI", "amplitudeIQI")
    FREQUENCY_FIELD_NUMBER: _ClassVar[int]
    AMPLITUDE_FIELD_NUMBER: _ClassVar[int]
    PHASE_FIELD_NUMBER: _ClassVar[int]
    PHASEIQI_FIELD_NUMBER: _ClassVar[int]
    AMPLITUDEIQI_FIELD_NUMBER: _ClassVar[int]
    frequency: float
    amplitude: float
    phase: float
    phaseIQI: float
    amplitudeIQI: float
    def __init__(self, frequency: _Optional[float] = ..., amplitude: _Optional[float] = ..., phase: _Optional[float] = ..., phaseIQI: _Optional[float] = ..., amplitudeIQI: _Optional[float] = ...) -> None: ...

class IndexedToneSpecs(_message.Message):
    __slots__ = ("index", "specs")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    SPECS_FIELD_NUMBER: _ClassVar[int]
    index: _datatypes_pb2.EndpointIndex
    specs: ToneSpecs
    def __init__(self, index: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ..., specs: _Optional[_Union[ToneSpecs, _Mapping]] = ...) -> None: ...

class IndexedToneSpecsVector(_message.Message):
    __slots__ = ("index", "specs")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    SPECS_FIELD_NUMBER: _ClassVar[int]
    index: _datatypes_pb2.EndpointIndex
    specs: _containers.RepeatedCompositeFieldContainer[ToneSpecs]
    def __init__(self, index: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ..., specs: _Optional[_Iterable[_Union[ToneSpecs, _Mapping]]] = ...) -> None: ...

class RawData(_message.Message):
    __slots__ = ("index", "value", "adjustPlaybackInterval")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    ADJUSTPLAYBACKINTERVAL_FIELD_NUMBER: _ClassVar[int]
    index: _datatypes_pb2.EndpointIndex
    value: _containers.RepeatedScalarFieldContainer[float]
    adjustPlaybackInterval: bool
    def __init__(self, index: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ..., value: _Optional[_Iterable[float]] = ..., adjustPlaybackInterval: bool = ...) -> None: ...

class Interval(_message.Message):
    __slots__ = ("index", "start", "end")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    START_FIELD_NUMBER: _ClassVar[int]
    END_FIELD_NUMBER: _ClassVar[int]
    index: _datatypes_pb2.EndpointIndex
    start: float
    end: float
    def __init__(self, index: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ..., start: _Optional[float] = ..., end: _Optional[float] = ...) -> None: ...

class Modulation(_message.Message):
    __slots__ = ("index", "frequency", "amplitude", "offset", "phase")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    FREQUENCY_FIELD_NUMBER: _ClassVar[int]
    AMPLITUDE_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    PHASE_FIELD_NUMBER: _ClassVar[int]
    index: _datatypes_pb2.EndpointIndex
    frequency: float
    amplitude: float
    offset: float
    phase: float
    def __init__(self, index: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ..., frequency: _Optional[float] = ..., amplitude: _Optional[float] = ..., offset: _Optional[float] = ..., phase: _Optional[float] = ...) -> None: ...

class DoubleArray(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, value: _Optional[_Iterable[float]] = ...) -> None: ...
