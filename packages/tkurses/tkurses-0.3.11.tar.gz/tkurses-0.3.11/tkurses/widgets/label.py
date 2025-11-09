from .base import Widget

class Label(Widget):
    def __init__(self, text: str, x: int, y: int):
        super().__init__(x, y)
        self.text = text


    def set_text(self, text: str):
        self.text = text

    def render(self):
        color = self.app.theme.get_label_theme()
        color = color["colors"]["forground"]
        self.app.stdscr.addstr(self.y, self.x, self.text, color)