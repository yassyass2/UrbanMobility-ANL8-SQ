def service_engineer_interface():
    print("Welcome to the Service Engineer Interface")
    
    while True:
        command = input("Enter a command (type 'help' for options): ").strip().lower()

        if command == 'help':
            print("Available commands: help, exit")
        elif command == 'exit':
            print("Exiting Service Engineer Interface.")
            break
        else:
            print(f"Unknown command: {command}. Type 'help' for options.")