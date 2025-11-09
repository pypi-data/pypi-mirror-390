import curses
from curses import panel
from typing import List, Optional
from tkurses.themes import ThemeManager

class App:
    def __init__(self, stdscr, theme=None):
        self.stdscr = stdscr
        self.theme = ThemeManager(stdscr=stdscr ,themeFile=theme)
        self.widgets: List["Widget"] = []
        self.focus_index = 0

        curses.curs_set(0)  # Hide cursor
        curses.start_color()
        curses.use_default_colors()

        self.running = True

    def add_widget(self, widget):
        widget.set_app(self)
        self.widgets.append(widget)
        # If widget has children (e.g. Frame), propagate app to them
        if hasattr(widget, 'children'):
            for child in widget.children:
                child.set_app(self)
        widget.render()


    def focus_next(self):
        if not self.widgets:
            return
        self.focus_index = (self.focus_index + 1) % len(self.widgets)
        for widget in self.widgets:
            widget.set_focus(False)
        self.widgets[self.focus_index].set_focus(True)
        self.refresh()

    def refresh(self):
        self.stdscr.clear()
        for widget in self.widgets:
            widget.render()
        self.stdscr.refresh()

    def handle_input(self, key):
        if not self.widgets:
            return

        focused = self.widgets[self.focus_index]
        handled = focused.handle_input(key)

        if not handled and key == 9:  # 9 is ASCII for Tab
            self.focus_next()

    def mainloop(self):
        self.refresh()
        while self.running:
            key = self.stdscr.getch()
            if key == 27:  # ESC key to quit
                self.running = False
            else:
                self.handle_input(key)
                for object in self.widgets:
                    object.update()
                self.refresh()

    def stop(self):
        self.running = False


class Widget:
    def __init__(self, x: int, y: int, width: int = None, height: int = None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.app: Optional[App] = None

    def set_app(self, app: App):
        self.app = app

    def render(self):
        pass  # To be overridden

    def handle_input(self, key: int) -> bool:
        return False  # Return True if key was handled


class DefaultTheme:
    def init_colors(self):
        # Example of color pairs
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(3, curses.COLOR_WHITE, -1)

    def get_color(self, name: str) -> int:
        mapping = {
            "primary": curses.color_pair(1),
            "secondary": curses.color_pair(2),
            "default": curses.color_pair(3)
        }
        return mapping.get(name, curses.color_pair(3))
