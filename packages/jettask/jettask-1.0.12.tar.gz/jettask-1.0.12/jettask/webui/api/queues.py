"""
队列模块 - 队列管理、任务处理、队列统计和监控、任务发送
提供轻量级的路由入口，业务逻辑在 QueueService 中实现
包含跨语言任务发送 API
"""
from fastapi import APIRouter, HTTPException, Request, Query, Path, Depends
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

from jettask.schemas import (
    TimeRangeQuery,
    TrimQueueRequest,
    TasksRequest,
    TaskActionRequest,
    BacklogLatestRequest,
    BacklogTrendRequest,
    SendTasksRequest,
    SendTasksResponse
)
from jettask.core.message import TaskMessage
from jettask.webui.services.queue_service import QueueService
from jettask.webui.services.task_service import TaskService
from jettask.utils.redis_monitor import RedisMonitorService
from jettask.utils.task_logger import LogContext, get_task_logger

router = APIRouter(prefix="/queues", tags=["queues"])
logger = get_task_logger(__name__)

_jettask_cache: Dict[str, "Jettask"] = {}



@router.get(
    "/overview",
    summary="获取队列概览信息",
    description="获取队列的关键指标概览，包括消费者组数、队列长度、在线Workers、成功失败统计等",
    responses={
        200: {
            "description": "成功返回队列概览数据",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": [
                            {
                                "queue_name": "email_queue",
                                "consumer_group_count": 2,
                                "queue_length": 150,
                                "online_workers": 5,
                                "success_count": 1234,
                                "failed_count": 12,
                                "success_rate": 99.03
                            }
                        ],
                        "total": 1,
                        "time_range": {
                            "start_time": "2025-11-16T15:46:35.900Z",
                            "end_time": "2025-11-29T16:41:45.900Z"
                        }
                    }
                }
            }
        },
        500: {"description": "服务器内部错误"}
    }
)
async def get_queue_overview(
    request: Request,
    queues: str = Query(..., description="队列名称列表（必填），多个队列用逗号分隔", example="email_queue,sms_queue"),
    start_time: Optional[datetime] = Query(None, description="开始时间（ISO格式），用于统计成功/失败数", example="2025-11-16T15:46:35.900Z"),
    end_time: Optional[datetime] = Query(None, description="结束时间（ISO格式），用于统计成功/失败数", example="2025-11-29T16:41:45.900Z"),
    time_range: Optional[str] = Query(None, description="时间范围，如 15m, 1h, 24h 等，与 start_time/end_time 二选一", example="15m")
) -> Dict[str, Any]:
    try:
        ns = request.state.ns

        pg_session = await ns.get_pg_session()

        try:
            queue_list = [q.strip() for q in queues.split(',') if q.strip()]

            if not queue_list:
                raise HTTPException(status_code=400, detail="queues 参数不能为空")

            registry = await ns.get_queue_registry()

            result = await QueueService.get_queue_overview(
                namespace=ns.name,
                pg_session=pg_session,
                registry=registry,  
                queues=queue_list,
                start_time=start_time,
                end_time=end_time,
                time_range=time_range
            )

            return result

        finally:
            await pg_session.close()

    except Exception as e:
        logger.error(f"获取队列概览失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))



@router.get(
    "/{queue_name}/tasks",
    summary="获取队列的 tasks 详情",
    description="获取指定队列的所有 task_name 的统计详情，包括成功率、失败率、平均执行时间等",
    responses={
        200: {
            "description": "成功返回队列 tasks 详情",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "queue_name": "email_queue",
                        "tasks": [
                            {
                                "task_name": "send_welcome_email",
                                "success_count": 1234,
                                "failed_count": 12,
                                "success_rate": 99.03,
                                "avg_duration": 0.1523
                            },
                            {
                                "task_name": "send_notification",
                                "success_count": 856,
                                "failed_count": 5,
                                "success_rate": 99.42,
                                "avg_duration": 0.0821
                            }
                        ],
                        "total": 2,
                        "time_range": {
                            "start_time": "2025-11-16T15:46:35.900Z",
                            "end_time": "2025-11-29T16:41:45.900Z"
                        }
                    }
                }
            }
        },
        400: {"description": "请求参数错误"},
        500: {"description": "服务器内部错误"}
    }
)
async def get_queue_tasks_detail(
    request: Request,
    queue_name: str = Path(..., description="队列名称", example="email_queue"),
    start_time: Optional[datetime] = Query(None, description="开始时间（ISO格式），用于统计成功/失败数", example="2025-11-16T15:46:35.900Z"),
    end_time: Optional[datetime] = Query(None, description="结束时间（ISO格式），用于统计成功/失败数", example="2025-11-29T16:41:45.900Z"),
    time_range: Optional[str] = Query(None, description="时间范围，如 15m, 1h, 24h 等，与 start_time/end_time 二选一", example="15m")
) -> Dict[str, Any]:
    try:
        ns = request.state.ns

        pg_session = await ns.get_pg_session()

        try:
            result = await QueueService.get_queue_tasks_detail(
                namespace=ns.name,
                queue_name=queue_name,
                pg_session=pg_session,
                start_time=start_time,
                end_time=end_time,
                time_range=time_range
            )

            return result

        finally:
            await pg_session.close()

    except Exception as e:
        logger.error(f"获取队列 tasks 详情失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "",
    summary="获取命名空间队列列表",
    description="获取指定命名空间下所有队列的基本信息和状态",
    responses={
        200: {
            "description": "成功返回队列列表",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "queues": [
                            {"name": "email_queue", "pending": 45, "processing": 3},
                            {"name": "sms_queue", "pending": 12, "processing": 1}
                        ]
                    }
                }
            }
        },
        500: {"description": "服务器内部错误"}
    }
)
async def get_queues(request: Request) -> Dict[str, Any]:
    try:
        ns = request.state.ns

        registry = await ns.get_queue_registry()

        base_queues = await registry.get_base_queues()

        queues_list = []
        for queue_name in sorted(base_queues):
            queues_list.append({
                "name": queue_name
            })

        logger.info(f"获取命名空间 {ns.name} 的队列列表成功，共 {len(queues_list)} 个队列")

        return {
            "success": True,
            "namespace": ns.name,
            "queues": queues_list,
            "total": len(queues_list)
        }

    except Exception as e:
        logger.error(f"获取队列列表失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))




@router.get(
    "/stats-v2",
    summary="获取队列统计信息 v2",
    description="获取队列的详细统计信息，支持消费者组和优先级队列",
    responses={
        200: {"description": "成功返回队列统计"},
        500: {"description": "服务器内部错误"}
    }
)
async def get_queue_stats(
    request: Request,
    queue: Optional[str] = Query(None, description="队列名称，为空则返回所有队列", example="email_queue"),
    start_time: Optional[datetime] = Query(None, description="开始时间（ISO格式）"),
    end_time: Optional[datetime] = Query(None, description="结束时间（ISO格式）"),
    time_range: Optional[str] = Query(None, description="时间范围（如 1h, 24h, 7d）", example="24h")
) -> Dict[str, Any]:
    try:
        ns = request.state.ns

        app = request.app
        if not app or not hasattr(app.state, 'namespace_data_access'):
            raise HTTPException(status_code=500, detail="Namespace data access not initialized")

        namespace_data_access = app.state.namespace_data_access
        return await QueueService.get_queue_stats_v2(
            namespace_data_access, ns.name, queue, start_time, end_time, time_range
        )
    except Exception as e:
        logger.error(f"获取队列统计v2失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))



@router.get(
    "/consumer-groups/{group_name}/stats",
    summary="获取消费者组统计",
    description="获取指定消费者组的详细统计信息和积压情况",
    responses={
        200: {
            "description": "成功返回消费者组统计",
            "content": {
                "application/json": {
                    "example": {
                        "group_name": "email_workers",
                        "pending_messages": 120,
                        "consumers": 5,
                        "lag": 95,
                        "last_delivered_id": "1697644800000-0"
                    }
                }
            }
        },
        400: {"description": "请求参数错误"},
        500: {"description": "服务器内部错误"}
    }
)
async def get_consumer_group_stats(
    request: Request,
    group_name: str = Path(..., description="消费者组名称", example="email_workers")
) -> Dict[str, Any]:
    try:
        ns = request.state.ns

        app = request.app
        if not app or not hasattr(app.state, 'namespace_data_access'):
            raise HTTPException(status_code=500, detail="Namespace data access not initialized")

        namespace_data_access = app.state.namespace_data_access
        return await QueueService.get_consumer_group_stats(namespace_data_access, ns.name, group_name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"获取消费者组统计失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))



@router.get(
    "/stream-backlog",
    summary="获取 Stream 积压监控数据",
    description="获取 Redis Stream 的积压监控数据和历史趋势",
    responses={
        200: {
            "description": "成功返回 Stream 积压数据",
            "content": {
                "application/json": {
                    "example": {
                        "stream_name": "task_stream",
                        "current_length": 1500,
                        "consumer_groups": 3,
                        "total_pending": 250,
                        "history": [
                            {"timestamp": "2025-10-18T10:00:00Z", "length": 1400},
                            {"timestamp": "2025-10-18T11:00:00Z", "length": 1500}
                        ]
                    }
                }
            }
        },
        500: {"description": "服务器内部错误"}
    }
)
async def get_stream_backlog(
    request: Request,
    stream_name: Optional[str] = Query(None, description="Stream 名称，为空则返回所有", example="task_stream"),
    hours: int = Query(24, ge=1, le=168, description="查询最近多少小时的数据", example=24)
) -> Dict[str, Any]:
    try:
        ns = request.state.ns

        app = request.app
        if not app or not hasattr(app.state, 'data_access'):
            raise HTTPException(status_code=500, detail="Data access not initialized")

        data_access = app.state.data_access
        return await QueueService.get_stream_backlog(data_access, ns.name, stream_name, hours)
    except Exception as e:
        logger.error(f"获取Stream积压监控数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/stream-backlog/summary",
    summary="获取 Stream 积压汇总",
    description="获取命名空间下所有 Stream 的积压汇总信息",
    responses={
        200: {
            "description": "成功返回积压汇总",
            "content": {
                "application/json": {
                    "example": {
                        "total_streams": 5,
                        "total_length": 7500,
                        "total_pending": 850,
                        "avg_backlog_rate": 12.5,
                        "streams": [
                            {"name": "task_stream", "length": 1500, "pending": 250},
                            {"name": "email_stream", "length": 2000, "pending": 180}
                        ]
                    }
                }
            }
        },
        500: {"description": "服务器内部错误"}
    }
)
async def get_stream_backlog_summary(request: Request) -> Dict[str, Any]:
    try:
        ns = request.state.ns

        app = request.app
        if not app or not hasattr(app.state, 'data_access'):
            raise HTTPException(status_code=500, detail="Data access not initialized")

        data_access = app.state.data_access
        return await QueueService.get_stream_backlog_summary(data_access, ns.name)
    except Exception as e:
        logger.error(f"获取Stream积压监控汇总失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))



@router.post(
    "/backlog/latest",
    summary="获取最新积压数据快照",
    description="获取指定命名空间下队列的最新积压数据快照",
    responses={
        200: {
            "description": "成功返回积压快照数据",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "namespace": "default",
                        "timestamp": "2025-10-18T10:30:00Z",
                        "snapshots": [
                            {
                                "queue_name": "email_queue",
                                "pending_count": 120,
                                "processing_count": 8,
                                "completed_count": 5430,
                                "failed_count": 12,
                                "queue_size": 128,
                                "oldest_task_age": 45
                            }
                        ]
                    }
                }
            }
        },
        500: {"description": "服务器内部错误"}
    }
)
async def get_latest_backlog(
    request: Request,
    backlog_request: BacklogLatestRequest = ...
) -> Dict[str, Any]:
    try:
        ns = request.state.ns

        app = request.app
        if not app or not hasattr(app.state, 'data_access'):
            raise HTTPException(status_code=500, detail="Data access not initialized")

        data_access = app.state.data_access
        queues = backlog_request.queues or []


        return {
            "success": True,
            "namespace": ns.name,
            "timestamp": datetime.now().isoformat(),
            "snapshots": [],
            "message": "Backlog monitoring endpoint - implementation pending"
        }
    except Exception as e:
        logger.error(f"获取最新积压数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/backlog/trend",
    summary="获取队列积压趋势",
    description="获取指定队列在一段时间内的积压趋势数据，支持多种时间粒度",
    responses={
        200: {
            "description": "成功返回积压趋势数据",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "namespace": "default",
                        "queue_name": "email_queue",
                        "time_range": "1h",
                        "interval": "5m",
                        "timestamps": [
                            "2025-10-18T10:00:00Z",
                            "2025-10-18T10:05:00Z",
                            "2025-10-18T10:10:00Z"
                        ],
                        "metrics": {
                            "pending": [120, 115, 108],
                            "processing": [8, 10, 9],
                            "completed": [5430, 5445, 5462],
                            "failed": [12, 12, 13]
                        },
                        "statistics": {
                            "peak_pending": 120,
                            "avg_pending": 114.3,
                            "avg_throughput": 10.7,
                            "overall_success_rate": 99.76
                        }
                    }
                }
            }
        },
        400: {"description": "请求参数错误"},
        500: {"description": "服务器内部错误"}
    }
)
async def get_backlog_trend(
    request: Request,
    trend_request: BacklogTrendRequest = ...
) -> Dict[str, Any]:
    try:
        ns = request.state.ns

        app = request.app
        if not app or not hasattr(app.state, 'data_access'):
            raise HTTPException(status_code=500, detail="Data access not initialized")

        data_access = app.state.data_access


        return {
            "success": True,
            "namespace": ns.name,
            "queue_name": trend_request.queue_name,
            "time_range": trend_request.time_range,
            "interval": trend_request.interval,
            "timestamps": [],
            "metrics": {},
            "statistics": {},
            "message": "Backlog trend endpoint - implementation pending"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"获取积压趋势失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))



def get_task_service(request: Request) -> TaskService:
    if not hasattr(request.app.state, 'data_access'):
        raise HTTPException(status_code=500, detail="Data access not initialized")
    return TaskService(request.app.state.data_access)



@router.post(
    "/tasks-v2",
    summary="获取任务列表 v2",
    description="获取任务列表v2版本，支持tasks和task_runs表连表查询，提供更丰富的查询和过滤功能",
    responses={
        200: {
            "description": "成功返回任务列表",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": [
                            {
                                "task_id": "task-001",
                                "queue_name": "email_queue",
                                "status": "completed",
                                "created_at": "2025-10-18T10:00:00Z",
                                "runs": []
                            }
                        ],
                        "total": 150,
                        "page": 1,
                        "page_size": 20
                    }
                }
            }
        },
        400: {"description": "请求参数错误"},
        500: {"description": "服务器内部错误"}
    }
)
async def get_tasks_v2(request: Request):
    try:
        ns = request.state.ns

        app = request.app
        if not app or not hasattr(app.state, 'namespace_data_access'):
            raise HTTPException(status_code=500, detail="Namespace data access not initialized")

        namespace_data_access = app.state.namespace_data_access

        body = await request.json()

        return await QueueService.get_tasks_v2(namespace_data_access, ns.name, body)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"获取任务列表v2失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))



