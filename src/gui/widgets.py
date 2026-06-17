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


class GroupedDropdown:
    """Dropdown with non-selectable group header rows.

    entries: list of (is_header, label, sublabel)
      - is_header=True  → drawn as a muted separator, not selectable
      - is_header=False → selectable item; sublabel shown right-aligned if non-empty
    selected: index into the selectable entries only (headers excluded)
    """

    def __init__(
        self,
        rect: pygame.Rect,
        entries: list[tuple[bool, str, str]],
        selected: int = 0,
    ) -> None:
        self.rect = rect
        self.entries = entries
        self._selectable: list[int] = [i for i, (h, _, _) in enumerate(entries) if not h]
        self.selected = selected  # index into _selectable
        self.open = False
        self._option_height = rect.height

    @property
    def value(self) -> str:
        return self.entries[self._selectable[self.selected]][1]

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Returns True if selection changed."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.open = not self.open
                return False
            if self.open:
                for row_idx, opt_rect in enumerate(self._all_option_rects()):
                    if opt_rect.collidepoint(event.pos):
                        entry_idx = row_idx
                        if self.entries[entry_idx][0]:  # header — not selectable
                            continue
                        sel_idx = self._selectable.index(entry_idx)
                        changed = self.selected != sel_idx
                        self.selected = sel_idx
                        self.open = False
                        return changed
                self.open = False
        return False

    def _all_option_rects(self) -> list[pygame.Rect]:
        return [
            pygame.Rect(
                self.rect.x,
                self.rect.bottom + i * self._option_height,
                self.rect.width,
                self._option_height,
            )
            for i in range(len(self.entries))
        ]

    def draw(self, surface: pygame.Surface) -> None:
        font = get_font("serif", 14)
        font_sm = get_font("serif", 11)
        # Main box
        pygame.draw.rect(surface, CARD_BG, self.rect, border_radius=3)
        pygame.draw.rect(surface, BORDER, self.rect, 1, border_radius=3)
        txt = font.render(self.value, True, TEXT_DARK)
        surface.blit(txt, (self.rect.x + 6, self.rect.centery - txt.get_height() // 2))
        ax = self.rect.right - 14
        ay = self.rect.centery
        pygame.draw.polygon(surface, TEXT_MUTED, [
            (ax - 5, ay - 3), (ax + 5, ay - 3), (ax, ay + 4),
        ])

        if not self.open:
            return

        for i, (opt_rect, (is_header, label, sublabel)) in enumerate(
            zip(self._all_option_rects(), self.entries)
        ):
            if is_header:
                pygame.draw.rect(surface, CARD_BG, opt_rect)
                pygame.draw.rect(surface, BORDER, opt_rect, 1)
                ht = font_sm.render(label, True, TEXT_MUTED)
                surface.blit(ht, (opt_rect.x + 6, opt_rect.centery - ht.get_height() // 2))
            else:
                sel_idx = self._selectable.index(i)
                bg = ACCENT_LIGHT if sel_idx == self.selected else CARD_BG
                pygame.draw.rect(surface, bg, opt_rect)
                pygame.draw.rect(surface, BORDER, opt_rect, 1)
                t = font.render(label, True, TEXT_DARK)
                surface.blit(t, (opt_rect.x + 6, opt_rect.centery - t.get_height() // 2))
                if sublabel:
                    st = font_sm.render(sublabel, True, TEXT_MUTED)
                    surface.blit(st, (opt_rect.right - st.get_width() - 6,
                                      opt_rect.centery - st.get_height() // 2))
