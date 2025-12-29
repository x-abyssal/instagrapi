"""
Example: Parse Browser-Exported Cookie JSON

This example demonstrates how to use the cookie parser utilities to convert
browser-exported cookie JSON data into usable cookie strings for Instagram
authentication.

Supported formats:
- Browser extension exports (EditThisCookie, Cookie-Editor, etc.)
- Chrome DevTools cookie JSON
- Firefox DevTools cookie JSON
- Multi-line cookie files (like fun-docs/10 COOKIES.txt)
"""

from instagrapi import Client
from instagrapi.cookie_parser import (
    extract_cookie_info,
    get_sessionid_from_json,
    parse_browser_cookies_json,
    parse_cookies_file,
)


# Example 1: Parse single JSON cookie array
def example_parse_json_string():
    """Parse cookie JSON string from browser"""
    print("=" * 70)
    print("Example 1: Parse JSON Cookie String")
    print("=" * 70)

    # This is the format you get from browser extensions like EditThisCookie
    json_cookies = '''[
        {
            "domain": ".instagram.com",
            "expirationDate": 1798244001670,
            "name": "sessionid",
            "value": "79608022750%3AGoXS08csI4bD7B%3A1%3AAYjAwVRYge4eQaVH"
        },
        {
            "domain": ".instagram.com",
            "name": "mid",
            "value": "aUxY0wABAAHc6RX2S4k5JBIWSqSr"
        },
        {
            "domain": ".instagram.com",
            "name": "csrftoken",
            "value": "s4YSjJRfSiALNClHfcYvuczbqosDoe5k"
        },
        {
            "domain": ".instagram.com",
            "name": "ds_user_id",
            "value": "79608022750"
        }
    ]'''

    # Convert to cookie string
    cookie_string = parse_browser_cookies_json(json_cookies)
    print(f"\nConverted cookie string:")
    print(f"{cookie_string[:100]}...")

    # Login with the cookie
    cl = Client()
    try:
        cl.login_by_cookie(cookie_string)
        print(f"\n✅ Logged in as: @{cl.username}")
        print(f"   User ID: {cl.user_id}")
    except Exception as e:
        print(f"\n❌ Login failed: {e}")
        print("   (This is expected if using example cookies)")

    print()


# Example 2: Parse from Python list
def example_parse_list():
    """Parse cookie list (already parsed JSON)"""
    print("=" * 70)
    print("Example 2: Parse Cookie List (Python objects)")
    print("=" * 70)

    # If you've already parsed the JSON
    cookies = [
        {"name": "sessionid", "value": "123456%3Axxx%3A27%3Ayyy"},
        {"name": "mid", "value": "aUxY0wABAAHc6RX2S4k5JBIWSqSr"},
        {"name": "ds_user_id", "value": "123456"},
    ]

    cookie_string = parse_browser_cookies_json(cookies)
    print(f"\nCookie string: {cookie_string}")
    print()


# Example 3: Parse only essential cookies
def example_essential_cookies_only():
    """Parse only essential cookies (filter out unnecessary ones)"""
    print("=" * 70)
    print("Example 3: Parse Essential Cookies Only")
    print("=" * 70)

    json_cookies = '''[
        {"name": "sessionid", "value": "xxx"},
        {"name": "mid", "value": "yyy"},
        {"name": "some_other_cookie", "value": "zzz"},
        {"name": "another_cookie", "value": "aaa"}
    ]'''

    # Include all cookies
    all_cookies = parse_browser_cookies_json(json_cookies, include_all=True)
    print(f"\nAll cookies: {all_cookies}")

    # Essential cookies only
    essential = parse_browser_cookies_json(json_cookies, include_all=False)
    print(f"Essential only: {essential}")
    print()


# Example 4: Parse multi-line cookie file
def example_parse_file():
    """Parse a file with multiple cookie sets (one JSON array per line)"""
    print("=" * 70)
    print("Example 4: Parse Multi-Account Cookie File")
    print("=" * 70)

    # Example file path (like fun-docs/10 COOKIES.txt)
    file_path = "fun-docs/10 COOKIES.txt"

    try:
        # Parse specific line (e.g., first account)
        print(f"\nParsing line 1 from {file_path}:")
        cookie_str = parse_cookies_file(file_path, line_number=1)
        print(f"Cookie: {cookie_str[:100]}...")

        # Extract info
        info = extract_cookie_info(cookie_str)
        print(f"\nExtracted info:")
        print(f"  - sessionid: {info.get('sessionid', 'N/A')[:50]}...")
        print(f"  - mid: {info.get('mid', 'N/A')}")
        print(f"  - ds_user_id: {info.get('ds_user_id', 'N/A')}")

    except FileNotFoundError:
        print(f"\n⚠️  File not found: {file_path}")
        print("   This is expected if running outside the repository root")
    except Exception as e:
        print(f"\n❌ Error: {e}")

    print()


