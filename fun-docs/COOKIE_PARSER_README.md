# Cookie Parser 工具说明

## 概述

Cookie Parser 是一个用于解析浏览器导出的 Cookie JSON 数据并将其转换为 instagrapi 可用格式的工具模块。它支持多种浏览器和 Cookie 导出工具的格式。

## 功能特性

- ✅ 解析浏览器导出的 JSON 格式 Cookie 数据
- ✅ 支持单个和批量账户处理
- ✅ 自动过滤必要的 Cookie 字段
- ✅ 从文件中读取多个账户的 Cookie（每行一个 JSON 数组）
- ✅ 提供丰富的错误处理和验证
- ✅ 完整的类型提示和文档

## 支持的数据源

### 1. 浏览器开发者工具

**Chrome/Edge:**
- 打开 DevTools (F12)
- Application → Cookies → `instagram.com`
- 复制 Cookie 数据

**Firefox:**
- 打开 DevTools (F12)
- Storage → Cookies → `instagram.com`
- 复制 Cookie 数据

### 2. 浏览器扩展

- EditThisCookie
- Cookie-Editor
- Export Cookies
- 其他 Cookie 导出工具

### 3. 数据格式

支持的 JSON 格式：
```json
[
    {
        "domain": ".instagram.com",
        "name": "sessionid",
        "value": "123456%3Axxx%3A27%3Ayyy",
        "expirationDate": 1798244001670,
        "path": "/",
        "secure": true,
        ...
    },
    {
        "domain": ".instagram.com",
        "name": "mid",
        "value": "aUxY0wABAAHc6RX2S4k5JBIWSqSr",
        ...
    }
]
```

## 核心方法

### 1. `parse_browser_cookies_json()`

解析 JSON 格式的 Cookie 数据并转换为 Cookie 字符串。

**参数:**
- `json_data` (str | List[Dict]): JSON 字符串或已解析的 Cookie 列表
- `include_all` (bool): 是否包含所有 Cookie，默认 True

**返回:**
- `str`: Cookie 字符串，格式：`"key1=value1; key2=value2"`

**示例:**
```python
from instagrapi.cookie_parser import parse_browser_cookies_json

# 从 JSON 字符串解析
json_str = '[{"name":"sessionid","value":"xxx"},{"name":"mid","value":"yyy"}]'
cookie_string = parse_browser_cookies_json(json_str)
# 结果: "sessionid=xxx; mid=yyy"

# 从 Python 列表解析
cookies = [
    {"name": "sessionid", "value": "xxx"},
    {"name": "mid", "value": "yyy"}
]
cookie_string = parse_browser_cookies_json(cookies)

# 只包含必要的 Cookie
cookie_string = parse_browser_cookies_json(json_str, include_all=False)
```

### 2. `parse_cookies_file()`

从文件中解析 Cookie 数据（每行一个 JSON 数组）。

**参数:**
- `file_path` (str): Cookie 文件路径
- `line_number` (int, optional): 要解析的行号（从 1 开始），None 则解析全部
- `include_all` (bool): 是否包含所有 Cookie

**返回:**
- `str` 或 `List[str]`: 单个或多个 Cookie 字符串

**示例:**
```python
from instagrapi.cookie_parser import parse_cookies_file

# 解析第一个账户
cookie = parse_cookies_file('cookies.txt', line_number=1)

# 解析所有账户
all_cookies = parse_cookies_file('cookies.txt')
for i, cookie in enumerate(all_cookies, 1):
    print(f"Account {i}: {cookie[:50]}...")
```

### 3. `extract_cookie_info()`

从 Cookie 字符串中提取各个字段的值。

**参数:**
- `cookie_string` (str): Cookie 字符串

**返回:**
- `Dict[str, str]`: Cookie 名称到值的映射

**示例:**
```python
from instagrapi.cookie_parser import extract_cookie_info

cookie = "sessionid=xxx; mid=yyy; ds_user_id=123"
info = extract_cookie_info(cookie)

print(info['sessionid'])  # xxx
print(info['mid'])        # yyy
print(info['ds_user_id']) # 123
```

### 4. `get_sessionid_from_json()`

快速从 JSON 中提取 sessionid（登录最小需求）。

**参数:**
- `json_data` (str | List[Dict]): Cookie JSON 数据

**返回:**
- `Optional[str]`: sessionid 的值，未找到则返回 None

**示例:**
```python
from instagrapi.cookie_parser import get_sessionid_from_json

json_str = '[{"name":"sessionid","value":"xxx"},{"name":"mid","value":"yyy"}]'
sessionid = get_sessionid_from_json(json_str)
print(sessionid)  # xxx
```

## 使用场景

### 场景 1: 单账户登录

