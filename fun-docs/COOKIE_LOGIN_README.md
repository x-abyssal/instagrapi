# Cookie 登录功能说明

## 概述

`login_by_cookie()` 方法允许您直接使用浏览器的 Cookie 字符串登录 Instagram，无需手动输入用户名和密码。

## ⚠️ 重要提示：风控风险

使用桌面浏览器的 Cookie 配合移动端 UA 可能触发 Instagram 安全检查，因为存在**设备指纹不一致**问题。

**风险级别：** 🟡 中等

**建议策略：**
1. 首次登录后只进行**只读操作**（查看信息、获取数据）
2. 保存 session 后，Instagram 会在后续请求中自动更新设备指纹
3. 避免频繁切换设备/Cookie
4. 准备处理邮箱/短信验证 Challenge

## 快速开始

### 1. 从浏览器获取 Cookie

**Chrome/Edge:**
1. 打开 Instagram 网站并登录
2. 按 F12 打开开发者工具
3. 进入 **Application** 标签
4. 左侧 **Cookies** -> `https://instagram.com`
5. 复制所有 Cookie（或只复制 sessionid）

**Firefox:**
1. 按 F12 打开开发者工具
2. 进入 **存储** 标签
3. **Cookie** -> `https://instagram.com`
4. 复制所有 Cookie

### 2. 使用 Cookie 登录

```python
from instagrapi import Client

# 从浏览器复制的 Cookie 字符串
cookie = 'csrftoken=xxx; sessionid=123456%3Ayyy%3A27%3Azzz; mid=aaa; ds_user_id=123456'

# 创建客户端并登录
cl = Client()
cl.login_by_cookie(cookie)

print(f"✅ 登录成功：@{cl.username}")

# 保存 session 供后续使用
cl.dump_settings("session.json")
```

### 3. 后续使用保存的 Session

```python
from instagrapi import Client

cl = Client()
cl.load_settings("session.json")

# 直接使用，无需重新登录
user = cl.account_info()
print(f"用户名: {user.username}")
```

## 支持的 Cookie 格式

### 完整 Cookie 字符串（推荐）
```python
cookie = 'csrftoken=xxx; datr=yyy; ig_did=zzz; mid=aaa; ds_user_id=123; sessionid=123%3Abbb%3A27%3Accc'
cl.login_by_cookie(cookie)
```

### 最小化 Cookie（仅 sessionid）
```python
cookie = 'sessionid=312488908%3ATfy3bX853vi4X0%3A27%3AAYj...'
cl.login_by_cookie(cookie)
```

### 带引号的 Cookie
```python
cookie = 'sessionid="123%3Axxx"; mid="yyy"'
cl.login_by_cookie(cookie)  # 自动移除引号
```

### 带转义字符的 Cookie
```python
cookie = r'rur="VLL\054123\0541798178884"'
cl.login_by_cookie(cookie)  # 自动处理 \054 -> ,
```

## 完整示例

### 示例 1：基础登录
```python
from instagrapi import Client

cookie_string = '''
csrftoken=ssSbbZh1RzdKYWm3uiPg5-;
datr=PcX1aMMdCNzF_kelTFfmV1NV;
ig_did=4763A861-F18D-42E6-ACF0-A97371201B89;
mid=aPXFPQAEAAGtay5gnPS10s6q9sfs;
ds_user_id=312488908;
sessionid=312488908%3ATfy3bX853vi4X0%3A27%3AAYjVf3kJ3YkJ8owAZu6Sl78sct_AZ4eY4zCHspePnA
'''

cl = Client()
cl.login_by_cookie(cookie_string)
print(f"登录成功：@{cl.username} (ID: {cl.user_id})")
```

### 示例 2：安全的首次使用（推荐）
```python
from instagrapi import Client

cookie = 'sessionid=...; mid=...'

cl = Client()
cl.login_by_cookie(cookie)

# 只进行低风险的只读操作
user = cl.account_info()
print(f"用户名: {user.username}")
print(f"粉丝数: {user.follower_count}")

# 获取最近帖子
medias = cl.user_medias(user.pk, amount=5)
for media in medias:
    print(f"- {media.caption_text[:50]}...")

# 保存 session，下次使用
cl.dump_settings("session.json")
print("✅ Session 已保存，设备指纹将在后续请求中自动更新")
```

