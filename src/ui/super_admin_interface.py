import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from menu_utils import navigate_menu

def super_admin_interface():
    menu_options = ["User Operations", "Exit"]

    while True:
        choice = navigate_menu(menu_options)
        if choice == "User Operations":
            user_menu()
        elif choice == "Exit":
            break

def user_menu():
    menu_options = ["User List", "Add User", "Modify User", "Delete User", "Reset User Password", "Back"]
    
    while True:
        choice = navigate_menu(menu_options)

        if choice == "User List":
            menu_options = ["Back"]
            print("User List")
            choice = navigate_menu(menu_options)
            if choice == "Back":
                user_menu()
        if choice == "Back":
            super_admin_interface()        
            

