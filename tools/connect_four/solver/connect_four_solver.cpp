/*
 * This file is part of Connect4 Game Solver <http://connect4.gamesolver.org>
 * Copyright (C) 2007 Pascal Pons <contact@gamesolver.org>
 *
 * Connect4 Game Solver is free software: you can redistribute it and/or
 * modify it under the terms of the GNU Affero General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 *
 * Connect4 Game Solver is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with Connect4 Game Solver. If not, see <http://www.gnu.org/licenses/>.
 */

#include "solver.hpp"
#include <iostream>
#include <fstream>

using namespace GameSolver::Connect4;

/*
 * Main function.
 * Reads Connect 4 positions, line by line, from standard input
 * and writes one line per position to standard output containing:
 *  - score of the position
 *  - number of nodes explored
 *  - time spent in microsecond to solve the position.
 *
 *  Any invalid position (invalid sequence of move, or already won game)
 *  will generate an error message to standard error and an empty line to standard output.
 */
int sign(int x) {
  if (x > 0) return 1;
  if (x < 0) return -1;
  return 0;
}

int main(int argc, char** argv) {
  Solver solver;

  if (argc < 2) {
    std::cout << "Input and output file names must be specified. Run as 'connect_four_solve_state state'" << std::endl;
    return 0;
  }
  std::string state = argv[1];

  int optimal_move, optimal_score;
  std::pair<int, int> result = solver.optimal_move(state);
  optimal_move = result.first;
  optimal_score = result.second;

  std::cout << state << " " << optimal_move << " " << sign(optimal_score) <<
      std::endl;
}