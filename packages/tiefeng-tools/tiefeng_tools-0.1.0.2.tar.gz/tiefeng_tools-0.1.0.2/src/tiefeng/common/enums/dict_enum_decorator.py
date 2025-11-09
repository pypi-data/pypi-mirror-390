"""
字典枚举装饰器
"""
from typing import Type, Callable

from tiefeng.common.enums.enum_items import BaseEnum

# 存储枚举类的映射（键：枚举类名，值：枚举类）
DICT_ENUM_MAP = {}


def dict_enum(value: str | Type[BaseEnum]) -> Callable[[type[BaseEnum]], type[BaseEnum]] | type[BaseEnum]:
    """支持可选自定义名称的装饰器：不传参则用类名作为键"""
    def enum_decorator(cls: Type[BaseEnum]) -> Type[BaseEnum]:
        if not issubclass(cls, BaseEnum):
            raise TypeError(f"装饰器 'dict_enum' 仅支持 BaseEnum 的子类，当前类型：{type(cls)}")

        # 若未传自定义名称，则使用枚举类自身的 __name__ 作为键
        key = value if value else cls.__name__
        DICT_ENUM_MAP[key] = cls
        return cls
    if isinstance(value, str):
        return enum_decorator
    return enum_decorator(value)


def get_dict_enum(code: str) -> Type[BaseEnum] | None:
    """获取注册的枚举类（根据类名）"""
    return DICT_ENUM_MAP.get(code)