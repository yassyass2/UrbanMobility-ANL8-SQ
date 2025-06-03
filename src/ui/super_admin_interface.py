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
# Please note: The Super Administrator should not be able to restore a specific backup on behalf of
# a System Administrator (using a restore-code). The Super Administrator can only generate a
# restore-code, but only the intended System Administrator is allowed to use it to perform the
# actual restore.
# Note 1: Service Engineers and System Administrators should have profiles, in addition to their
# usernames and passwords. Their profiles contain only first name, last name and registration date.
# Note 2: The search function must accept reasonable data fields as a search key. It must also accept
# partial keys. For example, a user can search for a Traveller with a name “Mike Thomson” and customer
# ID “2123287421” by entering any of these keys: “mik”, “omso”, or “2328”, etc.

class SuperAdminInterface:
    def __init__(self):
        self.commands = {
            'help': self.show_help,
            'exit': self.exit_interface,
            'update_attributes_scooter': self.update_attributes_scooter,
            'search_scooter': self.search_scooter,
            'check_users': self.check_users,
            'add_service_engineer': self.add_service_engineer,
            'modify_service_engineer': self.modify_service_engineer,
            'delete_service_engineer': self.delete_service_engineer,
            'reset_service_engineer_password': self.reset_service_engineer_password,
            'view_logs': self.view_logs,
            'add_traveller': self.add_traveller,
            'update_traveller': self.update_traveller,
            'delete_traveller': self.delete_traveller,
            'add_scooter': self.add_scooter,
            'update_scooter': self.update_scooter,
            'delete_scooter': self.delete_scooter,
            'search_traveller': self.search_traveller,
            'add_system_admin': self.add_system_admin,
            'modify_system_admin': self.modify_system_admin,
            'delete_system_admin': self.delete_system_admin,
            'reset_system_admin_password': self.reset_system_admin_password,
            'backup_system': self.backup_system,
            'restore_backup': self.restore_backup,
            'generate_restore_code': self.generate_restore_code,
            'revoke_restore_code': self.revoke_restore_code
        }

    def show_help(self):
        print("Available commands:")
        for command in self.commands.keys():
            print(f"- {command}")
        return True

    def exit_interface(self):
        print("Exiting Super Admin Interface.")
        return False
    
    def update_attributes_scooter(self):
        print("Updating scooter information...")
        return True
    
    def search_scooter(self):
        print("Searching for scooter information...")
        return True
    
    def check_users(self):
        print("Checking list of users and their roles...")
        return True
    
    def add_service_engineer(self):
        print("Adding a new Service Engineer...")
        return True
    
    def modify_service_engineer(self):
        print("Modifying an existing Service Engineer account...")
        return True
    
    def delete_service_engineer(self):
        print("Deleting an existing Service Engineer account...")
        return True
    
    def reset_service_engineer_password(self):
        print("Resetting Service Engineer password...")
        return True
    
    def view_logs(self):
        print("Viewing system logs...")
        return True
    
    def add_traveller(self):
        print("Adding a new Traveller...")
        return True
    
    def update_traveller(self):
        print("Updating Traveller information...")
        return True
    
    def delete_traveller(self):
        print("Deleting a Traveller...")
        return True
    
    def add_scooter(self):
        print("Adding a new scooter...")
        return True
    
    def update_scooter(self):
        print("Updating scooter information...")
        return True
    
    def delete_scooter(self):
        print("Deleting a scooter...")
        return True
    
    def search_traveller(self):
        print("Searching for Traveller information...")
        return True
    
    def add_system_admin(self):
        print("Adding a new System Administrator...")
        return True
    
    def modify_system_admin(self):
        print("Modifying an existing System Administrator account...")
        return True
    
    def delete_system_admin(self):
        print("Deleting an existing System Administrator account...")
        return True
    
    def reset_system_admin_password(self):
        print("Resetting System Administrator password...")
        return True
    
    def backup_system(self):
        print("Backing up the system...")
        return True
    
    def restore_backup(self):
        print("Restoring a backup...")
        return True
    
    def generate_restore_code(self):
        print("Generating a restore code for a System Administrator...")
        return True
    
    def revoke_restore_code(self):
        print("Revoking a previously generated restore code...")
        return True

def super_admin_interface():
    print("Welcome to the Super Admin Interface")
    
    while True:
        command = input("Enter a command (type 'help' for options): ").strip().lower()

        if command == 'help':
            SuperAdminInterface().show_help()
        elif command == 'exit':
            print("Exiting Super Admin Interface.")
            break
        elif command in SuperAdminInterface().commands:
            if not SuperAdminInterface().commands[command]():
                break
        else:
            print(f"Unknown command: {command}. Type 'help' for options.")