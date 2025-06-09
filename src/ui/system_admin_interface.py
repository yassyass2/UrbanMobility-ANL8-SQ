import sys
from services.SystemAdminService import SystemAdminService
from models.Session import Session
from ui.menu_utils import navigate_menu, flush_input, clear, click_to_return
from ui.super_admin_interface import user_menu



def system_admin_interface(session: Session):
    menu_options = ["User Operations", "Account Settings", "Backups", "Traveler Operations", "Scooter Operations", "Exit"]
    system_admin_service = SystemAdminService(session)

    while True:
        choice = navigate_menu(menu_options)
        if choice == "User Operations":
            user_menu(system_admin_service)
        elif choice == "Account Settings":
            account_settings_menu(system_admin_service)
        elif choice == "Backups":
            backup_menu(system_admin_service)
        elif choice == "Traveler Operations":
            traveler_operations_menu(system_admin_service)
        elif choice == "Scooter Operations":
            scooter_operations_menu(system_admin_service)
        else:
            sys.exit()

def account_settings_menu(system_admin_service):
    menu_options = ["Change Password", "Delete Account","Back"]
    
    while True:
        choice = navigate_menu(menu_options)
        
        if choice == "Change Password":
            clear()
            new_password = input("Enter new password: ").strip()
            if system_admin_service.change_password(new_password):
                print("Password changed successfully.")
            else:
                print("Failed to change password.")
            flush_input()
            click_to_return()

        elif choice == "Delete Account":
            clear()
            confirmation = input("Are you sure you want to delete your account? (yes/no): ").strip().lower()
            if confirmation == "yes":
                if system_admin_service.delete_account():
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

def backup_menu(system_admin_service):
    menu_options = ["Create Backup", "Restore Backup", "View Backups", "Back"]
    
    while True:
        choice = navigate_menu(menu_options)
        
        if choice == "Create Backup":
            clear()
            if system_admin_service.create_backup():
                print("Backup created successfully.")
            else:
                print("Failed to create backup.")
            flush_input()
            click_to_return()

        elif choice == "Restore Backup":
            clear()
            backup_id = input("Enter the ID of the backup to restore: ").strip()
            if system_admin_service.restore_backup(backup_id):
                print("Backup restored successfully.")
            else:
                print("Failed to restore backup.")
            flush_input()
            click_to_return()

        elif choice == "View Backups":
            clear()
            backups = system_admin_service.view_backups()
            if backups:
                print("Available Backups:")
                for backup in backups:
                    print(backup)
            else:
                print("No backups available.")
            flush_input()
            click_to_return()

        elif choice == "Back":
            return
        
def traveler_operations_menu(system_admin_service):
    menu_options = ["Add Traveler", "Update Traveler", "Delete Traveler", "View Travelers", "Back"]

    while True:
        choice = navigate_menu(menu_options)

        if choice == "Add Traveler":
            clear()
            traveler_data = system_admin_service.add_traveler()
            if traveler_data:
                print(f"Traveler added: {traveler_data}")
            else:
                print("Failed to add traveler.")
            flush_input()
            click_to_return()

        elif choice == "Update Traveler":
            clear()
            traveler_id = input("Enter Traveler ID to update: ").strip()
            updated_data = system_admin_service.update_traveler(traveler_id)
            if updated_data:
                print(f"Traveler updated: {updated_data}")
            else:
                print("Failed to update traveler.")
            flush_input()
            click_to_return()

        elif choice == "Delete Traveler":
            clear()
            traveler_id = input("Enter Traveler ID to delete: ").strip()
            if system_admin_service.delete_traveler(traveler_id):
                print("Traveler deleted successfully.")
            else:
                print("Failed to delete traveler.")
            flush_input()
            click_to_return()

        elif choice == "View Travelers":
            clear()
            travelers = system_admin_service.view_travelers()
            if travelers:
                print("Travelers List:")
                for traveler in travelers:
                    print(traveler)
            else:
                print("No travelers found.")
            flush_input()
            click_to_return()

        elif choice == "Back":
            return