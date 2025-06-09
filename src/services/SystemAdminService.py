import bcrypt
import os
import sqlite3
from models.Session import Session
from models.User import User
from services.ServiceEngineerService import ServiceEngineerService
from services import auth

from cryptography.fernet import Fernet
import hashlib
from datetime import date

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
    
    def add_user(self, allowed_roles: list, required_fields: dict) -> bool:
        if required_fields["role"] not in allowed_roles or not self.session.is_valid() or self.session.role not in ["super_admin", "system_admin"]:
            return False

        cipher = Fernet(os.getenv("FERNET_KEY").encode())

        hash_pw = bcrypt.hashpw(required_fields["password"].encode('utf-8'), bcrypt.gensalt())
        encrypted_username = cipher.encrypt(required_fields["username"].encode('utf-8'))

        reg_date = date.today().strftime('%Y-%m-%d')
        username_hash = hashlib.sha256(required_fields["username"].encode()).hexdigest()

        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
            INSERT INTO users (
                username,
                password_hash,
                role,
                first_name,
                last_name,
                registration_date,
                username_hash
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (encrypted_username.decode('utf-8'), hash_pw, required_fields["role"],
                  required_fields["first_name"], required_fields["last_name"], reg_date, username_hash))
            
            conn.commit()
            print("New user ID:", cursor.lastrowid)
        return True

    def delete_user(self, allowed_roles: list, delete_id: int) -> str:
        if not self.session.is_valid() or self.session.role not in ["super_admin", "system_admin"]:
            return "Fail, Session expired" if not self.session.is_valid() else "Must be atleast system admin to perform this action."

        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username FROM users WHERE id = ?", (delete_id,))
            id_and_username = cursor.fetchone()

            if id_and_username is None:
                return "Delete failed, User doesn't exist"

            role = auth.get_role_id(delete_id)
            if role not in allowed_roles:
                return f"Delete failed, you don't have permission to delete {role}s"
            
            cursor.execute("DELETE FROM users WHERE id = ?", (delete_id,))
            conn.commit()

        cipher = Fernet(os.getenv("FERNET_KEY").encode())
        decrypted_username = cipher.decrypt(id_and_username[1].encode('utf-8')).decode('utf-8')
        return f"Succesfully deleted user with ID {delete_id} and Username {decrypted_username}"

    def change_password():
        print("Change password functionality is not implemented yet.")
        
    def delete_account(self) -> bool:
        print("Delete account functionality is not implemented yet.")

    def create_backup(self) -> bool:
        print("Create backup functionality is not implemented yet.")

    def restore_backup(self) -> bool:
        print("Restore backup functionality is not implemented yet.")

    def view_backups(self) -> list:
        print("View backups functionality is not implemented yet.")
        return []
    
    def add_traveler(self, traveller_data: dict) -> bool:
        print("Add traveller functionality is not implemented yet.")

    def update_traveler(self, traveler_id: int, updated_data: dict) -> bool:
        print("Update traveller functionality is not implemented yet.")

    def delete_traveler(self, traveler_id: int) -> bool:
        print("Delete traveller functionality is not implemented yet.")
        return False
    
    def view_travelers(self) -> list:
        print("View travellers functionality is not implemented yet.")
        return []
    