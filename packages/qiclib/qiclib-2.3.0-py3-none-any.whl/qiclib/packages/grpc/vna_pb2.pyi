from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PhaseUnit(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    RADIAN: _ClassVar[PhaseUnit]
    DEGREES: _ClassVar[PhaseUnit]

class MagnitudeUnit(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    LINEAR: _ClassVar[MagnitudeUnit]
    DB_FS: _ClassVar[MagnitudeUnit]
RADIAN: PhaseUnit
DEGREES: PhaseUnit
LINEAR: MagnitudeUnit
DB_FS: MagnitudeUnit

class CalibrationData(_message.Message):
    __slots__ = ("name", "json")
    NAME_FIELD_NUMBER: _ClassVar[int]
    JSON_FIELD_NUMBER: _ClassVar[int]
    name: str
    json: str
    def __init__(self, name: _Optional[str] = ..., json: _Optional[str] = ...) -> None: ...

class CalibrationOptios(_message.Message):
    __slots__ = ("name", "comment", "fulcrums", "averages")
    NAME_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    FULCRUMS_FIELD_NUMBER: _ClassVar[int]
    AVERAGES_FIELD_NUMBER: _ClassVar[int]
    name: str
    comment: str
    fulcrums: int
    averages: int
    def __init__(self, name: _Optional[str] = ..., comment: _Optional[str] = ..., fulcrums: _Optional[int] = ..., averages: _Optional[int] = ...) -> None: ...

class CalibrationInfo(_message.Message):
    __slots__ = ("comment", "start_frequency", "step_frequency", "frequency_count", "time")
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    START_FREQUENCY_FIELD_NUMBER: _ClassVar[int]
    STEP_FREQUENCY_FIELD_NUMBER: _ClassVar[int]
    FREQUENCY_COUNT_FIELD_NUMBER: _ClassVar[int]
    TIME_FIELD_NUMBER: _ClassVar[int]
    comment: str
    start_frequency: float
    step_frequency: float
    frequency_count: int
    time: _timestamp_pb2.Timestamp
    def __init__(self, comment: _Optional[str] = ..., start_frequency: _Optional[float] = ..., step_frequency: _Optional[float] = ..., frequency_count: _Optional[int] = ..., time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class AvailableCalibrations(_message.Message):
    __slots__ = ("values",)
    class ValuesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: CalibrationInfo
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[CalibrationInfo, _Mapping]] = ...) -> None: ...
    VALUES_FIELD_NUMBER: _ClassVar[int]
    values: _containers.MessageMap[str, CalibrationInfo]
    def __init__(self, values: _Optional[_Mapping[str, CalibrationInfo]] = ...) -> None: ...

class ResonatorOptions(_message.Message):
    __slots__ = ("n_resonators", "smoothing_window", "derivative_smoothing_window", "sample_option", "filtering_window")
    N_RESONATORS_FIELD_NUMBER: _ClassVar[int]
    SMOOTHING_WINDOW_FIELD_NUMBER: _ClassVar[int]
    DERIVATIVE_SMOOTHING_WINDOW_FIELD_NUMBER: _ClassVar[int]
    SAMPLE_OPTION_FIELD_NUMBER: _ClassVar[int]
    FILTERING_WINDOW_FIELD_NUMBER: _ClassVar[int]
    n_resonators: int
    smoothing_window: int
    derivative_smoothing_window: int
    sample_option: int
    filtering_window: int
    def __init__(self, n_resonators: _Optional[int] = ..., smoothing_window: _Optional[int] = ..., derivative_smoothing_window: _Optional[int] = ..., sample_option: _Optional[int] = ..., filtering_window: _Optional[int] = ...) -> None: ...

class DetectedResonators(_message.Message):
    __slots__ = ("smoothed_spectrum", "unsmoothed_spectrum", "phase", "derivative", "resonator_indices", "detection_successful")
    SMOOTHED_SPECTRUM_FIELD_NUMBER: _ClassVar[int]
    UNSMOOTHED_SPECTRUM_FIELD_NUMBER: _ClassVar[int]
    PHASE_FIELD_NUMBER: _ClassVar[int]
    DERIVATIVE_FIELD_NUMBER: _ClassVar[int]
    RESONATOR_INDICES_FIELD_NUMBER: _ClassVar[int]
    DETECTION_SUCCESSFUL_FIELD_NUMBER: _ClassVar[int]
    smoothed_spectrum: _containers.RepeatedScalarFieldContainer[float]
    unsmoothed_spectrum: _containers.RepeatedScalarFieldContainer[float]
    phase: _containers.RepeatedScalarFieldContainer[float]
    derivative: _containers.RepeatedScalarFieldContainer[float]
    resonator_indices: _containers.RepeatedScalarFieldContainer[int]
    detection_successful: bool
    def __init__(self, smoothed_spectrum: _Optional[_Iterable[float]] = ..., unsmoothed_spectrum: _Optional[_Iterable[float]] = ..., phase: _Optional[_Iterable[float]] = ..., derivative: _Optional[_Iterable[float]] = ..., resonator_indices: _Optional[_Iterable[int]] = ..., detection_successful: bool = ...) -> None: ...

class FrequencySpec(_message.Message):
    __slots__ = ("start", "step", "count")
    START_FIELD_NUMBER: _ClassVar[int]
    STEP_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    start: float
    step: float
    count: float
    def __init__(self, start: _Optional[float] = ..., step: _Optional[float] = ..., count: _Optional[float] = ...) -> None: ...

class PhaseUnit_(_message.Message):
    __slots__ = ("phase_unit",)
    PHASE_UNIT_FIELD_NUMBER: _ClassVar[int]
    phase_unit: PhaseUnit
    def __init__(self, phase_unit: _Optional[_Union[PhaseUnit, str]] = ...) -> None: ...

class MagnitudeUnit_(_message.Message):
    __slots__ = ("magnitude_unit",)
    MAGNITUDE_UNIT_FIELD_NUMBER: _ClassVar[int]
    magnitude_unit: MagnitudeUnit
    def __init__(self, magnitude_unit: _Optional[_Union[MagnitudeUnit, str]] = ...) -> None: ...

class TransmissionOptions(_message.Message):
    __slots__ = ("magnitude_unit", "phase_unit", "unwrap_phase")
    MAGNITUDE_UNIT_FIELD_NUMBER: _ClassVar[int]
    PHASE_UNIT_FIELD_NUMBER: _ClassVar[int]
    UNWRAP_PHASE_FIELD_NUMBER: _ClassVar[int]
    magnitude_unit: MagnitudeUnit
    phase_unit: PhaseUnit
    unwrap_phase: bool
    def __init__(self, magnitude_unit: _Optional[_Union[MagnitudeUnit, str]] = ..., phase_unit: _Optional[_Union[PhaseUnit, str]] = ..., unwrap_phase: bool = ...) -> None: ...

class Polar(_message.Message):
    __slots__ = ("magnitude", "phase")
    MAGNITUDE_FIELD_NUMBER: _ClassVar[int]
    PHASE_FIELD_NUMBER: _ClassVar[int]
    magnitude: float
    phase: float
    def __init__(self, magnitude: _Optional[float] = ..., phase: _Optional[float] = ...) -> None: ...

class Transmission(_message.Message):
    __slots__ = ("values",)
    VALUES_FIELD_NUMBER: _ClassVar[int]
    values: _containers.RepeatedCompositeFieldContainer[Polar]
    def __init__(self, values: _Optional[_Iterable[_Union[Polar, _Mapping]]] = ...) -> None: ...

class CalData(_message.Message):
    __slots__ = ("f_min", "f_max", "magnitude", "phase")
    F_MIN_FIELD_NUMBER: _ClassVar[int]
    F_MAX_FIELD_NUMBER: _ClassVar[int]
    MAGNITUDE_FIELD_NUMBER: _ClassVar[int]
    PHASE_FIELD_NUMBER: _ClassVar[int]
    f_min: float
    f_max: float
    magnitude: _containers.RepeatedScalarFieldContainer[float]
    phase: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, f_min: _Optional[float] = ..., f_max: _Optional[float] = ..., magnitude: _Optional[_Iterable[float]] = ..., phase: _Optional[_Iterable[float]] = ...) -> None: ...
