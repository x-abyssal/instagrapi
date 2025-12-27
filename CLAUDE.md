# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`instagrapi` is a Python library providing an unofficial Instagram Private API wrapper. It supports both public (web) and private (mobile app) API requests with built-in challenge resolvers. The library uses reverse-engineering techniques to stay current with Instagram's API (last verified: May 25, 2025).

**Key Capabilities:**
- Authentication with username/password, sessionid, and 2FA support
- Upload/download photos, videos, IGTV, Reels, albums, and stories
- Interact with users, media, comments, insights, collections, locations, hashtags, and direct messages
- Challenge resolution for email and SMS verification
- Proxy support and rate limit handling

**Python Support:** >= 3.9

## Project Structure

```
instagrapi/
├── instagrapi/           # Core library code
│   ├── mixins/          # Mixin modules for different functionalities
│   ├── __init__.py      # Main Client class
│   ├── types.py         # Pydantic data models
│   ├── exceptions.py    # Custom exceptions
│   └── ...
├── tests/               # Test files
│   ├── tests.py         # Main test suite (~2000 lines)
│   ├── test_cookie_login.py
│   └── demo_cookie_login.py
├── examples/            # Usage examples
│   ├── cookie_login.py
│   ├── session_login.py
│   ├── challenge_resolvers.py
│   └── ...
├── fun-docs/            # Functional documentation
│   └── COOKIE_LOGIN_README.md
└── docs/                # MkDocs documentation
```

## Development Commands

### Testing

Run all tests and linting (with auto-formatting):
```bash
docker-compose run --rm test
```

Run specific test cases:
```bash
pytest -sv tests/tests.py::ClientMediaTestCase
pytest -sv tests/tests.py::ClientUserTestCase
```

Run all unit tests:
```bash
docker-compose run --rm tests
# or directly:
python -m unittest tests.tests
```

### Linting and Code Quality

Individual linters:
```bash
# Flake8 (syntax errors and undefined names)
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

# Isort (import sorting)
isort --check-only instagrapi
# Auto-fix:
isort instagrapi

# Bandit (security issues)
bandit --ini .bandit -r instagrapi
```

### Docker Development Environment

Interactive development container:
```bash
docker-compose run --rm devbox
# Then import and test the library interactively
```

### Documentation

Serve documentation locally:
```bash
docker-compose run --rm mkdocs
# Access at http://localhost:8000
```

Build documentation:
```bash
mkdocs build --strict
```

### Building and Publishing

Build package:
```bash
python -m build
```

Publish to PyPI:
```bash
twine upload dist/*
```

## Architecture

### Core Design: Mixin-Based Architecture

The `Client` class ([instagrapi/\_\_init\_\_.py](instagrapi/__init__.py)) inherits from 30+ mixins, each providing domain-specific functionality. This modular design keeps the codebase organized and maintainable.

**Main mixins** (located in [instagrapi/mixins/](instagrapi/mixins/)):
- `PublicRequestMixin` / `PrivateRequestMixin` - Base HTTP request handling for web and mobile APIs
- `LoginMixin` / `ChallengeResolveMixin` - Authentication and challenge handling
- `MediaMixin`, `UserMixin`, `StoryMixin` - Core Instagram object interactions
- `UploadPhotoMixin`, `UploadVideoMixin`, `UploadAlbumMixin`, `UploadClipMixin`, `UploadIGTVMixin` - Content upload handlers
- `DownloadPhotoMixin`, `DownloadVideoMixin`, `DownloadAlbumMixin`, `DownloadClipMixin`, `DownloadIGTVMixin` - Content download handlers
- `DirectMixin` - Direct messaging
- `HashtagMixin`, `LocationMixin`, `CollectionMixin` - Discovery and organization
- `InsightsMixin` - Analytics and metrics
- `TOTPMixin` - 2FA TOTP handling

### Request Flow

1. **Public vs Private API Selection**: The library intelligently chooses between web API (anonymous/public) and mobile API (authenticated/private) to avoid rate limits
2. **Request Layer**: All requests go through either `public_request()` or `private_request()` with built-in retries (3 attempts, exponential backoff)
3. **Exception Handling**: Rich exception hierarchy in [instagrapi/exceptions.py](instagrapi/exceptions.py) for granular error handling
4. **Data Models**: Pydantic-based types in [instagrapi/types.py](instagrapi/types.py) for validation (User, Media, Story, DirectMessage, etc.)

