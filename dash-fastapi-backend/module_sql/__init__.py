"""
通用数据库连接池模块

快速开始:
1. 初始化连接池
   from module_sql import init_pool, init_mysql_tool, get_mysql_tool
   
   config = {
       'host': 'localhost',
       'port': 3306,
       'user': 'root',
       'password': '123456',
       'database': 'test'
   }
   
   # 初始化连接池
   pool = init_pool(config)
   
   # 初始化MySQL工具
   mysql_tool = init_mysql_tool(pool)
   
2. 使用MySQL工具进行数据库操作
   # 查询数据
   user = mysql_tool.query_one("SELECT * FROM users WHERE id = %s", (1,))
   
   # 插入数据
   affected_rows = mysql_tool.execute("INSERT INTO users (name, age) VALUES (%s, %s)", ("张三", 25))

模块组成:
- db_connection_pool: 通用数据库连接池实现
- mysql_tool: MySQL数据库操作工具类
"""

from .db_connection_pool import init_pool, get_global_pool, BaseConnectionPool, MySQLConnectionPool
from .mysql_tool import MySQLTool, init_mysql_tool, get_mysql_tool
from .pool_init import init_project_pool, get_project_db_tool

__version__ = "1.0.0"
__author__ = "Dash-FastAPI-Admin"

__all__ = [
    "init_pool",
    "get_global_pool",
    "BaseConnectionPool",
    "MySQLConnectionPool",
    "MySQLTool",
    "init_mysql_tool",
    "get_mysql_tool",
    "init_project_pool",
    "get_project_db_tool"
]
