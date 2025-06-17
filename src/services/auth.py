import bcrypt
import os
import sqlite3
import sys
import hashlib
from logger import *

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

DB_FILE = "src/data/urban_mobility.db"


def authenticate_user(username, password) -> bool:
    username_hash = hashlib.sha256(username.encode()).hexdigest()
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password_hash, role, first_name, last_name, registration_date FROM users WHERE username_hash = ?", (username_hash,))
        row = cursor.fetchone()

    if not row:
        log_to_db({"username": username, "activity": f"Unsuccesful login as {username}", "additional_info": "Username doesn't exist.", "suspicious": 1})
    elif not bcrypt.checkpw(password.encode('utf-8'), row[2]):
        log_to_db({"username": username, "activity": f"Unsuccesful login as {username}", "additional_info": "Password was wrong.", "suspicious": 1})
    else:
        log_to_db({"username": username, "activity": f"Succesful login as {username}", "additional_info": "Succesfully logged in.", "suspicious": 0})

    return row and bcrypt.checkpw(password.encode('utf-8'), row[2])


def get_role(username):
    username_hash = hashlib.sha256(username.encode()).hexdigest()
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM users WHERE username_hash = ?", (username_hash,))

        found = cursor.fetchone()

    return found[0] if found else None


def get_role_id(id):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM users WHERE id = ?", (id,))

        found = cursor.fetchone()

    return found[0] if found else None