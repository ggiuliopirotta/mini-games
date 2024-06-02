import streamlit as st
from    connect_4_st import *

### ---------------------------------------------------------------------------------------------------- ###
### RULES OF THE GAME


st.markdown(
    '''
    # Connect 4 in a row 🎮

    ---

    ### Rules

    Connect 4 is probably one of the most popular games of all.  
    The two players take turns to drop a disc into a grid, which will fall to the lowest available position  
    into the selected column.

    The scope of the game is to be the first to connect 4 discs together either in a row, column or diagonal.
    Hence, each player should form his line while preventing his opponent from doing the same.
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

game_on     = st.session_state.connect4["game_on"]
end_status  = st.session_state.connect4["end_game"]

cols        = st.columns((0.2, 0.2, 0.6))

with cols[0]:
    n_rows_ = st.number_input(
        key         = "connect4_n_rows_",
        label       = "Board rows",
        min_value   = 2,
        max_value   = 7,
        step        = 1,
        disabled    = game_on or not end_status is None,
        on_change   = set_connect4_state,
        args        = ("n_rows", "connect4_n_rows_")
    )

with cols[1]:
    n_cols_ = st.number_input(
        key         = "connect4_n_cols_",
        label       = "Board columns",
        min_value   = 2,
        max_value   = 7,
        step        = 1,
        disabled    = game_on or not end_status is None,
        on_change   = set_connect4_state,
        args        = ("n_cols", "connect4_n_cols_")
    )

user_ = st.radio(
    key         = "connect4_user_",
    label       = "User position",
    options     = ["1", "2"],
    index       = int(st.session_state.connect4["user"])-1,
    disabled    = game_on or not end_status is None,
    on_change   = set_connect4_state,
    args        = ("user", "connect4_user_")
)


### ---------------------------------------------------------------------------------------------------- ###
### GAME BOARD


for x in range(st.session_state.connect4["n_rows"]):
    _, c, _ = st.columns((0.4, connect4_col[st.session_state.connect4["n_cols"]], 0.4))
    cols    = c.columns(tuple(0.1 for _ in range(st.session_state.connect4["n_cols"])))

    for y in range(st.session_state.connect4["n_cols"]):

        with cols[y]:

            board_ud = st.session_state.connect4["game_state"].board[::-1]
            if board_ud[x, y] == 0:
                s = "###### $~~~$.."
            else:
                s = "### 🔴" if board_ud[x, y] == 1 else "### 🟡"

            st.markdown(s)


### ---------------------------------------------------------------------------------------------------- ###
### GAME BUTTONS

st.markdown(
    '''
    Choose a column to place your disc.  
    Notice that the columns are indexed at 0, meaning that 0 stands for the first column etc...
    '''
)

cols = st.columns((0.28, 0.2, 0.5))

with cols[0]:
    col_ = st.selectbox(
        key         = "connect4_col_",
        label       = "Choose column to place disc",
        label_visibility    = "collapsed",
        options     = np.sort(st.session_state.connect4["game_state"].allowed_cols),
        index       = None,
        disabled    = not game_on
    )

with cols[1]:
    place_ = st.button(
        key         = "connect4_place_",
        label       = "Place disc",
        disabled    = col_ is None,
        on_click    = move,
        args        = (col_,)
    )

cols = st.columns((0.12, 0.15, 0.14, 0.84))

with cols[0]:
    play_ = st.button(
        key         = "chomp_play_",
        label       = "Play",
        disabled    = game_on or not st.session_state.connect4["game_state"].is_root(),
        on_click    = play,
    )

with cols[1]:
    resign_ = st.button(
        key         = "chomp_resign_",
        label       = "Resign",
        disabled    = not game_on,
        on_click    = end_game,
        args        = ("quit",)
    )

with cols[2]:
    reset_ = st.button(
        key         = "chomp_reset_",
        label       = "Reset",
        disabled    = end_status is None,
        on_click    = reset,
    )

st.markdown("Game stages (coordinates are indexed at 0):")
st.write(st.session_state.connect4["game_hist"])

if end_status is not None:

    if end_status == "game over":
        st.error("You lost against the bot 💩")

    if end_status == "quit":
        st.warning("You resigned 🎈")

    if end_status == "draw":
        st.info("It's a draw 🤝")

    if end_status == "user wins":
        st.success("You won against the bot 🏆")    
    

st.write(st.session_state.connect4)
st.write(str(st.session_state.connect4["game_state"]))
