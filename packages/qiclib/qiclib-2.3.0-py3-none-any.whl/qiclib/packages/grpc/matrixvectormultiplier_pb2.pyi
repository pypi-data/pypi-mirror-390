import qiclib.packages.grpc.datatypes_pb2 as _datatypes_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Channels(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: int
    def __init__(self, value: _Optional[int] = ...) -> None: ...

class Vector(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, value: _Optional[_Iterable[float]] = ...) -> None: ...

class Matrix(_message.Message):
    __slots__ = ("column",)
    COLUMN_FIELD_NUMBER: _ClassVar[int]
    column: _containers.RepeatedCompositeFieldContainer[Vector]
    def __init__(self, column: _Optional[_Iterable[_Union[Vector, _Mapping]]] = ...) -> None: ...

class Matrices(_message.Message):
    __slots__ = ("channelMatrix", "index")
    CHANNELMATRIX_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    channelMatrix: _containers.RepeatedCompositeFieldContainer[Matrix]
    index: _datatypes_pb2.EndpointIndex
    def __init__(self, channelMatrix: _Optional[_Iterable[_Union[Matrix, _Mapping]]] = ..., index: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ...) -> None: ...
