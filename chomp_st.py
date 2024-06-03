import streamlit as st
from chomp_minimax import *
from time import sleep


### ---------------------------------------------------------------------------------------------------- ###
### INITIALIZE SESSION STATE


if "chomp" not in st.session_state:

    st.session_state["chomp"] = {
        "bot_sigma"     : dict(),
        "end_game"      : None,
        "n_rows"        : 2,
        "n_cols"        : 2,
        "game_on"       : False,
        "game_hist"     : [],
        "game_state"    : ChompState(2, 2),
        "user"          : "1"
    }


# define game column
chomp_col = {
    2: 0.143,
    3: 0.24,
    4: 0.35,
    5: 0.485,
    6: 0.65,
    7: 0.855,
}


### ---------------------------------------------------------------------------------------------------- ###
### STATE FUNCTIONS


def set_chomp_state(key, val):
    st.session_state.chomp[key] = st.session_state[val]
    
    # reset table if height or width are changed and instantiate new root
    if key == "n_rows" or key == "n_cols":
        st.session_state.chomp["game_state"] = ChompState(
            n_rows = st.session_state.chomp["n_rows"],
            n_cols = st.session_state.chomp["n_cols"]
        )


### ---------------------------------------------------------------------------------------------------- ###
### GAME FUNCTIONS


def play():

    # start game
    st.session_state.chomp["game_on"] = True
    st.session_state.chomp["game_hist"].append("The game is started")

    # compute optimal strategy and store it in session state
    _, _, sigma                         = negamax(st.session_state.chomp["game_state"], True)
    st.session_state.chomp["bot_sigma"] = sigma

    # if user is in position 2, then let bot make its move first
    if st.session_state.chomp["user"] == "2":
        sleep(1)
        bot_move = bot_action(
            bot_sigma   = st.session_state.chomp["bot_sigma"],
            state       = st.session_state.chomp["game_state"]
        )

        # append it to history
        st.session_state.chomp["game_state"] = st.session_state.chomp["game_state"].bite(*bot_move)
        st.session_state.chomp["game_hist"].append("Player 1 bites at {}".format(bot_move))


def move(x, y):

    # get current state
    state = st.session_state.chomp["game_state"]

    # if top-left cell is bitten, then terminate game with a lose
    if x == 0 and y == 0:
        end_game("game over")
    else:

        # otherwise, apply move and append it to history
        state_n = state.bite(x, y)
        st.session_state.chomp["game_state"] = state_n
        st.session_state.chomp["game_hist"].append("Player {} bites at {}".format(st.session_state.chomp["user"], (x, y)))
    
        # if move leads to terminal state, then terminate game with a win
        if state_n.is_terminal():
            end_game("user wins")
        else:

            # otherwise, let bot make its move
            # this sleep command is actually not perceived because the page is only updated at the end of the function
            sleep(1)
            bot_move    = bot_action(
                bot_sigma   = st.session_state.chomp["bot_sigma"],
                state       = state_n
            )
            state_n     = state_n.bite(*bot_move)

            # append it to history
            st.session_state.chomp["game_state"] = state_n
            st.session_state.chomp["game_hist"].append("Player {} bites at {}".format(3-int(st.session_state.chomp["user"]), bot_move))


def bot_action(bot_sigma, state):
    # return bot's strategy at the given state
    return bot_sigma[str(state)]["move"]


def end_game(status):
    
    # append status to history
    st.session_state.chomp["game_hist"].append("Game over")

    # update game variables
    # according to end game status, different messages will be displayed
    st.session_state.chomp["end_game"]  = status
    st.session_state.chomp["game_on"]   = False


def reset():
    
    # reset table and instantiate new root
    st.session_state.chomp["game_state"] = ChompState(
            n_rows = st.session_state.chomp["n_rows"],
            n_cols = st.session_state.chomp["n_cols"]
        )
    
    # reset game variables
    st.session_state.chomp["game_hist"] = []
    st.session_state.chomp["end_game"]  = None