### 示例 3：错误处理
```python
from instagrapi import Client

try:
    cl = Client()
    cl.login_by_cookie("invalid cookie")
except ValueError as e:
    print(f"登录失败: {e}")
    # 输出: No 'sessionid' found in cookie string
```

## 错误说明

### ValueError: Cookie string cannot be empty
Cookie 字符串为空，请提供有效的 Cookie。

### ValueError: No 'sessionid' found in cookie string
Cookie 中没有找到 `sessionid` 字段，这是必需的。

### ValueError: Invalid sessionid length
sessionid 长度小于 30，可能已被截断或无效。

### ValueError: Cannot extract user_id from sessionid
sessionid 格式不正确，应该以数字开头（user_id）。

### ValueError: Failed to validate session
Cookie 已过期或无效，请重新从浏览器获取。

## 技术细节

### 设备指纹迁移策略

1. **初始状态**：使用浏览器的 `mid` (Machine ID) 和 Cookie
2. **首次请求**：Instagram 检测到 UA 不匹配（浏览器 Cookie + Android UA）
3. **服务器响应**：Instagram 在响应头中返回新的 `ig-set-x-mid`
4. **自动更新**：instagrapi 自动接收并保存新的 `mid`
5. **后续请求**：使用更新后的移动端设备指纹，风险降低

参见源码：[private.py:354-356](instagrapi/mixins/private.py#L354-L356)

### Cookie 解析流程

```python
# 1. 分割 Cookie 字符串
cookies = {}
for pair in cookie_string.split(';'):
    key, value = pair.split('=', 1)
    cookies[key.strip()] = value.strip()

# 2. 提取 sessionid
sessionid = cookies['sessionid']

# 3. 从 sessionid 提取 user_id
# 格式: "user_id%3Arest" 或 "user_id:rest"
user_id = re.search(r'^(\d+)', sessionid).group(1)

# 4. 构建 authorization_data
authorization_data = {
    "ds_user_id": user_id,
    "sessionid": sessionid,
    "should_use_header_over_cookies": True
}

# 5. 验证 session
user = cl.user_info_v1(int(user_id))
```

## 与其他登录方法的对比

| 方法 | Cookie 来源 | 风险 | 适用场景 |
|------|------------|------|---------|
| `login(username, password)` | 账号密码登录 | 🟢 低 | 长期稳定使用 |
| `login_by_sessionid(sessionid)` | 只需 sessionid | 🟡 中 | 快速登录 |
| `login_by_cookie(cookie_string)` | 浏览器完整 Cookie | 🟡 中 | 从浏览器快速迁移 |

## 最佳实践

1. **首次登录**：
   ```python
   cl = Client()
   cl.login_by_cookie(cookie)
   cl.dump_settings("session.json")  # 保存
   ```

2. **后续使用**：
   ```python
   cl = Client()
   cl.load_settings("session.json")  # 直接加载
   ```

3. **只读操作优先**：
   ```python
   # ✅ 推荐先做这些
   cl.account_info()
   cl.user_info(user_id)
   cl.user_medias(user_id)

   # ⚠️ 写操作建议等待一段时间后再做
   # cl.media_like(media_id)
   # cl.media_comment(media_id, text)
   ```

4. **Challenge 处理**：
   ```python
   def my_challenge_handler(username, choice):
       code = input(f"请输入验证码（发送到 {choice}）：")
       return code

   cl.challenge_code_handler = my_challenge_handler
   cl.login_by_cookie(cookie)
   ```

## 更多示例

完整示例代码请参见：
- [examples/cookie_login.py](examples/cookie_login.py) - 各种使用场景
- [test_cookie_login.py](test_cookie_login.py) - 单元测试

## 相关文档

- [登录过程分析](./CLAUDE.md) - 深入了解登录机制
- [session_login.py](examples/session_login.py) - Session 持久化示例
- [challenge_resolvers.py](examples/challenge_resolvers.py) - Challenge 处理示例
