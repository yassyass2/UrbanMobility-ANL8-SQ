import bcrypt
import os
import sqlite3
import sys
from src.models import Session
from src.models import User

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

DB_FILE = "src/data/urban_mobility.db"


class ServiceEngineerService():
    def __init__(self, session: Session):
        self.session: Session = session

    def user_overview(self):
        if (not self.session.is_valid() or self.session.role not in ["super_admin, system_admin"]):
            print("invalid session")
            return
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, password_hash, role, first_name, last_name, registration_date  FROM Users")
            all_users = cursor.fetchall()
        return all_users
