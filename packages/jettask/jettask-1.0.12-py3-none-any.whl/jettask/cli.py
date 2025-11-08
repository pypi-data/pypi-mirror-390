#!/usr/bin/env python
"""
JetTask CLI - 命令行接口
"""
import asyncio
import click
import sys
import os
import importlib
import importlib.util
import multiprocessing
from pathlib import Path

if __name__ == '__main__':
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

from jettask.config.nacos_config import config
from jettask.config.env_loader import EnvLoader
from jettask.core.app_importer import import_app, AppImporter
import functools


def async_command(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))
    return wrapper


@click.group()
@click.version_option(version='0.1.0', prog_name='JetTask')
@click.option('--env-file', '-e', envvar='JETTASK_ENV_FILE',
              help='环境变量文件路径 (.env 格式)，可通过 JETTASK_ENV_FILE 环境变量指定')
@click.pass_context
def cli(ctx, env_file):
    ctx.ensure_object(dict)

    loader = EnvLoader()

    if env_file:
        try:
            loader.load_env_file(env_file, override=True)
            click.echo(f"✓ 已加载环境变量文件: {env_file}")
        except FileNotFoundError:
            click.echo(f"Error: 环境变量文件不存在: {env_file}", err=True)
            raise click.Abort()
        except Exception as e:
            click.echo(f"Error: 加载环境变量文件失败: {e}", err=True)
            raise click.Abort()
    else:
        loader.auto_load()

    ctx.obj['env_loader'] = loader

@cli.command()
@click.option('--host', default='0.0.0.0', envvar='JETTASK_API_HOST', help='服务器监听地址')
@click.option('--port', default=8001, type=int, envvar='JETTASK_API_PORT', help='服务器监听端口')
@click.option('--redis-url', envvar='JETTASK_REDIS_URL', help='Redis连接URL')
@click.option('--redis-prefix', envvar='JETTASK_REDIS_PREFIX', help='Redis键前缀')
@click.option('--jettask-pg-url', envvar='JETTASK_PG_URL', help='PostgreSQL连接URL')
@click.option('--reload', is_flag=True, envvar='JETTASK_API_RELOAD', help='启用自动重载')
@click.option('--log-level', default='info', envvar='JETTASK_LOG_LEVEL',
              type=click.Choice(['debug', 'info', 'warning', 'error']),
              help='日志级别')
@click.option('--api-key', envvar='JETTASK_API_KEY', help='API密钥用于鉴权（可选，如果不设置则不启用鉴权）')
@click.option('--use-nacos', is_flag=True,
              help='从Nacos配置中心读取配置')
@click.option('--nacos-server',
              help='Nacos服务器地址 (如: 127.0.0.1:8848)')
@click.option('--nacos-namespace',
              help='Nacos命名空间')
@click.option('--nacos-username',
              help='Nacos用户名')
@click.option('--nacos-password',
              help='Nacos密码')
@click.option('--nacos-group',
              help='Nacos配置组')
@click.option('--nacos-data-id',
              help='Nacos配置ID')
