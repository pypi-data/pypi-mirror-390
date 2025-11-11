import qiclib.packages.grpc.datatypes_pb2 as _datatypes_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DiskType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SD: _ClassVar[DiskType]
    SSD: _ClassVar[DiskType]
    USB: _ClassVar[DiskType]
    RAMDISK: _ClassVar[DiskType]
SD: DiskType
SSD: DiskType
USB: DiskType
RAMDISK: DiskType

class StreamRequest(_message.Message):
    __slots__ = ("index", "count", "channels", "subChains", "sampleRate", "timeout", "acquisitionTime", "packageMode")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    CHANNELS_FIELD_NUMBER: _ClassVar[int]
    SUBCHAINS_FIELD_NUMBER: _ClassVar[int]
    SAMPLERATE_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    ACQUISITIONTIME_FIELD_NUMBER: _ClassVar[int]
    PACKAGEMODE_FIELD_NUMBER: _ClassVar[int]
    index: _datatypes_pb2.EndpointIndex
    count: int
    channels: _containers.RepeatedScalarFieldContainer[int]
    subChains: _containers.RepeatedScalarFieldContainer[int]
    sampleRate: float
    timeout: float
    acquisitionTime: float
    packageMode: bool
    def __init__(self, index: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ..., count: _Optional[int] = ..., channels: _Optional[_Iterable[int]] = ..., subChains: _Optional[_Iterable[int]] = ..., sampleRate: _Optional[float] = ..., timeout: _Optional[float] = ..., acquisitionTime: _Optional[float] = ..., packageMode: bool = ...) -> None: ...

class AcquiredData(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: bytes
    def __init__(self, value: _Optional[bytes] = ...) -> None: ...

class AcquiredAndMetaData(_message.Message):
    __slots__ = ("value", "data_fifo_highwatermark", "lost_samples")
    VALUE_FIELD_NUMBER: _ClassVar[int]
    DATA_FIFO_HIGHWATERMARK_FIELD_NUMBER: _ClassVar[int]
    LOST_SAMPLES_FIELD_NUMBER: _ClassVar[int]
    value: bytes
    data_fifo_highwatermark: float
    lost_samples: int
    def __init__(self, value: _Optional[bytes] = ..., data_fifo_highwatermark: _Optional[float] = ..., lost_samples: _Optional[int] = ...) -> None: ...

class FileRequest(_message.Message):
    __slots__ = ("FileName", "SubPath", "DiskType")
    FILENAME_FIELD_NUMBER: _ClassVar[int]
    SUBPATH_FIELD_NUMBER: _ClassVar[int]
    DISKTYPE_FIELD_NUMBER: _ClassVar[int]
    FileName: str
    SubPath: str
    DiskType: DiskType
    def __init__(self, FileName: _Optional[str] = ..., SubPath: _Optional[str] = ..., DiskType: _Optional[_Union[DiskType, str]] = ...) -> None: ...

class FileStreamRequest(_message.Message):
    __slots__ = ("streamrequest", "FileName", "DiskType", "SubPath")
    STREAMREQUEST_FIELD_NUMBER: _ClassVar[int]
    FILENAME_FIELD_NUMBER: _ClassVar[int]
    DISKTYPE_FIELD_NUMBER: _ClassVar[int]
    SUBPATH_FIELD_NUMBER: _ClassVar[int]
    streamrequest: StreamRequest
    FileName: str
    DiskType: DiskType
    SubPath: str
    def __init__(self, streamrequest: _Optional[_Union[StreamRequest, _Mapping]] = ..., FileName: _Optional[str] = ..., DiskType: _Optional[_Union[DiskType, str]] = ..., SubPath: _Optional[str] = ...) -> None: ...

class LostSamples(_message.Message):
    __slots__ = ("Hardware",)
    HARDWARE_FIELD_NUMBER: _ClassVar[int]
    Hardware: int
    def __init__(self, Hardware: _Optional[int] = ...) -> None: ...
