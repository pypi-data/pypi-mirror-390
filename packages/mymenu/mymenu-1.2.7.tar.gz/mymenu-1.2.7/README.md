# MyMenu

Menu for your remote console.

## Installation

You can install mymenu either by `uv`

```
uv tool install mymenu
```

or by `pip`

```
pip install mymenu
```

## Usage

Just run `menu` and `~/.mymenu.json` will be used.

Alternatively you can run `menu -f some_other_menu.json`

## Menu.json

Example of `menu.json` file:
```json
[
    {
        "type": "MENU_TITLE",
        "title": "Main menu"
    },
    {
        "type": "SUBMENU",
        "label": "Submenu",
        "key": "1",
        "submenu": [
            {
                "type": "MENU_TITLE",
                "title": "Submenu"
            },
            {
                "type": "COMMAND",
                "label": "Command 1",
                "key": "1",
                "command": "command1"
            },
            {
                "type": "COMMAND",
                "label": "Command 2",
                "key": "2",
                "command": "command2"
            }
        ]
    },
    {
        "type": "COMMAND",
        "label": "Command",
        "key": "2",
        "command": "command"
    }
]
```

## Contributing

Please install `pre-commit` before commiting and pushing your changes.
```
uv run pre-commit install
```
