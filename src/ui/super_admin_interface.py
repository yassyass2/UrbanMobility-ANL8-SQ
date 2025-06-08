import sys, os
import msvcrt
from services.SuperAdminService import SuperAdminService
from models.Session import Session
from ui.menu_utils import navigate_menu, flush_input, clear, click_to_return
from ui.prompts.user_prompts import prompt_new_user, get_valid_user_id


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
            clear()
            flush_input()
            users = user_service.user_overview()
            if users:
                print("====== DELETE A USER ======")
                for user in users:
                    if user.role != "super_admin":
                        print(repr(user))
                id_to_delete = get_valid_user_id()

                # delete functie geeft 2 waardes terug
                # 1: Of het succesvol was
                # 2: De reden dat het niet lukte
                del_result = user_service.delete_user(["system_admin", "service_engineer"], id_to_delete)
                if del_result[0]:
                    print(f"user {id_to_delete} Deleted")
                    click_to_return()
                else:
                    print(del_result[1])
                    click_to_return()

        elif choice == "Back":
            return
