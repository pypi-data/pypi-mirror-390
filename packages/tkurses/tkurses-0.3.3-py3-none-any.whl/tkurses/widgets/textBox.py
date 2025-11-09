from .base import Widget
import curses
import curses.textpad as textpad
typeable_chars = [chr(i) for i in range(32, 127)]
ENTER_KEYS = ['\n', '\r', 10, 13, curses.KEY_ENTER]
BACKSPACE_KEYS = ['\b', '\x7f', 8, 127, curses.KEY_BACKSPACE]


class TextBox(Widget):
    def __init__(self, pos, size, exitOnEnter=True):
        super().__init__(pos[0], pos[1],width=size[0],height=size[1])
        self.exitOnEnter = False
        self.text = ""
        self.done = False

    def render(self):
        textpad.rectangle(self.app.stdscr, self.y, self.x,
                          self.height+self.y, self.x+self.width)
        if self.done:
            self.app.stdscr.addstr(self.y,self.x+2,"Closed")
        row = 1
        for line in self.text.split("\n"):
            while len(line) >= self.width:
                newLine = line[:self.width-1]
                line = line[self.width-1:]
                self.app.stdscr.addstr(self.y+row, self.x+1, newLine)
                row = row + 1
            if row >= self.height:
                self.done = True
            self.app.stdscr.addstr(self.y+row, self.x+1, line)
            row+=1

    def handle_input(self, key):
        if self.done == False:
            if chr(key) in typeable_chars:
                self.text = self.text + chr(key)
            if key in ENTER_KEYS:
                if self.exitOnEnter:
                    self.done = True
                    return self.text
                else:
                    self.text = self.text + "\n"
            if key in BACKSPACE_KEYS:
                self.text = self.text[:-1]