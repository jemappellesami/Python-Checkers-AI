# Let's gooooo
import threading
from copy import deepcopy
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
POP_SIZE = 5
N_KEEP = 3  # Nb of pop members to keep between generations
NB_GAMES = 2
MAX_IT_ALLOWED = 10


class Villager:
    def __init__(self, it, safe_heuri, exploit, reward=0, nb_simu=0):
        self.it = it
        self.safe_heuri = safe_heuri
        self.exploit_param = exploit
        self.reward = reward
        self.nb_simu = nb_simu

    @classmethod
    def from_list(cls, params_list):
        return cls(*params_list, reward=0)

    def list_parameters(self) -> List:
        return [self.it, self.safe_heuri, self.exploit_param]

    def __repr__(self):
        return "it : " + str(self.it) + '\nsafe_heuri : ' \
               + str(self.safe_heuri) + '\nexploit_param : ' \
               + str(self.exploit_param) + '\nreward : ' \
               + str(self.reward) + '\nnb_simu : '\
               + str(self.nb_simu)


def init_population() -> List[Villager]:
    population = []
    for i in range(POP_SIZE):
        it = random.randint(5, MAX_IT_ALLOWED)
        safe_heuri = random.uniform(0, 1)
        exploit = random.uniform(0, 1)
        vil = Villager(it, safe_heuri, exploit)
        population.append(vil)
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
    :param param_list: Parameters of the game to play
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

    # print("Partie de simulation terminée")
    if winner == "RED":
        # print("Rouge a gagné")
        return 1
    elif winner == "WHITE":
        # print("Blanc a gagné")
        return 0
    else:
        return 0.5


def combine_parents(parents, n_couples: int):
    """
    Return n_couples pairs of parents randomly drawn
    :param n_couples: number of combinations to get
    :param parents: list of parents to merge later
    :return: n_comb combinations of parents
    """
    max_n_comb = comb(len(parents), 2)
    if n_couples > max_n_comb:
        print("Asked for more couples than available")
        n_couples = max_n_comb
    couples = []
    while len(couples) < n_couples:
        j = random.randint(0, len(parents) - 1)
        i = random.randint(0, len(parents) - 1)
        while i == j:
            i = random.randint(0, len(parents) - 1)
        couple = {parents[i], parents[j]}
        couples.append(couple) if couple not in couples else None
    return couples


def evolve_population(population: List):
    # TODO: select x% of best villagers and fuse them and perform mutations
    new_population = merge_population(population)
    mutate_population(new_population)

    return new_population


def mutate_population(new_population):
    # TODO
    pass


def cross_over(couple) -> Villager:
    # TODO : define a merging method
    # Single point crossover
    i = random.randint(0, len(couple)-1)
    parent_1: List = couple.pop().list_parameters()
    parent_2: List = couple.pop().list_parameters()
    child_params = parent_1
    for j in range(i, len(parent_2)):
        child_params[j] = parent_2[j]
    child: Villager = Villager.from_list(child_params)
    return child


def merge_population(population: List):
    global N_KEEP

    population.sort(key=lambda x: x.reward/x.nb_simu if x.nb_simu != 0 else 0, reverse=True)
    new_population = []

    # Keep best candidates
    for i in range(N_KEEP):
        new_population.append(population[i])

    # Merge them to get possibly good children
    for couple in combine_parents(new_population, n_couples=len(population) - N_KEEP):
        new_child = cross_over(couple)
        new_population.append(new_child)

    # Not enough children, complete with more previous generation villagers
    while len(new_population) < len(population):
        new_population.append(population[N_KEEP])
        N_KEEP += 1

    return new_population


def main():
    p = ["minimax", "mcts"]

    converged = False
    population = init_population()

    k = 0
    while not converged:
        threads: List[threading.Thread] = []
        print("New generation. Pop size :", len(population))
        for villager in population:
            t = threading.Thread(target=evaluate_villager, args=(p, villager,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        population = evolve_population(population)

        print(str(k) + "'th generation over")
        k += 1
        if k == 3:
            converged = True  # TODO : change
    population.sort(key=lambda x: x.reward/x.nb_simu if x.nb_simu != 0 else 0, reverse=True)
    print("Best candidate :", population[0])


def evaluate_villager(p, villager):
    for i in range(NB_GAMES):
        print("Evaluating villager with", villager.it, "iteration count. Round", i)
        villager.reward += play_game(p, villager.list_parameters())
        villager.nb_simu += 1


if __name__ == '__main__':
    print("Started optimization procedure at", time.ctime())
    main()
