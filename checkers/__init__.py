"""Checkers for a Discord bot: the rules, an opponent that searches ahead, and the board as a picture."""

from .ai import best_move
from .board import Board, IllegalMove
from .constants import BLACK, DRAW, WHITE
from .notation import parse_move

__all__ = ["BLACK", "DRAW", "WHITE", "Board", "IllegalMove", "best_move", "parse_move"]
