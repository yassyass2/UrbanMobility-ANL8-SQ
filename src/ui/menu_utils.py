import os
import keyboard
from visual.text_colors import TextColors


def kbhit():
    import sys
    if sys.platform == "win32":
        import msvcrt
        return msvcrt.kbhit()
    else:
        import select
        return select.select([sys.stdin], [], [], 0)[0] != []

def getch():
    import sys
    if sys.platform == "win32":
        import msvcrt
        return msvcrt.getch()
    else:
        import tty
        import termios
        import sys
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            return sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)

t = TextColors


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def flush_input():
    while kbhit():
        getch()


def click_to_return():
    print(f"\n{t.blue}press any key to return to menu...{t.end}")
    getch()


def click_to_renew_session():
    print(f"\n{t.blue}press any key to return to create a new session...{t.end}")
    getch()


def navigate_menu(options):
    selected = 0

    while True:
        clear()
        print("Use arrow keys to navigate and press Enter to select:\n")
        for i, option in enumerate(options):
            prefix = "> " if i == selected else "   "
            print(f"{prefix}{option}")

        key = keyboard.read_event()

        if key.event_type == keyboard.KEY_DOWN:
            if key.name == "down":
                selected = (selected + 1) % len(options)
            elif key.name == "up":
                selected = (selected - 1) % len(options)
            elif key.name == "enter":
                return options[selected]
