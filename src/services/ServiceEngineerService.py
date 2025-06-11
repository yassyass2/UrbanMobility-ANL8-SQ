import bcrypt
import os
import sqlite3
import sys
from models.Session import Session


class ServiceEngineerService():
    def __init__(self, session: Session):
        self.session: Session = session

    def update_password(self):
        if (not self.session.is_valid()):
            print("session expired")
            return
        new_password = input("Enter new password: ").strip()
        if len(new_password) < 8 or len(new_password) > 10:
            print("Password must be between 8 and 10 characters long.")
            return
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        # Update the password in the database
        # NOT YET IMPLEMENTED!

        print(f"Password updated for user {self.session.username}.")
        return

    def update_scooter(self, scooter_id):
        if (not self.session.is_valid()):
            print("session expired")
            return
        print(f"Updated scooter {scooter_id}.")

    def search_scooter(self, scooter_id):
        if not self.session.is_valid():
            print("session expired")
            return

        # Connect to the database
        conn = sqlite3.connect('src/data/urban_mobility.db')
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM scooters WHERE id = ?", (scooter_id,))
            scooter = cursor.fetchone()
            if scooter:
                print(f"Scooter found: {scooter}")
            else:
                print(f"No scooter found with ID {scooter_id}.")
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
            conn.close()
