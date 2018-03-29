from . import mcts, MCTSNode
from .backwards_induction import backwards_induction


class AbstractPlayer:

    def __init__(self, player_no, game):
        self.player_no = player_no  # TODO: do Players need to know this
        self.game = game

    def action_probabilities(self, game_state):
        raise NotImplementedError

    def __repr__(self):
        return f"{self.__class__.__name__}({self.game})"


class RandomPlayer(AbstractPlayer):

    def action_probabilities(self, game_state):
        next_states = self.game.compute_next_states(game_state)

        return {action: 1 / len(next_states) for action in next_states.keys()}


class MCTSPlayer(AbstractPlayer):

    def __init__(self, player_no, game, estimator, mcts_iters, c_puct):
        super().__init__(player_no, game)
        self.estimator = estimator
        self.mcts_iters = mcts_iters
        self.c_puct = c_puct

    def action_probabilities(self, game_state):
        current_node = MCTSNode(game_state, self.player_no)
        action_probs = mcts(current_node, self.game, self.estimator,
                            self.mcts_iters, self.c_puct)
        return action_probs


class OptimalPlayer(AbstractPlayer):  # TODO: Add UTs

    def action_probabilities(self, game_state):
        value, action = backwards_induction(self.game, game_state)
        return {action: 1}
