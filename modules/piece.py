from .constants import RED, WHITE, GREY, SQUARE_SIZE

class Piece:
	def __init__(self, row, col, color):
		self.row = row
		self.col = col
		self.color = color
		self.king = False



	def make_king(self):
		self.king = True

	def move(self, row, col):
		self.row = row
		self.col = col
		#self.calc_pos()

