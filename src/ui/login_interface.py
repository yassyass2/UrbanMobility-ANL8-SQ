import os
from services.auth import authenticate_user, get_role
from ui.super_admin_interface import super_admin_interface
from ui.system_admin_interface import system_admin_interface
from ui.service_engineer_interface import service_engineer_interface
from models.Session import Session
from visual.text_colors import TextColors
from ui.prompts.field_prompts import input_password


t = TextColors

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def start_interface():
    while True:
        print("====== URBAN MOBILITY BACKEND SYSTEM ======")
        print(f"\n{t.blue}Please log in to continue.{t.end}")
        username = input("Username: ").strip()
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

            print(f"\n[INFO] Welcome, {username}! Role: {role}")

            if role == "super_admin":
                super_admin_interface(session)
            elif role == "system_admin":
                system_admin_interface()
            elif role == "service_engineer":
                service_engineer_interface()
            else:
                print(f"{t.red}[ERROR] Unknown role. Access denied.{t.end}")
        else:
            print(f"{t.red}[ERROR] Invalid credentials.{t.end}")

        again = input(f"\n{t.blue}Do you want to log in again? (Y/N): {t.end}").strip().lower()
        if again != 'y':
            print(f"{t.blue}[INFO] Exiting the system.{t.end}")
            break
