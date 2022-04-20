# Assets: https://techwithtim.net/wp-content/uploads/2020/09/assets.zip
import time

from checkers.constants import WHITE, RED
from checkers.game import Game
from minimax.algorithm import minimax
from montecarlo.algorithm import montecarlots, MCNode
import argparse



def mcts_ai_move(game, run, tree):
    """
    Executes a move on the board determined by the MCTS AI.
    """
    new_board, new_tree, best_move = montecarlots(game.board,game.turn, game, tree)
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
        tree = tree.get_child(new_board)
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
        run, tree, best_move = mcts_ai_move(game, run, tree)

    end_time = time.time()
    execution_time = end_time - start_time
    return run, tree, best_move, execution_time


def main():



    run = True
    game = Game(benchmark=True)

    parser = argparse.ArgumentParser(description="Checkers game")
    parser.add_argument(
        "--player1",
        "--p1",
        "-1",
        type=str,
        help="Type of player for player 1",
        required=True,
        choices=("minimax", "mcts", "human"),
        default="minimax",
    )
    parser.add_argument(
        "--player2",
        "--p2",
        "-2",
        type=str,
        help="Type of player for player 2",
        required=True,
        choices=("minimax", "mcts", "human"),
        default="mcts",
    )
    args = parser.parse_args()

    p = [args.player1, args.player2]
    most_recent_tree = None

    while run:

        n = 0 if game.turn == WHITE else 1
        run, most_recent_tree, move, move_time = make_move(game, p, n, run, most_recent_tree)

        # Keep track in the log file
        game.update_log(move, move_time, p[n], count_red, count_white)



        if game.winner() is not None:
            run = False

    game.update_log_winner(game.winner())

main()
