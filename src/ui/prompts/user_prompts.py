from ui.menu_utils import clear, flush_input
from ui.prompts.field_prompts import *


def prompt_new_user(role_options: list):
    # Role options is wie je mag toevoegen
    # Hangt af van welke rol de gebruiker zelf heeft

    clear()
    print("=== ADD NEW USER ===")

    username = prompt_username()
    password = prompt_password()
    role = prompt_role(role_options)
    first_name = prompt_first_name()
    last_name = prompt_last_name()

    return {
        "username": username,
        "password": password,
        "role": role,
        "first_name": first_name,
        "last_name": last_name
    }


def prompt_update_user(id, role_options):
    fields = ["First Name", "Last Name", "Role", "Username"]
    print(f"Update fields for user {id}: \n")
    for i, field in enumerate(fields, 1):
        print(f"{i}. {field}")

    numbers_csv = input("Enter number(s) of fields to update (comma-separated): ").strip()
    while not is_valid_number_selection(numbers_csv):
        print(f"Update fields for user: \n")
        for i, field in enumerate(fields, 1):
            print(f"{i}. {field}")
        numbers_csv = input("Invalid format for fields to update. input numbers seperated by , like (1,2,3)")
    
    updates = {}
    if "1" in numbers_csv:
        updates["first_name"] = prompt_first_name("Enter new First name: ")
    if "2" in numbers_csv:
        updates["last_name"] = prompt_last_name("Enter new Last name: ")
    if "3" in numbers_csv:
        updates["role"] = prompt_role(role_options, "Enter the new  role (service_engineer / system_admin): ")
    if "4" in numbers_csv:
        updates["username"] = prompt_username("Enter new username: ")

    return updates

def prompt_update_self(id):
    fields = ["First Name", "Last Name", "Username"]
    print(f"Update fields for your profile: \n")
    for i, field in enumerate(fields, 1):
        print(f"{i}. {field}")

    numbers_csv = input("Enter number(s) of fields to update (comma-separated): ").strip()
    while not is_valid_number_selection(numbers_csv):
        print(f"Update fields for user: \n")
        for i, field in enumerate(fields, 1):
            print(f"{i}. {field}")
        numbers_csv = input("Invalid format for fields to update. input numbers seperated by, like (1,2,3): ")
    
    updates = {}
    if "1" in numbers_csv:
        updates["first_name"] = prompt_first_name("Enter new First name: ")
    if "2" in numbers_csv:
        updates["last_name"] = prompt_last_name("Enter new Last name: ")
    if "3" in numbers_csv:
        updates["username"] = prompt_username("Enter new username: ")
    if "1" not in numbers_csv and "2" not in numbers_csv and "3" not in numbers_csv:
        print("No fields selected for update.")
        click_to_return()
        return None
    return updates


def is_valid_number_selection(numbers: str) -> list:
    numbers = numbers.strip()

    if not numbers:
        return None

    parts = [part.strip() for part in numbers.split(',')]

    if all(part.isdigit() for part in parts):
        return parts
    else:
        return None
    

def get_valid_user_id(Prompt="\nEnter the ID of the user: "):
    while True:
        user_input = input(Prompt).strip()

        if not user_input.isdigit():
            print("Invalid input. Please enter a numeric ID.")
            continue

        user_id = int(user_input)

        if user_id <= 0:
            print("ID must be greater than 0.")
            continue

        return user_id
    

def get_valid_admin_id(admins, Prompt="\nEnter the ID of the admin: "):
    while True:
        user_input = input(Prompt).strip()

        if not user_input.isdigit():
            print("Invalid input. Please enter a numeric ID.")
            continue

        user_id = int(user_input)

        if user_id <= 0:
            print("ID must be greater than 0.")
            continue
        
        if not any(admin.id == user_id for admin in admins):
            print(f"There is no admin with ID {user_id}")
            continue

        return user_id