"""
WebUI 中间件模块
"""
from .namespace_middleware import NamespaceMiddleware
from .api_key_middleware import APIKeyMiddleware

__all__ = ['NamespaceMiddleware', 'APIKeyMiddleware']
