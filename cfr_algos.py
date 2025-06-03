from kuhn_game import *
import numpy as np


### -------------------------------------------------- ###
### --- CFR ALGORITHM -------------------------------- ###


class CfrAlgorithm:
    def __init__(self, root, mode='vanilla'):

        if mode not in ['vanilla', 'CFRPlus', 'CsCFR']:
            raise ValueError("Invalid mode.")

        self.root = root
        self.mode = mode
        self.ACTIONS = KUHN_ACTIONS
        self.N_ACTIONS = len(self.ACTIONS)

        # Initialize sigma and regret
        self.sigma = self.init_mapping("prob")
        self.sigma_cum = self.init_mapping("zero")
        self.r_cum = self.init_mapping("zero")


    def compute_ne(self):
        ne = dict()

        def compute_ne_rec(node):

            # Get information set and cumulative sigma
            # The regret is thresholded at 0 cause the proportions must be preserved
            info_set = node.info_set
            r = np.array(list(self.sigma_cum[info_set].values()))
            r_tot = np.sum(r)

            if node.is_root():
                # No ne at root or terminal node
                pass
            elif node.is_terminal():
                return None
            else:
                ne[info_set] = dict()
                for i, a in enumerate(self.sigma[info_set]):
                    # Update the ne at the info set
                    # If any of the regrets is positive, each action probability is proportional to the regret
                    # Otherwise, a uniform strategy is returned
                    ne[info_set][a] = r[i]/r_tot if r_tot > 0 else 1./self.N_ACTIONS

            # Call recursion
            for a in node.actions:
                compute_ne_rec(node.play(a))
        # Start recursion
        compute_ne_rec(self.root)

        return ne


    def compute_u(self, node, p=1, p_cfr=1):

        # Get the information set and initialize u
        info_set = node.info_set
        u_actions = dict()
        u_tot = 0

        if node.is_root():
            if self.mode == 'CFRPlus':
                for a in node.actions:
                    # Accumulate utilities for each child
                    # Both realization probabilities are still 1 cause neither of the players moved
                    u_tot += self.compute_u(node.play(a), p, p_cfr)
                # Return a weigthed average
                return (1/6)*u_tot
            elif self.mode == 'CsCFR':
                # Sample a possible dealing and run the algorithm there
                return self.compute_u(node.deal_cards())
            else:
                pass

        # Return node evaluation at terminal state
        elif node.is_terminal():
            return node.eval()
        else:
            for a in node.actions:
                # Get the new realization probabilities wrt player 1
                # Fix the probability for player 2 cause once the information set is reached, where to go only depends on player 1
                p_child = p*(self.sigma[info_set][a] if node.player == 1 else 1)
                p_cfr_child = p_cfr*(self.sigma[info_set][a] if node.player == 2 else 1)
                # Discount the utility for each child by the probability of reaching the information set
                u_actions[a] = self.compute_u(node.play(a), p_child, p_cfr_child)
                u_tot += self.sigma[info_set][a]*u_actions[a]

        # Get counterfactual probabilities wrt player 1
        p, p_cfr = (p, p_cfr) if node.player == 1 else (p_cfr, p)

        for a in node.actions:
            # Discount the regret
            # Fix probability for player 1 cause the regret is computed wrt pure actions
            r = p_cfr*(u_actions[a]-u_tot)*(1 if node.player == 1 else -1)

            if self.mode == 'CFRPlus':
                # Threshold the cumulative regret to 0
                self.r_cum[info_set][a] = max(self.r_cum[info_set][a]+r, 0)
            else:
                self.r_cum[info_set][a] += r
            self.sigma_cum[info_set][a] += p*self.sigma[info_set][a]

        return u_tot


    def init_mapping(self, fill):
        mapping = dict()

        def init_mapping_rec(node, fill):

            # Initialize a node-action mapping for the information set
            # Fill with uniform distribution if it's a mapping for the strategy and with 0 otherwise
            mapping[node.info_set] = {
                a: (1./len(node.actions) if fill == "prob" else 0.) for a in node.actions
            }

            # Call recursion
            for a in node.actions:
                init_mapping_rec(node.play(a), fill)
        # Start recursion
        init_mapping_rec(self.root, fill)

        return mapping


    def update_sigma(self):
        def update_sigma_rec(node):

            # No update at root or terminal node
            if node.is_root():
                pass
            elif node.is_terminal():
                return None
            else:
                # Get information set and cumulative regret
                # The regret is threshold at 0 cause negative probabilities don't exist
                info_set = node.info_set
                r = np.array(list(self.r_cum[info_set].values()))
                s_new = np.maximum(r, 0)
                s_new_normalized  = np.sum(s_new)

                # Update both sigma and cumulative sigma for the information set
                for i, a in enumerate(self.sigma[info_set]):
                    # If any of the regrets is positive, each action probability is proportional to the regret
                    # Otherwise, a uniform strategy is returned
                    self.sigma[info_set][a] = s_new[i]/s_new_normalized if s_new_normalized > 0 else 1./self.N_ACTIONS
                    self.sigma_cum[info_set][a] += self.sigma[info_set][a]

            # Call recursion
            for a in node.actions:
                update_sigma_rec(node.play(a))
        # Start recursion
        update_sigma_rec(self.root)


    def train(self, n_rounds):

        epoch = 0
        while epoch < n_rounds:
            # Traverse the tree to compute utility and update
            self.compute_u(self.root)
            self.update_sigma()
            epoch += 1


