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