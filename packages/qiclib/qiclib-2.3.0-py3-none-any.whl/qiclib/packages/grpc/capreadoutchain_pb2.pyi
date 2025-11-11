import qiclib.packages.grpc.datatypes_pb2 as _datatypes_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ChannelLocation(_message.Message):
    __slots__ = ("chain", "subchain", "channel")
    CHAIN_FIELD_NUMBER: _ClassVar[int]
    SUBCHAIN_FIELD_NUMBER: _ClassVar[int]
    CHANNEL_FIELD_NUMBER: _ClassVar[int]
    chain: int
    subchain: int
    channel: int
    def __init__(self, chain: _Optional[int] = ..., subchain: _Optional[int] = ..., channel: _Optional[int] = ...) -> None: ...

class ToneSpecs(_message.Message):
    __slots__ = ("frequency", "amplitude", "phase", "phaseIQI", "amplitudeIQI")
    FREQUENCY_FIELD_NUMBER: _ClassVar[int]
    AMPLITUDE_FIELD_NUMBER: _ClassVar[int]
    PHASE_FIELD_NUMBER: _ClassVar[int]
    PHASEIQI_FIELD_NUMBER: _ClassVar[int]
    AMPLITUDEIQI_FIELD_NUMBER: _ClassVar[int]
    frequency: float
    amplitude: float
    phase: float
    phaseIQI: float
    amplitudeIQI: float
    def __init__(self, frequency: _Optional[float] = ..., amplitude: _Optional[float] = ..., phase: _Optional[float] = ..., phaseIQI: _Optional[float] = ..., amplitudeIQI: _Optional[float] = ...) -> None: ...

class Frequencies(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: _containers.RepeatedCompositeFieldContainer[ToneSpecs]
    def __init__(self, value: _Optional[_Iterable[_Union[ToneSpecs, _Mapping]]] = ...) -> None: ...

class Configuration(_message.Message):
    __slots__ = ("tones", "fluxrampFrequency", "modulationFactor")
    TONES_FIELD_NUMBER: _ClassVar[int]
    FLUXRAMPFREQUENCY_FIELD_NUMBER: _ClassVar[int]
    MODULATIONFACTOR_FIELD_NUMBER: _ClassVar[int]
    tones: Frequencies
    fluxrampFrequency: float
    modulationFactor: int
    def __init__(self, tones: _Optional[_Union[Frequencies, _Mapping]] = ..., fluxrampFrequency: _Optional[float] = ..., modulationFactor: _Optional[int] = ...) -> None: ...

class ResonatorChannel(_message.Message):
    __slots__ = ("id", "toneSpecs", "channelLocation", "resonatorFrequency")
    ID_FIELD_NUMBER: _ClassVar[int]
    TONESPECS_FIELD_NUMBER: _ClassVar[int]
    CHANNELLOCATION_FIELD_NUMBER: _ClassVar[int]
    RESONATORFREQUENCY_FIELD_NUMBER: _ClassVar[int]
    id: int
    toneSpecs: ToneSpecs
    channelLocation: ChannelLocation
    resonatorFrequency: float
    def __init__(self, id: _Optional[int] = ..., toneSpecs: _Optional[_Union[ToneSpecs, _Mapping]] = ..., channelLocation: _Optional[_Union[ChannelLocation, _Mapping]] = ..., resonatorFrequency: _Optional[float] = ...) -> None: ...

class ResonatorChannels(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: _containers.RepeatedCompositeFieldContainer[ResonatorChannel]
    def __init__(self, value: _Optional[_Iterable[_Union[ResonatorChannel, _Mapping]]] = ...) -> None: ...

class ChainIndex(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: int
    def __init__(self, value: _Optional[int] = ...) -> None: ...

class FluxrampData(_message.Message):
    __slots__ = ("frequency", "phase", "offset")
    FREQUENCY_FIELD_NUMBER: _ClassVar[int]
    PHASE_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    frequency: _containers.RepeatedScalarFieldContainer[float]
    phase: _containers.RepeatedScalarFieldContainer[float]
    offset: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, frequency: _Optional[_Iterable[float]] = ..., phase: _Optional[_Iterable[float]] = ..., offset: _Optional[_Iterable[float]] = ...) -> None: ...

class FluxrampConfiguration(_message.Message):
    __slots__ = ("data",)
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: _containers.RepeatedCompositeFieldContainer[FluxrampData]
    def __init__(self, data: _Optional[_Iterable[_Union[FluxrampData, _Mapping]]] = ...) -> None: ...

class EventConfiguration(_message.Message):
    __slots__ = ("index", "chainIndex", "threshold", "packageLength", "pretriggerValues", "activeChannels")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    CHAININDEX_FIELD_NUMBER: _ClassVar[int]
    THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    PACKAGELENGTH_FIELD_NUMBER: _ClassVar[int]
    PRETRIGGERVALUES_FIELD_NUMBER: _ClassVar[int]
    ACTIVECHANNELS_FIELD_NUMBER: _ClassVar[int]
    index: _datatypes_pb2.EndpointIndex
    chainIndex: ChainIndex
    threshold: int
    packageLength: int
    pretriggerValues: int
    activeChannels: int
    def __init__(self, index: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ..., chainIndex: _Optional[_Union[ChainIndex, _Mapping]] = ..., threshold: _Optional[int] = ..., packageLength: _Optional[int] = ..., pretriggerValues: _Optional[int] = ..., activeChannels: _Optional[int] = ...) -> None: ...
