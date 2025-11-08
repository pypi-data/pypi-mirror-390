# weibo-cli

简洁的微博 API 异步客户端。类型安全，自动认证，开箱即用。

## 安装

```bash
uv pip install -e .
```

## 快速开始

```python
import asyncio
from weibo_cli import WeiboClient

async def main():
    async with WeiboClient() as client:
        # 获取用户信息
        user = await client.get_user("1749127163")
        print(f"用户: {user.screen_name}")

        # 获取用户微博
        posts = await client.get_user_posts("1749127163", page=1)
        print(f"微博数: {len(posts)}")

        # 获取微博详情
        post = await client.get_post("5226761046462968")
        print(f"内容: {post.text}")

        # 获取评论
        comments = await client.get_post_comments("5226761046462968")
        print(f"评论数: {len(comments)}")

asyncio.run(main())
```

## API

### WeiboClient

**异步上下文管理器，自动处理连接生命周期。**

```python
async with WeiboClient(cookies=None, config=None, logger=None) as client:
    ...
```

#### 参数
- `cookies`: 可选的 Cookie 字符串
- `config`: `WeiboConfig` 实例，默认使用标准配置
- `logger`: 自定义 logger，默认使用模块 logger

#### 方法

**`await get_user(user_id: str) -> User`**

获取用户资料。

**`await get_user_posts(user_id: str, page: int = 1) -> list[Post]`**

获取用户微博时间线。

**`await get_post(post_id: str) -> Post`**

获取微博详情（移动端 API）。

**`await get_post_comments(post_id: str) -> list[Comment]`**

获取微博评论。

### WeiboConfig

**配置类，控制 HTTP、认证、API 行为。**

```python
from weibo_cli import WeiboConfig

# 默认配置
config = WeiboConfig()

# 快速配置（低延迟，低重试）
config = WeiboConfig.create_fast()

# 保守配置（高超时，高重试）
config = WeiboConfig.create_conservative()
```

#### 配置字段

```python
@dataclass
class WeiboConfig:
    http: HttpConfig       # HTTP 配置
    auth: AuthConfig       # 认证配置
    api: ApiConfig         # API 端点配置
```

**HttpConfig**
```python
timeout: float = 10.0                    # 请求超时（秒）
max_retries: int = 3                     # 最大重试次数
base_delay: float = 1.0                  # 基础延迟（秒）
max_delay: float = 60.0                  # 最大延迟（秒）
max_connections: int = 20                # 最大连接数
max_keepalive_connections: int = 5       # 保持活跃连接数
```

**AuthConfig**
```python
cookie_ttl: float = 300.0                # Cookie 缓存时间（秒）
```

**ApiConfig**
```python
base_url: str = "https://weibo.com"
mobile_url: str = "https://m.weibo.cn"
user_agent: str = "Mozilla/5.0 ..."
```

### 数据模型

**所有模型都是 Pydantic dataclass，支持类型提示和 IDE 补全。**

**User**
```python
@dataclass
class User:
    id: int
    screen_name: str
    profile_image_url: str
    verified: bool = False
    followers_count: int = 0
    friends_count: int = 0
    statuses_count: int = 0
    description: str = ""
```

**Post**
```python
@dataclass
class Post:
    id: int
    created_at: datetime
    text: str
    user: User
    images: list[Image] = field(default_factory=list)
    video: Video | None = None
    reposts_count: int = 0
    comments_count: int = 0
    attitudes_count: int = 0
```

**Comment**
```python
@dataclass
class Comment:
    id: int
    created_at: datetime
    text: str
    user: User
    like_count: int = 0
    floor_number: int = 0
    rootid: int = 0
```

**Image**
```python
@dataclass
class Image:
    id: str
    thumbnail_url: str
    large_url: str
    original_url: str
    width: int = 0
    height: int = 0
```

**Video**
```python
@dataclass
class Video:
    duration: float
    play_count: int
    urls: dict[str, str] = field(default_factory=dict)
```

### 异常

```python
from weibo_cli.exceptions import (
    WeiboError,      # 基础异常
    AuthError,       # 认证失败
    NetworkError,    # 网络错误
    ParseError,      # 解析错误
)
```

## 测试

```bash
# 运行所有测试
uv run pytest -v

# 带覆盖率
uv run pytest --cov -v
```

## 架构

```
WeiboClient              # Facade 入口
├── HttpClient           # HTTP 请求
├── CookieManager        # Cookie 管理（自动获取访客 Cookie + XSRF token）
├── RetryStrategy        # 重试策略（指数退避）
├── UserParser           # 用户数据解析
├── PostParser           # 微博数据解析
└── CommentParser        # 评论数据解析
```

**设计原则**：
- 单一职责：每个类只做一件事
- 依赖注入：组件可独立测试
- 无全局状态：线程安全
- 显式优于隐式：所有配置都可见

## 许可证

MIT
