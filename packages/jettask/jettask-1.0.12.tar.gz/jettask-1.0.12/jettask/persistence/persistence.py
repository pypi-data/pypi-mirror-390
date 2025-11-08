"""任务持久化模块

负责解析Redis Stream消息，并将任务数据批量插入PostgreSQL数据库。
"""

import json
import logging
import traceback
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import insert

from jettask.db.models.task import Task

logger = logging.getLogger(__name__)


class TaskPersistence:
    """任务持久化处理器

    职责：
    - 解析Stream消息为任务信息
    - 批量插入任务到PostgreSQL的tasks表
    - 处理插入失败的降级策略
    """

    def __init__(
        self,
        async_session_local: sessionmaker,
        namespace_id: str,
        namespace_name: str
    ):
        self.AsyncSessionLocal = async_session_local
        self.namespace_id = namespace_id
        self.namespace_name = namespace_name










    async def insert_tasks(self, tasks: List[Dict[str, Any]]) -> int:
        if not tasks:
            return 0

        logger.info(f"Attempting to insert {len(tasks)} tasks to tasks table")

        try:
            async with self.AsyncSessionLocal() as session:
                tasks_data = []
                for task in tasks:
                    task_data = json.loads(task['task_data'])

                    scheduled_task_id = task_data.get('scheduled_task_id') or task.get('scheduled_task_id')

                    if scheduled_task_id:
                        source = 'scheduler'  
                    else:
                        source = 'redis_stream'  

                    tasks_data.append({
                        'stream_id': task['id'],  
                        'queue': task['queue_name'],
                        'namespace': self.namespace_name,
                        'scheduled_task_id': str(scheduled_task_id) if scheduled_task_id else None,
                        'payload': json.loads(task['task_data']),  
                        'priority': task['priority'],
                        'delay': task.get('delay'),  
                        'created_at': task['created_at'],
                        'source': source,
                        'task_metadata': json.loads(task.get('metadata', '{}'))  
                    })

                logger.debug(f"Executing batch insert with {len(tasks_data)} tasks")

                try:
                    stmt = insert(Task).values(tasks_data).on_conflict_do_nothing(
                        constraint='tasks_pkey'  
                    )

                    await session.execute(stmt)
                    await session.commit()

                    inserted_count = len(tasks_data)
                    logger.debug(f"Tasks table batch insert transaction completed: {inserted_count} tasks")
                    return inserted_count

                except Exception as e:
                    logger.error(f"Error in batch insert, trying fallback: {e}")
                    await session.rollback()

                    total_inserted = 0

                    for task_dict in tasks_data:
                        try:
                            stmt = insert(Task).values(**task_dict).on_conflict_do_nothing(
                                constraint='tasks_pkey'
                            )
                            await session.execute(stmt)
                            await session.commit()
                            total_inserted += 1
                        except Exception as single_error:
                            logger.error(f"Failed to insert task {task_dict.get('stream_id')}: {single_error}")
                            await session.rollback()

                    if total_inserted > 0:
                        logger.info(f"Fallback insert completed: {total_inserted} tasks inserted")
                    else:
                        logger.info(f"No new tasks inserted in fallback mode")

                    return total_inserted

        except Exception as e:
            logger.error(f"Error inserting tasks to PostgreSQL: {e}")
            logger.error(traceback.format_exc())
            return 0

    async def batch_insert_tasks(self, tasks: List[Dict[str, Any]]) -> int:
        if not tasks:
            return 0

        logger.info(f"[BATCH INSERT] 批量插入 {len(tasks)} 条任务...")

        try:
            async with self.AsyncSessionLocal() as session:
                insert_data = []
                for record in tasks:
                    scheduled_task_id = record.get('scheduled_task_id')
                    insert_data.append({
                        'stream_id': record['stream_id'],
                        'queue': record['queue'],
                        'namespace': record['namespace'],
                        'scheduled_task_id': str(scheduled_task_id) if scheduled_task_id is not None else None,
                        'payload': record.get('payload', {}),
                        'priority': record.get('priority', 0),
                        'delay': record.get('delay', 0),
                        'created_at': record.get('created_at'),
                        'source': record.get('source', 'redis_stream'),
                        'task_metadata': record.get('metadata', {})
                    })

                stmt = insert(Task).values(insert_data).on_conflict_do_nothing(
                    constraint='tasks_pkey'
                )

                await session.execute(stmt)
                await session.commit()

                logger.info(f"[BATCH INSERT] ✓ 成功插入 {len(insert_data)} 条任务")
                return len(insert_data)

        except Exception as e:
            logger.error(f"[BATCH INSERT] ✗ 批量插入失败: {e}", exc_info=True)
            return 0

    async def batch_update_tasks(self, updates: List[Dict[str, Any]]) -> int:
        if not updates:
            return 0


        try:
            from sqlalchemy.dialects.postgresql import insert
            from ..db.models import TaskRun
            from ..utils.serializer import loads_str
            from datetime import datetime, timezone

            deduplicated = {}
            for record in updates:
                stream_id = record['stream_id']
                deduplicated[stream_id] = record

            unique_updates = list(deduplicated.values())

            if len(unique_updates) < len(updates):
                logger.info(
                    f"[BATCH UPDATE] 去重: {len(updates)} 条 → {len(unique_updates)} 条 "
                    f"(合并了 {len(updates) - len(unique_updates)} 条重复记录)"
                )

            async with self.AsyncSessionLocal() as session:
                upsert_data = []
                for record in unique_updates:
                    logger.debug(f"处理记录: {record}")
                    result = record.get('result')
                    if result and isinstance(result, bytes):
                        try:
                            result = loads_str(result)
                        except Exception:
                            result = result.decode('utf-8') if isinstance(result, bytes) else result

                    error = record.get('error')
                    if error and isinstance(error, bytes):
                        error = error.decode('utf-8')

                    duration = None
                    started_at = record.get('started_at')
                    completed_at = record.get('completed_at')
                    if started_at and completed_at:
                        duration = completed_at - started_at

                    status = record.get('status')
                    if status and isinstance(status, bytes):
                        status = status.decode('utf-8')

                    consumer = record.get('consumer')
                    if consumer and isinstance(consumer, bytes):
                        consumer = consumer.decode('utf-8')

                    task_name = record.get('task_name')

                    upsert_record = {
                        'stream_id': record['stream_id'],
                        'task_name': task_name,  
                        'status': status,
                        'result': result,
                        'error': error,
                        'started_at': started_at,
                        'completed_at': completed_at,
                        'retries': record.get('retries', 0),
                        'duration': duration,
                        'consumer': consumer,
                        'updated_at': datetime.now(timezone.utc),
                    }
                    logger.debug(f"upsert_record: {upsert_record}")
                    upsert_data.append(upsert_record)

                logger.info(f"[BATCH UPDATE] 准备写入 {len(upsert_data)} 条记录")

                stmt = insert(TaskRun).values(upsert_data)

                from sqlalchemy import func
                stmt = stmt.on_conflict_do_update(
                    constraint='task_runs_pkey',
                    set_={
                        'status': stmt.excluded.status,
                        'result': func.coalesce(stmt.excluded.result, TaskRun.result),
                        'error': func.coalesce(stmt.excluded.error, TaskRun.error),
                        'started_at': func.coalesce(stmt.excluded.started_at, TaskRun.started_at),
                        'completed_at': func.coalesce(stmt.excluded.completed_at, TaskRun.completed_at),
                        'retries': func.coalesce(stmt.excluded.retries, TaskRun.retries),
                        'duration': func.coalesce(stmt.excluded.duration, TaskRun.duration),
                        'consumer': func.coalesce(stmt.excluded.consumer, TaskRun.consumer),
                        'updated_at': stmt.excluded.updated_at,
                    }
                )

                await session.execute(stmt)
                await session.commit()

                logger.info(f"[BATCH UPDATE] ✓ 成功更新 {len(upsert_data)} 条任务状态")
                return len(upsert_data)

        except Exception as e:
            logger.error(f"[BATCH UPDATE] ✗ 批量更新失败: {e}", exc_info=True)
            return 0
