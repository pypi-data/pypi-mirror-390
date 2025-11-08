"""
API密钥鉴权中间件
"""
import logging
import os
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)


class APIKeyMiddleware(BaseHTTPMiddleware):
    """API密钥鉴权中间件

    检查请求头中的 X-API-Key 是否与配置的API密钥匹配。
    如果配置了API密钥但请求未提供或不匹配,则返回401错误。
    如果未配置API密钥,则跳过鉴权。
    """

    def __init__(self, app, api_key: str = None):
        super().__init__(app)
        self.api_key = api_key or os.environ.get('JETTASK_API_KEY')

        if self.api_key:
            logger.info("API密钥鉴权已启用")
        else:
            logger.info("API密钥鉴权未启用 - 所有请求无需鉴权")

    async def dispatch(self, request: Request, call_next):
        if not self.api_key:
            return await call_next(request)

        request_api_key = request.headers.get('X-API-Key')

        if not request_api_key:
            logger.warning(f"请求未提供API密钥: {request.url.path} from {request.client.host if request.client else 'unknown'}")
            return JSONResponse(
                status_code=401,
                content={
                    "error": "Unauthorized",
                    "message": "缺少API密钥,请在请求头中提供 X-API-Key"
                }
            )

        if request_api_key != self.api_key:
            logger.warning(f"API密钥验证失败: {request.url.path} from {request.client.host if request.client else 'unknown'}")
            return JSONResponse(
                status_code=401,
                content={
                    "error": "Unauthorized",
                    "message": "API密钥无效"
                }
            )

        logger.debug(f"API密钥验证通过: {request.url.path}")
        return await call_next(request)
