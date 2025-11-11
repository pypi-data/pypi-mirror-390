from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ConverterType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ADC: _ClassVar[ConverterType]
    DAC: _ClassVar[ConverterType]

class IODirection(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    IN: _ClassVar[IODirection]
    OUT: _ClassVar[IODirection]
ADC: ConverterType
DAC: ConverterType
IN: IODirection
OUT: IODirection

class DacAnalogPath(_message.Message):
    __slots__ = ("index", "setting")
    class Setting(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DC: _ClassVar[DacAnalogPath.Setting]
        NYQUIST_1: _ClassVar[DacAnalogPath.Setting]
        NYQUIST_2: _ClassVar[DacAnalogPath.Setting]
        OFF: _ClassVar[DacAnalogPath.Setting]
    DC: DacAnalogPath.Setting
    NYQUIST_1: DacAnalogPath.Setting
    NYQUIST_2: DacAnalogPath.Setting
    OFF: DacAnalogPath.Setting
    INDEX_FIELD_NUMBER: _ClassVar[int]
    SETTING_FIELD_NUMBER: _ClassVar[int]
    index: int
    setting: DacAnalogPath.Setting
    def __init__(self, index: _Optional[int] = ..., setting: _Optional[_Union[DacAnalogPath.Setting, str]] = ...) -> None: ...

class AdcAnalogPath(_message.Message):
    __slots__ = ("index", "setting")
    class Setting(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        NYQUIST_1: _ClassVar[AdcAnalogPath.Setting]
        NYQUIST_2: _ClassVar[AdcAnalogPath.Setting]
        NYQUIST_6: _ClassVar[AdcAnalogPath.Setting]
        NYQUIST_7: _ClassVar[AdcAnalogPath.Setting]
        OFF: _ClassVar[AdcAnalogPath.Setting]
    NYQUIST_1: AdcAnalogPath.Setting
    NYQUIST_2: AdcAnalogPath.Setting
    NYQUIST_6: AdcAnalogPath.Setting
    NYQUIST_7: AdcAnalogPath.Setting
    OFF: AdcAnalogPath.Setting
    INDEX_FIELD_NUMBER: _ClassVar[int]
    SETTING_FIELD_NUMBER: _ClassVar[int]
    index: int
    setting: AdcAnalogPath.Setting
    def __init__(self, index: _Optional[int] = ..., setting: _Optional[_Union[AdcAnalogPath.Setting, str]] = ...) -> None: ...

class ConverterIndex(_message.Message):
    __slots__ = ("type", "index")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    type: ConverterType
    index: int
    def __init__(self, type: _Optional[_Union[ConverterType, str]] = ..., index: _Optional[int] = ...) -> None: ...

class IndexedDouble(_message.Message):
    __slots__ = ("index", "value")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    index: ConverterIndex
    value: float
    def __init__(self, index: _Optional[_Union[ConverterIndex, _Mapping]] = ..., value: _Optional[float] = ...) -> None: ...

class RfDcIndex(_message.Message):
    __slots__ = ("tile", "block")
    TILE_FIELD_NUMBER: _ClassVar[int]
    BLOCK_FIELD_NUMBER: _ClassVar[int]
    tile: int
    block: int
    def __init__(self, tile: _Optional[int] = ..., block: _Optional[int] = ...) -> None: ...

class DigitalPinDirection(_message.Message):
    __slots__ = ("direction", "pin")
    DIRECTION_FIELD_NUMBER: _ClassVar[int]
    PIN_FIELD_NUMBER: _ClassVar[int]
    direction: IODirection
    pin: int
    def __init__(self, direction: _Optional[_Union[IODirection, str]] = ..., pin: _Optional[int] = ...) -> None: ...
