"""What the rest of the package agrees on: the size of the board and the names of the two sides."""

ROWS, COLS = 8, 8

# Black starts at the bottom of the board, moves up it and plays first: it is the person's side.
# White starts at the top and moves down: it is the bot's side.
BLACK = "black"
WHITE = "white"

# What `Board.winner` answers when neither side wins.
DRAW = "draw"

# A game with this many moves in a row and no capture is a draw (40 moves by each side).
QUIET_PLIES_FOR_DRAW = 80


def other(color: str) -> str:
    return WHITE if color == BLACK else BLACK
