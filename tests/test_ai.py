from math import inf

from checkers import BLACK, WHITE, Board, best_move
from checkers.ai import minimax, self_play, successors

from test_board import counted, empty_board, place


def plain_minimax(board, depth):
    """The same search with nothing pruned: what alpha-beta must agree with."""
    children = successors(board) if depth > 0 else []
    if not children or 0 in board.left.values():
        # The end of the search or of the game: both searches value it the same way.
        return minimax(board, depth)[0]
    scores = [plain_minimax(child, depth - 1) for child in children]
    return max(scores) if board.turn == WHITE else min(scores)


def test_pruning_changes_how_long_the_search_takes_and_not_what_it_answers():
    board = Board()
    for _ in range(6):
        for depth in (1, 2, 3):
            assert minimax(board, depth, -inf, inf)[0] == plain_minimax(board, depth)
        board = best_move(board, 2)


def test_the_bot_takes_a_piece_it_can_take():
    board = empty_board(turn=WHITE)
    place(board, 2, 1, WHITE)
    place(board, 3, 2, BLACK)
    place(board, 7, 6, BLACK)
    reply = best_move(board, 3)
    assert reply.left == {BLACK: 1, WHITE: 1}
    assert reply.piece_at(4, 3).color == WHITE


def test_a_move_of_the_bot_is_one_the_rules_allow_and_leaves_the_game_itself_alone():
    board = Board()
    board.play((5, 0), (4, 1))
    before = [[None if p is None else (p.color, p.king) for p in row] for row in board.grid]
    reply = best_move(board, 3)
    after = [[None if p is None else (p.color, p.king) for p in row] for row in reply.grid]
    assert after in [[[None if p is None else (p.color, p.king) for p in row] for row in child.grid] for child in successors(board)]
    assert [[None if p is None else (p.color, p.king) for p in row] for row in board.grid] == before
    assert reply.turn == BLACK and board.turn == WHITE


def test_the_counts_stay_true_through_a_whole_game_and_the_game_comes_to_an_end():
    # The bug this bot had: the board the search returned had its counts back at twelve, so a game never ended.
    positions = self_play(depth=2, max_plies=300)
    for board in positions:
        assert counted(board) == (board.left, board.kings)
    assert positions[-1].winner() is not None
    assert positions[-1].left != {BLACK: 12, WHITE: 12}


def test_a_man_is_worth_more_near_its_crown_and_the_side_ahead_is_better_off_close_to_the_other():
    def lone_white_man(row, col):
        board = empty_board()
        place(board, row, col, WHITE)
        place(board, 7, 0, BLACK)
        return board.evaluate()

    assert lone_white_man(5, 2) > lone_white_man(1, 2)

    def two_kings_against_one(row, col):
        board = empty_board()
        place(board, 0, 1, WHITE, king=True)
        place(board, row, col, WHITE, king=True)
        place(board, 7, 6, BLACK, king=True)
        return board.evaluate()

    assert two_kings_against_one(5, 4) > two_kings_against_one(1, 2)
    # Neither is worth anything near a piece: the count of pieces still decides.
    assert abs(two_kings_against_one(5, 4) - two_kings_against_one(1, 2)) < 0.5


def test_a_side_with_no_move_gets_none():
    stuck = empty_board(turn=WHITE)
    place(stuck, 6, 7, WHITE)
    place(stuck, 7, 6, BLACK)
    assert best_move(stuck, 3) is None
