from typing import Optional
import os

class Widget:
    def __init__(self, x: int, y: int, width: Optional[int] = None, height: Optional[int] = None):
        terminalSize = [os.get_terminal_size().columns-1, os.get_terminal_size().lines-1]
        # set percentagses
        if x == 0:
            x=1
        if y == 0:
            y=1
        if width is None:
            width = 1
        if height is None:
            height = 1
        if width <= 0:
            width = 1
        if height <= 0:
            height = 1
        if width >= 100:
            width=99
        if height >= 100:
            height =99
        self.px=x
        self.py=y
        if width == None:
            self.pw=width
        else:
            self.pw=width+x
            self.width = int(width * terminalSize[0] / 100)
        if height == None:
            self.ph=height+y
        else:
            self.ph=height
            self.height = int(height * terminalSize[1] / 100)
        # set percentage
        self.x = int(x * terminalSize[0] / 100)
        self.y = int(y * terminalSize[1] / 100)
        self.app = None
        self.focused = False
        self.parent=None

    def set_app(self, app):
        self.app = app

    def set_focus(self, focused: bool):
        self.focused = focused

    def render(self):
        pass  # To be implemented by subclasses

    def handle_input(self, key: int) -> bool:
        return False
    
    def update(self):
        terminalSize = [os.get_terminal_size().columns, os.get_terminal_size().lines]
        # set percentagses

        # set percentage
        if self.pw != None:
            self.width = int(self.pw * terminalSize[0] / 100)
        if self.ph != None:
            self.height = int(self.ph * terminalSize[1] / 100)
        self.x = int(self.px * terminalSize[0] / 100)
        self.y = int(self.py * terminalSize[1] / 100)
        self.render()
    
    def add_parent(self, parent):
        self.parent=parent
        if parent == self.app:
            pass
        else:
            #changing x and y proportionaly
            self.x = parent.x + int(self.px * parent.width / 100)
            self.y = parent.y + int(self.py * parent.height / 100)

            # Relative size (%)
            if self.pw is not None:
                self.width = int(self.pw * parent.width / 100)
            if self.ph is not None:
                self.height = int(self.ph * parent.height / 100)

    def delete(self):
        self.parent.widgets.remove(self)
        self.app.stdscr.refresh()