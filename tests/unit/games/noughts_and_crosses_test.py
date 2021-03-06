import itertools

import numpy as np
import pytest

from alphago.games.noughts_and_crosses import (NoughtsAndCrosses, UltimateNoughtsAndCrosses,
                                               UltimateGameState, UltimateAction)
from .constants import (expected_next_states_list, non_terminal_states, actions_to_binary_list,
                        terminal_states, outcomes, win_bitmasks_list)


class TestMByNNoughtsAndCrosses:
    sizes = [(3, 3), (3, 5), (4, 7), (5, 6), (8, 8), (9, 9)]

    @pytest.mark.parametrize("size", sizes)
    def test_noughts_and_crosses_instances_have_correct_size(self, size, mocker):
        mock_game = mocker.MagicMock()
        rows, columns = size
        NoughtsAndCrosses.__init__(mock_game, *size)
        assert mock_game.rows == rows
        assert mock_game.columns == columns

    @pytest.mark.parametrize("size", sizes)
    def test_initial_state_is_correct(self, size, mocker):
        mock_game = mocker.MagicMock()
        NoughtsAndCrosses.__init__(mock_game, *size)
        assert mock_game.initial_state == (0, 0, 1)

    @pytest.mark.parametrize("size, actions_to_binary",
                             zip(sizes, actions_to_binary_list))
    def test_action_to_binary_is_correct(self, size, actions_to_binary, mocker):
        mock_game = mocker.MagicMock()
        NoughtsAndCrosses.__init__(mock_game, *size)
        assert mock_game._actions_to_binary == actions_to_binary

    @pytest.mark.parametrize("size, actions_to_binary, win_bitmasks",
                             zip(sizes, actions_to_binary_list, win_bitmasks_list))
    def test_calculating_row_win_bitmasks(self, size, actions_to_binary,
                                          win_bitmasks, mocker):
        rows, columns = size
        mock_game = mocker.MagicMock(rows=rows, columns=columns,
                                     _actions_to_binary=actions_to_binary)
        row_win_bitmasks = NoughtsAndCrosses._calculate_row_bitmasks(mock_game)
        print([(bin(x), bin(y)) for x, y in zip(row_win_bitmasks, win_bitmasks["row"])])
        assert row_win_bitmasks == win_bitmasks["row"]

    @pytest.mark.parametrize("size, actions_to_binary, win_bitmasks",
                             zip(sizes, actions_to_binary_list, win_bitmasks_list))
    def test_calculating_minor_diagonal_win_bitmasks(self, size, actions_to_binary,
                                                     win_bitmasks, mocker):
        rows, columns = size
        mock_game = mocker.MagicMock(rows=rows, columns=columns,
                                     _actions_to_binary=actions_to_binary)
        column_win_bitmasks = NoughtsAndCrosses._calculate_column_bitmasks(mock_game)
        print([(bin(x), bin(y)) for x, y in zip(column_win_bitmasks, win_bitmasks["column"])])
        assert column_win_bitmasks == win_bitmasks["column"]

    @pytest.mark.parametrize("size, actions_to_binary, win_bitmasks",
                             zip(sizes, actions_to_binary_list, win_bitmasks_list))
    def test_calculating_major_diagonal_win_bitmasks(self, size, actions_to_binary,
                                                     win_bitmasks, mocker):
        rows, columns = size
        mock_game = mocker.MagicMock(rows=rows, columns=columns,
                                     _actions_to_binary=actions_to_binary)
        major_diagonal_win_bitmasks = NoughtsAndCrosses._calculate_major_diagonal_bitmasks(mock_game)
        print([(bin(x), bin(y)) for x, y in zip(major_diagonal_win_bitmasks, win_bitmasks["major_diagonal"])])
        assert major_diagonal_win_bitmasks == win_bitmasks["major_diagonal"]

    @pytest.mark.parametrize("size, actions_to_binary, win_bitmasks",
                             zip(sizes, actions_to_binary_list, win_bitmasks_list))
    def test_calculating_minor_diagonal_win_bitmasks(self, size, actions_to_binary,
                                                     win_bitmasks, mocker):
        rows, columns = size
        mock_game = mocker.MagicMock(rows=rows, columns=columns,
                                     _actions_to_binary=actions_to_binary)
        minor_diagonal_win_bitmasks = NoughtsAndCrosses._calculate_minor_diagonal_bitmasks(mock_game)
        print([(bin(x), bin(y)) for x, y in zip(minor_diagonal_win_bitmasks, win_bitmasks["minor_diagonal"])])
        assert minor_diagonal_win_bitmasks == win_bitmasks["minor_diagonal"]

    @pytest.mark.parametrize("size, actions_to_binary, win_bitmasks, state",
                             zip(sizes, actions_to_binary_list,
                                 win_bitmasks_list, terminal_states))
    def test_is_terminal_returns_true_for_terminal_states(self, size, actions_to_binary,
                                                          win_bitmasks, state, mocker):
        rows, columns = size
        mock_game = mocker.MagicMock(rows=rows, columns=columns,
                                     _actions_to_binary=actions_to_binary,
                                     _win_bitmasks=win_bitmasks)
        print(state)
        assert NoughtsAndCrosses.is_terminal(mock_game, state) is True

    @pytest.mark.parametrize("size, actions_to_binary, win_bitmasks, state",
                             zip(sizes, actions_to_binary_list,
                                 win_bitmasks_list, non_terminal_states))
    def test_is_terminal_returns_false_for_non_terminal_states(self, size, actions_to_binary,
                                                               win_bitmasks, state, mocker):
        rows, columns = size
        mock_game = mocker.MagicMock(rows=rows, columns=columns,
                                     _actions_to_binary=actions_to_binary,
                                     _win_bitmasks=win_bitmasks)
        assert NoughtsAndCrosses.is_terminal(mock_game, state) is False

    players = (2, 1, 1, 1, 1)

    @pytest.mark.parametrize("player, state",
                             zip(players, non_terminal_states))
    def test_current_player_returns_correct_player(self, player, state, mocker):
        mock_game = mocker.MagicMock()
        assert NoughtsAndCrosses.current_player(mock_game, state) == player

    @pytest.mark.parametrize("size, state", zip(sizes, non_terminal_states))
    def test_utility_raises_exception_on_non_terminal_input_state(self, size, state, mocker):
        rows, columns = size
        mock_is_terminal = mocker.MagicMock(return_value=False)
        mock_game = mocker.MagicMock(rows=rows, columns=columns,
                                     is_terminal=mock_is_terminal)
        with pytest.raises(ValueError) as exception_info:
            NoughtsAndCrosses.utility(mock_game, state)
        assert str(exception_info.value) == ("Utility can not be calculated "
                                             "for a non-terminal state.")
        mock_is_terminal.assert_called_once_with(state)

    @pytest.mark.parametrize("size, win_bitmasks, state, outcome",
                             zip(sizes, win_bitmasks_list, terminal_states, outcomes))
    def test_utility_function_returns_correct_outcomes(self, size, win_bitmasks,
                                                       state, outcome, mocker):
        rows, columns = size
        mock_game = mocker.MagicMock(rows=rows, columns=columns, _win_bitmasks=win_bitmasks)

        assert NoughtsAndCrosses.utility(mock_game, state) == outcome

    def test_legal_actions_raises_exception_on_terminal_input_state(self, mocker):
        mock_game = mocker.MagicMock()
        mock_game.is_terminal = mocker.MagicMock(return_value=True)
        mock_state = mocker.MagicMock()
        with pytest.raises(ValueError) as exception_info:
            NoughtsAndCrosses.legal_actions(mock_game, mock_state)
        assert str(exception_info.value) == ("Legal actions can not be computed"
                                             " for a terminal state.")

    def test_generating_next_state_from_given_action_and_state(self, mocker):
        pass

    @pytest.mark.parametrize("size, actions_to_binary, state, player, expected_states",
                             zip(sizes, actions_to_binary_list, non_terminal_states,
                                 players, expected_next_states_list))
    def test_generating_a_dict_of_all_possible_next_states(self, size, actions_to_binary, state,
                                                           player, expected_states, mocker):
        # TODO: need to split this into two tests: one testing the _next_state function and one testing legal actions
        rows, columns = size
        mock_game = mocker.MagicMock(rows=rows, columns=columns,
                                     _actions_to_binary=actions_to_binary)
        mock_game.is_terminal = mocker.MagicMock(return_value=False)
        mock_game.current_player = mocker.MagicMock(return_value=player)
        assert NoughtsAndCrosses.legal_actions(mock_game, state) == expected_states

    states = [
        (0b000000000, 0b000000000, 1),
        (0b001010001, 0b100000010, 2),
        (0b100001111, 0b011110000, 2)
    ]
    div = "---+---+---"
    # additional newline character accounts for the one added to the output
    # by the print function itself
    outputs = [
        "\n".join(("   |   |   ", div, "   |   |   ", div, "   |   |   ")) + "\n",
        "\n".join((" x | o |   ", div, "   | x |   ", div, " x |   | o ")) + "\n",
        "\n".join((" x | x | x ", div, " x | o | o ", div, " o | o | x ")) + "\n",
    ]

    @pytest.mark.parametrize("state, expected_output", zip(states, outputs))
    def test_display_function_outputs_correct_string_for_3x3(self, state, expected_output,
                                                             capsys, mocker):
        mock_game = mocker.MagicMock(rows=3, columns=3,
                                     _actions_to_binary=actions_to_binary_list[0])
        NoughtsAndCrosses.display(mock_game, state)

        output = capsys.readouterr().out
        assert output == expected_output


