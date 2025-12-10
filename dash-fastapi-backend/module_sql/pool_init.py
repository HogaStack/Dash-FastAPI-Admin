"""
连接池初始化集成模块
用于将连接池与现有项目配置集成
"""
from config.env import DataBaseConfig
from .db_connection_pool import init_pool, get_global_pool
from .mysql_tool import init_mysql_tool, get_mysql_tool

def init_project_pool():
    """
    使用项目配置初始化连接池
    :return: 连接池实例和MySQL工具实例
    """
    if DataBaseConfig.db_type != 'mysql':
        raise ValueError(f"当前数据库类型 {DataBaseConfig.db_type} 不支持连接池，仅支持mysql")
    
    # 从项目配置中获取连接池参数
    config = {
        'host': DataBaseConfig.db_host,
        'port': DataBaseConfig.db_port,
        'user': DataBaseConfig.db_username,
        'password': DataBaseConfig.db_password,
        'database': DataBaseConfig.db_database,
        'max_connections': DataBaseConfig.db_pool_size + DataBaseConfig.db_max_overflow,
        'min_idle_connections': DataBaseConfig.db_pool_size,
        'max_idle_connections': DataBaseConfig.db_pool_size,
        'idle_timeout': DataBaseConfig.db_pool_recycle,
        'connect_timeout': DataBaseConfig.db_pool_timeout,
        'retry_times': 3,
        'blocking': True,
        'wait_timeout': DataBaseConfig.db_pool_timeout
    }
    
    # 初始化连接池
    pool = init_pool(config)
    
    # 初始化MySQL工具
    mysql_tool = init_mysql_tool(pool)
    
    return pool, mysql_tool

def get_project_db_tool():
    """
    获取项目全局数据库工具实例
    :return: MySQLTool实例
    """
    mysql_tool = get_mysql_tool()
    if not mysql_tool:
        # 如果未初始化，则自动初始化
        init_project_pool()
        mysql_tool = get_mysql_tool()
    return mysql_tool


# 初始化连接池
pool, mysql_tool = init_project_pool()
