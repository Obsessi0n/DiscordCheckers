"""The board as a picture, made in memory: a PNG of one position, or a GIF of a whole game."""

from __future__ import annotations

import io
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .board import Board
from .constants import BLACK, COLS, ROWS
from .notation import LETTERS

# Found from this file, not from wherever the bot was started.
ASSETS = Path(__file__).resolve().parent.parent / "assets"

CELL = 92
# The first square's corner on the background, and the piece's margin inside its square.
OFFSET = 27 + 20
INK = (0, 0, 0)


@lru_cache(maxsize=None)
def _sprite(name: str) -> Image.Image:
    with Image.open(ASSETS / name) as image:
        return image.convert("RGBA")


@lru_cache(maxsize=None)
def _font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(ASSETS / "fonts" / "RosesareFF0000.ttf"), size)


def draw(board: Board, player: str = "") -> Image.Image:
    """The position as an image: the pieces on the background, whose turn it is, and the names of rows and columns."""
    image = _sprite("checkers_background.png").copy()
    crown = _sprite("crown.png")
    for row in range(ROWS):
        for col in range(COLS):
            piece = board.piece_at(row, col)
            if piece is None:
                continue
            at = (CELL * col + OFFSET, CELL * row + OFFSET)
            sprite = _sprite(f"{piece.color}piece.png")
            image.paste(sprite, at, sprite)
            if piece.king:
                image.paste(crown, at, crown)

    pen = ImageDraw.Draw(image)
    side = "BLACK" if board.turn == BLACK else "WHITE"
    pen.text((190, 7), f"Turn: {player} - {side}" if player else f"Turn: {side}", INK, font=_font(22))
    for row in range(1, ROWS + 1):
        pen.text((6, row * CELL - 25), str(ROWS + 1 - row), INK, font=_font(28))
    for col in range(1, COLS + 1):
        pen.text((col * CELL - 25, 800 - 26), LETTERS[col - 1], INK, font=_font(28))
    return image


def png(board: Board, player: str = "") -> bytes:
    buffer = io.BytesIO()
    draw(board, player).save(buffer, format="PNG")
    return buffer.getvalue()


def gif(frames: list[Image.Image], frame_ms: int = 150, size: int = 480) -> bytes:
    """A game as a GIF that loops, its frames in the order given and made smaller so that the file stays light."""
    small = [frame.convert("RGB").resize((size, size)) for frame in frames]
    buffer = io.BytesIO()
    small[0].save(buffer, format="GIF", append_images=small[1:], save_all=True, duration=frame_ms, loop=0)
    return buffer.getvalue()
