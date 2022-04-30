# Let's gooooo
from typing import List

from checkers.board import Board
from checkers.constants import RED, WHITE
import random

from checkers.game import Game
from main import make_ai_move
from montecarlo.algorithm import MCNode

FPS = 60
random.seed(15)
POP_SIZE = 4
NB_PARENTS_TO_KEEP = 3
NB_CHILDREN = 3
NB_GAMES = 2


class Villager:
    def __init__(self, it, safe_heuri, exploit, reward=None):
        self.it = it
        self.safe_heuri = safe_heuri
        self.exploit_param = exploit
        self.reward = reward


def init_population() -> List[Villager]:
    population = []
    for i in range(POP_SIZE):
        it = random.randint(5, 40)
        safe_heuri = random.uniform(0, 1)
        exploit = random.uniform(0, 1)
        population.append(Villager(it, safe_heuri, exploit))
        print("Villageois ajouté")
    return population


def make_move(game, p, run, tree):
    """
    Executes a move on the board determined by the arguments chosen at game launch.
    """
    #print("Ready to make a move")
    n = -1
    if game.turn == WHITE:
        n = 0
    elif game.turn == RED:
        n = 1
    else:
        print("Error : game.turn is neither WHITE nor RED")

    run, tree = make_ai_move(game, n, p, run, tree)
    return run, tree


def play_game(p) -> float:
    """
    Play a game and return the reward of the game seen from the mcts view
    :param p: players setup
    :return: float reward value seen from mcts
    """
    game = Game()
    winner = 0
    most_recent_tree = None
    running = True

    while running:
        running, most_recent_tree = make_move(game, p, running, most_recent_tree)

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


def set_parameters(iterations, safe_heuristic, exploitation):
    Board.set_safe_heuri_param(safe_heuristic)
    MCNode.set_exploit(exploitation)
    MCNode.set_max_it(iterations)


def main():
    p = ["minimax", "mcts"]

    optimal = False
    population = init_population()
    j = 0
    while not optimal:
        for villager in population:
            set_parameters(villager.it, villager.safe_heuri, villager.exploit_param)
            reward = 0
            print("Prêt à jouer")
            for i in range(NB_GAMES):
                print("Jeu commencé")
                j += 1
                reward += play_game(p)
                print(j, "'th game is over")
            villager.reward = reward
        population.sort(key=lambda x: x.reward, reverse=True)
        best_parents = select(population)
        children = crossOver(best_parents)
        # TODO: select x% of best villagers and fuse them
        population = children
        print("Les enfants ont été générés, on commence avec eux")

def select(population) ->List[Villager]:
    # On garde les nb_parents qui sont les meilleurs.
    new_population = []
    print(len(population))
    if NB_PARENTS_TO_KEEP>=len(population):
        print("You want to keep too much parents, please change the parameter 'NB_PARENTS_TO_KEEP'")
        return population
    for i in range(NB_PARENTS_TO_KEEP):
        new_population[i] = population[i]
    return new_population

def crossOver(parents: List[Villager]) -> List[Villager]:
    if NB_CHILDREN%2 == 1:
        impair = True
        nb_children = NB_CHILDREN+1
    else:
        impair = False
        nb_children = NB_CHILDREN
    children = []
    for i in range(int(nb_children/2)):
        # First pick two parents in the list
        parent1 = random.choice(parents)
        parent2 = random.choice(parents)
        # Now we need to choose which parameter to keep from the first and the second parent.
        # TODO : randomisé la partie qui choisit quel paramètre on garde chez quel parent
        child1 = Villager(parent1.it, parent1.safe_heuri, parent2.exploit_param)
        child2 = Villager(parent2.it, parent2.safe_heuri, parent2.exploit_param)
        children.append(child1)
        children.append(child2)
    if impair:
        del children[0]
    return children

if __name__ == '__main__':
    main()
