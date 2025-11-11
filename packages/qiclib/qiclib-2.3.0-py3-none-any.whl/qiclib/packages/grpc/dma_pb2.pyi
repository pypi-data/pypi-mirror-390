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

class FileWriteCommand(_message.Message):
    __slots__ = ("FileName", "SubPath", "DiskType", "streamInfo")
    FILENAME_FIELD_NUMBER: _ClassVar[int]
    SUBPATH_FIELD_NUMBER: _ClassVar[int]
    DISKTYPE_FIELD_NUMBER: _ClassVar[int]
    STREAMINFO_FIELD_NUMBER: _ClassVar[int]
    FileName: str
    SubPath: str
    DiskType: DiskType
    streamInfo: StreamRequest
    def __init__(self, FileName: _Optional[str] = ..., SubPath: _Optional[str] = ..., DiskType: _Optional[_Union[DiskType, str]] = ..., streamInfo: _Optional[_Union[StreamRequest, _Mapping]] = ...) -> None: ...

class FileRequest(_message.Message):
    __slots__ = ("FileName", "SubPath", "DiskType")
    FILENAME_FIELD_NUMBER: _ClassVar[int]
    SUBPATH_FIELD_NUMBER: _ClassVar[int]
    DISKTYPE_FIELD_NUMBER: _ClassVar[int]
    FileName: str
    SubPath: str
    DiskType: DiskType
    def __init__(self, FileName: _Optional[str] = ..., SubPath: _Optional[str] = ..., DiskType: _Optional[_Union[DiskType, str]] = ...) -> None: ...

class FileContent(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: bytes
    def __init__(self, value: _Optional[bytes] = ...) -> None: ...

class StreamRequest(_message.Message):
    __slots__ = ("count", "channels", "TimeoutInMSecs")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    CHANNELS_FIELD_NUMBER: _ClassVar[int]
    TIMEOUTINMSECS_FIELD_NUMBER: _ClassVar[int]
    count: int
    channels: _containers.RepeatedScalarFieldContainer[int]
    TimeoutInMSecs: int
    def __init__(self, count: _Optional[int] = ..., channels: _Optional[_Iterable[int]] = ..., TimeoutInMSecs: _Optional[int] = ...) -> None: ...

class AcquiredData(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, value: _Optional[_Iterable[int]] = ...) -> None: ...

class PackageLossInfo(_message.Message):
    __slots__ = ("LostInHardware", "LostInSoftware")
    LOSTINHARDWARE_FIELD_NUMBER: _ClassVar[int]
    LOSTINSOFTWARE_FIELD_NUMBER: _ClassVar[int]
    LostInHardware: int
    LostInSoftware: int
    def __init__(self, LostInHardware: _Optional[int] = ..., LostInSoftware: _Optional[int] = ...) -> None: ...
