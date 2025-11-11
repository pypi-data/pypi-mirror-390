import qiclib.packages.grpc.datatypes_pb2 as _datatypes_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ChannelCount(_message.Message):
    __slots__ = ("input_channel_count", "output_channel_count")
    INPUT_CHANNEL_COUNT_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_CHANNEL_COUNT_FIELD_NUMBER: _ClassVar[int]
    input_channel_count: int
    output_channel_count: int
    def __init__(self, input_channel_count: _Optional[int] = ..., output_channel_count: _Optional[int] = ...) -> None: ...

class Configuration(_message.Message):
    __slots__ = ("index", "channels")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    CHANNELS_FIELD_NUMBER: _ClassVar[int]
    index: _datatypes_pb2.EndpointIndex
    channels: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, index: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ..., channels: _Optional[_Iterable[int]] = ...) -> None: ...
