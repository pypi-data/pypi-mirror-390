import qiclib.packages.grpc.datatypes_pb2 as _datatypes_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ChannelInfo(_message.Message):
    __slots__ = ("enabled", "type", "mode")
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    enabled: bool
    type: Channel.Type
    mode: HoldMode.Mode
    def __init__(self, enabled: bool = ..., type: _Optional[_Union[Channel.Type, str]] = ..., mode: _Optional[_Union[HoldMode.Mode, str]] = ...) -> None: ...

class Channel(_message.Message):
    __slots__ = ("number", "type")
    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SINGLE: _ClassVar[Channel.Type]
        DUAL: _ClassVar[Channel.Type]
    SINGLE: Channel.Type
    DUAL: Channel.Type
    NUMBER_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    number: int
    type: Channel.Type
    def __init__(self, number: _Optional[int] = ..., type: _Optional[_Union[Channel.Type, str]] = ...) -> None: ...

class BufferData(_message.Message):
    __slots__ = ("magnitude", "channel_index", "channel_sub_index")
    MAGNITUDE_FIELD_NUMBER: _ClassVar[int]
    CHANNEL_INDEX_FIELD_NUMBER: _ClassVar[int]
    CHANNEL_SUB_INDEX_FIELD_NUMBER: _ClassVar[int]
    magnitude: _containers.RepeatedScalarFieldContainer[float]
    channel_index: int
    channel_sub_index: int
    def __init__(self, magnitude: _Optional[_Iterable[float]] = ..., channel_index: _Optional[int] = ..., channel_sub_index: _Optional[int] = ...) -> None: ...

class SamplingFrequency(_message.Message):
    __slots__ = ("hertz",)
    HERTZ_FIELD_NUMBER: _ClassVar[int]
    hertz: float
    def __init__(self, hertz: _Optional[float] = ...) -> None: ...

class HoldMode(_message.Message):
    __slots__ = ("mode", "alpha", "has_alpha")
    class Mode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        NONE: _ClassVar[HoldMode.Mode]
        EMA: _ClassVar[HoldMode.Mode]
        MAX_HOLD: _ClassVar[HoldMode.Mode]
    NONE: HoldMode.Mode
    EMA: HoldMode.Mode
    MAX_HOLD: HoldMode.Mode
    MODE_FIELD_NUMBER: _ClassVar[int]
    ALPHA_FIELD_NUMBER: _ClassVar[int]
    HAS_ALPHA_FIELD_NUMBER: _ClassVar[int]
    mode: HoldMode.Mode
    alpha: float
    has_alpha: bool
    def __init__(self, mode: _Optional[_Union[HoldMode.Mode, str]] = ..., alpha: _Optional[float] = ..., has_alpha: bool = ...) -> None: ...

class ChanneledHoldMode(_message.Message):
    __slots__ = ("channel", "hold_mode")
    CHANNEL_FIELD_NUMBER: _ClassVar[int]
    HOLD_MODE_FIELD_NUMBER: _ClassVar[int]
    channel: Channel
    hold_mode: HoldMode
    def __init__(self, channel: _Optional[_Union[Channel, _Mapping]] = ..., hold_mode: _Optional[_Union[HoldMode, _Mapping]] = ...) -> None: ...
