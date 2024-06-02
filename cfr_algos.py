from    kuhn_game import *
import  numpy as np


### ---------------------------------------------------------------------------------------------------- ###
### CFR ALGORITHM


class CFR:
    def __init__(self, root):

        self.root = root

        # store actions and action set cardinality
        self.ACTIONS    = KUHN_ACTIONS
        self.N_ACTIONS  = len(self.ACTIONS)

        # initialize strategies and regret
        self.sigma      = self.init_map("prob")
        self.sigma_cum  = self.init_map("zero")
        self.r_cum      = self.init_map("zero")
    

    def compute_ne(self):

        # initialize dictionary
        ne = dict()

        # recursive function
        def compute_ne_rec(node):

            # get information set and cumulative sigma
            # the regret is thresholded at 0 cause the proportions between must be preserved
            info_set    = node.info_set
            r           = np.array(list(self.sigma_cum[info_set].values()))
            r_tot       = np.sum(r)

            # no ne at root or terminal node
            if node.is_root():
                pass
            elif node.is_terminal():
                return None
            else:
            
                ne[info_set] = dict()
                for i, a in enumerate(self.sigma[info_set]):
                    # update ne at info set
                    # if any of the regrets is positive, each action probability is proportional to the regret
                    # otherwise, a uniform strategy is returned
                    ne[info_set][a] = r[i]/r_tot if r_tot > 0 else 1./self.N_ACTIONS

            # call recursion on children
            for a in node.actions:
                compute_ne_rec(node.play(a))
        # start recursion
        compute_ne_rec(self.root)

        return ne
    

    def compute_u(self, node, p=1, p_cfr=1):
        # implement in variants
        return NotImplementedError("Implement this method")
    

    def init_map(self, fill):

        # initialize dictionary
        mapping = dict()

        # recursive function
        def init_map_rec(node, fill):
            
            # initialize node-action mapping for the information set
            # fill with uniform distribution if it's a map for the strategy and with 0 otherwise
            mapping[node.info_set] = {
                a: (1./len(node.actions) if fill == "prob" else 0.) for a in node.actions
            }

            # call recursion on children
            for a in node.actions:
                init_map_rec(node.play(a), fill)
        # start recursion
        init_map_rec(self.root, fill)

        return mapping


    def update_sigma(self):
        def update_sigma_rec(node):
            
            # no update at root or terminal node
            if node.is_root():
                pass
            elif node.is_terminal():
                return
            else:
                
                # get information set and cumulative regret
                # the regret is threshold at 0 cause negative probabilities don't exist
                info_set    = node.info_set
                r           = np.array(list(self.r_cum[info_set].values()))
                s_new       = np.maximum(r, 0)
                # sum to normalizer
                s_new_norm  = np.sum(s_new)

                # update sigma and cumulative sigma for the information set
                for i, a in enumerate(self.sigma[info_set]):

                    # if any of the regrets is positive, each action probability is proportional to the regret
                    # otherwise, a uniform strategy is returned
                    self.sigma[info_set][a]         = s_new[i]/s_new_norm if s_new_norm > 0 else 1./self.N_ACTIONS
                    # sum to cumulative sigma
                    self.sigma_cum[info_set][a]    += self.sigma[info_set][a]
                
            # call recursion on children
            for a in node.actions:
                update_sigma_rec(node.play(a))
        # start recursion
        update_sigma_rec(self.root)
        

    def train(self, n_rounds):

        epoch = 0
        while epoch < n_rounds:
            epoch += 1

            # traverse tree to compute utility and update
            self.compute_u(self.root)         
            self.update_sigma()


### ---------------------------------------------------------------------------------------------------- ###
### CFR +


