"""
Example: Using Persistent Sessions with the Interpals Library

This example demonstrates how to use session persistence to avoid logging in every time.
The session will be saved to a file and reused until it expires (default 24 hours).
"""

from interpal import InterpalClient


def example_persistent_session():
    """
    Example 1: Enable persistent sessions with auto-login.
    
    The first time you run this, it will:
    - Login with your credentials
    - Save the session to .interpals_session.json
    
    Subsequent runs (within 24 hours) will:
    - Load the saved session
    - Skip the login process
    - Use the existing session
    
    After 24 hours, it will automatically re-login and save a new session.
    """
    print("=== Example 1: Persistent Session with Auto-Login ===\n")
    
    client = InterpalClient(
        username="ayatolvl@gmail.com",
        password="sagar890",
        auto_login=True,
        persist_session=True  # Enable persistent sessions!
    )
    
    # Get profile
    profile = client.get_self()
    print(f"✓ Logged in as: {profile.name}")
    
    # Check session info
    session_info = client.get_session_info()
    if session_info:
        print(f"✓ Session expires at: {session_info['expires_at']}")
        print(f"✓ Time remaining: {session_info['time_remaining']}")
    
    client.close()
    print("\n✓ Done! Next time you run this, it will use the saved session.\n")


def example_custom_session_file():
    """
    Example 2: Use a custom session file location and expiration time.
    """
    print("=== Example 2: Custom Session File ===\n")
    
    client = InterpalClient(
        username="ayatolvl@gmail.com",
        password="sagar890",
        auto_login=True,
        persist_session=True,
        session_file="my_custom_session.json",  # Custom file path
        session_expiration_hours=48  # Expire after 48 hours instead of 24
    )
    
    profile = client.get_self()
    print(f"✓ Logged in as: {profile.name}")
    print(f"✓ Session saved to: my_custom_session.json")
    print(f"✓ Will expire in 48 hours")
    
    client.close()


def example_manual_session_control():
    """
    Example 3: Manual control over session persistence.
    """
    print("\n=== Example 3: Manual Session Control ===\n")
    
    # Initialize with persistent session
    client = InterpalClient(
        username="ayatolvl@gmail.com",
        password="sagar890",
        auto_login=True,
        persist_session=True
    )
    
    # Check session info
    session_info = client.get_session_info()
    if session_info:
        print(f"Username: {session_info['username']}")
        print(f"Created: {session_info['created_at']}")
        print(f"Expires: {session_info['expires_at']}")
        print(f"Time remaining: {session_info['time_remaining']}")
        print(f"Is expired: {session_info['is_expired']}")
    
    # Manually clear saved session if needed
    # client.clear_saved_session()
    # print("\n✓ Session cleared")
    
    client.close()


def example_multiple_accounts():
    """
    Example 4: Managing multiple accounts with different session files.
    """
    print("\n=== Example 4: Multiple Accounts ===\n")
    
    # Account 1
    client1 = InterpalClient(
        username="account1@example.com",
        password="password1",
        persist_session=True,
        session_file="account1_session.json"
    )
    # Use client1...
    
    # Account 2
    client2 = InterpalClient(
        username="account2@example.com",
        password="password2",
        persist_session=True,
        session_file="account2_session.json"
    )
    # Use client2...
    
    print("✓ Each account has its own session file")
    
    client1.close()
    client2.close()


def example_session_workflow():
    """
    Example 5: Complete workflow showing how sessions work over time.
    """
    print("\n=== Example 5: Session Workflow ===\n")
    
    # First run: Login and save session
    print("First run: Logging in...")
    client = InterpalClient(
        username="ayatolvl@gmail.com",
        password="sagar890",
        auto_login=True,
        persist_session=True,
        session_expiration_hours=24
    )
    
    print("✓ Session saved\n")
    client.close()
    
    # Subsequent runs: Reuse session
    print("Second run (within 24 hours): Reusing session...")
    client = InterpalClient(
        username="ayatolvl@gmail.com",
        password="sagar890",
        auto_login=True,  # Won't actually login if session is valid
        persist_session=True
    )
    
    profile = client.get_self()
    print(f"✓ Using saved session for: {profile.name}\n")
    client.close()
    
    # After 24 hours: Automatic re-login
    print("After 24 hours: Session expired...")
    print("✓ Will automatically re-login and save new session")


if __name__ == "__main__":
    # Run the first example
    example_persistent_session()
    
    # Uncomment to try other examples:
    # example_custom_session_file()
    # example_manual_session_control()
    # example_multiple_accounts()
    # example_session_workflow()
    
    print("\n" + "="*60)
    print("Key Features:")
    print("="*60)
    print("✓ Sessions are saved automatically when persist_session=True")
    print("✓ Sessions are reused for 24 hours (configurable)")
    print("✓ Expired sessions trigger automatic re-login")
    print("✓ Multiple accounts can have separate session files")
    print("✓ Session info can be checked anytime")
    print("✓ Sessions can be manually cleared if needed")
    print("="*60)

