import qiclib.packages.grpc.datatypes_pb2 as _datatypes_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
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

class Status(_message.Message):
    __slots__ = ("vtc_enabled", "calibration_done")
    VTC_ENABLED_FIELD_NUMBER: _ClassVar[int]
    CALIBRATION_DONE_FIELD_NUMBER: _ClassVar[int]
    vtc_enabled: bool
    calibration_done: bool
    def __init__(self, vtc_enabled: bool = ..., calibration_done: bool = ...) -> None: ...

class Port(_message.Message):
    __slots__ = ("kind", "value")
    class Kind(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        CLK: _ClassVar[Port.Kind]
        A: _ClassVar[Port.Kind]
        B: _ClassVar[Port.Kind]
    CLK: Port.Kind
    A: Port.Kind
    B: Port.Kind
    KIND_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    kind: Port.Kind
    value: int
    def __init__(self, kind: _Optional[_Union[Port.Kind, str]] = ..., value: _Optional[int] = ...) -> None: ...

class PortDelaySetting(_message.Message):
    __slots__ = ("port", "value")
    PORT_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    port: Port
    value: float
    def __init__(self, port: _Optional[_Union[Port, _Mapping]] = ..., value: _Optional[float] = ...) -> None: ...
