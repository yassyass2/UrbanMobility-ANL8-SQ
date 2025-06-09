import sys
from services.SuperAdminService import SuperAdminService
from models.Session import Session
from ui.menu_utils import navigate_menu, flush_input, clear, click_to_return
from ui.prompts.user_prompts import *


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
            click_to_return()

        elif choice == "Add User":
            required_fields = prompt_new_user(["system_admin", "service_engineer"])
            success = user_service.add_user(["system_admin", "service_engineer"], required_fields)
            flush_input()

            if success:
                print(f"User {required_fields['username']} added, role: {required_fields['role']}")
                click_to_return()
            else:
                print("Access denied, login again as atleast a system admin!")

        elif choice == "Delete User":
                id_to_delete = user_selection_screen(user_service, "DELETE")
                del_result = user_service.delete_user(["system_admin", "service_engineer"], id_to_delete)
                print(del_result)
                click_to_return()

        elif choice == "Modify User":
            id_to_update = user_selection_screen(user_service, "MODIFY")
            fields_to_update = prompt_update_user(id_to_update, ["system_admin", "service_engineer"])
            print(user_service.update_user(id_to_update, fields_to_update))
            click_to_return()

        elif choice == "Back":
            return


def user_selection_screen(user_service, action: str) -> int:
    clear()
    flush_input()
    users = user_service.user_overview()
    if users:
        print(f"====== {action} A USER ======")
        for user in users:
            if user.role != "super_admin":
                print(repr(user))

    return get_valid_user_id()
