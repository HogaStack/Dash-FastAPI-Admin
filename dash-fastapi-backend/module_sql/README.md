# 通用数据库连接池模块

## 概述

这是一个基于Python 3.8+开发的通用数据库连接池模块，主要解决数据库连接复用、并发控制、资源释放等问题。目前支持MySQL数据库，并预留了其他数据库的扩展接口。

## 核心特性

### 1. 基础连接池能力
- **连接复用**：避免频繁创建和销毁数据库连接，提升性能
- **空闲连接管理**：自动维护最小/最大空闲连接数
- **最大连接数限制**：防止连接耗尽数据库资源
- **连接超时控制**：自动清理空闲超时的连接
- **自动重连**：连接失败时自动重试
- **配置化初始化**：支持通过字典参数或配置文件传入连接参数

### 2. 线程安全

完全支持多线程并发访问，使用线程锁避免并发冲突。

### 3. 异常处理

完善的异常处理机制，包括：
- 连接异常处理
- 资源耗尽处理
- 无效连接自动检测
- 详细的日志记录

## 模块结构

```
module_sql/
├── __init__.py              # 模块导入文件
├── db_connection_pool.py    # 连接池核心实现
├── mysql_tool.py            # MySQL操作工具类
├── pool_init.py             # 项目集成初始化
└── README.md               # 文档说明
```

## 安装依赖

```bash
pip install PyMySQL>=1.1.1
```

## 使用方法

### 快速开始

#### 方式一：手动初始化

```python
from module_sql import init_pool, init_mysql_tool

# 配置连接池
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
    'retry_times': 3,
    'blocking': True,
    'wait_timeout': 60
}

# 初始化连接池
pool = init_pool(config)

# 初始化MySQL工具
mysql_tool = init_mysql_tool(pool)
```

#### 方式二：项目集成初始化

使用项目现有的配置自动初始化：

```python
from module_sql import get_project_db_tool

# 获取全局数据库工具实例
mysql_tool = get_project_db_tool()
```

### 数据库操作示例

#### 1. 插入数据

```python
# 插入单条数据
sql = "INSERT INTO users (name, age, email) VALUES (%s, %s, %s)"
affected_rows = mysql_tool.execute(sql, ("张三", 25, "zhangsan@example.com"))

# 批量插入数据
users = [
    ("李四", 28, "lisi@example.com"),
    ("王五", 30, "wangwu@example.com")
]
affected_rows = mysql_tool.execute_many(sql, users)
```

#### 2. 查询数据

```python
# 查询单条数据
user = mysql_tool.query_one("SELECT * FROM users WHERE id = %s", (1,))

# 查询所有数据
all_users = mysql_tool.query_all("SELECT * FROM users ORDER BY create_time DESC")

# 分页查询
page_users, total = mysql_tool.query_page(
    "SELECT * FROM users ORDER BY create_time DESC", 
    page=1, 
    page_size=10
)
```

#### 3. 更新数据

```python
sql = "UPDATE users SET age = %s WHERE id = %s"
affected_rows = mysql_tool.execute(sql, (26, 1))
```

#### 4. 删除数据

```python
sql = "DELETE FROM users WHERE id = %s"
affected_rows = mysql_tool.execute(sql, (1,))
```

#### 5. 事务操作

```python
# 开始事务
conn = mysql_tool.begin_transaction()

try:
    with conn.cursor() as cursor:
        cursor.execute("INSERT INTO users (name, age) VALUES (%s, %s)", ("赵六", 22))
        cursor.execute("INSERT INTO users (name, age) VALUES (%s, %s)", ("孙七", 24))
    # 提交事务
    mysql_tool.commit_transaction(conn)
except Exception as e:
    # 回滚事务
    mysql_tool.rollback_transaction(conn)
    print(f"事务失败: {e}")
```

#### 6. 表操作

```python
# 创建表
columns = {
    'id': 'INT AUTO_INCREMENT PRIMARY KEY',
    'name': 'VARCHAR(255) NOT NULL',
    'age': 'INT DEFAULT 0',
    'create_time': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
}
mysql_tool.create_table('users', columns)

# 删除表
mysql_tool.drop_table('users')
```

### 连接池管理

```python
# 获取连接池状态
status = pool.get_status()
print(status)

# 关闭连接池
pool.close()
```

## 配置参数说明

### 必选参数

| 参数名 | 说明 | 默认值 |
|--------|------|--------|
| host | 数据库地址 | localhost |
| port | 数据库端口 | 3306 |
| user | 数据库用户名 | root |
| password | 数据库密码 | 空字符串 |
| database | 数据库名 | 空字符串 |

### 连接池参数

| 参数名 | 说明 | 默认值 |
|--------|------|--------|
| max_connections | 最大连接数 | 10 |
| min_idle_connections | 最小空闲连接数 | 2 |
| max_idle_connections | 最大空闲连接数 | 5 |
| idle_timeout | 空闲连接超时时间（秒） | 300 |
| connect_timeout | 连接数据库超时时间（秒） | 10 |
| retry_times | 连接失败自动重试次数 | 3 |
| blocking | 无可用连接时是否阻塞等待 | True |
| wait_timeout | 阻塞等待超时时间（秒） | 60 |

## 扩展开发

### 添加新的数据库支持

继承`BaseConnectionPool`抽象类并实现以下方法：

```python
class PostgreSQLConnectionPool(BaseConnectionPool):
    def _create_connection(self) -> Optional[Connection]:
        # 实现PostgreSQL连接创建逻辑
        pass
    
    def _validate_connection(self, conn: Connection) -> bool:
        # 实现PostgreSQL连接验证逻辑
        pass
```

### 自定义钩子方法

可以重写以下方法来自定义连接池行为：

- `_initialize_idle_connections()`: 自定义初始化逻辑
- `_cleanup_idle_connections()`: 自定义空闲连接清理逻辑

## 设计规范

### 1. 模块化设计

模块之间低耦合，便于复用和扩展：
- 连接池核心逻辑与数据库实现分离
- 操作工具类与连接池分离

### 2. 资源自动管理

- 连接超时自动关闭
- 进程退出时自动释放所有连接
- 使用`with`语句确保资源自动释放

### 3. 代码规范

严格遵循PEP 8规范：
- 清晰的命名规范
- 详细的文档字符串
- 完善的异常处理

## 性能优化

1. **连接复用**：减少TCP握手和认证开销
2. **空闲连接管理**：保持适当的空闲连接数，平衡响应速度和资源占用
3. **并发控制**：通过队列和线程锁确保线程安全
4. **无效连接检测**：自动剔除无效连接，避免业务出错

## 异常处理

模块会自动处理以下异常场景：

1. **连接失败**：自动重试指定次数
2. **连接超时**：自动清理超时连接
3. **资源耗尽**：根据blocking参数决定阻塞等待或快速失败
4. **无效连接**：自动检测并替换无效连接

## 日志

模块提供详细的日志记录，可以通过以下方式调整日志级别：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 最佳实践

1. **合理设置连接池参数**：根据业务并发量调整max_connections
2. **及时归还连接**：使用完毕后确保连接归还到连接池
3. **使用事务批量操作**：减少网络交互次数
4. **监控连接池状态**：定期检查连接池使用情况
5. **避免长时间占用连接**：长事务会影响连接池可用性
