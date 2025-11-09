from .base import Widget
import curses
from curses.textpad import rectangle
typeable_chars = [chr(i) for i in range(32, 127)]
ENTER_KEYS = ['\n', '\r', 10, 13, curses.KEY_ENTER]
BACKSPACE_KEYS = ['\b', '\x7f', 8, 127, curses.KEY_BACKSPACE]

class Input(Widget):
    def __init__(self, title,pos,size,on_press,password=False):
        super().__init__(pos[0],pos[1],size[0],size[1])
        self.text=""
        self.size = [self.width,self.height]
        self.title=title
        self.done = False
        self.on_press = on_press
        self.show = password == True

    def render(self):
        theme = self.app.theme.get_input_theme()
        colors = self.app.theme.getColors()
        if self.focused:
            color = colors["inputs"]["focused"]
        else:
            color = colors["inputs"]["not-focused"]
        style = theme["style"]
        if style == "box":
            rectangle(self.app.stdscr,self.y,self.x,self.y+self.size[1],self.x+self.size[0])
            self.app.stdscr.addstr(self.y,self.x+2,self.title,curses.color_pair(color))
            if self.show == False:
                self.app.stdscr.addstr(self.y+1,self.x+1,self.text,curses.color_pair(color))
            else:
                self.app.stdscr.addstr(self.y+1,self.x+1,"*" * len(self.text),curses.color_pair(color))
        if style == "default":
            self.app.stdscr.addstr(self.y,self.x+2,self.title+": ",curses.color_pair(color))
            if self.show == False:
                self.app.stdscr.addstr(self.y,self.x+len(self.title)+4,self.text,curses.color_pair(color))
            else:
                self.app.stdscr.addstr(self.y,self.x+len(self.title)+4,len(self.text)*"*",curses.color_pair(color))
    def handle_input(self,key):
        if self.done == False:
            if key in typeable_chars or chr(key) in typeable_chars:
                self.text = self.text + chr(key)
            if key in BACKSPACE_KEYS:
                self.text = self.text[:-1]
            if key in ENTER_KEYS:
                self.on_press(self.text)
        else:
            return self.text