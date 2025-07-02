import streamlit as st
from src.chomp.chomp_minimax import *
from time import sleep


### -------------------------------------------------- ###
### --- SESSION STATE -------------------------------- ###


def init_chomp_state():
    if "chomp" not in st.session_state:
        st.session_state["chomp"] = {
            "bot_sigma": dict(),
            "end_game": None,
            "n_rows": 2,
            "n_cols": 2,
            "game_on": False,
            "game_hist": [],
            "game_state": ChompState(2, 2),
            "last_cell": (2, 2),
            "user": 1,
        }


### -------------------------------------------------- ###
### --- STATE FUNCTIONS ------------------------------ ###


def set_chomp_state(key, val):
    """Set a key in the chomp state."""

    st.session_state.chomp[key] = st.session_state[val]

    # Reset table if height or width are changed and instantiate new root
    if key == "n_rows" or key == "n_cols":
        n_rows = st.session_state.chomp["n_rows"]
        n_cols = st.session_state.chomp["n_cols"]
        st.session_state.chomp["game_state"] = ChompState(n_rows=n_rows, n_cols=n_cols)
        st.session_state.chomp["last_cell"] = (n_rows, n_cols)


### -------------------------------------------------- ###
### --- GAME FUNCTIONS ------------------------------- ###


def play():
    """
    Start the game and compute the optimal strategy for the bot.
    Then, let the bot move if necessary.
    """

    # Start the game
    st.session_state.chomp["game_on"] = True

    # Compute the optimal strategy
    _, _, sigma = negamax(st.session_state.chomp["game_state"], True)
    st.session_state.chomp["bot_sigma"] = sigma

    # If the user is in position 2, then let the bot move
    if st.session_state.chomp["user"] == 2:
        sleep(1)
        bot_move = bot_action(
            bot_sigma=st.session_state.chomp["bot_sigma"],
            state=st.session_state.chomp["game_state"],
        )

        # Append it to history
        st.session_state.chomp["game_state"] = st.session_state.chomp[
            "game_state"
        ].bite(*bot_move)
        st.session_state.chomp["game_hist"].append(
            "Player 1 bites at {}".format(bot_move)
        )


def move(x, y):
    """
    Apply a move to the game state and update the session state.
    Then, terminate the game if a terminal state is reached, or let the bot make its move.

    :param x: The row index of the cell to bite.
    :param y: The col index of the cell to bite.
    """

    # Get the current state
    state = st.session_state.chomp["game_state"]

    # If the top-left cell is bitten, then terminate game with a lose
    if x == 0 and y == 0:
        end_game("game over")
    else:
        # Otherwise, apply the move and append it to history
        state_n = state.bite(x, y)
        st.session_state.chomp["game_state"] = state_n
        st.session_state.chomp["last_cell"] = (x, y)
        st.session_state.chomp["game_hist"].append(
            "Player {} bites at {}".format(st.session_state.chomp["user"], (x, y))
        )

        # If the move leads to terminal state, then terminate the game with a win
        if state_n.is_terminal():
            end_game("user wins")
        else:
            # Otherwise, let the bot make its move
            # This sleep command is actually not perceived because the page is only updated at the end of the function
            sleep(1)
            bot_move = bot_action(
                bot_sigma=st.session_state.chomp["bot_sigma"], state=state_n
            )
            state_n = state_n.bite(*bot_move)

            # Append it to history
            st.session_state.chomp["game_state"] = state_n
            st.session_state.chomp["last_cell"] = bot_move
            st.session_state.chomp["game_hist"].append(
                "Player {} bites at {}".format(
                    3 - st.session_state.chomp["user"], bot_move
                )
            )


def bot_action(bot_sigma, state):
    """
    Get the bot's move based on the current state.

    :param bot_sigma: The bot's strategy dictionary.
    :param state: The current game state.

    :return: The bot's move
    """

    # Return bot's strategy at the given state
    return bot_sigma[str(state)]["move"]


def end_game(status):
    """Terminate the game and update the end status."""

    # Update game variables
    # According to the end game status, different messages will be displayed
    st.session_state.chomp["end_game"] = status
    st.session_state.chomp["game_on"] = False


def reset():
    """Reset the game state and variables."""

    # Reset the table and instantiate a new root
    n_rows = st.session_state.chomp["n_rows"]
    n_cols = st.session_state.chomp["n_cols"]
    st.session_state.chomp["game_state"] = ChompState(n_rows=n_rows, n_cols=n_cols)
    st.session_state.chomp["last_cell"] = (n_rows - 1, n_cols - 1)

    # Reset the game variables
    st.session_state.chomp["game_hist"] = []
    st.session_state.chomp["end_game"] = None
