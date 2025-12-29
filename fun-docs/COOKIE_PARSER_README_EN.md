# Cookie Parser Utility

## Overview

The Cookie Parser is a utility module for parsing browser-exported cookie JSON data and converting it into a format compatible with instagrapi's `login_by_cookie()` method.

## Key Features

- ✅ Parse browser-exported JSON cookie data
- ✅ Support single and batch account processing
- ✅ Automatic filtering of essential cookies
- ✅ Read multiple accounts from file (one JSON array per line)
- ✅ Rich error handling and validation
- ✅ Full type hints and documentation

## Quick Start

### 1. Parse Single Account

```python
from instagrapi import Client
from instagrapi.cookie_parser import parse_browser_cookies_json

# JSON from browser export
json_cookies = '''[
    {"name": "sessionid", "value": "123%3Axxx%3A27%3Ayyy"},
    {"name": "mid", "value": "aUxY0wABAAHc6RX2S4k5JBIWSqSr"}
]'''

# Parse to cookie string
cookie_str = parse_browser_cookies_json(json_cookies)

# Login
cl = Client()
cl.login_by_cookie(cookie_str)
print(f"Logged in as: @{cl.username}")

# Save session
cl.dump_settings('session.json')
```

### 2. Parse from File

```python
from instagrapi import Client
from instagrapi.cookie_parser import parse_cookies_file

# Parse first account from file
cookie_str = parse_cookies_file('cookies.txt', line_number=1)

# Login
cl = Client()
cl.login_by_cookie(cookie_str)
```

### 3. Batch Processing

```python
from instagrapi.cookie_parser import parse_cookies_file

# Parse all accounts
all_cookies = parse_cookies_file('cookies.txt')

for i, cookie_str in enumerate(all_cookies, 1):
    cl = Client()
    cl.login_by_cookie(cookie_str)
    print(f"Account {i}: @{cl.username}")
    cl.dump_settings(f'session_{i}.json')
```

## Core Functions

### `parse_browser_cookies_json(json_data, include_all=True)`

Parse browser cookie JSON and convert to cookie string.

**Parameters:**
- `json_data`: JSON string or list of cookie dicts
- `include_all`: Include all cookies (True) or only essential ones (False)

**Returns:** Cookie string in format `"key1=value1; key2=value2"`

### `parse_cookies_file(file_path, line_number=None, include_all=True)`

Parse cookies from file (one JSON array per line).

**Parameters:**
- `file_path`: Path to cookie file
- `line_number`: Parse specific line (1-indexed), or None for all lines
- `include_all`: Include all cookies or only essential ones

**Returns:** Single cookie string or list of strings

### `extract_cookie_info(cookie_string)`

Extract individual cookie values from cookie string.

**Returns:** Dict mapping cookie names to values

### `get_sessionid_from_json(json_data)`

Quick extraction of sessionid only.

**Returns:** Sessionid value or None if not found

## Supported Data Sources

### Browser DevTools

**Chrome/Edge:**
1. Open DevTools (F12)
2. Application → Cookies → `instagram.com`
3. Copy cookie data

**Firefox:**
1. Open DevTools (F12)
2. Storage → Cookies → `instagram.com`
3. Copy cookie data

### Browser Extensions

- EditThisCookie
- Cookie-Editor
- Export Cookies
- Any cookie export tool

### Expected JSON Format

```json
[
    {
        "domain": ".instagram.com",
        "name": "sessionid",
        "value": "123456%3Axxx%3A27%3Ayyy",
        "expirationDate": 1798244001670,
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

## File Format

Multi-account cookie file (e.g., `cookies.txt`):
```
[{"name":"sessionid","value":"xxx1"},{"name":"mid","value":"yyy1"}]
[{"name":"sessionid","value":"xxx2"},{"name":"mid","value":"yyy2"}]
[{"name":"sessionid","value":"xxx3"},{"name":"mid","value":"yyy3"}]
```

Each line is one JSON array representing one account's cookies.

See [fun-docs/10 COOKIES.txt](10 COOKIES.txt) for a real example with 10 accounts.

## Essential Cookies

When `include_all=False`, only these cookies are included:

| Cookie Name | Description | Required |
|------------|-------------|----------|
| `sessionid` | Session ID | ✅ Required |
| `mid` | Machine ID | Recommended |
| `csrftoken` | CSRF token | Recommended |
| `ds_user_id` | User ID | Recommended |
| `ig_did` | Instagram device ID | Optional |
| `datr` | Device tracking token | Optional |
| `wd` | Window dimensions | Optional |
| `rur` | Routing info | Optional |

## Testing

Run unit tests:
```bash
python -m unittest tests.test_cookie_parser -v
```

Run demo:
```bash
PYTHONPATH=. python tests/demo_cookie_parser.py
```

## Examples

See:
- [examples/parse_browser_cookies.py](../examples/parse_browser_cookies.py) - Complete examples
- [tests/demo_cookie_parser.py](../tests/demo_cookie_parser.py) - Demo script
- [tests/test_cookie_parser.py](../tests/test_cookie_parser.py) - Unit tests

## Best Practices

1. **First login**: Use only read operations initially
2. **Save session**: Always save session after successful login
3. **Resume from session**: Use `load_settings()` for subsequent runs
4. **Security**: Don't commit cookie files to version control

## Error Handling

```python
from instagrapi.cookie_parser import parse_browser_cookies_json

try:
    cookie_str = parse_browser_cookies_json(json_data)
    cl.login_by_cookie(cookie_str)
except ValueError as e:
    print(f"Parse error: {e}")
except FileNotFoundError as e:
    print(f"File not found: {e}")
```

## Related Documentation

- [COOKIE_LOGIN_README.md](COOKIE_LOGIN_README.md) - Cookie login details
- [examples/cookie_login.py](../examples/cookie_login.py) - Cookie login examples
- [COOKIE_PARSER_README.md](COOKIE_PARSER_README.md) - Chinese version (detailed)
