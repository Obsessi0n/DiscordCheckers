# DiscordCheckers

![board](https://user-images.githubusercontent.com/23345523/131253600-4bce1d31-d903-45ae-a45c-36b79e02f57a.png)

A Discord bot, written in Python, that plays checkers against you. It picks its moves with the minimax algorithm and alpha-beta pruning, and draws the board as an image after every move.

## Commands

| Command | What it does |
| --- | --- |
| `/checkers` | Starts a game. You are black and move first. |
| `/movepiece 3A 4B` | Moves your piece from one square to another. `A3 B4` and lower case work too. |
| `/resign` | Gives up the game you are playing. |
| `/checkeryourself` | The bot plays a game against itself and posts it as a GIF. |
| `/ping` | How long the bot takes to hear from Discord. |
| `/stats` | The memory the bot uses and how many games are in play. |

Each person has one game of their own, so several people can play at once, in one server or in many. A move the rules do not allow is answered to you alone, with the reason.

## Setup

1. Create an application and a bot in the [Discord developer portal](https://discord.com/developers/applications), and invite the bot to your server with the `bot` and `applications.commands` scopes.
2. Install what the bot needs (Python 3.10 or later):
   ```bash
   pip install -r requirements.txt
   ```
3. Give the bot its token in an environment variable and start it:
   ```bash
   export DISCORD_BOT_TOKEN="your token"   # PowerShell: $env:DISCORD_BOT_TOKEN = "your token"
   python checkersbot.py
   ```

| Variable | Default | Meaning |
| --- | --- | --- |
| `DISCORD_BOT_TOKEN` | none, required | The bot's token. It is read from the environment only, so it never has to be written in a file of the repository. |
| `DISCORD_GUILD_ID` | none | The id of one server. With it the commands show up there at once; without it they are registered for every server, which can take Discord up to an hour. |
| `CHECKERS_DEPTH` | `5` | How many moves ahead the bot looks, 1 to 8. Higher plays better and takes longer: a move takes about a tenth of a second at 5 and over a second at 7. |

## How it plays

- **The rules** are in `checkers/board.py`: steps, jumps and jumps one after another, kings that move both ways. A side with no piece left has lost, and so has the side to move when it has no move to make. Forty moves by each side with no capture is a draw. Taking a piece is not compulsory.
- **The search** is in `checkers/ai.py`: minimax with alpha-beta pruning, so branches that cannot change the answer are left unsearched. It runs in a thread of its own, and the bot goes on answering other people while it thinks.
- **A position is valued** by the count of pieces, with half a point more for a king. A man is worth a little more the nearer it is to being crowned, and the side that is ahead prefers its kings close to what is left of the other side.
- **The pictures** are made in memory by `checkers/render.py` and sent straight to Discord: nothing is written to disk.

## Development

```bash
pip install -r requirements-dev.txt
python -m pytest
```

The tests cover the rules, the search (pruning must give the same answer as a search with none), reading a move, the pictures, and the bot's commands against a stand-in for Discord. They run on every push and pull request.

```text
checkersbot.py        the Discord bot: commands and who is playing
checkers/board.py     the rules
checkers/ai.py        the search
checkers/notation.py  reading "3A 4B"
checkers/render.py    the board as a PNG, a game as a GIF
tests/                the tests
```

## What could come next

- Compulsory captures, as the tournament rules have them.
- A stronger endgame: with few pieces left the bot can fail to finish a won game, and the game ends in a draw.
- Player against player.
- Games that survive a restart of the bot: they are kept in memory only.

## License

[GPL-3.0](LICENSE)
