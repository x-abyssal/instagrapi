# 多账号自动化 Session 管理方案

## 一、需求分析

### 当前痛点
- `dump_settings()` 需要手动指定文件名，多账号操作时不便
- 无法自动关联账号身份信息（username/user_id）与 session 文件
- 缺乏统一的 session 文件存储目录管理

### 目标
1. 自动根据账号信息生成唯一且可识别的文件名
2. 支持预先指定统一的 session 存储目录
3. 提供自动加载对应账号 session 的便捷方法
4. 保持向后兼容，不影响现有 `dump_settings()` 和 `load_settings()` 方法

## 二、技术分析

### 可用的账号标识符

根据代码探索，有以下可用标识符：

| 标识符 | 可用性 | 稳定性 | 人类可读性 | 获取时机 |
|--------|--------|--------|------------|----------|
| **user_id** | ✅ 始终可用 | ✅ 永久不变 | ❌ 纯数字 | 登录后 |
| **username** | ✅ 始终可用 | ⚠️ 可被用户修改 | ✅ 人类可读 | 登录后 |
| **sessionid** | ✅ 始终可用 | ❌ 会话级别（会过期） | ❌ 长字符串 | 登录前/后 |

### 标识符提取逻辑

**user_id 获取**:
```python
@property
def user_id(self) -> str:
    return self.cookie_dict.get("ds_user_id") or \
           self.authorization_data.get("ds_user_id")
```

**username 获取**:
```python
self.username  # 直接属性，登录时通过 API 获取
```

**从 sessionid 提取 user_id**:
```python
import re
user_id = re.search(r"^\d+", sessionid).group()
```

### 当前 Settings 数据结构

`get_settings()` 返回的数据 **不包含 username**，但包含：
- `authorization_data.ds_user_id` - 用户 ID
- `authorization_data.sessionid` - 会话 ID
- `cookies` - 包含 ds_user_id 和 sessionid
- `device_settings`, `uuids`, `user_agent` 等设备指纹信息

## 三、最终实现方案

### 文件存储策略：目录结构 + 索引文件

采用目录结构：`./sessions/<username|user_id>/settings.json` 配合索引文件实现快速查询。

**目录结构示例**：
```
./sessions/
├── index.json                          # 快速索引文件
├── john_doe/                           # username 目录
│   └── settings.json                   # session 数据
├── 123456789/                          # user_id 目录（username 不可用时）
│   └── settings.json                   # session 数据
└── test_account/
    └── settings.json
```

**index.json 格式**：
```json
{
  "john_doe": {
    "username": "john_doe",
    "user_id": "123456789",
    "session_dir": "john_doe",
    "saved_at": "2025-12-28T10:30:00Z"
  },
  "123456789": {
    "username": "john_doe",
    "user_id": "123456789",
    "session_dir": "john_doe",
    "saved_at": "2025-12-28T10:30:00Z"
  }
}
```

**优点**：
- ✅ 目录名直接使用 username 或 user_id，避免文件名特殊字符问题
- ✅ 索引文件实现 O(1) 查找，避免目录扫描
- ✅ 可扩展：每个账号目录下可存储多个文件（如日志、缓存）
- ✅ 清晰的层次结构，易于管理

### 目录命名规则

**优先级策略**：
- 优先使用 `username` 作为目录名（人类可读）
- 如果 username 不可用或包含非法字符，回退使用 `user_id`
- 通过 OSError 捕获处理特殊字符问题

**实际实现**：
```python
# 优先使用 username，回退到 user_id
account_dir_name = username if username else user_id

# 创建目录时处理特殊字符
try:
    account_dir = session_dir_path / account_dir_name
    account_dir.mkdir(parents=True, exist_ok=True)
except OSError:
    # 如果 username 包含非法字符，使用 user_id 作为后备
    if username and user_id:
        account_dir_name = user_id
        account_dir = session_dir_path / user_id
        account_dir.mkdir(parents=True, exist_ok=True)
    else:
        raise
```

### 索引文件设计

**双键索引策略**：
- 同时使用 `username` 和 `user_id` 作为键
- 两个键指向同一个 `session_dir` 条目
- 支持通过任意标识符快速查找

**索引操作方法**：
- `_load_index(session_dir)` - 读取索引文件，不存在时返回空字典
- `_save_index(session_dir, index)` - 保存索引文件
- `_update_index(session_dir, username, user_id, account_dir)` - 更新索引条目

### 元数据策略

