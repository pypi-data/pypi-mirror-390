import qiclib.packages.grpc.datatypes_pb2 as _datatypes_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class NCOParam(_message.Message):
    __slots__ = ("frequency", "phase")
    FREQUENCY_FIELD_NUMBER: _ClassVar[int]
    PHASE_FIELD_NUMBER: _ClassVar[int]
    frequency: str
    phase: float
    def __init__(self, frequency: _Optional[str] = ..., phase: _Optional[float] = ...) -> None: ...

class MultiNCO(_message.Message):
    __slots__ = ("params", "index")
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    params: _containers.RepeatedCompositeFieldContainer[NCOParam]
    index: _datatypes_pb2.EndpointIndex
    def __init__(self, params: _Optional[_Iterable[_Union[NCOParam, _Mapping]]] = ..., index: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ...) -> None: ...

class SingleNCO(_message.Message):
    __slots__ = ("param", "channel", "index")
    PARAM_FIELD_NUMBER: _ClassVar[int]
    CHANNEL_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    param: NCOParam
    channel: int
    index: _datatypes_pb2.EndpointIndex
    def __init__(self, param: _Optional[_Union[NCOParam, _Mapping]] = ..., channel: _Optional[int] = ..., index: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ...) -> None: ...
