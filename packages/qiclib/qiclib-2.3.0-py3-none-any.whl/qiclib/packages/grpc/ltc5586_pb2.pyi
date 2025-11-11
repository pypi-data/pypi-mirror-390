import qiclib.packages.grpc.datatypes_pb2 as _datatypes_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union
from qiclib.packages.grpc.datatypes_pb2 import EndpointIndex as EndpointIndex
from qiclib.packages.grpc.datatypes_pb2 import Empty as Empty
from qiclib.packages.grpc.datatypes_pb2 import Bool as Bool
from qiclib.packages.grpc.datatypes_pb2 import Int as Int
from qiclib.packages.grpc.datatypes_pb2 import LInt as LInt
from qiclib.packages.grpc.datatypes_pb2 import UInt as UInt
from qiclib.packages.grpc.datatypes_pb2 import LUInt as LUInt
from qiclib.packages.grpc.datatypes_pb2 import Float as Float
from qiclib.packages.grpc.datatypes_pb2 import Double as Double
from qiclib.packages.grpc.datatypes_pb2 import String as String
from qiclib.packages.grpc.datatypes_pb2 import IndexedBool as IndexedBool
from qiclib.packages.grpc.datatypes_pb2 import IndexedInt as IndexedInt
from qiclib.packages.grpc.datatypes_pb2 import IndexedLInt as IndexedLInt
from qiclib.packages.grpc.datatypes_pb2 import IndexedUInt as IndexedUInt
from qiclib.packages.grpc.datatypes_pb2 import IndexedLUInt as IndexedLUInt
from qiclib.packages.grpc.datatypes_pb2 import IndexedFloat as IndexedFloat
from qiclib.packages.grpc.datatypes_pb2 import IndexedDouble as IndexedDouble
from qiclib.packages.grpc.datatypes_pb2 import IndexedString as IndexedString

DESCRIPTOR: _descriptor.FileDescriptor

class WriteVector(_message.Message):
    __slots__ = ("index", "name", "x", "y")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    index: _datatypes_pb2.EndpointIndex
    name: str
    x: int
    y: int
    def __init__(self, index: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ..., name: _Optional[str] = ..., x: _Optional[int] = ..., y: _Optional[int] = ...) -> None: ...

class VectorReg(_message.Message):
    __slots__ = ("index", "name")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    index: _datatypes_pb2.EndpointIndex
    name: str
    def __init__(self, index: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ..., name: _Optional[str] = ...) -> None: ...

class ReturnVector(_message.Message):
    __slots__ = ("x", "y")
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    x: int
    y: int
    def __init__(self, x: _Optional[int] = ..., y: _Optional[int] = ...) -> None: ...
