import qiclib.packages.grpc.datatypes_pb2 as _datatypes_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class StatusReport(_message.Message):
    __slots__ = ("report", "failure")
    REPORT_FIELD_NUMBER: _ClassVar[int]
    FAILURE_FIELD_NUMBER: _ClassVar[int]
    report: str
    failure: bool
    def __init__(self, report: _Optional[str] = ..., failure: bool = ...) -> None: ...

class InterferometerMode(_message.Message):
    __slots__ = ("index", "is_interferometer")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    IS_INTERFEROMETER_FIELD_NUMBER: _ClassVar[int]
    index: _datatypes_pb2.EndpointIndex
    is_interferometer: bool
    def __init__(self, index: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ..., is_interferometer: bool = ...) -> None: ...

class ContinuousMode(_message.Message):
    __slots__ = ("index", "is_continuous")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    IS_CONTINUOUS_FIELD_NUMBER: _ClassVar[int]
    index: _datatypes_pb2.EndpointIndex
    is_continuous: bool
    def __init__(self, index: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ..., is_continuous: bool = ...) -> None: ...

class Trigger(_message.Message):
    __slots__ = ("index", "value")
    class TriggerValue(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        NONE: _ClassVar[Trigger.TriggerValue]
        SINGLE: _ClassVar[Trigger.TriggerValue]
        ONESHOT: _ClassVar[Trigger.TriggerValue]
        START_CONTINUOUS: _ClassVar[Trigger.TriggerValue]
        STOP_CONTINUOUS: _ClassVar[Trigger.TriggerValue]
        RESET: _ClassVar[Trigger.TriggerValue]
        NCO_SYNC: _ClassVar[Trigger.TriggerValue]
    NONE: Trigger.TriggerValue
    SINGLE: Trigger.TriggerValue
    ONESHOT: Trigger.TriggerValue
    START_CONTINUOUS: Trigger.TriggerValue
    STOP_CONTINUOUS: Trigger.TriggerValue
    RESET: Trigger.TriggerValue
    NCO_SYNC: Trigger.TriggerValue
    INDEX_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    index: _datatypes_pb2.EndpointIndex
    value: Trigger.TriggerValue
    def __init__(self, index: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ..., value: _Optional[_Union[Trigger.TriggerValue, str]] = ...) -> None: ...

class TriggerOffset(_message.Message):
    __slots__ = ("index", "value")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    index: _datatypes_pb2.EndpointIndex
    value: float
    def __init__(self, index: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ..., value: _Optional[float] = ...) -> None: ...

class RecordingDuration(_message.Message):
    __slots__ = ("index", "value")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    index: _datatypes_pb2.EndpointIndex
    value: float
    def __init__(self, index: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ..., value: _Optional[float] = ...) -> None: ...

class ValueShift(_message.Message):
    __slots__ = ("index", "value")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    index: _datatypes_pb2.EndpointIndex
    value: int
    def __init__(self, index: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ..., value: _Optional[int] = ...) -> None: ...

class ValueShiftOffset(_message.Message):
    __slots__ = ("index", "value")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    index: _datatypes_pb2.EndpointIndex
    value: int
    def __init__(self, index: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ..., value: _Optional[int] = ...) -> None: ...

class AverageShift(_message.Message):
    __slots__ = ("index", "value")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    index: _datatypes_pb2.EndpointIndex
    value: int
    def __init__(self, index: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ..., value: _Optional[int] = ...) -> None: ...

class Frequency(_message.Message):
    __slots__ = ("index", "value")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    index: _datatypes_pb2.EndpointIndex
    value: float
    def __init__(self, index: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ..., value: _Optional[float] = ...) -> None: ...

class PhaseOffset(_message.Message):
    __slots__ = ("index", "value")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    index: _datatypes_pb2.EndpointIndex
    value: float
    def __init__(self, index: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ..., value: _Optional[float] = ...) -> None: ...

class ReferenceDelay(_message.Message):
    __slots__ = ("index", "value")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    index: _datatypes_pb2.EndpointIndex
    value: float
    def __init__(self, index: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ..., value: _Optional[float] = ...) -> None: ...

class StateConfig(_message.Message):
    __slots__ = ("index", "value_ai", "value_aq", "value_b")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    VALUE_AI_FIELD_NUMBER: _ClassVar[int]
    VALUE_AQ_FIELD_NUMBER: _ClassVar[int]
    VALUE_B_FIELD_NUMBER: _ClassVar[int]
    index: _datatypes_pb2.EndpointIndex
    value_ai: int
    value_aq: int
    value_b: int
    def __init__(self, index: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ..., value_ai: _Optional[int] = ..., value_aq: _Optional[int] = ..., value_b: _Optional[int] = ...) -> None: ...

class IQResult(_message.Message):
    __slots__ = ("i_value", "q_value")
    I_VALUE_FIELD_NUMBER: _ClassVar[int]
    Q_VALUE_FIELD_NUMBER: _ClassVar[int]
    i_value: int
    q_value: int
    def __init__(self, i_value: _Optional[int] = ..., q_value: _Optional[int] = ...) -> None: ...

class MemorySize(_message.Message):
    __slots__ = ("index", "size")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    index: _datatypes_pb2.EndpointIndex
    size: int
    def __init__(self, index: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ..., size: _Optional[int] = ...) -> None: ...

class MemoryStatus(_message.Message):
    __slots__ = ("index", "size", "empty", "full", "overflow")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    EMPTY_FIELD_NUMBER: _ClassVar[int]
    FULL_FIELD_NUMBER: _ClassVar[int]
    OVERFLOW_FIELD_NUMBER: _ClassVar[int]
    index: _datatypes_pb2.EndpointIndex
    size: int
    empty: bool
    full: bool
    overflow: bool
    def __init__(self, index: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ..., size: _Optional[int] = ..., empty: bool = ..., full: bool = ..., overflow: bool = ...) -> None: ...

class ResultMemory(_message.Message):
    __slots__ = ("result_i", "result_q")
    RESULT_I_FIELD_NUMBER: _ClassVar[int]
    RESULT_Q_FIELD_NUMBER: _ClassVar[int]
    result_i: _containers.RepeatedScalarFieldContainer[int]
    result_q: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, result_i: _Optional[_Iterable[int]] = ..., result_q: _Optional[_Iterable[int]] = ...) -> None: ...

