import argparse
import json
import os
import socket
import subprocess


# *********
# Constants
# *********

VERSION = "MyMenu 1.2.7"
CONFIG = f"{os.environ['HOME']}/.mymenu.json"
HOSTNAME = socket.gethostname()
USER = os.environ["USERNAME"] if os.name == "nt" else os.environ["USER"]

# Foreground colors
FG_DEFAULT = 39  # Default (usually green, white or light gray)
FG_BLACK = 30
FG_RED = 31
FG_GREEN = 32
FG_YELLOW = 33
FG_BLUE = 34
FG_MAGENTA = 35
FG_CYAN = 36
FG_WHITE = 37
FG_LBLACK = 90
FG_LRED = 91
FG_LGREEN = 92
FG_LYELLOW = 93
FG_LBLUE = 94
FG_LMAGENTA = 95
FG_LCYAN = 96
FG_LWHITE = 97

# Background colors
BG_DEFAULT = 49  # Default background color
BG_BLACK = 40
BG_RED = 41
BG_GREEN = 42
BG_YELLOW = 43
BG_BLUE = 44
BG_MAGENTA = 45
BG_CYAN = 46
BG_WHITE = 47
BG_LBLACK = 100
BG_LRED = 101
BG_LGREEN = 102
BG_LYELLOW = 103
BG_LBLUE = 104
BG_LMAGENTA = 105
BG_CYAN = 106
BG_LWHITE = 107

# Set Colors
BGCOLOR = BG_BLACK

BLACK = f"\033[{FG_BLACK};{BGCOLOR}m"
RED = f"\033[{FG_RED};{BGCOLOR}m"
GREEN = f"\033[{FG_GREEN};{BGCOLOR}m"
YELLOW = f"\033[{FG_YELLOW};{BGCOLOR}m"
BLUE = f"\033[{FG_BLUE};{BGCOLOR}m"
MAGENTA = f"\033[{FG_MAGENTA};{BGCOLOR}m"
CYAN = f"\033[{FG_CYAN};{BGCOLOR}m"
WHITE = f"\033[{FG_WHITE};{BGCOLOR}m"

LBLACK = f"\033[{FG_LBLACK};{BGCOLOR}m"
LRED = f"\033[{FG_LRED};{BGCOLOR}m"
LGREEN = f"\033[{FG_LGREEN};{BGCOLOR}m"
LYELLOW = f"\033[{FG_LYELLOW};{BGCOLOR}m"
LBLUE = f"\033[{FG_LBLUE};{BGCOLOR}m"
LMAGENTA = f"\033[{FG_LMAGENTA};{BGCOLOR}m"
LCYAN = f"\033[{FG_LCYAN};{BGCOLOR}m"
LWHITE = f"\033[{FG_LWHITE};{BGCOLOR}m"

RESET_ATTRS = "\033[m\033[2J"

# *****
# Types
# *****


class Coordinates:
    x: int
    y: int

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y


# ****
# Data
# ****

data = [
    {
        "type": "MENU_TITLE",
        "title": "Main menu",
    },
    {
        "type": "SUBMENU",
        "label": "Submenu",
        "key": "1",
        "submenu": [
            {
                "type": "MENU_TITLE",
                "title": "Submenu",
            },
            {
                "type": "COMMAND",
                "label": "Command 1",
                "key": "1",
                "command": "command1",
            },
            {
                "type": "COMMAND",
                "label": "Command 2",
                "key": "2",
                "command": "command2",
            },
        ],
    },
    {"type": "COMMAND", "label": "Command", "key": "2", "command": "command"},
]


# ****************
# Screen functions
# ****************


def run_cmd(cmd: str) -> None:
    os.system(cmd)


def run_cmd_silently(cmd: list) -> str:
    result = subprocess.run(cmd, stdout=subprocess.PIPE)
    return result.stdout.decode()


def get_scr_size() -> Coordinates:
    r = run_cmd_silently(["stty", "size"])
    arr = r.strip().split(" ")
    return Coordinates(int(arr[1]), int(arr[0]))


def goto_xy(x: int, y: int) -> None:
    print(f"\033[{y};{x}H", end=" ")