**settings.json 不添加额外元数据**：
- 保持原有 `get_settings()` 返回的数据结构不变
- 所有元数据（username、user_id、saved_at）存储在 `index.json` 中

**理由**：
- 避免修改现有 settings 数据结构
- 向后兼容性更强
- 索引文件已包含所有必要元数据

## 四、API 设计（已实现）

### 实例变量

在 `Client.__init__()` 中添加：
```python
def __init__(
    self,
    settings: dict = {},
    proxy: str | None = None,
    delay_range: list | None = None,
    logger=DEFAULT_LOGGER,
    session_dir: str | None = None,  # 新增参数
    **kwargs,
):
    ...
    self.session_dir = session_dir  # 新增实例变量
```

### 1. `auto_dump_settings(session_dir=None)` → Path

**功能**：自动保存 session 到目录结构

**参数**：
- `session_dir` (str | Path | None): session 根目录
  - None 时使用 `self.session_dir` 或默认 `./sessions/`

**返回**：`Path` 对象，指向保存的 `settings.json` 文件

**异常**：
- `ValueError`: 无法获取 username 或 user_id 时（未登录）

**实现流程**：
1. 确定根目录（`_ensure_session_dir()`）
2. 获取 username 和 user_id（优先 username）
3. 创建账号子目录（带 OSError 回退）
4. 保存 settings 到 `settings.json`
5. 更新索引文件（仅当 username 和 user_id 都存在时）

**示例**：
```python
cl = Client()
cl.login(username="john_doe", password="pass")
path = cl.auto_dump_settings()
print(path)  # './sessions/john_doe/settings.json'
```

### 2. `restore_settings(identifier, session_dir=None)` → Dict

**功能**：智能加载 session，支持多种标识符类型

**参数**：
- `identifier` (str | int): username、user_id 或 cookie 字符串
- `session_dir` (str | Path | None): session 根目录

**返回**：加载的 settings 字典

**异常**：
- `FileNotFoundError`: 找不到对应的 session 文件

**identifier 识别逻辑**：
1. 如果包含 `sessionid=` → 解析为 cookie 字符串，提取 user_id
2. 否则直接作为 username 或 user_id 查找索引

**实现流程**：
1. 加载索引文件
2. 解析 identifier（cookie 字符串特殊处理）
3. 从索引查找对应的 `session_dir`
4. 加载 `./sessions/<session_dir>/settings.json`
5. 调用 `load_settings(path)`

**示例**：
```python
cl = Client()
cl.restore_settings("john_doe")              # 通过 username
cl.restore_settings(123456789)               # 通过 user_id
cl.restore_settings("sessionid=123...")      # 通过 cookie
```

### 3. `get_available_sessions(session_dir="./sessions")` → List[Dict]

**功能**：列出目录下所有可用的 session（类方法）

**参数**：
- `session_dir` (str | Path): session 根目录，默认 `./sessions`

**返回**：session 信息列表（已去重）

**返回格式**：
```python
[
    {
        "username": "john_doe",
        "user_id": "123456789",
        "session_dir": "john_doe",
        "saved_at": "2025-12-28T10:30:00Z",
        "filepath": Path("./sessions/john_doe/settings.json")
    },
    ...
]
```

**去重逻辑**：
- 使用 `seen_dirs` set 跟踪已处理的 `session_dir`
- 跳过重复条目（username 和 user_id 指向同一目录）

**示例**：
```python
sessions = Client.get_available_sessions("./sessions")
for s in sessions:
    print(f"{s['username']} ({s['user_id']})")
```

### 4. 辅助方法（私有）

- `_load_index(session_dir)` - 加载索引文件，返回字典或空字典
- `_save_index(session_dir, index)` - 保存索引文件
- `_update_index(session_dir, username, user_id, account_dir)` - 更新索引条目
- `_ensure_session_dir(session_dir)` - 确保目录存在，返回 Path 对象

## 五、使用示例

详细示例请参考 [examples/auto_session_management.py](../examples/auto_session_management.py)

### 1. 单账号自动保存/加载

```python
from instagrapi import Client

# 初始化时指定 session 目录
cl = Client(session_dir="./my_sessions")

# 登录并自动保存
cl.login(username="john_doe", password="password")
saved_path = cl.auto_dump_settings()
print(saved_path)  # ./my_sessions/john_doe/settings.json

# 下次直接加载
cl2 = Client(session_dir="./my_sessions")
cl2.restore_settings("john_doe")  # 通过 username
```

