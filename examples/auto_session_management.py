"""
Auto Session Management Example

This example demonstrates how to use the new auto session management features:
- auto_dump_settings(): Automatically save session to organized directory structure
- restore_settings(): Intelligently load session by username, user_id, or cookie
- get_available_sessions(): List all saved sessions

Directory structure created:
./sessions/
├── index.json                      # Quick lookup index
├── username1/                      # Account directory
│   └── settings.json               # Session data
├── username2/
│   └── settings.json
└── 123456789/                      # Fallback to user_id if needed
    └── settings.json
"""

from instagrapi import Client

# Example 1: Single account auto save/load
def example_single_account():
    print("=== Example 1: Single Account ===")

    # Login and auto save
    cl = Client(session_dir="./sessions")
    cl.login("username", "password")

    # Automatically save to ./sessions/username/settings.json
    saved_path = cl.auto_dump_settings()
    print(f"Session saved to: {saved_path}")

    # Next time, load directly
    cl2 = Client(session_dir="./sessions")
    cl2.restore_settings("username")  # Load by username
    print(f"Session restored for user: {cl2.username}")


# Example 2: Multiple accounts batch operation
def example_multiple_accounts():
    print("\n=== Example 2: Multiple Accounts ===")

    accounts = [
        ("user1", "pass1"),
        ("user2", "pass2"),
        ("user3", "pass3"),
    ]

    for username, password in accounts:
        cl = Client(session_dir="./sessions")
        cl.login(username, password)

        # Auto save with automatically generated filename
        path = cl.auto_dump_settings()
        print(f"Saved {username} to {path}")

        # Perform some operations...
        user_info = cl.user_info_by_username(username)
        print(f"  - {user_info.full_name} ({user_info.follower_count} followers)")


# Example 3: List and select accounts
def example_list_sessions():
    print("\n=== Example 3: List Available Sessions ===")

    # List all saved sessions
    sessions = Client.get_available_sessions("./sessions")

    print(f"Found {len(sessions)} saved sessions:")
    for i, session in enumerate(sessions):
        print(f"{i+1}. {session['username']} (ID: {session['user_id']})")
        print(f"   Saved at: {session['saved_at']}")
        print(f"   Path: {session['filepath']}")

    # Select and load one
    if sessions:
        cl = Client(session_dir="./sessions")
        cl.restore_settings(sessions[0]['username'])  # Load first account
        print(f"\nLoaded account: {cl.username}")


# Example 4: Load by different identifiers
def example_load_by_different_identifiers():
    print("\n=== Example 4: Load by Different Identifiers ===")

    cl = Client(session_dir="./sessions")

    # Method 1: Load by username
    cl.restore_settings("username")
    print(f"Loaded by username: {cl.username}")

    # Method 2: Load by user_id
    cl2 = Client(session_dir="./sessions")
    cl2.restore_settings(123456789)  # Use actual user_id
    print(f"Loaded by user_id: {cl2.username}")

    # Method 3: Load by cookie string
    cl3 = Client(session_dir="./sessions")
    cookie_str = "sessionid=123456789%3ATfy3bX..."  # From browser
    cl3.restore_settings(cookie_str)
    print(f"Loaded by cookie: {cl3.username}")


# Example 5: Backward compatibility
def example_backward_compatibility():
    print("\n=== Example 5: Backward Compatibility ===")

    cl = Client()

    # Old method still works
    cl.login("username", "password")
    cl.dump_settings("custom_name.json")  # Manual filename
    print("Saved with old method: custom_name.json")

    # New method also available
    path = cl.auto_dump_settings("./sessions")  # Auto filename
    print(f"Saved with new method: {path}")


# Example 6: Error handling
def example_error_handling():
    print("\n=== Example 6: Error Handling ===")

    cl = Client(session_dir="./sessions")

    try:
        # Try to load non-existent session
        cl.restore_settings("nonexistent_user")
    except FileNotFoundError as e:
        print(f"Expected error: {e}")

    try:
        # Try to save without login
        cl_new = Client(session_dir="./sessions")
        cl_new.auto_dump_settings()
    except ValueError as e:
        print(f"Expected error: {e}")


if __name__ == "__main__":
    # Uncomment the examples you want to run
    # Note: Replace with actual credentials for testing

    # example_single_account()
    # example_multiple_accounts()
    # example_list_sessions()
    # example_load_by_different_identifiers()
    # example_backward_compatibility()
    # example_error_handling()

    print("\nAll examples completed!")
    print("\nQuick start:")
    print("1. Login and save: cl.login(...); cl.auto_dump_settings()")
    print("2. Load session: cl.restore_settings('username')")
    print("3. List sessions: Client.get_available_sessions('./sessions')")