class RawMemory(_message.Message):
    __slots__ = ("raw_i", "raw_q")
    RAW_I_FIELD_NUMBER: _ClassVar[int]
    RAW_Q_FIELD_NUMBER: _ClassVar[int]
    raw_i: _containers.RepeatedScalarFieldContainer[int]
    raw_q: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, raw_i: _Optional[_Iterable[int]] = ..., raw_q: _Optional[_Iterable[int]] = ...) -> None: ...

class ConditioningMatrix(_message.Message):
    __slots__ = ("index", "ii", "iq", "qi", "qq")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    II_FIELD_NUMBER: _ClassVar[int]
    IQ_FIELD_NUMBER: _ClassVar[int]
    QI_FIELD_NUMBER: _ClassVar[int]
    QQ_FIELD_NUMBER: _ClassVar[int]
    index: _datatypes_pb2.EndpointIndex
    ii: float
    iq: float
    qi: float
    qq: float
    def __init__(self, index: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ..., ii: _Optional[float] = ..., iq: _Optional[float] = ..., qi: _Optional[float] = ..., qq: _Optional[float] = ...) -> None: ...

class ConditioningOffset(_message.Message):
    __slots__ = ("index", "i", "q")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    I_FIELD_NUMBER: _ClassVar[int]
    Q_FIELD_NUMBER: _ClassVar[int]
    index: _datatypes_pb2.EndpointIndex
    i: int
    q: int
    def __init__(self, index: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ..., i: _Optional[int] = ..., q: _Optional[int] = ...) -> None: ...
