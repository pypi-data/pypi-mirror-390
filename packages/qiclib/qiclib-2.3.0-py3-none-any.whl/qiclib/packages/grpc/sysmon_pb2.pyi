import qiclib.packages.grpc.datatypes_pb2 as _datatypes_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
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

class TempSelect(_message.Message):
    __slots__ = ("select",)
    class TempID(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ps_rpu: _ClassVar[TempSelect.TempID]
        ps_apu: _ClassVar[TempSelect.TempID]
        pl: _ClassVar[TempSelect.TempID]
    ps_rpu: TempSelect.TempID
    ps_apu: TempSelect.TempID
    pl: TempSelect.TempID
    SELECT_FIELD_NUMBER: _ClassVar[int]
    select: TempSelect.TempID
    def __init__(self, select: _Optional[_Union[TempSelect.TempID, str]] = ...) -> None: ...

class VoltSelect(_message.Message):
    __slots__ = ("select",)
    class VoltID(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        main_pll: _ClassVar[VoltSelect.VoltID]
        main_batt: _ClassVar[VoltSelect.VoltID]
        main_int: _ClassVar[VoltSelect.VoltID]
        main_ram: _ClassVar[VoltSelect.VoltID]
        main_pl_aux: _ClassVar[VoltSelect.VoltID]
        main_ddr_pll: _ClassVar[VoltSelect.VoltID]
        main_int_ddr: _ClassVar[VoltSelect.VoltID]
        ps_int_lpd: _ClassVar[VoltSelect.VoltID]
        ps_int_fpd: _ClassVar[VoltSelect.VoltID]
        ps_aux: _ClassVar[VoltSelect.VoltID]
        ps_addr: _ClassVar[VoltSelect.VoltID]
        ps_io_3: _ClassVar[VoltSelect.VoltID]
        ps_io_0: _ClassVar[VoltSelect.VoltID]
        ps_io_1: _ClassVar[VoltSelect.VoltID]
        ps_io_2: _ClassVar[VoltSelect.VoltID]
        ps_trav_cc: _ClassVar[VoltSelect.VoltID]
        ps_trav_tt: _ClassVar[VoltSelect.VoltID]
        ps_adc: _ClassVar[VoltSelect.VoltID]
        pl_int: _ClassVar[VoltSelect.VoltID]
        pl_aux: _ClassVar[VoltSelect.VoltID]
        pl_adc_p: _ClassVar[VoltSelect.VoltID]
        pl_adc_n: _ClassVar[VoltSelect.VoltID]
        pl_ram: _ClassVar[VoltSelect.VoltID]
        pl_int_lpd: _ClassVar[VoltSelect.VoltID]
        pl_int_fpd: _ClassVar[VoltSelect.VoltID]
        pl_aux_sup: _ClassVar[VoltSelect.VoltID]
        pl_adc: _ClassVar[VoltSelect.VoltID]
    main_pll: VoltSelect.VoltID
    main_batt: VoltSelect.VoltID
    main_int: VoltSelect.VoltID
    main_ram: VoltSelect.VoltID
    main_pl_aux: VoltSelect.VoltID
    main_ddr_pll: VoltSelect.VoltID
    main_int_ddr: VoltSelect.VoltID
    ps_int_lpd: VoltSelect.VoltID
    ps_int_fpd: VoltSelect.VoltID
    ps_aux: VoltSelect.VoltID
    ps_addr: VoltSelect.VoltID
    ps_io_3: VoltSelect.VoltID
    ps_io_0: VoltSelect.VoltID
    ps_io_1: VoltSelect.VoltID
    ps_io_2: VoltSelect.VoltID
    ps_trav_cc: VoltSelect.VoltID
    ps_trav_tt: VoltSelect.VoltID
    ps_adc: VoltSelect.VoltID
    pl_int: VoltSelect.VoltID
    pl_aux: VoltSelect.VoltID
    pl_adc_p: VoltSelect.VoltID
    pl_adc_n: VoltSelect.VoltID
    pl_ram: VoltSelect.VoltID
    pl_int_lpd: VoltSelect.VoltID
    pl_int_fpd: VoltSelect.VoltID
    pl_aux_sup: VoltSelect.VoltID
    pl_adc: VoltSelect.VoltID
    SELECT_FIELD_NUMBER: _ClassVar[int]
    select: VoltSelect.VoltID
    def __init__(self, select: _Optional[_Union[VoltSelect.VoltID, str]] = ...) -> None: ...
