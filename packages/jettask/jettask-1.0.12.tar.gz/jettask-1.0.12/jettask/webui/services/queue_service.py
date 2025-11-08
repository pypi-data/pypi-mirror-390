"""
队列服务层
处理队列相关的业务逻辑
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta, timezone
from sqlalchemy import text, select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
import logging
import traceback

from jettask.db.models.task import Task
from jettask.db.models.task_run import TaskRun

logger = logging.getLogger(__name__)


class QueueService:
    """队列服务类"""
    
    @staticmethod
    def get_base_queue_name(queue_name: str) -> str:
        if ':' in queue_name:
            parts = queue_name.rsplit(':', 1)
            if parts[-1].isdigit():
                return parts[0]
        return queue_name
    
    @staticmethod
    async def get_queues_by_namespace(namespace_data_access, namespace: str) -> Dict[str, Any]:
        queues_data = await namespace_data_access.get_queue_stats(namespace)
        return {
            "success": True,
            "data": list(set([QueueService.get_base_queue_name(q['queue_name']) for q in queues_data]))
        }
    
    @staticmethod
    async def get_queue_flow_rates(data_access, query) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        
        if query.start_time and query.end_time:
            start_time = query.start_time
            end_time = query.end_time
            logger.info(f"使用自定义时间范围: {start_time} 到 {end_time}")
        else:
            time_range_map = {
                "15m": timedelta(minutes=15),
                "30m": timedelta(minutes=30),
                "1h": timedelta(hours=1),
                "3h": timedelta(hours=3),
                "6h": timedelta(hours=6),
                "12h": timedelta(hours=12),
                "24h": timedelta(hours=24),
                "7d": timedelta(days=7),
                "30d": timedelta(days=30),
            }
            
            time_range_value = query.time_range if query.time_range else query.interval
            delta = time_range_map.get(time_range_value, timedelta(minutes=15))
            
            queue_name = query.queues[0] if query.queues else None
            if queue_name:
                latest_time = await data_access.get_latest_task_time(queue_name)
                if latest_time:
                    end_time = latest_time.replace(second=59, microsecond=999999)  
                    logger.info(f"使用最新任务时间: {latest_time}")
                else:
                    end_time = now.replace(second=0, microsecond=0)
            else:
                end_time = now.replace(second=0, microsecond=0)
            
            start_time = end_time - delta
            logger.info(f"使用预设时间范围 {time_range_value}: {start_time} 到 {end_time}, delta: {delta}")
        
        if not query.queues or len(query.queues) == 0:
            return {"data": [], "granularity": "minute"}
        
        queue_name = query.queues[0]
        filters = getattr(query, 'filters', None)
        data, granularity = await data_access.fetch_queue_flow_rates(
            queue_name, start_time, end_time, filters
        )
        
        return {"data": data, "granularity": granularity}
    
    @staticmethod
    async def get_global_stats(data_access) -> Dict[str, Any]:
        stats_data = await data_access.fetch_global_stats()
        return {
            "success": True,
            "data": stats_data
        }
    
    @staticmethod
    async def get_queues_detail(data_access) -> Dict[str, Any]:
        queues_data = await data_access.fetch_queues_data()
        return {
            "success": True,
            "data": queues_data
        }
    
    @staticmethod
    async def delete_queue(queue_name: str) -> Dict[str, Any]:
        logger.info(f"删除队列请求: {queue_name}")
        return {
            "success": True,
            "message": f"队列 {queue_name} 已删除"
        }
    
    @staticmethod
    async def trim_queue(queue_name: str, max_length: int) -> Dict[str, Any]:
        logger.info(f"裁剪队列请求: {queue_name}, 保留 {max_length} 条消息")
        return {
            "success": True,
            "message": f"队列 {queue_name} 已裁剪至 {max_length} 条消息"
        }
    
    @staticmethod
    async def get_queue_stats_v2(
        namespace_data_access,
        namespace: str,
        queue: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        time_range: Optional[str] = None
    ) -> Dict[str, Any]:
        conn = await namespace_data_access.manager.get_connection(namespace)
        
        redis_client = await conn.get_redis_client(decode=False)
        
        pg_session = None
        if conn.AsyncSessionLocal:
            pg_session = conn.AsyncSessionLocal()
        
        try:
            from jettask.webui.services.queue_stats_v2 import QueueStatsV2
            
            stats_service = QueueStatsV2(
                redis_client=redis_client,
                pg_session=pg_session,
                redis_prefix=conn.redis_prefix
            )
            
            time_filter = None
            if time_range or start_time or end_time:
                time_filter = {}
                
                if time_range and time_range != 'custom':
                    now = datetime.now(timezone.utc)
                    if time_range.endswith('m'):
                        minutes = int(time_range[:-1])
                        time_filter['start_time'] = now - timedelta(minutes=minutes)
                        time_filter['end_time'] = now
                    elif time_range.endswith('h'):
                        hours = int(time_range[:-1])
                        time_filter['start_time'] = now - timedelta(hours=hours)
                        time_filter['end_time'] = now
                    elif time_range.endswith('d'):
                        days = int(time_range[:-1])
                        time_filter['start_time'] = now - timedelta(days=days)
                        time_filter['end_time'] = now
                else:
                    if start_time:
                        time_filter['start_time'] = start_time
                    if end_time:
                        time_filter['end_time'] = end_time
            
            stats = await stats_service.get_queue_stats_grouped(time_filter)
            
            if queue:
                stats = [s for s in stats if s['queue_name'] == queue]
            
            return {
                "success": True,
                "data": stats
            }
            
        finally:
            if pg_session:
                await pg_session.close()
            await redis_client.aclose()
    
    @staticmethod
    async def get_tasks_v2(namespace_data_access, namespace: str, body: Dict[str, Any]) -> Dict[str, Any]:
        from sqlalchemy import text
        from datetime import datetime, timezone, timedelta
        
        queue_name = body.get('queue_name')
        page = body.get('page', 1)
        page_size = body.get('page_size', 20)
        filters = body.get('filters', [])
        time_range = body.get('time_range', '1h')
        start_time = body.get('start_time')
        end_time = body.get('end_time')
        sort_field = body.get('sort_field', 'created_at')
        sort_order = body.get('sort_order', 'desc')
        
        if not queue_name:
            raise ValueError("queue_name is required")
        
        conn = await namespace_data_access.manager.get_connection(namespace)
        
        if not conn.pg_config or not conn.async_engine:
            return {
                "success": True,
                "data": [],
                "total": 0
            }
        
        if start_time and end_time:
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        else:
            end_dt = datetime.now(timezone.utc)
            time_deltas = {
                '15m': timedelta(minutes=15),
                '30m': timedelta(minutes=30),
                '1h': timedelta(hours=1),
                '3h': timedelta(hours=3),
                '6h': timedelta(hours=6),
                '12h': timedelta(hours=12),
                '1d': timedelta(days=1),
                '3d': timedelta(days=3),
                '7d': timedelta(days=7),
                '30d': timedelta(days=30)
            }
            delta = time_deltas.get(time_range, timedelta(hours=1))
            start_dt = end_dt - delta
        
        offset = (page - 1) * page_size
        
        async with conn.async_engine.begin() as pg_conn:
            conditions = [
                "t.namespace = :namespace",
                "t.queue = :queue",
                "t.created_at >= :start_time",
                "t.created_at <= :end_time"
            ]
            query_params = {
                "namespace": namespace,
                "queue": queue_name,
                "start_time": start_dt,
                "end_time": end_dt,
                "limit": page_size,
                "offset": offset
            }
            
            for i, filter_item in enumerate(filters):
                field = filter_item.get('field')
                operator = filter_item.get('operator')
                value = filter_item.get('value')
                
                if field and operator and value is not None:
                    param_key = f"filter_{i}"
                    
                    db_field_map = {
                        'id': 't.stream_id',
                        'task_name': "t.payload::jsonb->'event_data'->>'__task_name'",
                        'status': "t.payload::jsonb->>'status'",
                        'worker_id': "t.payload::jsonb->>'worker_id'",
                        'scheduled_task_id': 't.scheduled_task_id'
                    }
                    
                    db_field = db_field_map.get(field, f't.{field}')
                    
                    if operator == 'eq':
                        conditions.append(f"{db_field} = :{param_key}")
                        query_params[param_key] = value
                    elif operator == 'contains':
                        conditions.append(f"{db_field} LIKE :{param_key}")
                        query_params[param_key] = f"%{value}%"
                    elif operator == 'gt':
                        conditions.append(f"{db_field} > :{param_key}")
                        query_params[param_key] = value
                    elif operator == 'lt':
                        conditions.append(f"{db_field} < :{param_key}")
                        query_params[param_key] = value
            
            where_clause = " AND ".join(conditions)
            
            count_query = f"""
                SELECT COUNT(*) as total 
                FROM tasks t
                WHERE {where_clause}
            """
            count_result = await pg_conn.execute(text(count_query), query_params)
            total = count_result.fetchone().total
            
            sort_map = {
                'created_at': 't.created_at',
                'started_at': 't.started_at',
                'completed_at': 't.completed_at'
            }
            order_by = sort_map.get(sort_field, 't.created_at')
            order_direction = 'DESC' if sort_order == 'desc' else 'ASC'
            
            query = f"""
                SELECT 
                    t.stream_id as id,
                    t.payload::jsonb->'event_data'->>'__task_name' as task_name,
                    t.queue,
                    t.payload::jsonb->>'status' as status,
                    t.priority,
                    COALESCE((t.payload::jsonb->>'retry_count')::int, 0) as retry_count,
                    COALESCE((t.payload::jsonb->>'max_retry')::int, 3) as max_retry,
                    t.created_at,
                    (t.payload::jsonb->>'started_at')::timestamptz as started_at,
                    (t.payload::jsonb->>'completed_at')::timestamptz as completed_at,
                    t.payload::jsonb->>'worker_id' as worker_id,
                    t.payload::jsonb->>'error_message' as error_message,
                    (t.payload::jsonb->>'execution_time')::float as execution_time,
                    CASE 
                        WHEN t.payload::jsonb->>'completed_at' IS NOT NULL AND t.created_at IS NOT NULL 
                        THEN EXTRACT(EPOCH FROM ((t.payload::jsonb->>'completed_at')::timestamptz - t.created_at))
                        ELSE NULL 
                    END as duration,
                    t.scheduled_task_id,
                    t.source,
                    t.metadata
                FROM tasks t
                WHERE {where_clause}
                ORDER BY {order_by} {order_direction}
                LIMIT :limit OFFSET :offset
            """
            
            result = await pg_conn.execute(text(query), query_params)
            
            tasks = []
            for row in result:
                tasks.append({
                    "id": row.id,
                    "task_name": row.task_name or "unknown",
                    "queue": row.queue,
                    "status": row.status,
                    "priority": row.priority,
                    "retry_count": row.retry_count,
                    "max_retry": row.max_retry,
                    "created_at": row.created_at.isoformat() if row.created_at else None,
                    "started_at": row.started_at.isoformat() if row.started_at else None,
                    "completed_at": row.completed_at.isoformat() if row.completed_at else None,
                    "duration": round(row.duration, 2) if row.duration else None,
                    "execution_time": float(row.execution_time) if row.execution_time else None,
                    "worker_id": row.worker_id,
                    "error_message": row.error_message
                })
            
            return {
                "success": True,
                "data": tasks,
                "total": total
            }
    
    @staticmethod
    async def get_consumer_group_stats(namespace_data_access, namespace: str, group_name: str) -> Dict[str, Any]:
        conn = await namespace_data_access.manager.get_connection(namespace)
        
        if not conn.AsyncSessionLocal:
            raise ValueError("PostgreSQL not configured for this namespace")
        
        async with conn.AsyncSessionLocal() as session:
            query = text("""
                WITH group_stats AS (
                    SELECT 
                        tr.consumer_group,
                        tr.task_name,
                        COUNT(*) as total_tasks,
                        COUNT(CASE WHEN tr.status = 'success' THEN 1 END) as success_count,
                        COUNT(CASE WHEN tr.status = 'failed' THEN 1 END) as failed_count,
                        COUNT(CASE WHEN tr.status = 'running' THEN 1 END) as running_count,
                        AVG(tr.execution_time) as avg_execution_time,
                        MIN(tr.execution_time) as min_execution_time,
                        MAX(tr.execution_time) as max_execution_time,
                        AVG(tr.duration) as avg_duration,
                        MIN(tr.started_at) as first_task_time,
                        MAX(tr.completed_at) as last_task_time
                    FROM task_runs tr
                    WHERE tr.consumer_group = :group_name
                        AND tr.started_at > NOW() - INTERVAL '24 hours'
                    GROUP BY tr.consumer_group, tr.task_name
                ),
                hourly_stats AS (
                    SELECT 
                        DATE_TRUNC('hour', tr.started_at) as hour,
                        COUNT(*) as task_count,
                        AVG(tr.execution_time) as avg_exec_time
                    FROM task_runs tr
                    WHERE tr.consumer_group = :group_name
                        AND tr.started_at > NOW() - INTERVAL '24 hours'
                    GROUP BY DATE_TRUNC('hour', tr.started_at)
                    ORDER BY hour
                )
                SELECT 
                    (SELECT row_to_json(gs) FROM group_stats gs) as summary,
                    (SELECT json_agg(hs) FROM hourly_stats hs) as hourly_trend
            """)
            
            result = await session.execute(query, {'group_name': group_name})
            row = result.fetchone()
            
            if not row or not row.summary:
                return {
                    "success": True,
                    "data": {
                        "group_name": group_name,
                        "summary": {},
                        "hourly_trend": []
                    }
                }
            
            return {
                "success": True,
                "data": {
                    "group_name": group_name,
                    "summary": row.summary,
                    "hourly_trend": row.hourly_trend or []
                }
            }
    
    @staticmethod
    async def get_stream_backlog(
        data_access,
        namespace: str,
        stream_name: Optional[str] = None,
        hours: int = 24
    ) -> Dict[str, Any]:
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=hours)
        
        async with data_access.AsyncSessionLocal() as session:
            if stream_name:
                query = text("""
                    SELECT 
                        stream_name,
                        consumer_group,
                        last_published_offset,
                        last_delivered_offset,
                        last_acked_offset,
                        pending_count,
                        backlog_undelivered,
                        backlog_unprocessed,
                        created_at
                    FROM stream_backlog_monitor
                    WHERE namespace = :namespace
                        AND stream_name = :stream_name
                        AND created_at >= :start_time
                        AND created_at <= :end_time
                    ORDER BY created_at DESC
                    LIMIT 1000
                """)
                params = {
                    'namespace': namespace,
                    'stream_name': stream_name,
                    'start_time': start_time,
                    'end_time': end_time
                }
            else:
                query = text("""
                    SELECT DISTINCT ON (stream_name, consumer_group)
                        stream_name,
                        consumer_group,
                        last_published_offset,
                        last_delivered_offset,
                        last_acked_offset,
                        pending_count,
                        backlog_undelivered,
                        backlog_unprocessed,
                        created_at
                    FROM stream_backlog_monitor
                    WHERE namespace = :namespace
                        AND created_at >= :start_time
                    ORDER BY stream_name, consumer_group, created_at DESC
                """)
                params = {
                    'namespace': namespace,
                    'start_time': start_time
                }
            
            result = await session.execute(query, params)
            rows = result.fetchall()
            
            data = []
            for row in rows:
                data.append({
                    'stream_name': row.stream_name,
                    'consumer_group': row.consumer_group,
                    'last_published_offset': row.last_published_offset,
                    'last_delivered_offset': row.last_delivered_offset,
                    'last_acked_offset': row.last_acked_offset,
                    'pending_count': row.pending_count,
                    'backlog_undelivered': row.backlog_undelivered,
                    'backlog_unprocessed': row.backlog_unprocessed,
                    'created_at': row.created_at.isoformat() if row.created_at else None
                })
            
            return {
                'success': True,
                'data': data,
                'total': len(data)
            }
    
    @staticmethod
    async def get_stream_backlog_summary(data_access, namespace: str) -> Dict[str, Any]:
        async with data_access.AsyncSessionLocal() as session:
            query = text("""
                WITH latest_data AS (
                    SELECT DISTINCT ON (stream_name, consumer_group)
                        stream_name,
                        consumer_group,
                        backlog_undelivered,
                        backlog_unprocessed,
                        pending_count
                    FROM stream_backlog_monitor
                    WHERE namespace = :namespace
                        AND created_at >= NOW() - INTERVAL '1 hour'
                    ORDER BY stream_name, consumer_group, created_at DESC
                )
                SELECT 
                    COUNT(DISTINCT stream_name) as total_streams,
                    COUNT(DISTINCT consumer_group) as total_groups,
                    SUM(backlog_unprocessed) as total_backlog,
                    SUM(pending_count) as total_pending,
                    MAX(backlog_unprocessed) as max_backlog
                FROM latest_data
            """)
            
            result = await session.execute(query, {'namespace': namespace})
            row = result.fetchone()
            
            if row:
                return {
                    'success': True,
                    'data': {
                        'total_streams': row.total_streams or 0,
                        'total_groups': row.total_groups or 0,
                        'total_backlog': row.total_backlog or 0,
                        'total_pending': row.total_pending or 0,
                        'max_backlog': row.max_backlog or 0
                    }
                }
            else:
                return {
                    'success': True,
                    'data': {
                        'total_streams': 0,
                        'total_groups': 0,
                        'total_backlog': 0,
                        'total_pending': 0,
                        'max_backlog': 0
                    }
                }

    @staticmethod
    @staticmethod
    async def get_queue_overview(
        namespace: str,
        pg_session: AsyncSession,
        registry,  
        queues: List[str],  
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        time_range: Optional[str] = None
    ) -> Dict[str, Any]:
        try:
            if time_range and not start_time:
                now = datetime.now(timezone.utc)
                if time_range.endswith('m'):
                    minutes = int(time_range[:-1])
                    start_time = now - timedelta(minutes=minutes)
                    end_time = now
                elif time_range.endswith('h'):
                    hours = int(time_range[:-1])
                    start_time = now - timedelta(hours=hours)
                    end_time = now
                elif time_range.endswith('d'):
                    days = int(time_range[:-1])
                    start_time = now - timedelta(days=days)
                    end_time = now
                else:
                    start_time = now - timedelta(minutes=15)
                    end_time = now

            if not start_time:
                now = datetime.now(timezone.utc)
                start_time = now - timedelta(minutes=15)
                end_time = now

            all_base_queues = await registry.get_base_queues()

            target_queues = [q for q in queues if q in all_base_queues]

            if not target_queues:
                logger.warning(f"请求的队列 {queues} 在命名空间 {namespace} 中不存在")
                return {
                    "success": True,
                    "data": [],
                    "total": 0,
                    "time_range": {
                        "start_time": start_time.isoformat() if start_time else None,
                        "end_time": end_time.isoformat() if end_time else None
                    }
                }

            logger.info(f"队列概览查询: namespace={namespace}, queues={target_queues}, time_range={start_time} to {end_time}")

            stats_stmt = select(
                Task.queue,
                func.count(Task.stream_id).label('queue_length'),
                func.count(func.distinct(TaskRun.task_name)).label('task_count'),
                func.count().filter(TaskRun.status == 'success').label('success_count'),
                func.count().filter(TaskRun.status == 'failed').label('failed_count')
            ).select_from(Task).outerjoin(
                TaskRun,
                and_(
                    TaskRun.stream_id == Task.stream_id,
                    TaskRun.created_at >= start_time,
                    TaskRun.created_at <= end_time
                )
            ).where(
                and_(
                    Task.queue.in_(target_queues),
                    Task.namespace == namespace
                )
            ).group_by(Task.queue)

            result = await pg_session.execute(stats_stmt)
            rows = result.all()

            queue_stats_map = {}
            for row in rows:
                total_count = row.success_count + row.failed_count
                success_rate = round((row.success_count / total_count) * 100, 2) if total_count > 0 else 0.0

                queue_stats_map[row.queue] = {
                    "queue_name": row.queue,
                    "task_count": row.task_count or 0,
                    "queue_length": row.queue_length or 0,
                    "success_count": row.success_count or 0,
                    "failed_count": row.failed_count or 0,
                    "success_rate": success_rate
                }

            overview_data = []
            for queue_name in sorted(target_queues):
                if queue_name in queue_stats_map:
                    overview_data.append(queue_stats_map[queue_name])
                else:
                    overview_data.append({
                        "queue_name": queue_name,
                        "task_count": 0,
                        "queue_length": 0,
                        "success_count": 0,
                        "failed_count": 0,
                        "success_rate": 0.0
                    })

            return {
                "success": True,
                "data": overview_data,
                "total": len(overview_data),
                "time_range": {
                    "start_time": start_time.isoformat() if start_time else None,
                    "end_time": end_time.isoformat() if end_time else None
                }
            }

        except Exception as e:
            logger.error(f"获取队列概览失败: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "data": []
            }

    @staticmethod
    async def get_queue_tasks_detail(
        namespace: str,
        queue_name: str,
        pg_session: AsyncSession,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        time_range: Optional[str] = None
    ) -> Dict[str, Any]:
        try:
            if time_range and not start_time:
                now = datetime.now(timezone.utc)
                if time_range.endswith('m'):
                    minutes = int(time_range[:-1])
                    start_time = now - timedelta(minutes=minutes)
                    end_time = now
                elif time_range.endswith('h'):
                    hours = int(time_range[:-1])
                    start_time = now - timedelta(hours=hours)
                    end_time = now
                elif time_range.endswith('d'):
                    days = int(time_range[:-1])
                    start_time = now - timedelta(days=days)
                    end_time = now
                else:
                    start_time = now - timedelta(minutes=15)
                    end_time = now

            if not start_time:
                now = datetime.now(timezone.utc)
                start_time = now - timedelta(minutes=15)
                end_time = now

            logger.info(f"获取队列 tasks 详情: namespace={namespace}, queue={queue_name}, time_range={start_time} to {end_time}")

            task_stats_stmt = select(
                TaskRun.task_name,
                func.count().filter(TaskRun.status == 'success').label('success_count'),
                func.count().filter(TaskRun.status == 'failed').label('failed_count'),
                func.avg(TaskRun.duration).label('avg_duration')
            ).select_from(TaskRun).join(
                Task, TaskRun.stream_id == Task.stream_id
            ).where(
                and_(
                    Task.queue == queue_name,
                    Task.namespace == namespace,
                    TaskRun.created_at >= start_time,
                    TaskRun.created_at <= end_time,
                    TaskRun.task_name.isnot(None)
                )
            ).group_by(TaskRun.task_name)

            result = await pg_session.execute(task_stats_stmt)
            rows = result.all()

            tasks = []
            for row in rows:
                total_count = row.success_count + row.failed_count
                success_rate = round((row.success_count / total_count) * 100, 2) if total_count > 0 else 0.0

                tasks.append({
                    "task_name": row.task_name,
                    "success_count": row.success_count or 0,
                    "failed_count": row.failed_count or 0,
                    "success_rate": success_rate,
                    "avg_duration": round(row.avg_duration, 4) if row.avg_duration else 0.0
                })

            return {
                "success": True,
                "queue_name": queue_name,
                "tasks": tasks,
                "total": len(tasks),
                "time_range": {
                    "start_time": start_time.isoformat() if start_time else None,
                    "end_time": end_time.isoformat() if end_time else None
                }
            }

        except Exception as e:
            logger.error(f"获取队列 tasks 详情失败: queue={queue_name}, error={e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "queue_name": queue_name,
                "tasks": []
            }