### 2. 多账号批量操作

```python
accounts = [
    ("user1", "pass1"),
    ("user2", "pass2"),
    ("user3", "pass3"),
]

for username, password in accounts:
    cl = Client(session_dir="./sessions")
    cl.login(username, password)

    # 自动保存到 ./sessions/<username>/settings.json
    path = cl.auto_dump_settings()
    print(f"Saved {username} to {path}")

    # 执行操作...
    user_info = cl.user_info_by_username(username)
```

### 3. 列出并选择账号

```python
# 列出所有已保存的 session
sessions = Client.get_available_sessions("./sessions")

print(f"Found {len(sessions)} sessions:")
for session in sessions:
    print(f"  - {session['username']} (ID: {session['user_id']})")

# 选择一个加载
cl = Client(session_dir="./sessions")
cl.restore_settings(sessions[0]['username'])
```

### 4. 通过不同标识符加载

```python
cl = Client(session_dir="./sessions")

# 方法 1: 通过 username
cl.restore_settings("john_doe")

# 方法 2: 通过 user_id
cl.restore_settings(123456789)

# 方法 3: 通过 cookie 字符串
cookie_str = "sessionid=123456789%3ATfy3bX..."
cl.restore_settings(cookie_str)
```

### 5. 向后兼容

```python
cl = Client()

# 旧方法仍然可用
cl.login(username, password)
cl.dump_settings("custom_name.json")

# 新方法也可用
cl.auto_dump_settings("./sessions")
```

## 六、实现位置

### 文件修改清单

| 文件 | 修改内容 | 状态 |
|------|----------|------|
| [instagrapi/mixins/auth.py](../instagrapi/mixins/auth.py) | 添加 7 个新方法：`auto_dump_settings()`, `restore_settings()`, `get_available_sessions()`, `_load_index()`, `_save_index()`, `_update_index()`, `_ensure_session_dir()` | ✅ 已完成 |
| [instagrapi/\_\_init\_\_.py](../instagrapi/__init__.py) | 在 `Client.__init__()` 中添加 `session_dir` 参数 | ✅ 已完成 |
| [examples/auto_session_management.py](../examples/auto_session_management.py) | 新增示例文件，包含 6 个使用场景 | ✅ 已完成 |
| [test_auto_session_demo.py](../test_auto_session_demo.py) | 新增测试演示文件（无需真实账号） | ✅ 已完成 |

**实际代码位置**：
- 新增方法位于 `instagrapi/mixins/auth.py` 第 1036-1294 行
- `Client.__init__()` 修改位于 `instagrapi/__init__.py` 第 63 行

## 七、测试验证

### 测试结果（test_auto_session_demo.py）

运行测试：
```bash
python test_auto_session_demo.py
```

**测试用例**：
1. ✅ `test_auto_dump_settings()` - 验证自动保存功能
   - 创建目录结构 `./test_sessions/<username>/settings.json`
   - 生成索引文件 `./test_sessions/index.json`
   - 索引包含 username 和 user_id 双键

2. ✅ `test_restore_settings()` - 验证加载功能
   - 通过 username 加载成功
   - 通过 user_id 加载成功
   - 通过 cookie 字符串加载成功

3. ✅ `test_get_available_sessions()` - 验证列表功能
   - 正确去重（username 和 user_id 指向同一目录）
   - 返回完整 session 信息

4. ✅ `test_error_handling()` - 验证错误处理
   - 加载不存在的 session 抛出 `FileNotFoundError`
   - 未登录保存抛出 `ValueError`

**目录结构验证**：
```
./test_sessions/
├── index.json
└── test_user/
    └── settings.json
```

## 八、关键实现细节

### 1. 目录命名回退机制

实际实现使用 **try/except OSError** 处理特殊字符：

```python
# 优先使用 username
account_dir_name = username if username else user_id

try:
    account_dir = session_dir_path / account_dir_name
    account_dir.mkdir(parents=True, exist_ok=True)
except OSError:
    # username 包含非法字符时回退到 user_id
    if username and user_id:
        account_dir_name = user_id
        account_dir = session_dir_path / user_id
        account_dir.mkdir(parents=True, exist_ok=True)
    else:
        raise
```

### 2. Cookie 字符串解析

支持两种 cookie 格式：
- 完整 cookie: `sessionid=123456789%3ATfy3bX...; other=value`
- 单个 sessionid: `sessionid=123456789%3ATfy3bX...`

