import pytest

from checkers import BLACK, DRAW, WHITE, Board, IllegalMove
from checkers.constants import QUIET_PLIES_FOR_DRAW
from checkers.piece import Piece


def empty_board(turn=BLACK):
    """A board with nothing on it, to set a position on."""
    board = Board()
    board.grid = [[None] * 8 for _ in range(8)]
    board.left = {BLACK: 0, WHITE: 0}
    board.kings = {BLACK: 0, WHITE: 0}
    board.turn = turn
    return board


def place(board, row, col, color, king=False):
    piece = Piece(row, col, color, king)
    board.grid[row][col] = piece
    board.left[color] += 1
    board.kings[color] += king
    return piece


def counted(board):
    """The counts as the squares have them, to hold the board's own counts against."""
    left = {BLACK: 0, WHITE: 0}
    kings = {BLACK: 0, WHITE: 0}
    for row in board.grid:
        for piece in row:
            if piece is not None:
                left[piece.color] += 1
                kings[piece.color] += piece.king
    return left, kings


def test_a_new_board_has_twelve_pieces_a_side_and_black_moves_first():
    board = Board()
    assert board.left == {BLACK: 12, WHITE: 12}
    assert counted(board) == (board.left, board.kings)
    assert board.turn == BLACK
    assert board.winner() is None
    # Seven moves are open to each side at the start.
    assert len(board.all_moves(BLACK)) == 7
    assert len(board.all_moves(WHITE)) == 7


def test_a_step_moves_the_piece_and_hands_the_turn_over():
    board = Board()
    board.play((5, 0), (4, 1))
    assert board.piece_at(5, 0) is None
    assert board.piece_at(4, 1).color == BLACK
    assert board.turn == WHITE
    assert board.left == {BLACK: 12, WHITE: 12}


def test_a_move_the_rules_do_not_allow_is_refused_and_changes_nothing():
    board = Board()
    with pytest.raises(IllegalMove, match="no piece"):
        board.play((4, 1), (3, 2))
    with pytest.raises(IllegalMove, match="not yours"):
        board.play((2, 1), (3, 2))
    with pytest.raises(IllegalMove, match="cannot go there"):
        board.play((5, 0), (3, 0))
    assert board.turn == BLACK
    assert counted(board) == ({BLACK: 12, WHITE: 12}, {BLACK: 0, WHITE: 0})


def test_a_jump_takes_the_piece_and_the_counts_follow():
    board = empty_board()
    place(board, 5, 2, BLACK)
    place(board, 4, 3, WHITE)
    place(board, 0, 7, WHITE)
    board.play((5, 2), (3, 4))
    assert board.piece_at(4, 3) is None
    assert board.left == {BLACK: 1, WHITE: 1}
    assert counted(board) == (board.left, board.kings)
    assert board.quiet_plies == 0


def test_a_double_jump_takes_both_pieces_and_may_end_on_the_last_row():
    board = empty_board()
    jumper = place(board, 4, 1, BLACK)
    place(board, 3, 2, WHITE)
    place(board, 1, 4, WHITE)
    place(board, 7, 0, WHITE)
    moves = board.valid_moves(jumper)
    # One jump lands on (2, 3); the second goes on to the last row, (0, 5), with both pieces taken.
    assert set(moves) == {(3, 0), (2, 3), (0, 5)}
    assert len(moves[(0, 5)]) == 2
    board.play((4, 1), (0, 5))
    assert board.left == {BLACK: 1, WHITE: 1}
    assert board.piece_at(0, 5).king
    assert board.kings == {BLACK: 1, WHITE: 0}
    assert counted(board) == (board.left, board.kings)


def test_a_piece_that_reaches_the_far_row_is_a_king_and_a_king_taken_is_counted_out():
    board = empty_board()
    place(board, 1, 2, BLACK)
    place(board, 7, 6, WHITE)
    board.play((1, 2), (0, 1))
    king = board.piece_at(0, 1)
    assert king.king and board.kings[BLACK] == 1
    # A king moves down the board as well as up it.
    board.turn = BLACK
    assert (1, 0) in board.valid_moves(king) and (1, 2) in board.valid_moves(king)

    taken = empty_board(turn=WHITE)
    place(taken, 3, 2, BLACK, king=True)
    place(taken, 2, 1, WHITE)
    place(taken, 7, 6, BLACK)
    taken.play((2, 1), (4, 3))
    assert taken.kings == {BLACK: 0, WHITE: 0}
    assert counted(taken) == (taken.left, taken.kings)


def test_a_copy_is_a_board_of_its_own():
    board = Board()
    twin = board.copy()
    twin.play((5, 0), (4, 1))
    assert board.piece_at(5, 0) is not None and board.turn == BLACK
    assert twin.piece_at(5, 0) is None and twin.turn == WHITE
    assert twin.piece_at(5, 2) is not board.piece_at(5, 2)


def test_the_game_is_over_with_no_piece_left_or_no_move_to_make_and_drawn_after_a_long_quiet():
    lone = empty_board()
    place(lone, 4, 1, BLACK)
    assert lone.winner() == BLACK

    # White to move, its one piece hemmed in at the edge: it has lost.
    stuck = empty_board(turn=WHITE)
    place(stuck, 6, 7, WHITE)
    place(stuck, 7, 6, BLACK)
    assert stuck.all_moves(WHITE) == []
    assert stuck.winner() == BLACK

    quiet = empty_board()
    place(quiet, 7, 0, BLACK, king=True)
    place(quiet, 0, 7, WHITE, king=True)
    quiet.quiet_plies = QUIET_PLIES_FOR_DRAW - 1
    assert quiet.winner() is None
    quiet.play((7, 0), (6, 1))
    assert quiet.winner() == DRAW
