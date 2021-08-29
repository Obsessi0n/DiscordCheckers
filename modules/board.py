from .constants import BLACK, ROWS, RED, SQUARE_SIZE, COLS, WHITE
from .piece import Piece

from PIL import Image, ImageDraw, ImageFont

import os


class Board():
	def __init__(self, user, username):
		self.userID = user
		self.userName = username
		self.board = []
		self.red_left = self.white_left = 12
		self.red_kings = self.white_kings = 0
		self.createBoard()
		self.turn = RED
		self.photoIndex = 0



	def changeTurn(self):
		if self.turn == RED:
			self.turn = WHITE
		else:
			self.turn = RED

	def createBoard(self):
		
		for row in range(ROWS):
			self.board.append([])
			for col in range(COLS):
				if col % 2 == ((row +1 ) % 2):
					if row < 3:
						self.board[row].append(Piece(row, col, WHITE))
						#self.board[row].append("W")
					elif row > 4:
						self.board[row].append(Piece(row, col, RED))
						#self.board[row].append("R")
					else:
						self.board[row].append(0)
				else:
					self.board[row].append(0)


	##AI##
	def evaluate(self):
		return self.white_left - self.red_left +(self.white_kings * 0.5 - self.red_kings*0.5)


	def getAllPiecces(self,color):
		pieces = []
		for row in self.board:
			for piece in row:
				if piece != 0 and piece.color == color:
					pieces.append(piece)
		return pieces
	

				

	def updateBoardImage(self, override, photoIndex):
		#Create Background
		img1 = Image.open('assets/checkers_background.png')
		blackpiece = Image.open('assets/blackpiece.png')
		whitepiece = Image.open('assets/whitepiece.png')
		crown = Image.open('assets/crown.png')


		cellSize=92
		padding = 27

		#Place pieces
		for row in range(ROWS):
			for col in range(COLS):
					if self.board[row][col] != 0:
						if self.board[row][col].color == WHITE:
							if self.board[row][col].king == False:
								img1.paste(whitepiece, (cellSize*col+20+padding, cellSize*row+20+padding), whitepiece)
							else:
								img1.paste(whitepiece, (cellSize*col+20+padding, cellSize*row+20+padding), whitepiece)
								img1.paste(crown, (cellSize*col+20+padding, cellSize*row+20+padding), crown)
						elif self.board[row][col].color == RED:
							if self.board[row][col].king == False:
								img1.paste(blackpiece, (cellSize*col+20+padding, cellSize*row+20+padding), blackpiece)

							else:
								img1.paste(blackpiece, (cellSize*col+20+padding, cellSize*row+20+padding), blackpiece)
								img1.paste(crown, (cellSize*col+20+padding, cellSize*row+20+padding), crown)


		#Text
		draw = ImageDraw.Draw(img1)
		#Title
		fontTitle = ImageFont.truetype('assets/fonts/RosesareFF0000.ttf', 22)
		fontRows = ImageFont.truetype('assets/fonts/RosesareFF0000.ttf', 28)
		if self.turn == RED:
			turnText = 'BLACk'
		else:
			turnText = 'WHITE'
		draw.text((190, 7), f'Turn: {self.userName} - {turnText}', (0, 0, 0), font=fontTitle)

		#Row
		for row in range(1,9):
			draw.text((6, row*92 - 25), str((9-row)), (0, 0, 0), font=fontRows)
		#Col
		for col in range(1,9):
			if col == 1:
				text='A'
			elif col == 2:
				text = 'B'
			elif col == 3:
				text = 'C'
			elif col == 4:
				text = 'D'
			elif col == 5:
				text = 'E'
			elif col == 6:
				text = 'F'
			elif col == 7:
				text = 'G'
			else:
				text = 'H'
			draw.text((col*92 - 25, 800-26), text, (0, 0, 0), font=fontRows)

		if override == False:
			img1.save(f'boards/board-{self.userID}-{photoIndex}.png')
		else:
			img1.save(f'boards/board-{self.userID}.png')	


	def get_piece(self, row, col):
		return self.board[row][col]

	def get_valid_moves(self, piece):
		moves = {}
		left = piece.col - 1
		right = piece.col +1
		row = piece.row

		if piece.color == RED or piece.king:
			moves.update(self._traverse_left(row-1,max(row-3, -1), -1, piece.color, left))
			moves.update(self._traverse_right(row-1,max(row-3, -1), -1, piece.color, right))

		if piece.color == WHITE or piece.king:
			moves.update(self._traverse_left(row+1,min(row+3, ROWS), 1, piece.color, left))
			moves.update(self._traverse_right(row+1,min(row+3, ROWS), 1, piece.color, right))

		return moves

	def _traverse_left(self, start, stop, step, color, left, skipped=[]):
		moves = {}
		last = []
		for r in range(start, stop, step):
			if left < 0:
				break
            
			current = self.board[r][left]
			if current == 0:
				if skipped and not last:
					break
				elif skipped:
					moves[(r, left)] = last + skipped
				else:
					moves[(r, left)] = last
                
				if last:
					if step == -1:
						row = max(r-3, 0)
					else:
						row = min(r+3, ROWS)
					moves.update(self._traverse_left(r+step, row, step, color, left-1,skipped=last))
					moves.update(self._traverse_right(r+step, row, step, color, left+1,skipped=last))
				break
			elif current.color == color:
				break
			else:
				last = [current]

			left -= 1
        
		return moves

	def _traverse_right(self, start, stop, step, color, right, skipped=[]):
		moves = {}
		last = []
		for r in range(start, stop, step):
			if right >= COLS:
				break

			current = self.board[r][right]
			if current == 0:
				if skipped and not last:
					break
				elif skipped:
					moves[(r, right)] = last + skipped
				else:
					moves[(r, right)] = last

				if last:
					if step == -1:
						row = max(r-3,0)
					else:
						row=min(r+3,ROWS)

					moves.update(self._traverse_left(r+step, row, step, color, right-1, skipped=last))
					moves.update(self._traverse_right(r+step, row, step, color, right+1, skipped=last))
				break

			elif current.color == color:
				break
			else:
				last= [current]


			right += 1
		return moves


	def move(self, piece, row, col):
		self.board[piece.row][piece.col], self.board[row][col] = self.board[row][col], self.board[piece.row][piece.col]
		piece.move(row, col)
		if row==ROWS - 1 or row == 0:
			
			if piece.color == WHITE and piece.king == False:
				piece.make_king()
				self.white_kings +=1
			elif piece.king == False:
				piece.make_king()
				self.red_kings +=1


	def remove(self, pieces):
		#print(f'Black: {self.red_left} White: {self.white}')
		for piece in pieces:
			self.board[piece.row][piece.col]=0
			if piece != 0:
				if piece.color == RED:
					self.red_left -= 1
				else:
					self.white_left -= 1

	def checkWin(self):
		if self.red_left <=0:
			return 'whitewin'
			#white win
		elif self.white_left <=0:
			return 'blackwin'
			#Black win
		else:
			return False



		





	