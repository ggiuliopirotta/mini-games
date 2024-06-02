import numpy as np


### ---------------------------------------------------------------------------------------------------- ###
### CONSTANTS


KUHN_ACTIONS   = ["BET", "PASS"]

CARDS           = ["J", "Q", "K"]
DEALINGS        = ["JQ", "JK", "QJ", "QK", "KJ", "KQ"]
MAP_REWARDS     = {
    "JQ" : -1, "JK" : -1, "QK" : -1,
    "QJ" : +1, "KJ" : +1, "KQ" : +1
}

PLAYERS         = ["CHANCE", "1", "2"]


### ---------------------------------------------------------------------------------------------------- ###
### GAME NODES


class Node:
    def __init__(self, parent, player, actions):

        self.parent     = parent
        self.children   = {}

        self.player     = player
        self.actions    = actions


    def play(self, action):
        # return a child according to the action
        return self.children[action]


    def is_root(self):
        # check if root node
        return len(self.children) == 6    


    def is_terminal(self):
        # check if terminal node
        return len(self.children) == 0


### ---------- ###


class RootNode(Node):

    def __init__(self, dealings):
        super().__init__(parent=None, player=0, actions=dealings)

        # populate and store node children
        self.children = {
            deal: GameNode(
                parent  = self,
                player  = 1,
                cards   = deal,
                hist    = [],
                actions = KUHN_ACTIONS
            ) for deal in dealings
        }

        # define information set of the root node
        self.info_set = "."
    

    def deal_cards(self):
        
        # sample possible dealing
        self.deal = np.random.choice(list(self.children.values()))
        return self.deal


### ---------- ###


class GameNode(Node):

    def __init__(self, parent, player, cards, hist, actions):
        super().__init__(parent=parent, player=player, actions=actions)

        self.cards  = cards
        self.hist   = hist

        # populate and store node children
        self.children = {
            a: GameNode(
                parent  = self,
                player  = 2 if player == 1 else 1,
                cards   = cards,
                hist    = hist + [a],
                actions = self.get_next_node_actions(a)
            ) for a in actions
        }

        # set sentinel value for the player at terminal state
        if self.is_terminal():
            self.player = -1

        # define visible card to current player
        # show both at terminal state
        self.card_viz = cards[self.player-1] if not self.is_terminal() else cards

        # define information set of the game node
        # each set is identified by player, card, and history
        self.info_set = "{}:{}-{}".format(
            self.player, self.card_viz, "-".join(hist)
        ) + ("-." if len(hist) != 0 else ".")
    

    def __str__(self):

        # return information set and actions
        s = "-> GAME NODE <-\nplayer\t : {}\ninfo_set : {}\nhist\t : {}\nactions\t : {}\n".format(
            self.player, self.info_set, self.hist, self.actions
        )
        return s
    

    def get_next_node_actions(self, a):

        # at stage 0 and 1 all actions are available
        if len(self.hist) == 0:
            return KUHN_ACTIONS
        
        # at stage 2 all actions are available just after PASS-BET
        elif len(self.hist) == 1:
            if self.hist[-1] == "PASS" and a == "BET":
                return KUHN_ACTIONS
            else:
                return []
            
        # at stage 3 no actions are available
        else:
            return []
    

    def eval(self):

        # handle evaluation at non-terminal node
        if not self.is_terminal():
            self.u = None
            return self.u

        # map cards to rewards and handle non-standard cases
        # double rewards if both players bet and opposite if player 1 passes
        if self.hist[-2] == "BET" and self.hist[-1] == "BET":
            u = MAP_REWARDS[self.cards]*2
        elif self.hist[-2] == "BET":
            u = (1 if len(self.hist) == 2 else -1)
        elif self.hist[-1] == "BET":
            u = -1
        else:
            u = MAP_REWARDS[self.cards]
        
        self.u = u
        return self.u
