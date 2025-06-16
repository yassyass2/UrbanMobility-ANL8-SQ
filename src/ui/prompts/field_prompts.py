import msvcrt
from services.auth import authenticate_user, get_role
from visual.text_colors import TextColors
from services.validation import *
from ui.menu_utils import *


def input_password(prompt="Password: "):
    print(prompt, end='', flush=True)
    password = ''
    while True:
        ch = msvcrt.getch()
        if ch in {b'\r', b'\n'}:
            print('')
            break
        elif ch == b'\x08': # Backspace
            if len(password) > 0:
                password = password[:-1]
                print('\b \b', end='', flush=True)
        elif ch == b'\x03': # Ctrl+C
            raise KeyboardInterrupt
        elif ch in {b'\x00', b'\xe0'}: # Special keys (like arrows)
            msvcrt.getch()
        elif ch in {b'\x1b'}: # Escape key
            print(f'\n{t.red}[INFO] Exiting password input.{t.end}')
            return None
        else:
            password += ch.decode('utf-8')
            print('*', end='', flush=True)
    return password


def prompt_username(Prompt = "Enter username (8-10 chars, starts with letter or '_'): "):
    while True:
        flush_input()
        username = input(Prompt).strip().lower()
        if not is_valid_username(username):
            print("Invalid username format.")
            continue
        if get_role(username):
            print("Username already exists.")
            continue
        return username


def prompt_password(Prompt= "Enter a password: "):
    while True:
        print("Password rules: between 12 and 30 chars, atleast 1 lowercase, uppercase, number and symbol")
        password = input_password(prompt=Prompt)

        if is_valid_password(password):
            return password
        print("Invalid password format.")


def prompt_role(roles, Prompt = "Enter role (service_engineer / system_admin / super_admin): "):
    while True:
        role = input(Prompt).strip().lower()
        if role not in roles:
            print(f"You don't have permissions to choose Role {role}")
            continue
        return role
    

def prompt_first_name(Prompt = "Enter a First name: "):
    while True:
        first_name = input(Prompt).strip()
        if is_valid_name(first_name):
            return first_name
        print("Invalid format, only letters or ('.-) allowed, max 30")


def prompt_last_name(Prompt = "Enter a Last name: "):
    while True:
        last_name = input(Prompt).strip()
        if is_valid_name(last_name):
            return last_name
        print("Invalid format, only letters or ('.-) allowed, max 30")

def prompt_brand(Prompt = "Enter a Brand: "):
    while True:
        brand = input(Prompt).strip()
        if is_valid_name(brand):
            return brand
        print("Invalid Brand name")

def prompt_model(Prompt = "Enter a Model: "):
    while True:
        model = input(Prompt).strip()
        if is_valid_name(model):
            return model
        print("Invalid Model name")

def prompt_serial_number(Prompt = "Enter a Serial Number: "):
    while True:
        serial_number = input(Prompt).strip()
        if is_valid_serial_number(serial_number):
            return serial_number
        print("Invalid Serial Number")

def prompt_top_speed(Prompt = "Enter a Top Speed: "):
    while True:
        top_speed = input(Prompt).strip()
        if is_valid_number(top_speed):
            return top_speed
        print("Invalid Top Speed")

def prompt_capacity(Prompt = "Enter a Capacity: "):
    while True:
        capacity = input(Prompt).strip()
        if is_valid_number(capacity):
            return capacity
        print("Invalid Capacity")

def prompt_soc(Prompt = "Enter a State of Capacity: "):
    while True:
        soc = input(Prompt).strip()
        if is_valid_number(soc):
            return soc
        print("Invalid State of Capacity")

def prompt_target_range_soc(Prompt = "Enter a Target Range State of Capacity: "):
    while True:
        target_range_soc = input(Prompt).strip()
        if is_valid_number(target_range_soc):
            return target_range_soc
        print("Invalid Target Range State of Capacity")

def prompt_location(Prompt = "Enter a Location: "):
    cities = [
        "Rotterdam", "Delft", "Schiedam", "The Hague", "Leiden",
        "Gouda", "Zoetermeer", "Spijkenisse", "Vlaardingen", "Barendrecht"
    ]
    while True:
        print("Choose one of the following cities: " + ", ".join(cities))
        location = input(Prompt).strip()
        if location in cities:
            return location
        print("Invalid location. Please choose from the listed cities.")

def prompt_out_of_service(Prompt="Choose a State of Service (In Service/Out of Service): "):
    state_of_service = {"in service": 0, "out of service": 1}
    while True:
        choice = input(Prompt).strip().lower()
        if choice in state_of_service:
            return state_of_service[choice]
        print("Invalid input. Please enter 'In Service' or 'Out of Service'.")

def prompt_mileage(Prompt = "Choose a Mileage: "):
    while True:
        mileage = input(Prompt).strip()
        if is_valid_number(mileage):
            return mileage
        print("Invalid Mileage")

def prompt_last_maintenance(Prompt = "Choose Last Maintance date (yyyy-mm-dd): "):
    while True:
        last_maintenance = input(Prompt).strip()
        if is_valid_date_iso_8601(last_maintenance):
            return last_maintenance
        print("Invalid Last Maintance Date")