### Key Components

**[instagrapi/config.py](instagrapi/config.py)**:
- User-agent strings, API domain, login experiments, and capability flags
- Simulates Instagram mobile app (Android/iOS) to avoid detection

**[instagrapi/extractors.py](instagrapi/extractors.py)**:
- Parses Instagram API responses into typed Python objects
- Handles both public web and private mobile API response formats

**[instagrapi/utils.py](instagrapi/utils.py)**:
- Helper functions for signature generation, random delays, JSON serialization
- Rate limiting utilities

**[instagrapi/story.py](instagrapi/story.py)**:
- `StoryBuilder` class for creating stories with custom backgrounds, stickers, mentions, links

**Session Persistence**:
- `dump_settings()` / `load_settings()` save/restore authentication state to JSON files
- Avoids repeated logins which can trigger Instagram security checks

### Exception Handling

The library provides specific exceptions for different Instagram API errors:
- `LoginRequired`, `ChallengeRequired`, `TwoFactorRequired` - Authentication issues
- `ClientThrottledError`, `RateLimitError`, `PleaseWaitFewMinutes` - Rate limiting
- `PrivateAccount`, `UserNotFound`, `MediaUnavailable` - Access restrictions
- `ClientBadRequestError`, `ClientNotFoundError`, `ClientForbiddenError` - HTTP errors

Developers can implement custom exception handlers via `client.handle_exception` callback.

## Testing Strategy

**Test Directory**: [tests/](tests/) contains all test files:
- [tests/tests.py](tests/tests.py) - Main test suite (single monolithic file with ~2000 lines)
- [tests/test_cookie_login.py](tests/test_cookie_login.py) - Cookie-based authentication tests
- [tests/demo_cookie_login.py](tests/demo_cookie_login.py) - Cookie login demonstration

Test classes use Instagram account credentials from environment variables:
- `IG_USERNAME`, `IG_PASSWORD` - Basic auth
- `IG_SESSIONID` - Session-based auth (optional)
- `TEST_ACCOUNTS_URL` - URL to fetch test account credentials

CI runs subset of tests (`ClientMediaTestCase`, `ClientUserTestCase`) to avoid rate limits.

## Important Notes

### Instagram API Versioning
The library mimics specific Instagram app versions defined in [config.py](instagrapi/config.py). When Instagram updates their API, these constants need updating based on reverse-engineering.

### Rate Limiting
Instagram aggressively rate-limits API requests. Use:
- `delay_range` parameter in Client constructor for random delays between requests
- Session persistence to reduce login frequency
- Proxy rotation for higher throughput (see [examples/next_proxy.py](examples/next_proxy.py))

### Challenge Handlers
When Instagram detects suspicious activity, it triggers challenges (email/SMS verification). Implement custom handlers:
```python
def my_challenge_code_handler(username, choice):
    # Fetch code from email/SMS service
    return code

client.challenge_code_handler = my_challenge_code_handler
```

See [examples/challenge_resolvers.py](examples/challenge_resolvers.py) for working examples.

### Mobile Device Simulation
The library generates realistic mobile device signatures (device ID, Android version, screen resolution, etc.) stored in settings. Changing devices frequently can trigger security checks.

### Cookie-Based Authentication
Alternative authentication method using browser cookies. See [fun-docs/COOKIE_LOGIN_README.md](fun-docs/COOKIE_LOGIN_README.md) for detailed documentation and [examples/cookie_login.py](examples/cookie_login.py) for implementation examples.

## Dependencies

**Core:**
- `requests` - HTTP client
- `pydantic` - Data validation
- `moviepy` - Video processing
- `pycryptodomex` - Encryption/signatures
- `PySocks` - Proxy support

**Testing:**
- `pytest`, `pytest-xdist` - Test framework
- `flake8`, `isort`, `bandit` - Linting and security

## Common Pitfalls

1. **Don't call login() repeatedly** - Use session persistence with `dump_settings()`/`load_settings()`
2. **Handle rate limits gracefully** - Implement exponential backoff and respect Instagram's limits
3. **Test with throwaway accounts** - Instagram may ban accounts used for automation
4. **Proxy usage** - Residential proxies work best; datacenter IPs often get blocked
5. **Updates required** - Instagram API changes frequently; expect maintenance overhead
