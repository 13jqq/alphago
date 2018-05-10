from collections import OrderedDict
import json

import numpy as np
from tqdm import tqdm

from .player import MCTSPlayer, RandomPlayer
from .evaluator import evaluate
from .mcts_tree import MCTSNode, mcts
from .utilities import sample_distribution

__all__ = ["train_alphago", "self_play", "process_self_play_data",
           "process_training_data"]


def compute_checkpoint_name(step, path):
    return path + "{}.checkpoint".format(step)


def train_alphago(game, create_estimator, self_play_iters, training_iters,
                  checkpoint_path, alphago_steps=100, evaluate_every=1,
                  batch_size=32, mcts_iters=100, c_puct=1.0,
                  replay_length=100000, num_evaluate_games=500,
                  win_rate=0.55, verbose=True, restore_step=None,
                  self_play_file_path=None):
    """Trains AlphaGo on the game.

    Parameters
    ----------
    game: object
        An object that has the attributes a game needs.
    create_estimator: func
        Creates a trainable estimator for the game. The estimator should
        have a train function.
    self_play_iters: int
        Number of self-play games to play each self-play step.
    training_iters: int
        Number of training iters to use for each training step.
    checkpoint_path: str
        Where to save the checkpoints to.
    alphago_steps: int
        Number of steps to run the alphago loop for.
    evaluate_every: int
        Evaluate the network every evaluate_every steps.
    batch_size: int
        Batch size to train with.
    mcts_iters: int
        Number of iterations to run MCTS for.
    c_puct: float
        Parameter for MCTS. See AlphaGo paper.
    replay_length: int
        The amount of training data to use. Only train on the most recent
        training data.
    evaluator_games: int
        Number of games to evaluate the players for.
    win_rate: float
        Number between 0 and 1. Only update self-play player when training
        player beats self-play player by at least this rate.
    verbose: bool
        Whether or not to output progress.
    restore_step: int or None
        If given, restore the network from the checkpoint at this step.
    self_play_file_path: str or None
        Where to load self play data from, if given.
    """
    # TODO: Do self-play, training and evaluating in parallel.

    # We use a fixed estimator (the best one that's been trained) to
    # generate self-play training data. We then train the training estimator
    # on that data. We produce a checkpoint every 1000 training steps. This
    # checkpoint is then evaluated against the current best neural network.
    # If it beats the current best network by at least 55% then it becomes
    # the new best network.
    # 1 is the fixed player, and 2 is the training player.
    self_play_player = create_estimator()
    training_player = create_estimator()

    if restore_step:
        restore_path = compute_checkpoint_name(restore_step, checkpoint_path)
        self_play_player.restore(restore_path)
        training_player.restore(restore_path)

    all_losses = []

    initial_step = restore_step + 1 if restore_step else 0
    for alphago_step in range(initial_step, initial_step +
                                            alphago_steps):
        self_play_data = generate_self_play_data(
            game, self_play_player, mcts_iters, c_puct, self_play_iters,
            verbose=verbose, save_file_path=self_play_file_path)

        training_data = process_training_data(self_play_data, replay_length)
        losses = optimise(training_player, training_data, batch_size,
                          training_iters, output_losses=True, verbose=verbose)

        all_losses.append(losses)
        if verbose:
            print("Mean loss: {}".format(np.mean(losses)))

        # Evaluate the players and choose the best.
        if alphago_step % evaluate_every == 0:
            training_win_rate = evaluate_model(game, self_play_player,
                                               training_player, mcts_iters,
                                               c_puct, num_evaluate_games)
            checkpoint_model(training_player, alphago_step, checkpoint_path)

            # If training player beats self-play player by a large enough
            # margin, then it becomes the new best estimator.
            if training_win_rate > win_rate:
                # Create a new self player, with the weights of the most
                # recent training_player.
                if verbose:
                    print("Updating self-play player.")
                    print("Restoring from step: {}".format(alphago_step))
                self_play_player = create_estimator()
                restore_path = compute_checkpoint_name(alphago_step,
                                                       checkpoint_path)
                self_play_player.restore(restore_path)

    return all_losses


