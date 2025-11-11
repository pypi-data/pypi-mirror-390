import qiclib.packages.grpc.datatypes_pb2 as _datatypes_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TriggerEngine(_message.Message):
    __slots__ = ("index", "value")
    class TriggerType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        THRESHOLD: _ClassVar[TriggerEngine.TriggerType]
        MOVING_AVERAGE: _ClassVar[TriggerEngine.TriggerType]
    THRESHOLD: TriggerEngine.TriggerType
    MOVING_AVERAGE: TriggerEngine.TriggerType
    INDEX_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    index: _datatypes_pb2.EndpointIndex
    value: TriggerEngine.TriggerType
    def __init__(self, index: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ..., value: _Optional[_Union[TriggerEngine.TriggerType, str]] = ...) -> None: ...

class Statistics(_message.Message):
    __slots__ = ("index", "discardedEvents", "storedEvents")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    DISCARDEDEVENTS_FIELD_NUMBER: _ClassVar[int]
    STOREDEVENTS_FIELD_NUMBER: _ClassVar[int]
    index: _datatypes_pb2.EndpointIndex
    discardedEvents: int
    storedEvents: int
    def __init__(self, index: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ..., discardedEvents: _Optional[int] = ..., storedEvents: _Optional[int] = ...) -> None: ...

class ChannelNumber(_message.Message):
    __slots__ = ("index", "channel")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    CHANNEL_FIELD_NUMBER: _ClassVar[int]
    index: _datatypes_pb2.EndpointIndex
    channel: int
    def __init__(self, index: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ..., channel: _Optional[int] = ...) -> None: ...

class ChannelConfiguration(_message.Message):
    __slots__ = ("index", "channel", "status")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    CHANNEL_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    index: _datatypes_pb2.EndpointIndex
    channel: int
    status: bool
    def __init__(self, index: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ..., channel: _Optional[int] = ..., status: bool = ...) -> None: ...
