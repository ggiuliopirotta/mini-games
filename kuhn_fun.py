from    cfr_algos import *
from    kuhn_game import RootNode, DEALINGS
import  matplotlib.gridspec as gridspec
import  matplotlib.pyplot as plt
import  seaborn as sns


def evaluate(bot_sigma, user, user_sigma, n_rounds):

    # instantiate game
    root    = RootNode(DEALINGS)
    rewards = []

    for _ in range(n_rounds):
        node = root.deal_cards()

        while True:
            if node.is_terminal():
                # store rewards and start new round at terminal node
                rewards.append(node.eval())
                break

            # sample action and keep playing otherwise
            a       = sample_action(node, user_sigma if node.player == user else bot_sigma)
            node    = node.play(a)
    
    return rewards


def get_all_info_sets(user):

    # instantiate game
    root = RootNode(DEALINGS)
    sets = []

    def get_sets_rec(node):

        info_set = node.info_set
        # append info set if it belongs to the user and it was not visited before
        if node.player == user and info_set not in sets:
            sets.append(node.info_set)
        
        # call recursion on children
        for a in node.actions:
            get_sets_rec(node.play(a))

    # start recursion
    get_sets_rec(root)
    return sets


def plot_simulation(rewards):

    # create customized layout and figure
    gs  = gridspec.GridSpec(1, 3)
    fig = plt.figure(figsize=(10, 5))

    # subplots
    ax1 = fig.add_subplot(gs[0, :1])
    ax2 = fig.add_subplot(gs[0, 1:])

    # histogram for rewards
    sns.histplot(rewards, bins=5, stat="density", kde=True, ax=ax1)
    ax1.set_title("Rewards for player 1")
    ax1.set_xlabel("Rewards")
    ax1.set_xticks([-2, -1, 0, 1, 2])

    idxs        = np.linspace(0, len(rewards), 21, dtype=int)
    # compute average rewards over sets of rounds
    avg_rewards = [np.mean(rewards[idxs[i]: idxs[i+1]]) for i in range(len(idxs)-1)]

    # lineplot for exploitability
    sns.lineplot(x=np.arange(1, 21), y=avg_rewards)
    ax2.set_title("Exploitability")
    ax2.set_ylabel("Average rewards per set")
    ax2.set_xlabel("Sets of {} rounds".format(len(rewards)//20))
    ax2.set_xticks(np.arange(1, 21))

    plt.tight_layout()
    return fig


def train_bot(bot_type, bot_exp):

    # instantiate game
    root = RootNode(DEALINGS)

    # create bot
    if bot_type == "CFR +":
        bot = CFRPlus(root)
    else:
        bot = CsCFR(root)
    
    # train bot in sef-play to equilibrium
    bot.train(n_rounds=bot_exp)
    return bot


def sample_action(node, sigma):

    # get sigma for info set
    sigma_i = sigma[node.info_set]

    # sample from categorical distributon
    rnd     = np.random.random()
    a_idx   = np.argmax(rnd < np.cumsum(list(sigma_i.values())))
    a       = list(sigma_i.keys())[a_idx]
    
    return a


def simulate(bot_type, user, user_sigma, n_rounds):

    # instantiate game
    root = RootNode(DEALINGS)

    # create bot
    if bot_type == "CFR +":
        bot = CFRPlusBot(root, user, user_sigma)
    else:
        bot = CsCFRBot(root, user, user_sigma)

    # simulate with training
    rewards = bot.play(n_rounds=n_rounds, tracking=True)

    ne      = bot.compute_ne()
    bot_ne  = dict()
    
    for info_set in bot.compute_ne():
        if int(info_set[0]) != user:
            # append info set to the bot's ne
            bot_ne[info_set] = ne[info_set]

    return rewards, bot_ne