def optimise(estimator, training_data, batch_size, training_iters,
             output_losses=True, verbose=True):
    losses = estimator.train(training_data, batch_size, training_iters,
                             verbose=verbose)
    if output_losses:
        return losses


def evaluate_model(game, player1, player2, mcts_iters, c_puct, num_games):
    # Checkpoint the model.
    # TODO: Implement evaluation
    # TODO: Choose tau more systematically.

    print("Evaluating. Self-player vs training, then training vs "
          "self-player")
    wins1, wins2, draws = evaluate_estimators_in_both_positions(
        game, player1.create_estimate_fn(), player2.create_estimate_fn(),
        mcts_iters, c_puct, num_games, tau=0.1)

    print("Self-play player wins: {}, Training player wins: {}, "
          "Draws: {}".format(wins1, wins2, draws))
    training_win_rate = wins2 / (wins1 + wins2 + draws)
    print("Win rate for training player: {}".format(
        training_win_rate))

    # Also evaluate against a random player
    wins1, wins2, draws = evaluate_mcts_against_random_player(
        game, player2.create_estimate_fn(), mcts_iters, c_puct, num_games,
        tau=0.1)
    print("Training player vs random. Wins: {}, Losses: {}, "
          "Draws: {}".format(wins1, wins2, draws))

    return training_win_rate


def checkpoint_model(player, step, path):
    """Checkpoint the training player.
    """
    checkpoint_name = compute_checkpoint_name(step, path)
    player.save(checkpoint_name)


def evaluate_mcts_against_random_player(game, estimator, mcts_iters,
                                        c_puct, num_evaluate_games, tau):
    # Evaluate estimator1 vs estimator2.
    players = {1: MCTSPlayer(game, estimator, mcts_iters, c_puct, tau=tau),
               2: RandomPlayer(game)}
    player1_results, _ = evaluate(game, players, num_evaluate_games)
    wins1 = player1_results[1]
    wins2 = player1_results[-1]
    draws = player1_results[0]

    # Evaluate estimator2 vs estimator1.
    players = {1: RandomPlayer(game),
               2: MCTSPlayer(game, estimator, mcts_iters, c_puct, tau=tau)}
    player1_results, _ = evaluate(game, players, num_evaluate_games)
    wins1 += player1_results[-1]
    wins2 += player1_results[1]
    draws += player1_results[0]

    return wins1, wins2, draws


def evaluate_estimators_in_both_positions(game, estimator1, estimator2,
                                          mcts_iters, c_puct,
                                          num_evaluate_games, tau):
    # Evaluate estimator1 vs estimator2.
    players = {1: MCTSPlayer(game, estimator1, mcts_iters, c_puct, tau=tau),
               2: MCTSPlayer(game, estimator2, mcts_iters, c_puct, tau=tau)}
    player1_results, _ = evaluate(game, players, num_evaluate_games)
    wins1 = player1_results[1]
    wins2 = player1_results[-1]
    draws = player1_results[0]

    # Evaluate estimator2 vs estimator1.
    players = {1: MCTSPlayer(game, estimator2, mcts_iters, c_puct, tau=tau),
               2: MCTSPlayer(game, estimator1, mcts_iters, c_puct, tau=tau)}
    player1_results, _ = evaluate(game, players, num_evaluate_games)
    wins1 += player1_results[-1]
    wins2 += player1_results[1]
    draws += player1_results[0]

    return wins1, wins2, draws


def generate_self_play_data(game, estimator, mcts_iters, c_puct, num_iters,
                            save_file_path=None, verbose=True):
    """Generates self play data for a number of iterations for a given
    estimator. Saves to save_file_path, if given.
    """
    if save_file_path is not None:
        with open(save_file_path, 'r') as f:
            data = json.load(save_file_path)
        index = max(data.keys()) + 1
    else:
        data = OrderedDict()
        index = 0

    # Collect self-play training data using the best estimator.
    disable_tqdm = False if verbose else True
    for _ in tqdm(range(num_iters), disable=disable_tqdm):
        data[index] = self_play(
            game, estimator.create_estimate_fn(), mcts_iters, c_puct)

    if save_file_path is not None:
        with open(save_file_path, 'w') as f:
            json.dump(data, f)

    return data


