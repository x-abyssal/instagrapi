"""Example: Login using browser cookie string

This example demonstrates how to use the login_by_cookie() method to authenticate
using cookies copied directly from your browser's DevTools.

IMPORTANT: This method uses cookies from desktop browsers with Android mobile UA,
which may trigger Instagram security checks. The "gradual migration" strategy is
used where Instagram server will naturally update device fingerprints in subsequent
requests to reduce risk.

Risk Level: Medium - Use for read-only operations initially to build trust.
"""

from instagrapi import Client

# Example 1: Basic usage with your cookie string
def basic_cookie_login():
    """Login with cookie string from browser DevTools"""

    # Step 1: Copy cookie string from browser
    # Chrome/Edge: DevTools -> Application -> Cookies -> instagram.com -> Copy all cookies
    # Firefox: DevTools -> Storage -> Cookies -> instagram.com -> Copy all

    cookie_string = (
        'csrftoken=ssSbbZh1RzdKYWm3uiPg5-; '
        'datr=PcX1aMMdCNzF_kelTFfmV1NV; '
        'ig_did=4763A861-F18D-42E6-ACF0-A97371201B89; '
        'mid=aPXFPQAEAAGtay5gnPS10s6q9sfs; '
        'ds_user_id=312488908; '
        'ps_l=1; ps_n=1; '
        'sessionid=312488908%3ATfy3bX853vi4X0%3A27%3AAYjVf3kJ3YkJ8owAZu6Sl78sct_AZ4eY4zCHspePnA; '
        'rur="VLL\054312488908\0541798178884:01feb62012438998ab018a99c52c7c6b97ae4a7c23ff3847f5218e1b69afba4927c6106d"; '
        'wd=850x788'
    )

    # Step 2: Create client and login
    cl = Client()
    cl.login_by_cookie(cookie_string)

    # Step 3: Verify login
    print(f"✅ Logged in as: @{cl.username}")
    print(f"   User ID: {cl.user_id}")

    # Step 4: Save session for future use
    cl.dump_settings("session_from_cookie.json")
    print("✅ Session saved to session_from_cookie.json")

    return cl


# Example 2: Login and perform safe read-only operations
def cookie_login_with_safe_operations():
    """Login with cookie and perform low-risk read operations"""

    cookie_string = 'sessionid=312488908%3ATfy3bX853vi4X0%3A27%3A...; mid=aPXFPQAEAAGtay5gnPS10s6q9sfs'

    cl = Client()
    cl.login_by_cookie(cookie_string)

    # Perform read-only operations (lower risk)
    print(f"\n📊 Account Information:")
    user = cl.account_info()
    print(f"   Username: @{user.username}")
    print(f"   Full Name: {user.full_name}")
    print(f"   Followers: {user.follower_count}")
    print(f"   Following: {user.following_count}")
    print(f"   Bio: {user.biography}")

    # Get recent media
    print(f"\n📸 Recent Posts:")
    medias = cl.user_medias(user.pk, amount=5)
    for i, media in enumerate(medias, 1):
        print(f"   {i}. {media.caption_text[:50] if media.caption_text else 'No caption'}...")
        print(f"      Likes: {media.like_count}, Comments: {media.comment_count}")

    # Save session after successful operations
    cl.dump_settings("session_from_cookie.json")
    print("\n✅ Session updated and saved")

    return cl


# Example 3: Resume from saved session (recommended for subsequent uses)
def resume_from_saved_session():
    """Load session from file (avoids repeated cookie extraction)"""
    import os

    if not os.path.exists("session_from_cookie.json"):
        print("❌ No saved session found. Run cookie_login_with_safe_operations() first.")
        return None

    cl = Client()
    cl.load_settings("session_from_cookie.json")

    # Verify session is still valid
    try:
        user = cl.account_info()
        print(f"✅ Resumed session for @{user.username}")

        # By now, Instagram has updated device fingerprints to mobile-compatible values
        print(f"\n📱 Device fingerprint status:")
        print(f"   MID (Machine ID): {cl.mid}")
        print(f"   Android Device ID: {cl.android_device_id}")
        print(f"   Note: These values have been updated by Instagram server")

        return cl
    except Exception as e:
        print(f"❌ Session expired or invalid: {e}")
        print("   Please login again with fresh cookies")
        return None


# Example 4: Error handling
def cookie_login_with_error_handling():
    """Demonstrate proper error handling"""

    # Invalid cookie string examples
    invalid_cookies = [
        "",  # Empty string
        "foo=bar; baz=qux",  # No sessionid
        "sessionid=short",  # Too short
        "sessionid=invalid_format_no_userid",  # Cannot extract user_id
    ]

    for i, cookie in enumerate(invalid_cookies, 1):
        print(f"\nTest {i}: {cookie[:50]}...")
        try:
            cl = Client()
            cl.login_by_cookie(cookie)
            print("   ✅ Success")
        except ValueError as e:
            print(f"   ❌ Expected error: {e}")

    # Valid cookie with expired session
    print("\nTest 5: Valid format but expired session")
    expired_cookie = "sessionid=123456789%3Aexpired%3A27%3Afake; mid=test"
    try:
        cl = Client()
        cl.login_by_cookie(expired_cookie)
        print("   ✅ Success")
    except ValueError as e:
        print(f"   ❌ Expected error: {e}")


# Example 5: Extract only sessionid from full cookie string (utility function)
def extract_sessionid_only(cookie_string: str) -> str:
    """Utility: Extract only sessionid from cookie string"""
    for pair in cookie_string.split(';'):
        pair = pair.strip()
        if pair.startswith('sessionid='):
            return pair.split('=', 1)[1]
    raise ValueError("No sessionid found in cookie string")


# Example 6: Login with minimal cookie (only sessionid)
def minimal_cookie_login():
    """Login with only sessionid (if you don't want to share full cookies)"""

    full_cookie = 'csrftoken=xxx; sessionid=312488908%3ATfy3bX853vi4X0%3A27%3A...; mid=yyy'

    # Extract only sessionid
    sessionid_only = extract_sessionid_only(full_cookie)

    # Both methods work:
    # Method 1: login_by_cookie (will parse and extract sessionid)
    cl = Client()
    cl.login_by_cookie(f"sessionid={sessionid_only}")

    # Method 2: login_by_sessionid (original method, sessionid only)
    # cl.login_by_sessionid(sessionid_only)

    print(f"✅ Logged in with minimal cookie: @{cl.username}")
    return cl


if __name__ == "__main__":
    print("=" * 70)
    print("Instagram Cookie Login Examples")
    print("=" * 70)

    # Uncomment the example you want to run:

    # Example 1: Basic login
    # client = basic_cookie_login()

    # Example 2: Login with safe operations (recommended first run)
    # client = cookie_login_with_safe_operations()

    # Example 3: Resume from saved session (recommended for subsequent runs)
    # client = resume_from_saved_session()

    # Example 4: Error handling demonstration
    # cookie_login_with_error_handling()

    # Example 5: Minimal cookie login
    # client = minimal_cookie_login()

    print("\n" + "=" * 70)
    print("💡 Tips:")
    print("   1. First run: Use cookie_login_with_safe_operations()")
    print("   2. Perform only READ operations initially to build trust")
    print("   3. Save session with dump_settings()")
    print("   4. Subsequent runs: Use resume_from_saved_session()")
    print("   5. Device fingerprints will be updated by Instagram naturally")
    print("=" * 70)
