import numpy as np
import pickle


class Connect4State:

    def __init__(self, n_rows, n_cols, board=None):

        # store board variables
        self.n_rows = n_rows
        self.n_cols = n_cols

        # get board configuration from parent node if it is not the root node
        # compute available columns for the state
        self.board          = board if board is not None else np.zeros((self.n_rows, self.n_cols), dtype=int)
        self.allowed_cols   = self.init_allowed_cols()

    
    def __str__(self):

        s = ""
        # print board rows in reverse order
        # if only the columns chosen are used, then same states with distinct histories will have different string representations
        # using whole board is instead a unique identifier
        for row in self.board[::-1]:
            for col in row:
                s += str(col)
            s += "-"
        s = s[:-1]

        return s
    
    
    def init_allowed_cols(self):
        
        l = []
        for col in range(self.n_cols):

            # all columns with an empty space are allowed
            if np.any(self.board[:, col] == 0):
                l.append(col)
        l = np.array(l)
        
        # order columns by distance from the center
        # this is done to evaluate central moves first in the minimax and prune the tree faster
        sort_idx = np.argsort(np.abs(l - self.n_cols/2 + 1/self.n_cols))
        l_sort = l[sort_idx]
        
        return l_sort
    

    def add_disc(self, idx_c, player):

        # create new board and add disc to the chosen column
        board_n                 = self.board.copy()
        idx_r                   = np.argmax(self.board[:, idx_c] == 0) if np.sum(self.board[:, idx_c] > 0) else 0
        board_n[idx_r, idx_c]   = player

        # return new state
        # storing all children for all states would be too memory-intensive and with redundant information
        # this is not properly a tree, but it acts as such
        return Connect4State(
            n_rows  = self.n_rows,
            n_cols  = self.n_cols,
            board   = board_n
        )


    def get_win_cols(self, player):

        l = []
        for col in self.allowed_cols:

            # evaluate all possible moves
            # store in the list all columns that immediately lead to a win
            child = self.add_disc(col, player)
            if child.check_alignments(4, player):
                l.append(col)
                break
    
        return l
    

    def get_lose_cols(self, player):
        
        l = []
        for col in self.allowed_cols:

            # evaluate all possible moves
            # switch player to evaluate all possible moves for the opponent
            child   = self.add_disc(col, player)
            player_ = 3-player
            for col_ in child.allowed_cols:

                # evaluate all possible moves for the opponent
                # store in the list all columns that immediately lead to a loss if the opponent play optimally
                child_ = child.add_disc(col_, player_)
                if child_.check_alignments(4, player_):
                    l.append(col)
                    break
        
        return l


    def get_playable_cols(self, player):

        # if there are some winning moves, then just return them
        win_cols = self.get_win_cols(player)
        if len(win_cols) > 0:
            return win_cols

        l = self.allowed_cols.copy()
        # l = self.sort_cols(self.allowed_cols.copy(), player)

        for col in self.get_lose_cols(player):
        
            # otherwise, return just the moves that do not lead to an immediate loss
            # remove the losing columns from the allowed columns
            if len(l) > 1:
                l = np.delete(l, np.where(l == col))
        
        return l


    def is_root(self):
        return np.all(self.board == 0)
    

    def is_terminal(self):
        return self.check_alignments(4, 1) or self.is_full() or self.check_alignments(4, 2)
    

    def is_full(self):
        return not np.any(self.board == 0)


    def score_fun(self, player):
        return n_rows*n_cols//2 + 1 - np.sum(self.board == player)
    

    def sort_cols(self, cols, player):

        alignments_count = np.zeros(len(cols))
        for c in range(len(cols)):

            child = self.add_disc(cols[c], player)
            alignments_count[c] = child.check_alignments(3, player, return_count=True)
        
        # sort columns by number of alignments
        # if there is a draw, then keep the original ordering
        sort_idx = np.argsort(alignments_count)[::-1]

        # print("cols : {}, alignment count : {}".format(cols, alignments_count))

        l_sort = np.empty(len(cols), dtype=int)
        for i in range(len(cols)):

            count_eq = alignments_count == alignments_count[sort_idx[i]]
            if np.sum(count_eq) > 1:

                max_count_col   = alignments_count[sort_idx[i]]
                count_eq_idx    = np.where(count_eq)

                replace_idx     = []
                for j in range(len(cols)):
                    if alignments_count[sort_idx[j]] == max_count_col:
                        replace_idx.append(j)

                l_sort[replace_idx] = cols[count_eq_idx]

            else:
                l_sort[i] = cols[sort_idx[i]]

        # print("l_sort : {}".format(l_sort))
        
        return l_sort


    ### QUESTO CODICE FA SCHIFO


    # def eval(self):

    #     # distinguish between maximizer and minimizer for the minimax algorithm
    #     if self.check_alignments():
    #         return 1 if self.player == 1 else -1
    #     else:
    #         return 0
        

    # def check_alignments(self):
            
    #     # check diagonals if there are more rows than columns
    #     for row in range(self.n_rows-3):
    #         diag1, diag2 = get_diagonals(self.board, -row)
    #         if np.all(diag1 == diag1[0]) and diag1[0] != 0 or np.all(diag2 == diag2[0]) and diag2[0] != 0:
    #             return True

    #     # check rows
    #     for row in range(self.n_rows):
    #         for col in range(self.n_cols-3):
    #             board_sub = self.board[row, col:col+4]
    #             if np.all(board_sub == board_sub[0]) and board_sub[0] != 0:
    #                 return True
        
    #     # check diagonals if there are more columns than rows
    #     for col in range(1, self.n_cols-3):
            
    #         diag1, diag2 = get_diagonals(self.board, col)
    #         if np.all(diag1 == diag1[0]) and diag1[0] != 0 or np.all(diag2 == diag2[0]) and diag2[0] != 0:
    #             return True

    #     # check columns
    #     for col in range(self.n_cols):
    #         for row in range(self.n_rows-3):
    #             board_sub = self.board[row:row+4, col]
    #             if np.all(board_sub == board_sub[0]) and board_sub[0] != 0:
    #                 return True
        
    #     return False

    def check_alignments(self, len, player, return_count=False):

        # initialize count
        # c = 0

        # check alignments if there are more rows than columns
        # if that is the case, then more diagonals on the width than on the height needs to be checked
        for row in range(self.n_rows):

            # check all possible horizontal alignments
            for col in range(self.n_cols-len+1):
                board_sub = self.board[row, col:col+len]
                if np.all(board_sub == player):
                    return True
            
            # check all possible primary and secondary diagonal alignments
            if row < self.n_rows-len+1:
                diag1, diag2 = get_diagonals(self.board, row)
                if np.all(diag1 == player) or np.all(diag2 == player):
                    return True
        
        # check alignments if there are more columns than rows
        # if that is the case, then more diagonals on the height than on the width needs to be checked
        for col in range(self.n_cols):

            # check all possible vertical alignments
            for row in range(self.n_rows-len+1):
                board_sub = self.board[row:row+len, col]
                if np.all(board_sub == player):
                    return True
            
            # check all possible primary and secondary diagonal alignments
            if col in range(1, self.n_cols-len+1):
                diag1, diag2 = get_diagonals(self.board, col)
                if np.all(diag1 == player) or np.all(diag2 == player):
                    return True
        
        # return c if return_count else c > 0
        return False
    

    def eval(self, player):

        # check if the opponent has won
        # if so, then a negative score needs to be returned for the current player
        prev_player = 3-player
        if self.check_alignments(4, prev_player):
            return -self.score_fun(prev_player)
        else:
            return 0


