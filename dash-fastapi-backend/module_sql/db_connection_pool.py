import abc
import queue
import threading
import time
import logging
from typing import Dict, Optional, Any, TypeVar
import pymysql
from pymysql.connections import Connection

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

T = TypeVar('T', bound=Connection)


class BaseConnectionPool(metaclass=abc.ABCMeta):
    """
    数据库连接池抽象基类
    定义连接池的核心接口和通用逻辑
    """
    def __init__(self, config: Dict[str, Any]):
        # 数据库连接基础参数
        self.host = config.get('host', 'localhost')
        self.port = config.get('port', 3306)
        self.user = config.get('user', 'root')
        self.password = config.get('password', '')
        self.database = config.get('database', '')
        
        # 连接池配置参数
        self.max_connections = config.get('max_connections', 10)
        self.min_idle_connections = config.get('min_idle_connections', 2)
        self.max_idle_connections = config.get('max_idle_connections', 5)
        self.idle_timeout = config.get('idle_timeout', 300)  # 5分钟
        self.connect_timeout = config.get('connect_timeout', 10)
        self.retry_times = config.get('retry_times', 3)
        self.blocking = config.get('blocking', True)
        self.wait_timeout = config.get('wait_timeout', 60)
        
        # 连接池状态
        self._connection_queue: queue.Queue = queue.Queue(maxsize=self.max_connections)
        self._total_connections = 0
        self._lock = threading.Lock()
        self._closed = False
        
        # 初始化最小空闲连接
        self._initialize_idle_connections()
        
        # 启动空闲连接清理线程
        self._cleanup_thread = threading.Thread(target=self._cleanup_idle_connections, daemon=True)
        self._cleanup_thread.start()
    
    def _initialize_idle_connections(self):
        """初始化最小空闲连接"""
        for _ in range(self.min_idle_connections):
            try:
                conn = self._create_connection()
                if conn:
                    self._connection_queue.put((conn, time.time()))
            except Exception as e:
                logger.error(f"初始化空闲连接失败: {str(e)}")
    
    @abc.abstractmethod
    def _create_connection(self) -> Optional[T]:
        """创建数据库连接（抽象方法，子类实现）"""
        pass
    
    @abc.abstractmethod
    def _validate_connection(self, conn: T) -> bool:
        """验证连接是否有效（抽象方法，子类实现）"""
        pass
    
    def _cleanup_idle_connections(self):
        """定期清理空闲超时的连接"""
        while not self._closed:
            try:
                time.sleep(30)  # 每30秒检查一次
                current_time = time.time()
                new_queue = queue.Queue(maxsize=self.max_connections)
                
                # 遍历所有连接，清理超时连接
                while not self._connection_queue.empty():
                    conn, create_time = self._connection_queue.get()
                    if current_time - create_time < self.idle_timeout:
                        new_queue.put((conn, create_time))
                    else:
                        try:
                            conn.close()
                            logger.info(f"清理空闲超时连接")
                            with self._lock:
                                self._total_connections -= 1
                        except Exception as e:
                            logger.error(f"关闭超时连接失败: {str(e)}")
                
                self._connection_queue = new_queue
                
                # 补充最小空闲连接
                while (self._connection_queue.qsize() < self.min_idle_connections and
                       self._total_connections < self.max_connections):
                    try:
                        conn = self._create_connection()
                        if conn:
                            self._connection_queue.put((conn, current_time))
                    except Exception as e:
                        logger.error(f"补充空闲连接失败: {str(e)}")
                        break
                        
            except Exception as e:
                logger.error(f"清理空闲连接线程出错: {str(e)}")
    
    def get_connection(self) -> Optional[T]:
        """
        获取数据库连接
        :return: 数据库连接对象，如果获取失败则返回None
        """
        if self._closed:
            logger.error("连接池已关闭，无法获取连接")
            return None
        
        start_time = time.time()
        
        while True:
            try:
                # 尝试从连接队列获取连接
                if not self._connection_queue.empty():
                    conn, create_time = self._connection_queue.get()
                    
                    # 验证连接是否有效
                    if self._validate_connection(conn):
                        return conn
                    else:
                        # 连接无效则关闭并创建新连接
                        try:
                            conn.close()
                            with self._lock:
                                self._total_connections -= 1
                        except Exception as e:
                            logger.error(f"关闭无效连接失败: {str(e)}")
                
                # 如果没有可用连接，尝试创建新连接
                with self._lock:
                    if self._total_connections < self.max_connections:
                        conn = self._create_connection()
                        if conn:
                            return conn
                
                # 如果无法创建新连接，根据blocking参数决定是否等待
                if not self.blocking:
                    logger.warning("连接池已满，无法获取连接")
                    return None
                
                # 等待新连接可用
                wait_time = time.time() - start_time
                if wait_time >= self.wait_timeout:
                    logger.error("获取连接超时")
                    return None
                
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"获取连接失败: {str(e)}")
                return None
    
    def release_connection(self, conn: T):
        """
        归还数据库连接到连接池
        :param conn: 要归还的数据库连接对象
        """
        if self._closed:
            try:
                conn.close()
            except Exception as e:
                logger.error(f"关闭连接失败: {str(e)}")
            return
        
        try:
            if self._validate_connection(conn):
                if self._connection_queue.qsize() < self.max_idle_connections:
                    self._connection_queue.put((conn, time.time()))
                else:
                    # 如果空闲连接数已满，则直接关闭
                    conn.close()
                    with self._lock:
                        self._total_connections -= 1
            else:
                # 连接无效，直接关闭
                conn.close()
                with self._lock:
                    self._total_connections -= 1
        except Exception as e:
            logger.error(f"归还连接失败: {str(e)}")
            try:
                conn.close()
                with self._lock:
                    self._total_connections -= 1
            except:
                pass
    
    def close(self):
        """关闭连接池，释放所有连接"""
        self._closed = True
        
        # 关闭所有连接
        while not self._connection_queue.empty():
            conn, _ = self._connection_queue.get()
            try:
                conn.close()
            except Exception as e:
                logger.error(f"关闭连接失败: {str(e)}")
        
        with self._lock:
            self._total_connections = 0
        
        logger.info("连接池已关闭，所有连接已释放")
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取连接池状态
        :return: 连接池状态字典
        """
        with self._lock:
            return {
                'total_connections': self._total_connections,
                'idle_connections': self._connection_queue.qsize(),
                'max_connections': self.max_connections,
                'min_idle_connections': self.min_idle_connections,
                'max_idle_connections': self.max_idle_connections,
                'closed': self._closed
            }
    
    def __del__(self):
        """析构函数，确保连接池关闭"""
        if not self._closed:
            self.close()


class MySQLConnectionPool(BaseConnectionPool):
    """
    MySQL数据库连接池实现
    """
    def _create_connection(self) -> Optional[Connection]:
        """创建MySQL数据库连接"""
        for attempt in range(self.retry_times):
            try:
                conn = pymysql.connect(
                    host=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                    database=self.database,
                    connect_timeout=self.connect_timeout,
                    autocommit=True,
                    cursorclass=pymysql.cursors.DictCursor
                )
                
                with self._lock:
                    self._total_connections += 1
                
                logger.info(f"成功创建MySQL连接，当前总连接数: {self._total_connections}")
                return conn
                
            except Exception as e:
                logger.error(f"第 {attempt + 1} 次创建MySQL连接失败: {str(e)}")
                if attempt < self.retry_times - 1:
                    time.sleep(1)  # 重试前等待1秒
        
        logger.error(f"尝试 {self.retry_times} 次后仍无法创建MySQL连接")
        return None
    
    def _validate_connection(self, conn: Connection) -> bool:
        """验证MySQL连接是否有效"""
        try:
            # 通过执行简单SQL验证连接
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            return True
        except Exception as e:
            logger.warning(f"MySQL连接无效: {str(e)}")
            return False


# 全局连接池实例
_global_pool: Optional[BaseConnectionPool] = None


def init_pool(config: Dict[str, Any], db_type: str = "mysql") -> BaseConnectionPool:
    """
    初始化全局连接池
    :param config: 连接池配置
    :param db_type: 数据库类型，目前支持mysql
    :return: 连接池实例
    """
    global _global_pool
    
    if _global_pool is not None and not _global_pool._closed:
        logger.warning("连接池已初始化，将关闭现有连接池并重新初始化")
        _global_pool.close()
    
    if db_type.lower() == "mysql":
        _global_pool = MySQLConnectionPool(config)
    else:
        raise ValueError(f"不支持的数据库类型: {db_type}")
    
    return _global_pool


def get_global_pool() -> Optional[BaseConnectionPool]:
    """
    获取全局连接池实例
    :return: 全局连接池实例
    """
    return _global_pool


if __name__ == "__main__":
    """使用示例"""
    print("=== 数据库连接池模块演示 ===")
    
    # 配置示例
    config = {
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': '123456',
        'database': 'test',
        'max_connections': 10,
        'min_idle_connections': 2,
        'max_idle_connections': 5,
        'idle_timeout': 300,
        'connect_timeout': 10,
        'retry_times': 2,
        'blocking': True,
        'wait_timeout': 60
    }
    
    print("\n1. 连接池配置参数:")
    for key, value in config.items():
        print(f"   {key}: {value}")
    
    print("\n2. 连接池核心功能说明:")
    print("   - 支持连接复用，避免频繁创建销毁连接")
    print("   - 自动管理空闲连接，维持最小空闲连接数")
    print("   - 最大连接数限制，防止数据库连接耗尽")
    print("   - 连接超时自动清理，释放无用连接")
    print("   - 连接失败自动重试，提升系统可用性")
    print("   - 完全线程安全，支持高并发场景")
    
    print("\n3. 使用示例代码:")
    print("""
# 初始化连接池
pool = init_pool(config)

# 获取连接
conn = pool.get_connection()
if conn:
    try:
        # 执行SQL
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE id = %s", (1,))
            result = cursor.fetchone()
    finally:
        # 归还连接
        pool.release_connection(conn)

# 关闭连接池
pool.close()
    """)
    
    print("\n4. 集成到现有项目:")
    print("""
from module_sql import get_project_db_tool

# 获取全局数据库工具实例
mysql_tool = get_project_db_tool()

# 查询数据
user = mysql_tool.query_one("SELECT * FROM users WHERE id = %s", (1,))
    """)
    print("\n=== 演示结束 ===")
