import os
from services.auth import authenticate_user, get_role
from services.SystemAdminService import SystemAdminService
from ui.super_admin_interface import super_admin_interface
from ui.system_admin_interface import system_admin_interface
from ui.service_engineer_interface import service_engineer_interface
from models.Session import Session
from visual.text_colors import TextColors
from ui.prompts.field_prompts import *
from ui.menu_utils import *
import sqlite3
import hashlib


t = TextColors

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def start_interface():
    while True:
        print("====== URBAN MOBILITY BACKEND SYSTEM ======")
        print(f"\n{t.blue}Please log in to continue.{t.end}")
        username = input("Username: ").strip().lower()
        if len(username) < 8 or len(username) > 10 and username != 'super_admin':
            clear()
            print(f"{t.red}[ERROR] Username must be between 8 and 10 characters long.{t.end}")
            continue
        password_raw = input_password()

        if password_raw is None:
            print(f"{t.red}[INFO] Password input cancelled. Exiting.{t.end}")
            continue
        if not username:
            print(f"{t.red}[ERROR] Username cannot be empty.{t.end}")
            continue

        password = password_raw.strip()

        if authenticate_user(username, password):
            role = get_role(username)
            session = Session(username, role)
            check_temporary_password(username, session)

            print(f"\n[INFO] Welcome, {username}! Role: {role}")
            
            if role == "super_admin":
                super_admin_interface(session)
            elif role == "system_admin":
                system_admin_interface(session)
            elif role == "service_engineer":
                service_engineer_interface(session)
            else:
                print(f"{t.red}[ERROR] Unknown role. Access denied.{t.end}")
        else:
            print(f"{t.red}[ERROR] Invalid credentials.{t.end}")

        again = input(f"\n{t.blue}Do you want to log in again? (Y/N): {t.end}").strip().lower()
        if again != 'y':
            print(f"{t.blue}[INFO] Exiting the system.{t.end}")
            break


def check_temporary_password(username, session):
    with sqlite3.connect("src/data/urban_mobility.db") as conn:
        cursor = conn.cursor()
        hashed_uname = hashlib.sha256(username.encode()).hexdigest()
        
        cursor.execute("SELECT id, must_change_password FROM users WHERE username_hash = ?", (hashed_uname,))
        result = cursor.fetchone()

        if result and result[1] == 1:
            print("You must set a new password before continuing.")
            new_pass = prompt_password(Prompt="Enter a new strong password: ")
            service = SystemAdminService(session)
            service.update_user(result[0], {"password_hash": new_pass})

            # must_change_password terug naar 0
            cursor.execute("""
                UPDATE users
                SET must_change_password = 0
                WHERE username_hash = ?
            """, (hashed_uname,))
            conn.commit()

            print(f"Password successfully changed for account: {username}")
            click_to_return()