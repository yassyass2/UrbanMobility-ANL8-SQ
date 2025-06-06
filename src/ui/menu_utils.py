import os
import keyboard
import msvcrt


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')



def flush_input():
    while msvcrt.kbhit():
        msvcrt.getch()


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
