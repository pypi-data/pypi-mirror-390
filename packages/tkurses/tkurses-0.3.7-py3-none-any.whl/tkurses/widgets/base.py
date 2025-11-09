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
        if width == 0:
            width = 1
        if height == 0:
            height = 1
        self.px=1
        self.py=y
        if width == None:
            self.pw=width
        else:
            self.pw=width
            self.width = int(width * terminalSize[0] / 100)
        if height == None:
            self.ph=height
        else:
            self.ph=height
            self.height = int(height * terminalSize[1] / 100)
        # set percentage
        self.x = int(x * terminalSize[0] / 100)
        self.y = int(y * terminalSize[1] / 100)
        self.app = None
        self.focused = False

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