import bcrypt
import os
import sqlite3
from models.Session import Session
from models.User import User
from services.ServiceEngineerService import ServiceEngineerService
from cryptography.fernet import Fernet

DB_FILE = "src/data/urban_mobility.db"


class SystemAdminService(ServiceEngineerService):
    def __init__(self, session: Session):
        super().__init__(session)

    def user_overview(self) -> list[User]:
        if (not self.session.is_valid() or self.session.role not in ["super_admin", "system_admin"]):
            return None

        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, username, role, first_name, last_name, registration_date  FROM Users")
            rows = cursor.fetchall()

        cipher = Fernet(os.getenv("FERNET_KEY").encode())

        users = [User(id=row[0], username=cipher.decrypt(row[1].encode('utf-8')).decode('utf-8'), password_hash=None,
                 role=row[2], first_name=row[3], last_name=row[4],
                 reg_date=row[5]) for row in rows]

        return users
