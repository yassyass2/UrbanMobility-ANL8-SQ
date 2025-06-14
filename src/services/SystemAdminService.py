import bcrypt
import os
import sqlite3
from models.Session import Session
from models.User import User
from services.ServiceEngineerService import ServiceEngineerService
from services import auth
import string, random
import zipfile

from cryptography.fernet import Fernet
import hashlib
from datetime import date, datetime

DB_FILE = "src/data/urban_mobility.db"
BACKUP_DIR = "system_backups"


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

        users = [User(id=row[0], username=cipher.decrypt(row[1]).decode('utf-8'), password_hash=None,
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
    
    def update_user(self, id: int, to_update: dict):
        if not self.session.is_valid() or self.session.role not in ["super_admin", "system_admin"]:
            return "Fail, Session expired" if not self.session.is_valid() else "Must be atleast system admin to perform this action."
        if not to_update:
            return "No fields provided to update."
        
        if "password_hash" in to_update.keys():
            to_update["password_hash"] = bcrypt.hashpw(to_update["password_hash"].encode('utf-8'), bcrypt.gensalt())
        if "username" in to_update.keys():
            cipher = Fernet(os.getenv("FERNET_KEY").encode())
            plain_uname = to_update["username"]

            to_update["username_hash"] = hashlib.sha256(plain_uname.encode()).hexdigest()
            to_update["username"] = cipher.encrypt(to_update["username"].encode('utf-8')).decode('utf-8')

        fields_query = ", ".join(f"{field} = ?" for field in to_update)
        new_values = list(to_update.values())

        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()

                query = f"UPDATE users SET {fields_query} WHERE id = ?"
                cursor.execute(query, new_values + [id])
                conn.commit()

                if cursor.rowcount == 0:
                    return "No user found with the given ID."

                return "User updated successfully."

        except sqlite3.Error as e:
            return f"Database error: {e}"

    def generate_temp_password(self, length=16):
        if length < 12 or length > 30:
            raise ValueError("Password length must be between 12 and 30")

        upper = random.choice(string.ascii_uppercase)
        lower = random.choice(string.ascii_lowercase)
        digit = random.choice(string.digits)
        symbol = random.choice("~!@#$%&_-+=`|\\(){}[]:;'<>,.?/")
        remaining = random.choices(string.ascii_letters + string.digits + "~!@#$%&_-+=`|\\(){}[]:;'<>,.?/", k=length - 4)

        # Shuffle
        password_list = list(upper + lower + digit + symbol + ''.join(remaining))
        random.shuffle(password_list)
        return ''.join(password_list)

    def reset_password(self, id, allowed_roles, temp_password):
        if not self.session.is_valid() or self.session.role not in ["super_admin", "system_admin"]:
            return "Fail, Session expired" if not self.session.is_valid() else "Must be atleast system admin to perform this action."
        if auth.get_role_id(id) not in allowed_roles:
            return f"You can't reset the password of a user with role {auth.get_role_id(id)}"

        password_hash = bcrypt.hashpw(temp_password.encode(), bcrypt.gensalt())

        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users 
                SET password_hash = ?, must_change_password = 1
                WHERE id = ?
            """, (password_hash, id))
            conn.commit()

        return f"Temporary password for user {id} succesfully set"

    def create_backup(self) -> tuple[bool, str]:
        if not self.session.is_valid() or self.session.role not in ["super_admin", "system_admin"]:
            return "Fail, Session expired" if not self.session.is_valid() else "Must be atleast system admin to perform this action."
        
        if not os.path.exists(DB_FILE):
            return (False, f"Database file '{DB_FILE}' does not exist.")

        os.makedirs(BACKUP_DIR, exist_ok=True)

        backup_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"backup_{backup_timestamp}.zip"
        backup_path = os.path.join(BACKUP_DIR, backup_filename)

        try:
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(DB_FILE, arcname=os.path.basename(DB_FILE))
            return (True, f"Backup created at: {backup_path}")
        except Exception as e:
            return (False, f"Backup failed: {e}")

    def restore_backup_with_code(self) -> bool:
        print("Restore backup functionality is not implemented yet.")
    
    def add_traveller(self, traveller_data: dict) -> bool:
        print("Add traveller functionality is not implemented yet.")

    def update_traveller(self, traveller_id: int, updated_data: dict) -> bool:
        print("Update traveller functionality is not implemented yet.")

    def delete_traveller(self, traveller_id: int) -> bool:
        print("Delete traveller functionality is not implemented yet.")
        return False
    
    def view_travellers_by_id(self, traveller_id):
        if not self.session.is_valid():
            print("Session Expired")
            return

        conn = sqlite3.connect('src/data/urban_mobility.db')
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM travellers WHERE id LIKE ?", (f"%{traveller_id}%",))   
            travellers = cursor.fetchall()
            if travellers:
                print("Travellers found:")
                for traveller in travellers:
                    print(traveller)
            else:
                print(f"No travellers found containing ID: {traveller_id}")
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
            conn.close()

    def view_travellers_by_last_name(self, traveller_last_name):
        if not self.session.is_valid():
            print("Session Expired")
            return

        conn = sqlite3.connect('src/data/urban_mobility.db')
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM travellers WHERE last_name LIKE ?", (f"%{traveller_last_name}%",))   
            travellers = cursor.fetchall()
            if travellers:
                print("Travellers found:")
                for traveller in travellers:
                    print(traveller)
            else:
                print(f"No travellers found containing Last Name: {traveller_last_name}")
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
            conn.close()