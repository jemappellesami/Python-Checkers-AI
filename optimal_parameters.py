# Let's gooooo
import time
from typing import List

from checkers.board import Board
from checkers.constants import RED, WHITE
import random

from checkers.game import Game
from main import make_ai_move
from montecarlo.algorithm import MCNode

FPS = 60
random.seed(15)
POP_SIZE = 3
NB_GAMES = 2


class Villager:
    def __init__(self, it, safe_heuri, exploit, reward=None):
        self.it = it
        self.safe_heuri = safe_heuri
        self.exploit_param = exploit
        self.reward = reward

    def list_parameters(self) -> List:
        return [self.it, self.safe_heuri, self.exploit_param]


def init_population() -> List[Villager]:
    population = []
    for i in range(POP_SIZE):
        it = random.randint(5, 40)
        safe_heuri = random.uniform(0, 1)
        exploit = random.uniform(0, 1)
        population.append(Villager(it, safe_heuri, exploit))
    return population


def make_move(game, p, run, tree):
    """
    Executes a move on the board determined by the arguments chosen at game launch.
    """
    n = -1
    if game.turn == WHITE:
        n = 0
    elif game.turn == RED:
        n = 1
    else:
        print("Error : game.turn is neither WHITE nor RED")

    start = time.time()
    run, tree, best_move = make_ai_move(game, n, p, run, tree)
    execution_time = time.time() - start

    return run, tree, best_move, execution_time


def play_game(p, param_list) -> float:
    """
    Play a game and return the reward of the game seen from the mcts view
    :param param_list: List of the parameters of a game
    :param p: players setup
    :return: float reward value seen from mcts
    """
    game = Game(param_list, logging=False)
    winner = 0
    most_recent_tree = None
    running = True

    while running:
        running, most_recent_tree, best_move, exec_time = make_move(game, p, running, most_recent_tree)

        if not running:
            if game.turn == WHITE:
                winner = "RED"
            elif game.turn == RED:
                winner = "WHITE"

        if game.winner() is not None:
            running = False
            winner = game.winner()

    print("Partie de simulation terminée")
    if winner == "RED":
        print("Rouge a gagné")
        return 1
    elif winner == "WHITE":
        print("Blanc a gagné")
        return 0
    else:
        return 0.5


def main():
    p = ["minimax", "mcts"]

    optimal = False
    population = init_population()
    j = 0
    while not optimal:
        for villager in population:
            reward = 0
            for i in range(NB_GAMES):
                j += 1
                reward += play_game(p, villager.list_parameters())
                print(j, "'th game is over")
            villager.reward = reward
        population.sort(key=lambda x: x.reward, reverse=True)
        # TODO: select x% of best villagers and fuse them
        break


if __name__ == '__main__':
    main()