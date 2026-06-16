from __future__ import annotations

import pygame

from gui.assets import load_sprites
from gui.constants import SQ_SIZE, WINDOW_H, WINDOW_W
from gui.main_menu import MainMenuScreen


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    pygame.display.set_caption("Los Alamos")
    load_sprites(SQ_SIZE)
    clock = pygame.time.Clock()
    current = MainMenuScreen(screen)

    while True:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            result = current.handle_event(event)
            if result is not None:
                current = result
        current.update(dt)
        current.draw()
        pygame.display.flip()


if __name__ == "__main__":
    main()
