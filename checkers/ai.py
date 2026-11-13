"""The bot's play: minimax with alpha-beta pruning. White is the side that maximises."""

from __future__ import annotations

from math import inf

from .board import Board
from .constants import BLACK, QUIET_PLIES_FOR_DRAW, WHITE

# Worth more than any count of pieces. The depth left is added to it, so a win sooner is worth more than a win later.
WIN = 1000.0


def successors(board: Board) -> list[Board]:
    """Each position the side to move can reach in one move, on a board of its own."""
    boards = []
    for piece, square, taken in board.all_moves(board.turn):
        child = board.copy()
        mover = child.piece_at(piece.row, piece.col)
        child.apply(mover, square, [child.piece_at(rival.row, rival.col) for rival in taken])
        boards.append(child)
    return boards


def minimax(board: Board, depth: int, alpha: float = -inf, beta: float = inf) -> tuple[float, Board | None]:
    """The value of `board` for white, looking `depth` moves ahead, and the best position to move to.

    `alpha` and `beta` are the best each side is already sure of elsewhere: a branch that cannot beat them is left
    unsearched, which changes how long the search takes and never what it answers.
    """
    if board.left[BLACK] == 0:
        return WIN + depth, None
    if board.left[WHITE] == 0:
        return -WIN - depth, None
    if board.quiet_plies >= QUIET_PLIES_FOR_DRAW:
        return 0.0, None
    if depth == 0:
        return board.evaluate(), None

    children = successors(board)
    maximising = board.turn == WHITE
    if not children:
        # The side to move has no move: it has lost.
        return (-WIN - depth, None) if maximising else (WIN + depth, None)

    best = None
    if maximising:
        value = -inf
        for child in children:
            score, _ = minimax(child, depth - 1, alpha, beta)
            if score > value:
                value, best = score, child
            alpha = max(alpha, value)
            if alpha >= beta:
                break
    else:
        value = inf
        for child in children:
            score, _ = minimax(child, depth - 1, alpha, beta)
            if score < value:
                value, best = score, child
            beta = min(beta, value)
            if alpha >= beta:
                break
    return value, best


def best_move(board: Board, depth: int = 5) -> Board | None:
    """The position after the best move for the side whose turn it is, or None when it has no move."""
    return minimax(board, max(1, depth))[1]


def self_play(depth: int = 2, max_plies: int = 200) -> list[Board]:
    """A game the bot plays against itself: every position from the first, until one side wins, a draw, or `max_plies`."""
    board = Board()
    positions = [board]
    while len(positions) <= max_plies and board.winner() is None:
        following = best_move(board, depth)
        if following is None:
            break
        board = following
        positions.append(board)
    return positions
