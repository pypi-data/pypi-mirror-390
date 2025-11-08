from nominal.ai.v1 import ai_agent_pb2 as _ai_agent_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class WorkbookAgentServiceStreamChatRequest(_message.Message):
    __slots__ = ("messages", "notebook_as_json", "selected_tab_index", "images", "range", "message")
    MESSAGES_FIELD_NUMBER: _ClassVar[int]
    NOTEBOOK_AS_JSON_FIELD_NUMBER: _ClassVar[int]
    SELECTED_TAB_INDEX_FIELD_NUMBER: _ClassVar[int]
    IMAGES_FIELD_NUMBER: _ClassVar[int]
    RANGE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    messages: _containers.RepeatedCompositeFieldContainer[_ai_agent_pb2.ModelMessage]
    notebook_as_json: str
    selected_tab_index: int
    images: _containers.RepeatedCompositeFieldContainer[_ai_agent_pb2.ImagePart]
    range: _ai_agent_pb2.TimeRange
    message: AppendMessage
    def __init__(self, messages: _Optional[_Iterable[_Union[_ai_agent_pb2.ModelMessage, _Mapping]]] = ..., notebook_as_json: _Optional[str] = ..., selected_tab_index: _Optional[int] = ..., images: _Optional[_Iterable[_Union[_ai_agent_pb2.ImagePart, _Mapping]]] = ..., range: _Optional[_Union[_ai_agent_pb2.TimeRange, _Mapping]] = ..., message: _Optional[_Union[AppendMessage, _Mapping]] = ...) -> None: ...

class AppendMessage(_message.Message):
    __slots__ = ("message", "conversation_rid")
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    CONVERSATION_RID_FIELD_NUMBER: _ClassVar[int]
    message: _ai_agent_pb2.UserModelMessage
    conversation_rid: str
    def __init__(self, message: _Optional[_Union[_ai_agent_pb2.UserModelMessage, _Mapping]] = ..., conversation_rid: _Optional[str] = ...) -> None: ...
