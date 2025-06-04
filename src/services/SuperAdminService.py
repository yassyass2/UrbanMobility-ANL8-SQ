import bcrypt
import os
import sqlite3
import sys
from src.models.Session import Session
from src.models.User import User

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

DB_FILE = "src/data/urban_mobility.db"


class ServiceEngineerService():
    def __init__(self, session: Session):
        self.session: Session = session

    def user_overview(self) -> list[User]:
        if (not self.session.is_valid() or self.session.role not in ["super_admin, system_admin"]):
            print("invalid session")
            return
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, username, role, first_name, last_name, registration_date  FROM Users")
            rows = cursor.fetchall()

        users = [User(id=row[0], username=row[1], password_hash=None,
                 role=row[2], first_name=row[3], last_name=row[4],
                 registration_date=row[5]) for row in rows]
        return users
