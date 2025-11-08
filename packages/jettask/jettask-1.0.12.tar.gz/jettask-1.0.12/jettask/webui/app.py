import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from jettask.webui.config import webui_config
import uvicorn

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):

    try:
        log_format = os.environ.get('JETTASK_LOG_FORMAT', 'text').lower()
        log_level = logging.INFO

        from jettask.utils.task_logger import JSONFormatter, ExtendedTextFormatter, TaskContextFilter
        import sys

        jettask_logger_names = [name for name in logging.Logger.manager.loggerDict
                                if name.startswith('jettask')]

        if not jettask_logger_names:
            jettask_logger_names = ['jettask']

        for logger_name in jettask_logger_names:
            jettask_logger = logging.getLogger(logger_name)
            jettask_logger.setLevel(log_level)

            jettask_logger.handlers.clear()

            handler = logging.StreamHandler(sys.stderr)
            handler.addFilter(TaskContextFilter())

            if log_format == 'json':
                handler.setFormatter(JSONFormatter())
            else:
                handler.setFormatter(ExtendedTextFormatter(
                    '%(asctime)s - %(levelname)s - [%(task_id)s] - %(name)s - %(message)s'
                ))

            jettask_logger.addHandler(handler)
            jettask_logger.propagate = False  

        if log_format == 'json':
            logger.info("日志格式已配置为 JSON (仅jettask相关日志)")
        else:
            logger.info("日志格式已配置为 TEXT (仅jettask相关日志)")

        db_info = webui_config.get_database_info()

        logger.info("=" * 60)
        logger.info("任务中心配置:")
        logger.info(f"  配置模式: {'Nacos' if webui_config.use_nacos else '环境变量'}")

        if db_info['host']:
            logger.info(f"  元数据库: {db_info['host']}:{db_info['port']}/{db_info['database']}")
        else:
            logger.info(f"  元数据库: {webui_config.pg_url}")

        logger.info(f"  Redis: {webui_config._mask_url(webui_config.redis_url)}")
        logger.info(f"  Redis Prefix: {webui_config.redis_prefix}")
        logger.info(f"  API服务: {webui_config.api_host}:{webui_config.api_port}")
        logger.info(f"  基础URL: {webui_config.base_url}")
        logger.info("=" * 60)

        logger.info("JetTask WebUI 启动成功")
    except Exception as e:
        logger.error(f"启动失败: {e}")
        import traceback
        traceback.print_exc()
        raise

    yield


app = FastAPI(title="Jettask Monitor", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

from jettask.webui.middleware import APIKeyMiddleware
app.add_middleware(APIKeyMiddleware)
logger.info("APIKeyMiddleware 已注册 - API密钥鉴权功能已启用")

from jettask.webui.middleware import NamespaceMiddleware
app.add_middleware(NamespaceMiddleware)
logger.info("NamespaceMiddleware 已注册 - 所有包含 {namespace} 的路由将自动注入命名空间上下文")

from jettask.webui.api import api_router
app.include_router(api_router)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    uvicorn.run(app, host="0.0.0.0", port=8000)