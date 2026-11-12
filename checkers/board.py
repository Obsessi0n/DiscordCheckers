"""The rules of the game: the board, the moves a piece may make, and who has won. No drawing and no I/O."""

from __future__ import annotations

from .constants import BLACK, COLS, DRAW, QUIET_PLIES_FOR_DRAW, ROWS, WHITE, other
from .piece import Piece

Square = tuple[int, int]

# What `evaluate` adds to the count of pieces: for each row a man has advanced, and for each square a king of the side
# ahead stands away from the nearest rival piece.
ADVANCE = 0.03
CHASE = 0.02


class IllegalMove(Exception):
    """A move the rules do not allow. Its text is written for the player who tried it."""


class Board:
    """An 8x8 board. Row 0 is the top, where white starts; black starts at the bottom and moves first."""

    def __init__(self) -> None:
        self.grid: list[list[Piece | None]] = [[None] * COLS for _ in range(ROWS)]
        for row in range(ROWS):
            for col in range(COLS):
                if col % 2 != (row + 1) % 2:
                    continue
                if row < 3:
                    self.grid[row][col] = Piece(row, col, WHITE)
                elif row > 4:
                    self.grid[row][col] = Piece(row, col, BLACK)
        self.turn = BLACK
        self.left = {BLACK: 12, WHITE: 12}
        self.kings = {BLACK: 0, WHITE: 0}
        # Moves in a row with no capture, by either side: a long enough run of them is a draw.
        self.quiet_plies = 0

    def copy(self) -> Board:
        """The same position on a board of its own, counts included: what the search moves on is never the game."""
        twin = Board.__new__(Board)
        twin.grid = [[None if p is None else Piece(p.row, p.col, p.color, p.king) for p in row] for row in self.grid]
        twin.turn = self.turn
        twin.left = dict(self.left)
        twin.kings = dict(self.kings)
        twin.quiet_plies = self.quiet_plies
        return twin

    def piece_at(self, row: int, col: int) -> Piece | None:
        return self.grid[row][col]

    def pieces(self, color: str) -> list[Piece]:
        return [piece for row in self.grid for piece in row if piece is not None and piece.color == color]

    # ---- moves --------------------------------------------------------------------------------

    def valid_moves(self, piece: Piece) -> dict[Square, list[Piece]]:
        """Where `piece` may go, each square with the pieces it takes on the way there (none for a plain step)."""
        moves: dict[Square, list[Piece]] = {}
        row = piece.row
        if piece.color == BLACK or piece.king:
            moves.update(self._traverse(row - 1, max(row - 3, -1), -1, piece.color, piece.col - 1, -1))
            moves.update(self._traverse(row - 1, max(row - 3, -1), -1, piece.color, piece.col + 1, 1))
        if piece.color == WHITE or piece.king:
            moves.update(self._traverse(row + 1, min(row + 3, ROWS), 1, piece.color, piece.col - 1, -1))
            moves.update(self._traverse(row + 1, min(row + 3, ROWS), 1, piece.color, piece.col + 1, 1))
        return moves

    def _traverse(self, start: int, stop: int, step: int, color: str, col: int, side: int, skipped: list[Piece] | None = None) -> dict[Square, list[Piece]]:
        """Walks one diagonal: a step onto an empty square, or a jump over a rival piece and on from where it lands.

        `skipped` holds what the jumps before this one took; after a jump only another jump may follow.
        """
        skipped = skipped or []
        moves: dict[Square, list[Piece]] = {}
        last: list[Piece] = []
        for r in range(start, stop, step):
            if not 0 <= col < COLS:
                break
            current = self.grid[r][col]
            if current is None:
                if skipped and not last:
                    break
                moves[(r, col)] = last + skipped
                if last:
                    # A jump landed here: try to go on jumping, to either side, with all that was taken so far.
                    reach = max(r - 3, -1) if step == -1 else min(r + 3, ROWS)
                    moves.update(self._traverse(r + step, reach, step, color, col - 1, -1, last + skipped))
                    moves.update(self._traverse(r + step, reach, step, color, col + 1, 1, last + skipped))
                break
            if current.color == color or last:
                # One's own piece is in the way, or two pieces stand one behind the other.
                break
            last = [current]
            col += side
        return moves

    def all_moves(self, color: str) -> list[tuple[Piece, Square, list[Piece]]]:
        """Every move of one side: the piece, where it goes, and what it takes."""
        return [(piece, square, taken) for piece in self.pieces(color) for square, taken in self.valid_moves(piece).items()]

    def apply(self, piece: Piece, square: Square, taken: list[Piece] | tuple[Piece, ...] = ()) -> None:
        """Makes a move that `valid_moves` gave for a piece of this board, and hands the turn to the other side."""
        row, col = square
        self.grid[piece.row][piece.col] = None
        self.grid[row][col] = piece
        piece.row, piece.col = row, col
        for rival in taken:
            self.grid[rival.row][rival.col] = None
            self.left[rival.color] -= 1
            if rival.king:
                self.kings[rival.color] -= 1
        if not piece.king and row in (0, ROWS - 1):
            piece.king = True
            self.kings[piece.color] += 1
        self.quiet_plies = 0 if taken else self.quiet_plies + 1
        self.turn = other(self.turn)

    def play(self, origin: Square, square: Square) -> None:
        """A player's move from one square to another, or `IllegalMove` saying why not."""
        piece = self.piece_at(*origin)
        if piece is None:
            raise IllegalMove("There is no piece on that square.")
        if piece.color != self.turn:
            raise IllegalMove("That piece is not yours to move.")
        moves = self.valid_moves(piece)
        if square not in moves:
            raise IllegalMove("That piece cannot go there.")
        self.apply(piece, square, moves[square])

    # ---- the state of the game ----------------------------------------------------------------

    def winner(self) -> str | None:
        """The side that has won, `DRAW`, or None while the game goes on.

        A side with no piece left has lost, and so has the side to move when it has no move to make.
        """
        if self.left[BLACK] == 0:
            return WHITE
        if self.left[WHITE] == 0:
            return BLACK
        if not self.all_moves(self.turn):
            return other(self.turn)
        if self.quiet_plies >= QUIET_PLIES_FOR_DRAW:
            return DRAW
        return None

    def evaluate(self) -> float:
        """How good the position is for white.

        A point for each piece ahead and half a point more for each king. Two small things beside it, each worth far
        less than a piece: a man is worth more the nearer it is to being crowned, and the side that is ahead wants its
        kings close to what is left of the other side. Without the second a won game is never finished: every move
        counts the same pieces, so the kings wander until the game is drawn.
        """
        score = self.left[WHITE] - self.left[BLACK] + 0.5 * (self.kings[WHITE] - self.kings[BLACK])
        whites = self.pieces(WHITE)
        blacks = self.pieces(BLACK)
        score += ADVANCE * sum(piece.row for piece in whites if not piece.king)
        score -= ADVANCE * sum(ROWS - 1 - piece.row for piece in blacks if not piece.king)
        lead = self.left[WHITE] - self.left[BLACK]
        if lead != 0 and whites and blacks:
            hunters, hunted = (whites, blacks) if lead > 0 else (blacks, whites)
            gap = sum(min(max(abs(king.row - rival.row), abs(king.col - rival.col)) for rival in hunted) for king in hunters if king.king)
            score += -CHASE * gap if lead > 0 else CHASE * gap
        return score
