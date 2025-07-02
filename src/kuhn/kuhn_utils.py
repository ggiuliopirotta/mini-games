from src.kuhn.cfr_algos import *
from src.kuhn.kuhn_game import RootNode, DEALINGS
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import seaborn as sns


def evaluate(bot_sigma, user, user_sigma, n_rounds):
    """
    Evaluate the bot's strategy against a user strategy in a Kuhn poker game.

    :param bot_sigma: The bot's strategy
    :param user: The user position
    :param user_sigma: The user strategy
    :param n_rounds: The number of rounds to play

    :return: A list of rewards for the user
    """

    # Instantiate a game
    root = RootNode(DEALINGS)
    rewards = []

    for _ in range(n_rounds):
        node = root.deal_cards()
        while True:
            if node.is_terminal():
                # Store the rewards and start a new round at terminal node
                rewards.append(node.eval())
                break

            # Sample an action and keep playing otherwise
            a = sample_action(node, user_sigma if node.player == user else bot_sigma)
            node = node.play(a)

    return rewards


def get_all_info_sets(user):
    """
    Get all information sets for a user in the Kuhn poker game.

    :param user: The user position

    :return: A list of information sets for the user
    """

    # Instantiate a game
    root = RootNode(DEALINGS)
    sets = []

    def get_sets_rec(node):

        info_set = node.info_set
        # Append the info set if it belongs to the user and it was not visited before
        if node.player == user and info_set not in sets:
            sets.append(node.info_set)

        # Call recursion on children
        for a in node.actions:
            get_sets_rec(node.play(a))

    # Start recursion
    get_sets_rec(root)

    return sets


def plot_simulation(rewards):
    """
    Plot the rewards and exploitability of the bot in a Kuhn poker game.

    :param rewards: A list of rewards for the user
    """

    gs = gridspec.GridSpec(1, 3)
    fig = plt.figure(figsize=(10, 5))
    ax1 = fig.add_subplot(gs[0, :1])
    ax2 = fig.add_subplot(gs[0, 1:])

    # Histogram for rewards
    sns.histplot(rewards, bins=5, stat="density", kde=True, ax=ax1)
    ax1.set_title("Rewards for player 1")
    ax1.set_xlabel("Rewards")
    ax1.set_xticks([-2, -1, 0, 1, 2])

    idxs = np.linspace(0, len(rewards), 21, dtype=int)
    # Compute average rewards over sets of rounds
    avg_rewards = [
        np.mean(rewards[idxs[i] : idxs[i + 1]]) for i in range(len(idxs) - 1)
    ]

    # Lineplot for exploitability
    sns.lineplot(x=np.arange(1, 21), y=avg_rewards)
    ax2.set_title("Exploitability")
    ax2.set_xlabel("Sets of {} rounds".format(len(rewards) // 20))
    ax2.set_ylabel("Average rewards per set")
    ax2.set_xticks(np.arange(1, 21))

    plt.tight_layout()
    return fig


def train_bot(bot_type, bot_exp):
    """
    Train a bot for the Kuhn poker game using the specified algorithm and experience.

    :param bot_type: The type of bot to train (e.g., "cfr", "cfr_plus", "cfr_plus_2")
    :param bot_exp: The number of rounds to train the bot

    :return: An instance of the trained bot
    """

    # Instantiate a game
    root = RootNode(DEALINGS)
    bot = CfrAlgorithm(root, mode=bot_type)
    # Train the bot in sef-play to ne
    bot.train(n_rounds=bot_exp)

    return bot


def sample_action(node, sigma):
    """
    Sample an action from the given node based on the provided strategy sigma.

    :param node: The current game node
    :param sigma: The strategy for the current player at the node

    :return: The sampled action
    """

    # Get the sigma relative to the information set
    sigma_i = sigma[node.info_set]
    # Sample
    a_idx = np.argmax(np.random.random() < np.cumsum(list(sigma_i.values())))
    a = list(sigma_i.keys())[a_idx]

    return a


def simulate(bot_type, user, user_sigma, n_rounds):
    """
    Simulate a Kuhn poker game with a bot and a user strategy.

    :param bot_type: The type of bot to use (e.g., "cfr", "cfr_plus", "cfr_plus_2")
    :param user: The user position
    :param user_sigma: The user strategy
    :param n_rounds: The number of rounds to simulate

    :return: The rewards for the user and the bot's NE
    """

    # Instantiate game
    root = RootNode(DEALINGS)
    print(bot_type)
    bot = CfrBot(root, user, user_sigma, mode=bot_type)

    # Simulate while training
    rewards = bot.play(n_rounds, tracking=True)
    ne = bot.compute_ne()
    bot_ne = dict()

    for info_set in bot.compute_ne():
        if int(info_set[0]) != user:
            # Append the info set to the bot's ne
            bot_ne[info_set] = ne[info_set]

    return rewards, bot_ne
