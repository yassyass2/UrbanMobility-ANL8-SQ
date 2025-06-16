import sys
from services.SuperAdminService import SuperAdminService
from models.Session import Session
from ui.menu_utils import navigate_menu, flush_input, clear, click_to_return
from ui.prompts.user_prompts import *
from ui.prompts.scooter_prompts import *


def super_admin_interface(session: Session):
    menu_options = ["User Operations", "Account Settings", "Backups", "Traveller Operations", "Scooter Operations", "Exit"]
    super_admin_service = SuperAdminService(session)

    while True:
        choice = navigate_menu(menu_options)
        if choice == "User Operations":
            user_menu(super_admin_service)
        elif choice == "Account Settings":
            account_settings_menu(super_admin_service)
        elif choice == "Backups":
            backup_menu(super_admin_service)
        elif choice == "Traveller Operations":
            traveller_operations_menu(super_admin_service)
        elif choice == "Scooter Operations":
            scooter_operations_menu(super_admin_service)
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

        elif choice == "Reset User Password":
            id_to_reset = user_selection_screen(user_service, "RESET PASSWORD OF")
            temp_pass = prompt_password(Prompt=f"Enter a temporary password for User {id_to_reset}: ")
            user_service.reset_password(id_to_reset, ["system_admin", "service_engineer"], temp_pass)
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

def show_system_admins(user_service) -> int:
    clear()
    flush_input()
    users = user_service.user_overview()
    if users:
        print(f"====== SYSTEM ADMINS TO RECEIVE RESTORE CODE ======")
        for user in users:
            if user.role == "system_admin":
                print(repr(user))

    return get_valid_user_id(Prompt=f"Enter the admin ID to make a restore code for: ")

def account_settings_menu(super_admin_service):
    menu_options = ["Change Password", "Delete Account","Back"]
    
    while True:
        choice = navigate_menu(menu_options)
        
        if choice == "Change Password":
            clear()
            new_password = input("Enter new password: ").strip()
            if super_admin_service.change_password(new_password):
                print("Password changed successfully.")
            else:
                print("Failed to change password.")
            flush_input()
            click_to_return()

        elif choice == "Delete Account":
            clear()
            confirmation = input("Are you sure you want to delete your account? (yes/no): ").strip().lower()
            if confirmation == "yes":
                if super_admin_service.delete_account():
                    print("Account deleted successfully.")
                    sys.exit()
                else:
                    print("Failed to delete account.")
            else:
                print("Account deletion cancelled.")
            flush_input()
            click_to_return()

        elif choice == "Back":
            return

def backup_menu(super_admin_service):
    menu_options = ["Create Backup", "Restore Backup", "View Backups", "Generate Restore Code", "Back"]
    
    while True:
        choice = navigate_menu(menu_options)
        
        if choice == "Create Backup":
            clear()
            print(super_admin_service.create_backup()[1])
            flush_input()
            click_to_return()

        elif choice == "Restore Backup":
            clear()
            backups = super_admin_service.view_all_backups()
            if backups:
                print("Available Backups:")
                for i, backup in enumerate(backups):
                    print(f"Backup {i}. {backup}")
            else:
                print("No backups available.")
            flush_input()

            backup_id = get_valid_user_id(Prompt=f"Enter the Backup ID to restore (maximum of {len(backups)}): ")
            while backup_id > len(backups):
                backup_id = get_valid_user_id(Prompt=f"Enter the Backup ID to restore (maximum of {len(backups)}): ")

            print(super_admin_service.restore_backup_without_code(backups[backup_id-1])[1])
            flush_input()
            click_to_return()

        elif choice == "View Backups":
            clear()
            backups = super_admin_service.view_all_backups()
            if backups:
                print("Available Backups:")
                for i, backup in enumerate(backups):
                    print(f"Backup {i}. {backup}")
            else:
                print("No backups available.")
            flush_input()
            click_to_return()

        elif choice == "Generate Restore Code":
            clear()
            backups = super_admin_service.view_all_backups()
            if backups:
                print("Available Backups:")
                for i, backup in enumerate(backups):
                    print(f"Backup {i}. {backup}")
            else:
                print("No backups available.")
            flush_input()
            backup_id = get_valid_user_id(Prompt=f"Enter the Backup ID to make a restore code for (maximum of {len(backups)}): ")

            admin_id = show_system_admins(super_admin_service)
            print(super_admin_service.generate_restore_code(backups[backup_id-1], admin_id))

            click_to_return()
            flush_input()

        elif choice == "Back":
            return
        
