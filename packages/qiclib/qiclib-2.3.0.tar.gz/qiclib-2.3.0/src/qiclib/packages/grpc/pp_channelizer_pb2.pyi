import qiclib.packages.grpc.datatypes_pb2 as _datatypes_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class ChannelizerConfig(_message.Message):
    __slots__ = ("ppc_decimation", "ppc_bandwidth", "channel_bandwidth", "reverse_iq", "shifted", "sample_rate", "center_frequency", "bb_passband")
    PPC_DECIMATION_FIELD_NUMBER: _ClassVar[int]
    PPC_BANDWIDTH_FIELD_NUMBER: _ClassVar[int]
    CHANNEL_BANDWIDTH_FIELD_NUMBER: _ClassVar[int]
    REVERSE_IQ_FIELD_NUMBER: _ClassVar[int]
    SHIFTED_FIELD_NUMBER: _ClassVar[int]
    SAMPLE_RATE_FIELD_NUMBER: _ClassVar[int]
    CENTER_FREQUENCY_FIELD_NUMBER: _ClassVar[int]
    BB_PASSBAND_FIELD_NUMBER: _ClassVar[int]
    ppc_decimation: int
    ppc_bandwidth: float
    channel_bandwidth: float
    reverse_iq: bool
    shifted: bool
    sample_rate: float
    center_frequency: float
    bb_passband: float
    def __init__(self, ppc_decimation: _Optional[int] = ..., ppc_bandwidth: _Optional[float] = ..., channel_bandwidth: _Optional[float] = ..., reverse_iq: bool = ..., shifted: bool = ..., sample_rate: _Optional[float] = ..., center_frequency: _Optional[float] = ..., bb_passband: _Optional[float] = ...) -> None: ...
