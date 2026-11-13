from dataclasses import dataclass


@dataclass
class Piece:
    """A piece and where it stands. A king may move both up and down the board."""

    row: int
    col: int
    color: str
    king: bool = False