def get_diagonals(arr, idx):

    # get main and secondary diagonal separately
    diag1 = np.diag(arr, k=idx)
    diag2 = np.diag(np.fliplr(arr), k=idx)

    return diag1, diag2


# def minimax(state, maximizer, alpha=-float("inf"), beta=+float("inf"), memo=None):

#     # # convert player position number to boolean
#     # maximizer = True

#     if state.is_terminal():
#         # return evaluation for the player at terminal state
#         return None, state.eval(2 if maximizer else 1), memo
    
#     if memo is None:
#         # initialize memo at first call
#         memo = {
#             "maximizer": dict(),
#             "minimizer": dict()
#         }
    
#     key = "maximizer" if maximizer else "minimizer"
#     if str(state) in memo[key]:
#         if memo[key][str(state)]["eval"] > 0:
#             # return memoized value if optimized
#             return None, memo[key][str(state)]["eval"], memo
    
#     if maximizer:
#         # initialize maximum evaluation and best move
#         max_move = None
#         max_eval = -np.inf

#         for column in state.allowed_cols:
#             child = state.add_disc(column, 1)
#             _, eval, memo = minimax(child, False, alpha, beta, memo)

#             if eval > max_eval:
#                 max_move = column
#                 max_eval = eval
            
#             alpha = max(alpha, eval)
#             if beta <= alpha:
#                 break

