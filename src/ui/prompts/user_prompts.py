from services.validation import is_valid_username, is_valid_name, is_valid_password
from services.auth import get_role
from ui.menu_utils import clear, flush_input


def prompt_new_user(role_options: list):
    # Role options is wie je mag toevoegen
    # Hangt af van welke rol de gebruiker zelf heeft

    clear()
    print("=== ADD NEW USER ===")
    while True:
        flush_input()
        username = input("Enter username (8-10 chars, starts with letter or '_'): ").strip().lower()
        if not is_valid_username(username):
            print("Invalid username format.")
            continue
        if get_role(username):
            print("Username already exists.")
            continue
        break

    while True:
        print("Password rules: between 12 and 30 chars, atleast 1 lowercase, uppercase, number and symbol")
        password = input("Enter password: ")

        if is_valid_password(password):
            break
        print("Invalid password format.")

    while True:
        role = input("Enter role (service_engineer / system_admin / super_admin): ").strip().lower()
        if role not in role_options:
            print(f"You don't have permissions to add user of role {role}")
            continue
        break

    first_correct, last_correct = False, False
    while not first_correct and not last_correct:
        if not first_correct:
            first_name = input("Enter first name: ")
            if is_valid_name(first_name):
                first_correct = True
            else:
                print("Invalid format, only letters or ('.-) allowed, max 30")
                continue

        if not last_correct:
            last_name = input("Enter last name: ")
            if is_valid_name(last_name):
                last_correct = True
            else:
                print("Invalid format, only letters or ('.-) allowed, max 30")
                continue
    
    return {
        "username": username,
        "password": password,
        "role": role,
        "first_name": first_name,
        "last_name": last_name
    }


def get_valid_user_id():
    while True:
        user_input = input("\nEnter the ID of the user to delete: ").strip()

        if not user_input.isdigit():
            print("Invalid input. Please enter a numeric user ID.")
            continue

        user_id = int(user_input)

        if user_id <= 0:
            print("User ID must be greater than 0.")
            continue

        return user_id