@router.get(
    "/redis/monitor",
    summary="获取 Redis 性能监控数据",
    description="获取指定命名空间的 Redis 实时性能监控数据，包括内存使用、连接数、命令统计等",
    responses={
        200: {
            "description": "成功返回 Redis 监控数据",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "namespace": "default",
                        "redis_info": {
                            "used_memory": "10485760",
                            "used_memory_human": "10M",
                            "connected_clients": "25",
                            "total_commands_processed": "1500000",
                            "instantaneous_ops_per_sec": "150",
                            "keyspace_hits": "98500",
                            "keyspace_misses": "1500"
                        },
                        "performance": {
                            "hit_rate": "98.5%",
                            "qps": 150,
                            "memory_fragmentation_ratio": 1.2
                        }
                    }
                }
            }
        },
        500: {"description": "服务器内部错误"}
    }
)
async def get_redis_monitor(request: Request):
    try:
        ns = request.state.ns

        app = request.app
        if not app or not hasattr(app.state, 'namespace_data_access'):
            raise HTTPException(status_code=500, detail="Namespace data access not initialized")

        namespace_data_access = app.state.namespace_data_access
        redis_monitor_service = RedisMonitorService(namespace_data_access)
        return await redis_monitor_service.get_redis_monitor_data(ns.name)
    except Exception as e:
        logger.error(f"获取Redis监控数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/redis/slow-log",
    summary="获取 Redis 慢查询日志",
    description="获取 Redis 的慢查询日志，用于诊断性能问题",
    responses={
        200: {
            "description": "成功返回慢查询日志",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "namespace": "default",
                        "slow_logs": [
                            {
                                "id": 12345,
                                "timestamp": 1697644800,
                                "duration_us": 15000,
                                "command": "KEYS pattern*",
                                "client_addr": "127.0.0.1:54321"
                            }
                        ],
                        "total": 10
                    }
                }
            }
        },
        500: {"description": "服务器内部错误"}
    }
)
async def get_redis_slow_log(
    request: Request,
    limit: int = Query(10, ge=1, le=100, description="返回记录数，范围 1-100", example=10)
):
    try:
        ns = request.state.ns

        app = request.app
        if not app or not hasattr(app.state, 'namespace_data_access'):
            raise HTTPException(status_code=500, detail="Namespace data access not initialized")

        namespace_data_access = app.state.namespace_data_access
        redis_monitor_service = RedisMonitorService(namespace_data_access)
        return await redis_monitor_service.get_slow_log(ns.name, limit)
    except Exception as e:
        logger.error(f"获取Redis慢查询日志失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/redis/command-stats",
    summary="获取 Redis 命令统计",
    description="获取 Redis 各类命令的执行统计信息，包括调用次数、耗时等",
    responses={
        200: {
            "description": "成功返回命令统计",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "namespace": "default",
                        "command_stats": [
                            {
                                "command": "GET",
                                "calls": 1500000,
                                "usec": 45000000,
                                "usec_per_call": 30.0
                            },
                            {
                                "command": "SET",
                                "calls": 800000,
                                "usec": 32000000,
                                "usec_per_call": 40.0
                            }
                        ],
                        "total_commands": 25
                    }
                }
            }
        },
        500: {"description": "服务器内部错误"}
    }
)
async def get_redis_command_stats(request: Request):
    try:
        ns = request.state.ns

        app = request.app
        if not app or not hasattr(app.state, 'namespace_data_access'):
            raise HTTPException(status_code=500, detail="Namespace data access not initialized")

        namespace_data_access = app.state.namespace_data_access
        redis_monitor_service = RedisMonitorService(namespace_data_access)
        return await redis_monitor_service.get_command_stats(ns.name)
    except Exception as e:
        logger.error(f"获取Redis命令统计失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/redis/stream-stats",
    summary="获取 Redis Stream 统计",
    description="获取 Redis Stream 的详细统计信息，包括长度、消费者组、消息等",
    responses={
        200: {
            "description": "成功返回 Stream 统计",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "namespace": "default",
                        "streams": [
                            {
                                "stream_name": "task_stream",
                                "length": 1500,
                                "first_entry_id": "1697644800000-0",
                                "last_entry_id": "1697731200000-5",
                                "groups": [
                                    {
                                        "name": "workers",
                                        "consumers": 5,
                                        "pending": 120,
                                        "last_delivered_id": "1697730000000-3"
                                    }
                                ]
                            }
                        ]
                    }
                }
            }
        },
        500: {"description": "服务器内部错误"}
    }
)
async def get_redis_stream_stats(
    request: Request,
    stream_name: Optional[str] = Query(None, description="Stream 名称，为空则返回所有 Stream 的统计", example="task_stream")
):
    try:
        ns = request.state.ns

        app = request.app
        if not app or not hasattr(app.state, 'namespace_data_access'):
            raise HTTPException(status_code=500, detail="Namespace data access not initialized")

        namespace_data_access = app.state.namespace_data_access
        redis_monitor_service = RedisMonitorService(namespace_data_access)
        return await redis_monitor_service.get_stream_stats(ns.name, stream_name)
    except Exception as e:
        logger.error(f"获取Redis Stream统计失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))



@router.get(
    "/tasks",
    summary="获取队列任务列表（简化版）",
    description="获取指定队列的任务列表，向后兼容的简化版本",
    responses={
        200: {
            "description": "成功返回任务列表",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": [
                            {
                                "task_id": "task-001",
                                "queue_name": "email_queue",
                                "status": "completed",
                                "created_at": "2025-10-18T10:00:00Z"
                            }
                        ],
                        "total": 50
                    }
                }
            }
        },
        500: {"description": "服务器内部错误"}
    }
)
async def get_queue_tasks_simple(
    request: Request,
    queue_name: str = Query(..., description="队列名称", example="email_queue"),
    start_time: Optional[str] = Query(None, description="开始时间（ISO格式或 \"-\" 表示最早）", example="2025-10-18T00:00:00Z"),
    end_time: Optional[str] = Query(None, description="结束时间（ISO格式或 \"+\" 表示最新）", example="2025-10-18T23:59:59Z"),
    limit: int = Query(50, ge=1, le=1000, description="返回数量限制，范围 1-1000", example=50)
):
    try:
        ns = request.state.ns

        if not hasattr(request.app.state, 'monitor'):
            raise HTTPException(status_code=500, detail="Monitor service not initialized")

        monitor = request.app.state.monitor
        result = await monitor.get_queue_tasks(
            queue_name,
            start_time or "-",
            end_time or "+",
            limit,
            reverse=True  
        )

        return result
    except Exception as e:
        logger.error(f"获取队列 {queue_name} 任务列表失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/send-queue",
    summary="发送任务到队列",
    description="跨语言的任务发送接口，支持批量发送任务到指定命名空间的队列",
    response_model=SendTasksResponse,
    responses={
        200: {
            "description": "任务发送成功",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Tasks sent successfully",
                        "event_ids": [
                            "1730361234567-0",
                            "1730361234568-0"
                        ],
                        "total_sent": 2,
                        "namespace": "default"
                    }
                }
            }
        },
        400: {"description": "请求参数错误"},
        404: {"description": "命名空间不存在"},
        500: {"description": "服务器内部错误"}
    }
)
async def send_tasks(
    request: Request,
    send_request: SendTasksRequest
) -> SendTasksResponse:
    try:
        ns = request.state.ns
        namespace = ns.name

        client_host = request.client.host if request.client else 'unknown'
        client_port = request.client.port if request.client else 'unknown'

        with LogContext(
            endpoint='/queues/send-queue',
            namespace=namespace,
            client_ip=client_host,
            client_port=client_port,
            task_count=len(send_request.messages)
        ):
            logger.info(
                f"收到任务发送请求",
                extra={
                    'extra_fields': {
                        'namespace': namespace,
                        'task_count': len(send_request.messages),
                        'client_ip': client_host,
                        'client_port': client_port,
                        'request_path': str(request.url.path),
                        'method': request.method,
                        'messages': [msg.model_dump() for msg in send_request.messages ]
                    }
                }
            )

            for idx, msg_req in enumerate(send_request.messages):
                logger.debug(
                    f"任务 #{idx+1} 详情",
                    extra={
                        'extra_fields': {
                            'task_index': idx + 1,
                            'queue': msg_req.queue,
                            'priority': msg_req.priority,
                            'delay': msg_req.delay,
                            'has_args': bool(msg_req.args),
                            'args_count': len(msg_req.args) if msg_req.args else 0,
                            'kwargs_keys': list(msg_req.kwargs.keys()) if msg_req.kwargs else [],
                            'kwargs': msg_req.kwargs
                        }
                    }
                )

            logger.debug(f"正在获取命名空间 '{namespace}' 的 Jettask 实例")
            jettask_app = await ns.get_jettask_app()

            task_messages = []
            for msg_req in send_request.messages:
                msg = TaskMessage(
                    queue=msg_req.queue,
                    kwargs=msg_req.kwargs,
                    priority=msg_req.priority,
                    delay=msg_req.delay,
                    args=tuple(msg_req.args) if msg_req.args else ()
                )
                task_messages.append(msg)

            logger.info(
                f"开始发送 {len(task_messages)} 个任务到命名空间 '{namespace}'"
            )
            event_ids = await jettask_app.send_tasks(task_messages, asyncio=True)

            if not event_ids:
                logger.error(
                    "任务发送失败: 未返回事件ID",
                    extra={
                        'extra_fields': {
                            'namespace': namespace,
                            'task_count': len(task_messages)
                        }
                    }
                )
                raise HTTPException(
                    status_code=500,
                    detail="Failed to send tasks: no event IDs returned"
                )

            logger.info(
                f"成功发送 {len(event_ids)} 个任务到命名空间 '{namespace}'",
                extra={
                    'extra_fields': {
                        'namespace': namespace,
                        'event_ids': event_ids,
                        'total_sent': len(event_ids),
                        'client_ip': client_host
                    }
                }
            )

            return SendTasksResponse(
                success=True,
                message="Tasks sent successfully",
                event_ids=event_ids,
                total_sent=len(event_ids),
                namespace=namespace
            )

    except HTTPException:
        raise
    except Exception as e:
        namespace_name = getattr(request.state, 'ns', None)
        namespace_name = namespace_name.name if namespace_name else 'unknown'

        logger.error(
            f"任务发送失败",
            extra={
                'extra_fields': {
                    'namespace': namespace_name,
                    'error': str(e),
                    'error_type': type(e).__name__
                }
            },
            exc_info=True
        )

        return SendTasksResponse(
            success=False,
            message="Failed to send tasks",
            event_ids=[],
            total_sent=0,
            namespace=namespace_name,
            error=str(e)
        )


__all__ = ['router']