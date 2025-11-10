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
async with WeiboClient(
    cookies=None,
    config=None,
    logger=None,
    max_concurrent_requests=4,
    requests_per_interval=10,
    rate_interval_seconds=1.0,
) as client:
    ...
```

#### 参数
- `cookies`: 可选的 Cookie 字符串
- `config`: `WeiboConfig` 实例，默认使用标准配置
- `logger`: 自定义 logger，默认使用模块 logger
- `max_concurrent_requests`: 并发请求上限
- `requests_per_interval`: 每时间窗口的请求数上限
- `rate_interval_seconds`: 速率限制窗口（秒）
- `rate_limiter`: 传入自定义 `RateLimiter`，覆盖默认策略

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

**所有模型都基于 [Pydantic v2](https://docs.pydantic.dev/) 的 `BaseModel`，自动完成类型转换、校验与序列化。**

**User**
```python
from weibo_cli.models import User

user = User(
    id=123,
    screen_name="Test User",
    profile_image_url="https://example.com/avatar.jpg",
    followers_count=100,
)

# Pydantic API 同样可用
user_dict = user.model_dump()
```

**Post**
```python
from datetime import datetime

from weibo_cli.models import Post, Image, Video

post = Post(
    id=1,
    created_at=datetime.utcnow(),
    text="Hello Weibo",
    user=user,
    images=[Image(id="pic1", thumbnail_url="...", large_url="...", original_url="...")],
    video=Video(duration=10.5, play_count=999),
    reposts_count=1,
    comments_count=2,
    attitudes_count=3,
)

# 每个模型都带有 `raw` 字段，保存原始 JSON 字符串快照
print(post.raw)
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
uv run pytest -v
```

## 发布前清理

发布/打包前运行 `scripts/prep_release.sh`，脚本会：

- 执行 `python -m compileall -q src tests`，提前暴露语法错误
- 清理 `__pycache__` 目录，确保工作区干净

```bash
bash scripts/prep_release.sh
```

## 验证 XSRF 修复

运行 `python examples/verify_xsrf_fix.py` 即可验证 CookieManager 是否成功获取 `XSRF-TOKEN` 并调用时间线接口：

```bash
python examples/verify_xsrf_fix.py
```

脚本会：

- 输出生成的访客 Cookie 片段
- 打印获取到的 `XSRF-TOKEN`，若缺失会直接报错
- 调用 `get_user_posts` 并统计返回的微博数量，用于确认 HTTP 432 错误已消失

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

GNU Affero General Public License v3.0
