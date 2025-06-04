import bcrypt
import os
import sqlite3
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

DB_FILE = "src/data/urban_mobility.db"


def authenticate_user(username, password) -> bool:
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password_hash, role, first_name, last_name, registration_date FROM Users WHERE username = ?", (username,))
        row = cursor.fetchone()

    return row and bcrypt.checkpw(password.encode('utf-8'), row[2])


def get_role(username):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM Users WHERE username = ?", (username,))
        return cursor.fetchone()[0]
