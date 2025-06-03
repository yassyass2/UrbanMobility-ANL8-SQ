import getpass
from auth import authenticate_user, get_role
import super_admin_interface
import system_admin_interface
import service_engineer_interface


def start_interface():
    print("====== URBAN MOBILITY BACKEND SYSTEM ======")

    while True:
        print("\nPlease log in to continue.")
        username = input("Username: ").strip()
        password = getpass.getpass("Password: ").strip()

        if authenticate_user(username, password):
            role = get_role(username)

            print(f"\n[INFO] Welcome, {username}! Role: {role}")

            if role == "super_admin":
                super_admin_interface(username)
            elif role == "system_admin":
                system_admin_interface(username)
            elif role == "service_engineer":
                service_engineer_interface(username)
            else:
                print("[ERROR] Unknown role. Access denied.")
        else:
            print("[ERROR] Invalid credentials.")

        again = input("\nDo you want to log in again? (Y/N): ").strip().lower()
        if again != 'y':
            print("[INFO] Exiting the system.")
            break