@click.pass_context
def api(ctx, host, port, redis_url, redis_prefix, jettask_pg_url, reload, log_level,
        api_key, use_nacos, nacos_server, nacos_namespace, nacos_username, nacos_password,
        nacos_group, nacos_data_id):
    import os
    import uvicorn

    if use_nacos:
        try:
            nacos_server = nacos_server or os.environ.get('NACOS_SERVER')
            nacos_namespace = nacos_namespace or os.environ.get('NACOS_NAMESPACE')
            nacos_username = nacos_username or os.environ.get('NACOS_USERNAME')
            nacos_password = nacos_password or os.environ.get('NACOS_PASSWORD')
            nacos_group = nacos_group or os.environ.get('NACOS_GROUP', 'DEFAULT_GROUP')
            nacos_data_id = nacos_data_id or os.environ.get('NACOS_DATA_ID')

            if not all([nacos_server, nacos_namespace, nacos_group]):
                missing = []
                if not nacos_server: missing.append("--nacos-server 或 NACOS_SERVER")
                if not nacos_namespace: missing.append("--nacos-namespace 或 NACOS_NAMESPACE")
                if not nacos_group: missing.append("--nacos-group 或 NACOS_GROUP")

                click.echo("Error: Nacos配置不完整，缺少以下配置:", err=True)
                for item in missing:
                    click.echo(f"  - {item}", err=True)
                raise click.Abort()

            os.environ['NACOS_SERVER'] = nacos_server
            os.environ['NACOS_NAMESPACE'] = nacos_namespace
            os.environ['NACOS_GROUP'] = nacos_group
            if nacos_data_id:
                os.environ['NACOS_DATA_ID'] = nacos_data_id
            if nacos_username:
                os.environ['NACOS_USERNAME'] = nacos_username
            if nacos_password:
                os.environ['NACOS_PASSWORD'] = nacos_password

            click.echo(f"正在从Nacos加载配置 ({nacos_server}/{nacos_namespace})...")

            nacos_pg_url = config.config.get('JETTASK_PG_URL')
            if not nacos_pg_url:
                pg_host = config.config.get('PG_DB_HOST', 'localhost')
                pg_port = config.config.get('PG_DB_PORT', 5432)
                pg_user = config.config.get('PG_DB_USERNAME', 'jettask')
                pg_password = config.config.get('PG_DB_PASSWORD', '123456')
                pg_database = config.config.get('PG_DB_DATABASE', 'jettask')
                nacos_pg_url = f'postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_database}'

            if nacos_pg_url:
                os.environ['JETTASK_PG_URL'] = nacos_pg_url
                if not jettask_pg_url:  
                    jettask_pg_url = nacos_pg_url

            for key, value in config.config.items():
                if isinstance(value, (str, int, float, bool)):
                    os.environ[key] = str(value)

            if not redis_url:
                redis_host = config.config.get('REDIS_HOST', 'localhost')
                redis_port = config.config.get('REDIS_PORT', 6379)
                redis_db = config.config.get('REDIS_DB', 0)
                redis_password = config.config.get('REDIS_PASSWORD')
                if redis_password:
                    redis_url = f'redis://:{redis_password}@{redis_host}:{redis_port}/{redis_db}'
                else:
                    redis_url = f'redis://{redis_host}:{redis_port}/{redis_db}'
                os.environ['JETTASK_REDIS_URL'] = redis_url

            if not api_key:
                nacos_api_key = config.config.get('JETTASK_API_KEY') or config.config.get('API_KEY')
                if nacos_api_key:
                    api_key = nacos_api_key
                    os.environ['JETTASK_API_KEY'] = api_key
                    click.echo(f"✓ 从Nacos获取API密钥配置")

            click.echo(f"✓ 从Nacos加载配置成功")
        except click.Abort:
            raise
        except Exception as e:
            click.echo(f"Error: 从Nacos加载配置失败: {e}", err=True)
            import traceback
            traceback.print_exc()
            raise click.Abort()

    if not jettask_pg_url:
        raise ValueError(
            "必须提供 --jettask-pg-url 或在环境变量中设置 JETTASK_PG_URL\n"
            "或使用 jettask api --use-nacos 从Nacos加载配置"
        )

    if not redis_url:
        raise ValueError(
            "必须提供 --redis-url 或在环境变量中设置 JETTASK_REDIS_URL\n"
            "或使用 jettask api --use-nacos 从Nacos加载配置"
        )

    os.environ['JETTASK_REDIS_URL'] = redis_url
    if redis_prefix:
        os.environ['JETTASK_REDIS_PREFIX'] = redis_prefix
    os.environ['JETTASK_PG_URL'] = jettask_pg_url
    os.environ['USE_NACOS'] = 'true' if use_nacos else 'false'
    if api_key:
        os.environ['JETTASK_API_KEY'] = api_key
    
    app_module = "jettask.webui.app:app"
    click.echo(f"Starting JetTask API Server on {host}:{port}")
    
    click.echo("=" * 60)
    click.echo("API Server Configuration")
    click.echo("=" * 60)
    click.echo(f"Host:         {host}")
    click.echo(f"Port:         {port}")
    click.echo(f"Redis URL:    {redis_url}")
    click.echo(f"Redis Prefix: {redis_prefix or 'jettask (default)'}")
    click.echo(f"Database:     {jettask_pg_url}")
    click.echo(f"Auto-reload:  {reload}")
    click.echo(f"Log level:    {log_level}")

    if api_key:
        if ctx.params.get('api_key'):
            api_key_source = "命令行参数"
        elif use_nacos and (config.config.get('JETTASK_API_KEY') or config.config.get('API_KEY')):
            api_key_source = "Nacos配置"
        else:
            api_key_source = "环境变量"
        click.echo(f"API Key:      Enabled (鉴权已启用, 来源: {api_key_source})")
    else:
        click.echo(f"API Key:      Disabled (无鉴权)")

    click.echo(f"Nacos:        {'Enabled' if use_nacos else 'Disabled'}")
    click.echo("=" * 60)
    click.echo(f"API Endpoint: http://{host}:{port}/api")
    click.echo(f"WebUI:        http://{host}:{port}/")
    click.echo("=" * 60)
    
    try:
        uvicorn.run(
            app_module,
            host=host,
            port=port,
            log_level=log_level,
            reload=reload
        )
    except KeyboardInterrupt:
        click.echo("\nShutting down API Server...")
    except Exception as e:
        click.echo(f"Error starting API Server: {e}", err=True)
        sys.exit(1)