class TestUltimateNoughtsAndCrosses:
    initial_state = UltimateGameState(last_sub_action=(0, 0), board=(0,) * 81)

    action_space = tuple(UltimateAction(sub_board, sub_action)
                         for sub_board in itertools.product(range(3), range(3))
                         for sub_action in itertools.product(range(3), range(3)))

    action_indices = {}
    for action in action_space:
        sub_board_row, sub_board_col = action.sub_board
        sub_row, sub_col = action.sub_action
        action_indices[action] = (sub_board_row * 27 + sub_board_col * 3 +
                                  sub_row * 9 + sub_col)

    index_to_action = {index: action for action, index
                       in action_indices.items()}

    def test_initial_state_is_correct(self, mocker):
        mock_game = mocker.MagicMock()
        UltimateNoughtsAndCrosses.__init__(mock_game)

        assert mock_game.initial_state == self.initial_state

    terminal_board = [0] * 81
    terminal_board[18:27] = [1] * 9
    terminal_board[54:56] = [-1] * 2
    terminal_board[57:63] = [-1] * 6
    terminal_state1 = UltimateGameState(last_sub_action=(0, 0), board=tuple(terminal_board))
    meta_board1 = (1, 1, 1, 0, 0, 0, 0, -1, -1)
    utilities1 = ({1: 1, 2: -1}, {1: 1, 2: -1}, {1: 1, 2: -1},
                  ValueError, ValueError, ValueError,
                  ValueError, {1: -1, 2: 1}, {1: -1, 2: 1})

    terminal_state2 = UltimateGameState(
        last_sub_action=(0, 2),
        board=(
            1, 0, 1, -1, 0, 0, 0, 1, 0,
            -1, 1, 1, 1, -1, 0, 0, -1, 0,
            1, 0, -1, 0, 0, -1, 0, 1, 0,
            0, 1, 0, 1, 1, 1, 0, 0, -1,
            0, -1, 0, -1, -1, 1, 0, -1, 0,
            -1, 1, 0, 0, 0, -1, -1, 0, 0,
            0, -1, 0, -1, -1, -1, 0, 1, 0,
            0, 1, 0, 0, 0, 0, 0, 1, 0,
            0, 1, 0, 0, 0, 0, 0, 1, 0)
    )
    meta_board2 = (1, -1, 0, 0, 1, -1, 0, -1, 1)
    utilities2 = ({1: 1, 2: -1}, {1: -1, 2: 1}, ValueError,
                  ValueError, {1: 1, 2: -1}, {1: -1, 2: 1},
                  ValueError, {1: -1, 2: 1}, {1: 1, 2: -1})

    terminal_state3 = UltimateGameState(
        last_sub_action=(0, 0),
        board=(
            0, -1, 0, -1, 0, 1, -1, 0, 0,
            1, 0, 1, 0, 1, 0, -1, 1, 0,
            0, 1, 1, 1, 0, 0, 1, 0, 0,
            -1, 0, 0, 0, 1, 0, 0, -1, 1,
            -1, 0, 1, 0, 1, 0, 0, 0, 0,
            -1, 0, 1, -1, 1, -1, -1, 0, 0,
            1, -1, 0, 1, 0, -1, 0, 0, -1,
            0, -1, 0, 1, 0, 0, 0, -1, -1,
            0, -1, 0, 1, -1, 0, 0, 0, 1)
    )
    meta_board3 = (0, 1, 0, -1, 1, 0, -1, 1, 0)
    utilities3 = (ValueError, {1: 1, 2: -1}, ValueError,
                  {1: -1, 2: 1}, {1: 1, 2: -1}, ValueError,
                  {1: -1, 2: 1}, {1: 1, 2: -1}, ValueError)

    terminal_state4 = UltimateGameState(
        last_sub_action=(0, 1),
        board=(
            1, -1, 1, 0, 1, -1, 1, -1, -1,
            0, -1, 1, 1, 1, 1, 0, 1, -1,
            -1, 0, 1, -1, 1, 0, 0, 0, -1,
            -1, -1, -1, -1, 0, 0, 0, 1, 1,
            1, 1, -1, -1, 1, 0, -1, 1, -1,
            1, -1, 0, -1, 0, 0, 0, 1, 0,
            0, 1, 1, 0, -1, 1, 0, 0, 0,
            1, 1, 0, 0, -1, 0, -1, -1, -1,
            -1, 1, -1, 0, -1, 1, 0, 0, 1)
    )
    meta_board4 = (1, 1, -1, -1, -1, 1, 1, -1, -1)
    utilities4 = ({1: 1, 2: -1}, {1: 1, 2: -1}, {1: -1, 2: 1},
                  {1: -1, 2: 1}, {1: -1, 2: 1}, {1: 1, 2: -1},
                  {1: 1, 2: -1}, {1: -1, 2: 1}, {1: -1, 2: 1})

    terminal_states = (terminal_state1, terminal_state2, terminal_state3, terminal_state4)
    meta_boards = (meta_board1, meta_board2, meta_board3, meta_board4)
    utilities_list = (utilities1, utilities2, utilities3, utilities4)

    @pytest.mark.parametrize("state, meta_board, utilities",
                             zip(terminal_states, meta_boards, utilities_list))
    def test_meta_board_delegates_to_sub_game_utility_method(self, state, meta_board,
                                                             utilities, mocker):
        mock_utility = mocker.MagicMock(side_effect=utilities)
        mock_nac = mocker.MagicMock(utility=mock_utility)
        mock_game = mocker.MagicMock(sub_game=mock_nac)
        # split state into sub boards
        board = np.array(state.board).reshape(9, 9)
        sub_boards = [board[i * 3:(i + 1) * 3, j * 3:(j * 3) + 3]
                      for i in range(3) for j in range(3)]

        expected_calls = [mocker.call(tuple(sub_board.ravel()))
                          for sub_board in sub_boards]

        assert UltimateNoughtsAndCrosses._compute_meta_board(mock_game, state) == meta_board
        mock_utility.assert_has_calls(expected_calls)

    def test_is_terminal_calls_compute_meta_board(self, mocker):
        mock_is_terminal = mocker.MagicMock()
        mock_game = mocker.MagicMock(
            sub_game=mocker.MagicMock(is_terminal=mock_is_terminal),
            _compute_meta_board=mocker.MagicMock(return_value="some_meta_board"))
        mock_state = mocker.MagicMock()
        UltimateNoughtsAndCrosses.is_terminal(mock_game, mock_state)
        mock_game._compute_meta_board.assert_called_once_with(mock_state)
        mock_is_terminal.assert_called_once_with("some_meta_board")

    def test_utility_calls_compute_meta_board(self, mocker):
        mock_utility = mocker.MagicMock()
        mock_game = mocker.MagicMock(
            sub_game=mocker.MagicMock(utility=mock_utility),
            _compute_meta_board=mocker.MagicMock(return_value="some_meta_board"))
        mock_state = mocker.MagicMock()
        UltimateNoughtsAndCrosses.utility(mock_game, mock_state)

        mock_game._compute_meta_board.assert_called_once_with(mock_state)
        mock_utility.assert_called_once_with("some_meta_board")

    def test_current_player_delegates_to_sub_game_current_player(self, mocker):
        mock_current_player = mocker.MagicMock()
        mock_game = mocker.MagicMock(sub_game=mocker.MagicMock(current_player=mock_current_player))
        mock_state = mocker.MagicMock()
        UltimateNoughtsAndCrosses.current_player(mock_game, mock_state)
        mock_current_player.assert_called_once_with(mock_state.board)

    def test_compute_next_states_raises_exception_on_terminal_input_state(self, mocker):
        mock_game = mocker.MagicMock()
        mock_game.is_terminal = mocker.MagicMock(return_value=True)
        mock_state = mocker.MagicMock()
        with pytest.raises(ValueError) as exception_info:
            UltimateNoughtsAndCrosses.compute_next_states(mock_game, mock_state)
        assert str(exception_info.value) == ("Next states can not be generated "
                                             "for a terminal state.")

    def test_compute_next_states_returns_correct_states_on_initial_state(self, mocker):
        # generate dictionary of all next states (all of them)
        next_states = {}
        for action_index in range(81):
            action = self.index_to_action[action_index]
            board = list(self.initial_state.board)
            board[action_index] = 1
            next_state = UltimateGameState(last_sub_action=action.sub_action,
                                           board=tuple(board))
            next_states[action] = next_state

        mock_is_terminal = mocker.MagicMock(return_value=False)
        mock_current_player = mocker.MagicMock(return_value=1)
        mock_game = mocker.MagicMock(is_terminal=mock_is_terminal,
                                     current_player=mock_current_player,
                                     initial_state=self.initial_state,
                                     index_to_action=self.index_to_action)
        assert UltimateNoughtsAndCrosses.compute_next_states(
            mock_game, self.initial_state) == next_states

    def test_compute_next_states_returns_correct_states_for_incomplete_sub_board(self, mocker):
        first_state = UltimateGameState(last_sub_action=(0, 0), board=(1,) + (0,) * 80)
        next_states = {}
        sub_actions = (sub_action for sub_action in itertools.product(range(3), range(3))
                       if sub_action != (0, 0))
        for (sub_row, sub_col) in sub_actions:
            action = UltimateAction(sub_board=(0, 0),
                                    sub_action=(sub_row, sub_col))
            board_index = sub_row * 9 + sub_col
            board = list(first_state.board)
            board[board_index] = -1
            next_state = UltimateGameState(last_sub_action=(sub_row, sub_col),
                                           board=tuple(board))
            next_states[action] = next_state

        mock_is_terminal = mocker.MagicMock(return_value=False)
        mock_game = mocker.MagicMock(is_terminal=mock_is_terminal,
                                     action_indices=self.action_indices,
                                     sub_game=mocker.MagicMock(is_terminal=mock_is_terminal))
        assert UltimateNoughtsAndCrosses.compute_next_states(
            mock_game, first_state) == next_states

    @pytest.mark.skip(reason="not implemented yet.")
    def test_compute_next_states_returns_correct_state_on_complete_sub_board(self, mocker):
        # board with completed top left sub board
        board = [0] * 81
        board[0] = board[10] = board[20] = 1
        board[3] = board[30] = board[60] = -1
        state = UltimateGameState(last_sub_action=(0, 0), board=tuple(board))
        next_states = {}
        for action_index in range(81):
            if board[action_index] == 0:
                action = self.index_to_action[action_index]
                board = list(self.initial_state.board)
                board[action_index] = 1
                next_state = UltimateGameState(last_sub_action=action.sub_action,
                                               board=tuple(board))
                next_states[action] = next_state

        mock_is_terminal = mocker.MagicMock(return_value=False)
        mock_current_player = mocker.MagicMock(return_value=1)
        mock_sub_game = mocker.MagicMock(is_terminal=mocker.MagicMock(return_value=True))
        mock_game = mocker.MagicMock(is_terminal=mock_is_terminal,
                                     current_player=mock_current_player,
                                     index_to_action=self.index_to_action,
                                     sub_game=mock_sub_game)
        assert UltimateNoughtsAndCrosses.compute_next_states(
            mock_game, state) == next_states
