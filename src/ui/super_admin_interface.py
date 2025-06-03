# Same as Service Engineer:
# • To update the attributes of scooters in the system
# • To search and retrieve the information of a scooter (check note 2 below)
# Please note: The credentials of the Super Administrator are hard-coded. Therefore, it is not
# required that he should be able to update his own password. The Super Administrator does not
# need a password change option in the user interface.
# Same as System Administrator:
# • To check the list of users and their roles.
# • To add a new Service Engineer to the backend system.
# • To modify or update an existing Service Engineer account and profile.
# • To delete an existing Service Engineer account.
# • To reset an existing Service Engineer password (a temporary password).
# • To see the logs file(s) of the backend system.
# • To add a new Traveller to the backend system.
# Analysis 8: Software Quality (INFSWQ01-A | INFSWQ21-A) OP4 | 2023-2024 CMI | HR
# FINAL ASSIGNMENT: Urban Mobility Backend System PAGE 8
# • To update the information of a Traveller in the backend system.
# • To delete a Traveller from the backend system.
# • To add a new scooter to the backend system.
# • To update the information of a scooter in the backend system.
# • To delete a scooter from the backend system.
# • To search and retrieve the information of a Traveller (check note 2 below).
# Specific for the Super Administrator:
# • To add a new System Administrator to the backend system.
# • To modify or update an existing System Administrator account and profile.
# • To delete an existing System Administrator account.
# • To reset an existing System Administrator password (a temporary password).
# • To make a backup of the backend system and to restore a backup.
# • To allow a specific System Administrator to restore a specific backup. For this purpose,
# the Super Administrator should be able to generate a restore-code linked to a specific
# backup and System Administrator. The restore-code is one-use-only.
# • To revoke a previously generated restore-code for a System Administrator.


def super_admin_interface():
    print("Welcome to the Super Admin Interface")
    
    while True:
        command = input("Enter a command (type 'help' for options): ").strip().lower()

        if command == 'help':
            print("Available commands: help, exit")
        elif command == 'exit':
            print("Exiting Super Admin Interface.")
            break
        else:
            print(f"Unknown command: {command}. Type 'help' for options.")