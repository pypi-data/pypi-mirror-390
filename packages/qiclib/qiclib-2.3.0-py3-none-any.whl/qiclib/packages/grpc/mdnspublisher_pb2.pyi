import qiclib.packages.grpc.datatypes_pb2 as _datatypes_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class mdnsService(_message.Message):
    __slots__ = ("name", "type", "port", "address", "domain")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    PORT_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    DOMAIN_FIELD_NUMBER: _ClassVar[int]
    name: str
    type: str
    port: int
    address: str
    domain: str
    def __init__(self, name: _Optional[str] = ..., type: _Optional[str] = ..., port: _Optional[int] = ..., address: _Optional[str] = ..., domain: _Optional[str] = ...) -> None: ...

class mdnsServices(_message.Message):
    __slots__ = ("Service",)
    SERVICE_FIELD_NUMBER: _ClassVar[int]
    Service: _containers.RepeatedCompositeFieldContainer[mdnsService]
    def __init__(self, Service: _Optional[_Iterable[_Union[mdnsService, _Mapping]]] = ...) -> None: ...