#         # store best move and evaluation in memo
#         memo["maximizer"][str(state)] = {
#             "move": max_move,
#             "eval": max_eval
#         }
#         return max_move, max_eval, memo
    
#     else:
#         # initialize minimum evaluation and best move
#         min_move = None
#         min_eval = np.inf

#         for column in state.allowed_cols:
#             child = state.add_disc(column, 2)
#             _, eval, memo = minimax(child, True, alpha, beta, memo)

#             if eval < min_eval:
#                 min_move = column
#                 min_eval = eval
            
#             beta = min(beta, eval)
#             if beta <= alpha:
#                 break
        
#         # store best move and evaluation in memo
#         memo["minimizer"][str(state)] = {
#             "move": min_move,
#             "eval": min_eval
#         }
#         return min_move, min_eval, memo


def negamax(state, depth, maximizer, alpha=-float("inf"), beta=+float("inf"), memo=None):

    # convert maximizer boolean to player number
    # this is done to indicate the moves on the board and produce an identifier
    player = 1 if maximizer else 2

    if depth == 0 or state.is_terminal():
        # return evaluation for the player at terminal state
        # with negamax we are not distinguishing between maximizer and minimizer and the evaluation is the same
        # evaluate wrt the previous player
        return None, state.eval(player), memo
    
    if memo is None:
        # initialize memo at first call
        # this is also useful to reduce computational time in the search
        # acts as a hash table
        memo = dict()

    if str(state) in memo and memo[str(state)]["eval"] > 0:
        # return memoized value if optimized
        return memo[str(state)]["move"], memo[str(state)]["eval"], memo
    
    # initialize best evaluation and best move
    best_move = None
    best_eval = -np.inf

    # print("state : {}, allowed_cols: {},  \tplayer : {}, playable_cols : {}".format(str(state), state.allowed_cols, player, state.get_playable_cols(player)))

    for column in state.get_playable_cols(player):
        # call recursion on children to evaluate all possible moves
        child           = state.add_disc(column, player)
        _, eval, memo   = negamax(child, depth-1, not maximizer, -beta, -alpha, memo)
        # switch sign of evaluation for current player
        eval            = -eval

        # update best move and evaluation
        if eval > best_eval:
            best_move = column
            best_eval = eval
        
        # prune tree if best evaluation was already found
        # this is done to reduce computation
        alpha = max(alpha, eval)
        if beta <= alpha:
            break

    # store best move and evaluation in memo
    # this is guaranteed to be the best move and evaluation for the current state
    memo[str(state)] = {
        "move": best_move,
        "eval": best_eval
    }

    return best_move, best_eval, memo




n_rows = 5
n_cols = 6

root        = Connect4State(n_rows, n_cols)

# _, _, memo  = negamax(root, 5, True)
# print(memo)

# with open(f"assets/connect 4/solution_{n_rows}x{n_cols}.pkl", "wb") as f:
#     pickle.dump(memo, f)