class CFRPlus(CFR):
    
    def __init__(self, root):
        super().__init__(root=root)


    def compute_u(self, node, p=1, p_cfr=1):

        # get information set and initialize utility
        info_set    = node.info_set
        u_actions   = dict()
        u_tot       = 0

        if node.is_root():
            for a in node.actions:
                # accumulate utilities for each child
                # both realization probabilities are still 1 cause neither of the players moved
                u_tot += self.compute_u(node.play(a), p, p_cfr)
            
            # return weigthed average of the total utility
            return (1/6)*u_tot
        
        # return node evaluation at terminal state
        elif node.is_terminal():
            return node.eval()
        else:

            for a in node.actions:
                # get new realization probabilities wrt player 1
                # fix probability for player 2 cause once the information set is reached, where to go only depends on player 1
                p_child     = p*(self.sigma[info_set][a] if node.player == 1 else 1)
                p_cfr_child = p_cfr*(self.sigma[info_set][a] if node.player == 2 else 1)

                # discount utility for each child by the probability of reaching the information set
                u_actions[a] = self.compute_u(node.play(a), p_child, p_cfr_child)
                u_tot       += self.sigma[info_set][a]*u_actions[a]
        
        # get counterfactual probabilities wrt player 1
        p, p_cfr = (p, p_cfr) if node.player == 1 else (p_cfr, p)

        for a in node.actions:
            # discount regret by counterfactual probability
            # fix probability for player 1 cause the regret is computed wrt pure actions
            r = p_cfr*(u_actions[a]-u_tot)*(1 if node.player == 1 else -1)

            # difference wrt Vanilla CFR
            # threshold the cumulative regret to 0 at each iteration rather than just in the update
            self.r_cum[info_set][a]      = max(self.r_cum[info_set][a]+r, 0)
            self.sigma_cum[info_set][a] += p*self.sigma[info_set][a]
        
        return u_tot


### ---------------------------------------------------------------------------------------------------- ###
### Chance sampling CFR


class CsCFR(CFR):
    
    def __init__(self, root):
        super().__init__(root=root)


    def compute_u(self, node, p=1, p_cfr=1):

        # get information set and initialize utility
        info_set    = node.info_set
        u_actions   = dict()
        u_tot       = 0

        if node.is_root():
            # difference wrt VanillaCFR
            # sample a possible dealing and run the algorithm there instead of evaluating all possible outcomes
            return self.compute_u(node.deal_cards())
        
        # return node evaluation at terminal state
        elif node.is_terminal():
            return node.eval()
        else:

            for a in node.actions:
                # get new realization probabilities wrt player 1
                # fix probability for player 2 cause once the information set is reached, where to go only depends on player 1
                p_child     = p*(self.sigma[info_set][a] if node.player == 1 else 1)
                p_cfr_child = p_cfr*(self.sigma[info_set][a] if node.player == 2 else 1)

                # discount utility for each child by the probability of reaching the information set
                u_actions[a] = self.compute_u(node.play(a), p_child, p_cfr_child)
                u_tot       += self.sigma[info_set][a]*u_actions[a]
        
        # get counterfactual probabilities wrt player 1
        p, p_cfr = (p, p_cfr) if node.player == 1 else (p_cfr, p)

        for a in node.actions:
            # discount regret by counterfactual probability
            # fix probability for player 1 cause the regret is computed wrt pure actions
            r = p_cfr*(u_actions[a]-u_tot)*(1 if node.player == 1 else -1)

            # update cumulative regret and cumulative sigma
            self.r_cum[info_set][a]     += r
            self.sigma_cum[info_set][a] += p*self.sigma[info_set][a]
        
        return u_tot


### ---------------------------------------------------------------------------------------------------- ###
### BOT