def clrscr() -> None:
    print(f"\033[0;{BGCOLOR}m", end=" ")
    print("\033[2J", end=" ")


# ***********
# Application
# ***********


def load_config(file: str) -> None:
    global data
    global CONFIG

    if file is not None:
        if not os.path.isfile(file):
            CONFIG = file
            print(f"File doesnt exist: {CONFIG}")
            exit(1)
        else:
            CONFIG = file

    # create config file if doesn't exist
    if not os.path.isfile(CONFIG):
        with open(CONFIG, "w") as f:
            json.dump(data, f, indent=4)

    # load config file
    with open(CONFIG, "r") as f:
        data = json.load(f)


def get_parent(menu: list, current_menu: list) -> list | None:
    for i in menu:
        if "submenu" in i:
            if i["submenu"] == current_menu:
                return menu
            else:
                res = get_parent(i["submenu"], current_menu)
                if res is not None:
                    return res
    return None


def color_text(text: str, col1: str, col2: str) -> str:
    n = int(len(text) / 2)
    return f"{col1}{text[:n]}{col2}{text[n:]}"


def print_menu_item(key: str, label: str, width: int) -> None:
    print(
        f"{WHITE}[ {LWHITE}{key} {LBLUE}- {color_text(label, LBLUE, BLUE)} {'.' * (width + 3 - len(label))} {LBLACK}]"
    )


def draw_menu(menu: list) -> None:
    title = ""
    menu_width = 0
    menu_height = 0

    for i in menu:
        if i["type"] == "MENU_TITLE":
            title = i["title"]
        elif i["type"] in ["SUBMENU", "COMMAND"]:
            wdth = len(i["label"])
            menu_width = wdth if wdth > menu_width else menu_width
            menu_height += 1

    size = get_scr_size()
    goto_xy(int(size.x / 2 - (len(title) + 18) / 2), 2)
    print(f"{WHITE}---{LBLUE}---[- {color_text(title, LBLUE, BLUE)} -]---{LBLACK}---")

    line = int(size.y / 2 - menu_height / 2)
    col = int(size.x / 2 - (menu_width + 12) / 2)

    for i in menu:
        if i["type"] in ["SUBMENU", "COMMAND"]:
            goto_xy(col, line)
            print_menu_item(i["key"], i["label"], menu_width)
            line += 1

    goto_xy(1, size.y - 2)
    shortcuts = f"{WHITE}[{LWHITE}Q{LBLACK}]uit"
    shlen = 6
    if menu != data:
        shortcuts = f"{WHITE}[{LWHITE}B{LBLACK}]ack, " + shortcuts
        shlen += 8
    print(f"{LBLACK}{VERSION}", end=" ")
    uhost = f"{USER}@{HOSTNAME}"
    goto_xy(int((size.x - len(uhost)) / 2), size.y - 2)
    print(uhost, end=" ")
    goto_xy(size.x - shlen - 1, size.y - 2)
    print(shortcuts, end=" ")

    goto_xy(1, size.y - 1)


def main():
    parser = argparse.ArgumentParser(description="Menu")
    optional = parser.add_argument_group("optional arguments")
    optional.add_argument(
        "-f",
        "--file",
        type=str,
        help="You can specify menu config file otherwise $HOME/.pymenu.json will be taken.",
    )
    args = parser.parse_args()

    load_config(args.file)
    current_menu: list = data

    while True:
        clrscr()
        draw_menu(current_menu)
        k = input(f"{WHITE}> ")

        for i in current_menu:
            if "key" in i and i["key"] == k and i["type"] == "SUBMENU":
                current_menu = i["submenu"]
            elif "key" in i and i["key"] == k and i["type"] == "COMMAND":
                print(f"{RESET_ATTRS}")
                run_cmd(i["command"])
                input("Press Enter to continue...")
            elif k == "B":
                parent = get_parent(data, current_menu)
                if parent is not None:
                    current_menu = parent
                    break
            elif k == "Q":
                print(f"{RESET_ATTRS}Bye")
                exit(0)


if __name__ == "__main__":
    main()
