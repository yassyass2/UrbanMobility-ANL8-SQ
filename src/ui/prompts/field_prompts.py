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
        print(Prompt)
        password = input_password()

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