def traveller_operations_menu(super_admin_service):
    menu_options = ["Add Traveller", "Update Traveller", "Delete Traveller", "View Travellers", "Back"]

    while True:
        choice = navigate_menu(menu_options)

        if choice == "Add Traveller":
            clear()
            traveller_data = super_admin_service.add_traveller()
            if traveller_data:
                print(f"Traveller added: {traveller_data}")
            else:
                print("Failed to add traveller.")
            flush_input()
            click_to_return()

        elif choice == "Update Traveller":
            clear()
            traveller_id = input("Enter Traveller ID to update: ").strip()
            updated_data = super_admin_service.update_traveller(traveller_id)
            if updated_data:
                print(f"Traveller updated: {updated_data}")
            else:
                print("Failed to update traveller.")
            flush_input()
            click_to_return()

        elif choice == "Delete Traveller":
            clear()
            traveller_id = input("Enter Traveller ID to delete: ").strip()
            if super_admin_service.delete_traveller(traveller_id):
                print("Traveller deleted successfully.")
            else:
                print("Failed to delete traveller.")
            flush_input()
            click_to_return()

        elif choice == "View Travellers":
            while True:
                menu_options = ["Search By ID", "Search By Last Name", "Back"]
                choice = navigate_menu(menu_options)

                if choice == "Search By ID":
                    clear()
                    flush_input()
                    traveller_id = input("Enter Traveller ID: ")
                    super_admin_service.view_travellers_by_id(traveller_id)
                    click_to_return()

                elif choice == "Search By Last Name":
                    clear()
                    flush_input()
                    traveller_name = input("Enter Traveller Last Name: ")
                    super_admin_service.view_travellers_by_last_name(traveller_name)
                    click_to_return()

                elif choice == "Back":
                        clear()
                        flush_input()
                        return

        elif choice == "Back":
            clear()
            flush_input()
            return

def scooter_operations_menu(super_admin_service):
    menu_options = ["Add Scooter" , "Update Scooter", "Delete Scooter", "Search Scooter", "Back"]

    while True:
        choice = navigate_menu(menu_options)

        if choice == "Add Scooter":
            clear()
            flush_input()
            scooter_data = prompt_new_scooter()
            if super_admin_service.add_scooter(scooter_data):
                print(f"Scooter added successfully: {scooter_data}")
            else:
                print("Failed to add scooter.")
            click_to_return()

        elif choice == "Update Scooter":
            clear()
            flush_input()
            scooter_id = input("Enter a scooter id to update: ")
            fields_to_update = prompt_update_scooter(scooter_id, super_admin_service.session.role)
            super_admin_service.update_scooter(scooter_id, fields_to_update)
            click_to_return()

        elif choice == "Delete Scooter":
            clear()
            flush_input()
            id_to_delete = input("Enter the ID of the scooter to delete: ").strip()
            del_result = super_admin_service.delete_scooter(id_to_delete)
            print(del_result)
            click_to_return()

        elif choice == "Search Scooter":
            while True:
                menu_options = ["Search By ID", "Search By Name", "Back"]
                choice = navigate_menu(menu_options)

                if choice == "Search By ID":
                    clear()
                    flush_input()
                    scooter_id = input("Enter scooter ID: ")
                    super_admin_service.search_scooter_by_id(scooter_id)
                    click_to_return()

                elif choice == "Search By Name":
                    clear()
                    flush_input()
                    scooter_name = input("Enter scooter Name: ")
                    super_admin_service.search_scooter_by_name(scooter_name)
                    click_to_return()

                elif choice == "Back":
                    clear()
                    flush_input()
                    return
                
        elif choice == "Back":
            clear()
            flush_input()
            return
