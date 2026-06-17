from __future__ import annotations

from dataclasses import dataclass

import pygame

from bots.base import Bot
from bots.greedy_bot import GreedyBot
from bots.random_bot import RandomBot
from gui.constants import (
    ACCENT,
    ACCENT_LIGHT,
    BG,
    BORDER,
    CARD_BG,
    TEXT_DARK,
    TEXT_MUTED,
    WINDOW_W,
    get_font,
)
from gui.widgets import Dropdown


@dataclass
class GameConfig:
    white_bot: Bot | None       # None = human
    black_bot: Bot | None       # None = human
    white_name: str
    black_name: str
    time_seconds: float         # 0 = no time control
    increment_seconds: float
    starting_mode: str          # "normal", "random_sym", "random_asym"


_BOT_OPTIONS = ["Mensch", "RandomBot", "GreedyBot"]
_POS_OPTIONS = ["Normal", "Sym. Zufall", "Asym. Zufall"]
_POS_MODES = ["normal", "random_sym", "random_asym"]


def _make_bot(option: str, name: str) -> Bot | None:
    if option == "RandomBot":
        return RandomBot(name)
    if option == "GreedyBot":
        return GreedyBot(name)
    return None


class MainMenuScreen:
    def __init__(self, surface: pygame.Surface) -> None:
        self._surf = surface
        self._setup_layout()

    def _setup_layout(self) -> None:
        cx = WINDOW_W // 2
        left_x = cx - 280
        row_h = 32
        gap = 8

        # White player
        self._white_type_dd = Dropdown(
            pygame.Rect(left_x, 160, 200, row_h), _BOT_OPTIONS, 0)
        self._white_name_rect = pygame.Rect(left_x, 160 + row_h + gap, 200, row_h)
        self._white_name = "Spieler 1"

        # Black player
        self._black_type_dd = Dropdown(
            pygame.Rect(left_x, 260, 200, row_h), _BOT_OPTIONS, 1)
        self._black_name_rect = pygame.Rect(left_x, 260 + row_h + gap, 200, row_h)
        self._black_name = "RandomBot"

        # Active input field
        self._active_input: str | None = None  # "white" or "black"

        # Time control
        self._time_rect = pygame.Rect(left_x, 370, 90, row_h)
        self._inc_rect = pygame.Rect(left_x + 110, 370, 80, row_h)
        self._time_str = ""
        self._inc_str = ""
        self._active_time: str | None = None  # "time" or "inc"

        # Start button
        self._start_rect = pygame.Rect(left_x, 420, 200, 40)

        # Starting position selection
        self._pos_selected = 0
        self._pos_rects = [
            pygame.Rect(cx + 20, 200 + i * 44, 160, 36)
            for i in range(3)
        ]

    def handle_event(self, event: pygame.event.Event):
        """Returns GameScreen if match started, else None."""
        from gui.game_screen import GameScreen

        self._white_type_dd.handle_event(event)
        self._black_type_dd.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Name inputs
            if self._white_name_rect.collidepoint(event.pos):
                self._active_input = "white"
                self._active_time = None
            elif self._black_name_rect.collidepoint(event.pos):
                self._active_input = "black"
                self._active_time = None
            elif self._time_rect.collidepoint(event.pos):
                self._active_time = "time"
                self._active_input = None
            elif self._inc_rect.collidepoint(event.pos):
                self._active_time = "inc"
                self._active_input = None
            else:
                self._active_input = None
                self._active_time = None

            # Position selection
            for i, r in enumerate(self._pos_rects):
                if r.collidepoint(event.pos):
                    self._pos_selected = i

            # Start button
            if self._start_rect.collidepoint(event.pos):
                return GameScreen(self._surf, self._build_config())

        if event.type == pygame.KEYDOWN:
            self._handle_key(event)

        return None

    def _handle_key(self, event: pygame.event.Event) -> None:
        if event.key == pygame.K_BACKSPACE:
            if self._active_input == "white":
                self._white_name = self._white_name[:-1]
            elif self._active_input == "black":
                self._black_name = self._black_name[:-1]
            elif self._active_time == "time":
                self._time_str = self._time_str[:-1]
            elif self._active_time == "inc":
                self._inc_str = self._inc_str[:-1]
        elif event.unicode:
            if self._active_input == "white":
                self._white_name += event.unicode
            elif self._active_input == "black":
                self._black_name += event.unicode
            elif (
                self._active_time == "time"
                and event.unicode.isdigit()
                and len(self._time_str) < 3
            ):
                self._time_str += event.unicode
            elif (
                self._active_time == "inc"
                and event.unicode.isdigit()
                and len(self._inc_str) < 3
            ):
                self._inc_str += event.unicode

    def _build_config(self) -> GameConfig:
        wname = self._white_name or "Weiß"
        bname = self._black_name or "Schwarz"
        w_type = self._white_type_dd.value
        b_type = self._black_type_dd.value
        mins = int(self._time_str) if self._time_str else 0
        inc = int(self._inc_str) if self._inc_str else 0
        return GameConfig(
            white_bot=_make_bot(w_type, wname),
            black_bot=_make_bot(b_type, bname),
            white_name=wname,
            black_name=bname,
            time_seconds=mins * 60.0,
            increment_seconds=float(inc),
            starting_mode=_POS_MODES[self._pos_selected],
        )

    def update(self, dt: float) -> None:
        pass

    def draw(self) -> None:
        surf = self._surf
        surf.fill(BG)
        font_title = get_font("serif", 28)
        font_sub = get_font("serif", 12)
        font_label = get_font("serif", 11)
        font_body = get_font("serif", 14)

        # Title
        t = font_title.render("LOS ALAMOS", True, ACCENT)
        surf.blit(t, (WINDOW_W // 2 - t.get_width() // 2, 60))
        s = font_sub.render("Schachvariante · 6×6", True, TEXT_MUTED)
        surf.blit(s, (WINDOW_W // 2 - s.get_width() // 2, 98))

        cx = WINDOW_W // 2
        left_x = cx - 280

        # Divider
        pygame.draw.line(surf, BORDER, (left_x - 10, 120), (left_x + 380, 120), 1)

        # White section
        lbl = font_label.render("WEISS", True, TEXT_MUTED)
        surf.blit(lbl, (left_x, 140))
        self._white_type_dd.draw(surf)
        self._draw_input(surf, self._white_name_rect, self._white_name,
                         self._active_input == "white", font_body)

        # Black section
        lbl = font_label.render("SCHWARZ", True, TEXT_MUTED)
        surf.blit(lbl, (left_x, 240))
        self._black_type_dd.draw(surf)
        self._draw_input(surf, self._black_name_rect, self._black_name,
                         self._active_input == "black", font_body)

        # Divider
        pygame.draw.line(surf, BORDER, (left_x - 10, 355), (left_x + 200, 355), 1)

        # Time control
        lbl = font_label.render("ZEIT & INKREMENT", True, TEXT_MUTED)
        surf.blit(lbl, (left_x, 358))
        self._draw_input(surf, self._time_rect, self._time_str or "",
                         self._active_time == "time", font_body,
                         placeholder="min")
        plus = font_body.render("+", True, TEXT_MUTED)
        surf.blit(plus, (left_x + 96, self._time_rect.centery - plus.get_height() // 2))
        self._draw_input(surf, self._inc_rect, self._inc_str or "",
                         self._active_time == "inc", font_body,
                         placeholder="sek")

        # Start button
        pygame.draw.rect(surf, ACCENT, self._start_rect, border_radius=4)
        bt = font_body.render("Match starten", True, (255, 255, 255))
        surf.blit(bt, (self._start_rect.centerx - bt.get_width() // 2,
                       self._start_rect.centery - bt.get_height() // 2))

        # Right column — starting position
        right_x = cx + 20
        lbl = font_label.render("AUFSTELLUNG", True, TEXT_MUTED)
        surf.blit(lbl, (right_x, 160))

        # Position buttons
        for i, (r, label) in enumerate(zip(self._pos_rects, _POS_OPTIONS)):
            bg = ACCENT_LIGHT if i == self._pos_selected else CARD_BG
            border = ACCENT if i == self._pos_selected else BORDER
            pygame.draw.rect(surf, bg, r, border_radius=3)
            pygame.draw.rect(surf, border, r, 1, border_radius=3)
            t = font_body.render(label, True, ACCENT if i == self._pos_selected else TEXT_DARK)
            surf.blit(t, (r.centerx - t.get_width() // 2, r.centery - t.get_height() // 2))

    def _draw_input(self, surf, rect, text, active, font, placeholder=""):
        pygame.draw.rect(surf, CARD_BG, rect, border_radius=3)
        border_color = ACCENT if active else BORDER
        pygame.draw.rect(surf, border_color, rect, 1, border_radius=3)
        display = text if text else placeholder
        color = TEXT_DARK if text else TEXT_MUTED
        t = font.render(display, True, color)
        surf.blit(t, (rect.x + 6, rect.centery - t.get_height() // 2))
        if active and text:
            cx = rect.x + 6 + t.get_width() + 2
            pygame.draw.line(surf, TEXT_DARK, (cx, rect.y + 4), (cx, rect.bottom - 4), 1)

