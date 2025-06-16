import sys
import services.ServiceEngineerService as ServiceEngineerService
from models.Session import Session
from ui.menu_utils import navigate_menu, flush_input, clear, click_to_return
from ui.prompts.scooter_prompts import *



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
            scooter_id = input("Enter a scooter id to update: ")
            fields_to_update = prompt_update_scooter(scooter_id, session.role)
            service_engineer_service.update_scooter(scooter_id, fields_to_update)
            click_to_return()


        elif choice == "Search Scooter":
            while True:
                menu_options = ["Search By ID", "Search By Name", "Back"]
                choice = navigate_menu(menu_options)

                if choice == "Search By ID":
                    clear()
                    flush_input()
                    scooter_id = input("Enter scooter ID: ")
                    service_engineer_service.search_scooter_by_id(scooter_id)
                    click_to_return()

                elif choice == "Search By Name":
                    clear()
                    flush_input()
                    scooter_name = input("Enter scooter Name: ")
                    service_engineer_service.search_scooter_by_name(scooter_name)
                    click_to_return()

                elif choice == "Back":
                    clear();
                    flush_input()
                    return

        elif choice == "Exit":
            sys.exit()

