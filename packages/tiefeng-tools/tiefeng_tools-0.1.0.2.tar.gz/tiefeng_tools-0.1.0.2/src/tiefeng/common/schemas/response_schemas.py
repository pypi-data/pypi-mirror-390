from typing import Any, Dict, Generic, Optional, TypeVar, Union

from pydantic import BaseModel, Field, ConfigDict

from tiefeng.common.exception.error_code import ErrorCode

# 定义泛型类型变量
T = TypeVar('T')


class ApiResponse(BaseModel, Generic[T]):
    """
    统一响应模型

    Args:
        success: 是否成功
        code: 状态码
        message: 提示信息
        data: 响应数据
        details: 详细信息（通常用于错误情况）
    """
    # 添加ORM模式配置
    model_config = ConfigDict(arbitrary_types_allowed=True, from_attributes=True)

    success: bool = Field(default=True, description="是否成功")
    code: int = Field(default=ErrorCode.SUCCESS.code, description="状态码")
    message: str = Field(default="操作成功", description="提示信息")
    details: Optional[Union[Dict[str, Any], str, Any]] = Field(default=None, description="详细信息")
    data: Optional[Union[T, Any]] = Field(default=None, description="响应数据")

    @classmethod
    def success_response(cls, data: Any = None, message: str = "操作成功") -> "ApiResponse":
        """
        成功响应

        Args:
            data: 响应数据
            message: 提示信息

        Returns:
            ApiResponse: 响应模型
        """
        # 如果数据是SQLAlchemy模型实例，转换为字典
        if hasattr(data, '__table__'):  # 简单检查是否是SQLAlchemy模型
            data = {c.name: getattr(data, c.name) for c in data.__table__.columns}

        return cls(
            success=True,
            code=ErrorCode.SUCCESS.code,
            message=message,
            data=data
        )

    @classmethod
    def error_response(
            cls,
            code: ErrorCode = ErrorCode.UNKNOWN_ERROR,
            message: Optional[str] = None,
            details: Optional[Union[Dict[str, Any], str]] = None
    ) -> "ApiResponse":
        """
        错误响应

        Args:
            code: 错误码
            message: 错误信息，如果为None则使用错误码对应的默认信息
            details: 详细错误信息

        Returns:
            ApiResponse: 响应模型
        """
        return cls(
            success=False,
            code=code.code,
            message=message if message is not None else code.message,
            data=None,
            details=details
        )

    @classmethod
    def validation_error_response(
            cls,
            field: str,
            value: Any,
            message: str = "数据验证错误，请检查数据"
    ) -> "ApiResponse":
        """
        验证错误响应

        Args:
            field: 错误字段
            value: 错误值
            message: 错误信息

        Returns:
            ApiResponse: 响应模型
        """
        return cls(
            success=False,
            code=ErrorCode.VALIDATION_ERROR.code,
            message=message,
            data=None,
            details={
                "field": field,
                "value": value
            }
        )