# main.py
# -----------------------------------
"""
Entry point for the Leitner Box CLI App.

Responsibilities:
- Initialize database tables (if not yet created)
- Provide main menu options: Register / Login / Exit
- Navigate user to the dashboard upon successful login
"""

import os
from auth import register_user, login_user
from dashboard import dashboard_menu
from database import create_tables


def clear_screen():
    """
    Clear the terminal screen.
    Works for both Windows (cls) and macOS/Linux (clear).
    """
    os.system("cls" if os.name == "nt" else "clear")


def main_menu():
    """
    Display the main menu and handle user navigation.

    Flow:
        1. Ensure the database and tables exist.
        2. Present menu options to the user.
        3. Route actions:
            - Register → create new account
            - Login → authenticate and open dashboard
            - Exit → terminate the program
    """
    # Ensure required tables exist before proceeding
    create_tables()

    while True:
        clear_screen()
        print("\n=== LEITNER BOX ===")
        print("1) Register")
        print("2) Login")
        print("3) Exit")

        # Get user input safely
        choice = input("\nEnter your choice: ").strip()

        if choice == "1":
            register_user()
        elif choice == "2":
            user_id = login_user()
            if user_id:
                dashboard_menu(user_id)
        elif choice == "3":
            print("👋 Goodbye! See you next time.")
            break
        else:
            print("❌ Invalid choice! Please enter a number between 1 and 3.")
            input("Press Enter to continue...")  # Pause before clearing screen


if __name__ == "__main__":
    main_menu()