# auth.py
# ------------------------
# Handles user authentication (registration and login)
# This module interacts with the database layer (database.py)
# to add new users and validate login credentials.

from database import add_user, get_user


def register_user():
    """
    Register a new user in the system.

    - Prompts for username and password.
    - Checks if the username already exists.
    - If not, adds the new user to the database.
    """
    print("\n📝 === REGISTER ===")

    # Prompt for user credentials
    username = input("Enter username: ").strip()
    password = input("Enter password: ").strip()

    # Validate input
    if not username or not password:
        print("❌ Username and password cannot be empty.")
        return None

    # Check if the username already exists in the database
    existing_user = get_user(username, password=None)
    if existing_user:
        print("❌ Username already exists. Try a different one.")
        return None

    # Register the new user
    add_user(username, password)
    print("✅ Registration successful!")
    return True


def login_user():
    """
    Log in an existing user.

    - Prompts for username and password.
    - Checks credentials against the database.
    - If valid, returns the user's ID for session tracking.
    """
    print("\n🔐 === LOGIN ===")

    # Prompt for user credentials
    username = input("Enter username: ").strip()
    password = input("Enter password: ").strip()

    # Retrieve user from database
    user = get_user(username, password)

    if user:
        print(f"✅ Welcome, {username}!")
        return user[0]  # Return user_id for use in dashboard
    else:
        print("❌ Wrong username or password.")
        return None