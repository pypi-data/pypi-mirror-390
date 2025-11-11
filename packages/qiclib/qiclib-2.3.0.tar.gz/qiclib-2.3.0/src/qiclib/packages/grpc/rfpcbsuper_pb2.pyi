import qiclib.packages.grpc.datatypes_pb2 as _datatypes_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
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

class Device(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TXPL: _ClassVar[Device]
    RXPL: _ClassVar[Device]
    IFLO: _ClassVar[Device]
    RFLO: _ClassVar[Device]
    DEMOD: _ClassVar[Device]
TXPL: Device
RXPL: Device
IFLO: Device
RFLO: Device
DEMOD: Device

class LMXStart(_message.Message):
    __slots__ = ("device", "power_a", "power_b")
    DEVICE_FIELD_NUMBER: _ClassVar[int]
    POWER_A_FIELD_NUMBER: _ClassVar[int]
    POWER_B_FIELD_NUMBER: _ClassVar[int]
    device: Device
    power_a: float
    power_b: float
    def __init__(self, device: _Optional[_Union[Device, str]] = ..., power_a: _Optional[float] = ..., power_b: _Optional[float] = ...) -> None: ...

class LTCStart(_message.Message):
    __slots__ = ("gain", "gain_error", "phase_error")
    GAIN_FIELD_NUMBER: _ClassVar[int]
    GAIN_ERROR_FIELD_NUMBER: _ClassVar[int]
    PHASE_ERROR_FIELD_NUMBER: _ClassVar[int]
    gain: int
    gain_error: float
    phase_error: float
    def __init__(self, gain: _Optional[int] = ..., gain_error: _Optional[float] = ..., phase_error: _Optional[float] = ...) -> None: ...

class EndpointList(_message.Message):
    __slots__ = ("index", "devices")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    DEVICES_FIELD_NUMBER: _ClassVar[int]
    index: _datatypes_pb2.EndpointIndex
    devices: _containers.RepeatedScalarFieldContainer[Device]
    def __init__(self, index: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ..., devices: _Optional[_Iterable[_Union[Device, str]]] = ...) -> None: ...

class SweepInput(_message.Message):
    __slots__ = ("index", "frequency", "power", "offset", "method")
    class Method(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        MIXSWEEP: _ClassVar[SweepInput.Method]
        IFSWEEP: _ClassVar[SweepInput.Method]
        IFSWEEP_EXTENDED: _ClassVar[SweepInput.Method]
        RFSWEEP: _ClassVar[SweepInput.Method]
        RFSWEEP_EXTENDED: _ClassVar[SweepInput.Method]
    MIXSWEEP: SweepInput.Method
    IFSWEEP: SweepInput.Method
    IFSWEEP_EXTENDED: SweepInput.Method
    RFSWEEP: SweepInput.Method
    RFSWEEP_EXTENDED: SweepInput.Method
    INDEX_FIELD_NUMBER: _ClassVar[int]
    FREQUENCY_FIELD_NUMBER: _ClassVar[int]
    POWER_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    METHOD_FIELD_NUMBER: _ClassVar[int]
    index: _datatypes_pb2.EndpointIndex
    frequency: float
    power: float
    offset: float
    method: SweepInput.Method
    def __init__(self, index: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ..., frequency: _Optional[float] = ..., power: _Optional[float] = ..., offset: _Optional[float] = ..., method: _Optional[_Union[SweepInput.Method, str]] = ...) -> None: ...

class StartInfo(_message.Message):
    __slots__ = ("index", "lmx_list", "ltc")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    LMX_LIST_FIELD_NUMBER: _ClassVar[int]
    LTC_FIELD_NUMBER: _ClassVar[int]
    index: _datatypes_pb2.EndpointIndex
    lmx_list: _containers.RepeatedCompositeFieldContainer[LMXStart]
    ltc: LTCStart
    def __init__(self, index: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ..., lmx_list: _Optional[_Iterable[_Union[LMXStart, _Mapping]]] = ..., ltc: _Optional[_Union[LTCStart, _Mapping]] = ...) -> None: ...