class CFRBot:
    def __init__(self, root, user, user_sigma):

        self.root = root

        # store actions and action set cardinality
        self.ACTIONS    = KUHN_ACTIONS
        self.N_ACTIONS  = len(self.ACTIONS)
    
        # store user variables
        self.user       = user
        self.user_sigma = user_sigma

        # initialize strategies and regret
        self.sigma      = self.init_map("prob")
        self.sigma_cum  = self.init_map("zero")
        self.r_cum      = self.init_map("zero")

    def compute_ne(self):

        # initialize dictionary
        ne = dict()

        # recursive function
        def compute_ne_rec(node):

            # get information set and cumulative sigma
            # the regret is thresholded at 0 cause the proportions between must be preserved
            info_set    = node.info_set
            r           = np.array(list(self.sigma_cum[info_set].values()))
            r_tot       = np.sum(r)

            # no ne at root or terminal node
            if node.is_root():
                pass
            elif node.is_terminal():
                return None
            else:

                ne[info_set] = dict()
                if node.player == self.user:

                    # store user sigma at a user node
                    # fill with actions' probabilities if defined and with 0 otherwise
                    ne[info_set] = (
                        self.user_sigma[info_set] if info_set in self.user_sigma else dict()
                    )
                else:

                    # store bot sigma at a bot node
                    for i, a in enumerate(self.sigma[info_set]):
                        # update ne at info set
                        # if any of the regrets is positive, each action probability is proportional to the regret
                        # otherwise, a uniform strategy is returned
                        ne[info_set][a] = r[i]/r_tot if r_tot > 0 else 1./self.N_ACTIONS

            # call recursion on children
            for a in node.actions:
                compute_ne_rec(node.play(a))
        # start recursion
        compute_ne_rec(self.root)

        return ne
    

    def compute_u(self, node, p=1, p_cfr=1):
        # implement in variants
        return NotImplementedError("Implement this method")
    

    def init_map(self, fill):

        # initialize dictionary
        mapping = dict()

        # recursive function
        def init_map_rec(node, fill):
            info_set = node.info_set

            if info_set in self.user_sigma:
                # initialize user node-action map at a user information set
                # fill with user sigma if it's a map for the strategy and with 0 otherwise
                mapping[info_set] = {
                    a: (self.user_sigma[info_set][a] if fill == "prob" else 0.) for a in node.actions
                }
            
            else:
                # initialize bot node-action map at a bot information set
                # fill with uniform distribution if it's a map for the strategy and with 0 otherwise
                mapping[info_set] = {
                    a: (1./len(node.actions) if fill == "prob" else 0.) for a in node.actions
                }

            # call recursion on children
            for a in node.actions:
                init_map_rec(node.play(a), fill)
        # start recursion
        init_map_rec(self.root, fill)

        return mapping


    def update_sigma(self):
        def update_sigma_rec(node):
            
            # no update at root, user, or terminal node
            if node.is_root() or node.player == self.user:
                pass
            elif node.is_terminal():
                return None
            else:
                
                # get information set and cumulative regret
                # the regret is threshold at 0 cause negative probabilities don't exist
                info_set    = node.info_set
                r           = np.array(list(self.r_cum[info_set].values()))
                s_new       = np.maximum(r, 0)
                # sum to normalizer
                s_new_norm  = np.sum(s_new)

                # update sigma and cumulative sigma for the information set
                for i, a in enumerate(self.sigma[info_set]):

                    # if any of the regrets is positive, each action probability is proportional to the regret
                    # otherwise, a uniform strategy is returned
                    self.sigma[info_set][a]         = s_new[i]/s_new_norm if s_new_norm > 0 else 1./self.N_ACTIONS
                    # sum to cumulative sigma
                    self.sigma_cum[info_set][a]    += self.sigma[info_set][a]
                
            # call recursion on children
            for a in node.actions:
                update_sigma_rec(node.play(a))
        # start recursion
        update_sigma_rec(self.root)


    def sample_action(self, info_set):
        
        # get sigma for info set
        sigma_i = self.sigma[info_set]

        # sample from categorical distributon
        rnd     = np.random.random()
        a_idx   = np.argmax(rnd < np.cumsum(list(sigma_i.values())))
        a       = list(sigma_i.keys())[a_idx]

        return a


    def traverse_tree(self):
        
        # deal cards
        node = self.root.deal_cards()
        while True:

            # return evaluation at terminal node
            if node.is_terminal():
                return node.eval()
            else:

                # sample action and proceed to child otherwise
                a       = self.sample_action(node.info_set)
                node    = node.play(a)
        

    def play(self, n_rounds, tracking=False):

        # keep track of rewards
        rewards = []

        epoch   = 0
        while epoch < n_rounds:
            epoch += 1

            # traverse tree to compute utility and update
            rewards.append(self.traverse_tree())
            self.compute_u(self.root)
            self.update_sigma()
        
        if tracking:
            return rewards
        

