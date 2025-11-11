import qiclib.packages.grpc.datatypes_pb2 as _datatypes_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class OutputLevel(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ACTIVE_LOW: _ClassVar[OutputLevel]
    ACTIVE_HIGH: _ClassVar[OutputLevel]
ACTIVE_LOW: OutputLevel
ACTIVE_HIGH: OutputLevel

class TriggerIndex(_message.Message):
    __slots__ = ("index", "trigger")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    TRIGGER_FIELD_NUMBER: _ClassVar[int]
    index: _datatypes_pb2.EndpointIndex
    trigger: int
    def __init__(self, index: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ..., trigger: _Optional[int] = ...) -> None: ...

class OutputIndex(_message.Message):
    __slots__ = ("index", "output")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_FIELD_NUMBER: _ClassVar[int]
    index: _datatypes_pb2.EndpointIndex
    output: int
    def __init__(self, index: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ..., output: _Optional[int] = ...) -> None: ...

class TriggerSet(_message.Message):
    __slots__ = ("continuous", "duration_cycles", "output_select")
    CONTINUOUS_FIELD_NUMBER: _ClassVar[int]
    DURATION_CYCLES_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_SELECT_FIELD_NUMBER: _ClassVar[int]
    continuous: bool
    duration_cycles: int
    output_select: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, continuous: bool = ..., duration_cycles: _Optional[int] = ..., output_select: _Optional[_Iterable[int]] = ...) -> None: ...

class IndexedTriggerSet(_message.Message):
    __slots__ = ("index", "set")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    SET_FIELD_NUMBER: _ClassVar[int]
    index: TriggerIndex
    set: TriggerSet
    def __init__(self, index: _Optional[_Union[TriggerIndex, _Mapping]] = ..., set: _Optional[_Union[TriggerSet, _Mapping]] = ...) -> None: ...

class OutputConfig(_message.Message):
    __slots__ = ("level", "duration_cycles")
    LEVEL_FIELD_NUMBER: _ClassVar[int]
    DURATION_CYCLES_FIELD_NUMBER: _ClassVar[int]
    level: OutputLevel
    duration_cycles: int
    def __init__(self, level: _Optional[_Union[OutputLevel, str]] = ..., duration_cycles: _Optional[int] = ...) -> None: ...

class IndexedOutputConfig(_message.Message):
    __slots__ = ("index", "config")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    index: OutputIndex
    config: OutputConfig
    def __init__(self, index: _Optional[_Union[OutputIndex, _Mapping]] = ..., config: _Optional[_Union[OutputConfig, _Mapping]] = ...) -> None: ...
