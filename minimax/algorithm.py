from copy import deepcopy
from modules.board import Board

RED = (60, 60, 60)
WHITE = (255, 255, 255)

def minimax(position, depth, max_player):
    if depth == 0 or position.checkWin() != False:
        return position.evaluate(), position
    
    if max_player:
        maxEval = float('-inf')
        best_move = None
        for move in getAllMoves(position, WHITE):
            evaluation = minimax(move, depth-1, False)[0]
            maxEval = max(maxEval, evaluation)
            if maxEval == evaluation:
                best_move = move
        
        return maxEval, best_move
    else:
        minEval = float('inf')
        best_move = None
        for move in getAllMoves(position, RED):
            evaluation = minimax(move, depth-1, True)[0]
            minEval = min(minEval, evaluation)
            if minEval == evaluation:
                best_move = move
        
        return minEval, best_move


def simulate_move(piece, move, board ,skip):
	board.move(piece, move[0], move[1])
	if skip:
		board.remove(skip)

	return board



def getAllMoves(board, color):
    moves = []




    for piece in board.getAllPiecces(color):
        valid_moves = board.get_valid_moves(piece)
        for move, skip in valid_moves.items():
            board2 = Board(0, 0)
            #board2.createBoard()
            board2.userID = deepcopy(board.userID)
            board2.board = deepcopy(board.board)
            #board2.red_left = deepcopy(board.white_left)
            #board2.red_kings = deepcopy(board.white_kings)
            board2.turn = deepcopy(board.turn)

            temp_board = board2#deepcopy(board)

            temp_piece = temp_board.get_piece(piece.row, piece.col)

            new_board = simulate_move(temp_piece, move, temp_board, skip)
            moves.append(new_board)

    return moves