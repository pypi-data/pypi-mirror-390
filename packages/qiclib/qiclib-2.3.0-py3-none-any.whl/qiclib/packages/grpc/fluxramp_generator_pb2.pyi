import qiclib.packages.grpc.datatypes_pb2 as _datatypes_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FluxrampRequest(_message.Message):
    __slots__ = ("index", "frequency", "amplitude", "falltime")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    FREQUENCY_FIELD_NUMBER: _ClassVar[int]
    AMPLITUDE_FIELD_NUMBER: _ClassVar[int]
    FALLTIME_FIELD_NUMBER: _ClassVar[int]
    index: _datatypes_pb2.EndpointIndex
    frequency: float
    amplitude: float
    falltime: float
    def __init__(self, index: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ..., frequency: _Optional[float] = ..., amplitude: _Optional[float] = ..., falltime: _Optional[float] = ...) -> None: ...
