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
            success = user_service.add_user(["system_admin", "service_engineer"], required_fields)
            flush_input()

            if success:
                print(f"User {required_fields['username']} added, role: {required_fields['role']}")
                print("\npress any key to return to menu...")
                msvcrt.getch()

        elif choice == "Delete User":
            clear()
            flush_input()
            users = user_service.user_overview()
            if users:
                print("====== DELETE A USER ======")
                for user in users:
                    if user.role != "super_admin":
                        print(repr(user))
                    id_to_delete = input("Enter ID of user to delete: ")
                # To do: delete functie aan Service toevoegen en hier aanroepen
            else:
                print("Access denied, login again as atleast a system admin!")

        elif choice == "Back":
            return
