import sys, os
from services.SuperAdminService import SuperAdminService
from models.Session import Session
from ui.menu_utils import navigate_menu
from ui.menu_utils import flush_input
from ui.menu_utils import clear
import msvcrt


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

        elif choice == "Back":
            return
