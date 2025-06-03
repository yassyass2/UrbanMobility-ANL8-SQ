import os
import bcrypt
from ..services.auth import authenticate_user, get_role
from . import super_admin_interface
from . import system_admin_interface
from . import service_engineer_interface

clear = lambda: os.system('cls' if os.name == 'nt' else 'clear')

def login_interface():
    print(""".-------------------------------------------------------.
|                                                       |
|  __  __    _    ___ _   _   __  __ _____ _   _ _   _  |
| |  \/  |  / \  |_ _| \ | | |  \/  | ____| \ | | | | | |
| | |\/| | / _ \  | ||  \| | | |\/| |  _| |  \| | | | | |
| | |  | |/ ___ \ | || |\  | | |  | | |___| |\  | |_| | |
| |_|  |_/_/   \_\___|_| \_| |_|  |_|_____|_| \_|\___/  |
|                                                       |
'-------------------------------------------------------'""")

    while True:
        print("Choose what you want to do:")
        print("1. Log in")
        print("2. Register")
        print("3. Exit")
        choice = input("Enter your choice (1/2/3): ").strip().lower()
        if choice == '1' or choice == 'log in' or choice == 'login':
            login()
        elif choice == '2' or choice == 'register':
            register()
        elif choice == '3' or choice == 'exit':
            exit()
        else:
            print("[ERROR] Invalid choice. Please try again.")
        clear()

def login():
    while True:
        print(""".------------------------------.
|                              |
|  _     ___   ____ ___ _   _  |
| | |   / _ \ / ___|_ _| \ | | |
| | |  | | | | |  _ | ||  \| | |
| | |__| |_| | |_| || || |\  | |
| |_____\___/ \____|___|_| \_| |
|                              |
'------------------------------'""")
        username = input("Username: ").strip()
        password = input("Password: ").strip()

        if authenticate_user(username, password):
            role = get_role(username)

            print(f"\n[INFO] Welcome, {username}! Role: {role}")

            if role == "super_admin":
                super_admin_interface.super_admin_interface(username)
            elif role == "system_admin":
                system_admin_interface.system_admin_interface(username)
            elif role == "service_engineer":
                service_engineer_interface.service_engineer_interface(username)
            else:
                print("[ERROR] Unknown role. Access denied.")
        else:
            print("[ERROR] Invalid credentials.")

        again = input("\nDo you want to log in again? (Y/N): ").strip().lower()
        if again != 'y':
            print("[INFO] Exiting the system.")
            break

def register():
    print("not implemented yet")
    
    pass

def exit():
    print("[INFO] Exiting the system. Goodbye!")
    raise SystemExit(0)