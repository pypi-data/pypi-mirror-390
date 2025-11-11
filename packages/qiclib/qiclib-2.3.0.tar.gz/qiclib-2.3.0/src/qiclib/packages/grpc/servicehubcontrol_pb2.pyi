import qiclib.packages.grpc.datatypes_pb2 as _datatypes_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ReloadData(_message.Message):
    __slots__ = ("config", "device_tree_overlay", "bitstream", "additional_device_tree_overlays")
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    DEVICE_TREE_OVERLAY_FIELD_NUMBER: _ClassVar[int]
    BITSTREAM_FIELD_NUMBER: _ClassVar[int]
    ADDITIONAL_DEVICE_TREE_OVERLAYS_FIELD_NUMBER: _ClassVar[int]
    config: str
    device_tree_overlay: str
    bitstream: bytes
    additional_device_tree_overlays: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, config: _Optional[str] = ..., device_tree_overlay: _Optional[str] = ..., bitstream: _Optional[bytes] = ..., additional_device_tree_overlays: _Optional[_Iterable[str]] = ...) -> None: ...

class Log(_message.Message):
    __slots__ = ("name", "path", "content")
    NAME_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    name: str
    path: str
    content: str
    def __init__(self, name: _Optional[str] = ..., path: _Optional[str] = ..., content: _Optional[str] = ...) -> None: ...

class BuildPath(_message.Message):
    __slots__ = ("str",)
    STR_FIELD_NUMBER: _ClassVar[int]
    str: str
    def __init__(self, str: _Optional[str] = ...) -> None: ...

class MultiLog(_message.Message):
    __slots__ = ("log",)
    LOG_FIELD_NUMBER: _ClassVar[int]
    log: _containers.RepeatedCompositeFieldContainer[Log]
    def __init__(self, log: _Optional[_Iterable[_Union[Log, _Mapping]]] = ...) -> None: ...

class PluginInfo(_message.Message):
    __slots__ = ("plugin_name", "plugin_config")
    PLUGIN_NAME_FIELD_NUMBER: _ClassVar[int]
    PLUGIN_CONFIG_FIELD_NUMBER: _ClassVar[int]
    plugin_name: str
    plugin_config: str
    def __init__(self, plugin_name: _Optional[str] = ..., plugin_config: _Optional[str] = ...) -> None: ...

class Plugins(_message.Message):
    __slots__ = ("pi",)
    PI_FIELD_NUMBER: _ClassVar[int]
    pi: _containers.RepeatedCompositeFieldContainer[PluginInfo]
    def __init__(self, pi: _Optional[_Iterable[_Union[PluginInfo, _Mapping]]] = ...) -> None: ...

class EndpointIndexRequest(_message.Message):
    __slots__ = ("plugin_name", "endpoint_name")
    PLUGIN_NAME_FIELD_NUMBER: _ClassVar[int]
    ENDPOINT_NAME_FIELD_NUMBER: _ClassVar[int]
    plugin_name: str
    endpoint_name: str
    def __init__(self, plugin_name: _Optional[str] = ..., endpoint_name: _Optional[str] = ...) -> None: ...

class String(_message.Message):
    __slots__ = ("str",)
    STR_FIELD_NUMBER: _ClassVar[int]
    str: str
    def __init__(self, str: _Optional[str] = ...) -> None: ...

class StringVector(_message.Message):
    __slots__ = ("str",)
    STR_FIELD_NUMBER: _ClassVar[int]
    str: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, str: _Optional[_Iterable[str]] = ...) -> None: ...

class Integer(_message.Message):
    __slots__ = ("val",)
    VAL_FIELD_NUMBER: _ClassVar[int]
    val: int
    def __init__(self, val: _Optional[int] = ...) -> None: ...

class PluginVersions(_message.Message):
    __slots__ = ("driver_version", "proto_version", "common_version")
    DRIVER_VERSION_FIELD_NUMBER: _ClassVar[int]
    PROTO_VERSION_FIELD_NUMBER: _ClassVar[int]
    COMMON_VERSION_FIELD_NUMBER: _ClassVar[int]
    driver_version: str
    proto_version: str
    common_version: str
    def __init__(self, driver_version: _Optional[str] = ..., proto_version: _Optional[str] = ..., common_version: _Optional[str] = ...) -> None: ...

class ServiceHubVersions(_message.Message):
    __slots__ = ("servicehub_version", "proto_version", "common_version")
    SERVICEHUB_VERSION_FIELD_NUMBER: _ClassVar[int]
    PROTO_VERSION_FIELD_NUMBER: _ClassVar[int]
    COMMON_VERSION_FIELD_NUMBER: _ClassVar[int]
    servicehub_version: str
    proto_version: str
    common_version: str
    def __init__(self, servicehub_version: _Optional[str] = ..., proto_version: _Optional[str] = ..., common_version: _Optional[str] = ...) -> None: ...
