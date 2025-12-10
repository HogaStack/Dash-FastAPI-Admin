import logging
from typing import List, Dict, Optional, Any, Tuple
import pymysql
from pymysql.cursors import DictCursor
from .db_connection_pool import get_global_pool, BaseConnectionPool

# 配置日志
logger = logging.getLogger(__name__)


class MySQLTool:
    """
    MySQL数据库操作工具类
    基于连接池封装常用的数据库操作
    """
    def __init__(self, pool: Optional[BaseConnectionPool] = None):
        """
        初始化MySQL工具类
        :param pool: 连接池实例，如果不提供则使用全局连接池
        """
        self.pool = pool or get_global_pool()
        if not self.pool:
            raise RuntimeError("连接池未初始化，请先调用init_pool初始化连接池")
    
    def execute(self, sql: str, params: Optional[Tuple[Any, ...]] = None) -> int:
        """
        执行SQL语句（INSERT/UPDATE/DELETE）
        :param sql: SQL语句
        :param params: SQL参数
        :return: 受影响的行数
        """
        conn = None
        try:
            conn = self.pool.get_connection()
            if not conn:
                raise RuntimeError("无法获取数据库连接")
            
            with conn.cursor() as cursor:
                affected_rows = cursor.execute(sql, params)
                conn.commit()
                logger.info(f"执行SQL成功，受影响行数: {affected_rows}")
                return affected_rows
                
        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                except Exception as rollback_err:
                    logger.error(f"回滚事务失败: {str(rollback_err)}")
            logger.error(f"执行SQL失败: {str(e)}, SQL: {sql}, params: {params}")
            raise
            
        finally:
            if conn:
                self.pool.release_connection(conn)
    
    def execute_many(self, sql: str, params_list: List[Tuple[Any, ...]]) -> int:
        """
        批量执行SQL语句
        :param sql: SQL语句
        :param params_list: 参数列表
        :return: 受影响的行数
        """
        conn = None
        try:
            conn = self.pool.get_connection()
            if not conn:
                raise RuntimeError("无法获取数据库连接")
            
            with conn.cursor() as cursor:
                affected_rows = cursor.executemany(sql, params_list)
                conn.commit()
                logger.info(f"批量执行SQL成功，受影响行数: {affected_rows}")
                return affected_rows
                
        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                except Exception as rollback_err:
                    logger.error(f"回滚事务失败: {str(rollback_err)}")
            logger.error(f"批量执行SQL失败: {str(e)}, SQL: {sql}")
            raise
            
        finally:
            if conn:
                self.pool.release_connection(conn)
    
    def query_one(self, sql: str, params: Optional[Tuple[Any, ...]] = None) -> Optional[Dict[str, Any]]:
        """
        查询单条记录
        :param sql: SQL查询语句
        :param params: SQL参数
        :return: 查询结果字典，如果没有结果则返回None
        """
        conn = None
        try:
            conn = self.pool.get_connection()
            if not conn:
                raise RuntimeError("无法获取数据库连接")
            
            with conn.cursor(DictCursor) as cursor:
                cursor.execute(sql, params)
                result = cursor.fetchone()
                logger.info(f"查询单条记录成功，结果: {result}")
                return result
                
        except Exception as e:
            logger.error(f"查询单条记录失败: {str(e)}, SQL: {sql}, params: {params}")
            raise
            
        finally:
            if conn:
                self.pool.release_connection(conn)
    
    def query_all(self, sql: str, params: Optional[Tuple[Any, ...]] = None) -> List[Dict[str, Any]]:
        """
        查询多条记录
        :param sql: SQL查询语句
        :param params: SQL参数
        :return: 查询结果列表
        """
        conn = None
        try:
            conn = self.pool.get_connection()
            if not conn:
                raise RuntimeError("无法获取数据库连接")
            
            with conn.cursor(DictCursor) as cursor:
                cursor.execute(sql, params)
                results = cursor.fetchall()
                logger.info(f"查询多条记录成功，共 {len(results)} 条结果")
                return results
                
        except Exception as e:
            logger.error(f"查询多条记录失败: {str(e)}, SQL: {sql}, params: {params}")
            raise
            
        finally:
            if conn:
                self.pool.release_connection(conn)
    
    def query_page(self, sql: str, params: Optional[Tuple[Any, ...]] = None, 
                   page: int = 1, page_size: int = 10) -> Tuple[List[Dict[str, Any]], int]:
        """
        分页查询
        :param sql: SQL查询语句
        :param params: SQL参数
        :param page: 页码
        :param page_size: 每页大小
        :return: (查询结果列表, 总记录数)
        """
        # 计算总记录数
        count_sql = f"SELECT COUNT(*) as total FROM ({sql}) as temp"
        count_result = self.query_one(count_sql, params)
        total = count_result.get('total', 0) if count_result else 0
        
        # 分页查询
        offset = (page - 1) * page_size
        page_sql = f"{sql} LIMIT %s OFFSET %s"
        page_params = tuple(params) + (page_size, offset) if params else (page_size, offset)
        results = self.query_all(page_sql, page_params)
        
        return results, total
    
    def begin_transaction(self) -> Any:
        """
        开始事务
        :return: 数据库连接对象
        """
        conn = self.pool.get_connection()
        if not conn:
            raise RuntimeError("无法获取数据库连接")
        conn.autocommit(False)
        return conn
    
    def commit_transaction(self, conn: Any):
        """
        提交事务
        :param conn: 数据库连接对象
        """
        try:
            conn.commit()
            logger.info("事务提交成功")
        except Exception as e:
            logger.error(f"提交事务失败: {str(e)}")
            raise
        finally:
            self.pool.release_connection(conn)
    
    def rollback_transaction(self, conn: Any):
        """
        回滚事务
        :param conn: 数据库连接对象
        """
        try:
            conn.rollback()
            logger.info("事务回滚成功")
        except Exception as e:
            logger.error(f"回滚事务失败: {str(e)}")
            raise
        finally:
            self.pool.release_connection(conn)
    
    def create_table(self, table_name: str, columns: Dict[str, str]) -> bool:
        """
        创建表
        :param table_name: 表名
        :param columns: 列定义字典，格式: {列名: 列类型}
        :return: 是否创建成功
        """
        columns_def = [f"`{col}` {typ}" for col, typ in columns.items()]
        create_sql = f"CREATE TABLE IF NOT EXISTS `{table_name}` ({', '.join(columns_def)})"
        
        try:
            self.execute(create_sql)
            logger.info(f"表 {table_name} 创建成功")
            return True
        except Exception as e:
            logger.error(f"创建表 {table_name} 失败: {str(e)}")
            return False
    
    def drop_table(self, table_name: str) -> bool:
        """
        删除表
        :param table_name: 表名
        :return: 是否删除成功
        """
        drop_sql = f"DROP TABLE IF EXISTS `{table_name}`"
        
        try:
            self.execute(drop_sql)
            logger.info(f"表 {table_name} 删除成功")
            return True
        except Exception as e:
            logger.error(f"删除表 {table_name} 失败: {str(e)}")
            return False