def self_play(game, estimator, mcts_iters, c_puct):
    """Plays a single game using MCTS to choose actions for both players.

    Parameters
    ----------
    game: Game
        An object representing the game to be played.
    estimator: func
        An estimate function.
    mcts_iters: int
        Number of iterations to run MCTS for.
    c_puct: float
        Parameter for MCTS.

    Returns
    -------
    game_state_list: list
        A list of game states encountered in the self-play game. Starts
        with the initial state and ends with a terminal state.
    action_probs_list: list
        A list of action probability dictionaries, as returned by MCTS
        each time the algorithm has to take an action. The ith action
        probabilities dictionary corresponds to the ith game_state, and
        action_probs_list has length one less than game_state_list,
        since we don't have to move in a terminal state.
    """
    node = MCTSNode(game.initial_state, game.which_player(game.initial_state))

    game_state_list = [node.game_state]
    action_probs_list = []
    action_list = []

    move_count = 0

    while not node.is_terminal:
        # TODO: Choose this better.
        tau = 1 / (move_count + 1)

        # First run MCTS to compute action probabilities.
        action_probs = mcts(node, game, estimator, mcts_iters, c_puct, tau=tau)

        # Choose the action according to the action probabilities.
        action = sample_distribution(action_probs)
        action_list.append(action)

        # Play the action
        node = node.children[action]

        # Add the action probabilities and game state to the list.
        action_probs_list.append(action_probs)
        game_state_list.append(node.game_state)
        move_count += 1

    data = process_self_play_data(game_state_list, action_list,
                                  action_probs_list, game, game.action_indices)

    return data


def process_training_data(self_play_data, replay_length=None):
    """Takes self play data and returns a list of tuples (state,
    action_probs, utility) suitable for training an estimator.

    Parameters
    ----------
    self_play_data: dict
        Dictionary with keys given by an index (int) and values given by a
        log of the game. This is a list of tuples as in generate self play
        data.
    replay_length: int or None
        If given, only return the last replay_length (state, probs, utility)
        tuples.
    """
    training_data = []
    for index, game_log in self_play_data.items():
        for (state, action, probs_vector, z) in game_log:
            training_data.append((state, probs_vector, z))

    if replay_length is not None:
        training_data = training_data[-replay_length:]

    return training_data


def process_self_play_data(states_, actions_, action_probs_, game,
                           action_indices):
    """Takes a list of states and action probabilities, as returned by
    play, and creates training data from this. We build up a list
    consisting of (state, probs, z) tuples, where player is the player
    in state 'state', and 'z' is the utility to 'player' in 'last_state'.

    We omit the terminal state from the list as there are no probabilities to
    train. TODO: Potentially include the terminal state in order to train the
    value.

    Parameters
    ----------
    states_: list
        A list of n states, with the last being terminal.
    actions_: list
        A list of n-1 actions, being the action taken in the corresponding
        state.
    action_probs_: list
        A list of n-1 dictionaries containing action probabilities. The ith
        dictionary applies to the ith state, representing the probabilities
        returned by play of taking each available action in the state.
    game: Game
        An object representing the game to be played.
    action_indices: dict
        A dictionary mapping actions (in the form of the compute_next_states
        function) to action indices (to be used for training the neural
        network).

    Returns
    -------
    training_data: list
        A list consisting of (state, action, probs, z) tuples, where player
        is the player in state 'state', and 'z' is the utility to 'player' in
        'last_state'.
    """

    # Get the outcome for the game. This should be the last state in states_.
    last_state = states_.pop()
    outcome = game.utility(last_state)

    # Now action_probs_ and states_ are the same length.
    training_data = []
    for state, action, probs in zip(states_, actions_, action_probs_):
        # Get the player in the state, and the value to this player of the
        # terminal state.
        player = game.which_player(state)
        z = outcome[player]

        # Convert the probs dictionary to a numpy array using action_indices.
        probs_vector = np.zeros(len(action_indices))
        for a, prob in probs.items():
            probs_vector[action_indices[a]] = prob

        non_nan_state = np.nan_to_num(state)

        training_data.append((non_nan_state, action, probs_vector, z))

    return training_data
