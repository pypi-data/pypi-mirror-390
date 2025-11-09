from .base import Widget
import curses

class Frame(Widget):
    def __init__(self,pos, size, title=""):
        x,y = pos
        width, height = size
        super().__init__(x, y, width, height)
        self.title = title
        self.children = []

    def add_widget(self, widget):
        widget.set_app(self.app)
        self.children.append(widget)

    def render(self):
        win = curses.newwin(self.height, self.width, self.y, self.x)
        win.box()

        if self.title:
            win.addstr(0, 2, f" {self.title} ")

        for child in self.children:
            child.render()

        win.refresh()

    def handle_input(self, key: int) -> bool:
        for child in self.children:
            if child.handle_input(key):
                return True
        return False