### -------------------------------------------------- ###
### --- CFR BOT -------------------------------------- ###


class CfrBot:
    def __init__(self, root, user, user_sigma, mode='vanilla'):

        if mode not in ['vanilla', 'CFRPlus', 'CsCFR']:
            raise ValueError("Invalid mode.")

        self.root = root
        self.mode = mode
        self.ACTIONS = KUHN_ACTIONS
        self.N_ACTIONS = len(self.ACTIONS)

        self.user = user
        self.user_sigma = user_sigma

        # Initialize sigma and regret
        self.sigma = self.init_mapping("prob")
        self.sigma_cum = self.init_mapping("zero")
        self.r_cum = self.init_mapping("zero")


    def compute_ne(self):
        ne = dict()

        def compute_ne_rec(node):

            # Get information set and cumulative sigma
            # The regret is thresholded at 0 cause the proportions must be preserved
            info_set = node.info_set
            r = np.array(list(self.sigma_cum[info_set].values()))
            r_tot = np.sum(r)

            if node.is_root():
                # No ne at root or terminal node
                pass
            elif node.is_terminal():
                return None
            else:
                ne[info_set] = dict()
                if node.player == self.user:
                    # Store the user sigma at a user node
                    # Fill with actions' probabilities if defined and with 0 otherwise
                    ne[info_set] = (
                        self.user_sigma[info_set] if info_set in self.user_sigma else dict()
                    )
                else:
                    for i, a in enumerate(self.sigma[info_set]):
                        # Update the ne at the info set
                        # If any of the regrets is positive, each action probability is proportional to the regret
                        # Otherwise, a uniform strategy is returned
                        ne[info_set][a] = r[i]/r_tot if r_tot > 0 else 1./self.N_ACTIONS

            # Call recursion
            for a in node.actions:
                compute_ne_rec(node.play(a))
        # Start recursion
        compute_ne_rec(self.root)

        return ne


    def compute_u(self, node, p=1, p_cfr=1):

        # Get the information set and initialize u
        info_set = node.info_set
        u_actions = dict()
        u_tot = 0

        if node.is_root():
            if self.mode == 'CFRPlus':
                for a in node.actions:
                    # Accumulate utilities for each child
                    # Both realization probabilities are still 1 cause neither of the players moved
                    u_tot += self.compute_u(node.play(a), p, p_cfr)
                # Return a weigthed average
                return (1/6)*u_tot
            elif self.mode == 'CsCFR':
                # Sample a possible dealing and run the algorithm there
                return self.compute_u(node.deal_cards())
            else:
                pass

        # Return node evaluation at terminal state
        elif node.is_terminal():
            return node.eval()
        else:
            for a in node.actions:
                # Get the new realization probabilities wrt player 1
                # Fix the probability for player 2 cause once the information set is reached, where to go only depends on player 1
                p_child = p*(self.sigma[info_set][a] if node.player == 1 else 1)
                p_cfr_child = p_cfr*(self.sigma[info_set][a] if node.player == 2 else 1)
                # Discount the utility for each child by the probability of reaching the information set
                u_actions[a] = self.compute_u(node.play(a), p_child, p_cfr_child)
                u_tot += self.sigma[info_set][a]*u_actions[a]

        # Get counterfactual probabilities wrt player 1
        p, p_cfr = (p, p_cfr) if node.player == 1 else (p_cfr, p)

        for a in node.actions:
            # Discount the regret
            # Fix probability for player 1 cause the regret is computed wrt pure actions
            r = p_cfr*(u_actions[a]-u_tot)*(1 if node.player == 1 else -1)

            if self.mode == 'CFRPlus':
                # Threshold the cumulative regret to 0
                self.r_cum[info_set][a] = max(self.r_cum[info_set][a]+r, 0)
            else:
                self.r_cum[info_set][a] += r
            self.sigma_cum[info_set][a] += p*self.sigma[info_set][a]

        return u_tot


    def init_mapping(self, fill):
        mapping = dict()

        def init_mapping_rec(node, fill):

            info_set = node.info_set
            if info_set in self.user_sigma:
                # Initialize user node-action map at a user information set
                # Fill it with the user sigma if it's a map for the strategy and 0 otherwise
                mapping[info_set] = {
                    a: (self.user_sigma[info_set][a] if fill == "prob" else 0.) for a in node.actions
                }
            else:
                # Initialize bot node-action map at a bot information set
                # Fill it with uniform distribution if it's a map for the strategy and 0 otherwise
                mapping[info_set] = {
                    a: (1./len(node.actions) if fill == "prob" else 0.) for a in node.actions
                }

            # Call recursion
            for a in node.actions:
                init_mapping_rec(node.play(a), fill)
        # Start recursion
        init_mapping_rec(self.root, fill)

        return mapping


    def update_sigma(self):
        def update_sigma_rec(node):

            # No update at root or terminal node
            if node.is_root() or node.player == self.user:
                pass
            elif node.is_terminal():
                return
            else:
                # Get information set and cumulative regret
                # The regret is threshold at 0 cause negative probabilities don't exist
                info_set = node.info_set
                r = np.array(list(self.r_cum[info_set].values()))
                s_new = np.maximum(r, 0)
                s_new_normalized  = np.sum(s_new)

                # Update both sigma and cumulative sigma for the information set
                for i, a in enumerate(self.sigma[info_set]):
                    # If any of the regrets is positive, each action probability is proportional to the regret
                    # Otherwise, a uniform strategy is returned
                    self.sigma[info_set][a] = s_new[i]/s_new_normalized if s_new_normalized > 0 else 1./self.N_ACTIONS
                    self.sigma_cum[info_set][a] += self.sigma[info_set][a]

            # Call recursion
            for a in node.actions:
                update_sigma_rec(node.play(a))
        # Start recursion
        update_sigma_rec(self.root)


    def sample_action(self, info_set):

        # Get the sigma relative to the information set
        sigma_i = self.sigma[info_set]
        # Sample
        a_idx = np.argmax(np.random.random() < np.cumsum(list(sigma_i.values())))
        a = list(sigma_i.keys())[a_idx]

        return a


    def traverse_tree(self):

        # Deal
        node = self.root.deal_cards()

        while True:
            # Return evaluation at terminal node
            if node.is_terminal():
                return node.eval()
            else:
                # Sample and move to the child
                a = self.sample_action(node.info_set)
                node = node.play(a)


    def play(self, n_rounds, tracking=False):

        # Track rewards
        rewards = []

        epoch = 0
        while epoch < n_rounds:
            # Traverse the tree to compute utility and update
            rewards.append(self.traverse_tree())
            self.compute_u(self.root)
            self.update_sigma()
            epoch += 1

        if tracking:
            return rewards