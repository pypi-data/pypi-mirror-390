import curses
import curses

COLOR_MAP = {
    "black": curses.COLOR_BLACK,
    "red": curses.COLOR_RED,
    "green": curses.COLOR_GREEN,
    "yellow": curses.COLOR_YELLOW,
    "blue": curses.COLOR_BLUE,
    "magenta": curses.COLOR_MAGENTA,
    "cyan": curses.COLOR_CYAN,
    "white": curses.COLOR_WHITE
}

def convert_colors(config):
    if isinstance(config, dict):
        new_dict = {}
        for k, v in config.items():
            if isinstance(v, str):
                lower_v = v.lower()
                # Replace if the string matches a color name
                if lower_v in COLOR_MAP:
                    new_dict[k] = COLOR_MAP[lower_v]
                else:
                    new_dict[k] = v
            else:
                new_dict[k] = convert_colors(v)
        return new_dict
    elif isinstance(config, list):
        return [convert_colors(item) for item in config]
    else:
        return config


def fill_background(stdscr, color_pair_number):
    height, width = stdscr.getmaxyx()
    stdscr.bkgd(' ', curses.color_pair(color_pair_number))  # Set default background property
    stdscr.clear()  # Clear with the background color set
    stdscr.refresh()

class ThemeManager:
    def __init__(self,stdscr, themeFile):
        import json
        with open(themeFile,"r") as file:
            data = json.load(file)
        self.data = data
        self.data = convert_colors(self.data)
        curses.start_color()
        curses.init_pair(1, self.data["colors"]["forground"], self.data["colors"]["background"])
        curses.init_pair(2, self.data["input"]["colors"]["focused"]["forground"],self.data["input"]["colors"]["focused"]["background"])
        curses.init_pair(3, self.data["buttons"]["colors"]["focused"]["forground"],self.data["buttons"]["colors"]["focused"]["background"])
        curses.init_pair(4, self.data["text"]["colors"]["forground"],self.data["text"]["colors"]["background"])
        curses.init_pair(5, self.data["input"]["colors"]["not-focused"]["forground"],self.data["input"]["colors"]["not-focused"]["background"])
        curses.init_pair(6, self.data["buttons"]["colors"]["not-focused"]["forground"],self.data["buttons"]["colors"]["not-focused"]["background"])
        fill_background(stdscr=stdscr,color_pair_number=1)
    def get_input_theme(self):
        return self.data["input"]
    def get_label_theme(self):
        return self.data["text"]
    def get_button_theme(self):
        return self.data["buttons"]
    def getColors(self):
        return {"inputs":{"focused":2,"not-focused":5},"buttons":{"focused":3 ,"not-focused":6},"text":4}