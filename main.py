# --- main.py ---
import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.clock import Clock
from kivy.core.window import Window

from ig_fetch import fetch_profile, format_number, ProfileResult
from ui.theme import COLORS, FONT_SIZE
from ui.components import Card, StatBox, Divider, BadgeLabel

Window.clearcolor = COLORS["bg"]


class IGAnalyzerApp(App):

    def build(self):
        self.title = "IG Profil Analiz"
        root = BoxLayout(orientation="vertical", spacing=0)
        root.add_widget(self._build_header())
        root.add_widget(self._build_search_bar())
        root.add_widget(Divider())

        scroll = ScrollView(size_hint=(1, 1))
        self.content_area = BoxLayout(
            orientation="vertical",
            spacing=16,
            padding=[20, 20, 20, 20],
            size_hint_y=None,
        )
        self.content_area.bind(minimum_height=self.content_area.setter("height"))
        scroll.add_widget(self.content_area)
        root.add_widget(scroll)

        self._show_placeholder()
        return root

    # ── HEADER ────────────────────────────────────────────────────────────────
    def _build_header(self):
        header = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=60,
            padding=[20, 0, 20, 0],
        )
        with header.canvas.before:
            Color(*COLORS["surface"])
            self._header_rect = Rectangle(pos=header.pos, size=header.size)
        header.bind(
            pos=lambda *_: setattr(self._header_rect, "pos", header.pos),
            size=lambda *_: setattr(self._header_rect, "size", header.size),
        )

        header.add_widget(Label(
            text="⚡ IG Profil Analiz",
            font_size=FONT_SIZE["lg"],
            bold=True,
            color=COLORS["text"],
            halign="left",
            valign="middle",
        ))
        header.add_widget(Widget())
        self.status_dot = Label(
            text="● HAZIR",
            font_size=FONT_SIZE["xs"],
            color=COLORS["green"],
            size_hint=(None, None),
            size=(90, 30),
        )
        header.add_widget(self.status_dot)
        return header

    # ── SEARCH BAR ────────────────────────────────────────────────────────────
    def _build_search_bar(self):
        bar = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=64,
            padding=[20, 10, 20, 10],
            spacing=10,
        )
        with bar.canvas.before:
            Color(*COLORS["surface"])
            Rectangle(pos=bar.pos, size=bar.size)

        self.search_input = TextInput(
            hint_text="Kullanıcı adı veya profil linki...",
            multiline=False,
            background_color=COLORS["surface2"],
            foreground_color=COLORS["text"],
            hint_text_color=COLORS["muted"],
            cursor_color=COLORS["accent"],
            padding=[14, 10, 14, 10],
            font_size=FONT_SIZE["sm"],
        )
        self.search_input.bind(on_text_validate=self._on_search)

        self.search_btn = Button(
            text="Ara",
            size_hint=(None, 1),
            width=80,
            background_color=COLORS["accent"],
            color=COLORS["white"],
            bold=True,
            font_size=FONT_SIZE["sm"],
        )
        self.search_btn.bind(on_press=self._on_search)

        bar.add_widget(self.search_input)
        bar.add_widget(self.search_btn)
        return bar

    # ── PLACEHOLDER ───────────────────────────────────────────────────────────
    def _show_placeholder(self):
        self.content_area.clear_widgets()
        self.content_area.add_widget(Widget(size_hint_y=None, height=60))
        self.content_area.add_widget(Label(
            text="📱",
            font_size="64sp",
            size_hint_y=None,
            height=80,
            halign="center",
        ))
        self.content_area.add_widget(Label(
            text="Kullanıcı adı veya\nInstagram profil linki girin",
            font_size=FONT_SIZE["md"],
            color=COLORS["muted"],
            halign="center",
            size_hint_y=None,
            height=60,
        ))

    # ── LOADING ───────────────────────────────────────────────────────────────
    def _show_loading(self, username: str):
        self.content_area.clear_widgets()
        self.content_area.add_widget(Widget(size_hint_y=None, height=80))
        self.content_area.add_widget(Label(
            text="🔍",
            font_size="48sp",
            size_hint_y=None,
            height=64,
            halign="center",
        ))
        self.content_area.add_widget(Label(
            text=f"@{username} aranıyor...",
            font_size=FONT_SIZE["md"],
            color=COLORS["muted"],
            halign="center",
            size_hint_y=None,
            height=40,
        ))

    # ── SEARCH TRIGGER ────────────────────────────────────────────────────────
    def _on_search(self, *_):
        raw = self.search_input.text.strip()
        if not raw:
            return

        self.search_btn.disabled = True
        self.status_dot.text = "● YÜKLÜYOR"
        self.status_dot.color = COLORS["accent"]

        from ig_fetch import clean_username
        self._show_loading(clean_username(raw))

        thread = threading.Thread(target=self._fetch_thread, args=(raw,), daemon=True)
        thread.start()

    def _fetch_thread(self, raw: str):
        result = fetch_profile(raw)
        Clock.schedule_once(lambda dt: self._on_result(result), 0)

    # ── RESULT RENDER ─────────────────────────────────────────────────────────
    def _on_result(self, result: ProfileResult):
        self.search_btn.disabled = False
        self.content_area.clear_widgets()

        if result.error:
            self.status_dot.text = "● HATA"
            self.status_dot.color = COLORS["red"]
            self._show_error(result.error)
            return

        self.status_dot.text = "● HAZIR"
        self.status_dot.color = COLORS["green"]
        self._render_profile(result)

    def _show_error(self, message: str):
        self.content_area.add_widget(Widget(size_hint_y=None, height=60))
        self.content_area.add_widget(Label(
            text="❌",
            font_size="48sp",
            size_hint_y=None,
            height=64,
            halign="center",
        ))
        self.content_area.add_widget(Label(
            text=message,
            font_size=FONT_SIZE["sm"],
            color=COLORS["red"],
            halign="center",
            size_hint_y=None,
            height=60,
        ))

    def _render_profile(self, r: ProfileResult):
        # ── PROFILE HEADER CARD ──
        header_card = Card(
            orientation="vertical",
            spacing=10,
            padding=[20, 20, 20, 20],
            size_hint_y=None,
            height=180,
        )

        # Name row
        name_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=36, spacing=8)
        name_row.add_widget(Label(
            text=r.full_name,
            font_size=FONT_SIZE["lg"],
            bold=True,
            color=COLORS["text"],
            halign="left",
            valign="middle",
        ))
        if r.is_verified:
            name_row.add_widget(BadgeLabel("✅ Onaylı", COLORS["accent2"]))
        header_card.add_widget(name_row)

        # Username
        header_card.add_widget(Label(
            text=f"@{r.username}",
            font_size=FONT_SIZE["sm"],
            color=COLORS["muted"],
            halign="left",
            size_hint_y=None,
            height=24,
        ))

        # Badges row
        badge_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=32, spacing=8)
        privacy_color = COLORS["red"] if r.is_private else COLORS["green"]
        privacy_text = "🔒 Gizli Hesap" if r.is_private else "🌐 Herkese Açık"
        badge_row.add_widget(BadgeLabel(privacy_text, privacy_color))

        acct_text = "💼 İşletme" if r.is_business else "👤 Kişisel"
        badge_row.add_widget(BadgeLabel(acct_text, COLORS["accent"]))
        badge_row.add_widget(Widget())
        header_card.add_widget(badge_row)

        self.content_area.add_widget(header_card)

        # ── STATS ROW ──
        stats_row = BoxLayout(
            orientation="horizontal",
            spacing=10,
            size_hint_y=None,
            height=80,
        )
        stats_row.add_widget(StatBox("TAKİPÇİ", format_number(r.followers), COLORS["green"]))
        stats_row.add_widget(StatBox("TAKİP", format_number(r.followees), COLORS["accent"]))
        stats_row.add_widget(StatBox("GÖNDERİ", format_number(r.post_count), COLORS["text"]))
        self.content_area.add_widget(stats_row)

        # ── BIO CARD ──
        bio_card = Card(
            orientation="vertical",
            spacing=8,
            padding=[18, 14, 18, 14],
            size_hint_y=None,
            height=120,
        )
        bio_card.add_widget(Label(
            text="BİYOGRAFİ",
            font_size=FONT_SIZE["xs"],
            color=COLORS["muted"],
            bold=True,
            halign="left",
            size_hint_y=None,
            height=20,
        ))
        bio_card.add_widget(Label(
            text=r.bio,
            font_size=FONT_SIZE["sm"],
            color=COLORS["text"],
            halign="left",
            valign="top",
            text_size=(Window.width - 76, None),
        ))
        self.content_area.add_widget(bio_card)

        # ── BIO LINK CARD ──
        if r.bio_url != "—":
            link_card = Card(
                orientation="horizontal",
                spacing=8,
                padding=[18, 12, 18, 12],
                size_hint_y=None,
                height=52,
            )
            link_card.add_widget(Label(
                text="🔗",
                font_size=FONT_SIZE["md"],
                size_hint=(None, 1),
                width=30,
            ))
            link_card.add_widget(Label(
                text=r.bio_url,
                font_size=FONT_SIZE["sm"],
                color=COLORS["accent2"],
                halign="left",
                valign="middle",
            ))
            self.content_area.add_widget(link_card)

        # ── PROFILE PIC URL CARD ──
        pic_card = Card(
            orientation="vertical",
            spacing=6,
            padding=[18, 12, 18, 12],
            size_hint_y=None,
            height=100,
        )
        pic_card.add_widget(Label(
            text="PROFİL RESMİ URL",
            font_size=FONT_SIZE["xs"],
            color=COLORS["muted"],
            bold=True,
            halign="left",
            size_hint_y=None,
            height=20,
        ))
        pic_card.add_widget(Label(
            text=r.profile_pic_url[:80] + "..." if len(r.profile_pic_url) > 80 else r.profile_pic_url,
            font_size="10sp",
            color=COLORS["muted"],
            halign="left",
            valign="top",
            text_size=(Window.width - 76, None),
        ))
        self.content_area.add_widget(pic_card)

        # ── DISCLAIMER ──
        self.content_area.add_widget(Label(
            text="⚠️ Hesap oluşturma tarihi Instagram public API'de mevcut değil.\nBu Meta kısıtlamasıdır.",
            font_size=FONT_SIZE["xs"],
            color=COLORS["muted"],
            halign="center",
            size_hint_y=None,
            height=40,
        ))

        self.content_area.add_widget(Widget(size_hint_y=None, height=20))


if __name__ == "__main__":
    IGAnalyzerApp().run()
