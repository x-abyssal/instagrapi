"""
Simple demo to test auto session management without actual login

This script tests the core functionality without requiring Instagram credentials.
"""

import json
import shutil
from pathlib import Path
from instagrapi import Client


def cleanup_test_dir():
    """Remove test session directory"""
    test_dir = Path("./test_sessions")
    if test_dir.exists():
        shutil.rmtree(test_dir)


def create_mock_session():
    """Create a mock session for testing"""
    cl = Client(session_dir="./test_sessions")

    # Manually set attributes to simulate a logged-in state
    cl.username = "test_user"

    # Create mock settings with authorization_data (user_id is derived from this)
    cl.authorization_data = {
        "ds_user_id": "123456789",
        "sessionid": "123456789%3Atest_session",
        "should_use_header_over_cookies": False,
    }

    # Create mock settings
    cl.settings = {
        "uuids": {
            "phone_id": "test-phone-id",
            "uuid": "test-uuid",
            "client_session_id": "test-session-id",
            "advertising_id": "test-ad-id",
            "android_device_id": "test-device-id",
            "request_id": "test-request-id",
            "tray_session_id": "test-tray-id",
        },
        "authorization_data": {
            "ds_user_id": "123456789",
            "sessionid": "123456789%3Atest_session",
            "should_use_header_over_cookies": False,
        },
        "cookies": {},
        "mid": "test-mid",
        "ig_u_rur": "test-rur",
        "ig_www_claim": "0",
        "last_login": 1640000000.0,
    }

    return cl


def test_auto_dump_settings():
    """Test auto_dump_settings method"""
    print("Test 1: auto_dump_settings()")

    cl = create_mock_session()

    # Auto save
    saved_path = cl.auto_dump_settings()
    print(f"✓ Session saved to: {saved_path}")

    # Verify directory structure
    assert saved_path.exists(), "Settings file should exist"
    assert saved_path.parent.name == "test_user", "Directory should be named after username"
    assert saved_path.name == "settings.json", "File should be named settings.json"

    # Verify index file
    index_path = Path("./test_sessions/index.json")
    assert index_path.exists(), "Index file should exist"

    with open(index_path, "r") as f:
        index = json.load(f)
        assert "test_user" in index, "Index should contain username key"
        assert "123456789" in index, "Index should contain user_id key"
        assert index["test_user"]["session_dir"] == "test_user", "Index should point to correct directory"

    print("✓ All assertions passed\n")


def test_restore_settings():
    """Test restore_settings method"""
    print("Test 2: restore_settings()")

    # First create and save a session
    cl1 = create_mock_session()
    cl1.auto_dump_settings()

    # Load by username
    cl2 = Client(session_dir="./test_sessions")
    settings = cl2.restore_settings("test_user")
    print(f"✓ Loaded by username: {settings.get('authorization_data', {}).get('ds_user_id')}")

    # Load by user_id
    cl3 = Client(session_dir="./test_sessions")
    settings = cl3.restore_settings(123456789)
    print(f"✓ Loaded by user_id: {settings.get('authorization_data', {}).get('ds_user_id')}")

    # Load by cookie string
    cl4 = Client(session_dir="./test_sessions")
    cookie_str = "sessionid=123456789%3Atest_session; other=value"
    settings = cl4.restore_settings(cookie_str)
    print(f"✓ Loaded by cookie string: {settings.get('authorization_data', {}).get('ds_user_id')}\n")


def test_get_available_sessions():
    """Test get_available_sessions method"""
    print("Test 3: get_available_sessions()")

    # List all sessions (including from previous tests)
    sessions = Client.get_available_sessions("./test_sessions")
    print(f"✓ Found {len(sessions)} sessions")

    for session in sessions:
        print(f"  - {session['username']} (ID: {session['user_id']})")

    assert len(sessions) >= 1, "Should find at least 1 session"
    print()


def test_error_handling():
    """Test error handling"""
    print("Test 4: Error handling")

    # Test loading non-existent session
    try:
        cl = Client(session_dir="./test_sessions")
        cl.restore_settings("nonexistent_user")
        assert False, "Should raise FileNotFoundError"
    except FileNotFoundError as e:
        print(f"✓ Correctly raised FileNotFoundError: {str(e)[:50]}...")

    # Test saving without login
    try:
        cl = Client(session_dir="./test_sessions")
        cl.auto_dump_settings()
        assert False, "Should raise ValueError"
    except ValueError as e:
        print(f"✓ Correctly raised ValueError: {str(e)[:50]}...")

    print()


def main():
    print("=" * 60)
    print("Auto Session Management - Demo Test")
    print("=" * 60)
    print()

    try:
        # Cleanup before tests
        cleanup_test_dir()

        # Run tests
        test_auto_dump_settings()
        test_restore_settings()
        test_get_available_sessions()
        test_error_handling()

        print("=" * 60)
        print("✅ All tests passed successfully!")
        print("=" * 60)
        print()
        print("Directory structure created:")
        print("./test_sessions/")
        print("├── index.json")
        print("├── test_user/")
        print("│   └── settings.json")
        print("├── test_user_0/")
        print("│   └── settings.json")
        print("├── test_user_1/")
        print("│   └── settings.json")
        print("└── test_user_2/")
        print("    └── settings.json")
        print()
        print("You can inspect the files to see the structure.")
        print("Run cleanup_test_dir() to remove test files.")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Optional: cleanup after tests
        # cleanup_test_dir()
        pass


if __name__ == "__main__":
    main()
