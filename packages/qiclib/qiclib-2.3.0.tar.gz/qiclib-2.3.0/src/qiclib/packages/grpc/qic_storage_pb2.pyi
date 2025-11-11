import qiclib.packages.grpc.datatypes_pb2 as _datatypes_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class StateHandling(_message.Message):
    __slots__ = ("index", "store", "accumulate", "destination", "dense_mode")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    STORE_FIELD_NUMBER: _ClassVar[int]
    ACCUMULATE_FIELD_NUMBER: _ClassVar[int]
    DESTINATION_FIELD_NUMBER: _ClassVar[int]
    DENSE_MODE_FIELD_NUMBER: _ClassVar[int]
    index: _datatypes_pb2.EndpointIndex
    store: bool
    accumulate: bool
    destination: int
    dense_mode: bool
    def __init__(self, index: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ..., store: bool = ..., accumulate: bool = ..., destination: _Optional[int] = ..., dense_mode: bool = ...) -> None: ...

class StateAccumulation(_message.Message):
    __slots__ = ("accu_states", "accu_counter")
    ACCU_STATES_FIELD_NUMBER: _ClassVar[int]
    ACCU_COUNTER_FIELD_NUMBER: _ClassVar[int]
    accu_states: int
    accu_counter: int
    def __init__(self, accu_states: _Optional[int] = ..., accu_counter: _Optional[int] = ...) -> None: ...

class ResultHandling(_message.Message):
    __slots__ = ("index", "store", "destination")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    STORE_FIELD_NUMBER: _ClassVar[int]
    DESTINATION_FIELD_NUMBER: _ClassVar[int]
    index: _datatypes_pb2.EndpointIndex
    store: bool
    destination: int
    def __init__(self, index: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ..., store: bool = ..., destination: _Optional[int] = ...) -> None: ...

class AveragedHandling(_message.Message):
    __slots__ = ("index", "store", "destination")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    STORE_FIELD_NUMBER: _ClassVar[int]
    DESTINATION_FIELD_NUMBER: _ClassVar[int]
    index: _datatypes_pb2.EndpointIndex
    store: bool
    destination: int
    def __init__(self, index: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ..., store: bool = ..., destination: _Optional[int] = ...) -> None: ...

class BramControl(_message.Message):
    __slots__ = ("index", "reset", "wrap", "bram")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    RESET_FIELD_NUMBER: _ClassVar[int]
    WRAP_FIELD_NUMBER: _ClassVar[int]
    BRAM_FIELD_NUMBER: _ClassVar[int]
    index: _datatypes_pb2.EndpointIndex
    reset: bool
    wrap: bool
    bram: int
    def __init__(self, index: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ..., reset: bool = ..., wrap: bool = ..., bram: _Optional[int] = ...) -> None: ...

class BramStatus(_message.Message):
    __slots__ = ("full", "empty", "overflow", "next_address")
    FULL_FIELD_NUMBER: _ClassVar[int]
    EMPTY_FIELD_NUMBER: _ClassVar[int]
    OVERFLOW_FIELD_NUMBER: _ClassVar[int]
    NEXT_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    full: bool
    empty: bool
    overflow: bool
    next_address: int
    def __init__(self, full: bool = ..., empty: bool = ..., overflow: bool = ..., next_address: _Optional[int] = ...) -> None: ...

class BramIndex(_message.Message):
    __slots__ = ("index", "bram")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    BRAM_FIELD_NUMBER: _ClassVar[int]
    index: _datatypes_pb2.EndpointIndex
    bram: int
    def __init__(self, index: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ..., bram: _Optional[int] = ...) -> None: ...

class ResultData(_message.Message):
    __slots__ = ("result_i", "result_q")
    RESULT_I_FIELD_NUMBER: _ClassVar[int]
    RESULT_Q_FIELD_NUMBER: _ClassVar[int]
    result_i: _containers.RepeatedScalarFieldContainer[int]
    result_q: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, result_i: _Optional[_Iterable[int]] = ..., result_q: _Optional[_Iterable[int]] = ...) -> None: ...

class AveragedData(_message.Message):
    __slots__ = ("averaged",)
    AVERAGED_FIELD_NUMBER: _ClassVar[int]
    averaged: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, averaged: _Optional[_Iterable[int]] = ...) -> None: ...

class StateData(_message.Message):
    __slots__ = ("state",)
    STATE_FIELD_NUMBER: _ClassVar[int]
    state: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, state: _Optional[_Iterable[int]] = ...) -> None: ...

class BramDataUInt32(_message.Message):
    __slots__ = ("data", "bram")
    DATA_FIELD_NUMBER: _ClassVar[int]
    BRAM_FIELD_NUMBER: _ClassVar[int]
    data: _containers.RepeatedScalarFieldContainer[int]
    bram: int
    def __init__(self, data: _Optional[_Iterable[int]] = ..., bram: _Optional[int] = ...) -> None: ...

class BramDataInt32(_message.Message):
    __slots__ = ("data", "bram")
    DATA_FIELD_NUMBER: _ClassVar[int]
    BRAM_FIELD_NUMBER: _ClassVar[int]
    data: _containers.RepeatedScalarFieldContainer[int]
    bram: int
    def __init__(self, data: _Optional[_Iterable[int]] = ..., bram: _Optional[int] = ...) -> None: ...

class LatestData(_message.Message):
    __slots__ = ("data", "bram")
    DATA_FIELD_NUMBER: _ClassVar[int]
    BRAM_FIELD_NUMBER: _ClassVar[int]
    data: int
    bram: int
    def __init__(self, data: _Optional[int] = ..., bram: _Optional[int] = ...) -> None: ...

class DataLost(_message.Message):
    __slots__ = ("single_result", "state_accumulation", "qubit_state", "averaged_result", "bram_input")
    SINGLE_RESULT_FIELD_NUMBER: _ClassVar[int]
    STATE_ACCUMULATION_FIELD_NUMBER: _ClassVar[int]
    QUBIT_STATE_FIELD_NUMBER: _ClassVar[int]
    AVERAGED_RESULT_FIELD_NUMBER: _ClassVar[int]
    BRAM_INPUT_FIELD_NUMBER: _ClassVar[int]
    single_result: bool
    state_accumulation: bool
    qubit_state: bool
    averaged_result: bool
    bram_input: bool
    def __init__(self, single_result: bool = ..., state_accumulation: bool = ..., qubit_state: bool = ..., averaged_result: bool = ..., bram_input: bool = ...) -> None: ...

class WriteDataRequest(_message.Message):
    __slots__ = ("index", "address", "data")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    index: _datatypes_pb2.EndpointIndex
    address: int
    data: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, index: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ..., address: _Optional[int] = ..., data: _Optional[_Iterable[int]] = ...) -> None: ...

class ReadDataRequest(_message.Message):
    __slots__ = ("index", "address", "count")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    index: _datatypes_pb2.EndpointIndex
    address: int
    count: int
    def __init__(self, index: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ..., address: _Optional[int] = ..., count: _Optional[int] = ...) -> None: ...

class ReadDataResponse(_message.Message):
    __slots__ = ("data",)
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, data: _Optional[_Iterable[int]] = ...) -> None: ...
