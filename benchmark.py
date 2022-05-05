# Assets: https://techwithtim.net/wp-content/uploads/2020/09/assets.zip
import time

from checkers.constants import WHITE, RED
from checkers.game import Game
from minimax.algorithm import minimax
from montecarlo.algorithm import montecarlots, MCNode
import argparse

default_weights = (3, 1)
default_max_it = 8


def mcts_ai_move(game, run, tree, max_it=default_max_it):
    """
    Executes a move on the board determined by the MCTS AI.
    """
    new_board, new_tree, best_move = montecarlots(game.board, game.turn, game, tree, max_it)
    if new_board is None:
        print("end of game?")
        run = False
    else:
        game.ai_move(new_board, best_move)
    return run, new_tree, best_move


def minimax_ai_move(game, tree):
    """
    Executes a move on the board determined by the Minimax AI.
    :param game: Game instance
    :param tree: MCTS tree
    """
    value, chosen_move = minimax(game.get_board(), 3, game)
    chosen_move.compute_final_state()
    new_board = chosen_move.final_state
    if tree:
        tree = tree.find_child(new_board)
    if new_board is None:
        new_board = game.board
    game.ai_move(new_board, chosen_move)
    return tree, chosen_move


def make_move(game, p, n, run, tree):
    """
    Executes a move on the board determined by the arguments chosen at game launch.
    """
    start_time = time.time()

    if p[n] == "minimax":
        tree, best_move = minimax_ai_move(game, tree)
    elif p[n] == "mcts":
        run, tree, best_move = mcts_ai_move(game, run, tree, game.max_it)

    end_time = time.time()
    execution_time = end_time - start_time
    return run, tree, best_move, execution_time


def main():
    for n in range(0, 10) :
        run = True
        max_it = 250 -n*10
        game = Game(parameters=[max_it, 0, 1], logging=True)

        p = ["mcts", "minimax"]
        most_recent_tree = None

        while run:

            n = 0 if game.turn == WHITE else 1
            count_red = len(game.board.get_all_pieces(RED))
            count_white = len(game.board.get_all_pieces(WHITE))
            run, most_recent_tree, move, move_time = make_move(game, p, n, run, most_recent_tree)

            # Keep track in the log file
            game.update_log(move, move_time, p[n], count_red, count_white)

            if game.winner() is not None:
                run = False

        game.update_log_winner(game.winner())


main()
