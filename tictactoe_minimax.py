import numpy as np


class TicTacToe:

    def __init__(self, board=None, moves=None):

        self.board = board if board is not None else np.zeros((3, 3))
        self.moves = moves if moves is not None else np.zeros((3, 3))

        self.allowed_moves = self.init_allowed_moves()

    def __str__(self):
        return str(self.board)
    

    def add_symbol(self, num, row, col, player):

        board_n = self.board.copy()
        moves_n = self.moves.copy()
        board_n[row, col] = num
        moves_n[row, col] = player

        return TicTacToe(board_n, moves_n)
    
    def is_terminal(self):
        return not np.any(self.board) == 0 or self.check_alignments()
    
    def is_root(self):
        return np.all(self.board == 0)
    

    def init_allowed_moves(self):
        return [(i, j) for i in range(3) for j in range(3) if self.board[i, j] == 0]
    

    def score_fun(self, player):
        return 3*3 // 2 + (1 if player == 1 else 0) - np.sum(self.moves == player)


    def check_alignments(self):
        
        for i in range(3):

            # check horizontal alignments
            if np.sum(self.board[i, :]) == 15:
                return True
            
            # check vertical alignments
            if np.sum(self.board[:, i]) == 15:
                return True
            
            # check primary and secondary diagonal alignments
            if np.sum(np.diag(self.board)) == 15 or np.sum(np.diag(np.fliplr(self.board))) == 15:
                return True

        return False
    


x = TicTacToe(np.zeros((3, 3)))
print(x.allowed_moves)