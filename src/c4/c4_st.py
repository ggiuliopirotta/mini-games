from src.c4.c4_game import Connect4State
import os
import platform
import streamlit as st
import subprocess


### -------------------------------------------------- ###
### --- SESSION STATE -------------------------------- ###


def init_connect4_state():
    if "connect4" not in st.session_state:
        st.session_state["connect4"] = {
            "bot_level": 2,
            "end_status": None,
            "n_rows": 6,
            "n_cols": 7,
            "game_on": False,
            "game_state": Connect4State(6, 7),
            "game_descr": "",
            "user": 1,
        }


### -------------------------------------------------- ###
### --- STATE FUNCTIONS ------------------------------ ###


def set_connect4_state(key, val):
    """Set a key in the connect4 state."""
    st.session_state.connect4[key] = st.session_state[val]


def apply_move(col, new_state):
    """Apply a move to the game state and update the session state."""
    st.session_state.connect4["game_state"] = new_state
    st.session_state.connect4["game_descr"] += str(col)


### -------------------------------------------------- ###
### --- OPENINGS ------------------------------------- ###


def load_openings():
    """Load openings from text file into a dictionary."""
    openings = {}
    openings_path = os.path.join(os.getcwd(), "src", "c4", "openings.txt")
    with open(openings_path, "r") as f:
        for line in f:
            line = line.strip()
            position, move = line.split(":", 1)
            openings[position.strip()] = int(move.strip())
    return openings


def save_openings(openings):
    """Save openings dictionary to text file."""
    openings_path = os.path.join(os.getcwd(), "src", "c4", "openings.txt")
    with open(openings_path, "w") as f:
        for position, move in sorted(openings.items()):
            f.write(f"{position}:{move}\n")


### -------------------------------------------------- ###
### --- GAME FUNCTIONS ------------------------------- ###


def play():
    """Start the game and let the bot make its first move if needed."""

    # Start the game
    st.session_state.connect4["game_on"] = True
    player = st.session_state.connect4["user"]

    # If the player is in 2nd position, then let the bot move
    if player == 2:
        bot = 3 - player
        bot_move = get_bot_move(st.session_state.connect4["game_descr"])
        new_state = st.session_state.connect4["game_state"].add_disc(bot_move - 1, bot)
        apply_move(bot_move, new_state)


def move(col):
    """
    Make a move in the game and handle the game logic.
    Then, check if the game is over or if the bot needs to make a move.

    :param col: The column where to drop the disc.
    """

    # Get the state
    state = st.session_state.connect4["game_state"]
    player = st.session_state.connect4["user"]
    bot = 3 - player

    # Apply the move and append it
    new_state = state.add_disc(col, player)
    apply_move(col + 1, new_state)

    # Check if user's move ends the game
    if new_state.check_win(player):
        terminate_game("user wins")
        return
    elif new_state.is_full():
        terminate_game("draw")
        return

    # If game continues, get bot move
    bot_move = get_bot_move(st.session_state.connect4["game_descr"])
    if bot_move is None:
        return  # Error getting bot move

    new_state = new_state.add_disc(bot_move - 1, bot)
    apply_move(bot_move, new_state)

    # Check if bot's move ends the game
    if new_state.check_win(bot):
        terminate_game("bot wins")
    elif new_state.is_full():
        terminate_game("draw")


def get_bot_move(position):
    """
    Get the bot's move based on the current position.
    To do so, call the C4 solver executable with the position string.
    If the position is cached in the openings file, return it.

    :param position: The current game state as a string.

    :return: The column where to drop the disc.
    """

    # At the beginning, the best column is the central one
    if not position:
        return 4

    # Load current openings from file and check if we have a cached move
    openings = load_openings()
    if position in openings:
        return openings[position]

    exe_path = os.path.join(os.getcwd(), "src", "c4", "c4_solver")
    system = platform.system().lower()
    exe_path = exe_path.rsplit(".", 1)[0] if ".exe" in exe_path else exe_path
    command = ["wine64", exe_path] if system != "windows" else [exe_path]
    command.extend([position])

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
        )
        if result.returncode != 0:
            st.error("Error while getting bot move. Please retry.")
            return None
        move_col = int(result.stdout.strip())

        # Save this move to the openings and update the file
        if len(position) < 5:
            openings[position] = move_col
            save_openings(openings)

        return move_col
    except Exception as e:
        st.error("Bot move failed: " + str(e))
        return None


def terminate_game(status):
    """Terminate the game and update the end status."""

    # Update the game variables
    # According to the end game status, different messages will be displayed
    st.session_state.connect4["end_status"] = status
    st.session_state.connect4["game_on"] = False


def reset():
    """Reset the game state and variables."""

    # Reset the board and instantiate a new root
    st.session_state.connect4["game_state"] = Connect4State(
        n_rows=st.session_state.connect4["n_rows"],
        n_cols=st.session_state.connect4["n_cols"],
    )

    # Reset the game variables
    st.session_state.connect4["end_status"] = None
    st.session_state.connect4["game_descr"] = ""
