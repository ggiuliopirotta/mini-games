class ChompState:

    def __init__(self, n_rows, n_cols, last_r=None, last_c=None, parent_bites=None, n_bites=0):

        # store board size variables
        # the chomped cell corresponds to the bottom-right corner of the board
        self.n_rows     = n_rows
        self.n_cols     = n_cols

        # store indices of chomped cell
        self.last_r     = last_r # if last_r is not None else n_rows-1
        self.last_c     = last_c # if last_c is not None else n_cols-1

        # compute available bites for current state
        # parent bites are passed because just previously available bites are allowed here
        self.n_bites    = n_bites
        self.parent_bites = parent_bites
        self.bites      = self.init_allowed_bites(parent_bites)
    

    def __str__(self):

        s = ""
        # print all allowed bites for current state
        # if just the last chomped cell is used, then same states with distinct histories will have different string representations
        # using all allowed bites is instead a unique identifier
        for (x, y) in self.bites:
            s += str(x) + str(y) + "-"
        s = s[:-1]
        
        return s
    

    def bite(self, idx_r, idx_c):

        # return new state
        # storing all children for all states would be too memory-intensive and with redundant information
        # this is not properly a tree, but it acts as such
        return ChompState(
            n_rows          = self.n_rows,
            n_cols          = self.n_cols,
            last_r          = idx_r,
            last_c          = idx_c,
            parent_bites    = self.bites,
            n_bites         = self.n_bites + 1,
        )


    def init_allowed_bites(self, parent_bites):

        if self.is_root():
            # all cells are allowed at root state
            l = [(i, j) for i in range(self.n_rows) for j in range(self.n_cols)]
            # always discard poison cell
            l.pop(0)
        else:
            l = []

            # only previously available bites are allowed again
            for (i, j) in parent_bites:
                if i >= self.last_r and j >= self.last_c:
                    pass
                else:
                    l.append((i, j))
        return l
    

    def count_skipped_cells(self):
        return len(self.parent_bites) - len(self.bites) - 1
    

    def get_moves(self):
        return self.bites[::-1]


    def is_root(self):
        return self.n_bites == 0
    

    def is_terminal(self):
        return len(self.bites) == 0


# def negamax(state, maximizer, memo=None):
        
#     if state.is_terminal():
#         # return evaluation for the player at terminal state
#         # with negamax we are not distinguishing between maximizer and minimizer and the evaluation is the same
#         return None, -1, memo
    
#     if memo is None:
#         # initialize memo at first call
#         # this is also useful to reduce computational time in the search
#         # acts as a hash table
#         memo = dict()
    
#     if str(state) in memo and memo[str(state)]["eval"] == 1:
#         # return memoized values if optimized
#         return memo[str(state)]["move"], memo[str(state)]["eval"], memo
    
#     # initialize best evaluation and move
#     best_move = None
#     best_eval = -float("inf")

#     for (i, j) in state.bites:
#         # call recursion on children to evaluate all possible moves
#         child           = state.bite(i, j)
#         _, eval, memo   = negamax(child, not maximizer, memo)
#         # switch sign of the evaluation for current player
#         eval            = -eval

#         # update best move and evaluation
#         if eval > best_eval:
#             best_move = (i, j)
#             best_eval = eval
    
#     # store best move and evaluation in memo
#     # this is guaranteed to be the best move and evaluation for the current state
#     memo[str(state)] = {
#         "move": best_move,
#         "eval": best_eval
#     }

#     return best_move, best_eval, memo


def minimax(state, maximizer, memo=None):
    
    if state.is_terminal():
        # return evaluation for the player at terminal state
        # with minimax we are distinguishing between maximizer and minimizer
        return None, -state.score_fun(maximizer), memo
    
    if memo is None:
        # initialize memo at first call
        # this is also useful to reduce computational time in the search
        # acts as a hash table
        memo = {
            "max": dict(),
            "min": dict(),
        }

    key = "max" if maximizer else "min"
    if str(state) in memo[key] and memo[key][str(state)]["eval"] > 0:
        # return memoized values if optimized
        return memo[key][str(state)]["move"], memo[key][str(state)]["eval"], memo
    
    # initialize best evaluation and move
    if maximizer:
        best_eval = -float("inf")
        best_move = None

        for (i, j) in state.sort_bites():
            # call recursion on children to evaluate all possible moves
            child           = state.bite(i, j)
            _, eval, memo   = minimax(child, not maximizer, memo)

            # update best move and evaluation
            if eval > best_eval:
                best_move = (i, j)
                best_eval = eval
        
        # store best move and evaluation in memo
        # this is guaranteed to be the best move and evaluation for the current state
        memo[key][str(state)] = {
            "move": best_move,
            "eval": best_eval
        }
    
    else:
        best_eval = +float("inf")
        best_move = None

        for (i, j) in state.sort_bites():
            # call recursion on children to evaluate all possible moves
            child           = state.bite(i, j)
            _, eval, memo   = minimax(child, not maximizer, memo)

            # update best move and evaluation
            if eval < best_eval:
                best_move = (i, j)
                best_eval = eval
        
        # store best move and evaluation in memo
        # this is guaranteed to be the best move and evaluation for the current state
        memo[key][str(state)] = {
            "move": best_move,
            "eval": best_eval
        }
    
    return best_move, best_eval, memo
    
    


def negamax(state, maximizer, alpha=-float("inf"), beta=+float("inf"), memo=None):
        
    if state.is_terminal():
        # return evaluation for the player at terminal state
        # with negamax we are not distinguishing between maximizer and minimizer and the evaluation is the same
        return None, -state.score_fun(maximizer), memo
        # return None, -1, memo
    
    if memo is None:
        # initialize memo at first call
        # this is also useful to reduce computational time in the search
        # acts as a hash table
        memo = dict()
    
    if str(state) in memo and memo[str(state)]["eval"] > 0:
        # return memoized values if optimized
        return memo[str(state)]["move"], memo[str(state)]["eval"], memo
    
    # initialize best evaluation and move
    best_move = None
    best_eval = -float("inf")

    for (i, j) in state.bites:
        # call recursion on children to evaluate all possible moves
        child           = state.bite(i, j)
        _, eval, memo   = negamax(child, not maximizer, -beta, -alpha, memo)
        # switch sign of the evaluation for current player
        eval            = -eval

        # update best move and evaluation
        if eval > best_eval:
            best_move = (i, j)
            best_eval = eval
        
        # prune tree if best evaluation was already found
        # this is done to reduce computation
        # alpha = max(alpha, eval)
        # if alpha >= beta:
        #     break
    
    # store best move and evaluation in memo
    # this is guaranteed to be the best move and evaluation for the current state
    memo[str(state)] = {
        "move": best_move,
        "eval": best_eval
    }

    return best_move, best_eval, memo

root = ChompState(3, 3)
# root.bite(2, 2)
# print(root.is_root())
# _, _, memo = minimax(root, True)
# print(memo)

a = root.bite(1, 1)
print(a.count_skipped_cells())