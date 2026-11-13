import asyncio
from types import SimpleNamespace

import pytest

pytest.importorskip("discord")

from checkers import BLACK, WHITE
from checkersbot import CheckersBot


class Sink:
    """Stands for Discord's side of an interaction: it keeps what the bot sent."""

    def __init__(self):
        self.sent = []
        self.is_deferred = False

    async def send_message(self, content=None, **options):
        self.sent.append((content, options))

    async def send(self, content=None, **options):
        self.sent.append((content, options))

    async def defer(self, **options):
        self.is_deferred = True


def interaction(user_id=7):
    return SimpleNamespace(user=SimpleNamespace(id=user_id, display_name="Player"), response=Sink(), followup=Sink())


def test_the_commands_are_the_ones_the_readme_names():
    bot = CheckersBot()
    assert sorted(command.name for command in bot.tree.get_commands()) == ["checkers", "checkeryourself", "movepiece", "ping", "resign", "stats"]


def test_a_game_starts_with_the_board_and_a_move_is_answered_with_the_bots_own():
    async def play():
        bot = CheckersBot(depth=2)
        start = interaction()
        await bot.start_game(start)
        assert "board.png" == start.response.sent[0][1]["file"].filename

        turn = interaction()
        await bot.move(turn, "3A 4B")
        assert turn.response.is_deferred and turn.response.sent == []
        # The board after the person's move, then the bot's move with the board after it.
        assert [content for content, _ in turn.followup.sent] == [None, "My move."]
        board = bot.games[7]
        assert board.turn == BLACK
        assert board.piece_at(4, 1).color == BLACK
        assert sum(piece.color == WHITE for row in board.grid for piece in row if piece) == 12

    asyncio.run(play())


def test_what_cannot_be_played_is_said_to_the_person_alone_and_changes_nothing():
    async def play():
        bot = CheckersBot(depth=1)

        nothing = interaction()
        await bot.move(nothing, "3A 4B")
        assert "not started" in nothing.response.sent[0][0] and nothing.response.sent[0][1] == {"ephemeral": True}

        await bot.start_game(interaction())
        for text, reason in (("hello", "could not read"), ("4B 3A", "no piece"), ("6B 5A", "not yours"), ("3A 5A", "cannot go there")):
            attempt = interaction()
            await bot.move(attempt, text)
            assert reason in attempt.response.sent[0][0], text
            assert attempt.response.sent[0][1] == {"ephemeral": True}
            assert not attempt.response.is_deferred
        assert bot.games[7].turn == BLACK and bot.games[7].piece_at(5, 0) is not None

    asyncio.run(play())


def test_each_person_has_a_game_of_their_own_and_may_give_it_up():
    async def play():
        bot = CheckersBot(depth=1)
        await bot.start_game(interaction(1))
        await bot.start_game(interaction(2))
        await bot.move(interaction(1), "3A 4B")
        assert bot.games[1].piece_at(5, 0) is None
        assert bot.games[2].piece_at(5, 0) is not None

        leaving = interaction(1)
        await bot.resign(leaving)
        assert "resigned" in leaving.response.sent[0][0]
        assert list(bot.games) == [2]
        again = interaction(1)
        await bot.resign(again)
        assert again.response.sent[0][1] == {"ephemeral": True}

    asyncio.run(play())
