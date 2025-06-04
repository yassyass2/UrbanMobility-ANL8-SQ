import msvcrt
from services.auth import authenticate_user, get_role
from ui.super_admin_interface import super_admin_interface
from ui.system_admin_interface import system_admin_interface
from ui.service_engineer_interface import service_engineer_interface
from models.Session import Session


def input_password(prompt="Password: "):
    print(prompt, end='', flush=True)
    password = ''
    while True:
        ch = msvcrt.getch()
        if ch in {b'\r', b'\n'}:
            print('')
            break
        elif ch == b'\x08':
            if len(password) > 0:
                password = password[:-1]
                print('\b \b', end='', flush=True)
        elif ch == b'\x03':
            raise KeyboardInterrupt
        elif ch in {b'\x00', b'\xe0'}:
            msvcrt.getch()
        elif ch == b'\x1b':
            print('\n[INFO] Exiting password input.')
            return None
        else:
            password += ch.decode('utf-8')
            print('*', end='', flush=True)
    return password


def start_interface():
    print("====== URBAN MOBILITY BACKEND SYSTEM ======")

    while True:
        print("\nPlease log in to continue.")
        username = input("Username: ").strip()
        password = input_password().strip()

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
                print("[ERROR] Unknown role. Access denied.")
        else:
            print("[ERROR] Invalid credentials.")

        again = input("\nDo you want to log in again? (Y/N): ").strip().lower()
        if again != 'y':
            print("[INFO] Exiting the system.")
            break
