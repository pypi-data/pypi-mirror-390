import qiclib.packages.grpc.datatypes_pb2 as _datatypes_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class BoardInfo(_message.Message):
    __slots__ = ("coreId", "project", "buildTime")
    COREID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_FIELD_NUMBER: _ClassVar[int]
    BUILDTIME_FIELD_NUMBER: _ClassVar[int]
    coreId: int
    project: Project
    buildTime: str
    def __init__(self, coreId: _Optional[int] = ..., project: _Optional[_Union[Project, _Mapping]] = ..., buildTime: _Optional[str] = ...) -> None: ...

class Project(_message.Message):
    __slots__ = ("projectId", "platformId", "buildRevision")
    PROJECTID_FIELD_NUMBER: _ClassVar[int]
    PLATFORMID_FIELD_NUMBER: _ClassVar[int]
    BUILDREVISION_FIELD_NUMBER: _ClassVar[int]
    projectId: int
    platformId: int
    buildRevision: int
    def __init__(self, projectId: _Optional[int] = ..., platformId: _Optional[int] = ..., buildRevision: _Optional[int] = ...) -> None: ...

class PIMCStatus(_message.Message):
    __slots__ = ("rst_done", "ready", "busy")
    RST_DONE_FIELD_NUMBER: _ClassVar[int]
    READY_FIELD_NUMBER: _ClassVar[int]
    BUSY_FIELD_NUMBER: _ClassVar[int]
    rst_done: bool
    ready: bool
    busy: bool
    def __init__(self, rst_done: bool = ..., ready: bool = ..., busy: bool = ...) -> None: ...

class Info(_message.Message):
    __slots__ = ("pimcId", "pimcVersion", "projectId", "platformId", "buildRevision", "buildTime", "projectName", "platformName", "buildCommit")
    PIMCID_FIELD_NUMBER: _ClassVar[int]
    PIMCVERSION_FIELD_NUMBER: _ClassVar[int]
    PROJECTID_FIELD_NUMBER: _ClassVar[int]
    PLATFORMID_FIELD_NUMBER: _ClassVar[int]
    BUILDREVISION_FIELD_NUMBER: _ClassVar[int]
    BUILDTIME_FIELD_NUMBER: _ClassVar[int]
    PROJECTNAME_FIELD_NUMBER: _ClassVar[int]
    PLATFORMNAME_FIELD_NUMBER: _ClassVar[int]
    BUILDCOMMIT_FIELD_NUMBER: _ClassVar[int]
    pimcId: int
    pimcVersion: int
    projectId: int
    platformId: int
    buildRevision: int
    buildTime: str
    projectName: str
    platformName: str
    buildCommit: str
    def __init__(self, pimcId: _Optional[int] = ..., pimcVersion: _Optional[int] = ..., projectId: _Optional[int] = ..., platformId: _Optional[int] = ..., buildRevision: _Optional[int] = ..., buildTime: _Optional[str] = ..., projectName: _Optional[str] = ..., platformName: _Optional[str] = ..., buildCommit: _Optional[str] = ...) -> None: ...
