from connect_4_minimax import *
import streamlit as st


### -------------------------------------------------- ###
### --- SESSION STATE -------------------------------- ###


def init_connect4_state():
    if "connect4" not in st.session_state:
        st.session_state["connect4"] = {
            "bot_sigma"     : dict(),
            "end_game"      : None,
            "n_rows"        : 6,
            "n_cols"        : 7,
            "game_on"       : False,
            "game_hist"     : [],
            "game_state"    : Connect4State(6, 7),
            "user"          : "1"
        }

init_connect4_state()


### -------------------------------------------------- ###
### --- STATE FUNCTIONS ------------------------------ ###


def set_connect4_state(key, val):
    st.session_state.connect4[key] = st.session_state[val]


### -------------------------------------------------- ###
### --- GAME FUNCTIONS ------------------------------- ###


def play():

    # Start game
    st.session_state.connect4["game_on"] = True
    st.session_state.connect4["game_hist"].append("The game is started")


def move(col):

    # Get the current state
    state = st.session_state.connect4["game_state"]
    player = st.session_state.connect4["user"]

    # Apply move and append it to history
    state_n = state.add_disc(col, player)
    st.session_state.connect4["game_state"] = state_n
    st.session_state.connect4["game_hist"].append("Player {} places disc at column {}".format(player, col))
    
    # If the move leads to terminal state, then end the game with a win or a draw accordingly
    if state_n.is_terminal():
        if state_n.check_win():
            end_game("user wins")
        else:
            end_game("draw")
    else:
        # Otherwise, let the bot play
        pass


def end_game(status):
    
    # Append status to history
    st.session_state.connect4["game_hist"].append("Game over")
    # Update the game variables
    # According to the end game status, different messages will be displayed
    st.session_state.connect4["end_game"] = status
    st.session_state.connect4["game_on"] = False


def reset():
    
    # Reset the board and instantiate a new root
    st.session_state.connect4["game_state"] = Connect4State(
            n_rows=st.session_state.connect4["n_rows"],
            n_cols=st.session_state.connect4["n_cols"],
        )
    
    # Reset the game variables
    st.session_state.connect4["game_hist"] = []
    st.session_state.connect4["end_game"] = None
