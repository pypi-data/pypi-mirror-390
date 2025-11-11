from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class EndpointIndex(_message.Message):
    __slots__ = ("value", "name")
    VALUE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    value: int
    name: str
    def __init__(self, value: _Optional[int] = ..., name: _Optional[str] = ...) -> None: ...

class Empty(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class Bool(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: bool
    def __init__(self, value: bool = ...) -> None: ...

class Int(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: int
    def __init__(self, value: _Optional[int] = ...) -> None: ...

class LInt(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: int
    def __init__(self, value: _Optional[int] = ...) -> None: ...

class UInt(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: int
    def __init__(self, value: _Optional[int] = ...) -> None: ...

class LUInt(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: int
    def __init__(self, value: _Optional[int] = ...) -> None: ...

class Float(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: float
    def __init__(self, value: _Optional[float] = ...) -> None: ...

class Double(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: float
    def __init__(self, value: _Optional[float] = ...) -> None: ...

class String(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: str
    def __init__(self, value: _Optional[str] = ...) -> None: ...

class IndexedBool(_message.Message):
    __slots__ = ("index", "value")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    index: EndpointIndex
    value: bool
    def __init__(self, index: _Optional[_Union[EndpointIndex, _Mapping]] = ..., value: bool = ...) -> None: ...

class IndexedInt(_message.Message):
    __slots__ = ("index", "value")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    index: EndpointIndex
    value: int
    def __init__(self, index: _Optional[_Union[EndpointIndex, _Mapping]] = ..., value: _Optional[int] = ...) -> None: ...

class IndexedLInt(_message.Message):
    __slots__ = ("index", "value")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    index: EndpointIndex
    value: int
    def __init__(self, index: _Optional[_Union[EndpointIndex, _Mapping]] = ..., value: _Optional[int] = ...) -> None: ...

class IndexedUInt(_message.Message):
    __slots__ = ("index", "value")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    index: EndpointIndex
    value: int
    def __init__(self, index: _Optional[_Union[EndpointIndex, _Mapping]] = ..., value: _Optional[int] = ...) -> None: ...

class IndexedLUInt(_message.Message):
    __slots__ = ("index", "value")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    index: EndpointIndex
    value: int
    def __init__(self, index: _Optional[_Union[EndpointIndex, _Mapping]] = ..., value: _Optional[int] = ...) -> None: ...

class IndexedFloat(_message.Message):
    __slots__ = ("index", "value")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    index: EndpointIndex
    value: float
    def __init__(self, index: _Optional[_Union[EndpointIndex, _Mapping]] = ..., value: _Optional[float] = ...) -> None: ...

class IndexedDouble(_message.Message):
    __slots__ = ("index", "value")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    index: EndpointIndex
    value: float
    def __init__(self, index: _Optional[_Union[EndpointIndex, _Mapping]] = ..., value: _Optional[float] = ...) -> None: ...

class IndexedString(_message.Message):
    __slots__ = ("index", "value")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    index: EndpointIndex
    value: str
    def __init__(self, index: _Optional[_Union[EndpointIndex, _Mapping]] = ..., value: _Optional[str] = ...) -> None: ...
