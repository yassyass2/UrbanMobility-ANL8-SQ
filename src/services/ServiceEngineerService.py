import bcrypt
import os
import sqlite3
import sys
import hashlib
from models.Session import Session

DB_FILE = 'src/data/urban_mobility.db'

class ServiceEngineerService():
    def __init__(self, session: Session):
        self.session: Session = session

    def update_password(self):
        if not self.session.is_valid():
            print("Session expired")
            return

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        try:
            username = self.session.user
            username_hash = hashlib.sha256(username.encode()).hexdigest()
            cursor.execute("SELECT password_hash FROM users WHERE username_hash = ?", (username_hash,))
            result = cursor.fetchone()
            if not result:
                print("User not found.")
                return

            stored_hash = result[0]

            old_password = input("Enter your current password: ").strip()
            if not bcrypt.checkpw(old_password.encode(), stored_hash):
                print("Incorrect current password.")
                return

            # Ask for new password
            while True:
                new_password = input("Enter new password: ").strip()
                if not (12 <= len(new_password) <= 30):
                    print("Password must be between 12 and 30 characters.")
                    continue
                if not any(c.islower() for c in new_password):
                    print("Password must contain at least one lowercase letter.")
                    continue
                if not any(c.isupper() for c in new_password):
                    print("Password must contain at least one uppercase letter.")
                    continue
                if not any(c.isdigit() for c in new_password):
                    print("Password must contain at least one digit.")
                    continue
                if not any(c in "~!@#$%&_-+=`|\\(){}[]:;'<>,.?/" for c in new_password):
                    print("Password must contain at least one symbol.")
                    continue
                break

            hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())

            cursor.execute("UPDATE users SET password_hash = ?, must_change_password = 0 WHERE username_hash = ?", (hashed, username_hash))
            conn.commit()
            print("Password updated successfully.")
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
            conn.close()

    def update_scooter(self, scooter_id):
        if (not self.session.is_valid()):
            print("session expired")
            return
        print(f"Updated scooter {scooter_id}.")

    def search_scooter_by_id(self, scooter_id):
        if not self.session.is_valid():
            print("session expired")
            return

        # Connect to the database
        conn = sqlite3.connect('src/data/urban_mobility.db')
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
            conn.close()

    def search_scooter_by_name(self, scooter_name):
        if not self.session.is_valid():
            print("Session expired")
            return
        
        conn = sqlite3.connect('src/data/urban_mobility.db')
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
            conn.close()

    def change_password(self, new_password):
        if not self.session.is_valid():
            print("Session expired")
            return
        
        if len(new_password) < 8 or len(new_password) > 10:
            print("Password must be between 8 and 10 characters long.")
            return
        
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

        # Update the password in the database
        conn = sqlite3.connect('src/data/urban_mobility.db')
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE users SET password = ? WHERE username = ?", (hashed_password, self.session.username))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return
        finally:
            conn.close()
        
        print(f"Password changed successfully for user {self.session.username}.")

