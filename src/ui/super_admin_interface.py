import sys, os
from services.SuperAdminService import SuperAdminService
from models.Session import Session
from ui.menu_utils import navigate_menu
import time


def super_admin_interface(session: Session):
    menu_options = ["User Operations", "Exit"]
    super_admin_service = SuperAdminService(session)

    while True:
        choice = navigate_menu(menu_options)
        if choice == "User Operations":
            user_menu(super_admin_service)
        elif choice == "Exit":
            break


def user_menu(user_service):
    menu_options = ["User List", "Add User", "Modify User", "Delete User", "Reset User Password", "Back"]

    while True:
        choice = navigate_menu(menu_options)

        if choice == "User List":
            menu_options = ["Back"]

            users_query_result = user_service.user_overview()
            if (users_query_result is not False):
                for user in users_query_result:
                    print(repr(user))

            time.sleep(5)

            choice = navigate_menu(menu_options)
            if choice == "Back":
                user_menu(user_service)
        if choice == "Back":
            super_admin_interface(user_service.session)
