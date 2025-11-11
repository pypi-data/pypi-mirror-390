import qiclib.packages.grpc.datatypes_pb2 as _datatypes_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ConverterType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ADC: _ClassVar[ConverterType]
    DAC: _ClassVar[ConverterType]

class InvSincFIR_Enum(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DISABLED: _ClassVar[InvSincFIR_Enum]
    FIRST_NYQUIST: _ClassVar[InvSincFIR_Enum]
    SECOND_NYQUIST: _ClassVar[InvSincFIR_Enum]

class MixerMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    OFF: _ClassVar[MixerMode]
    COMPLEX_TO_COMPLEX: _ClassVar[MixerMode]
    COMPLEX_TO_REAL: _ClassVar[MixerMode]
    REAL_TO_COMPLEX: _ClassVar[MixerMode]

class DataType_Enum(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    REAL: _ClassVar[DataType_Enum]
    IQ: _ClassVar[DataType_Enum]
ADC: ConverterType
DAC: ConverterType
DISABLED: InvSincFIR_Enum
FIRST_NYQUIST: InvSincFIR_Enum
SECOND_NYQUIST: InvSincFIR_Enum
OFF: MixerMode
COMPLEX_TO_COMPLEX: MixerMode
COMPLEX_TO_REAL: MixerMode
REAL_TO_COMPLEX: MixerMode
REAL: DataType_Enum
IQ: DataType_Enum

class ConverterIndex(_message.Message):
    __slots__ = ("tile", "block", "converter_type")
    TILE_FIELD_NUMBER: _ClassVar[int]
    BLOCK_FIELD_NUMBER: _ClassVar[int]
    CONVERTER_TYPE_FIELD_NUMBER: _ClassVar[int]
    tile: int
    block: int
    converter_type: ConverterType
    def __init__(self, tile: _Optional[int] = ..., block: _Optional[int] = ..., converter_type: _Optional[_Union[ConverterType, str]] = ...) -> None: ...

class TileIndex(_message.Message):
    __slots__ = ("tile", "converter_type")
    TILE_FIELD_NUMBER: _ClassVar[int]
    CONVERTER_TYPE_FIELD_NUMBER: _ClassVar[int]
    tile: int
    converter_type: ConverterType
    def __init__(self, tile: _Optional[int] = ..., converter_type: _Optional[_Union[ConverterType, str]] = ...) -> None: ...

class BlockStatus(_message.Message):
    __slots__ = ("frequency", "analogstatus", "digitalstatus", "clockstatus", "fifoflagsenabled", "fifoflagsasserted")
    FREQUENCY_FIELD_NUMBER: _ClassVar[int]
    ANALOGSTATUS_FIELD_NUMBER: _ClassVar[int]
    DIGITALSTATUS_FIELD_NUMBER: _ClassVar[int]
    CLOCKSTATUS_FIELD_NUMBER: _ClassVar[int]
    FIFOFLAGSENABLED_FIELD_NUMBER: _ClassVar[int]
    FIFOFLAGSASSERTED_FIELD_NUMBER: _ClassVar[int]
    frequency: float
    analogstatus: int
    digitalstatus: int
    clockstatus: int
    fifoflagsenabled: int
    fifoflagsasserted: int
    def __init__(self, frequency: _Optional[float] = ..., analogstatus: _Optional[int] = ..., digitalstatus: _Optional[int] = ..., clockstatus: _Optional[int] = ..., fifoflagsenabled: _Optional[int] = ..., fifoflagsasserted: _Optional[int] = ...) -> None: ...

class Frequency(_message.Message):
    __slots__ = ("index", "value")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    index: ConverterIndex
    value: float
    def __init__(self, index: _Optional[_Union[ConverterIndex, _Mapping]] = ..., value: _Optional[float] = ...) -> None: ...

class NyquistZone(_message.Message):
    __slots__ = ("index", "value")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    index: ConverterIndex
    value: int
    def __init__(self, index: _Optional[_Union[ConverterIndex, _Mapping]] = ..., value: _Optional[int] = ...) -> None: ...

class InvSincFIR(_message.Message):
    __slots__ = ("index", "value")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    index: ConverterIndex
    value: InvSincFIR_Enum
    def __init__(self, index: _Optional[_Union[ConverterIndex, _Mapping]] = ..., value: _Optional[_Union[InvSincFIR_Enum, str]] = ...) -> None: ...

class ThresholdToUpdate(_message.Message):
    __slots__ = ("index", "threshold")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    index: ConverterIndex
    threshold: int
    def __init__(self, index: _Optional[_Union[ConverterIndex, _Mapping]] = ..., threshold: _Optional[int] = ...) -> None: ...

class InterruptSettings(_message.Message):
    __slots__ = ("index", "intrmask")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    INTRMASK_FIELD_NUMBER: _ClassVar[int]
    index: ConverterIndex
    intrmask: int
    def __init__(self, index: _Optional[_Union[ConverterIndex, _Mapping]] = ..., intrmask: _Optional[int] = ...) -> None: ...

class Phase(_message.Message):
    __slots__ = ("index", "value")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    index: ConverterIndex
    value: float
    def __init__(self, index: _Optional[_Union[ConverterIndex, _Mapping]] = ..., value: _Optional[float] = ...) -> None: ...

class MixerSettings(_message.Message):
    __slots__ = ("index", "mode", "frequency")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    FREQUENCY_FIELD_NUMBER: _ClassVar[int]
    index: ConverterIndex
    mode: MixerMode
    frequency: float
    def __init__(self, index: _Optional[_Union[ConverterIndex, _Mapping]] = ..., mode: _Optional[_Union[MixerMode, str]] = ..., frequency: _Optional[float] = ...) -> None: ...

class Mode(_message.Message):
    __slots__ = ("mode",)
    MODE_FIELD_NUMBER: _ClassVar[int]
    mode: MixerMode
    def __init__(self, mode: _Optional[_Union[MixerMode, str]] = ...) -> None: ...

class IndexedMode(_message.Message):
    __slots__ = ("index", "mode")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    index: ConverterIndex
    mode: MixerMode
    def __init__(self, index: _Optional[_Union[ConverterIndex, _Mapping]] = ..., mode: _Optional[_Union[MixerMode, str]] = ...) -> None: ...

class DataType(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: DataType_Enum
    def __init__(self, value: _Optional[_Union[DataType_Enum, str]] = ...) -> None: ...

class Interpolation(_message.Message):
    __slots__ = ("index", "factor")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    FACTOR_FIELD_NUMBER: _ClassVar[int]
    index: ConverterIndex
    factor: int
    def __init__(self, index: _Optional[_Union[ConverterIndex, _Mapping]] = ..., factor: _Optional[int] = ...) -> None: ...

class Decimation(_message.Message):
    __slots__ = ("index", "factor")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    FACTOR_FIELD_NUMBER: _ClassVar[int]
    index: ConverterIndex
    factor: int
    def __init__(self, index: _Optional[_Union[ConverterIndex, _Mapping]] = ..., factor: _Optional[int] = ...) -> None: ...

class StatusReport(_message.Message):
    __slots__ = ("failure", "report", "adc_overrange", "adc_overvoltage")
    FAILURE_FIELD_NUMBER: _ClassVar[int]
    REPORT_FIELD_NUMBER: _ClassVar[int]
    ADC_OVERRANGE_FIELD_NUMBER: _ClassVar[int]
    ADC_OVERVOLTAGE_FIELD_NUMBER: _ClassVar[int]
    failure: bool
    report: str
    adc_overrange: _containers.RepeatedCompositeFieldContainer[ConverterIndex]
    adc_overvoltage: _containers.RepeatedCompositeFieldContainer[ConverterIndex]
    def __init__(self, failure: bool = ..., report: _Optional[str] = ..., adc_overrange: _Optional[_Iterable[_Union[ConverterIndex, _Mapping]]] = ..., adc_overvoltage: _Optional[_Iterable[_Union[ConverterIndex, _Mapping]]] = ...) -> None: ...

class IndexedDouble(_message.Message):
    __slots__ = ("index", "value")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    index: ConverterIndex
    value: float
    def __init__(self, index: _Optional[_Union[ConverterIndex, _Mapping]] = ..., value: _Optional[float] = ...) -> None: ...
