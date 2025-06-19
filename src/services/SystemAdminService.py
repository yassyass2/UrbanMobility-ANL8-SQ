import bcrypt
import sys
import os
import sqlite3
import time
import string, random
import zipfile
import hashlib
import shutil

from models.Session import Session
from models.User import User
from services.ServiceEngineerService import ServiceEngineerService
from services import auth
from cryptography.fernet import Fernet
from datetime import date, datetime
from ui.menu_utils import *
from services.validation import *
from logger import log_to_db
from ui.prompts.user_prompts import *

from cryptography.fernet import Fernet
from datetime import date, datetime

DB_FILE = "data/urban_mobility.db"
BACKUP_DIR = "system_backups"
TEMP_EXTRACT_PATH = "temp_restore" 


class SystemAdminService(ServiceEngineerService):
    def __init__(self, session: Session):
        super().__init__(session)

    def user_overview(self) -> list[User]:
        if (not self.session.is_valid() or self.session.role not in ["super_admin", "system_admin"]):
            log_to_db({"username": self.session.user, "activity": "Unauthorized attempt to view users", "additional_info": f"{self.session.user} is not an admin.", "suspicious": 1})
            return None

        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, username, role, first_name, last_name, registration_date  FROM Users")
            rows = cursor.fetchall()

        cipher = Fernet(os.getenv("FERNET_KEY").encode())

        log_to_db({"username": self.session.user, "activity": "Fetched the overview of users", "additional_info": f"{self.session.user} is an admin.", "suspicious": 0})

        users = [User(id=row[0], username=cipher.decrypt(row[1]).decode('utf-8'), password_hash=None,
                 role=row[2], first_name=row[3], last_name=row[4],
                 reg_date=row[5]) for row in rows]

        return users
    
    def add_user(self, allowed_roles: list, required_fields: dict) -> bool:
        if required_fields["role"] not in allowed_roles or not self.session.is_valid() or self.session.role not in ["super_admin", "system_admin"]:
            log_to_db({"username": self.session.user, "activity": "Unauthorized attempt to add user", "additional_info": f"not allowed to add user of role {required_fields['role']}", "suspicious": 1})
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
            log_to_db({"username": self.session.user, "activity": "Added a user", "additional_info": "", "suspicious": 0})
            print("New user ID:", cursor.lastrowid)
        return True

    def delete_user(self, allowed_roles: list, delete_id: int) -> str:
        if not self.session.is_valid() or self.session.role not in ["super_admin", "system_admin"]:
            log_to_db({"username": self.session.user, "activity": "Unauthorized attempt to delete user", "additional_info": f"{self.session.user} is not an admin.", "suspicious": 1})
            return "Fail, Session expired" if not self.session.is_valid() else "Must be atleast system admin to perform this action."

        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username FROM users WHERE id = ?", (delete_id,))
            id_and_username = cursor.fetchone()

            if id_and_username is None:
                log_to_db({"username": self.session.user, "activity": "Failed attempt to delete user", "additional_info": "user doesn't exist", "suspicious": 0})
                return "Delete failed, User doesn't exist"

            role = auth.get_role_id(delete_id)
            if role not in allowed_roles:
                log_to_db({"username": self.session.user, "activity": "Unauthorized attempt to delete user", "additional_info": f"No permission for Role of user to delete", "suspicious": 1})
                return f"Delete failed, you don't have permission to delete {role}s"
            
            cursor.execute("DELETE FROM users WHERE id = ?", (delete_id,))
            conn.commit()

        cipher = Fernet(os.getenv("FERNET_KEY").encode())
        decrypted_username = cipher.decrypt(id_and_username[1].encode('utf-8')).decode('utf-8')
        log_to_db({"username": self.session.user, "activity": f"Deleted a user with ID {delete_id}", "additional_info": "", "suspicious": 0})
        return f"Succesfully deleted user with ID {delete_id} and Username {decrypted_username}"
    
    def update_user(self, id: int, to_update: dict):
        role_list = ["super_admin", "system_admin"]
        role = auth.get_role_id(id)

        if (role == "super_admin" or not self.session.is_valid() or self.session.role not in role_list
        or self.session.role == "system_admin" and role in role_list):
            log_to_db({"username": self.session.user, "activity": "Unauthorized attempt to update user", "additional_info": f"Updating role {role} not allowed", "suspicious": 1})
            return "Fail, Session expired" if not self.session.is_valid() else f"Insufficient permissions to update user of role {role}"
        
        if not to_update:
            log_to_db({"username": self.session.user, "activity": "Failed attempt to update user", "additional_info": f"No fields provided", "suspicious": 0})
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
                    log_to_db({"username": self.session.user, "activity": "Failed attempt to update user", "additional_info": f"no user found with id {id}", "suspicious": 0})
                    return "No user found with the given ID."

                log_to_db({"username": self.session.user, "activity": f"Updated user with id {id}", "additional_info": f"", "suspicious": 0})
                return "User updated successfully."

        except sqlite3.Error as e:
            return f"Database error: {e}"
        
    def update_own_account(self):

        if not self.session.is_valid() or self.session.role != "system_admin":
            log_to_db({"username": self.session.user, "activity": "Unauthorized attempt to update own account", "additional_info": "Not a System admin", "suspicious": 1})
            return "Fail, Session expired" if not self.session.is_valid() else f"Only system admins can update own account"
        
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username_hash = ?", (hashlib.sha256(self.session.user.encode()).hexdigest(),))
            own_id = cursor.fetchone()[0]

        to_update = prompt_update_self(own_id)
        if not to_update:
            log_to_db({"username": self.session.user, "activity": "Failed attempt to update own account", "additional_info": "No fields provided", "suspicious": 0})
            return "No fields provided to update."

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
                cursor.execute(query, new_values + [own_id])
                conn.commit()

                log_to_db({"username": self.session.user, "activity": f"Updated their own account", "additional_info": f"Success", "suspicious": 0})
                return "Own account updated successfully."

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
            log_to_db({"username": self.session.user, "activity": "Unauthorized attempt to reset user password", "additional_info": f"{self.session.user} is not an admin.", "suspicious": 1})
            return "Fail, Session expired" if not self.session.is_valid() else "Must be atleast system admin to perform this action."
        if auth.get_role_id(id) not in allowed_roles:
            log_to_db({"username": self.session.user, "activity": "Unauthorized attempt to update user", "additional_info": f"{self.session.user} can't update {auth.get_role_id(id)} roles", "suspicious": 1})
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

        log_to_db({"username": self.session.user, "activity": f"Reset password for user {id}", "additional_info": f"Temporary password set", "suspicious": 0})
        return f"Temporary password for user {id} succesfully set"

    def create_backup(self) -> tuple[bool, str]:
        if not self.session.is_valid() or self.session.role not in ["super_admin", "system_admin"]:
            log_to_db({"username": self.session.user, "activity": "Tried to create a backup", "additional_info": f"{self.session.user} is not an admin.", "suspicious": 1})
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
            
            log_to_db({"username": self.session.user, "activity": "Succesfully created a backup", "additional_info": f"At {backup_path}", "suspicious": 0})
            return (True, f"Backup created at: {backup_path}")
        except Exception as e:
            return (False, f"Backup failed: {e}")


    def restore_backup_with_code(self, code) -> bool:
        if not self.session.is_valid() or self.session.role not in ["system_admin", "super_admin"]:
            log_to_db({"username": self.session.user, "activity": "Tried to restore a backup with code", "additional_info": f"Is not an admin", "suspicious": 1})
            return "Fail, Session expired" if not self.session.is_valid() else "Must be super admin to perform this action."
        cipher = Fernet(os.getenv("FERNET_KEY").encode())
        backup = cipher.decrypt(code[1].encode()).decode()
        plain_code = cipher.decrypt(code[0].encode()).decode()
        
        backup_path = os.path.join(BACKUP_DIR, backup)
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username_hash = ?", (hashlib.sha256(self.session.user.encode()).hexdigest(),))
            if cursor.fetchone()[0] != code[2]:
                log_to_db({"username": self.session.user, "activity": "Tried to restore a backup with code", "additional_info": "Code was not theirs", "suspicious": 0})
                return "Fail, this restore code is not yours. Only designated admin can use it to restore."

        if not os.path.exists(backup_path):
            log_to_db({"username": self.session.user, "activity": "Tried to restore backup", "additional_info": "no such backup", "suspicious": 0})
            return f"Backup file '{backup}' not found."

        try:
            os.makedirs(TEMP_EXTRACT_PATH, exist_ok=True)

            with zipfile.ZipFile(backup_path, 'r') as zip_ref:
                zip_ref.extractall(TEMP_EXTRACT_PATH)

            db_files = [f for f in os.listdir(TEMP_EXTRACT_PATH) if f.endswith('.db')]
            if not db_files:
                log_to_db({"username": self.session.user, "activity": "Tried to restore a backup with code", "additional_info": "No database found.", "suspicious": 0})
                return "No database file found in the backup ZIP."

            extracted_db_path = os.path.join(TEMP_EXTRACT_PATH, db_files[0])

            shutil.copy2(extracted_db_path, DB_FILE)

            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT code FROM restore_codes")
                rows = cursor.fetchall()

                for row in rows:
                    decrypted_code = cipher.decrypt(row[0].encode()).decode()
                    if decrypted_code == plain_code:
                        cursor.execute("DELETE FROM restore_codes WHERE code = ?", (row[0],))
                        conn.commit()
                        break

            log_to_db({"username": self.session.user, "activity": "Succesfully restored backup with code", "additional_info": f"", "suspicious": 0})
            return f"Backup {backup} Restored, code {plain_code} No longer usable"

        except Exception as e:
            log_to_db({"username": self.session.user, "activity": "Tried to restore a backup with code", "additional_info": "Database error", "suspicious": 0})
            return f"Error restoring backup: {str(e)}"

        finally:
            # Clean up van tijdelijke folder
            shutil.rmtree(TEMP_EXTRACT_PATH, ignore_errors=True)

    
    def add_traveller(self) -> None:
        if not self.session.is_valid() or self.session.role not in ["super_admin", "system_admin"]:
            log_to_db({"username": self.session.user, "activity": "Tried to search travellers", "additional_info": "Is not an admin", "suspicious": 1})
            print("Unauthorized or session expired.")
            return

        print("====== ADD NEW TRAVELLER ======")

        cities = ["Rotterdam", "Delft", "Schiedam", "The Hague", "Leiden",
                "Gouda", "Zoetermeer", "Spijkenisse", "Vlaardingen", "Barendrecht"]

        try:
            while True:
                first_name = input("First name: ").strip()
                if is_valid_name(first_name): break
                print("Invalid first name.")

            while True:
                last_name = input("Last name: ").strip()
                if is_valid_name(last_name): break
                print("Invalid last name.")

            while True:
                birthday = input("Birthday (YYYY-MM-DD): ").strip()
                if is_valid_birthday(birthday): break
                print("Invalid birthday. Use YYYY-MM-DD and must be between 16 and 99.")

            while True:
                gender = input("Gender (male/female): ").strip().lower()
                if is_valid_gender(gender): break
                print("Gender must be 'male' or 'female'.")

            while True:
                street = input("Street: ").strip()
                if is_valid_street(street): break
                print("Street must contain only letters and spaces.")

            while True:
                house_number = input("House number: ").strip()
                if is_valid_house_number(house_number):
                    break
                print("Invalid house number.")

            while True:
                zip_code = input("Zip Code (e.g. 1234AB): ").strip().upper()
                if is_valid_zip(zip_code): break
                print("Invalid zip code format.")

            while True:
                for i, c in enumerate(cities, start=1):
                    print(f"{i}. {c}")
                selected = input("Choose city number (1-10): ").strip()
                if selected.isdigit() and is_valid_city(cities[int(selected) - 1], cities):
                    city = cities[int(selected) - 1]
                    break
                print("Invalid city selection.")

            while True:
                email = input("E-mail (e.g. example@gmail.com): ").strip()
                if is_valid_email_and_domain(email):
                    break
                else:
                    print("Email already exists. Please use a different email.")

            while True:
                mobile = input("Mobile number (8 digits only): +31-6-").strip()
                if is_valid_mobile(mobile): break
                print("Mobile must be exactly 8 digits.")

            while True:
                license_number = input("Driving license (e.g. XX1234567 or X12345678): ").strip().upper()
                if is_valid_license(license_number): break
                print("Invalid license number format.")

            # Encrypt and insert into DB
            cipher = Fernet(os.getenv("FERNET_KEY").encode())
            registration_date = date.today().strftime('%Y-%m-%d')

            encrypted_fields = {
                "first_name": cipher.encrypt(first_name.encode()).decode('utf-8'),
                "last_name": cipher.encrypt(last_name.encode()).decode('utf-8'),
                "birthday": cipher.encrypt(birthday.encode()).decode('utf-8'),
                "gender": cipher.encrypt(gender.encode()).decode('utf-8'),
                "street": cipher.encrypt(street.encode()).decode('utf-8'),
                "house_number": cipher.encrypt(house_number.encode()).decode('utf-8'),
                "zip_code": cipher.encrypt(zip_code.encode()).decode('utf-8'),
                "city": cipher.encrypt(city.encode()).decode('utf-8'),
                "email": cipher.encrypt(email.encode()).decode('utf-8'),
                "mobile": cipher.encrypt(mobile.encode()).decode('utf-8'),
                "license_number": cipher.encrypt(license_number.encode()).decode('utf-8'),
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
                    encrypted_fields["first_name"],
                    encrypted_fields["last_name"],
                    encrypted_fields["birthday"],
                    encrypted_fields["gender"],
                    encrypted_fields["street"],
                    encrypted_fields["house_number"],
                    encrypted_fields["zip_code"],
                    encrypted_fields["city"],
                    encrypted_fields["email"],
                    encrypted_fields["mobile"],
                    encrypted_fields["license_number"],
                    registration_date
                ))


                conn.commit()
                log_to_db({"username": self.session.user, "activity": "Added a traveller", "additional_info": "Success", "suspicious": 0})
                print(f"Traveller added successfully with ID: {cursor.lastrowid}")

        except Exception as e:
            log_to_db({"username": self.session.user, "activity": "Tried to add traveller", "additional_info": "Database error", "suspicious": 0})
            print(f"[ERROR] Failed to add traveller: {e}")


    def update_traveller(self) -> None:
        if not self.session.is_valid() or self.session.role not in ["super_admin", "system_admin"]:
            log_to_db({"username": self.session.user, "activity": "Tried to update traveller", "additional_info": "Is not an admin", "suspicious": 1})
            print("Unauthorized or session expired.")
            return

        log_to_db({"username": self.session.user, "activity": "Updated a traveller", "additional_info": "Success", "suspicious": 0})
        travellers = self.traveller_overview()
        if not travellers:
            print("No travellers found.")
            return

        print("====== MODIFY A TRAVELLER ======")
        for t in travellers:
            print(f"[TRAVELLER] ID: {t['id']} | Name: {t['name']} | Registered: {t['registration_date']}")

        traveller_id = input("\nEnter the ID of the traveller: ").strip()
        if not traveller_id.isdigit():
            print("Invalid ID.")
            return

        traveller = self.get_traveller_by_id(int(traveller_id))
        if not traveller:
            print("Traveller not found.")
            return

        print("\nCurrent Traveller Details:")
        for key, value in traveller.items():
            if key not in ["id", "registration_date"]:
                print(f"  {key.replace('_', ' ').title()}: {value}")

        field_map = {
            1: "first_name", 2: "last_name", 3: "birthday", 4: "gender", 5: "street",
            6: "house_number", 7: "zip_code", 8: "city", 9: "email", 10: "mobile", 11: "license_number"
        }

        print("\nWhich fields do you want to update?")
        for num, name in field_map.items():
            print(f"{num}. {name.replace('_', ' ').title()}")

        selection = input("Enter numbers separated by commas (e.g. 1,4,7): ").strip()
        try:
            selected_fields = [int(s) for s in selection.split(",") if int(s) in field_map]
        except ValueError:
            print("Invalid selection.")
            return

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

        updated_data = {}
        cipher = Fernet(os.getenv("FERNET_KEY").encode())

        for field_id in selected_fields:
            field = field_map[field_id]
            old_value = traveller.get(field, "[not found]")
            new_value = input(f"New {field.replace('_', ' ').title()} (was: {old_value}): ").strip()

            validator = validators.get(field)
            if validator and validator(new_value):
                if field == "house_number":
                    updated_data[field] = cipher.encrypt(str(int(new_value)).encode()).decode('utf-8')
                else:
                    updated_data[field] = cipher.encrypt(new_value.encode()).decode('utf-8')
            else:
                print(f"Invalid input for {field.replace('_', ' ')}. Skipping.")

        if not updated_data:
            print("No valid fields provided to update.")
            return

        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                fields_query = ", ".join(f"{field} = ?" for field in updated_data)
                values = list(updated_data.values())

                query = f"UPDATE travellers SET {fields_query} WHERE id = ?"
                cursor.execute(query, values + [int(traveller_id)])
                conn.commit()

                if cursor.rowcount == 0:
                    print(f"No traveller found with ID {traveller_id}.")
                else:
                    print(f"Traveller {traveller_id} successfully updated.")
        except Exception as e:
            print(f"[ERROR] Failed to update traveller: {e}")

    def delete_traveller(self) -> None:
        if not self.session.is_valid() or self.session.role not in ["super_admin", "system_admin"]:
            log_to_db({"username": self.session.user, "activity": "Tried to delete traveller", "additional_info": "Is not an admin", "suspicious": 1})
            print("Unauthorized or session expired.")
            return

        log_to_db({"username": self.session.user, "activity": "Deleted a traveller", "additional_info": "Success", "suspicious": 0})
        travellers = self.traveller_overview()
        if not travellers:
            print("No travellers found.")
            return

        print("====== DELETE A TRAVELLER ======")
        for t in travellers:
            print(f"[TRAVELLER] ID: {t['id']} | Name: {t['name']} | Registered: {t['registration_date']}")

        traveller_id = input("\nEnter the ID of the traveller to delete: ").strip()
        if not traveller_id.isdigit():
            print("Invalid ID.")
            return

        confirm = input("Are you sure you want to delete this traveller? (yes/no): ").strip().lower()
        if confirm not in ("yes", "y"):
            print("Deletion cancelled.")
            return

        try:
            cipher = Fernet(os.getenv("FERNET_KEY").encode())

            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT first_name, last_name FROM travellers WHERE id = ?", (int(traveller_id),))
                row = cursor.fetchone()

                if not row:
                    print("Traveller not found.")
                    return

                decrypted_first_name = cipher.decrypt(row[0].encode()).decode()
                decrypted_last_name = cipher.decrypt(row[1].encode()).decode()
                full_name = f"{decrypted_first_name} {decrypted_last_name}"

                cursor.execute("DELETE FROM travellers WHERE id = ?", (int(traveller_id),))
                conn.commit()

            print(f"Traveller {full_name} with ID {traveller_id} successfully deleted.")
        except Exception as e:
            print(f"[ERROR] Failed to delete traveller: {e}")
    
    # Wordt alleen gebruikt door update_traveller, dus geen logging nodig
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

                # Alle velden behalve id, house_number en registration_date moeten worden ontsleuteld
                encrypted_keys = {
                    "first_name", "last_name", "birthday", "gender",
                    "street", "house_number" , "zip_code", "city", "email", "mobile", "license_number"
                }

                for key in encrypted_keys:
                    if decrypted[key]:
                        decrypted[key] = cipher.decrypt(decrypted[key].encode()).decode()

                return decrypted
        except Exception as e:
            print(f"[ERROR] Failed to load traveller: {e}")
            return None

    def view_travellers_by_id(self, traveller_id):
        if not self.session.is_valid() or self.session.role not in ["super_admin", "system_admin"]:
            log_to_db({"username": self.session.user, "activity": "Tried to view travellers by id", "additional_info": "Is not an admin", "suspicious": 1})
            print("Session Expired or Not an admin")
            return

        cipher = Fernet(os.getenv("FERNET_KEY").encode())
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        log_to_db({"username": self.session.user, "activity": "Fetched travellers by id", "additional_info": "Success", "suspicious": 0})

        try:
            cursor.execute("SELECT * FROM travellers WHERE id LIKE ?", (f"%{traveller_id}%",))
            travellers = cursor.fetchall()
            if travellers:
                print("Travellers found:")
                fields = [
                    "id", "first_name", "last_name", "birthday", "gender",
                    "street", "house_number", "zip_code", "city", "email",
                    "mobile", "license_number", "registration_date"
                ]
                encrypted_keys = {
                    "first_name", "last_name", "birthday", "gender",
                    "street", "house_number" ,"zip_code", "city", "email", "mobile", "license_number"
                }

                for row in travellers:
                    traveller = dict(zip(fields, row))

                    for key in encrypted_keys:
                        try:
                            if traveller[key]:
                                traveller[key] = cipher.decrypt(traveller[key].encode()).decode()
                        except Exception:
                            traveller[key] = "[DECRYPTION FAILED]"

                    for key, value in traveller.items():
                        print(f"{key.replace('_', ' ').title()}: {value}")
                    print("-" * 40)
            else:
                print(f"No travellers found containing ID: {traveller_id}")
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
            conn.close()

    def view_travellers_by_last_name(self, traveller_last_name):
        if not self.session.is_valid():
            log_to_db({"username": self.session.user, "activity": "Tried to view travellers by last name", "additional_info": "Is not an admin", "suspicious": 1})
            print("Session Expired")
            return

        cipher = Fernet(os.getenv("FERNET_KEY").encode())
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        log_to_db({"username": self.session.user, "activity": "Fetched travellers by lastname", "additional_info": "Success", "suspicious": 0})

        try:
            cursor.execute("SELECT * FROM travellers WHERE last_name LIKE ?", (f"%{traveller_last_name}%",))
            travellers = cursor.fetchall()
            if travellers:
                print("Travellers found:")
                fields = [
                    "id", "first_name", "last_name", "birthday", "gender",
                    "street", "house_number", "zip_code", "city", "email",
                    "mobile", "license_number", "registration_date"
                ]
                encrypted_keys = {
                    "first_name", "last_name", "birthday", "gender",
                    "street","house_number", "zip_code", "city", "email", "mobile", "license_number"
                }

                for row in travellers:
                    traveller = dict(zip(fields, row))

                    for key in encrypted_keys:
                        try:
                            if traveller[key]:
                                traveller[key] = cipher.decrypt(traveller[key].encode()).decode()
                        except Exception:
                            traveller[key] = "[DECRYPTION FAILED]"

                    for key, value in traveller.items():
                        print(f"{key.replace('_', ' ').title()}: {value}")
                    print("-" * 40)
            else:
                print(f"No travellers found containing Last Name: {traveller_last_name}")
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
            conn.close()

    def add_scooter(self, scooter_data: dict) -> bool:
        if not self.session.is_valid() or self.session.role not in ["super_admin", "system_admin"]:
            log_to_db({"username": self.session.user, "activity": "Tried to add scooter", "additional_info": "Not an admin", "suspicious": 1})
            return False

        cipher = Fernet(os.getenv("FERNET_KEY").encode())

        try:
            encrypted_serial = cipher.encrypt(scooter_data["serial_number"].encode()).decode('utf-8')
            encrypted_location = cipher.encrypt(scooter_data["location"].encode()).decode('utf-8')

            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO scooters (
                        brand, model, serial_number, top_speed, battery_capacity,
                        soc, target_range_soc, location, out_of_service,
                        mileage, last_maintenance, in_service
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    scooter_data["brand"],
                    scooter_data["model"],
                    encrypted_serial,
                    scooter_data["top_speed"],
                    scooter_data["battery_capacity"],
                    scooter_data["soc"],
                    scooter_data["target_range_soc"],
                    encrypted_location,
                    scooter_data["out_of_service"],
                    scooter_data["mileage"],
                    scooter_data["last_maintenance"],
                    scooter_data["in_service"]
                ))
                conn.commit()
                print("New scooter ID:", cursor.lastrowid)
                log_to_db({
                    "username": self.session.user,
                    "activity": "Added a scooter",
                    "additional_info": f"Encrypted serial number added",
                    "suspicious": 0
                })
            return True
        except Exception as e:
            print(f"[ERROR] Failed to add scooter: {e}")
            return False

    def delete_scooter(self) -> bool:
        if not self.session.is_valid() or self.session.role not in ["super_admin", "system_admin"]:
            print("Unauthorized or session expired.")
            log_to_db({"username": self.session.user, "activity": "tried to delete scooter", "additional_info": "not an admin", "suspicious": 1})
            return False

        cipher = Fernet(os.getenv("FERNET_KEY").encode())

        log_to_db({"username": self.session.user, "activity": "Deleted a scooter", "additional_info": "Success", "suspicious": 0})
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, brand, model, location, out_of_service FROM scooters")
            scooters = cursor.fetchall()

            if not scooters:
                print("No scooters found.")
                return False

            print("====== DELETE A SCOOTER ======")
            for s in scooters:
                scooter_id = s[0]
                brand = s[1]
                model = s[2]
                try:
                    location = cipher.decrypt(s[3].encode()).decode()
                except Exception:
                    location = "[DECRYPTION FAILED]"
                out_of_service = bool(s[4])

                print(f"[SCOOTER] ID: {scooter_id} | Brand: {brand} | Model: {model} | Location: {location} | Out of Service: {out_of_service}")

            scooter_id_input = input("\nEnter the ID of the scooter to delete: ").strip()
            if not scooter_id_input.isdigit():
                print("Invalid ID.")
                return False
            scooter_id = int(scooter_id_input)

            confirm = input("Are you sure you want to delete this scooter? (Y/N): ").strip().lower()
            if confirm not in ("yes", "y"):
                print("Deletion cancelled.")
                return False

            cursor.execute("SELECT brand, model FROM scooters WHERE id = ?", (scooter_id,))
            scooter_data = cursor.fetchone()

            if not scooter_data:
                print("Scooter not found.")
                return False

            cursor.execute("DELETE FROM scooters WHERE id = ?", (scooter_id,))
            conn.commit()

            print(f"Scooter '{scooter_data[0]} {scooter_data[1]}' with ID {scooter_id} successfully deleted.")
            return True
        
    def view_restore_codes(self, sys=True):
        log_to_db({"username": self.session.user, "activity": "Viewed their restore codes", "additional_info": "Success", "suspicious": 0})
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        if sys:
            cursor.execute("SELECT id FROM users WHERE username_hash = ?", (hashlib.sha256(self.session.user.encode()).hexdigest(),))
            ad_id = cursor.fetchone()[0]
            cursor.execute("""SELECT code, backup_filename, system_admin_id, used, created_at
                        FROM restore_codes WHERE system_admin_id = ?""", (ad_id,))
        else:
            cursor.execute("SELECT code, backup_filename, system_admin_id, used, created_at FROM restore_codes")
        records = cursor.fetchall()
        conn.close()

        if not records:
            if sys:
                print("You have no restore codes. Ask a super admin to give you one.")
                return False
            print("There are no restore codes.")
            return False
        
        cipher = Fernet(os.getenv("FERNET_KEY").encode())

        if sys:
            print("\n--- Your personal restore codes ---")
        else:
            print("\n--- ALL RESTORE CODES ---\n")
        for row in records:
            code, backup_filename, admin_id, used, date_created = row
            print(f"Code: {cipher.decrypt(code.encode()).decode()}")
            print(f"  Backup File: {cipher.decrypt(backup_filename.encode()).decode()}")
            print(f"  Super admin ID:    {admin_id}")
            print(f"  Used:        {used}")
            print(f"  Date Created:{date_created}")
            print("-----------------------------\n")
        return True

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
                try:
                    first_name = cipher.decrypt(row[1].encode()).decode()
                    last_name = cipher.decrypt(row[2].encode()).decode()
                except Exception:
                    first_name = "[DECRYPTION FAILED]"
                    last_name = "[DECRYPTION FAILED]"

                reg_date = row[3]
                overview.append({
                    "id": traveller_id,
                    "name": f"{first_name} {last_name}",
                    "registration_date": reg_date
                })

        return overview

    def delete_account(self) -> None:
        if not self.session.is_valid():
            log_to_db({"username": self.session.user, "activity": "Tried to delete their account", "additional_info": "No session", "suspicious": 1})
            print("Session expired.")
            return

        try:
            confirm = input("Are you sure you want to delete your account? (yes/no): ").strip().lower()
            if confirm != "yes":
                print("Account deletion cancelled.")
                return

            final_confirm = input("Type 'CONFIRM' in all caps to permanently delete your account: ").strip()
            if final_confirm != "CONFIRM":
                print("Final confirmation failed. Account not deleted.")
                return

            username = self.session.user
            username_hash = hashlib.sha256(username.encode()).hexdigest()

            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, username FROM users WHERE username_hash = ?", (username_hash,))
                result = cursor.fetchone()

                if not result:
                    print("User not found.")
                    return

                user_id, encrypted_username = result
                cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
                conn.commit()

                cipher = Fernet(os.getenv("FERNET_KEY").encode())
                decrypted_username = cipher.decrypt(encrypted_username.encode()).decode()
                print(f"Deleted account for user: {decrypted_username}")
                log_to_db({"username": self.session.user, "activity": "Deleted their account", "additional_info": "Success", "suspicious": 0})
                
                print("\nSession terminated. Returning to login menu...")
                
                time.sleep(2)
                from ui.login_interface import start_interface
                clear()
                start_interface()
                sys.exit()

        except Exception as e:
            print(f"[ERROR] Failed to delete account: {e}")

    def get_user_by_id(self, user_id: int) -> dict | None:
        try:
            cipher = Fernet(os.getenv("FERNET_KEY").encode())

            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
                row = cursor.fetchone()

                if not row:
                    return None

                fields = [
                    "id", "username", "password_hash", "role", "first_name",
                    "last_name", "registration_date", "username_hash", "must_change_password"
                ]

                decrypted = dict(zip(fields, row))

                # Only username is encrypted
                if decrypted["username"]:
                    decrypted["username"] = cipher.decrypt(decrypted["username"].encode()).decode()

                return decrypted
        except Exception as e:
            print(f"[ERROR] Failed to load user: {e}")
            return None
