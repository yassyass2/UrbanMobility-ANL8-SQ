import sys
from services.SystemAdminService import SystemAdminService
from models.Session import Session
from ui.menu_utils import navigate_menu, flush_input, clear, click_to_return
from services.validation import *
from ui.prompts.scooter_prompts import prompt_new_scooter, prompt_update_scooter
from ui.menu_utils import navigate_menu, flush_input, clear, click_to_return
from ui.prompts.user_prompts import *
from logger import *


def system_admin_interface(session: Session):
    menu_options = ["User Operations", "Account Settings", "Backups", "Traveller Operations", "Scooter Operations", "View All Logs", "View Unviewed Logs", "Exit"]
    system_admin_service = SystemAdminService(session)

    while True:
        choice = navigate_menu(menu_options)
        if choice == "User Operations":
            user_menu(system_admin_service)
        elif choice == "Account Settings":
            account_settings_menu(system_admin_service)
        elif choice == "Backups":
            backup_menu(system_admin_service)
        elif choice == "Traveller Operations":
            traveller_operations_menu(system_admin_service)
        elif choice == "Scooter Operations":
            scooter_operations_menu(system_admin_service)
        elif choice == "View All Logs":
            view_logs(session)
            flush_input()
            click_to_return()
        elif choice == "View Unviewed Logs":
            view_logs(session, only_unviewed=True)
            flush_input()
            click_to_return()
        else:
            flush_input()
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
            required_fields = prompt_new_user(["service_engineer"])
            success = user_service.add_user(["service_engineer"], required_fields)
            flush_input()

            if success:
                print(f"User {required_fields['username']} added, role: {required_fields['role']}")
                click_to_return()
            else:
                print("Access denied, login again as atleast a system admin!")

        elif choice == "Delete User":
                id_to_delete = user_selection_screen(user_service, "DELETE")
                del_result = user_service.delete_user(["service_engineer"], id_to_delete)
                print(del_result)
                click_to_return()

        elif choice == "Modify User":
            id_to_update = user_selection_screen(user_service, "MODIFY")
            fields_to_update = prompt_update_user(id_to_update, ["service_engineer"])
            print(user_service.update_user(id_to_update, fields_to_update))
            click_to_return()

        elif choice == "Reset User Password":
            id_to_reset = user_selection_screen(user_service, "RESET PASSWORD OF")
            temp_pass = prompt_password(Prompt=f"Enter a temporary password for User {id_to_reset}: ")
            user_service.reset_password(id_to_reset, ["service_engineer"], temp_pass)
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
            if user.role == "service_engineer":
                print(repr(user))

    return get_valid_user_id()

def account_settings_menu(system_admin_service):
    menu_options = ["Update Password", "Delete Account", "Back"]
    
    while True:
        choice = navigate_menu(menu_options)
        
        if choice == "Update Password":
            clear()
            flush_input()
            system_admin_service.update_password()
            flush_input()
            click_to_return()

        elif choice == "Delete Account":
            clear()
            flush_input()
            system_admin_service.delete_account()
            flush_input()
            click_to_return()

        elif choice == "Back":
            return

def backup_menu(system_admin_service):
    menu_options = ["Create Backup", "Restore Backup", "View Backups", "Back"]
    
    while True:
        choice = navigate_menu(menu_options)
        
        if choice == "Create Backup":
            clear()
            print(system_admin_service.create_backup()[1])
            flush_input()
            click_to_return()

        elif choice == "Restore Backup":
            clear()
            if not system_admin_service.view_restore_codes():
                click_to_return()
                continue

            restore_record = validate_restore_code(system_admin_service.session.user)
            if restore_record:
                system_admin_service.restore_backup_with_code(restore_record)
                print(f"Backup {restore_record[1]} Restored, code {restore_record[0]} No longer usable")

            flush_input()
            click_to_return()

        elif choice == "View Backups":
            clear()
            backups = system_admin_service.view_all_backups()
            if backups:
                if "Fail" in backups:
                    print(backups)
                else:
                    print("Available Backups:")
                    for backup in backups:
                        print(backup)
            else:
                print("No backups available.")
            flush_input()
            click_to_return()

        elif choice == "Back":
            return
        
def traveller_operations_menu(system_admin_service):
    menu_options = ["Add Traveller", "Update Traveller", "Delete Traveller", "View Travellers", "Back"]

    while True:
        choice = navigate_menu(menu_options)

        if choice == "Add Traveller":
            clear()
            flush_input()
            system_admin_service.add_traveller()
            click_to_return()

        elif choice == "Update Traveller":
            clear()
            flush_input()
            system_admin_service.update_traveller()
            click_to_return()

        elif choice == "Delete Traveller":
            clear()
            flush_input()
            system_admin_service.delete_traveller()
            click_to_return()


        elif choice == "View Travellers":
            while True:
                menu_options = ["Search By ID", "Search By Last Name", "Back"]
                choice = navigate_menu(menu_options)

                if choice == "Search By ID":
                    clear()
                    flush_input()
                    traveller_id = input("Enter Traveller ID: ")
                    system_admin_service.view_travellers_by_id(traveller_id)
                    click_to_return()

                elif choice == "Search By Last Name":
                    clear()
                    flush_input()
                    traveller_name = input("Enter Traveller Last Name: ")
                    system_admin_service.view_travellers_by_last_name(traveller_name)
                    click_to_return()

                elif choice == "Back":
                        clear()
                        flush_input()
                        return

        elif choice == "Back":
            clear()
            flush_input()
            return
        
def scooter_operations_menu(system_admin_service):
    menu_options = ["Add Scooter" , "Update Scooter", "Delete Scooter", "Search Scooter", "Back"]

    while True:
        choice = navigate_menu(menu_options)

        if choice == "Add Scooter":
            clear()
            flush_input()
            scooter_data = prompt_new_scooter()
            if system_admin_service.add_scooter(scooter_data):
                print(f"Scooter added successfully: {scooter_data}")
            else:
                print("Failed to add scooter.")
            click_to_return()

        elif choice == "Update Scooter":
            clear()
            flush_input()
            scooter_id = input("Enter a scooter id to update: ")
            fields_to_update = prompt_update_scooter(scooter_id, system_admin_service.session.role)
            system_admin_service.update_scooter(scooter_id, fields_to_update)
            click_to_return()

        elif choice == "Delete Scooter":
            clear()
            flush_input()
            system_admin_service.delete_scooter()
            click_to_return()
            
        elif choice == "Search Scooter":
            while True:
                menu_options = ["Search By ID", "Search By Name", "Back"]
                choice = navigate_menu(menu_options)

                if choice == "Search By ID":
                    clear()
                    flush_input()
                    scooter_id = input("Enter scooter ID: ")
                    system_admin_service.search_scooter_by_id(scooter_id)
                    click_to_return()

                elif choice == "Search By Name":
                    clear()
                    flush_input()
                    scooter_name = input("Enter scooter Name: ")
                    system_admin_service.search_scooter_by_name(scooter_name)
                    click_to_return()

                elif choice == "Back":
                    clear()
                    flush_input()
                    return
        elif choice == "Back":
            clear()
            flush_input()
            return
                