import curses

KEYMAP = {
    # Letters (uppercase and lowercase)
    **{chr(i): ord(chr(i)) for i in range(ord('a'), ord('z')+1)},
    **{chr(i): ord(chr(i)) for i in range(ord('A'), ord('Z')+1)},

    # Numbers
    **{str(i): ord(str(i)) for i in range(0, 10)},

    # Ctrl+letters (ASCII control codes)
    "CTRL+A": ord("a") & 0x1F,
    "CTRL+B": ord("b") & 0x1F,
    "CTRL+C": ord("c") & 0x1F,
    "CTRL+D": ord("d") & 0x1F,
    "CTRL+E": ord("e") & 0x1F,
    "CTRL+F": ord("f") & 0x1F,
    "CTRL+G": ord("g") & 0x1F,
    "CTRL+H": ord("h") & 0x1F,
    "CTRL+I": ord("i") & 0x1F,
    "CTRL+J": ord("j") & 0x1F,
    "CTRL+K": ord("k") & 0x1F,
    "CTRL+L": ord("l") & 0x1F,
    "CTRL+M": ord("m") & 0x1F,
    "CTRL+N": ord("n") & 0x1F,
    "CTRL+O": ord("o") & 0x1F,
    "CTRL+P": ord("p") & 0x1F,
    "CTRL+Q": ord("q") & 0x1F,
    "CTRL+R": ord("r") & 0x1F,
    "CTRL+S": ord("s") & 0x1F,
    "CTRL+T": ord("t") & 0x1F,
    "CTRL+U": ord("u") & 0x1F,
    "CTRL+V": ord("v") & 0x1F,
    "CTRL+W": ord("w") & 0x1F,
    "CTRL+X": ord("x") & 0x1F,
    "CTRL+Y": ord("y") & 0x1F,
    "CTRL+Z": ord("z") & 0x1F,

    # Arrow keys
    "UP": curses.KEY_UP,
    "DOWN": curses.KEY_DOWN,
    "LEFT": curses.KEY_LEFT,
    "RIGHT": curses.KEY_RIGHT,

    # Function keys
    "F1": curses.KEY_F1,
    "F2": curses.KEY_F2,
    "F3": curses.KEY_F3,
    "F4": curses.KEY_F4,
    "F5": curses.KEY_F5,
    "F6": curses.KEY_F6,
    "F7": curses.KEY_F7,
    "F8": curses.KEY_F8,
    "F9": curses.KEY_F9,
    "F10": curses.KEY_F10,
    "F11": curses.KEY_F11,
    "F12": curses.KEY_F12,

    # Other common keys
    "TAB": ord("\t"),
    "ENTER": ord("\n"),
    "SPACE": ord(" "),
    "ESC": 27,
    "BACKSPACE": 8,
    "DELETE": curses.KEY_DC,
    "HOME": curses.KEY_HOME,
    "END": curses.KEY_END,
    "PAGE_UP": curses.KEY_PPAGE,
    "PAGE_DOWN": curses.KEY_NPAGE,
    "None": None,
}

class SettingsManager:
    def __init__(self, settingsFile):
        with open(settingsFile,"r") as f:
            import json
            self.settings = json.load(f)
    def interpret_keybindings(self):
        config=self.settings
        keymap = KEYMAP
        interpreted = {}
        bindings = config.get("keybindings", {})

        for action, key_str in bindings.items():
            if key_str is None:
                interpreted[action] = None
            else:
                try:
                    code = keymap.get(key_str)
                    if code is None:
                        raise ValueError(f"Key '{key_str}' for action '{action}' not a valid key")
                    interpreted[action] = code
                except:
                    interpreted[action] = None

        return interpreted
