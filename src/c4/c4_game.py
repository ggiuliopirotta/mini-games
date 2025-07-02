import numpy as np


class Connect4State:

    def __init__(self, n_rows, n_cols, board=None):

        # Store board variables
        self.n_rows = n_rows
        self.n_cols = n_cols
        # Get board configuration from parent node if it is not the root node
        self.board = (
            board
            if board is not None
            else np.zeros((self.n_rows, self.n_cols), dtype=int)
        )

    def __str__(self):

        s = ""
        # Print board rows in reverse order
        # If only the columns chosen are used, then same states with distinct histories will have different string representations
        # Using whole board is instead a unique identifier
        for row in self.board[::-1]:
            for col in row:
                s += str(col)
            s += "-"
        s = s[:-1]

        return s

    def add_disc(self, idx_c, player):
        """
        Add a disc to the board in the specified column for the given player.

        :param idx_c: Index of the column
        :param player: Player number (1 or 2)

        :return: New Connect4State
        """

        # Create a new board and add a disc to the chosen column
        board_n = self.board.copy()
        idx_r = (
            np.argmax(self.board[:, idx_c] == 0)
            if np.sum(self.board[:, idx_c] > 0)
            else 0
        )
        board_n[idx_r, idx_c] = player

        # Return the new state
        # Storing all children for all states would be too memory-intensive and with redundant information
        # This is not properly a tree, but it acts as such
        return Connect4State(n_rows=self.n_rows, n_cols=self.n_cols, board=board_n)

    def check_win(self, player):
        """
        Check if the specified player has a winning alignment of 4 discs.

        :param player: Player number (1 or 2)
        :return: True if the player has won, False otherwise
        """

        n_rows, n_cols = self.n_rows, self.n_cols

        # Check horizontal alignments
        for row in range(n_rows):
            for col in range(n_cols - 3):
                if np.all(self.board[row, col : col + 4] == player):
                    return True

        # Check vertical alignments
        for col in range(n_cols):
            for row in range(n_rows - 3):
                if np.all(self.board[row : row + 4, col] == player):
                    return True

        # Check main diagonals
        for row in range(n_rows - 3):
            for col in range(n_cols - 3):
                if all(self.board[row + i, col + i] == player for i in range(4)):
                    return True

        # Check secondary diagonals
        for row in range(3, n_rows):
            for col in range(n_cols - 3):
                if all(self.board[row - i, col + i] == player for i in range(4)):
                    return True

        return False

    def is_full(self):
        """Check if the board is full (no empty cells)."""
        return not np.any(self.board == 0)

    def is_root(self):
        """Check if the board is empty."""
        return np.all(self.board == 0)
