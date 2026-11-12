"""A Discord bot that plays checkers: `/checkers` starts a game, `/movepiece 3A 4B` moves a piece.

Run it with the bot's token in the DISCORD_BOT_TOKEN environment variable:

    python checkersbot.py
"""

from __future__ import annotations

import asyncio
import io
import os

import discord
from discord import app_commands

from checkers import BLACK, DRAW, WHITE, Board, IllegalMove, best_move, parse_move
from checkers import render
from checkers.ai import self_play

DEFAULT_DEPTH = 5

ENDINGS = {BLACK: "You win. Good game!", WHITE: "I win. Good game!", DRAW: "It is a draw. Good game!"}


class CheckersBot(discord.Client):
    """One game for each person, kept in memory: a restart of the bot ends the games in play."""

    def __init__(self, depth: int = DEFAULT_DEPTH, guild_id: int | None = None) -> None:
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)
        self.games: dict[int, Board] = {}
        self.depth = depth
        self.guild = discord.Object(id=guild_id) if guild_id else None
        _add_commands(self)

    async def setup_hook(self) -> None:
        # Commands of one server show up at once; commands of every server can take Discord an hour to show.
        if self.guild is not None:
            self.tree.copy_global_to(guild=self.guild)
            await self.tree.sync(guild=self.guild)
        else:
            await self.tree.sync()

    # ---- what the commands do -----------------------------------------------------------------

    async def start_game(self, interaction: discord.Interaction) -> None:
        board = Board()
        self.games[interaction.user.id] = board
        await interaction.response.send_message(
            "Let's play! You are black and move first, for example `/movepiece 3A 4B`.",
            file=_picture(board, interaction.user.display_name),
        )

    async def move(self, interaction: discord.Interaction, text: str) -> None:
        player = interaction.user
        board = self.games.get(player.id)
        if board is None:
            await interaction.response.send_message("You have not started a game. Use `/checkers`.", ephemeral=True)
            return
        if board.turn != BLACK:
            await interaction.response.send_message("Wait for my move first.", ephemeral=True)
            return
        squares = parse_move(text)
        if squares is None:
            await interaction.response.send_message("I could not read that move. Give two squares, for example `3A 4B`.", ephemeral=True)
            return
        try:
            board.play(*squares)
        except IllegalMove as problem:
            await interaction.response.send_message(str(problem), ephemeral=True)
            return

        # The search takes longer than Discord waits for an answer, so say that one is coming.
        await interaction.response.defer()
        await interaction.followup.send(file=_picture(board, player.display_name))
        if await self._ended(interaction, board):
            return

        # In a thread of its own, so the bot goes on answering everyone else while it thinks.
        reply = await asyncio.to_thread(best_move, board, self.depth)
        if reply is None or self.games.get(player.id) is not board:
            # The person resigned or started again meanwhile.
            return
        self.games[player.id] = reply
        await interaction.followup.send("My move.", file=_picture(reply, player.display_name))
        await self._ended(interaction, reply)

    async def resign(self, interaction: discord.Interaction) -> None:
        if self.games.pop(interaction.user.id, None) is None:
            await interaction.response.send_message("You have no game to give up.", ephemeral=True)
        else:
            await interaction.response.send_message("You resigned. Use `/checkers` for another game.")

    async def play_itself(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        animation = await asyncio.to_thread(_self_play_gif)
        await interaction.followup.send(file=discord.File(io.BytesIO(animation), filename="checkers.gif"))

    async def _ended(self, interaction: discord.Interaction, board: Board) -> bool:
        """Says how the game ended and forgets it, when it has ended."""
        result = board.winner()
        if result is None:
            return False
        self.games.pop(interaction.user.id, None)
        await interaction.followup.send(ENDINGS[result])
        return True


def _picture(board: Board, player: str) -> discord.File:
    return discord.File(io.BytesIO(render.png(board, player)), filename="board.png")


def _self_play_gif() -> bytes:
    return render.gif([render.draw(board, "AI") for board in self_play()])


def _add_commands(bot: CheckersBot) -> None:
    @bot.tree.command(name="checkers", description="Start a game of checkers against the bot")
    async def checkers_command(interaction: discord.Interaction) -> None:
        await bot.start_game(interaction)

    @bot.tree.command(name="movepiece", description="Move one of your pieces")
    @app_commands.describe(move="The square to move from and the square to move to, for example 3A 4B")
    async def movepiece_command(interaction: discord.Interaction, move: str) -> None:
        await bot.move(interaction, move)

    @bot.tree.command(name="resign", description="Give up the game you are playing")
    async def resign_command(interaction: discord.Interaction) -> None:
        await bot.resign(interaction)

    @bot.tree.command(name="checkeryourself", description="Watch the bot play a game against itself")
    async def checkeryourself_command(interaction: discord.Interaction) -> None:
        await bot.play_itself(interaction)

    @bot.tree.command(name="ping", description="How long the bot takes to hear from Discord")
    async def ping_command(interaction: discord.Interaction) -> None:
        await interaction.response.send_message(f"Ping is {round(bot.latency * 1000)} ms")

    @bot.tree.command(name="stats", description="The memory the bot uses and the games in play")
    async def stats_command(interaction: discord.Interaction) -> None:
        await interaction.response.send_message(f"{_memory()}Games in play: {len(bot.games)}")


def _memory() -> str:
    try:
        import psutil
    except ImportError:
        return ""
    return f"RAM: {psutil.Process(os.getpid()).memory_info().rss / 1024**2:.1f} MB. "


def _number(name: str, default: int | None, low: int, high: int) -> int | None:
    """A whole number from the environment, held between two bounds; the default when it is missing or not a number."""
    try:
        return max(low, min(high, int(os.environ[name])))
    except (KeyError, ValueError):
        return default


def main() -> None:
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        raise SystemExit("Set the DISCORD_BOT_TOKEN environment variable to your bot's token.")
    depth = _number("CHECKERS_DEPTH", DEFAULT_DEPTH, 1, 8)
    guild_id = _number("DISCORD_GUILD_ID", None, 1, 2**63)
    CheckersBot(depth=depth or DEFAULT_DEPTH, guild_id=guild_id).run(token)


if __name__ == "__main__":
    main()
