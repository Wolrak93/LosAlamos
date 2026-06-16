from __future__ import annotations

from pathlib import Path

import pygame

from engine.board import Color, PieceType

_ASSET_DIR = Path(__file__).parent.parent.parent / "user_input" / "assets"

_FILE_NAMES = {
    (Color.WHITE, PieceType.PAWN):   "w-pawn.png",
    (Color.WHITE, PieceType.KNIGHT): "w-knight.png",
    (Color.WHITE, PieceType.ROOK):   "w-rook.png",
    (Color.WHITE, PieceType.QUEEN):  "w-queen.png",
    (Color.WHITE, PieceType.KING):   "w-king.png",
    (Color.BLACK, PieceType.PAWN):   "b-pawn.png",
    (Color.BLACK, PieceType.KNIGHT): "b-knight.png",
    (Color.BLACK, PieceType.ROOK):   "b-rook.png",
    (Color.BLACK, PieceType.QUEEN):  "b-queen.png",
    (Color.BLACK, PieceType.KING):   "b-king.png",
}

_sprites: dict[tuple[Color, PieceType], pygame.Surface] = {}


def load_sprites(sq_size: int) -> None:
    for key, filename in _FILE_NAMES.items():
        path = _ASSET_DIR / filename
        img = pygame.image.load(str(path)).convert_alpha()
        _sprites[key] = pygame.transform.smoothscale(img, (sq_size, sq_size))


def get_sprite(color: Color, pt: PieceType) -> pygame.Surface:
    return _sprites[(color, pt)]
