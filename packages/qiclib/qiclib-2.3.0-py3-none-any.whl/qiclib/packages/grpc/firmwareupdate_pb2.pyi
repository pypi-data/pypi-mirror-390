import qiclib.packages.grpc.datatypes_pb2 as _datatypes_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Firmware(_message.Message):
    __slots__ = ("name", "data")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    name: str
    data: bytes
    def __init__(self, name: _Optional[str] = ..., data: _Optional[bytes] = ...) -> None: ...

class FirmwareNames(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, value: _Optional[_Iterable[str]] = ...) -> None: ...

class UpdateRequest(_message.Message):
    __slots__ = ("name", "clean")
    NAME_FIELD_NUMBER: _ClassVar[int]
    CLEAN_FIELD_NUMBER: _ClassVar[int]
    name: str
    clean: bool
    def __init__(self, name: _Optional[str] = ..., clean: bool = ...) -> None: ...

class FirmwareChunk(_message.Message):
    __slots__ = ("data", "isLast", "name")
    DATA_FIELD_NUMBER: _ClassVar[int]
    ISLAST_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    data: bytes
    isLast: bool
    name: str
    def __init__(self, data: _Optional[bytes] = ..., isLast: bool = ..., name: _Optional[str] = ...) -> None: ...

class FirmwareError(_message.Message):
    __slots__ = ("ocurred", "msg")
    OCURRED_FIELD_NUMBER: _ClassVar[int]
    MSG_FIELD_NUMBER: _ClassVar[int]
    ocurred: bool
    msg: str
    def __init__(self, ocurred: bool = ..., msg: _Optional[str] = ...) -> None: ...
