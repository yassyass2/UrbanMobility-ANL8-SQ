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

DB_FILE = 'data/urban_mobility.db'

class ServiceEngineerService():
    def __init__(self, session: Session):
        self.session: Session = session

    def update_password(self):
        if not self.session.is_valid():
            log_to_db({"username": self.session.user, "activity": "Tried to change password", "additional_info": "Expired session", "suspicious": 0})
            print("Session expired")
            return

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

    def search_scooter_by_id(self, scooter_id):
        if not self.session.is_valid():
            log_to_db({"username": self.session.user, "activity": "Tried to search scooter", "additional_info": "Expired session", "suspicious": 0})
            print("session expired")
            return

        # Connect to the database
        conn = sqlite3.connect('data/urban_mobility.db')
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM scooters WHERE id LIKE ?", (f"%{scooter_id}%",))
            scooters = cursor.fetchall()
            if scooters:
                print("Scooters found:")
                for scooter in scooters:
                    print(scooter)
            else:
                print(f"No scooter found with ID containing '{scooter_id}'.")
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
            log_to_db({"username": self.session.user, "activity": "Searched for scooters by ID", "additional_info": "", "suspicious": 0})
            conn.close()

    def search_scooter_by_name(self, scooter_name):
        if not self.session.is_valid():
            log_to_db({"username": self.session.user, "activity": "Tried to search scooter", "additional_info": "Expired session", "suspicious": 0})
            print("Session expired")
            return
        
        conn = sqlite3.connect('data/urban_mobility.db')
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM scooters WHERE brand LIKE ?", (f"%{scooter_name}%",))
            scooters = cursor.fetchall()
            if scooters:
                print(f"Scooters found:")
                for scooter in scooters:
                    print(scooter)
            else: 
                print(f"No scooter found containing name: {scooter_name}.")
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
            log_to_db({"username": self.session.user, "activity": "Searched for scooters by name", "additional_info": "", "suspicious": 0})
            conn.close()


    def update_scooter(self, scooter_id: int, to_update: dict):
        if not self.session.is_valid() or self.session.role not in ["service_engineer", "system_admin", "super_admin"]:
            log_to_db({"username": self.session.user, "activity": "Tried to update scooter", "additional_info": "Expired session", "suspicious": 0})
            return "Fail, Session expired" if not self.session.is_valid() else "Must be at least service engineer to perform this action."
        if not to_update:
            log_to_db({"username": self.session.user, "activity": "Tried to change password", "additional_info": "no fields provided.", "suspicious": 0})
            return "No fields provided to update."

        fields_query = ", ".join(f"{field} = ?" for field in to_update)
        new_values = list(to_update.values())

        try:
            with sqlite3.connect('data/urban_mobility.db') as conn:
                cursor = conn.cursor()
                query = f"UPDATE scooters SET {fields_query} WHERE id = ?"
                cursor.execute(query, new_values + [scooter_id])
                conn.commit()

                if cursor.rowcount == 0:
                    print(f"No scooter found with ID {scooter_id}.")
                    return False
                print(f"Scooter with ID {scooter_id} updated successfully.")
                log_to_db({"username": self.session.user, "activity": "Updated a scooter.", "additional_info": f"Scooter with ID {scooter_id} updated successfully.", "suspicious": 0})
                return True

        except sqlite3.Error as e:
            return f"Database error: {e}"
