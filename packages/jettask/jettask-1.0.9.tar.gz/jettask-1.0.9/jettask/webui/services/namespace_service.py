"""
命名空间服务

提供命名空间的完整管理功能，包括增删改查、激活/停用、统计等
"""
import json
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy import text
from urllib.parse import urlparse

from jettask.db.connector import get_pg_engine_and_factory
from jettask.webui.config import webui_config
from jettask.schemas import (
    ConfigMode,
    NamespaceCreate,
    NamespaceUpdate,
    NamespaceResponse
)

logger = logging.getLogger(__name__)


class NamespaceService:
    """命名空间服务类 - 提供命名空间的所有管理功能"""

    @staticmethod
    def validate_redis_url(redis_url: str) -> bool:
        try:
            parsed = urlparse(redis_url)
            return parsed.scheme in ['redis', 'rediss']
        except Exception:
            return False

    @staticmethod
    def validate_pg_url(pg_url: str) -> bool:
        try:
            parsed = urlparse(pg_url)
            return parsed.scheme in ['postgresql', 'postgres', 'postgresql+asyncpg']
        except Exception:
            return False

    @staticmethod
    def mask_url_password(url: str) -> str:
        try:
            parsed = urlparse(url)
            if parsed.password:
                if parsed.username:
                    netloc = f"{parsed.username}:***@{parsed.hostname}"
                else:
                    netloc = f":***@{parsed.hostname}"

                if parsed.port:
                    netloc += f":{parsed.port}"

                masked_url = f"{parsed.scheme}://{netloc}{parsed.path}"
                if parsed.query:
                    masked_url += f"?{parsed.query}"
                if parsed.fragment:
                    masked_url += f"#{parsed.fragment}"

                return masked_url
            return url
        except Exception:
            return url

    @staticmethod
    async def get_config_from_nacos(key: str) -> str:
        try:
            from jettask.config.nacos_config import config
            value = config.config.get(key)
            if not value:
                raise ValueError(f"Nacos配置键 '{key}' 不存在或为空")
            return value
        except ImportError:
            raise ValueError("无法加载Nacos配置模块")
        except Exception as e:
            raise ValueError(f"从Nacos获取配置失败: {str(e)}")

    @staticmethod
    def _build_namespace_response(row) -> NamespaceResponse:
        redis_config_dict = row.redis_config if row.redis_config else {}
        pg_config_dict = row.pg_config if row.pg_config else {}

        redis_config_mode = redis_config_dict.get('config_mode', 'direct')
        pg_config_mode = pg_config_dict.get('config_mode', 'direct')

        if redis_config_mode == 'nacos':
            redis_url = None
            redis_nacos_key = redis_config_dict.get('nacos_key')
            logger.debug(f"命名空间 {row.name} 使用 Nacos 模式，返回 Redis key: {redis_nacos_key}")
        else:
            redis_url = redis_config_dict.get('url', '')
            redis_nacos_key = None
            logger.debug(f"命名空间 {row.name} 使用 Direct 模式，返回真实 Redis URL")

        if pg_config_mode == 'nacos':
            pg_url = None
            pg_nacos_key = pg_config_dict.get('nacos_key')
            logger.debug(f"命名空间 {row.name} 使用 Nacos 模式，返回 PG key: {pg_nacos_key}")
        else:
            pg_url = pg_config_dict.get('url')
            pg_nacos_key = None
            if pg_url:
                logger.debug(f"命名空间 {row.name} 使用 Direct 模式，返回真实 PG URL")

        return NamespaceResponse(
            name=row.name,
            description=row.description,
            redis_url=redis_url,
            redis_config_mode=redis_config_mode,
            redis_nacos_key=redis_nacos_key,
            pg_url=pg_url,
            pg_config_mode=pg_config_mode,
            pg_nacos_key=pg_nacos_key,
            connection_url=f"/api/v1/namespaces/{row.name}",
            version=row.version or 1,
            enabled=row.is_active,
            created_at=row.created_at,
            updated_at=row.updated_at
        )

    @staticmethod
    async def list_namespaces(
        page: int = 1,
        page_size: int = 20,
        is_active: Optional[bool] = None
    ) -> List[NamespaceResponse]:
        logger.info(f"列出命名空间: page={page}, page_size={page_size}, is_active={is_active}")

        _, session_factory = get_pg_engine_and_factory(webui_config.meta_database_url)
        async with session_factory() as session:
            query = """
                SELECT id, name, description, redis_config, pg_config,
                       is_active, version, created_at, updated_at
                FROM namespaces
            """
            params = {}

            if is_active is not None:
                query += " WHERE is_active = :is_active"
                params['is_active'] = is_active

            query += " ORDER BY created_at DESC"
            query += " LIMIT :limit OFFSET :offset"
            params['limit'] = page_size
            params['offset'] = (page - 1) * page_size

            result = await session.execute(text(query), params)
            rows = result.fetchall()

            namespaces = [NamespaceService._build_namespace_response(row) for row in rows]

            logger.info(f"成功获取 {len(namespaces)} 个命名空间")
            return namespaces

    @staticmethod
    async def create_namespace(namespace: NamespaceCreate) -> NamespaceResponse:
        redis_config_mode = namespace.redis_config_mode or namespace.config_mode or ConfigMode.DIRECT
        pg_config_mode = namespace.pg_config_mode or namespace.config_mode or ConfigMode.DIRECT

        logger.info(
            f"创建命名空间: {namespace.name}, "
            f"Redis模式: {redis_config_mode}, PG模式: {pg_config_mode}"
        )

        _, session_factory = get_pg_engine_and_factory(webui_config.meta_database_url)
        async with session_factory() as session:
            check_query = text("SELECT COUNT(*) FROM namespaces WHERE name = :name")
            result = await session.execute(check_query, {'name': namespace.name})
            if result.scalar() > 0:
                logger.error(f"命名空间 '{namespace.name}' 已存在")
                raise ValueError(f"命名空间 '{namespace.name}' 已存在")

            redis_config = {'config_mode': redis_config_mode.value}
            if redis_config_mode == ConfigMode.DIRECT:
                if not namespace.redis_url:
                    raise ValueError("Redis直接配置模式下，redis_url是必需的")
                if namespace.redis_nacos_key:
                    raise ValueError("Redis直接配置模式下不应提供redis_nacos_key")

                if not NamespaceService.validate_redis_url(namespace.redis_url):
                    raise ValueError("无效的Redis URL格式")

                redis_config['url'] = namespace.redis_url
                logger.debug(f"Redis URL: {NamespaceService.mask_url_password(namespace.redis_url)}")

            elif redis_config_mode == ConfigMode.NACOS:
                if not namespace.redis_nacos_key:
                    raise ValueError("Redis Nacos配置模式下，redis_nacos_key是必需的")
                if namespace.redis_url:
                    raise ValueError("Redis Nacos配置模式下不应提供redis_url")

                redis_config['nacos_key'] = namespace.redis_nacos_key
                logger.info(f"Redis Nacos模式：存储配置键 '{namespace.redis_nacos_key}'")

            pg_config = {'config_mode': pg_config_mode.value}
            if pg_config_mode == ConfigMode.DIRECT:
                if namespace.pg_url:
                    if not NamespaceService.validate_pg_url(namespace.pg_url):
                        raise ValueError("无效的PostgreSQL URL格式")
                    pg_config['url'] = namespace.pg_url
                    logger.debug(f"PG URL: {NamespaceService.mask_url_password(namespace.pg_url)}")
                if namespace.pg_nacos_key:
                    raise ValueError("PostgreSQL直接配置模式下不应提供pg_nacos_key")

            elif pg_config_mode == ConfigMode.NACOS:
                if namespace.pg_nacos_key:
                    pg_config['nacos_key'] = namespace.pg_nacos_key
                    logger.info(f"PostgreSQL Nacos模式：存储配置键 '{namespace.pg_nacos_key}'")
                if namespace.pg_url:
                    raise ValueError("PostgreSQL Nacos配置模式下不应提供pg_url")

            insert_query = text("""
                INSERT INTO namespaces (name, description, redis_config, pg_config, version)
                VALUES (:name, :description, :redis_config, :pg_config, 1)
                RETURNING id, name, description, redis_config, pg_config,
                          is_active, version, created_at, updated_at
            """)

            result = await session.execute(insert_query, {
                'name': namespace.name,
                'description': namespace.description,
                'redis_config': json.dumps(redis_config),
                'pg_config': json.dumps(pg_config)
            })

            row = result.fetchone()
            await session.commit()

            logger.info(f"成功创建命名空间: {namespace.name}")
            return NamespaceService._build_namespace_response(row)

    @staticmethod
    async def get_namespace(namespace_name: str) -> NamespaceResponse:
        logger.debug(f"获取命名空间详情: {namespace_name}")

        _, session_factory = get_pg_engine_and_factory(webui_config.meta_database_url)
        async with session_factory() as session:
            query = text("""
                SELECT id, name, description, redis_config, pg_config,
                       is_active, version, created_at, updated_at
                FROM namespaces
                WHERE name = :name
            """)

            result = await session.execute(query, {'name': namespace_name})
            row = result.fetchone()

            if not row:
                logger.error(f"命名空间 '{namespace_name}' 不存在")
                raise ValueError(f"命名空间 '{namespace_name}' 不存在")

            return NamespaceService._build_namespace_response(row)

    @staticmethod
    async def update_namespace(namespace_name: str, namespace: NamespaceUpdate) -> NamespaceResponse:
        logger.info(f"更新命名空间: {namespace_name}")

        _, session_factory = get_pg_engine_and_factory(webui_config.meta_database_url)
        async with session_factory() as session:
            check_query = text("""
                SELECT id, redis_config, pg_config FROM namespaces WHERE name = :name
            """)
            result = await session.execute(check_query, {'name': namespace_name})
            row = result.fetchone()

            if not row:
                logger.error(f"命名空间 '{namespace_name}' 不存在")
                raise ValueError(f"命名空间 '{namespace_name}' 不存在")

            current_redis_config = row.redis_config if row.redis_config else {}
            current_pg_config = row.pg_config if row.pg_config else {}

            updates = []
            params = {'name': namespace_name}

            if namespace.description is not None:
                updates.append("description = :description")
                params['description'] = namespace.description

            redis_mode = None
            pg_mode = None

            if namespace.redis_config_mode is not None:
                redis_mode = namespace.redis_config_mode
            elif namespace.config_mode is not None:
                redis_mode = namespace.config_mode

            if namespace.pg_config_mode is not None:
                pg_mode = namespace.pg_config_mode
            elif namespace.config_mode is not None:
                pg_mode = namespace.config_mode

            redis_config_updated = False
            if redis_mode is not None:
                redis_config = {'config_mode': redis_mode.value}

                if redis_mode == ConfigMode.DIRECT:
                    if namespace.redis_nacos_key:
                        raise ValueError("Redis直接配置模式下不应提供redis_nacos_key")

                    if namespace.redis_url:
                        if not NamespaceService.validate_redis_url(namespace.redis_url):
                            raise ValueError("无效的Redis URL格式")
                        redis_config['url'] = namespace.redis_url
                        logger.debug(f"更新 Redis URL: {NamespaceService.mask_url_password(namespace.redis_url)}")
                    else:
                        redis_config['url'] = current_redis_config.get('url', '')

                elif redis_mode == ConfigMode.NACOS:
                    if namespace.redis_url:
                        raise ValueError("Redis Nacos配置模式下不应提供redis_url")

                    if namespace.redis_nacos_key:
                        redis_config['nacos_key'] = namespace.redis_nacos_key
                        logger.info(f"Nacos模式：更新Redis配置键为 '{namespace.redis_nacos_key}'")
                    else:
                        if current_redis_config.get('nacos_key'):
                            redis_config['nacos_key'] = current_redis_config.get('nacos_key')

                redis_config_updated = True
            else:
                current_redis_mode = current_redis_config.get('config_mode', 'direct')

                if current_redis_mode == 'direct':
                    if namespace.redis_nacos_key:
                        raise ValueError("Redis当前为直接配置模式，不能提供redis_nacos_key")

                    if namespace.redis_url:
                        if not NamespaceService.validate_redis_url(namespace.redis_url):
                            raise ValueError("无效的Redis URL格式")
                        current_redis_config['url'] = namespace.redis_url
                        redis_config = current_redis_config
                        redis_config_updated = True
                        logger.debug(f"更新 Redis URL: {NamespaceService.mask_url_password(namespace.redis_url)}")

                else:  
                    if namespace.redis_url:
                        raise ValueError("Redis当前为Nacos配置模式，不能提供redis_url")

                    if namespace.redis_nacos_key:
                        current_redis_config['nacos_key'] = namespace.redis_nacos_key
                        redis_config = current_redis_config
                        redis_config_updated = True
                        logger.info(f"Nacos模式：更新Redis配置键为 '{namespace.redis_nacos_key}'")

            if redis_config_updated:
                updates.append("redis_config = :redis_config")
                params['redis_config'] = json.dumps(redis_config)

            pg_config_updated = False
            if pg_mode is not None:
                pg_config = {'config_mode': pg_mode.value}

                if pg_mode == ConfigMode.DIRECT:
                    if namespace.pg_nacos_key:
                        raise ValueError("PostgreSQL直接配置模式下不应提供pg_nacos_key")

                    if namespace.pg_url:
                        if not NamespaceService.validate_pg_url(namespace.pg_url):
                            raise ValueError("无效的PostgreSQL URL格式")
                        pg_config['url'] = namespace.pg_url
                        logger.debug(f"更新 PG URL: {NamespaceService.mask_url_password(namespace.pg_url)}")
                    elif current_pg_config.get('url'):
                        pg_config['url'] = current_pg_config.get('url')

                elif pg_mode == ConfigMode.NACOS:
                    if namespace.pg_url:
                        raise ValueError("PostgreSQL Nacos配置模式下不应提供pg_url")

                    if namespace.pg_nacos_key:
                        pg_config['nacos_key'] = namespace.pg_nacos_key
                        logger.info(f"Nacos模式：更新PG配置键为 '{namespace.pg_nacos_key}'")
                    else:
                        if current_pg_config.get('nacos_key'):
                            pg_config['nacos_key'] = current_pg_config.get('nacos_key')

                pg_config_updated = True
            else:
                current_pg_mode = current_pg_config.get('config_mode', 'direct')

                if current_pg_mode == 'direct':
                    if namespace.pg_nacos_key:
                        raise ValueError("PostgreSQL当前为直接配置模式，不能提供pg_nacos_key")

                    if namespace.pg_url:
                        if not NamespaceService.validate_pg_url(namespace.pg_url):
                            raise ValueError("无效的PostgreSQL URL格式")
                        current_pg_config['url'] = namespace.pg_url
                        pg_config = current_pg_config
                        pg_config_updated = True
                        logger.debug(f"更新 PG URL: {NamespaceService.mask_url_password(namespace.pg_url)}")

                else:  
                    if namespace.pg_url:
                        raise ValueError("PostgreSQL当前为Nacos配置模式，不能提供pg_url")

                    if namespace.pg_nacos_key:
                        current_pg_config['nacos_key'] = namespace.pg_nacos_key
                        pg_config = current_pg_config
                        pg_config_updated = True
                        logger.info(f"Nacos模式：更新PG配置键为 '{namespace.pg_nacos_key}'")

            if pg_config_updated:
                updates.append("pg_config = :pg_config")
                params['pg_config'] = json.dumps(pg_config)

            if namespace.enabled is not None:
                updates.append("is_active = :is_active")
                params['is_active'] = namespace.enabled

            if not updates:
                raise ValueError("没有提供要更新的字段")

            updates.append("version = version + 1")
            updates.append("updated_at = CURRENT_TIMESTAMP")

            update_query = text(f"""
                UPDATE namespaces
                SET {', '.join(updates)}
                WHERE name = :name
                RETURNING id, name, description, redis_config, pg_config,
                          is_active, version, created_at, updated_at
            """)

            result = await session.execute(update_query, params)
            updated_row = result.fetchone()
            await session.commit()

            logger.info(f"成功更新命名空间: {namespace_name}")
            return NamespaceService._build_namespace_response(updated_row)

    @staticmethod
    async def delete_namespace(namespace_name: str) -> Dict[str, str]:
        if namespace_name == 'default':
            logger.error("尝试删除默认命名空间")
            raise ValueError("不能删除默认命名空间")

        logger.info(f"删除命名空间: {namespace_name}")

        _, session_factory = get_pg_engine_and_factory(webui_config.meta_database_url)
        async with session_factory() as session:
            check_query = text("SELECT id FROM namespaces WHERE name = :name")
            result = await session.execute(check_query, {'name': namespace_name})

            if not result.fetchone():
                logger.error(f"命名空间 '{namespace_name}' 不存在")
                raise ValueError(f"命名空间 '{namespace_name}' 不存在")

            delete_query = text("DELETE FROM namespaces WHERE name = :name")
            await session.execute(delete_query, {'name': namespace_name})
            await session.commit()

            logger.info(f"成功删除命名空间: {namespace_name}")
            return {"message": f"命名空间 '{namespace_name}' 已删除"}

    @staticmethod
    async def activate_namespace(namespace_name: str) -> Dict[str, str]:
        logger.info(f"激活命名空间: {namespace_name}")

        _, session_factory = get_pg_engine_and_factory(webui_config.meta_database_url)
        async with session_factory() as session:
            update_query = text("""
                UPDATE namespaces
                SET is_active = true, updated_at = CURRENT_TIMESTAMP
                WHERE name = :name
            """)

            result = await session.execute(update_query, {'name': namespace_name})

            if result.rowcount == 0:
                logger.error(f"命名空间 '{namespace_name}' 不存在")
                raise ValueError(f"命名空间 '{namespace_name}' 不存在")

            await session.commit()

            logger.info(f"成功激活命名空间: {namespace_name}")
            return {"message": f"命名空间 '{namespace_name}' 已激活"}

    @staticmethod
    async def deactivate_namespace(namespace_name: str) -> Dict[str, str]:
        if namespace_name == 'default':
            logger.error("尝试停用默认命名空间")
            raise ValueError("不能停用默认命名空间")

        logger.info(f"停用命名空间: {namespace_name}")

        _, session_factory = get_pg_engine_and_factory(webui_config.meta_database_url)
        async with session_factory() as session:
            update_query = text("""
                UPDATE namespaces
                SET is_active = false, updated_at = CURRENT_TIMESTAMP
                WHERE name = :name
            """)

            result = await session.execute(update_query, {'name': namespace_name})

            if result.rowcount == 0:
                logger.error(f"命名空间 '{namespace_name}' 不存在")
                raise ValueError(f"命名空间 '{namespace_name}' 不存在")

            await session.commit()

            logger.info(f"成功停用命名空间: {namespace_name}")
            return {"message": f"命名空间 '{namespace_name}' 已停用"}

    @staticmethod
    async def get_namespace_statistics(namespace_name: str) -> Dict[str, Any]:
        logger.debug(f"获取命名空间统计信息: {namespace_name}")


        return {
            "success": True,
            "data": {
                "total_queues": 0,
                "total_tasks": 0,
                "active_workers": 0,
                "pending_tasks": 0,
                "processing_tasks": 0,
                "completed_tasks": 0,
                "failed_tasks": 0
            },
            "namespace": namespace_name,
            "timestamp": datetime.now().isoformat()
        }

    @staticmethod
    async def batch_activate_namespaces(namespace_names: List[str]) -> Dict[str, Any]:
        logger.info(f"批量激活命名空间: {namespace_names}")

        _, session_factory = get_pg_engine_and_factory(webui_config.meta_database_url)
        async with session_factory() as session:
            update_query = text("""
                UPDATE namespaces
                SET is_active = true, updated_at = CURRENT_TIMESTAMP
                WHERE name = ANY(:names)
            """)

            result = await session.execute(update_query, {'names': namespace_names})
            await session.commit()

            activated_count = result.rowcount
            logger.info(f"批量激活了 {activated_count} 个命名空间")

            return {
                "activated": activated_count,
                "namespaces": namespace_names[:activated_count]
            }

    @staticmethod
    async def batch_deactivate_namespaces(namespace_names: List[str]) -> Dict[str, Any]:
        logger.info(f"批量停用命名空间: {namespace_names}")

        filtered_names = [name for name in namespace_names if name != 'default']

        if not filtered_names:
            logger.warning("批量停用操作中所有命名空间都被跳过（包含 default）")
            return {
                "deactivated": 0,
                "namespaces": [],
                "skipped": ["default"]
            }

        _, session_factory = get_pg_engine_and_factory(webui_config.meta_database_url)
        async with session_factory() as session:
            update_query = text("""
                UPDATE namespaces
                SET is_active = false, updated_at = CURRENT_TIMESTAMP
                WHERE name = ANY(:names)
            """)

            result = await session.execute(update_query, {'names': filtered_names})
            await session.commit()

            deactivated_count = result.rowcount
            logger.info(f"批量停用了 {deactivated_count} 个命名空间")

            response = {
                "deactivated": deactivated_count,
                "namespaces": filtered_names[:deactivated_count]
            }

            skipped = [name for name in namespace_names if name not in filtered_names]
            if skipped:
                response["skipped"] = skipped

            return response


__all__ = ['NamespaceService']
