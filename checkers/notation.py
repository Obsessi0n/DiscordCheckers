"""Reading a move as a player types it: two squares, such as `3A 4B`."""

from __future__ import annotations

import re

from .constants import COLS, ROWS

Square = tuple[int, int]

LETTERS = "ABCDEFGH"
_SQUARE = re.compile(r"([A-H])\s*([1-8])|([1-8])\s*([A-H])")


def parse_move(text: str) -> tuple[Square, Square] | None:
    """The squares a move goes from and to, as (row, col) on the board, or None when the text is not two squares.

    A square is a letter and a number in either order (`3A` or `A3`), in capitals or not. Row 1 is the bottom of the
    board as it is drawn, so it is the last row of the grid.
    """
    squares = []
    for letter_first, number_last, number_first, letter_last in _SQUARE.findall(text.upper()):
        letter = letter_first or letter_last
        number = number_last or number_first
        squares.append((ROWS - int(number), LETTERS.index(letter)))
    if len(squares) != 2:
        return None
    return squares[0], squares[1]


def name_of(square: Square) -> str:
    """A square as the board is labelled: (5, 0) is `3A`."""
    row, col = square
    assert 0 <= row < ROWS and 0 <= col < COLS
    return f"{ROWS - row}{LETTERS[col]}"
