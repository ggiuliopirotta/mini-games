from    kuhn_st import *
import  pandas as pd
import  streamlit as st


### ---------------------------------------------------------------------------------------------------- ###
### RULES OF THE GAME


st.markdown(
    '''
    # Kuhn Poker 👑

    ---

    ### Rules

    Kuhn Poker is the simplest version of poker and is played with only 3 cards: a jack, a queen, a and king.
    Both players receive a card and are given the chance to bet, call, check, or pass.

    To make things easy, let **bet** be any action that keeps the betting phase going, and **pass** otherwise.  
    After an initial **antes** of 1, a dollar is added to the pot at each bet.
    
    The betting phase can therefore develop as follows:
    - 1 passes (+0), 2 passes (+0)
    - 1 passes (+0), 2 bets (+1), 1 bets (+1)
    - 1  passes (+0), 2 bets (+1), 1 passes (+0)
    - 1 bets (+1), 2 bets (+1)
    - 1 bets (+1), 2 passes (+0)
    
    Once the betting phase is over, the cards are revealed and the pot is given to the winner.  
    However, if any of the two players pass, the pot is devolved to his opponent.
    
    Here is a representation of the game in sequential form.  
    Notice that the payoff is expressed with respect to player 1, which implies that when the bets are x and y,
    the payoff will be (x+y)-x if player 1 wins, and -((x+y)-x) otherwise.
'''
)

st.image("assets/kuhn_diagram.png")

st.markdown('''
    Information sets are groups of nodes that are indistinguishable to players.  
    For example, if player 1 is dealt a queen, he doesn't know whether his opponent received a jack or a king,
    thus forcing QJ and QK to be in the same set.
            
    Hence, the strategies must be information sets-oriented, and not nodes-specific.
            
    ---

    ### Single round

    Choose the bot, how experienced it should be, and your position in the game.  
    When ready, train it and start the round dealing the cards.  
    Notice that the bot needs re-training if the algorithm is changed, but not after each round.

    This is to help you understand how the game works, though the fun part comes with the simulation.  
    Check it out ⬇️
    '''
)


### ---------------------------------------------------------------------------------------------------- ###
### GAME SETTINGS


cols = st.columns((0.3, 0.2, 0.45))
node = st.session_state.kuhn_game["node"]

with cols[0]:
    game_bot_ = st.selectbox(
        key         = "game_bot_",
        label       = "Bot",
        options     = ["CFR +", "Chance Sampling CFR"],
        index       = map_bot_idx(st.session_state.kuhn_game["bot"]),
        on_change   = set_kuhn_state,
        args        = ("game", "bot", "game_bot_")
    )

with cols[1]:
    bot_exp_ = st.number_input(
        key         = "bot_exp_",
        label       = "Bot experience",
        help        = "The number of games the bot should be trained on",
        min_value   = 10,
        max_value   = 1000,
        value       = st.session_state.kuhn_game["bot_exp"],
        step        = 10,
        on_change   = set_kuhn_state,
        args        = ("game", "bot_exp", "bot_exp_")
    )

game_user_ = st.radio(
    key         = "game_user_",
    label       = "User position",
    help        = "Whether to play first or second",
    options     = [1, 2],
    index       = 0,
    disabled    = not node.is_root()
)

st.image(st.session_state.kuhn_game["img_path"])


### ---------------------------------------------------------------------------------------------------- ###
### GAME BUTTONS


cols = st.columns((0.14, 0.1, 0.15, 0.6))

with cols[0]:
    train_ = st.button(
        label       = "Train bot",
        disabled    = not node.is_root(),
        on_click    = set_bot
    )

with cols[1]:
    deal_ = st.button(
        label       = "Deal",
        disabled    = not node.is_root() or not bool(st.session_state.kuhn_game["bot_sigma"]),
        on_click    = deal
    )

with cols[2]:
    reset_ = st.button(
        label       = "Reset",
        disabled    = not node.is_terminal(),
        on_click    = reset_round
    )

cols = st.columns((0.095, 0.1, 0.85))

with cols[0]:
    bet_ = st.button(
        key         = "bet_",
        label       = "Bet",
        disabled    = node.is_root() or node.is_terminal(),
        on_click    = move,
        args        = ("BET", )
    )

with cols[1]:
    pass_ = st.button(
        key         = "pass_",
        label       = "Pass",
        disabled    = node.is_root() or node.is_terminal(),
        on_click    = move,
        args        = ("PASS", )
    )


### ---------------------------------------------------------------------------------------------------- ###
### GAME RESULTS


st.markdown(
    '''
    In the figure above, your card is always displayed on the bottom left corner.  
    Round stages:
    '''
)

st.write(st.session_state.kuhn_game["hist"])

st.markdown(
    '''
    Recap of your games:
    '''
)

game_rewards    = st.session_state.kuhn_game["rewards"]
game_rewards_df = pd.DataFrame({
        "As"            : [],
        "Total games"   : [],
        "Avg reward"    : [],
    })