### ---------------------------------------------------------------------------------------------------- ###
### CFR + BOT



class CFRPlusBot(CFRBot):

    def __init__(self, root, user, user_sigma):
        super().__init__(root=root, user=user, user_sigma=user_sigma)

    
    def compute_u(self, node, p=1, p_cfr=1):

        # get information set and initialize utility
        info_set    = node.info_set
        u_actions   = dict()
        u_tot       = 0

        if node.is_root():
            for a in node.actions:
                # accumulate utilities for each child
                # both realization probabilities are still 1 cause neither of the players moved
                u_tot += self.compute_u(node.play(a), p, p_cfr)
            
            # return weigthed average of the total utility
            return (1/6)*u_tot
        
        # return node evaluation at terminal state
        elif node.is_terminal():
            return node.eval()
        else:

            for a in node.actions:
                # get new realization probabilities wrt player 1
                # fix probability for player 2 cause once the information set is reached, where to go only depends on player 1
                p_child     = p*(self.sigma[info_set][a] if node.player == 1 else 1)
                p_cfr_child = p_cfr*(self.sigma[info_set][a] if node.player == 2 else 1)

                # discount utility for each child by the probability of reaching the information set
                u_actions[a] = self.compute_u(node.play(a), p_child, p_cfr_child)
                u_tot       += self.sigma[info_set][a]*u_actions[a]
        
        # get counterfactual probabilities wrt player 1
        p, p_cfr = (p, p_cfr) if node.player == 1 else (p_cfr, p)

        for a in node.actions:
            # discount regret by counterfactual probability
            # fix probability for player 1 cause the regret is computed wrt pure actions
            r = p_cfr*(u_actions[a]-u_tot)*(1 if node.player == 1 else -1)

            # difference wrt Vanilla CFR
            # threshold the cumulative regret to 0 at each iteration rather than just in the update
            self.r_cum[info_set][a]      = max(self.r_cum[info_set][a]+r, 0)
            self.sigma_cum[info_set][a] += p*self.sigma[info_set][a]
        
        return u_tot


### ---------------------------------------------------------------------------------------------------- ###
### Chance sampling CFR BOT


class CsCFRBot(CFRBot):
    
    def __init__(self, root, user, user_sigma):
        super().__init__(root=root, user=user, user_sigma=user_sigma)


    def compute_u(self, node, p=1, p_cfr=1):

        # get information set and initialize utility
        info_set    = node.info_set
        u_actions   = dict()
        u_tot       = 0

        if node.is_root():
            # difference wrt VanillaCFR
            # sample a possible dealing and run the algorithm there instead of evaluating all possible outcomes
            return self.compute_u(node.deal_cards())
        
        # return node evaluation at terminal state
        elif node.is_terminal():
            return node.eval()
        else:

            for a in node.actions:
                # get new realization probabilities wrt player 1
                # fix probability for player 2 cause once the information set is reached, where to go only depends on player 1
                p_child     = p*(self.sigma[info_set][a] if node.player == 1 else 1)
                p_cfr_child = p_cfr*(self.sigma[info_set][a] if node.player == 2 else 1)

                # discount utility for each child by the probability of reaching the information set
                u_actions[a] = self.compute_u(node.play(a), p_child, p_cfr_child)
                u_tot       += self.sigma[info_set][a]*u_actions[a]
        
        # get counterfactual probabilities wrt player 1
        p, p_cfr = (p, p_cfr) if node.player == 1 else (p_cfr, p)

        for a in node.actions:
            # discount regret by counterfactual probability
            # fix probability for player 1 cause the regret is computed wrt pure actions
            r = p_cfr*(u_actions[a]-u_tot)*(1 if node.player == 1 else -1)

            # update cumulative regret and cumulative sigma
            self.r_cum[info_set][a]     += r
            self.sigma_cum[info_set][a] += p*self.sigma[info_set][a]
        
        return u_tot
