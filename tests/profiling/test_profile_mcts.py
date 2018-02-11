import pytest

from alphago import mcts_tree
from alphago.evaluator import trivial_evaluator
import alphago.noughts_and_crosses as nac


def test_self_play_multiple_can_play_nac():
    max_iters = 100
    num_self_play = 10
    c_puct = 1.0

    action_space = [(i, j) for i in range(3) for j in range(3)]

    def which_player(state):
        return state.player

    def evaluator(state):
        return trivial_evaluator(
            state, nac.next_states, action_space, nac.is_terminal,
            nac.utility, which_player)

    training_data = mcts_tree.self_play_multiple(
        nac.next_states, evaluator, nac.INITIAL_STATE, nac.is_terminal,
        nac.utility, which_player, max_iters, c_puct, num_self_play
    )
    assert len(training_data) > 0