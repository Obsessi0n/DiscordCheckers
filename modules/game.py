from .board import Board
from .constants import RED, WHITE
from copy import deepcopy

class Game:

	def __init__(self):
		self._init()

	
	def _init(self):
	#	self.turn = RED
		pass

	#def change_turn(self):
	#	if self.turn == RED:
	#		self.turn = WHITE
	#	else:
	#		self.turn = RED



	def move(self,  selectedRow, selectedCol, row, col, board):
		
		currentBoard = board

		#Peça a mover e obter possiveis movimentos
		piece = currentBoard.get_piece(selectedRow, selectedCol)

		if piece != 0 and piece.color == currentBoard.turn:
			selected = piece
			valid_moves = currentBoard.get_valid_moves(piece)
		elif piece!=0:
			return 'You didnt select a piece'
		else:
			return False



		#Mover a peça
		piece = currentBoard.get_piece(row, col)
		if selected and piece == 0 and (row, col) in valid_moves:
			currentBoard.move(selected, row, col)
			skipped = valid_moves[(row, col)]

			if skipped:
				currentBoard.remove(skipped)
				if currentBoard.checkWin() != False:
					return currentBoard.checkWin()

			#self.change_turn()
			currentBoard.changeTurn()
		else:
			return False

		currentBoard.updateBoardImage(True,0)

		return True

	##AI##
	def getBoard(self):
		return self.board

	def aiMove(self, originalboard,newboard):
		originalboard = deepcopy(newboard)
		return originalboard
		

		

