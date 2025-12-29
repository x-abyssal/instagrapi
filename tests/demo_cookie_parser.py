"""
Demo: Parse and use browser cookie JSON data

This demo shows how to parse cookie JSON exported from browsers
and use it to login to Instagram.
"""

from instagrapi import Client
from instagrapi.cookie_parser import (
    extract_cookie_info,
    parse_browser_cookies_json,
    parse_cookies_file,
)


def demo_parse_and_display():
    """Demo: Parse cookies from file and display info"""
    print("=" * 70)
    print("Demo: Parse Browser Cookie JSON")
    print("=" * 70)

    file_path = "fun-docs/10 COOKIES.txt"

    try:
        # Parse all cookies from file
        print(f"\nParsing cookies from: {file_path}")
        all_cookies = parse_cookies_file(file_path)
        print(f"✅ Found {len(all_cookies)} cookie sets\n")

        # Display info for each account
        for i, cookie_str in enumerate(all_cookies, 1):
            info = extract_cookie_info(cookie_str)

            print(f"Account {i}:")
            print(f"  User ID: {info.get('ds_user_id', 'Unknown')}")
            print(f"  MID: {info.get('mid', 'N/A')}")
            print(f"  Has sessionid: {'✅' if 'sessionid' in info else '❌'}")
            print(f"  Has csrftoken: {'✅' if 'csrftoken' in info else '❌'}")
            print(f"  Has ig_did: {'✅' if 'ig_did' in info else '❌'}")

            # Show partial sessionid
            if 'sessionid' in info:
                sessionid = info['sessionid']
                print(f"  Sessionid: {sessionid[:40]}...")

            print()

    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        print("   Please ensure you're running from the repository root")
    except Exception as e:
        print(f"❌ Error: {e}")


def demo_parse_single_account():
    """Demo: Parse and prepare single account for login"""
    print("=" * 70)
    print("Demo: Parse Single Account")
    print("=" * 70)

    file_path = "fun-docs/10 COOKIES.txt"

    try:
        # Parse first account
        print(f"\nParsing account #1 from {file_path}")
        cookie_str = parse_cookies_file(file_path, line_number=1)

        print(f"✅ Parsed successfully\n")
        print(f"Cookie string length: {len(cookie_str)} characters")
        print(f"Cookie preview: {cookie_str[:100]}...\n")

        # Extract and display info
        info = extract_cookie_info(cookie_str)
        print("Extracted information:")
        print(f"  - User ID: {info.get('ds_user_id', 'N/A')}")
        print(f"  - MID: {info.get('mid', 'N/A')}")
        print(f"  - CSRF Token: {info.get('csrftoken', 'N/A')[:30]}...")
        print(f"  - IG Device ID: {info.get('ig_did', 'N/A')}")
        print(f"  - Session ID: {info.get('sessionid', 'N/A')[:60]}...")

        print("\n✅ This cookie string is ready to use with Client.login_by_cookie()")

    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
    except Exception as e:
        print(f"❌ Error: {e}")


def demo_json_string_parsing():
    """Demo: Parse JSON string directly"""
    print("=" * 70)
    print("Demo: Parse JSON String")
    print("=" * 70)

    # Example JSON from browser export
    json_cookies = '''[
        {
            "domain": ".instagram.com",
            "name": "sessionid",
            "value": "123456789%3Axxx%3A27%3Ayyy"
        },
        {
            "domain": ".instagram.com",
            "name": "mid",
            "value": "aUxY0wABAAHc6RX2S4k5JBIWSqSr"
        },
        {
            "domain": ".instagram.com",
            "name": "csrftoken",
            "value": "abc123def456"
        },
        {
            "domain": ".instagram.com",
            "name": "ds_user_id",
            "value": "123456789"
        }
    ]'''

    print("\nInput JSON:")
    print(json_cookies[:200] + "...\n")

    # Parse to cookie string
    cookie_str = parse_browser_cookies_json(json_cookies)

    print("Output cookie string:")
    print(cookie_str)
    print()

    # Extract info
    info = extract_cookie_info(cookie_str)
    print("Extracted values:")
    for key, value in info.items():
        print(f"  - {key}: {value}")


def demo_essential_cookies_only():
    """Demo: Filter essential cookies"""
    print("\n" + "=" * 70)
    print("Demo: Essential Cookies Filter")
    print("=" * 70)

    json_cookies = '''[
        {"name": "sessionid", "value": "xxx"},
        {"name": "mid", "value": "yyy"},
        {"name": "csrftoken", "value": "zzz"},
        {"name": "random_cookie", "value": "aaa"},
        {"name": "another_cookie", "value": "bbb"},
        {"name": "unnecessary", "value": "ccc"}
    ]'''

    print("\nAll cookies:")
    all_cookies = parse_browser_cookies_json(json_cookies, include_all=True)
    print(all_cookies)

    print("\nEssential cookies only:")
    essential = parse_browser_cookies_json(json_cookies, include_all=False)
    print(essential)

    print(f"\nReduced from {len(all_cookies.split(';'))} to {len(essential.split(';'))} cookies")


if __name__ == "__main__":
    print("\n")
    print("=" * 70)
    print("Instagram Browser Cookie Parser - Demonstration")
    print("=" * 70)
    print()

    # Run demos
    demo_parse_and_display()
    print("\n")
    demo_parse_single_account()
    print("\n")
    demo_json_string_parsing()
    print("\n")
    demo_essential_cookies_only()

    print("\n" + "=" * 70)
    print("💡 How to use in your code:")
    print("=" * 70)
    print("""
from instagrapi import Client
from instagrapi.cookie_parser import parse_cookies_file

# Parse cookie from file
cookie_str = parse_cookies_file('cookies.txt', line_number=1)

# Login with cookie
cl = Client()
cl.login_by_cookie(cookie_str)

# Verify login
print(f"Logged in as: @{cl.username}")

# Save session for future use
cl.dump_settings('session.json')

# Next time, just load the session
cl = Client()
cl.load_settings('session.json')
""")
    print("=" * 70)
