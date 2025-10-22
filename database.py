# database.py
# -------------------------------
# Handles all PostgreSQL operations for the Leitner Box app.
# Includes: connection management, user management, card management,
# and review scheduling logic.

import psycopg2
from functools import wraps
import bcrypt


# ==============================
#  Database Connection
# ==============================
def get_connection():
    """
    Establish a connection to the PostgreSQL database.

    Returns:
        psycopg2.connection: Active connection object.
    """
    return psycopg2.connect(
        dbname="leitner_db",
        user="postgres",
        password="1234",
        host="localhost",
        port="5432"
    )


# ==============================
#  Connection Decorator
# ==============================
def db_connection(func):
    """
    Decorator to automatically handle database connection, commit,
    and cleanup for each function call.

    Ensures that:
    - The connection opens and closes safely.
    - Transactions are automatically committed.
    - Errors are caught and printed.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        conn = get_connection()
        try:
            with conn:
                with conn.cursor() as cursor:
                    return func(cursor, *args, **kwargs)
        except Exception as e:
            print(f"DATABASE ERROR: {e}")
        finally:
            conn.close()
    return wrapper


# ==============================
#  Table Creation
# ==============================
@db_connection
def create_tables(cursor):
    """
    Create the required tables: 'users' and 'cards' if they do not exist.
    """
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            password TEXT NOT NULL
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cards (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            slot INTEGER DEFAULT 1,
            last_review DATE DEFAULT CURRENT_DATE
        );
    """)


# ==============================
#  User Management
# ==============================
@db_connection
def add_user(cursor, username, password):
    """
    Add a new user with a securely hashed password.

    Args:
        username (str): The chosen username.
        password (str): The user's plaintext password (to be hashed).
    """
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    cursor.execute(
        "INSERT INTO users (username, password) VALUES (%s, %s)",
        (username, hashed_pw.decode())
    )


@db_connection
def get_user(cursor, username, password=None):
    """
    Retrieve user information for login or registration validation.

    Args:
        username (str): The username to look up.
        password (str, optional): Plaintext password for login authentication.

    Returns:
        tuple or None: User record if found (and password matches), else None.
    """
    if password is None:
        cursor.execute("SELECT id, username FROM users WHERE username=%s", (username,))
    else:
        cursor.execute("SELECT id, username, password FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()
        if user and bcrypt.checkpw(password.encode(), user[2].encode()):
            return user
        return None
    return cursor.fetchone()


# ==============================
#  Card Management
# ==============================
@db_connection
def add_card(cursor, user_id, question, answer, slot=1):
    """
    Insert a new flashcard into the database.

    Args:
        user_id (int): The ID of the user who owns the card.
        question (str): The question text.
        answer (str): The answer text.
        slot (int): Leitner box slot (default is 1).
    """
    cursor.execute(
        "INSERT INTO cards (user_id, question, answer, slot) VALUES (%s, %s, %s, %s)",
        (user_id, question, answer, slot)
    )


@db_connection
def get_cards_by_slot(cursor, user_id, slot):
    """
    Retrieve all cards for a specific user and Leitner slot.

    Args:
        user_id (int): The user's ID.
        slot (int): The slot number (1–6).

    Returns:
        list[tuple]: List of (id, question, answer) tuples.
    """
    cursor.execute(
        "SELECT id, question, answer FROM cards WHERE user_id=%s AND slot=%s",
        (user_id, slot)
    )
    return cursor.fetchall()


@db_connection
def update_card(cursor, card_id, question, answer):
    """
    Update the question and answer fields of an existing card.

    Args:
        card_id (int): The card's unique ID.
        question (str): Updated question text.
        answer (str): Updated answer text.
    """
    cursor.execute(
        "UPDATE cards SET question=%s, answer=%s WHERE id=%s",
        (question, answer, card_id)
    )


@db_connection
def delete_card(cursor, card_id):
    """
    Delete a flashcard from the database.

    Args:
        card_id (int): The unique ID of the card to delete.
    """
    cursor.execute("DELETE FROM cards WHERE id=%s", (card_id,))


@db_connection
def update_card_slot(cursor, card_id, new_slot):
    """
    Move a card to a different Leitner slot.

    Args:
        card_id (int): The ID of the card.
        new_slot (int): The updated slot number.
    """
    cursor.execute(
        "UPDATE cards SET slot=%s WHERE id=%s",
        (new_slot, card_id)
    )


# ==============================
#  Review System
# ==============================
@db_connection
def get_due_cards(cursor, user_id):
    """
    Retrieve all cards that are due for review (last_review <= today).

    Args:
        user_id (int): The user's ID.

    Returns:
        list[tuple]: Cards that should be reviewed today.
    """
    cursor.execute("""
        SELECT id, question, answer, slot, last_review
        FROM cards
        WHERE user_id = %s
        AND last_review <= CURRENT_DATE
        ORDER BY slot;
    """, (user_id,))
    return cursor.fetchall()


@db_connection
def update_review_date(cursor, card_id, next_date):
    """
    Update the review date after a successful or failed review.

    Args:
        card_id (int): The card's ID.
        next_date (date): The next scheduled review date.
    """
    cursor.execute(
        "UPDATE cards SET last_review = %s WHERE id = %s;",
        (next_date, card_id)
    )