import qiclib.packages.grpc.datatypes_pb2 as _datatypes_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ProtocolDriversMap(_message.Message):
    __slots__ = ("entries",)
    class ProtocolDriversEntry(_message.Message):
        __slots__ = ("protocol", "drivers")
        PROTOCOL_FIELD_NUMBER: _ClassVar[int]
        DRIVERS_FIELD_NUMBER: _ClassVar[int]
        protocol: str
        drivers: _containers.RepeatedScalarFieldContainer[str]
        def __init__(self, protocol: _Optional[str] = ..., drivers: _Optional[_Iterable[str]] = ...) -> None: ...
    ENTRIES_FIELD_NUMBER: _ClassVar[int]
    entries: _containers.RepeatedCompositeFieldContainer[ProtocolDriversMap.ProtocolDriversEntry]
    def __init__(self, entries: _Optional[_Iterable[_Union[ProtocolDriversMap.ProtocolDriversEntry, _Mapping]]] = ...) -> None: ...
