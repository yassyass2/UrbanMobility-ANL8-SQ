import sys, os
import msvcrt
from services.SuperAdminService import SuperAdminService
from models.Session import Session
from ui.menu_utils import navigate_menu, flush_input, clear
from ui.prompts.user_prompts import prompt_new_user


def super_admin_interface(session: Session):
    menu_options = ["User Operations", "Exit"]
    super_admin_service = SuperAdminService(session)

    while True:
        choice = navigate_menu(menu_options)
        if choice == "User Operations":
            user_menu(super_admin_service)
        elif choice == "Exit":
            sys.exit()


def user_menu(user_service):
    menu_options = ["User List", "Add User", "Modify User", "Delete User", "Reset User Password", "Back"]

    while True:
        choice = navigate_menu(menu_options)

        if choice == "User List":
            clear()
            users = user_service.user_overview()
            if users:
                print("====== USER LIST ======")
                for user in users:
                    print(repr(user))
            else:
                print("Access denied, login again as atleast a system admin!")

            flush_input()
            print("\npress any key to return to menu...")
            msvcrt.getch()

        elif choice == "Add User":
            required_fields = prompt_new_user(["system_admin", "service_engineer"])
            success = user_service.Add_user(["system_admin", "service_engineer"], required_fields)

        elif choice == "Back":
            return