```python
from instagrapi import Client
from instagrapi.cookie_parser import parse_browser_cookies_json

# 从浏览器复制的 JSON
json_cookies = '''[
    {"name": "sessionid", "value": "123%3Axxx%3A27%3Ayyy"},
    {"name": "mid", "value": "aUxY0wABAAHc6RX2S4k5JBIWSqSr"},
    {"name": "csrftoken", "value": "abc123"}
]'''

# 解析为 Cookie 字符串
cookie_str = parse_browser_cookies_json(json_cookies)

# 登录
cl = Client()
cl.login_by_cookie(cookie_str)
print(f"登录成功: @{cl.username}")

# 保存会话
cl.dump_settings('session.json')
```

### 场景 2: 批量账户管理

```python
from instagrapi import Client
from instagrapi.cookie_parser import parse_cookies_file

# 从文件读取所有账户（每行一个 JSON 数组）
all_cookies = parse_cookies_file('accounts.txt')

for i, cookie_str in enumerate(all_cookies, 1):
    cl = Client()
    try:
        cl.login_by_cookie(cookie_str)
        print(f"账户 {i}: @{cl.username} 登录成功")

        # 执行操作...
        user = cl.account_info()
        print(f"  粉丝: {user.follower_count}")

        # 保存会话
        cl.dump_settings(f'session_{i}.json')

    except Exception as e:
        print(f"账户 {i} 登录失败: {e}")
```

### 场景 3: 从特定账户登录

```python
from instagrapi import Client
from instagrapi.cookie_parser import parse_cookies_file, extract_cookie_info

# 解析第 5 个账户
cookie_str = parse_cookies_file('accounts.txt', line_number=5)

# 查看账户信息
info = extract_cookie_info(cookie_str)
print(f"准备登录用户 ID: {info.get('ds_user_id')}")

# 登录
cl = Client()
cl.login_by_cookie(cookie_str)
```

### 场景 4: 最小化 Cookie（仅 sessionid）

```python
from instagrapi import Client
from instagrapi.cookie_parser import get_sessionid_from_json

json_cookies = '[{"name":"sessionid","value":"xxx"},{"name":"mid","value":"yyy"}]'

# 提取 sessionid
sessionid = get_sessionid_from_json(json_cookies)

# 使用 sessionid 登录
cl = Client()
cl.login_by_cookie(f"sessionid={sessionid}")
# 或者使用原始方法
# cl.login_by_sessionid(sessionid)
```

## 文件格式示例

### 多账户 Cookie 文件格式

文件 `accounts.txt`：
```
[{"name":"sessionid","value":"xxx1"},{"name":"mid","value":"yyy1"}]
[{"name":"sessionid","value":"xxx2"},{"name":"mid","value":"yyy2"}]
[{"name":"sessionid","value":"xxx3"},{"name":"mid","value":"yyy3"}]
```

每行一个 JSON 数组，代表一个账户的 Cookie 数据。

### 完整格式示例

参见项目文件 [fun-docs/10 COOKIES.txt](10 COOKIES.txt)，包含 10 个账户的完整 Cookie 数据。

## 必要 Cookie 字段

Cookie Parser 识别以下必要字段（当 `include_all=False` 时）：

| Cookie 名称 | 说明 | 必需性 |
|------------|------|--------|
| `sessionid` | 会话 ID | ✅ 必需 |
| `mid` | 设备 Machine ID | 推荐 |
| `csrftoken` | CSRF 保护令牌 | 推荐 |
| `ds_user_id` | 用户 ID | 推荐 |
| `ig_did` | Instagram 设备 ID | 可选 |
| `datr` | 设备追踪令牌 | 可选 |
| `wd` | 窗口尺寸 | 可选 |
| `rur` | 路由信息 | 可选 |

## 错误处理

### 常见错误

**ValueError: Cookie string cannot be empty**
- Cookie 数据为空
- 解决：提供有效的 Cookie JSON 数据

**ValueError: Invalid JSON format**
- JSON 格式错误
- 解决：检查 JSON 语法，确保是有效的 JSON 数组

**ValueError: No cookies found in data**
- JSON 数组为空 `[]`
- 解决：确保 JSON 包含至少一个 Cookie 对象

**ValueError: No valid cookies found**
- Cookie 对象缺少 `name` 或 `value` 字段
- 解决：确保每个 Cookie 对象都有 `name` 和 `value` 字段

**FileNotFoundError: Cookie file not found**
- 文件路径不存在
- 解决：检查文件路径是否正确

**ValueError: Line number X out of range**
- 指定的行号超出文件行数
- 解决：检查文件总行数，使用有效的行号

### 错误处理示例

```python
from instagrapi.cookie_parser import parse_browser_cookies_json

try:
    cookie_str = parse_browser_cookies_json(json_data)
    cl.login_by_cookie(cookie_str)
except ValueError as e:
    print(f"Cookie 解析错误: {e}")
except FileNotFoundError as e:
    print(f"文件未找到: {e}")
except Exception as e:
    print(f"其他错误: {e}")
```

