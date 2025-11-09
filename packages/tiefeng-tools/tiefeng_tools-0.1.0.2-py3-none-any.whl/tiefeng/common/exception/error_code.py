from enum import Enum


class ErrorCode(tuple[int, str], Enum):
    """错误码枚举
    错误码规则：共6位数字，结构为 XX YYY Z
        - XX: 业务域标识（前两位，10-99）
            - 10: 通用错误
            - 11: 权限和认证错误
        - YYY: 类似HTTP的响应码（中间三位）
        - Z: 细分编号（最后一位），表示该响应码下的具体分类
    """
    SUCCESS = (0, "操作成功")  # 成功
    UNKNOWN_ERROR = (105000, "服务出现未知错误，请稍后重试")  # 未知错误（对应500）
    PARAM_ERROR = (104000, "参数错误，请检查参数是否正确")  # 参数错误（对应400）
    DUPLICATE_DATA = (104090, "数据已存在，请检查数据是否已存在")  # 数据已存在（对应409）
    VALIDATION_ERROR = (104220, "数据验证错误，请检查数据是否正确")  # 数据验证错误（对应422）
    NOT_FOUND = (104040, "资源不存在，请检查资源是否存在")  # 资源不存在（对应404）
    METHOD_NOT_ALLOWED = (104050, "方法不允许，请检查请求方法是否正确")  # 方法不允许（对应405）
    REQUEST_TIMEOUT = (104080, "请求超时，请稍后重试")  # 请求超时（对应408）
    SERVER_ERROR = (105000, "服务器内部错误，请联系管理员")  # 服务器内部错误（对应500）
    SERVICE_UNAVAILABLE = (105030, "服务暂时不可用，请稍后重试")  # 服务暂时不可用（对应503）

    # 用户相关错误 (11 YYY Z)
    USER_NOT_FOUND = (114040, "用户不存在，请检查用户名")  # 用户不存在（对应404-0）
    USER_ALREADY_EXISTS = (114090, "用户已存在，请检查用户名")  # 用户已存在（对应409-0）

    # 认证相关错误（11 401 Z）
    PASSWORD_ERROR = (114011, "密码错误，请检查密码")  # 密码错误（401-1）
    LOGIN_ERROR = (114012, "登录失败，请检查用户名和密码")  # 登录失败（401-2）
    TOKEN_INVALID = (114013, "令牌无效，请重新登录")  #  # 令牌无效（401-3）
    TOKEN_EXPIRED = (114014, "令牌已过期，请重新登录")  # 令牌过期（401-4）
    TOKEN_REVOKED = (114015, "令牌已被撤销，请重新登录")  #  # 令牌已被撤销（401-5）
    AUTHENTICATION_REQUIRED =  (114016, "需要认证，请先登录")  # 需要认证（401-6）

    # 权限相关错误（11 403 Z）
    PERMISSION_DENIED = (114031, "权限不足，无法执行此操作")  # 权限不足（403-0）
    ACCOUNT_DISABLED = (114032, "账户已禁用，请联系管理员")  # 账户已禁用（403-1）
    ACCESS_DENIED = (114033, "访问被拒绝，请联系管理员")  # 访问被拒绝（403-2）

    @property
    def message(self) -> str:
        """获取错误信息"""
        return self.value[1]

    @property
    def code(self) -> int:
        """获取错误码"""
        return self.value[0]


    @property
    def http_status(self) -> int:
        """获取对应的HTTP状态码"""
        code = self.value[0]
        if code == 0:
            return 200
        # 提取中间三位作为HTTP状态码
        return int(str(code).zfill(6)[2:5])

    @property
    def business_domain(self) -> int:
        """获取业务域标识"""
        code = self.value[0]
        if code == 0:
            return 0
        # 提取前两位作为业务域标识
        return int(str(code).zfill(6)[:2])

    @property
    def sub_code(self) -> int:
        """获取细分编号"""
        code = self.value[0]
        if code == 0:
            return 0
        # 提取最后一位作为细分编号
        return int(str(code).zfill(6)[5:6])


