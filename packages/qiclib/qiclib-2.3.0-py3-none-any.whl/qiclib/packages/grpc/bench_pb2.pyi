import qiclib.packages.grpc.datatypes_pb2 as _datatypes_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class SizeRequest(_message.Message):
    __slots__ = ("size", "blocksize")
    SIZE_FIELD_NUMBER: _ClassVar[int]
    BLOCKSIZE_FIELD_NUMBER: _ClassVar[int]
    size: int
    blocksize: int
    def __init__(self, size: _Optional[int] = ..., blocksize: _Optional[int] = ...) -> None: ...

class DurationReply(_message.Message):
    __slots__ = ("duration", "nivContextSwitches")
    DURATION_FIELD_NUMBER: _ClassVar[int]
    NIVCONTEXTSWITCHES_FIELD_NUMBER: _ClassVar[int]
    duration: float
    nivContextSwitches: int
    def __init__(self, duration: _Optional[float] = ..., nivContextSwitches: _Optional[int] = ...) -> None: ...

class AvailableReply(_message.Message):
    __slots__ = ("available",)
    AVAILABLE_FIELD_NUMBER: _ClassVar[int]
    available: bool
    def __init__(self, available: bool = ...) -> None: ...

class CounterRequest(_message.Message):
    __slots__ = ("newValue",)
    NEWVALUE_FIELD_NUMBER: _ClassVar[int]
    newValue: int
    def __init__(self, newValue: _Optional[int] = ...) -> None: ...

class BenchReply(_message.Message):
    __slots__ = ("Counter", "Array")
    COUNTER_FIELD_NUMBER: _ClassVar[int]
    ARRAY_FIELD_NUMBER: _ClassVar[int]
    Counter: int
    Array: bytes
    def __init__(self, Counter: _Optional[int] = ..., Array: _Optional[bytes] = ...) -> None: ...

class BenchmarkInt32(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: int
    def __init__(self, value: _Optional[int] = ...) -> None: ...

class BenchmarkInt32Array(_message.Message):
    __slots__ = ("values",)
    VALUES_FIELD_NUMBER: _ClassVar[int]
    values: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, values: _Optional[_Iterable[int]] = ...) -> None: ...

class ByteStream(_message.Message):
    __slots__ = ("data",)
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: bytes
    def __init__(self, data: _Optional[bytes] = ...) -> None: ...

class DMASetup(_message.Message):
    __slots__ = ("size", "timeoutinmsecs")
    SIZE_FIELD_NUMBER: _ClassVar[int]
    TIMEOUTINMSECS_FIELD_NUMBER: _ClassVar[int]
    size: int
    timeoutinmsecs: int
    def __init__(self, size: _Optional[int] = ..., timeoutinmsecs: _Optional[int] = ...) -> None: ...

class AcquiredData(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, value: _Optional[_Iterable[int]] = ...) -> None: ...

class LostDataReply(_message.Message):
    __slots__ = ("hw_counter", "sw_counter")
    HW_COUNTER_FIELD_NUMBER: _ClassVar[int]
    SW_COUNTER_FIELD_NUMBER: _ClassVar[int]
    hw_counter: int
    sw_counter: int
    def __init__(self, hw_counter: _Optional[int] = ..., sw_counter: _Optional[int] = ...) -> None: ...
