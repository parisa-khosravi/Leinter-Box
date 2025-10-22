# dashboard.py
# -------------------------------
"""
Command-line dashboard for the Leitner Box app.

This module provides the main user interface after login.
Users can:
- View their Leitner box summary.
- Add new cards.
- Edit or delete existing cards.
- Review due cards.
"""

import os
from database import get_cards_by_slot, add_card, update_card, delete_card
from review import review_cards


# ==============================
#  Utility Functions
# ==============================
def clear_screen():
    """
    Clear the terminal screen for better readability.

    Works on both Windows (cls) and macOS/Linux (clear).
    """
    os.system("cls" if os.name == "nt" else "clear")


# ==============================
#  Dashboard Menu
# ==============================
def dashboard_menu(user_id):
    """
    Main dashboard loop displayed after user login.

    Args:
        user_id (int): The logged-in user's ID.

    Provides access to:
    - Viewing the Leitner box overview.
    - Adding, modifying, or reviewing cards.
    """
    while True:
        clear_screen()
        print("\n=== DASHBOARD ===")
        print("1) Show Box")
        print("2) Add Card")
        print("3) Modify Card")
        print("4) Review Cards")
        print("5) Logout")

        choice = input("\nEnter your choice: ").strip()

        if choice == "1":
            show_box(user_id)
        elif choice == "2":
            add_card_menu(user_id)
        elif choice == "3":
            modify_card_menu(user_id)
        elif choice == "4":
            review_cards(user_id)
        elif choice == "5":
            break
        else:
            print("Invalid choice!")
            input("Press Enter to continue...")


# ==============================
#  Box Overview
# ==============================
def show_box(user_id):
    """
    Display the number of cards in each Leitner slot for the user.

    Args:
        user_id (int): The ID of the logged-in user.
    """
    clear_screen()
    print("\n=== YOUR LEITNER BOX ===")
    for slot in range(1, 7):
        cards = get_cards_by_slot(user_id, slot) or []
        print(f"Slot {slot} → {len(cards)} Cards")
    input("\nPress Enter to return to dashboard...")


# ==============================
#  Add Card
# ==============================
def add_card_menu(user_id):
    """
    Add a new flashcard to the Leitner box (starts in slot 1).

    Args:
        user_id (int): The ID of the user adding the card.
    """
    clear_screen()
    print("\n=== ADD CARD ===")

    # Prompt for user input
    question = input("Enter question: ").strip()
    answer = input("Enter answer: ").strip()

    if not question or not answer:
        print("❌ Question and answer cannot be empty.")
    else:
        try:
            add_card(user_id, question, answer)
            print("✅ Card added successfully!")
        except Exception as e:
            print(f"❌ Failed to add card: {e}")
    input("\nPress Enter to return...")


# ==============================
#  Modify or Delete Card
# ==============================
def modify_card_menu(user_id):
    """
    Allow the user to edit or delete a card from a chosen slot.

    Args:
        user_id (int): The ID of the logged-in user.
    """
    clear_screen()
    print("\n=== MODIFY CARD ===")

    # Select slot
    try:
        slot = int(input("Enter slot number (1–6): ").strip())
        if slot < 1 or slot > 6:
            print("Invalid slot number.")
            input("Press Enter to return...")
            return
    except ValueError:
        print("Invalid input.")
        input("Press Enter to return...")
        return

    # Fetch cards in that slot
    cards = get_cards_by_slot(user_id, slot) or []
    if not cards:
        print("No cards found in this slot.")
        input("Press Enter to return...")
        return

    # Show all cards
    print(f"\n=== SLOT {slot} CARDS ===")
    for card_id, question, answer in cards:
        print(f"ID: {card_id} | Q: {question} | A: {answer}")

    # Choose which card to modify
    try:
        card_id = int(input("\nEnter card ID to modify: ").strip())
    except ValueError:
        print("Invalid ID.")
        input("Press Enter to return...")
        return

    # Validate card ID exists
    if card_id not in [card[0] for card in cards]:
        print("Card ID not found.")
        input("Press Enter to return...")
        return

    # Choose edit or delete
    action = input("Enter 'e' to edit or 'd' to delete (e/d): ").strip().lower()
    if action == "d":
        try:
            delete_card(card_id)
            print("✅ Card deleted successfully!")
        except Exception as e:
            print(f"❌ Failed to delete card: {e}")

    elif action == "e":
        new_q = input("Enter new question (leave blank to keep current): ").strip()
        new_a = input("Enter new answer (leave blank to keep current): ").strip()

        # Keep current values if user leaves input blank
        existing = next((c for c in cards if c[0] == card_id), None)
        final_q = new_q if new_q else existing[1]
        final_a = new_a if new_a else existing[2]

        try:
            update_card(card_id, final_q, final_a)
            print("✅ Card updated successfully!")
        except Exception as e:
            print(f"❌ Failed to update card: {e}")
    else:
        print("Unknown action.")
    input("\nPress Enter to return...")