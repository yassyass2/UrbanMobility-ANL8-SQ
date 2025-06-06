import bcrypt
import os
import sqlite3
import sys
import hashlib

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

DB_FILE = "src/data/urban_mobility.db"


def authenticate_user(username, password) -> bool:
    username_hash = hashlib.sha256(username.encode()).hexdigest()
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password_hash, role, first_name, last_name, registration_date FROM users WHERE username_hash = ?", (username_hash,))
        row = cursor.fetchone()

    return row and bcrypt.checkpw(password.encode('utf-8'), row[2])


def get_role(username):
    username_hash = hashlib.sha256(username.encode()).hexdigest()
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM users WHERE username_hash = ?", (username_hash,))

        found = cursor.fetchone()

    return found[0] if found else None
