from components.c4 import render_connect4
from src.c4.c4_st import *
import streamlit as st
import numpy as np


### -------------------------------------------------- ###
### --- GAME RULES ----------------------------------- ###


st.markdown(
    """
    # Connect 4 in a row 🎮
    ---
    ### Rules

    Connect 4 is probably one of the most popular games of all.  
    The two players take turns to drop a disc into a grid, which will fall to the lowest available position  
    into the selected column.

    The scope of the game is to be the first to connect 4 discs together either in a row, column or diagonal.
    Hence, each player should form his line while preventing his opponent from doing the same.
    """
)

with st.expander("Tip"):
    st.markdown(
        """
        Player 1 has always a winning strategy, while player 2 must hope for an opponent's mistake to win, so choose your position accordingly!
        """
    )

st.markdown(
    """
    **Note**: The CPU is not yet optimized, so you have a chance to win against it!
    
    ---
    ### Settings
    
    Choose your position in the game.
    """
)

game_on = st.session_state.connect4["game_on"]
end_status = st.session_state.connect4["end_status"]


user_ = st.radio(
    key="connect4_user_",
    label="User position",
    options=[1, 2],
    index=st.session_state.connect4["user"] - 1,
    disabled=game_on or not end_status is None,
    on_change=set_connect4_state,
    args=("user", "connect4_user_"),
)


### -------------------------------------------------- ###
### --- BOARD ---------------------------------------- ###


# Flip the board vertically before rendering
flipped_board = np.flipud(st.session_state.connect4["game_state"].board).tolist()
click = render_connect4(grid=flipped_board, game_on=game_on)
if click and "column" in click:
    column = click["column"]
    move(column)
    st.rerun()


### -------------------------------------------------- ###
### --- GAME BUTTONS --------------------------------- ###


cols = st.columns((0.12, 0.15, 0.14, 0.84))

with cols[0]:
    play_ = st.button(
        key="connect4_play_",
        label="Play",
        disabled=game_on or not st.session_state.connect4["game_state"].is_root(),
        on_click=play,
    )

with cols[1]:
    resign_ = st.button(
        key="connect4_resign_",
        label="Resign",
        disabled=not game_on,
        on_click=terminate_game,
        args=("quit",),
    )

with cols[2]:
    reset_ = st.button(
        key="connect4_reset_",
        label="Reset",
        disabled=end_status is None,
        on_click=reset,
    )


### -------------------------------------------------- ###
### --- RESULTS -------------------------------------- ###


if end_status is not None:

    if end_status == "bot wins":
        st.error("You lost against the bot 💩")
    if end_status == "quit":
        st.warning("You resigned 🎈")
    if end_status == "draw":
        st.info("It's a draw 🤝")
    if end_status == "user wins":
        st.success("You won 🏆")
