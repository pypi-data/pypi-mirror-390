import copy
import enum
from datetime import datetime
from enum import Enum
from typing import Optional, Any, Type

from pydantic import BaseModel, ConfigDict

from tiefeng.common.enums.enum_items import EnumItem


def convert_enum_value(v: Enum):
    print(f"convert_enum_value called with: {v}, type: {type(v)}")
    if isinstance(v, EnumItem):
        return v.value
    return v

def parse_enum_value(value: Any, enum_class: Type[Enum]) -> Enum:
    """将输入值解析为指定的枚举类型"""
    if isinstance(value, enum_class):
        return value
    # 根据value找到对应的枚举成员
    for member in enum_class:
        if isinstance(member.value, EnumItem):
            if member.value.value == value:
                return member
        elif member.value == value:
            return member
    for member in enum_class:
        if member.name == value:
            return member
    raise ValueError(f"Invalid value for {enum_class.__name__}: {value}")


def get_underlying_type(field_info):
    """获取字段的底层类型，处理 Optional、Union 等"""
    from typing import Union, get_args, get_origin

    annotation = field_info.annotation

    # 处理 Optional[T] (即 Union[T, None])
    if get_origin(annotation) is Union:
        args = get_args(annotation)
        # 移除 None 类型
        non_none_args = [arg for arg in args if arg is not type(None)]

        if len(non_none_args) == 1:
            return non_none_args[0]  # 单个非 None 类型
        elif non_none_args:
            return Union[tuple(non_none_args)]  # 多个非 None 类型
        else:
            return type(None)  # 只有 None

    # 处理其他类型
    return annotation


def datetime_serializer(dt: Optional[datetime]) -> Optional[str]:
    """将datetime对象序列化为ISO格式字符串"""
    return dt.isoformat() if dt else None


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True,
                              arbitrary_types_allowed=True,
                              use_enum_values=True,
                              json_encoders={
                                  enum.Enum: lambda v: convert_enum_value(v),
                                  datetime: datetime_serializer
                              })
    # 如果是子类且未定义model_config，则继承父类的model_config
    def __init_subclass__(cls, **kwargs):
        if not hasattr(cls, "model_config"):
            cls.model_config = copy.deepcopy(super().model_config)


class DBModelInfo(BaseSchema):
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    order_num: Optional[float] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    delete_flag: Optional[int] = None
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[int] = None

    @property
    def is_deleted(self):
        return self.delete_flag == 1