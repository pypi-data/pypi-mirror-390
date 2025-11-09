from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Task(_message.Message):
    __slots__ = ("id", "callable", "args", "kwargs", "caller", "proxy", "proxy_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    CALLABLE_FIELD_NUMBER: _ClassVar[int]
    ARGS_FIELD_NUMBER: _ClassVar[int]
    KWARGS_FIELD_NUMBER: _ClassVar[int]
    CALLER_FIELD_NUMBER: _ClassVar[int]
    PROXY_FIELD_NUMBER: _ClassVar[int]
    PROXY_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    callable: bytes
    args: bytes
    kwargs: bytes
    caller: str
    proxy: bytes
    proxy_id: str
    def __init__(self, id: _Optional[str] = ..., callable: _Optional[bytes] = ..., args: _Optional[bytes] = ..., kwargs: _Optional[bytes] = ..., caller: _Optional[str] = ..., proxy: _Optional[bytes] = ..., proxy_id: _Optional[str] = ...) -> None: ...

class Result(_message.Message):
    __slots__ = ("dump",)
    DUMP_FIELD_NUMBER: _ClassVar[int]
    dump: bytes
    def __init__(self, dump: _Optional[bytes] = ...) -> None: ...

class Exception(_message.Message):
    __slots__ = ("dump",)
    DUMP_FIELD_NUMBER: _ClassVar[int]
    dump: bytes
    def __init__(self, dump: _Optional[bytes] = ...) -> None: ...

class Worker(_message.Message):
    __slots__ = ("id", "address")
    ID_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    id: str
    address: str
    def __init__(self, id: _Optional[str] = ..., address: _Optional[str] = ...) -> None: ...
