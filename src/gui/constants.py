from __future__ import annotations

import pygame

# Window
WINDOW_W, WINDOW_H = 900, 650

# Board geometry
SQ_SIZE = 88
BOARD_PX = SQ_SIZE * 6  # 528
RANK_LABEL_W = 20
FILE_LABEL_H = 20
BOARD_X = 10 + RANK_LABEL_W                          # 30
BOARD_Y = (WINDOW_H - BOARD_PX - FILE_LABEL_H) // 2  # ~46

# Panel geometry
INFO_X = BOARD_X + BOARD_PX + 8   # 566
INFO_W = 196
HIST_X = INFO_X + INFO_W          # 762
HIST_W = WINDOW_W - HIST_X        # 138

# Colours (classic & light theme)
BG = (245, 240, 232)
CARD_BG = (250, 246, 238)
BORDER = (200, 184, 154)
ACCENT = (61, 90, 62)
ACCENT_LIGHT = (238, 242, 238)
TEXT_DARK = (51, 51, 51)
TEXT_MUTED = (139, 115, 85)
BOARD_LIGHT = (240, 217, 181)
BOARD_DARK = (181, 136, 99)
HIGHLIGHT_SEL = (246, 246, 105)
HIGHLIGHT_LEGAL = (205, 209, 111)
CLOCK_ACTIVE_BG = (61, 90, 62)
CLOCK_ACTIVE_FG = (255, 255, 255)
CLOCK_INACTIVE_BG = (192, 176, 154)
CLOCK_INACTIVE_FG = (245, 240, 232)
PROMO_HOVER_BG = (232, 160, 32)
PROMO_CIRCLE_BG = (255, 255, 255)
OVERLAY_DIM = (0, 0, 0, 160)

# File/rank labels
FILE_NAMES = "abcdef"

_fonts: dict[tuple[str, int], pygame.font.Font] = {}


def get_font(name: str, size: int) -> pygame.font.Font:
    key = (name, size)
    if key not in _fonts:
        try:
            _fonts[key] = pygame.font.SysFont(name, size)
        except Exception:
            _fonts[key] = pygame.font.Font(None, size)
    return _fonts[key]
