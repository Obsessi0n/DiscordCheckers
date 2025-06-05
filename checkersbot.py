import discord
import os, psutil
import string
import glob

from PIL import Image
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_choice, create_option

from modules.constants import TOKEN, WHITE

from modules.board import Board
from modules.game import Game

from os.path import exists

from minimax.algorithm import minimax

from time import sleep


guild_id = GUILDIDHERE

client = commands.Bot(command_prefix="!")
slash = SlashCommand(client, sync_commands=True)

userList = []
boardList = []

game = Game()

dictionaryLetter = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
dictionaryNumber = ['1', '2', '3', '4', '5', '6', '7', '8']



def cleanMovInput(input):
        InputList = list(input)

        originCol = None
        originRow = None
        destCol = None
        destRow = None

        for char in InputList:
                if char in dictionaryNumber:
                        if originRow is None:
                                originRow = char
                        else:
                                destRow = char
                elif char in dictionaryLetter:
                        if originCol is None:
                                originCol = char
                        else:
                                destCol = char
                else:
                        pass

        if None in (originCol, originRow, destCol, destRow):
                return False

        # Convert values into matrix acceptable values
        originRow = 8 - int(originRow)
        destRow = 8 - int(destRow)
        originCol = dictionaryLetter.index(originCol)
        destCol = dictionaryLetter.index(destCol)

        moveClean = [originRow, originCol, destRow, destCol]
        return moveClean



def checkIfValidPiece(row, col, board):
	turn = board.turn

	piece = board.get_piece(row, col)

	if piece == 0:
		return False
	elif piece.color != board.turn:
		return False
	else:
		return True


def initialize():
	for f in os.listdir('boards/'):
		print(f'Deleting previous games: {os.path.basename(f)}')
		os.remove(f'boards/{f}')


def runbot():
	client.run(TOKEN)

def slashCommands():

	@slash.slash(
	name="ping",
	description="Ping the bot",
	guild_ids=[guild_id])

	async def _ping(ctx:SlashContext):
		await ctx.send(f' Ping is: {round(client.latency*1000)}ms')


	@slash.slash(
		name="checkers",
		description="player checkers",
		guild_ids=[guild_id])

	async def _checkers(ctx:SlashContext):
		author = ctx.author_id
		username = ctx.author
		board = Board(author, username)

		boardList.append(board)
		userList.append(author)
		
		board.updateBoardImage(True,0)

		await ctx.send("Let's play!")

		await ctx.send(file=discord.File(f'boards/board-{author}.png'))


	@slash.slash(
		name="movepiece",
		description="Choose a piece to move!",
		guild_ids=[guild_id],
		options=[
    		create_option(
      		name= "move",
     		description= "What piece would you like to choose? Example 3E 4D",
      		option_type= 3,
      		required= True
    		)
    	]
    	)

	async def _movepiece(ctx, move: str):
		author = ctx.author_id
		

		if author in userList:
			error= False

			index = userList.index(author)
			board = boardList[index]

			#Check if input is OK!
			moveClean = cleanMovInput(move)
			if moveClean == False:
				return
			#Check if we chose our piece or opponent
			if checkIfValidPiece(moveClean[0], moveClean[1], board) == False:
				return

			#MOVE
			result = game.move(moveClean[0], moveClean[1], moveClean[2], moveClean[3], board)			
			if result == False:
				return


			#Send board
			await ctx.send(file=discord.File(f'boards/board-{author}.png'))


			#Check if game ended
			if board.checkWin() != False:
				await ctx.send(content= 'Game Ended. Good game!')

	

			##AI turn
			await ctx.send(content= 'My turn!')

			value, new_board = minimax(boardList[index], 5, True)
			boardList[index] = game.aiMove(boardList[index],new_board)
			boardList[index].updateBoardImage(True,0)
			boardList[index].changeTurn()	
			
			await ctx.send(file=discord.File(f'boards/board-{author}.png'))




		else:
			await ctx.send(content=f'It seems you have not started a game! use /checkers')



	@slash.slash(
		name="checkeryourself",
		description="Make bot play against him!",
		guild_ids=[guild_id]    	
    	)

	async def _checkeryourself(ctx:SlashContext):

		board = Board('AI', 'AI')
		index = 0	
		board.updateBoardImage(False, index)
		red_left = 12
		white_left = 12

		#Needs to be fixed later on
		for f in os.listdir('boards/'):			
			os.remove(f'boards/{f}')


		await ctx.send(content=(f'Calculating'))
		while board.checkWin() == False:

			red_left -= (red_left-board.red_left)
			white_left -= (white_left-board.white_left)

			value, new_board = minimax(board, 1, False)
			board = game.aiMove(board,new_board)

			index +=1

			try:
				board.updateBoardImage(False, index)
			except:
				break
			board.changeTurn()	



			value, new_board = minimax(board, 1, True)
			board = game.aiMove(board,new_board)

			index +=1

			try:
				board.updateBoardImage(False, index)
			except:
				break
			board.changeTurn()
			
			

			if index > 85:
				break


		# Create the frames
		frames = []
		imgs = glob.glob("boards/board-AI-*.png")
		for i in imgs:
			new_frame = Image.open(i)
			frames.append(new_frame)
    	# Save into a GIF file that loops forever
		frames[0].save('boards/png_to_gif.gif', format='GIF',
               append_images=frames[1:],
               save_all=True,
               duration=100, loop=0)

		await ctx.send(file=discord.File(f'boards/png_to_gif.gif'))
		await ctx.send(content= f'DONE')



	@slash.slash(
		name="stats",
		description="Choose a piece to move!",
		guild_ids=[guild_id]    	
    	)

	async def _movepiece(ctx:SlashContext):
		await ctx.send(content= f'Ram: {round((psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2), 2)}mb')



initialize()
slashCommands()
runbot()
