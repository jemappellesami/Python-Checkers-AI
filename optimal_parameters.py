# Let's gooooo
from math import factorial, comb
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

    def __repr__(self):
        return "it : " + str(self.it) + '\n safe_heuri : ' \
               + str(self.safe_heuri) + '\n exploit_param : ' \
               + str(self.exploit_param)


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


def parent_comb(parents, n_comb: int):
    """
    :param n_comb: number of combinations to get
    :param parents: list of parents to merge later
    :return: n_comb combinations of parents
    """
    max_n_comb = comb(len(parents), 2)
    if n_comb > max_n_comb:
        print("Asked for more couples than available")
        n_comb = max_n_comb
    couples = []
    while len(couples) < n_comb:
        j = random.randint(0, len(parents) - 1)
        i = random.randint(0, len(parents) - 1)
        while i == j:
            i = random.randint(0, len(parents) - 1)
        couple = {parents[i], parents[j]}
        couples.append(couple) if couple not in couples else None
    return couples


def merge_coupe(couple):
    # TODO : define a merging method
    pass


def evolve_population(population: List):
    # TODO: select x% of best villagers and fuse them and perform mutations
    new_population = merge_population(population)
    mutate_population(new_population)

    return new_population


def mutate_population(new_population):
    # TODO
    pass


def merge_population(population: List):
    population.sort(key=lambda x: x.reward, reverse=True)

    new_population = []
    n_keep = 2

    # Keep best candidates
    for i in range(n_keep):
        new_population.append(population[i])

    # Merge them to get possibly good children
    for couple in parent_comb(new_population, len(population) - n_keep):
        new_child = merge_coupe(couple)
        new_population.append(new_child)
    while len(new_population) <= len(population):
        # Not enough children, complete with more previous generation villagers
        new_population.append(population[n_keep])
        n_keep += 1

    return new_population


def main():
    p = ["minimax", "mcts"]

    converged = False
    population = init_population()
    j = 0
    while not converged:
        for villager in population:
            reward = 0
            for i in range(NB_GAMES):
                j += 1
                reward += play_game(p, villager.list_parameters())
                print(j, "th game is over")
            villager.reward = reward

        # population = evolve_population(population)
        converged = True  # TODO : change
    population.sort(key=lambda x: x.reward, reverse=True)
    print(population[0])


if __name__ == '__main__':
    main()