```python
if isinstance(identifier, str) and "sessionid=" in identifier:
    match = re.search(r'sessionid=([^;]+)', identifier)
    if match:
        sessionid = match.group(1)
        # 提取 user_id (sessionid 前缀)
        user_id_match = re.search(r'^(\d+)', sessionid)
        if user_id_match:
            identifier = user_id_match.group(1)
```

### 3. 索引文件双键策略

**同一 session 使用两个键指向**：

```python
entry = {
    "username": username,
    "user_id": user_id,
    "session_dir": account_dir_name,
    "saved_at": datetime.now(timezone.utc).isoformat(),
}

# 双键索引
index[username] = entry  # 键1: username
index[user_id] = entry   # 键2: user_id
```

**去重逻辑**（get_available_sessions）：

```python
seen_dirs = set()
for key, entry in index.items():
    session_dir_name = entry["session_dir"]
    if session_dir_name in seen_dirs:
        continue  # 跳过重复
    seen_dirs.add(session_dir_name)
    sessions.append(entry)
```

### 4. settings.json 数据结构

**不修改原有结构**：
- 保持 `get_settings()` 返回格式不变
- 元数据完全存储在 `index.json` 中
- 确保向后兼容

## 九、常见问题与解决方案

### Q1: 为什么不在 settings.json 中添加 username？

**答**：为了保持向后兼容性。现有代码使用 `get_settings()` 返回的数据结构，添加新字段可能影响兼容性。所有元数据通过 `index.json` 管理更清晰。

### Q2: 如果 index.json 损坏怎么办？

**答**：当前实现中，`_load_index()` 会捕获 `json.JSONDecodeError` 并返回空字典。未来可添加修复工具，扫描目录重建索引。

### Q3: 为什么优先使用 username 而非 user_id？

**答**：username 人类可读，便于调试和管理。user_id 作为回退保证唯一性和稳定性。

### Q4: session 文件安全性如何保证？

**答**：当前使用系统默认文件权限。建议用户：
- 不要将 session 目录提交到版本控制
- 在生产环境中使用适当的文件权限（如 0o600）
- 定期轮换 session

### Q5: 如何处理 username 修改的情况？

**答**：
- 如果 Instagram 用户修改了 username，原有目录名不会自动更新
- user_id 保持不变，通过 user_id 仍可加载 session
- 建议定期重新登录刷新 session

## 十、向后兼容性

### 保留的旧方法

以下方法完全保留，不受新功能影响：

- `dump_settings(path)` - 手动指定路径保存 session
- `load_settings(path)` - 从指定路径加载 session
- `get_settings()` - 获取当前 settings 字典

### 混合使用示例

```python
cl = Client(session_dir="./sessions")

# 使用旧方法手动管理
cl.login("user", "pass")
cl.dump_settings("backup.json")

# 使用新方法自动管理
cl.auto_dump_settings()

# 两种文件都可以加载
cl2 = Client()
cl2.load_settings("backup.json")  # 旧方法

cl3 = Client(session_dir="./sessions")
cl3.restore_settings("user")  # 新方法
```

## 十一、总结

### 方案优势

1. **目录结构更清晰**
   - 每个账号独立目录，便于管理和扩展
   - 可在账号目录下存储额外文件（日志、缓存等）

2. **索引文件提升性能**
   - O(1) 查找复杂度，避免目录扫描
   - 同时支持 username 和 user_id 查找

3. **无需清理特殊字符**
   - 操作系统处理目录名，减少代码复杂度
   - 异常时自动回退使用 user_id

4. **元数据分离**
   - settings.json 保持原有结构不变
   - 元数据存储在 index.json，向后兼容性更强

5. **扩展性强**
   - 未来可在账号目录下添加更多文件
   - 索引文件可扩展存储更多元信息

### 实现状态

✅ **已完成**：
- [x] 文件存储：目录结构 `./sessions/<username|user_id>/settings.json`
- [x] 索引文件：`./sessions/index.json` 用于快速查找
- [x] 不修改 settings.json 数据结构（不添加 `_metadata`）
- [x] 默认目录：`./sessions/`
- [x] 支持通过 username、user_id、cookie 加载
- [x] 新方法：`auto_dump_settings` 和 `restore_settings`
- [x] 类方法：`get_available_sessions`
- [x] 完整测试验证
- [x] 示例代码
- [x] 文档更新

---

**开发完成时间**：2025-12-29
**测试状态**：✅ 所有测试通过
**文档状态**：✅ 已与实现同步
