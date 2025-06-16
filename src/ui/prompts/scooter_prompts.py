from ui.menu_utils import clear, flush_input
from ui.prompts.field_prompts import *

def prompt_update_scooter(scooter_id: int, role: str):
    clear()
    print(f"=== UPDATE SCOOTER {scooter_id} ===\n")

    # Full field list with labels
    fields = [
        "Brand",              
        "Model",              
        "Serial Number",      
        "Top Speed",          
        "Battery Capacity",   
        "State of Charge",    
        "Target Range SOC",   
        "Location",           
        "Out of Service",     
        "Mileage",            
        "Last Maintenance"    
    ]

    # Determine allowed fields based on role
    if role == "service_engineer":
        allowed_indexes = list(range(5, 11))  
        print("As a service engineer, you can only update the following fields:\n")
    elif role == "system_admin" or "super_admin":
        allowed_indexes = list(range(1, len(fields)+1))  # all fields
        print("Select fields to update:\n")

    for i, field in enumerate(fields, 1):
        if i in allowed_indexes:
            print(f"{i}. {field}")

    numbers_csv = input("\nEnter number(s) of fields to update (comma-separated): ").strip()
    selected_indexes = is_valid_number_selection(numbers_csv)

    while not selected_indexes or not all(int(i) in allowed_indexes for i in selected_indexes):
        print("\nInvalid selection. Please select valid field numbers.\n")
        for i, field in enumerate(fields, 1):
            if i in allowed_indexes:
                print(f"{i}. {field}")
        numbers_csv = input("\nEnter number(s) of fields to update (comma-separated): ").strip()
        selected_indexes = is_valid_number_selection(numbers_csv)

    # Build update dictionary
    updates = {}
    for i in selected_indexes:
        i = int(i)
        match i:
            case 1: updates["brand"] = prompt_brand()
            case 2: updates["model"] = prompt_model()
            case 3: updates["serial_number"] = prompt_serial_number()
            case 4: updates["top_speed"] = prompt_top_speed()
            case 5: updates["battery_capacity"] = prompt_capacity()
            case 6: updates["soc"] = prompt_soc()
            case 7: updates["target_range_soc"] = prompt_target_range_soc()
            case 8: updates["location"] = prompt_location()
            case 9: updates["out_of_service"] = prompt_out_of_service()
            case 10: updates["mileage"] = prompt_mileage()
            case 11: updates["last_maintenance"] = prompt_last_maintenance()

    return updates


def is_valid_number_selection(numbers: str) -> list:
    numbers = numbers.strip()

    if not numbers:
        return None

    parts = [part.strip() for part in numbers.split(',')]

    if all(part.isdigit() and int(part) > 0 for part in parts):
        return parts
    else:
        return None

