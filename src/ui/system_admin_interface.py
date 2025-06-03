def system_admin_interface():
    print("Welcome to the System Admin Interface")
    
    while True:
        command = input("Enter a command (type 'help' for options): ").strip().lower()

        if command == 'help':
            print("Available commands: help, exit")
        elif command == 'exit':
            print("Exiting System Admin Interface.")
            break
        else:
            print(f"Unknown command: {command}. Type 'help' for options.")