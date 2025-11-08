import task_pb2 as _task_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Response(_message.Message):
    __slots__ = ("ack", "nack", "result", "exception")
    ACK_FIELD_NUMBER: _ClassVar[int]
    NACK_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    EXCEPTION_FIELD_NUMBER: _ClassVar[int]
    ack: Ack
    nack: Nack
    result: _task_pb2.Result
    exception: _task_pb2.Exception
    def __init__(self, ack: _Optional[_Union[Ack, _Mapping]] = ..., nack: _Optional[_Union[Nack, _Mapping]] = ..., result: _Optional[_Union[_task_pb2.Result, _Mapping]] = ..., exception: _Optional[_Union[_task_pb2.Exception, _Mapping]] = ...) -> None: ...

class Ack(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class Nack(_message.Message):
    __slots__ = ("reason",)
    REASON_FIELD_NUMBER: _ClassVar[int]
    reason: str
    def __init__(self, reason: _Optional[str] = ...) -> None: ...

class StopRequest(_message.Message):
    __slots__ = ("timeout",)
    TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    timeout: float
    def __init__(self, timeout: _Optional[float] = ...) -> None: ...

class WorkerInfo(_message.Message):
    __slots__ = ("uid", "host", "port", "pid", "version", "tags", "extra")
    class ExtraEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    UID_FIELD_NUMBER: _ClassVar[int]
    HOST_FIELD_NUMBER: _ClassVar[int]
    PORT_FIELD_NUMBER: _ClassVar[int]
    PID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    EXTRA_FIELD_NUMBER: _ClassVar[int]
    uid: str
    host: str
    port: int
    pid: int
    version: str
    tags: _containers.RepeatedScalarFieldContainer[str]
    extra: _containers.ScalarMap[str, str]
    def __init__(self, uid: _Optional[str] = ..., host: _Optional[str] = ..., port: _Optional[int] = ..., pid: _Optional[int] = ..., version: _Optional[str] = ..., tags: _Optional[_Iterable[str]] = ..., extra: _Optional[_Mapping[str, str]] = ...) -> None: ...

class Void(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
