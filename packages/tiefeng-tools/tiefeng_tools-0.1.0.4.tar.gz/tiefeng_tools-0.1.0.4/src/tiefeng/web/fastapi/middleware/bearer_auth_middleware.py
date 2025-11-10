from abc import ABC, abstractmethod

from starlette.requests import Request

from tiefeng.web.fastapi.middleware.auth_middleware import AuthMiddleware


class BearerAuthMiddleware(AuthMiddleware, ABC):
    """

    """
    async def authenticate(self, request: Request) -> bool:
        # 1. 从请求中获取token（示例：从headers中获取）
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            return  False
        request.state.token = token
        # 2、通过token获取用户信息
        user = await self.get_current_user(token)
        if not user:
            return  False
        # 3、将用户信息存入请求上下文（request.state）
        request.state.user = user
        return True


    @abstractmethod
    async def get_current_user(self, token: str):
        """
        从token中获取用户信息
        :param token:
        :return:
        """
        pass