import sys
from ui.login_interface import start_interface
from data.database import initialize_database
from dotenv import load_dotenv
from ui.menu_utils import clear


def main():
    load_dotenv()
    clear()

    # initialize_database()

    start_interface()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[INFO] Program exited by user.")
        sys.exit(0)
