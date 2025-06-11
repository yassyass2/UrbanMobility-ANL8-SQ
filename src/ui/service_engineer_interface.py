import sys
import services.ServiceEngineerService as ServiceEngineerService
from models.Session import Session
from ui.menu_utils import navigate_menu, flush_input, clear, click_to_return



def service_engineer_interface(session: Session):
    menu_options = ["Update Password", "Update Scooters", "Search Scooter", "Exit"]
    service_engineer_service = ServiceEngineerService.ServiceEngineerService(session)

    while True:
        choice = navigate_menu(menu_options)
        if choice == "Update Password":
            clear()
            flush_input()
            new_password = service_engineer_service.update_password()
            if new_password:
                print(f"Password updated successfully to: {new_password}")
            else:
                print("Failed to update password.")
            click_to_return()


        elif choice == "Update Scooters":
            clear()
            flush_input()
            scooter_id = input("Enter scooter ID to update: ")
            service_engineer_service.update_scooter(scooter_id)
            click_to_return()


        elif choice == "Search Scooter":
            clear()
            flush_input()
            scooter_id = input("Enter scooter ID to check status: ")
            service_engineer_service.search_scooter(scooter_id)
            click_to_return()

        elif choice == "Exit":
            sys.exit()

