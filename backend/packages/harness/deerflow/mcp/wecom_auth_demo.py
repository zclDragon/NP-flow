from typing import Any


def build_wecom_userid_interceptor():
    async def interceptor(request: Any, handler: Any) -> Any:
        return await handler(request)

    return interceptor
