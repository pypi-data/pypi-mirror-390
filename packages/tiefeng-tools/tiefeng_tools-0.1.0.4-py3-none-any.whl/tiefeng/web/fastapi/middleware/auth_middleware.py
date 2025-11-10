from abc import ABC, abstractmethod

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from tiefeng.web.common.util import url_path_utils


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        if not await self.authenticate(request):
            ignore_paths = await self.get_ignore_paths()
            if not url_path_utils.is_path_ignored(request.url.path, ignore_paths):
                return await self.error_response()
        # 继续处理请求（进入接口函数）
        response = await call_next(request)
        return response

    async def authenticate(self, request: Request) -> bool:
        """
        验证用户是否已登录
        :param request: 请求对象
        :return: 验证结果
        """
        return True

    async def get_ignore_paths(self) -> list[str]:
        """
        获取忽略验证的路径
        :return: 忽略验证的路径列表， 可以是： ['/test/**/user/**/public.html']
        """
        return  ["/login", "/openapi/**", '/public/**', '/static/**']

    async def error_response(self) -> Response:
        """
        返回错误响应
        :return: 错误响应对象
        """
        return Response("需要认证，请先登录!", status_code=401)