import os

# Bot token can be provided through the DISCORD_BOT_TOKEN environment
# variable. Falling back to a placeholder string keeps the code running
# for development purposes.
TOKEN = os.getenv("DISCORD_BOT_TOKEN", "Bot-Token")

WIDTH, HEIGHT = 800, 800
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH//COLS

RED = (60, 60, 60)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREY = (128,128,128)
