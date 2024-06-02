from    connect_4_minimax import *
from    time import sleep
import  streamlit as st
import  pickle


if "connect4" not in st.session_state:

    st.session_state["connect4"] = {
        "bot"           : "minimizer",
        "bot_sigma"     : dict(),
        "end_game"      : None,
        "n_rows"        : 2,
        "n_cols"        : 2,
        "game_on"       : False,
        "game_hist"     : [],
        "game_state"    : Connect4State(2, 2),
        "user"          : "1"
    }


connect4_col = {
    2: 0.143,
    3: 0.24,
    4: 0.35,
    5: 0.485,
    6: 0.65,
    7: 0.855,
}


def set_connect4_state(key, val):
    st.session_state.connect4[key] = st.session_state[val]
    
    if key == "n_rows" or key == "n_cols":
        st.session_state.connect4["game_state"] = Connect4State(
            n_rows = st.session_state.connect4["n_rows"],
            n_cols = st.session_state.connect4["n_cols"],
        )
    
    if key == "user":
        st.session_state.connect4["bot"] = "maximizer" if st.session_state[val] == "2" else "minimizer"


def move(*col):

    state = st.session_state.connect4["game_state"]

    state_n = state.add_disc(*col)
    st.session_state.connect4["game_state"] = state_n
    st.session_state.connect4["game_hist"].append("Player {} places disc at column {}".format(st.session_state.connect4["user"], *col))
    
    if state_n.is_terminal():
        if state_n.check_win():
            end_game("user wins")
        else:
            end_game("draw")
    else:

        sleep(1)
        bot_move    = bot_action(
            bot_sigma   = st.session_state.connect4["bot_sigma"],
            state       = state_n
        )
        state_n     = state_n.add_disc(*bot_move)

        st.session_state.connect4["game_state"] = state_n
        st.session_state.connect4["game_hist"].append("Player {} places disc at column {}".format(3-int(st.session_state.connect4["user"]), *bot_move))
    
        if state_n.is_terminal():
            if state_n.check_win():
                end_game("game over")
            else:
                end_game("draw")


def play():
    st.session_state.connect4["game_on"] = True

    st.session_state.connect4["game_hist"].append("The game is started")

    # _, _, sigma = negamax(st.session_state.connect4["game_state"])
    # st.session_state.connect4["bot_sigma"] = sigma

    with open(f"assets/connect 4/solution{st.session_state.connect4["n_rows"]}x{st.session_state.connect4["n_rows"]}.pkl", "rb") as f:
        sigma = pickle.load(f)
    st.session_state.connect4["bot_sigma"] = sigma[st.session_state.connect4["bot"]]


    if st.session_state.connect4["bot"] == "maximizer":
        sleep(1)
        bot_move = bot_action(
            bot_sigma   = st.session_state.connect4["bot_sigma"],
            state       = st.session_state.connect4["game_state"],
        )

        st.session_state.connect4["game_state"] = st.session_state.connect4["game_state"].add_disc(*bot_move)
        st.session_state.connect4["game_hist"].append("Player 1 places disc at column {}".format(*bot_move))

    st.write(str(st.session_state.connect4["game_state"]))

def reset():
    
    st.session_state.connect4["game_state"] = Connect4State(
            n_rows = st.session_state.connect4["n_rows"],
            n_cols = st.session_state.connect4["n_cols"],
        )
    
    st.session_state.connect4["game_hist"] = []
    st.session_state.connect4["end_game"]  = None


def bot_action(bot_sigma, state):
    return (bot_sigma[str(state)]["move"], )


def end_game(status):
    
    st.session_state.connect4["game_hist"].append("Game over")
    st.session_state.connect4["end_game"]  = status
    st.session_state.connect4["game_on"]   = False
