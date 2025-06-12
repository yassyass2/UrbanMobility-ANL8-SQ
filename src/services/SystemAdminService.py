import bcrypt
import os
import sqlite3
from models.Session import Session
from models.User import User
from services.ServiceEngineerService import ServiceEngineerService
from services import auth
import string, random
from services.validation import (
    is_valid_name, is_valid_birthday, is_valid_gender, is_valid_street,
    is_valid_house_number, is_valid_zip, is_valid_city, is_valid_email_and_domain,
    is_valid_mobile, is_valid_license
)
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

    def create_backup(self) -> bool:
        print("Create backup functionality is not implemented yet.")

    def restore_backup(self) -> bool:
        print("Restore backup functionality is not implemented yet.")

    def view_backups(self) -> list:
        print("View backups functionality is not implemented yet.")
        return []
    
    def traveller_overview(self) -> list[dict]:
        if not self.session.is_valid() or self.session.role not in ["super_admin", "system_admin"]:
            return []

        cipher = Fernet(os.getenv("FERNET_KEY").encode())
        overview = []

        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, first_name, last_name, registration_date FROM travellers")
            rows = cursor.fetchall()

            for row in rows:
                traveller_id = row[0]
                first_name = row[1]
                last_name = row[2]
                reg_date = row[3]
                overview.append({
                    "id": traveller_id,
                    "name": f"{first_name} {last_name}",
                    "registration_date": reg_date
                })

        return overview
    
    def get_traveller_by_id(self, traveller_id: int) -> dict | None:
        try:
            cipher = Fernet(os.getenv("FERNET_KEY").encode())

            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM travellers WHERE id = ?", (traveller_id,))
                row = cursor.fetchone()

                if not row:
                    return None

                fields = [
                    "id", "first_name", "last_name", "birthday", "gender",
                    "street", "house_number", "zip_code", "city", "email",
                    "mobile", "license_number", "registration_date"
                ]

                decrypted = dict(zip(fields, row))
                for key in ["street", "zip_code", "city", "email", "mobile", "license_number"]:
                    if decrypted[key]:
                        decrypted[key] = cipher.decrypt(decrypted[key].encode()).decode()

                return decrypted
        except Exception as e:
            print(f"[ERROR] Failed to load traveller: {e}")
            return None
    
    def add_traveller(self, traveller_data: dict) -> str:
        if not self.session.is_valid() or self.session.role not in ["super_admin", "system_admin"]:
            return "Unauthorized or session expired."

        try:
            birthday_db_format = traveller_data["birthday"]

            cipher = Fernet(os.getenv("FERNET_KEY").encode())
            registration_date = date.today().strftime('%Y-%m-%d')

            encrypted_fields = {
                "street": cipher.encrypt(traveller_data["street"].encode()).decode('utf-8'),
                "zip_code": cipher.encrypt(traveller_data["zip_code"].encode()).decode('utf-8'),
                "city": cipher.encrypt(traveller_data["city"].encode()).decode('utf-8'),
                "email": cipher.encrypt(traveller_data["email"].encode()).decode('utf-8'),
                "mobile": cipher.encrypt(traveller_data["mobile"].encode()).decode('utf-8'),
                "license_number": cipher.encrypt(traveller_data["license_number"].encode()).decode('utf-8'),
            }

            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO travellers (
                        first_name, last_name, birthday, gender,
                        street, house_number, zip_code, city,
                        email, mobile, license_number, registration_date
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    traveller_data["first_name"],
                    traveller_data["last_name"],
                    birthday_db_format,
                    traveller_data["gender"],
                    encrypted_fields["street"],
                    traveller_data["house_number"],
                    encrypted_fields["zip_code"],
                    encrypted_fields["city"],
                    encrypted_fields["email"],
                    encrypted_fields["mobile"],
                    encrypted_fields["license_number"],
                    registration_date
                ))

                conn.commit()
                return f"Traveller added with ID: {cursor.lastrowid}"

        except Exception as e:
            return f"[ERROR] Failed to add traveller: {e}"

    def update_traveller(self, traveller_id: int, updated_data: dict) -> str:
        if not self.session.is_valid() or self.session.role not in ["super_admin", "system_admin"]:
            return "Unauthorized or session expired."

        if not updated_data:
            return "No fields provided to update."



        cities = ["Rotterdam", "Delft", "Schiedam", "The Hague", "Leiden",
                "Gouda", "Zoetermeer", "Spijkenisse", "Vlaardingen", "Barendrecht"]
        
        validators = {
            "first_name": is_valid_name,
            "last_name": is_valid_name,
            "birthday": is_valid_birthday,
            "gender": is_valid_gender,
            "street": is_valid_street,
            "house_number": is_valid_house_number,
            "zip_code": is_valid_zip,
            "city": lambda val: is_valid_city(val, cities),
            "email": is_valid_email_and_domain,
            "mobile": is_valid_mobile,
            "license_number": is_valid_license,
        }

        sensitive_fields = {"street", "zip_code", "city", "email", "mobile", "license_number"}

        cipher = Fernet(os.getenv("FERNET_KEY").encode())
        final_updates = {}

        for key, value in updated_data.items():
            validator = validators.get(key)
            if validator and validator(value):
                if key == "house_number":
                    final_updates[key] = int(value)
                elif key in sensitive_fields:
                    final_updates[key] = cipher.encrypt(value.encode()).decode('utf-8')
                else:
                    final_updates[key] = value
            else:
                continue

        if not final_updates:
            return "No valid fields provided to update."

        try:
            fields_query = ", ".join(f"{field} = ?" for field in final_updates)
            values = list(final_updates.values())

            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                query = f"UPDATE travellers SET {fields_query} WHERE id = ?"
                cursor.execute(query, values + [traveller_id])
                conn.commit()

                if cursor.rowcount == 0:
                    return f"No traveller found with ID {traveller_id}."
                return f"Traveller {traveller_id} successfully updated."

        except Exception as e:
            return f"[ERROR] Failed to update traveller: {e}"



    def delete_traveller(self, traveller_id: int) -> str:
        if not self.session.is_valid() or self.session.role not in ["super_admin", "system_admin"]:
            return "Unauthorized or session expired."

        try:
            cipher = Fernet(os.getenv("FERNET_KEY").encode())

            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT first_name, last_name FROM travellers WHERE id = ?", (traveller_id,))
                row = cursor.fetchone()

                if not row:
                    return "Traveller not found."

                full_name = f"{row[0]} {row[1]}"
                cursor.execute("DELETE FROM travellers WHERE id = ?", (traveller_id,))
                conn.commit()

            return f"Traveller {full_name} with ID {traveller_id} successfully deleted."

        except Exception as e:
            return f"[ERROR] Failed to delete traveller: {e}"

    
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