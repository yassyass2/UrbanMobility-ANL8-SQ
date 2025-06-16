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
    
    def add_traveller(self) -> None:
        if not self.session.is_valid() or self.session.role not in ["super_admin", "system_admin"]:
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
                print("Invalid birthday. Use YYYY-MM-DD and must be in the past.")

            while True:
                gender = input("Gender (male/female): ").strip().lower()
                if is_valid_gender(gender): break
                print("Gender must be 'male' or 'female'.")

            while True:
                street = input("Street: ").strip()
                if is_valid_street(street): break
                print("Street must contain only letters and spaces.")

            while True:
                house_number_input = input("House number: ").strip()
                if is_valid_house_number(house_number_input):
                    house_number = int(house_number_input)
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
                license_number = input("Driving license (e.g. 1234567890): ").strip().upper()
                if is_valid_license(license_number): break
                print("Invalid license number format.")

            # Encrypt and insert into DB
            cipher = Fernet(os.getenv("FERNET_KEY").encode())
            registration_date = date.today().strftime('%Y-%m-%d')

            encrypted_fields = {
                "street": cipher.encrypt(street.encode()).decode('utf-8'),
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
                    first_name,
                    last_name,
                    birthday,
                    gender,
                    encrypted_fields["street"],
                    house_number,
                    encrypted_fields["zip_code"],
                    encrypted_fields["city"],
                    encrypted_fields["email"],
                    encrypted_fields["mobile"],
                    encrypted_fields["license_number"],
                    registration_date
                ))

                conn.commit()
                print(f"Traveller added successfully with ID: {cursor.lastrowid}")

        except Exception as e:
            print(f"[ERROR] Failed to add traveller: {e}")


    def update_traveller(self) -> None:
        if not self.session.is_valid() or self.session.role not in ["super_admin", "system_admin"]:
            print("Unauthorized or session expired.")
            return

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

        sensitive_fields = {"street", "zip_code", "city", "email", "mobile", "license_number"}
        updated_data = {}
        cipher = Fernet(os.getenv("FERNET_KEY").encode())

        for field_id in selected_fields:
            field = field_map[field_id]
            old_value = traveller.get(field, "[not found]")
            new_value = input(f"New {field.replace('_', ' ').title()} (was: {old_value}): ").strip()

            validator = validators.get(field)
            if validator and validator(new_value):
                if field == "house_number":
                    updated_data[field] = int(new_value)
                elif field in sensitive_fields:
                    updated_data[field] = cipher.encrypt(new_value.encode()).decode('utf-8')
                else:
                    updated_data[field] = new_value
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
            print("Unauthorized or session expired.")
            return

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
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT first_name, last_name FROM travellers WHERE id = ?", (int(traveller_id),))
                row = cursor.fetchone()

                if not row:
                    print("Traveller not found.")
                    return

                full_name = f"{row[0]} {row[1]}"
                cursor.execute("DELETE FROM travellers WHERE id = ?", (int(traveller_id),))
                conn.commit()

            print(f"Traveller {full_name} with ID {traveller_id} successfully deleted.")
        except Exception as e:
            print(f"[ERROR] Failed to delete traveller: {e}")


    
    def view_travellers_by_id(self, traveller_id):
        if not self.session.is_valid():
            print("Session Expired")
            return

        cipher = Fernet(os.getenv("FERNET_KEY").encode())
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

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
                for row in travellers:
                    traveller = dict(zip(fields, row))

                    # Decrypt sensitive fields
                    for key in ["street", "zip_code", "city", "email", "mobile", "license_number"]:
                        if traveller[key]:
                            traveller[key] = cipher.decrypt(traveller[key].encode()).decode()

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
            print("Session Expired")
            return

        cipher = Fernet(os.getenv("FERNET_KEY").encode())
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM travellers WHERE last_name LIKE ?", (f"%{traveller_last_name}%",))   
            travellers = cursor.fetchall()
            if travellers:
                print("Travellers found:")
                for row in travellers:
                    fields = [
                        "id", "first_name", "last_name", "birthday", "gender",
                        "street", "house_number", "zip_code", "city", "email",
                        "mobile", "license_number", "registration_date"
                    ]
                    traveller = dict(zip(fields, row))

                    # Decrypt sensitive fields
                    for key in ["street", "zip_code", "city", "email", "mobile", "license_number"]:
                        if traveller[key]:
                            traveller[key] = cipher.decrypt(traveller[key].encode()).decode()

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
            return False

        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO scooters (
                    brand, model, serial_number, top_speed, battery_capacity, soc, target_range_soc, location, out_of_service, mileage, last_maintenance
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                scooter_data["brand"],
                scooter_data["model"],
                scooter_data["serial_number"],
                scooter_data["top_speed"],
                scooter_data["battery_capacity"],
                scooter_data["soc"],
                scooter_data["target_range_soc"],
                scooter_data["location"],
                scooter_data["out_of_service"],
                scooter_data["mileage"],
                scooter_data["last_maintenance"]
            ))
            conn.commit()
        return True

    def delete_scooter(self, scooter_id: int) -> bool:
        if not self.session.is_valid() or self.session.role not in ["super_admin", "system_admin"]:
            return False

        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM scooters WHERE id = ?", (scooter_id,))
            conn.commit()
            return f"Scooter with ID {scooter_id} deleted successfully." if cursor.rowcount > 0 else f"No scooter found with ID {scooter_id}."