# --- ui/components.py ---
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Rectangle
from ui.theme import COLORS, FONT_SIZE


class Card(BoxLayout):
    def __init__(self, radius=16, bg=None, **kwargs):
        super().__init__(**kwargs)
        self._radius = radius
        self._bg = bg or COLORS["surface"]
        self.bind(pos=self._redraw, size=self._redraw)

    def _redraw(self, *_):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self._bg)
            RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[self._radius]
            )


class StatBox(BoxLayout):
    def __init__(self, label: str, value: str, color=None, **kwargs):
        super().__init__(orientation="vertical", spacing=4, **kwargs)
        self._color = color or COLORS["text"]
        self._label_text = label
        self._value_text = value
        self._build()
        self.bind(pos=self._redraw, size=self._redraw)

    def _build(self):
        with self.canvas.before:
            Color(*COLORS["surface2"])
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[12])

        self.add_widget(Label(
            text=self._label_text,
            font_size=FONT_SIZE["xs"],
            color=COLORS["muted"],
            halign="center",
            valign="middle",
            size_hint_y=None,
            height=20,
        ))
        self.value_label = Label(
            text=self._value_text,
            font_size=FONT_SIZE["md"],
            color=self._color,
            bold=True,
            halign="center",
            valign="middle",
        )
        self.add_widget(self.value_label)

    def _redraw(self, *_):
        self._rect.pos = self.pos
        self._rect.size = self.size

    def update(self, value: str):
        self.value_label.text = value


class Divider(Widget):
    def __init__(self, **kwargs):
        super().__init__(size_hint_y=None, height=1, **kwargs)
        self.bind(pos=self._draw, size=self._draw)

    def _draw(self, *_):
        self.canvas.clear()
        with self.canvas:
            Color(*COLORS["border"])
            Rectangle(pos=self.pos, size=self.size)


class BadgeLabel(Label):
    def __init__(self, text: str, color, **kwargs):
        super().__init__(
            text=text,
            font_size=FONT_SIZE["xs"],
            color=color,
            bold=True,
            size_hint=(None, None),
            size=(120, 28),
            **kwargs,
        )
        self.bind(pos=self._draw, size=self._draw)
        self._color = color

    def _draw(self, *_):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(self._color[0], self._color[1], self._color[2], 0.15)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[8])
