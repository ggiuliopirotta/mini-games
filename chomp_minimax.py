### ---------------------------------------------------------------------------------------------------- ###
### GAME NODES


class ChompState:

    def __init__(self, n_rows, n_cols, last_r=None, last_c=None, parent_bites=None, skipped_bites=0):

        # store board size variables
        # the chomped cell corresponds to the bottom-right corner of the board
        self.n_rows     = n_rows
        self.n_cols     = n_cols

        # store indices of chomped cell
        self.last_r     = last_r
        self.last_c     = last_c

        # compute available bites for current state
        # parent bites are passed because just previously available bites are allowed here
        self.bites          = self.init_allowed_bites(parent_bites)
        self.skipped_bites  = skipped_bites + self.count_skipped_cells(parent_bites)
    

    def __str__(self):

        s = ""
        # print all allowed bites for current state
        # if just the last chomped cell is used, then same states with distinct histories will have different string representations
        # using all allowed bites is instead a unique identifier
        for (x, y) in self.bites:
            s += str(x) + str(y) + "-"
        s = s[:-1]
        
        return s


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
    

    def count_skipped_cells(self, parent_bites):
        return 0 if self.is_root() else len(parent_bites) - len(self.bites) - 1
    

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
            skipped_bites   = self.skipped_bites,
        )


    def is_root(self):
        return self.last_r is None and self.last_c is None
    

    def is_terminal(self):
        return len(self.bites) == 0
    

### ---------------------------------------------------------------------------------------------------- ###
### NEGAMAX FUNCTION


def negamax(state, maximizer, memo=None):
        
    if state.is_terminal():
        # return evaluation for the player at terminal state
        # with negamax there is no distinction between maximizer and minimizer and the evaluation is the same
        return None, -1, memo
    
    if memo is None:
        # initialize memo at first call
        # this is also useful to reduce computational time in the search
        # acts as a hash table
        memo = dict()
    
    if str(state) in memo and memo[str(state)]["eval"] > 0:
        # return memoized values if optimized
        return memo[str(state)]["move"], memo[str(state)]["eval"], memo
    
    # initialize best evaluation and move
    best_move   = None
    max_eval    = -float("inf")

    # initalize count of skipped moves
    # this is done because if two moves have the same evaluation, another criterion is needed
    # the maximizer aims to maximize it and the minimizer aims to minimize it
    n_skipped   = -float("inf") if maximizer else +float("inf")

    for (i, j) in state.bites:
        # call recursion on children to evaluate all possible moves
        child           = state.bite(i, j)
        _, eval, memo   = negamax(child, not maximizer, memo)
        # switch sign of the evaluation for current player
        eval            = -eval

        # update best move and evaluation if current move is better
        if eval > max_eval:
            best_move   = (i, j)
            max_eval    = eval

        # update best move and evaluation if current move is not better but as good
        if eval == max_eval:
            if (maximizer and child.skipped_bites > n_skipped) or (not maximizer and child.skipped_bites < n_skipped):
                best_move   = (i, j)
                max_eval    = eval
        
    # store best move and evaluation in memo
    # this is guaranteed to be the best move and evaluation for the state
    memo[str(state)] = {
        "move": best_move,
        "eval": max_eval
    }

    return best_move, max_eval, memo
