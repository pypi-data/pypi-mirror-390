from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CostType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    COST_TYPE_UNSPECIFIED: _ClassVar[CostType]
    COST_TYPE_TOKEN_INPUT: _ClassVar[CostType]
    COST_TYPE_TOKEN_OUTPUT: _ClassVar[CostType]
    COST_TYPE_API_CALL: _ClassVar[CostType]
    COST_TYPE_STORAGE: _ClassVar[CostType]
    COST_TYPE_TIME: _ClassVar[CostType]
COST_TYPE_UNSPECIFIED: CostType
COST_TYPE_TOKEN_INPUT: CostType
COST_TYPE_TOKEN_OUTPUT: CostType
COST_TYPE_API_CALL: CostType
COST_TYPE_STORAGE: CostType
COST_TYPE_TIME: CostType

class Cost(_message.Message):
    __slots__ = ()
    COST_FIELD_NUMBER: _ClassVar[int]
    MISSION_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    UNIT_FIELD_NUMBER: _ClassVar[int]
    cost: float
    mission_id: str
    name: str
    type: CostType
    unit: str
    def __init__(self, cost: _Optional[float] = ..., mission_id: _Optional[str] = ..., name: _Optional[str] = ..., type: _Optional[_Union[CostType, str]] = ..., unit: _Optional[str] = ...) -> None: ...

class AddCostRequest(_message.Message):
    __slots__ = ()
    COST_FIELD_NUMBER: _ClassVar[int]
    MISSION_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    UNIT_FIELD_NUMBER: _ClassVar[int]
    cost: float
    mission_id: str
    name: str
    type: CostType
    unit: str
    def __init__(self, cost: _Optional[float] = ..., mission_id: _Optional[str] = ..., name: _Optional[str] = ..., type: _Optional[_Union[CostType, str]] = ..., unit: _Optional[str] = ...) -> None: ...

class AddCostResponse(_message.Message):
    __slots__ = ()
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: _Optional[bool] = ...) -> None: ...

class GetCostsByMissionRequest(_message.Message):
    __slots__ = ()
    MISSION_ID_FIELD_NUMBER: _ClassVar[int]
    mission_id: str
    def __init__(self, mission_id: _Optional[str] = ...) -> None: ...

class GetCostsByMissionResponse(_message.Message):
    __slots__ = ()
    COSTS_FIELD_NUMBER: _ClassVar[int]
    costs: _containers.RepeatedCompositeFieldContainer[Cost]
    def __init__(self, costs: _Optional[_Iterable[_Union[Cost, _Mapping]]] = ...) -> None: ...

class GetCostsByNameRequest(_message.Message):
    __slots__ = ()
    MISSION_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    mission_id: str
    name: str
    def __init__(self, mission_id: _Optional[str] = ..., name: _Optional[str] = ...) -> None: ...

class GetCostsByNameResponse(_message.Message):
    __slots__ = ()
    COSTS_FIELD_NUMBER: _ClassVar[int]
    costs: _containers.RepeatedCompositeFieldContainer[Cost]
    def __init__(self, costs: _Optional[_Iterable[_Union[Cost, _Mapping]]] = ...) -> None: ...

class GetCostsByTypeRequest(_message.Message):
    __slots__ = ()
    MISSION_ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    mission_id: str
    type: CostType
    def __init__(self, mission_id: _Optional[str] = ..., type: _Optional[_Union[CostType, str]] = ...) -> None: ...

class GetCostsByTypeResponse(_message.Message):
    __slots__ = ()
    COSTS_FIELD_NUMBER: _ClassVar[int]
    costs: _containers.RepeatedCompositeFieldContainer[Cost]
    def __init__(self, costs: _Optional[_Iterable[_Union[Cost, _Mapping]]] = ...) -> None: ...
