from fastapi import Request, HTTPException


async def get_current_user(request: Request, is_need_auth: bool = True):
    """从当前请求上下文获取用户信息"""
    if hasattr(request.state, "user"):
        return request.state.user

    if is_need_auth:
        raise HTTPException(status_code=401, detail="需要认证，请先登录!")
    return None



