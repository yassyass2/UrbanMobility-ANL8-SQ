import sys
from services.ServiceEngineerService import ServiceEngineerService
from models.Session import Session
from ui.menu_utils import navigate_menu, flush_input, clear, click_to_return
from ui.prompts.scooter_prompts import *
from services.validation import is_valid_number


def service_engineer_interface(session: Session):
    menu_options = ["Update Password", "Update Scooters", "Search Scooter", "Exit"]
    service_engineer_service = ServiceEngineerService(session)

    while True:
        choice = navigate_menu(menu_options)
        if choice == "Update Password":
            clear()
            flush_input()
            service_engineer_service.update_password()
            click_to_return()

        elif choice == "Update Scooters":
            clear()
            flush_input()
            service_engineer_service.get_scooter_list()
            scooter_id = input("Enter a scooter id to update: ")

            if not is_valid_number(scooter_id):
                print("[ERROR] Invalid scooter ID. Must be a positive integer.")
                flush_input()
                click_to_return()
                return

            scooter = service_engineer_service.get_scooter_by_id(scooter_id)
            if not scooter:
                print(f"No scooter found with ID: {scooter_id}")
                flush_input()
                click_to_return()
                return
            
            fields_to_update = prompt_update_scooter(scooter_id, session.role)
            service_engineer_service.update_scooter(scooter_id, fields_to_update)
            click_to_return()


        elif choice == "Search Scooter":
            while True:
                menu_options_s = ["Search By ID", "Search By Brand", "Back"]
                choice = navigate_menu(menu_options_s)

                if choice == "Search By ID":
                    clear()
                    flush_input()
                    scooter_id = input("Enter scooter ID: ")
                    service_engineer_service.search_scooter_by_id(scooter_id)
                    click_to_return()

                elif choice == "Search By Brand":
                    clear()
                    flush_input()
                    scooter_brand = input("Enter scooter Brand: ")
                    
                    if not is_valid_name(scooter_brand):
                        print("[ERROR] Invalid scooter brand. Must be a non-empty string.")
                        flush_input()
                        click_to_return()
                        return
                    
                    service_engineer_service.search_scooter_by_brand(scooter_brand)
                    click_to_return()

                elif choice == "Back":
                    clear()
                    flush_input()
                    break

        elif choice == "Exit":
            flush_input()
            sys.exit()

