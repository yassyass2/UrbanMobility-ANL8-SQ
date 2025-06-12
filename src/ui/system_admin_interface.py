import sys
from services.SystemAdminService import SystemAdminService
from services.ServiceEngineerService import ServiceEngineerService
from models.Session import Session
from ui.menu_utils import navigate_menu, flush_input, clear, click_to_return
from ui.super_admin_interface import user_menu
from services.validation import (
                is_valid_name, is_valid_birthday, is_valid_gender,
                is_valid_street, is_valid_house_number, is_valid_zip,
                is_valid_mobile, is_valid_license, is_valid_city, is_valid_email_and_domain
            )



def system_admin_interface(session: Session):
    menu_options = ["User Operations", "Account Settings", "Backups", "Traveller Operations", "Scooter Operations", "Exit"]
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
        else:
            sys.exit()

def account_settings_menu(system_admin_service):
    menu_options = ["Change Password", "Delete Account", "Update Password", "Back"]
    
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
        
        elif choice == "Update Password":
            clear()
            flush_input()
            new_password = system_admin_service.update_password()
            if new_password:
                print(f"Password updated successfully to: {new_password}")
            else:
                print("Failed to update password.")
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
        
def traveller_operations_menu(system_admin_service):
    menu_options = ["Add Traveller", "Update Traveller", "Delete Traveller", "View Travellers", "Back"]

    while True:
        choice = navigate_menu(menu_options)

        if choice == "Add Traveller":
            clear()
            flush_input()
            print("====== Add New Traveller ======")

            cities = ["Rotterdam", "Delft", "Schiedam", "The Hague", "Leiden",
                      "Gouda", "Zoetermeer", "Spijkenisse", "Vlaardingen", "Barendrecht"]

            try:
                while True:
                    first_name = input("First name: ").strip()
                    if is_valid_name(first_name): break
                    print("Invalid first name.")

                while True:
                    last_name = input("Last name: ").strip()
                    if is_valid_name(last_name): break
                    print("Invalid last name.")

                while True:
                    birthday = input("Birthday (YYYY-MM-DD): ").strip()
                    if is_valid_birthday(birthday): break
                    print("Invalid birthday. Use YYYY-MM-DD and must be in the past.")

                while True:
                    gender = input("Gender (male/female): ").strip().lower()
                    if is_valid_gender(gender): break
                    print("Gender must be 'male' or 'female'.")

                while True:
                    street = input("Street: ").strip()
                    if is_valid_street(street): break
                    print("Street must contain only letters and spaces.")

                while True:
                    house_number_input = input("House number: ").strip()
                    if is_valid_house_number(house_number_input):
                        house_number = int(house_number_input)
                        break
                    print("Invalid house number.")

                while True:
                    zip_code = input("Zip Code (e.g. 1234AB): ").strip().upper()
                    if is_valid_zip(zip_code): break
                    print("Invalid zip code format.")

                while True:
                    for i, c in enumerate(cities, start=1):
                        print(f"{i}. {c}")
                    selected = input("Choose city number (1-10): ").strip()
                    if selected.isdigit() and is_valid_city(cities[int(selected)-1], cities):
                        city = cities[int(selected)-1]
                        break
                    print("Invalid city selection.")

                while True:
                    email = input("E-mail (e.g. example@gmail.com): ").strip()
                    if is_valid_email_and_domain(email):
                        break
                    else:
                        print("Email already exists. Please use a different email.")


                while True:
                    mobile = input("Mobile number (8 digits only): +31-6-").strip()
                    if is_valid_mobile(mobile): break
                    print("Mobile must be exactly 8 digits.")

                while True:
                    license_number = input("Driving license (e.g. 1234567890): ").strip().upper()
                    if is_valid_license(license_number): break
                    print("Invalid license number format.")

                traveler_data = {
                    "first_name": first_name,
                    "last_name": last_name,
                    "birthday": birthday,
                    "gender": gender,
                    "street": street,
                    "house_number": house_number,
                    "zip_code": zip_code,
                    "city": city,
                    "email": email,
                    "mobile": mobile,
                    "license_number": license_number
                }

                result = system_admin_service.add_traveller(traveler_data)
                print(result)

            except Exception as e:
                print(f"[ERROR] Unexpected input error: {e}")

            flush_input()
            click_to_return()

        elif choice == "Update Traveller":
            clear()
            traveller_id = input("Enter Traveller ID to update: ").strip()
            updated_data = system_admin_service.update_traveller(traveller_id)
            if updated_data:
                print(f"Traveller updated: {updated_data}")
            else:
                print("Failed to update traveller.")
            flush_input()
            click_to_return()

        elif choice == "Delete Traveller":
            clear()
            traveller_id = input("Enter Traveller ID to delete: ").strip()
            if system_admin_service.delete_traveller(traveller_id):
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
            system_admin_service.add_scooter()
        elif choice == "Update Scooter":
            system_admin_service.update_scooter()
        elif choice == "Delete Scooter":
            system_admin_service.delete_scooter()
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
                