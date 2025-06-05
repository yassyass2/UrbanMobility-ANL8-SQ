import sys, os
from ui.login_interface import start_interface
from data.database import initialize_database

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    clear()
    
    initialize_database()

    start_interface()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[INFO] Program exited by user.")
        sys.exit(0)
