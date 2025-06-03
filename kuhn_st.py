from kuhn_fun import *
from kuhn_game import RootNode, DEALINGS
import streamlit as st


### -------------------------------------------------- ###
### --- SESSION STATE -------------------------------- ###


def init_state():
    if "kuhn" not in st.session_state:

        st.session_state["kuhn_game"] = {
            "bot"       : "CFRPlus",
            "bot_exp"   : 10,
            "bot_sigma" : dict(),
            "hist"      : [],
            "img_path"  : "assets/poker_table.png",
            "node"      : RootNode(DEALINGS),
            "rewards"   : {"1": [], "2": []},   
            "user"      : None,
        }

        st.session_state["kuhn_simulation"] = {
            "bot"           : "CFRPlus",
            "bot_freeze"    : False,
            "bot_ne"        : dict(),
            "n_rounds"      : 100,
            "rewards"       : [],
            "user"          : None,
            "user1_sigma"   : dict(),
            "user2_sigma"   : dict(),
        }

        st.session_state["kuhn"] = True


### -------------------------------------------------- ###
### --- STATE FUNCTIONS ------------------------------ ###


def get_sigma_key():

    idx = 1 if st.session_state.kuhn_simulation["user"] == 1 else 2
    return "user" + str(idx) + "_sigma"


def map_bot_idx(bot_type):

    d = {
        "CFRPlus"   : 0,
        "CsCFR"     : 1,
    }
    return d[bot_type]


def set_all_info_sets():

    set_kuhn_state("simulation", "user", "simulation_user_")
    # Get key and info sets for the user position
    sigma_key       = get_sigma_key()
    all_info_sets   = get_all_info_sets(st.session_state.simulation_user_)

    if not bool(st.session_state.kuhn_simulation[sigma_key]):
        for info_set in all_info_sets:
            # Initialize user sigma for all info sets
            st.session_state.kuhn_simulation[sigma_key][info_set] = {
                "BET"   : 0.5,
                "PASS"  : 0.5
            }


def set_bot():

    # Initialize and train bot
    bot = train_bot(
        st.session_state.kuhn_game["bot"],
        st.session_state.kuhn_game["bot_exp"]
    )
    # Compute the e
    st.session_state.kuhn_game["bot_sigma"] = bot.compute_ne()


def set_kuhn_state(partition, key, val):
    
    st.session_state["kuhn_" + partition][key] = st.session_state[val]
    # Reset bot sigma if bot type is switched to force re-training
    if partition == "game" and key == "bot":
        st.session_state.kuhn_game["bot_sigma"] = dict()


def set_user_sigma():

    info_set = st.session_state.info_set_
    p = st.session_state.bet_prob_

    # Set the action probabilities
    st.session_state.kuhn_simulation[get_sigma_key()][info_set]["BET"] = p
    st.session_state.kuhn_simulation[get_sigma_key()][info_set]["PASS"] = 1-p


### -------------------------------------------------- ###
### --- GAME FUNCTIONS ------------------------------- ###


def deal():

    # Deal
    st.session_state.kuhn_game["hist"].append("The cards are dealt")
    node_n = st.session_state.kuhn_game["node"].deal_cards()

    # Make bot move if user is in position 2
    if node_n.player != st.session_state.game_user_:
        a = sample_action(node_n, st.session_state.kuhn_game["bot_sigma"])
        node_n = node_n.play(a)
        
        # Update game history
        st.session_state.kuhn_game["hist"].append(
            "Player {}: {}".format(3-st.session_state.game_user_, a)
        )

    # Update image path and game node
    st.session_state.kuhn_game["img_path"] = "assets/deals/{}.png".format(node_n.card_viz)
    st.session_state.kuhn_game["node"] = node_n


def move(*a):

    # User move
    node = st.session_state.kuhn_game["node"]
    a = a[0]
    node_n = node.play(a)

    # Update game history and node
    st.session_state.kuhn_game["hist"].append(
        "Player {}: {}".format(st.session_state.game_user_, a)
    )
    st.session_state.kuhn_game["node"] = node_n

    # Terminate round at terminal node
    if node_n.is_terminal():
        end_round()
    else:

        # Bot move
        a = sample_action(node_n, st.session_state.kuhn_game["bot_sigma"])
        node_n = node_n.play(a)

        # Update game history and node
        st.session_state.kuhn_game["hist"].append(
            "Player {}: {}".format(3-st.session_state.game_user_, a)
        )
        st.session_state.kuhn_game["node"] = node_n

        # Terminate round
        if node_n.is_terminal():
            end_round()


def end_round():

    node = st.session_state.kuhn_game["node"]
    user_pos = st.session_state.game_user_

    # Update
    st.session_state.kuhn_game["rewards"][str(user_pos)].append(
        node.eval() if user_pos == 1 else -node.eval()
    )
    st.session_state.kuhn_game["hist"].append("Round over")
    st.session_state.kuhn_game["hist"].append("Player 1 reward: {}".format(node.eval()))
    st.session_state.kuhn_game["img_path"] = "assets/deals/{}.png".format(
        node.cards if user_pos == 1 else node.cards[::-1]
    )


def reset_round():

    # Reset session state
    st.session_state.kuhn_game["node"] = RootNode(DEALINGS)
    st.session_state.kuhn_game["img_path"] = "assets/poker_table.png"
    st.session_state.kuhn_game["hist"] = []


def reset_count():
    
    # Reset session state
    st.session_state.kuhn_game["rewards"] = {"1": [], "2": []}


### ---------------------------------------------------------------------------------------------------- ###
### SIMULATION FUNCTIONS


def run_simulation():

    if st.session_state.kuhn_simulation["bot_freeze"]:
        
        # Initialize and train the bot
        bot = train_bot(
            st.session_state.kuhn_simulation["bot"],
            st.session_state.kuhn_simulation["n_rounds"],
        )
        # Compute the ne
        st.session_state.kuhn_simulation["bot_sigma"] = bot.compute_ne()
        # Reset unfreezed bot ne to prevent it to be shown in next simulation results
        st.session_state.kuhn_simulation["bot_ne"] = dict()

        # simulate with freezed bot
        rewards = evaluate(
            bot_sigma=st.session_state.kuhn_simulation["bot_sigma"],
            user=st.session_state.kuhn_simulation["user"],
            user_sigma=st.session_state.kuhn_simulation[get_sigma_key()],
            n_rounds=st.session_state.kuhn_simulation["n_rounds"]
        )
    else:

        # Simulate with unfreezed bot and store ne
        rewards, bot_ne = simulate(
            bot_type=st.session_state.kuhn_simulation["bot"],
            user=st.session_state.kuhn_simulation["user"],
            user_sigma=st.session_state.kuhn_simulation[get_sigma_key()],
            n_rounds=st.session_state.kuhn_simulation["n_rounds"]
        )
        st.session_state.kuhn_simulation["bot_ne"] = bot_ne

    # Store rewards
    st.session_state.kuhn_simulation["rewards"] = rewards
