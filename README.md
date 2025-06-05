# DiscordCheckers
![board](https://user-images.githubusercontent.com/23345523/131253600-4bce1d31-d903-45ae-a45c-36b79e02f57a.png)

A bot for discord made with python that allows users to play checkers against an AI using the Minimax Algorithm.

The user can start a game by using /checkers.
The user can move pieces using for example /movepiece 3A 4B.

The AI uses the Minimax Algorithm to calculate the next move. It's dificult can be adjusted by changing the Minimax Depth.
The user can also ask the AI to play against itself using /checkeryourself.

For debug purposes the bot also has a /ping and /stats commands.

More test needs to be done for multiple servers/users checkers games simultaneously.

## Setup

1. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
2. Provide your Discord bot token using the `DISCORD_BOT_TOKEN` environment
   variable or edit `modules/constants.py` with your token.
3. Ensure the `boards/` directory exists. This repository includes the folder
   with a `.gitkeep` file so the bot can store board images there at runtime.

# Known Issues

The bot has trouble detecting when a game has ended due to the fact that board.white_left and board.red_left keep getting reseted to 12.

When creating the gif for /checkeryourself sometimes the gif jumps to the start for a brief second.

An algorithm to detect DRAW needs to be implemented.

# Further improvements

The Minimax Algorithm could be more efficient (maybe multi threading?).

Player vs Player mode.

# Test this current version of the bot
Discord server to test the bot:
https://discord.gg/Nf3SWA77

