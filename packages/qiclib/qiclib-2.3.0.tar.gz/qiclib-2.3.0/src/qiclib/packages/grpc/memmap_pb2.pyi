from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UINT8: _ClassVar[Type]
    INT8: _ClassVar[Type]
    UINT16: _ClassVar[Type]
    INT16: _ClassVar[Type]
    UINT32: _ClassVar[Type]
    INT32: _ClassVar[Type]
    UINT64: _ClassVar[Type]
    INT64: _ClassVar[Type]
UINT8: Type
INT8: Type
UINT16: Type
INT16: Type
UINT32: Type
INT32: Type
UINT64: Type
INT64: Type

class ReadRequest(_message.Message):
    __slots__ = ("adr", "count", "type")
    ADR_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    adr: int
    count: int
    type: Type
    def __init__(self, adr: _Optional[int] = ..., count: _Optional[int] = ..., type: _Optional[_Union[Type, str]] = ...) -> None: ...

class ReadSliceRequest(_message.Message):
    __slots__ = ("adr", "type", "slice_lsb", "slice_width")
    ADR_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    SLICE_LSB_FIELD_NUMBER: _ClassVar[int]
    SLICE_WIDTH_FIELD_NUMBER: _ClassVar[int]
    adr: int
    type: Type
    slice_lsb: int
    slice_width: int
    def __init__(self, adr: _Optional[int] = ..., type: _Optional[_Union[Type, str]] = ..., slice_lsb: _Optional[int] = ..., slice_width: _Optional[int] = ...) -> None: ...

class WriteSliceRequest(_message.Message):
    __slots__ = ("adr", "value", "type", "slice_lsb", "slice_width")
    ADR_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    SLICE_LSB_FIELD_NUMBER: _ClassVar[int]
    SLICE_WIDTH_FIELD_NUMBER: _ClassVar[int]
    adr: int
    value: int
    type: Type
    slice_lsb: int
    slice_width: int
    def __init__(self, adr: _Optional[int] = ..., value: _Optional[int] = ..., type: _Optional[_Union[Type, str]] = ..., slice_lsb: _Optional[int] = ..., slice_width: _Optional[int] = ...) -> None: ...

class WriteRequest(_message.Message):
    __slots__ = ("adr", "value", "type")
    ADR_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    adr: int
    value: _containers.RepeatedScalarFieldContainer[int]
    type: Type
    def __init__(self, adr: _Optional[int] = ..., value: _Optional[_Iterable[int]] = ..., type: _Optional[_Union[Type, str]] = ...) -> None: ...

class MemContent(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, value: _Optional[_Iterable[int]] = ...) -> None: ...

class WriteAck(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...