for i in st.session_state.kuhn_game["rewards"]:
    game_rewards_df.loc[int(i)-1] = [i, len(game_rewards[i]), np.mean(game_rewards[i])]
game_rewards_df.set_index("As", inplace=True)

st.write(game_rewards_df)

restart_ = st.button(
    label       = "Restart count",
    on_click    = reset_count
)


### ---------------------------------------------------------------------------------------------------- ###
### SIMULATION SETTINGS


st.markdown(
    '''
    ---
                     
    ### Simulation

    Choose the bot, whether it should be pre-trained or not, and your position in the game.  
    Once your strategy is defined, simulate a game of n rounds against it.
    '''
)

with st.expander("Settings"):

    user_position = st.session_state.kuhn_simulation["user"]
    user_sigma    = st.session_state.kuhn_simulation[get_sigma_key()]

    st.markdown("Recap of your strategy:")
    st.write(pd.DataFrame(user_sigma))

    bot_freeze_ = st.checkbox(
        key         = "bot_freeze_",
        label       = "Freeze the bot",
        help        = "If flagged, the bot won't train to exploit your specific strategy",
        value       = st.session_state.kuhn_simulation["bot_freeze"],
        on_change   = set_kuhn_state,
        args        = ("simulation", "bot_freeze", "bot_freeze_")
    )

    simulation_user_ = st.radio(
        key         = "simulation_user_",
        label       = "User position",
        help        = "Whether to play first or second",
        options     = [1, 2],
        index       = user_position-1 if bool(user_position) else None,
        on_change   = set_all_info_sets
    )

    cols = st.columns((0.25, 0.2, 0.55))

    with cols[0]:
        info_set_ = st.selectbox(
            key         = "info_set_",
            label       = "Information set",
            help        = '''
            How to read \"1:J-PASS-BET-.\":  
            - 1 indicates who has to make the move
            - J is the (visible) card dealt
            - PASS-BET is the set of actions that led to the current node  
            
            To do: define the next action
            ''',
            options     = get_all_info_sets(user_position) if bool(user_position) else [""]
        )
    
    with cols[1]:
        bet_prob_ = st.number_input(
            key         = "bet_prob_",
            label       = "Betting prob",
            min_value   = 0.,
            max_value   = 1.,
            value       = user_sigma[info_set_]["BET"] if bool(user_position) else 0.5,
            step        = 0.1,
            disabled    = st.session_state.simulation_user_ is None,
            on_change   = set_user_sigma
        )
    
    cols = st.columns((0.35, 0.25, 0.5))

    with cols[0]:
        simulation_bot_ = st.selectbox(
            key         = "simulation_bot_",
            label       = "Bot",
            options     = ["CFR +", "Chance Sampling CFR"],
            index       = map_bot_idx(st.session_state.kuhn_simulation["bot"]),
            on_change   = set_kuhn_state,
            args        = ("simulation", "bot", "simulation_bot_")
        )
    
    with cols[1]:
        n_rounds_ = st.number_input(
            key         = "n_rounds_", 
            label       = "Rounds",
            min_value   = 10,
            max_value   = 1000,
            value       = st.session_state.kuhn_simulation["n_rounds"],
            step        = 10,
            on_change   = set_kuhn_state,
            args        = ("simulation", "n_rounds", "n_rounds_")
        )

simulate_   = st.button(
    label       = "Simulate",
    disabled    = not bool(user_position),
    on_click    = run_simulation
)


### ---------------------------------------------------------------------------------------------------- ###
### SIMULATION RESULTS


rewards = st.session_state.kuhn_simulation["rewards"]
bot_ne  = st.session_state.kuhn_simulation["bot_ne"]

if bool(rewards):

    fig = plot_simulation(rewards)
    st.pyplot(fig)

    st.markdown(
        '''
        Rewards below are expressed with respect to player 1.  
        Total: {}  
        Average: {:.3f}  
        '''.format(np.sum(rewards), np.mean(rewards))
    )

    if bool(bot_ne):

        st.markdown("Strategy learnt by the bot:")
        st.write(pd.DataFrame(bot_ne))


### ---------------------------------------------------------------------------------------------------- ###
### PAPERS LINKS


st.markdown(
    '''
    ---
                     
    ### Papers

    If you're interested, follow the links and have a look at these papers.  
    They first introduced the algos that I implemented here!
    '''
)

cols = st.columns((0.2, 0.2, 0.8))

with cols[0]:
    st.link_button(
        label   = "Vanilla CFR",
        url     = "https://proceedings.neurips.cc/paper/2007/file/08d98638c6fcd194a4b1e6992063e944-Paper.pdf"
    )

with cols[1]:
    st.link_button(
        label   = "CFR +",
        url     = "https://arxiv.org/pdf/1407.5042.pdf"
    )
