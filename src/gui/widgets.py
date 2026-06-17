from __future__ import annotations

import pygame

from gui.constants import (
    ACCENT_LIGHT,
    BORDER,
    CARD_BG,
    TEXT_DARK,
    TEXT_MUTED,
    get_font,
)


class Dropdown:
    def __init__(self, rect: pygame.Rect, options: list[str], selected: int = 0) -> None:
        self.rect = rect
        self.options = options
        self.selected = selected
        self.open = False
        self._option_height = rect.height

    @property
    def value(self) -> str:
        return self.options[self.selected]

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Returns True if selection changed."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.open = not self.open
                return False
            if self.open:
                for i, opt_rect in enumerate(self._option_rects()):
                    if opt_rect.collidepoint(event.pos):
                        changed = self.selected != i
                        self.selected = i
                        self.open = False
                        return changed
                self.open = False
        return False

    def _option_rects(self) -> list[pygame.Rect]:
        return [
            pygame.Rect(self.rect.x, self.rect.bottom + i * self._option_height,
                        self.rect.width, self._option_height)
            for i in range(len(self.options))
        ]

    def draw(self, surface: pygame.Surface) -> None:
        font = get_font("serif", 14)
        # Main box
        pygame.draw.rect(surface, CARD_BG, self.rect, border_radius=3)
        pygame.draw.rect(surface, BORDER, self.rect, 1, border_radius=3)
        txt = font.render(self.value, True, TEXT_DARK)
        surface.blit(txt, (self.rect.x + 6, self.rect.centery - txt.get_height() // 2))
        # Arrow (drawn triangle — font glyph unreliable across systems)
        ax = self.rect.right - 14
        ay = self.rect.centery
        pygame.draw.polygon(surface, TEXT_MUTED, [
            (ax - 5, ay - 3),
            (ax + 5, ay - 3),
            (ax, ay + 4),
        ])

        if self.open:
            for i, opt_rect in enumerate(self._option_rects()):
                bg = ACCENT_LIGHT if i == self.selected else CARD_BG
                pygame.draw.rect(surface, bg, opt_rect)
                pygame.draw.rect(surface, BORDER, opt_rect, 1)
                t = font.render(self.options[i], True, TEXT_DARK)
                surface.blit(t, (opt_rect.x + 6, opt_rect.centery - t.get_height() // 2))
