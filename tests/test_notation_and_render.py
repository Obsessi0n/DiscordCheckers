import io

from PIL import Image

from checkers import Board, parse_move, render
from checkers.ai import self_play
from checkers.notation import name_of


def test_a_move_is_two_squares_in_either_order_and_any_case():
    # Row 1 is the bottom of the board as drawn: the last row of the grid.
    assert parse_move("3A 4B") == ((5, 0), (4, 1))
    assert parse_move("a3 b4") == ((5, 0), (4, 1))
    assert parse_move("3a to 4b, please") == ((5, 0), (4, 1))
    assert parse_move("8H 1A") == ((0, 7), (7, 0))
    assert name_of((5, 0)) == "3A" and name_of((0, 7)) == "8H"


def test_text_that_is_not_two_squares_is_no_move():
    for text in ("", "3A", "3A 4B 5C", "9A 4B", "3I 4B", "hello"):
        assert parse_move(text) is None


def test_the_board_is_drawn_in_memory_as_a_png():
    data = render.png(Board(), "Player")
    assert data.startswith(b"\x89PNG\r\n\x1a\n")
    with Image.open(io.BytesIO(data)) as image:
        assert image.size == (800, 800)


def test_a_game_is_a_gif_with_a_frame_for_each_position_in_order():
    positions = self_play(depth=1, max_plies=6)
    data = render.gif([render.draw(board, "AI") for board in positions])
    assert data.startswith(b"GIF8")
    with Image.open(io.BytesIO(data)) as animation:
        assert animation.n_frames == len(positions)
        assert animation.size == (480, 480)