# Example 5: Parse all accounts from file
def example_parse_all_accounts():
    """Parse all cookie sets from a multi-account file"""
    print("=" * 70)
    print("Example 5: Parse All Accounts from File")
    print("=" * 70)

    file_path = "fun-docs/10 COOKIES.txt"

    try:
        # Parse all lines
        all_cookies = parse_cookies_file(file_path)
        print(f"\nFound {len(all_cookies)} cookie sets")

        # Display each one
        for i, cookie_str in enumerate(all_cookies, 1):
            info = extract_cookie_info(cookie_str)
            user_id = info.get('ds_user_id', 'Unknown')
            print(f"\nAccount {i}:")
            print(f"  - User ID: {user_id}")
            print(f"  - Has sessionid: {'sessionid' in info}")
            print(f"  - Has mid: {'mid' in info}")
            print(f"  - Cookie: {cookie_str[:80]}...")

    except FileNotFoundError:
        print(f"\n⚠️  File not found: {file_path}")
    except Exception as e:
        print(f"\n❌ Error: {e}")

    print()


# Example 6: Quick sessionid extraction
def example_extract_sessionid():
    """Extract only sessionid from JSON (minimal parsing)"""
    print("=" * 70)
    print("Example 6: Extract Sessionid Only")
    print("=" * 70)

    json_cookies = '''[
        {"name": "csrftoken", "value": "xxx"},
        {"name": "sessionid", "value": "123456%3Axxx%3A27%3Ayyy"},
        {"name": "mid", "value": "zzz"}
    ]'''

    sessionid = get_sessionid_from_json(json_cookies)
    print(f"\nExtracted sessionid: {sessionid}")

    # Can use directly with login_by_cookie
    if sessionid:
        cl = Client()
        try:
            # Both work:
            # Method 1: login_by_cookie with minimal string
            cl.login_by_cookie(f"sessionid={sessionid}")

            # Method 2: login_by_sessionid (original method)
            # cl.login_by_sessionid(sessionid)

            print(f"✅ Could login with sessionid only")
        except Exception as e:
            print(f"❌ Login failed: {e}")

    print()


# Example 7: Batch login multiple accounts
def example_batch_login():
    """Login to multiple accounts from a cookie file"""
    print("=" * 70)
    print("Example 7: Batch Login Multiple Accounts")
    print("=" * 70)

    file_path = "fun-docs/10 COOKIES.txt"

    try:
        all_cookies = parse_cookies_file(file_path)

        for i, cookie_str in enumerate(all_cookies[:3], 1):  # Test first 3 accounts
            print(f"\n--- Attempting login for account {i} ---")

            cl = Client()
            try:
                cl.login_by_cookie(cookie_str)
                print(f"✅ Logged in as: @{cl.username} (ID: {cl.user_id})")

                # Perform some operation
                user = cl.account_info()
                print(f"   Followers: {user.follower_count}")
                print(f"   Following: {user.following_count}")

                # Save session
                session_file = f"session_account_{i}.json"
                cl.dump_settings(session_file)
                print(f"   Session saved to: {session_file}")

            except Exception as e:
                print(f"❌ Login failed: {e}")

    except FileNotFoundError:
        print(f"\n⚠️  File not found: {file_path}")
    except Exception as e:
        print(f"\n❌ Error: {e}")

    print()


# Example 8: Error handling
def example_error_handling():
    """Demonstrate error handling"""
    print("=" * 70)
    print("Example 8: Error Handling")
    print("=" * 70)

    test_cases = [
        ("Empty string", ""),
        ("Invalid JSON", "not json"),
        ("Empty array", "[]"),
        ("No name/value", '[{"foo": "bar"}]'),
        ("Valid", '[{"name": "sessionid", "value": "xxx"}]'),
    ]

    for name, json_data in test_cases:
        print(f"\nTest: {name}")
        try:
            result = parse_browser_cookies_json(json_data)
            print(f"  ✅ Success: {result}")
        except ValueError as e:
            print(f"  ❌ Error: {e}")

    print()


if __name__ == "__main__":
    print("\n")
    print("=" * 70)
    print("Instagram Browser Cookie Parser Examples")
    print("=" * 70)
    print()

    # Run all examples
    example_parse_json_string()
    example_parse_list()
    example_essential_cookies_only()
    example_parse_file()
    example_parse_all_accounts()
    example_extract_sessionid()
    # example_batch_login()  # Uncomment to test actual logins
    example_error_handling()

    print("=" * 70)
    print("💡 Usage Tips:")
    print("=" * 70)
    print("""
1. Export cookies from browser:
   - Chrome: DevTools -> Application -> Cookies -> Copy as JSON
   - Firefox: DevTools -> Storage -> Cookies
   - Use browser extensions: EditThisCookie, Cookie-Editor

2. Parse and login:
   from instagrapi import Client
   from instagrapi.cookie_parser import parse_browser_cookies_json

   cookie_str = parse_browser_cookies_json(json_data)
   cl = Client()
   cl.login_by_cookie(cookie_str)

3. For multi-account files:
   from instagrapi.cookie_parser import parse_cookies_file

   cookies = parse_cookies_file('cookies.txt', line_number=1)
   cl.login_by_cookie(cookies)

4. Save session after login:
   cl.dump_settings('session.json')

5. Resume from saved session:
   cl.load_settings('session.json')
""")
    print("=" * 70)