## 测试

### 运行单元测试

```bash
python -m unittest tests.test_cookie_parser -v
```

### 运行演示程序

```bash
# 从仓库根目录运行
PYTHONPATH=. python tests/demo_cookie_parser.py
```

### 查看示例代码

- [examples/parse_browser_cookies.py](../examples/parse_browser_cookies.py) - 完整示例
- [tests/demo_cookie_parser.py](../tests/demo_cookie_parser.py) - 演示程序
- [tests/test_cookie_parser.py](../tests/test_cookie_parser.py) - 单元测试

## 最佳实践

### 1. 首次使用流程

```python
# 1. 解析 Cookie
from instagrapi import Client
from instagrapi.cookie_parser import parse_cookies_file

cookie_str = parse_cookies_file('cookies.txt', line_number=1)

# 2. 登录
cl = Client()
cl.login_by_cookie(cookie_str)

# 3. 先执行只读操作
user = cl.account_info()
print(f"用户: {user.username}, 粉丝: {user.follower_count}")

# 4. 保存会话
cl.dump_settings('session.json')
```

### 2. 后续使用流程

```python
# 直接加载已保存的会话
from instagrapi import Client

cl = Client()
cl.load_settings('session.json')

# 无需重新登录，直接使用
user = cl.account_info()
```

### 3. 安全建议

- ⚠️ 不要在代码中硬编码 Cookie 数据
- ⚠️ 不要将 Cookie 文件提交到版本控制系统
- ⚠️ 首次登录后先执行只读操作
- ⚠️ 定期更新 Cookie 数据
- ⚠️ 使用 `.gitignore` 忽略敏感文件

```gitignore
# .gitignore
session*.json
cookies.txt
accounts.txt
```

## 与其他登录方式对比

| 登录方式 | 数据来源 | 便利性 | 安全性 | 适用场景 |
|---------|---------|--------|--------|---------|
| `login(username, password)` | 用户名密码 | ⭐⭐ | ⭐⭐⭐ | 长期稳定使用 |
| `login_by_sessionid(sessionid)` | 仅 sessionid | ⭐⭐⭐ | ⭐⭐ | 快速登录 |
| `login_by_cookie(cookie_str)` | 完整 Cookie 字符串 | ⭐⭐⭐ | ⭐⭐ | 浏览器迁移 |
| **Cookie Parser + login_by_cookie** | 浏览器导出 JSON | ⭐⭐⭐⭐ | ⭐⭐ | 批量账户管理 |

## 技术细节

### Cookie 解析流程

1. **输入验证**: 检查 JSON 格式和数据类型
2. **JSON 解析**: 将字符串转换为 Python 对象（如需要）
3. **字段提取**: 从每个 Cookie 对象中提取 `name` 和 `value`
4. **过滤**: 根据 `include_all` 参数过滤 Cookie
5. **拼接**: 将所有 Cookie 拼接成字符串格式
6. **返回**: 返回可用于 `login_by_cookie()` 的字符串

### 数据流程图

```
浏览器 Cookie JSON
       ↓
parse_browser_cookies_json()
       ↓
Cookie 字符串 (key1=value1; key2=value2)
       ↓
Client.login_by_cookie()
       ↓
Instagram 登录
```

## FAQ

**Q: 支持哪些浏览器？**
A: 所有现代浏览器（Chrome、Firefox、Edge、Safari 等），只要能导出 JSON 格式的 Cookie。

**Q: 文件必须每行一个账户吗？**
A: 是的，`parse_cookies_file()` 要求每行一个 JSON 数组。

**Q: 可以混合使用不同格式的 Cookie 吗？**
A: 可以，Parser 会自动提取有效的 `name` 和 `value` 字段。

**Q: 解析失败怎么办？**
A: 检查 JSON 格式是否正确，确保每个 Cookie 都有 `name` 和 `value` 字段。

**Q: 是否需要所有 Cookie 字段？**
A: 最少只需要 `sessionid`，但推荐包含 `mid`、`csrftoken` 等以提高成功率。

## 相关文档

- [COOKIE_LOGIN_README.md](COOKIE_LOGIN_README.md) - Cookie 登录详细说明
- [examples/cookie_login.py](../examples/cookie_login.py) - Cookie 登录示例
- [examples/parse_browser_cookies.py](../examples/parse_browser_cookies.py) - Cookie 解析示例

## 更新日志

### v1.0.0 (2025-12-27)
- ✨ 初始版本发布
- ✅ 支持浏览器 JSON Cookie 解析
- ✅ 支持批量账户文件解析
- ✅ 完整的测试套件和文档
