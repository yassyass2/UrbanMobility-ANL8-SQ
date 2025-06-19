import bcrypt
import os
import sqlite3
import sys
import hashlib
from models.Session import Session
from cryptography.fernet import Fernet
from ui.prompts.field_prompts import input_password
from ui.menu_utils import clear
from logger import *
from services.validation import is_valid_number

DB_FILE = 'data/urban_mobility.db'

class ServiceEngineerService():
    def __init__(self, session: Session):
        self.session: Session = session

    def update_password(self):
        if self.session.is_valid():

            username = self.session.user
            username_hash = hashlib.sha256(username.encode()).hexdigest()

            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT password_hash FROM users WHERE username_hash = ?", (username_hash,))
                result = cursor.fetchone()
                if not result:
                    print("User not found.")
                    return

                stored_hash = result[0]

                # OLD PASSWORD
                old_password = input_password("Enter your current password: ").strip()
                if old_password is None:
                    return
                if not bcrypt.checkpw(old_password.encode(), stored_hash):
                    print("Incorrect current password.")
                    return

                # NEW PASSWORD ENTRY + CONFIRMATION
                while True:
                    print("Password rules: between 12 and 30 chars, at least 1 lowercase, 1 uppercase, 1 digit, and 1 symbol")
                    new_password = input_password("Enter new password: ").strip()
                    if new_password is None:
                        return

                    # VALIDATION
                    if not (12 <= len(new_password) <= 30):
                        clear(); continue
                    if not any(c.islower() for c in new_password):
                        clear(); continue
                    if not any(c.isupper() for c in new_password):
                        clear(); continue
                    if not any(c.isdigit() for c in new_password):
                        clear(); continue
                    if not any(c in "~!@#$%&_-+=`|\\(){}[]:;'<>,.?/" for c in new_password):
                        clear(); continue

                    # CONFIRMATION
                    confirm_password = input_password("Confirm new password: ").strip()
                    if confirm_password != new_password:
                        clear()
                        print("Passwords do not match."); continue

                    break

                hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())

                cursor.execute(
                    "UPDATE users SET password_hash = ?, must_change_password = 0 WHERE username_hash = ?",
                    (hashed, username_hash)
                )
                conn.commit()
                print("Password updated successfully.")
                log_to_db({"username": self.session.user, "activity": "Changed their password", "additional_info": "succesful change", "suspicious": 0})
            except sqlite3.Error as e:
                print(f"Database error: {e}")
            finally:
                conn.close()

        else:
            log_to_db({"username": self.session.user, "activity": "Tried to change password", "additional_info": "Expired session", "suspicious": 0})
            print("Session expired")
            return

    def search_scooter_by_id(self, scooter_id):
        if self.session.is_valid():

            cipher = Fernet(os.getenv("FERNET_KEY").encode())
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()

            try:
                cursor.execute("SELECT * FROM scooters WHERE id LIKE ?", (f"%{scooter_id}%",))
                scooters = cursor.fetchall()

                if scooters:
                    print("Scooters found:")
                    fields = [
                        "id", "brand", "model", "serial_number", "top_speed",
                        "battery_capacity", "soc", "target_range_soc", "location",
                        "out_of_service", "mileage", "last_maintenance", "in_service"
                    ]
                    for s in scooters:
                        scooter = dict(zip(fields, s))

                        for field in ["serial_number", "location"]:
                            try:
                                if scooter[field]:
                                    scooter[field] = cipher.decrypt(scooter[field].encode()).decode()
                            except Exception:
                                scooter[field] = "[DECRYPTION FAILED]"

                        for key, value in scooter.items():
                            print(f"{key.replace('_', ' ').title()}: {value}")
                        print("-" * 40)
                else:
                    print(f"No scooter found with ID containing '{scooter_id}'.")
            except sqlite3.Error as e:
                print(f"Database error: {e}")
            finally:
                log_to_db({"username": self.session.user, "activity": "Searched for scooters by ID", "additional_info": "", "suspicious": 0})
                conn.close()
        else:
            log_to_db({"username": self.session.user, "activity": "Tried to search scooter", "additional_info": "Expired session", "suspicious": 0})
            print("Session expired")
            return

    def search_scooter_by_brand(self, scooter_brand):
        if self.session.is_valid():
            

            cipher = Fernet(os.getenv("FERNET_KEY").encode())
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()

            try:
                cursor.execute("SELECT * FROM scooters WHERE brand LIKE ?", (f"%{scooter_brand}%",))
                scooters = cursor.fetchall()

                if scooters:
                    print("Scooters found:")
                    fields = [
                        "id", "brand", "model", "serial_number", "top_speed",
                        "battery_capacity", "soc", "target_range_soc", "location",
                        "out_of_service", "mileage", "last_maintenance", "in_service"
                    ]
                    for s in scooters:
                        scooter = dict(zip(fields, s))

                        # Decrypt sensitive fields
                        for field in ["serial_number", "location"]:
                            try:
                                if scooter[field]:
                                    scooter[field] = cipher.decrypt(scooter[field].encode()).decode()
                            except Exception:
                                scooter[field] = "[DECRYPTION FAILED]"

                        # Print formatted output
                        for key, value in scooter.items():
                            print(f"{key.replace('_', ' ').title()}: {value}")
                        print("-" * 40)
                else:
                    print(f"No scooter found containing brand: {scooter_brand}.")
            except sqlite3.Error as e:
                print(f"Database error: {e}")
            finally:
                log_to_db({"username": self.session.user, "activity": "Searched for scooters by brand", "additional_info": "", "suspicious": 0})
                conn.close()
        else:
            log_to_db({"username": self.session.user, "activity": "Tried to search scooter", "additional_info": "Expired session", "suspicious": 0})
            print("Session expired")
            return

    def update_scooter(self, scooter_id: int, to_update: dict):
        if self.session.is_valid():

            if not to_update:
                log_to_db({"username": self.session.user, "activity": "Tried to update scooter", "additional_info": "No fields provided", "suspicious": 0})
                return "No fields provided to update."

            cipher = Fernet(os.getenv("FERNET_KEY").encode())
            encrypted_fields = {"serial_number", "location"}

            try:
                with sqlite3.connect(DB_FILE) as conn:
                    cursor = conn.cursor()

                    cursor.execute("SELECT 1 FROM scooters WHERE id = ?", (scooter_id,))
                    exists = cursor.fetchone()
                    if not exists:
                        print(f"No scooter found with ID {scooter_id}.")
                        return False

                    for field in encrypted_fields:
                        if field in to_update:
                            try:
                                to_update[field] = cipher.encrypt(to_update[field].encode()).decode('utf-8')
                            except Exception as e:
                                return f"Encryption failed for '{field}': {e}"

                    fields_query = ", ".join(f"{field} = ?" for field in to_update)
                    values = list(to_update.values())

                    query = f"UPDATE scooters SET {fields_query} WHERE id = ?"
                    cursor.execute(query, values + [scooter_id])
                    conn.commit()

                    print(f"Scooter with ID {scooter_id} updated successfully.")
                    log_to_db({
                        "username": self.session.user,
                        "activity": "Updated a scooter.",
                        "additional_info": f"Scooter with ID {scooter_id} updated successfully.",
                        "suspicious": 0
                    })
                    return True

            except sqlite3.Error as e:
                return f"Database error: {e}"
            
        else:
            log_to_db({"username": self.session.user, "activity": "Tried to update scooter", "additional_info": "Expired session", "suspicious": 0})
            return "Fail, Session expired" if not self.session.is_valid() else "Must be at least service engineer to perform this action."

    def get_scooter_by_id(self, scooter_id: int) -> dict | None:
        if self.session.is_valid():

            try:
                cipher = Fernet(os.getenv("FERNET_KEY").encode())

                with sqlite3.connect(DB_FILE) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM scooters WHERE id = ?", (scooter_id,))
                    row = cursor.fetchone()

                    if not row:
                        return None

                    fields = [
                        "id", "brand", "model", "serial_number", "top_speed",
                        "battery_capacity", "soc", "target_range_soc", "location",
                        "out_of_service", "mileage", "last_maintenance", "in_service"
                    ]

                    decrypted = dict(zip(fields, row))

                    encrypted_keys = {"serial_number", "location"}

                for key in encrypted_keys:
                    if decrypted[key]:
                        decrypted[key] = cipher.decrypt(decrypted[key].encode()).decode()

                return decrypted
            except Exception as e:
                print(f"[ERROR] Failed to load scooter: {e}")
                return None
            
        else:
            log_to_db({"username": self.session.user, "activity": "Tried to search scooters", "additional_info": "Expired session", "suspicious": 0})
            print("Session expired")
            return
        
    def get_scooter_list(self):
        if self.session.is_valid():

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
        else:
            log_to_db({"username": self.session.user, "activity": "Tried to search scooters", "additional_info": "Expired session", "suspicious": 0})
            print("Session expired")
            return