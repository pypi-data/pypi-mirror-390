import qiclib.packages.grpc.datatypes_pb2 as _datatypes_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SystemInfo(_message.Message):
    __slots__ = ("version", "sampleFreq", "sampleCount", "channelCount")
    VERSION_FIELD_NUMBER: _ClassVar[int]
    SAMPLEFREQ_FIELD_NUMBER: _ClassVar[int]
    SAMPLECOUNT_FIELD_NUMBER: _ClassVar[int]
    CHANNELCOUNT_FIELD_NUMBER: _ClassVar[int]
    version: int
    sampleFreq: float
    sampleCount: int
    channelCount: int
    def __init__(self, version: _Optional[int] = ..., sampleFreq: _Optional[float] = ..., sampleCount: _Optional[int] = ..., channelCount: _Optional[int] = ...) -> None: ...

class Channel(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: int
    def __init__(self, value: _Optional[int] = ...) -> None: ...

class ChannelStatus(_message.Message):
    __slots__ = ("bufferFull", "ready", "enabled")
    BUFFERFULL_FIELD_NUMBER: _ClassVar[int]
    READY_FIELD_NUMBER: _ClassVar[int]
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    bufferFull: bool
    ready: bool
    enabled: bool
    def __init__(self, bufferFull: bool = ..., ready: bool = ..., enabled: bool = ...) -> None: ...

class ChannelWriteableStatus(_message.Message):
    __slots__ = ("channel", "enabled")
    CHANNEL_FIELD_NUMBER: _ClassVar[int]
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    channel: int
    enabled: bool
    def __init__(self, channel: _Optional[int] = ..., enabled: bool = ...) -> None: ...

class TriggerMode(_message.Message):
    __slots__ = ("channel", "enabled")
    CHANNEL_FIELD_NUMBER: _ClassVar[int]
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    channel: int
    enabled: bool
    def __init__(self, channel: _Optional[int] = ..., enabled: bool = ...) -> None: ...

class TriggerLevel(_message.Message):
    __slots__ = ("channel", "level")
    CHANNEL_FIELD_NUMBER: _ClassVar[int]
    LEVEL_FIELD_NUMBER: _ClassVar[int]
    channel: int
    level: float
    def __init__(self, channel: _Optional[int] = ..., level: _Optional[float] = ...) -> None: ...

class Flank(_message.Message):
    __slots__ = ("channel", "type")
    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        Rising: _ClassVar[Flank.Type]
        Falling: _ClassVar[Flank.Type]
        DontCare: _ClassVar[Flank.Type]
    Rising: Flank.Type
    Falling: Flank.Type
    DontCare: Flank.Type
    CHANNEL_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    channel: int
    type: Flank.Type
    def __init__(self, channel: _Optional[int] = ..., type: _Optional[_Union[Flank.Type, str]] = ...) -> None: ...

class Time(_message.Message):
    __slots__ = ("channel", "seconds")
    CHANNEL_FIELD_NUMBER: _ClassVar[int]
    SECONDS_FIELD_NUMBER: _ClassVar[int]
    channel: int
    seconds: float
    def __init__(self, channel: _Optional[int] = ..., seconds: _Optional[float] = ...) -> None: ...

class TimeScale(_message.Message):
    __slots__ = ("start", "stop")
    START_FIELD_NUMBER: _ClassVar[int]
    STOP_FIELD_NUMBER: _ClassVar[int]
    start: float
    stop: float
    def __init__(self, start: _Optional[float] = ..., stop: _Optional[float] = ...) -> None: ...

class DecimationMode(_message.Message):
    __slots__ = ("channel", "type")
    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        Average: _ClassVar[DecimationMode.Type]
        MinMax: _ClassVar[DecimationMode.Type]
    Average: DecimationMode.Type
    MinMax: DecimationMode.Type
    CHANNEL_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    channel: int
    type: DecimationMode.Type
    def __init__(self, channel: _Optional[int] = ..., type: _Optional[_Union[DecimationMode.Type, str]] = ...) -> None: ...

class ChannelData(_message.Message):
    __slots__ = ("channel", "tStart", "tStep", "values")
    CHANNEL_FIELD_NUMBER: _ClassVar[int]
    TSTART_FIELD_NUMBER: _ClassVar[int]
    TSTEP_FIELD_NUMBER: _ClassVar[int]
    VALUES_FIELD_NUMBER: _ClassVar[int]
    channel: int
    tStart: float
    tStep: float
    values: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, channel: _Optional[int] = ..., tStart: _Optional[float] = ..., tStep: _Optional[float] = ..., values: _Optional[_Iterable[float]] = ...) -> None: ...

class OscilloscopeData(_message.Message):
    __slots__ = ("channels",)
    CHANNELS_FIELD_NUMBER: _ClassVar[int]
    channels: _containers.RepeatedCompositeFieldContainer[ChannelData]
    def __init__(self, channels: _Optional[_Iterable[_Union[ChannelData, _Mapping]]] = ...) -> None: ...
