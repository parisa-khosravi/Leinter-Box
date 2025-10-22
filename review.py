# review.py
# -----------------
# Handles Leitner review system logic:
# - Fetch cards that are due for review
# - Ask user for answers
# - Update card slot and next review date
# - Penalize cards that are reviewed more than 2 days late

from database import get_due_cards, update_card_slot, update_review_date
from datetime import date, timedelta


def review_cards(user_id):
    """Main Leitner review loop for the given user."""
    cards = get_due_cards(user_id)
    if not cards:
        print("\n📭 No cards to review today!")
        return

    # Define review intervals for each slot (in days)
    intervals = {
        1: 1,
        2: 3,
        3: 7,
        4: 14,
        5: 30,
        6: 60
    }

    print(f"\n🧠 {len(cards)} card(s) due for review today!\n")

    for card_id, question, answer, slot, last_review in cards:
        # --- Check for overdue penalty ---
        overdue_days = (date.today() - last_review).days
        grace_period = 2  # allowed days past the due date before penalty

        # If more than 2 days late, demote one slot (minimum slot = 1)
        if overdue_days > intervals.get(slot, 1) + grace_period:
            if slot > 1:
                new_slot = slot - 1
                update_card_slot(card_id, new_slot)
                print(f"⚠️ Card was overdue ({overdue_days} days). Moved back to slot {new_slot}.")
                slot = new_slot  # update local slot value

        # --- Ask the user the question ---
        print(f"\nQ: {question}")
        user_answer = input("Your answer: ").strip()

        # --- Evaluate the answer ---
        if user_answer.lower() == answer.lower():
            print("✅ Correct!")
            new_slot = min(slot + 1, 6)  # max slot = 6 (learned)
        else:
            print(f"❌ Wrong! Correct answer: {answer}")
            new_slot = 1  # restart from slot 1

        # --- Schedule the next review date ---
        next_date = date.today() + timedelta(days=intervals[new_slot])
        update_card_slot(card_id, new_slot)
        update_review_date(card_id, next_date)

        print(f"🗓️ Card moved to slot {new_slot}. Next review on {next_date}.\n")

    print("🎉 Review session complete!")