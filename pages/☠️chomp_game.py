from chomp_component import render_chomp
from chomp_st import *
import streamlit as st


### -------------------------------------------------- ###
### --- GAME RULES ----------------------------------- ###


st.markdown(
    '''
    # Chomp Game ☠️
    ---
    ### Rules

    Chomp is a simple, but tricky, game, and is played on a board resembling a chocolate bar.  
    The two players take turns to eat a piece of chocolate out of it, but when chomping, they will also remove all the pieces to the right and below the chosen one.

    Unfortunately, the top-left piece of chocolate is poisoned, so whoever eats it loses the game.  
    Hence, each player should try to force the opponent to eat the poisoned piece.
    '''
)

with st.expander("Tip"):
    st.markdown(
        '''
        Player 1 has always a winning strategy, while player 2 must hope for an opponent's mistake to win, so choose your position accordingly!
        '''
    )

st.markdown(
    '''
    ---
    ### Settings

    Choose the size of the board and your position in the game.
    '''
)


### -------------------------------------------------- ###
### --- GAME SETTINGS -------------------------------- ###


game_on = st.session_state.chomp["game_on"]
end_status = st.session_state.chomp["end_game"]

cols = st.columns((0.2, 0.2, 0.6))

with cols[0]:
    n_rows_ = st.number_input(
        key="chomp_n_rows_",
        label="Board rows",
        min_value=2,
        max_value=7,
        step=1,
        value=st.session_state.chomp["n_rows"],
        disabled=game_on or not end_status is None,
        on_change=set_chomp_state,
        args=("n_rows", "chomp_n_rows_")
    )

with cols[1]:
    n_cols_ = st.number_input(
        key="chomp_n_cols_",
        label="Board columns",
        min_value=2,
        max_value=7,
        step=1,
        value=st.session_state.chomp["n_cols"],
        disabled=game_on or not end_status is None,
        on_change=set_chomp_state,
        args=("n_cols", "chomp_n_cols_")
    )

user_ = st.radio(
    key="chomp_user_",
    label="User position",
    options=["1", "2"],
    index=int(st.session_state.chomp["user"])-1,
    disabled=game_on or not end_status is None,
    on_change=set_chomp_state,
    args=("user", "chomp_user_")
)


### -------------------------------------------------- ###
### --- BOARD ---------------------------------------- ###


clicked = render_chomp(n=n_rows_, m=n_cols_, available=st.session_state.chomp["game_state"].moves, game_on=game_on)
if clicked:
    row = clicked["row"]
    col = clicked["col"]
    move(row, col)
    st.rerun()


### -------------------------------------------------- ###
### --- GAME BUTTONS --------------------------------- ###


cols = st.columns((0.12, 0.15, 0.14, 0.84))

with cols[0]:
    play_ = st.button(
        key="chomp_play_",
        label="Play",
        disabled=game_on or not st.session_state.chomp["game_state"].is_root(),
        on_click=play,
    )

with cols[1]:
    resign_ = st.button(
        key="chomp_resign_",
        label="Resign",
        disabled=not game_on,
        on_click=end_game,
        args=("quit",)
    )

with cols[2]:
    reset_ = st.button(
        key="chomp_reset_",
        label="Reset",
        disabled=end_status is None,
        on_click=reset,
    )


### -------------------------------------------------- ###
### --- RESULTS -------------------------------------- ###


st.markdown("Game stages (coordinates are indexed at 0):")
st.write(st.session_state.chomp["game_hist"])

if end_status is not None:
    if end_status == "game over":
        st.error("You bit the poisoned chocolate 💀")
    if end_status == "quit":
        st.warning("You resigned 🎈")
    if end_status == "user wins":
        st.success("You won 🏆")
