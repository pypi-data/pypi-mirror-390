import enum
from typing import Optional, Any, Union, List, Dict

from pydantic import BaseModel, Field


class EnumItem(BaseModel):
    """枚举项"""
    label: str = Field(default=None, title='枚举标题')
    value: Union[str, int, float] = Field(default=None, title='枚举值')
    description: Optional[str] = Field(default=None, title='枚举描述')
    ext_data: Optional[dict[str, Any]] = Field(title='额外数据', default=dict())


class BaseEnum:
    """基础枚举类"""
    @classmethod
    def get_enum(cls: type[enum.Enum], value: Union[str, int, float]):
        """根据值获取枚举项"""
        for item in cls:
            if item.value.value == value:
                return item
        return None

    @classmethod
    def get_enum_by_label(cls: type[enum.Enum], label: str):
        """根据标签获取枚举项"""
        for item in cls:
            if item.value.label == label:
                return item
        return None

    @classmethod
    def get_enum_value_list(cls: type[enum.Enum]) -> List[Dict[str, Any]]:
        """获取所有枚举项的列表"""
        return [item.value.model_dump() for item in cls]

    @classmethod
    def get_enum_list(cls: type[enum.Enum]) -> List:
        """获取所有枚举成员的列表"""
        return [item for item in cls]

