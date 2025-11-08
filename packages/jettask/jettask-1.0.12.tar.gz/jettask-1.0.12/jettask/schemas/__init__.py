"""
数据模型定义
所有的Pydantic模型集中管理
"""

from .task import (
    TasksRequest,
    TaskDetailResponse,
    TaskInfo,
    TaskActionRequest,
    TaskListResponse,
    TaskMessageRequest,
    SendTasksRequest,
    SendTasksResponse
)

from .queue import (
    TimeRangeQuery,
    QueueStatsResponse,
    QueueTimelineResponse,
    TrimQueueRequest,
    QueueInfo,
    QueueStats,
    QueueActionRequest
)

from .scheduled_task import (
    ScheduledTaskRequest,
    ScheduledTaskResponse,
    ScheduledTaskInfo,
    ScheduleConfig,
    ScheduledTaskCreate,
    ScheduledTaskUpdate,
    ScheduledTaskCreateRequest
)

from .alert import (
    AlertRuleRequest,
    AlertRuleCreate,
    AlertRuleUpdate,
    AlertRule,
    AlertInstance,
    AlertSummary
)

from .namespace import (
    ConfigMode,
    NamespaceCreate,
    NamespaceUpdate,
    NamespaceResponse,
    NamespaceInfo,
    NamespaceCreateRequest,
    NamespaceUpdateRequest
)

from .backlog import (
    BacklogLatestRequest,
    BacklogTrendRequest,
    BacklogSnapshot,
    BacklogStatistics,
    BacklogTrendResponse,
    BacklogAlert
)

from .common import (
    ErrorResponse,
    FilterCondition,
    BaseListRequest,
    TimeRangeRequest,
    BatchOperationRequest,
    BatchOperationResponse,
    PaginationResponse,
    ListResponse,
    HealthCheck,
    SystemConfigUpdateRequest,
    ApiResponse
)

from .monitoring import (
    MetricPoint,
    TimeSeries,
    MonitoringMetrics,
    AnalyticsData,
    SystemHealth,
    DashboardOverviewRequest,
    DashboardOverview,
    WorkerMetrics
)

from .responses import (
    SuccessResponse,
    DataResponse,
    PaginatedDataResponse,
    SystemStatsData,
    SystemStatsResponse,
    DashboardStatsData,
    DashboardStatsResponse,
    QueueRankingItem,
    TopQueuesResponse,
    NamespaceStatistics,
    NamespaceStatisticsResponse,
    WorkerHeartbeatInfo,
    WorkersResponse,
    WorkerSummary,
    WorkerSummaryResponse,
    WorkerOfflineRecord,
    WorkerOfflineHistoryResponse,
    DatabaseStatus,
    SystemSettings,
    SystemSettingsResponse,
    DatabaseStatusResponse
)

__all__ = [
    'TasksRequest',
    'TaskDetailResponse',
    'TaskInfo',
    'TaskActionRequest',
    'TaskListResponse',
    'TaskMessageRequest',
    'SendTasksRequest',
    'SendTasksResponse',
    
    'TimeRangeQuery',
    'QueueStatsResponse',
    'QueueTimelineResponse',
    'TrimQueueRequest',
    'QueueInfo',
    'QueueStats',
    'QueueActionRequest',
    
    'ScheduledTaskRequest',
    'ScheduledTaskResponse',
    'ScheduledTaskInfo',
    'ScheduleConfig',
    'ScheduledTaskCreate',
    'ScheduledTaskUpdate',
    'ScheduledTaskCreateRequest',
    
    'AlertRuleRequest',
    'AlertRuleCreate',
    'AlertRuleUpdate',
    'AlertRule',
    'AlertInstance',
    'AlertSummary',
    
    'ConfigMode',
    'NamespaceCreate',
    'NamespaceUpdate',
    'NamespaceResponse',
    'NamespaceInfo',
    'NamespaceCreateRequest',
    'NamespaceUpdateRequest',
    
    'BacklogTrendRequest',
    'BacklogSnapshot',
    'BacklogStatistics',
    'BacklogTrendResponse',
    'BacklogAlert',
    
    'ErrorResponse',
    'FilterCondition',
    'BaseListRequest',
    'TimeRangeRequest',
    'BatchOperationRequest',
    'BatchOperationResponse',
    'PaginationResponse',
    'ListResponse',
    'HealthCheck',
    'SystemConfigUpdateRequest',
    'ApiResponse',
    
    'MetricPoint',
    'TimeSeries',
    'MonitoringMetrics',
    'AnalyticsData',
    'SystemHealth',
    'DashboardOverviewRequest',
    'DashboardOverview',
    'WorkerMetrics',

    'SuccessResponse',
    'DataResponse',
    'PaginatedDataResponse',
    'SystemStatsData',
    'SystemStatsResponse',
    'DashboardStatsData',
    'DashboardStatsResponse',
    'QueueRankingItem',
    'TopQueuesResponse',
    'NamespaceStatistics',
    'NamespaceStatisticsResponse',
    'WorkerHeartbeatInfo',
    'WorkersResponse',
    'WorkerSummary',
    'WorkerSummaryResponse',
    'WorkerOfflineRecord',
    'WorkerOfflineHistoryResponse',
    'DatabaseStatus',
    'SystemSettings',
    'SystemSettingsResponse',
    'DatabaseStatusResponse'
]