@cli.command()
@click.option('--app', '-a', 'app_str', envvar='JETTASK_APP',
              help='应用位置 (如: module:app, path/to/file.py:app, 或目录名)')
@click.option('--tasks', '-t', envvar='JETTASK_TASKS', help='任务名称（逗号分隔，如: task1,task2）')
@click.option('--concurrency', '-c', type=int, envvar='JETTASK_CONCURRENCY', help='并发数（默认为CPU核心数的一半）')
@click.option('--prefetch', '-p', type=int, default=100, envvar='JETTASK_PREFETCH', help='预取倍数')
def worker(app_str, tasks, concurrency, prefetch):


    if not tasks:
        click.echo("Error: 必须指定 --tasks 参数或设置 JETTASK_TASKS 环境变量", err=True)
        click.echo("\n示例:", err=True)
        click.echo("  jettask worker --tasks my_task", err=True)
        click.echo("  jettask worker -t task1,task2", err=True)
        click.echo("  export JETTASK_TASKS=my_task && jettask worker", err=True)
        raise click.Abort()

    cpu_count = multiprocessing.cpu_count()
    if concurrency is None:
        concurrency = max(1, cpu_count // 4)
        click.echo(f"Using default concurrency: {concurrency} (1/4 of {cpu_count} CPU cores)")
    if concurrency>cpu_count:
        click.echo(f"Error: Specified concurrency {concurrency} exceeds CPU cores {cpu_count}", err=True)
        raise click.Abort()

    try:
        if app_str:
            click.echo(f"Loading app from: {app_str}")
            app = import_app(app_str)
        else:
            click.echo("Auto-discovering Jettask app...")
            click.echo("Searching in: app.py, main.py, server.py, worker.py")
            app = import_app()  
        
        
        app_info = AppImporter.get_app_info(app)
        click.echo(f"\nFound Jettask app:")
        click.echo(f"  Tasks: {app_info['tasks']} registered")
        
        if app_info.get('task_names') and app_info['tasks'] > 0:
            task_preview = app_info['task_names'][:3]
            click.echo(f"  Names: {', '.join(task_preview)}" + 
                      (f" (+{app_info['tasks'] - 3} more)" if app_info['tasks'] > 3 else ""))
    except ImportError as e:
        import traceback
        click.echo(f"Error: Failed to import app: {e}", err=True)
        
        click.echo("\n" + "=" * 60, err=True)
        click.echo("Full traceback:", err=True)
        click.echo("=" * 60, err=True)
        traceback.print_exc()
        click.echo("=" * 60, err=True)
        
        click.echo("\nTips:", err=True)
        click.echo("  - Check if there are syntax errors in your code", err=True)
        click.echo("  - Verify all imports in your module are available", err=True)
        click.echo("  - Specify app location: jettask worker myapp:app", err=True)
        click.echo("  - Or set environment variable: export JETTASK_APP=myapp:app", err=True)
        click.echo("  - Or ensure app.py or main.py exists in current directory", err=True)
        sys.exit(1)
    except Exception as e:
        import traceback
        traceback.print_exc()
        click.echo(f"Error loading app: {e}", err=True)
        
        click.echo("\n" + "=" * 60, err=True)
        click.echo("Full traceback:", err=True)
        click.echo("=" * 60, err=True)
        traceback.print_exc()
        click.echo("=" * 60, err=True)
        
        click.echo("\nThis might be a bug in JetTask or your application.", err=True)
        click.echo("Please check the traceback above for details.", err=True)
        sys.exit(1)
    
    task_list = [t.strip() for t in tasks.split(',') if t.strip()]

    redis_url = app.redis_url if hasattr(app, 'redis_url') else 'Not configured'
    redis_prefix = app.redis_prefix if hasattr(app, 'redis_prefix') else 'jettask'

    click.echo("=" * 60)
    click.echo("JetTask Worker Configuration")
    click.echo("=" * 60)
    click.echo(f"App:          {app_str}")
    click.echo(f"Redis URL:    {redis_url}")
    click.echo(f"Redis Prefix: {redis_prefix}")
    click.echo(f"Tasks:        {', '.join(task_list)}")
    click.echo(f"Concurrency:  {concurrency}")
    click.echo(f"Prefetch:     {prefetch}")
    click.echo("=" * 60)

    try:
        click.echo(f"Starting worker...")
        app.start(
            tasks=task_list,
            concurrency=concurrency,
            prefetch_multiplier=prefetch
        )
    except KeyboardInterrupt:
        click.echo("\nShutting down worker...")
    except Exception as e:
        click.echo(f"Error starting worker: {e}", err=True)
        sys.exit(1)

@cli.command('webui-consumer')
@click.option('--task-center', '-tc', envvar='JETTASK_CENTER_URL', required=True,
              help='任务中心URL，如: http://localhost:8001 或 http://localhost:8001/api/namespaces/default')
@click.option('--check-interval', type=int, default=30,
              help='命名空间检测间隔（秒），仅多命名空间模式使用，默认30秒')
@click.option('--concurrency', '-c', type=int, default=4,
              help='并发数（每个命名空间的 worker 进程数），默认4')
@click.option('--prefetch', '-p', type=int, default=1000,
              help='预取倍数（控制每次从队列预取的消息数），默认1000')
@click.option('--debug', is_flag=True, help='启用调试模式')
def webui_consumer(task_center, check_interval, concurrency, prefetch, debug):
    import asyncio
    from jettask.persistence.manager import UnifiedConsumerManager

    async def run_manager():
        manager = UnifiedConsumerManager(
            task_center_url=task_center,
            check_interval=check_interval,
            concurrency=concurrency,
            prefetch_multiplier=prefetch,
            debug=debug
        )
        await manager.run()

    try:
        asyncio.run(run_manager())
    except KeyboardInterrupt:
        click.echo("\n✓ 消费者已关闭")


@cli.command()
@click.option('--pg-url', envvar='JETTASK_PG_URL',
              help='PostgreSQL连接URL (如: postgresql://user:pass@localhost/db)')
@async_command
async def init(pg_url):
    click.echo("Initializing JetTask...")

    import os
    from jettask.utils.db_init import init_database_async, PostgreSQLConfig
    from urllib.parse import urlparse

    if pg_url:
        os.environ['JETTASK_PG_URL'] = pg_url
        click.echo(f"Using PostgreSQL: {pg_url.split('@')[1] if '@' in pg_url else pg_url}")
    else:
        pg_url = os.environ.get('JETTASK_PG_URL')
        if not pg_url:
            click.echo("Error: 必须提供 --pg-url 或设置 JETTASK_PG_URL 环境变量", err=True)
            raise click.Abort()

    parsed = urlparse(pg_url)
    pg_config = PostgreSQLConfig(
        host=parsed.hostname or 'localhost',
        port=parsed.port or 5432,
        username=parsed.username or 'jettask',
        password=parsed.password or '123456',
        database=parsed.path.lstrip('/') if parsed.path else 'jettask'
    )

    click.echo("\nInitializing database...")
    await init_database_async(pg_config)

    click.echo("\n✓ JetTask initialized successfully!")

@cli.command()
@async_command
async def status():
    import os

    click.echo("JetTask System Status")
    click.echo("=" * 50)

    try:
        from jettask.db import get_async_redis_client
        redis_url = os.getenv('JETTASK_REDIS_URL', 'redis://localhost:6379/0')
        redis = await get_async_redis_client(redis_url, decode_responses=True)
        await redis.ping()
        await redis.aclose()
        click.echo("✓ Redis: Connected")
    except Exception as e:
        click.echo(f"✗ Redis: Not connected ({e})")

    try:
        from jettask.db import get_asyncpg_pool
        pg_url = os.getenv('JETTASK_PG_URL')
        if not pg_url:
            pg_host = os.getenv('JETTASK_PG_HOST', 'localhost')
            pg_port = os.getenv('JETTASK_PG_PORT', '5432')
            pg_user = os.getenv('JETTASK_PG_USER', 'jettask')
            pg_password = os.getenv('JETTASK_PG_PASSWORD', '123456')
            pg_db = os.getenv('JETTASK_PG_DB', 'jettask')
            pg_url = f'postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}'

        pool = await get_asyncpg_pool(pg_url)
        async with pool.acquire() as conn:
            await conn.fetchval('SELECT 1')
        await pool.close()
        click.echo("✓ PostgreSQL: Connected")
    except Exception as e:
        click.echo(f"✗ PostgreSQL: Not connected ({e})")

    click.echo("=" * 50)

@cli.command()
@click.option('--task-center', '-tc', envvar='JETTASK_CENTER_URL', required=True,
              help='任务中心URL，如: http://localhost:8001 或 http://localhost:8001/api/namespaces/default')
@click.option('--interval', '-i', type=float, default=5,
              help='调度器扫描间隔（秒），默认0.1秒')
@click.option('--batch-size', '-b', type=int, default=100,
              help='每批处理的最大任务数，默认100')
@click.option('--check-interval', type=int, default=30,
              help='命名空间检测间隔（秒），仅多命名空间模式使用，默认30秒')
@click.option('--debug', is_flag=True, help='启用调试模式')
def scheduler(task_center, interval, batch_size, check_interval, debug):
    import asyncio
    from jettask.scheduler.manager import UnifiedSchedulerManager

    async def run_manager():
        manager = UnifiedSchedulerManager(
            task_center_url=task_center,
            scan_interval=interval,
            batch_size=batch_size,
            check_interval=check_interval,
            debug=debug
        )
        await manager.run()

    try:
        asyncio.run(run_manager())
    except KeyboardInterrupt:
        click.echo("\nShutdown complete")

@cli.command()
@click.option('--port', default=8080, help='前端服务器端口')
@click.option('--host', default='0.0.0.0', help='前端服务器监听地址')
@click.option('--api-url', default='http://localhost:8001', help='后端 API 服务器地址')
@click.option('--auto-install', is_flag=True, default=True, help='自动安装缺失的依赖')
@click.option('--force-install', is_flag=True, help='强制重新安装依赖')
@click.option('--build-only', is_flag=True, help='仅构建生产版本，不启动服务器')
def frontend(port, host, api_url, auto_install, force_install, build_only):
    import subprocess
    import shutil
    from pathlib import Path
    
    frontend_dir = Path(__file__).parent.parent / "webui" / "frontend"
    if not frontend_dir.exists():
        click.echo(f"错误：前端目录不存在: {frontend_dir}", err=True)
        sys.exit(1)
    
    node_cmd = shutil.which('node')
    if not node_cmd:
        click.echo("错误：未检测到 Node.js 环境", err=True)
        click.echo("\n请先安装 Node.js:")
        click.echo("  - Ubuntu/Debian: sudo apt-get install nodejs npm")
        click.echo("  - macOS: brew install node")
        click.echo("  - Windows: 从 https://nodejs.org 下载安装")
        click.echo("  - 或使用 nvm: curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash")
        sys.exit(1)
    
    npm_cmd = shutil.which('npm')
    if not npm_cmd:
        click.echo("错误：未检测到 npm", err=True)
        click.echo("\n请安装 npm:")
        click.echo("  - Ubuntu/Debian: sudo apt-get install npm")
        click.echo("  - 或重新安装 Node.js (包含 npm)")
        sys.exit(1)
    
    try:
        node_version = subprocess.check_output([node_cmd, '--version'], text=True).strip()
        npm_version = subprocess.check_output([npm_cmd, '--version'], text=True).strip()
        click.echo(f"检测到 Node.js {node_version}, npm {npm_version}")
    except subprocess.CalledProcessError:
        pass
    
    os.chdir(frontend_dir)
    click.echo(f"前端目录: {frontend_dir}")
    
    package_json = frontend_dir / "package.json"
    if not package_json.exists():
        click.echo("错误：package.json 文件不存在", err=True)
        sys.exit(1)
    
    node_modules = frontend_dir / "node_modules"
    need_install = not node_modules.exists() or force_install
    
    if need_install and auto_install:
        click.echo("\n正在安装依赖...")
        try:
            if force_install and node_modules.exists():
                click.echo("清理旧的 node_modules...")
                shutil.rmtree(node_modules)
            
            lock_file = frontend_dir / "package-lock.json"
            if force_install and lock_file.exists():
                lock_file.unlink()
            
            subprocess.run([npm_cmd, 'install'], check=True)
            click.echo("✓ 依赖安装完成")
        except subprocess.CalledProcessError as e:
            click.echo(f"错误：依赖安装失败 - {e}", err=True)
            click.echo("\n可以尝试:")
            click.echo("  1. 手动删除 node_modules 目录后重试")
            click.echo("  2. 使用 --force-install 参数强制重新安装")
            click.echo("  3. 检查网络连接和 npm 源设置")
            sys.exit(1)
    elif need_install and not auto_install:
        click.echo("警告：未检测到 node_modules，请运行 'npm install' 安装依赖")
        if not click.confirm("是否现在安装依赖？"):
            sys.exit(1)
    
    try:
        dist_dir = frontend_dir.parent / "static" / "dist"
        
        need_build = not dist_dir.exists() or build_only
        
        if need_build:
            click.echo("\n正在构建生产版本...")
            subprocess.run([npm_cmd, 'run', 'build'], check=True)
            
            if dist_dir.exists():
                files = list(dist_dir.rglob('*'))
                file_count = len([f for f in files if f.is_file()])
                total_size = sum(f.stat().st_size for f in files if f.is_file())
                click.echo(f"\n✓ 构建完成！")
                click.echo(f"  - 输出目录: {dist_dir}")
                click.echo(f"  - 文件数量: {file_count}")
                click.echo(f"  - 总大小: {total_size / 1024 / 1024:.2f} MB")
            else:
                click.echo("错误：构建失败，未生成输出目录", err=True)
                sys.exit(1)
        
        if not build_only:
            if not dist_dir.exists():
                click.echo("错误：未找到构建输出，请先运行构建", err=True)
                sys.exit(1)
            
            click.echo(f"\n正在启动生产版本服务器...")
            click.echo(f"  - 访问地址: http://localhost:{port}")
            if host != 'localhost':
                click.echo(f"  - 网络地址: http://{host}:{port}")
            click.echo(f"  - 静态文件: {dist_dir}")
            click.echo(f"  - API 地址: {api_url}")
            click.echo("\n按 Ctrl+C 停止服务器\n")
            
            import http.server
            import socketserver
            import urllib.request
            
            class ProxyHandler(http.server.SimpleHTTPRequestHandler):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, directory=str(dist_dir), **kwargs)
                
                def proxy_request(self, method='GET', body=None):
                    if self.path.startswith('/api/') or self.path.startswith('/ws/'):
                        target_url = api_url + self.path
                        
                        try:
                            req = urllib.request.Request(target_url, method=method)
                            
                            for header, value in self.headers.items():
                                if header.lower() not in ['host', 'connection']:
                                    req.add_header(header, value)
                            
                            if body:
                                req.data = body
                            
                            with urllib.request.urlopen(req, timeout=30) as response:
                                self.send_response(response.getcode())
                                for header, value in response.headers.items():
                                    if header.lower() not in ['connection', 'transfer-encoding']:
                                        self.send_header(header, value)
                                self.end_headers()
                                self.wfile.write(response.read())
                            return True
                            
                        except urllib.error.HTTPError as e:
                            self.send_response(e.code)
                            self.end_headers()
                            self.wfile.write(e.read())
                            return True
                        except Exception as e:
                            self.send_error(502, f"Bad Gateway: {str(e)}")
                            return True
                    return False
                
                def do_GET(self):
                    if self.proxy_request('GET'):
                        return
                    
                    if self.path == '/' or self.path == '/index.html' or (
                        self.path != '/' and not Path(dist_dir / self.path[1:]).exists()
                    ):
                        index_path = dist_dir / 'index.html'
                        if index_path.exists():
                            with open(index_path, 'r', encoding='utf-8') as f:
                                html_content = f.read()
                            
                            api_config = f'''
                            <script>
                                window.JETTASK_API_URL = '';  // 使用相对路径，由服务器代理
                                console.log('API requests will be proxied by server');
                            </script>
                            '''
                            
                            html_content = html_content.replace('</head>', api_config + '</head>')
                            
                            self.send_response(200)
                            self.send_header('Content-type', 'text/html')
                            self.send_header('Content-Length', str(len(html_content.encode('utf-8'))))
                            self.end_headers()
                            self.wfile.write(html_content.encode('utf-8'))
                            return
                    
                    return super().do_GET()
                
                def do_POST(self):
                    content_length = int(self.headers.get('Content-Length', 0))
                    body = self.rfile.read(content_length) if content_length > 0 else None
                    
                    if self.proxy_request('POST', body):
                        return
                    
                    self.send_error(405, "Method Not Allowed")
                
                def do_PUT(self):
                    content_length = int(self.headers.get('Content-Length', 0))
                    body = self.rfile.read(content_length) if content_length > 0 else None
                    if self.proxy_request('PUT', body):
                        return
                    self.send_error(405, "Method Not Allowed")
                
                def do_DELETE(self):
                    if self.proxy_request('DELETE'):
                        return
                    self.send_error(405, "Method Not Allowed")
                
                def log_message(self, format, *args):
                    click.echo(f"[{self.log_date_time_string()}] {format % args}")
            
            class ReuseAddrTCPServer(socketserver.TCPServer):
                allow_reuse_address = True
                allow_reuse_port = True
            
            try:
                click.echo(f"正在绑定到 {host}:{port}...")
                httpd = ReuseAddrTCPServer((host, port), ProxyHandler)
                click.echo(f"✓ 服务器已启动，监听 {host}:{port}")
                click.echo(f"✓ API 请求将被代理到 {api_url}")
                httpd.serve_forever()
            except OSError as e:
                if e.errno == 98:  
                    click.echo(f"错误：端口 {port} 已被占用，请尝试其他端口", err=True)
                else:
                    click.echo(f"错误：{e}", err=True)
                sys.exit(1)
            except KeyboardInterrupt:
                pass
    except subprocess.CalledProcessError as e:
        click.echo(f"错误：命令执行失败 - {e}", err=True)
        sys.exit(1)
    except KeyboardInterrupt:
        click.echo("\n停止前端服务器")

def main():
    try:
        cli()
    except KeyboardInterrupt:
        click.echo("\nOperation cancelled by user")
        sys.exit(0)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

if __name__ == '__main__':
    main()