# 全局MySQL工具实例
_global_mysql_tool: Optional[MySQLTool] = None


def init_mysql_tool(pool: Optional[BaseConnectionPool] = None) -> MySQLTool:
    """
    初始化全局MySQL工具实例
    :param pool: 连接池实例，如果不提供则使用全局连接池
    :return: MySQLTool实例
    """
    global _global_mysql_tool
    _global_mysql_tool = MySQLTool(pool)
    return _global_mysql_tool


def get_mysql_tool() -> Optional[MySQLTool]:
    """
    获取全局MySQL工具实例
    :return: MySQLTool实例
    """
    return _global_mysql_tool


if __name__ == "__main__":
    """使用示例"""
    from .db_connection_pool import init_pool
    
    # 初始化连接池
    config = {
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': '123456',
        'database': 'test',
        'max_connections': 10,
        'min_idle_connections': 2
    }
    
    try:
        # 初始化连接池和工具类
        pool = init_pool(config)
        mysql_tool = init_mysql_tool(pool)
        
        # 创建测试表
        columns = {
            'id': 'INT AUTO_INCREMENT PRIMARY KEY',
            'name': 'VARCHAR(255) NOT NULL',
            'age': 'INT DEFAULT 0',
            'email': 'VARCHAR(255) UNIQUE',
            'create_time': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
        }
        mysql_tool.create_table('test_users', columns)
        
        # 插入单条数据
        insert_sql = "INSERT INTO test_users (name, age, email) VALUES (%s, %s, %s)"
        affected_rows = mysql_tool.execute(insert_sql, ("张三", 25, "zhangsan@example.com"))
        print(f"插入数据成功，受影响行数: {affected_rows}")
        
        # 批量插入数据
        users = [
            ("李四", 28, "lisi@example.com"),
            ("王五", 30, "wangwu@example.com"),
            ("赵六", 22, "zhaoliu@example.com")
        ]
        affected_rows = mysql_tool.execute_many(insert_sql, users)
        print(f"批量插入数据成功，受影响行数: {affected_rows}")
        
        # 查询单条数据
        user = mysql_tool.query_one("SELECT * FROM test_users WHERE name = %s", ("张三",))
        print("查询单条用户:", user)
        
        # 查询所有数据
        all_users = mysql_tool.query_all("SELECT * FROM test_users ORDER BY create_time DESC")
        print(f"查询所有用户，共 {len(all_users)} 条:", all_users)
        
        # 分页查询
        page_users, total = mysql_tool.query_page("SELECT * FROM test_users ORDER BY create_time DESC", page=1, page_size=2)
        print(f"分页查询第1页，共 {total} 条记录:", page_users)
        
        # 更新数据
        update_sql = "UPDATE test_users SET age = %s WHERE name = %s"
        affected_rows = mysql_tool.execute(update_sql, (26, "张三"))
        print(f"更新数据成功，受影响行数: {affected_rows}")
        
        # 删除数据
        delete_sql = "DELETE FROM test_users WHERE name = %s"
        affected_rows = mysql_tool.execute(delete_sql, ("赵六",))
        print(f"删除数据成功，受影响行数: {affected_rows}")
        
        # 事务操作示例
        conn = mysql_tool.begin_transaction()
        try:
            with conn.cursor() as cursor:
                cursor.execute(insert_sql, ("钱七", 35, "qianqi@example.com"))
                cursor.execute(insert_sql, ("孙八", 29, "sunba@example.com"))
            mysql_tool.commit_transaction(conn)
            print("事务提交成功")
        except Exception as e:
            mysql_tool.rollback_transaction(conn)
            print(f"事务回滚: {str(e)}")
            
    except Exception as e:
        logger.error(f"测试出错: {str(e)}")
    finally:
        # 关闭连接池
        if pool:
            pool.close()
