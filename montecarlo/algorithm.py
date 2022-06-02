import copy
import math
import random
from collections import defaultdict
from copy import deepcopy

import pickle

from typing import List

from checkers.move import Move
from checkers.board import Board

RED = (255, 0, 0)
WHITE = (255, 255, 255)


def montecarlots(board, player, game, tree=None, first=False, max_it=5000):
    """
    Proceeds a Monte Carlo tree search on the given board, considering that it's given player's turn.
    A possible precomputed search tree can be given to allow deeper computations
    :param board: Board to evaluate the best move on
    :param player: Player who has to make a move
    :param game: Current game
    :param tree: Optional precomputed tree where root should be the current state of the game
    :param max_it: Maximum number of mcts iteration allowed
    :return: Board after best move, node after best move (the future root), move to go from current to chosen board
    """
    nb_king_moved = game.king_moved
    if first:
        # print("loaded pickle file")
        tree = pickle.load(open("montecarlo/tree.p", "rb"))
    if not tree:
        # New tree
        tree = MCNode(board, player, nb_king_moved, max_it)
    chosen_node = tree.monte_carlo_tree_search()
    if chosen_node is None:
        return None, None, None
    chosen_node_board = chosen_node.board
    return chosen_node_board, chosen_node, chosen_node.parent_action


class MCNode:
    # p = 1 was the best parameter (won 2 games over 10)
    exploit_param = 1

    def __init__(self, board: Board, color, nb_king_moved, max_it, parent=None, previous_move: Move = None):
        """
        Class that models a node as manipulated in an MCTS
        :param board:   Current board
        :param color:   Current player color
        :param parent:  Parent node, if any (none by default, for root)
        :param previous_move:   Move to go from parent board to self.board
        """
        self.board: Board = board
        self.color = color
        self.adv_color = WHITE if self.color == RED else RED
        self.reward = 0.0
        self.visits = 1  # We always visit newly created node
        self.parent = parent
        self.parent_action = previous_move
        self.children: List[MCNode] = []
        self.children_moves = []
        self.remaining_moves = self.get_all_moves()
        self.num_possible_moves = len(self.remaining_moves)
        self.max_it = max_it
        self.nb_king_moved = nb_king_moved
        return

    @staticmethod
    def set_exploit(exploit):
        MCNode.exploit_param = exploit

    def monte_carlo_tree_search(self):
        for i in range(self.max_it):
            last_node = self.select()  # Select + expand if needed
            reward = self.simulate(last_node)
            self.backpropagate(reward, last_node)
            # print(self.as_string())
            # input()  # DEBUG
        if self.is_terminal_node():
            return self
        return self.best_child()

    def select(self):
        """
        This function defines the selection policy. If the current node is still not fully explored,
        it expands the node and selects the newly created child. If the node is fully explored, we
        move down in the tree, selecting the best child until the node is terminal or not fully explored
        :return: The selected node according to the policy.
        """
        current_node = self
        while not current_node.is_terminal_node():
            if not current_node.fully_explored():
                return current_node.expand()
            else:
                current_node = current_node.best_child()
        return current_node

    def expand(self):
        """
        Expansion of the current node. We try to create a child node by chosing a move that has not been chosen before
        for this node.
        :return: The newly created node
        """
        move = random.choice(self.remaining_moves)
        self.remaining_moves.remove(move)
        piece = move.get_piece()
        final_loc = move.get_loc()
        skip = move.get_skip()
        # Copy of the board, to avoid simulation from influencing the board
        new_board = deepcopy(self.board)
        # Need to make a deep copy of piece to avoid simulation from influencing the board
        temp_piece = new_board.get_piece(piece.row, piece.col)
        if temp_piece == 0:
            print("Error, got a non existing piece from possible moves")
            # print(piece, 'with move', move)
            # print(temp_piece)
            input("[enter]")

        new_state = new_board.simulate_move(temp_piece, final_loc, skip)
        # See definition of the function.
        self.add_child(new_state, move)

        return self.children[-1]

    def best_child(self):
        """
        Returns the best child of self based on a scoring system combining exploration and exploitation
        :return:
        """
        best_score = -float("inf")
        best_children = []

        for c in self.children:
            exploitation = c.reward / c.visits
            exploration = math.sqrt(math.log2(c.visits) / c.visits)
            score = exploration + exploitation * self.exploit_param/100
            # division by 100 because of the benchmark (on peut pas mettre de décimale pour le nom des tables alors bref)
            if score == best_score:
                best_children.append(c)
            elif score > best_score:
                best_children = [c]
                best_score = score

        return random.choice(best_children)

    def is_terminal_node(self):
        """
        Function that tests if a node is terminal. By definition, a node is terminal when there are no possible moves.

        :return: Boolean
        """
        return self.num_possible_moves == 0

    def fully_explored(self) -> bool:
        """
        Returns a boolean value telling whether the node has been fully explored or not. A node is fully explored when
        all his possible moves are in his children

        :return: True if node is fully explored, False otherwise
        """
        return self.num_possible_moves == len(self.children_moves)

    def get_all_moves(self) -> List[Move]:
        """
        Function that returns all the possible out coming boards from the current position when it is the turn of
        player "color"

        :return: List of Moves corresponding to possible outcomes
        """
        moves = []
        for piece in self.board.get_all_pieces(self.color):
            valid_moves = self.board.get_valid_moves(piece)[1]  # index 0 is the piece itself
            if len(valid_moves) != 0:
                for final_dest, skip in valid_moves.items():
                    move = Move(self.board, self.color, piece, final_dest, skip)
                    moves.append(move)
        return moves

    def add_child(self, state: Board, move: Move):
        """
        Function that modifies the current node by adding a new child node, and adding a move to his list of moves

        :param state:   Current board
        :param move:    move to add
        :return:        None
        """
        self.analyze_move(move)
        child_node = MCNode(state,
                            parent=self,
                            color=self.adv_color,
                            nb_king_moved=self.nb_king_moved,
                            previous_move=move,
                            max_it=self.max_it)
        self.children.append(child_node)
        self.children_moves.append(move)

    def find_child(self, state: Board):
        for child in self.children:
            if child.board == state:
                return child

    def not_in_children_moves(self, move: Move) -> bool:
        for child_move in self.children_moves:
            if child_move.is_equivalent_to(move):
                return False
        return True

    @staticmethod
    def choose_best_moves(moves, number=3) -> List[Move]:
        """
        Chooses the best moves in a list of moves. Default : chooses 3 best moves.
        Returns all the moves if less than 3 moves in the list

        :param moves: list of possible moves
        :param number: number of best moves to keep
        :return: List of the *number* best moves in the *moves* list
        """

        for move in moves:
            move.compute_value()

        if len(moves) <= number:
            return moves

        # Sorts the moves list in increasing order, keeps the *number* first ones
        best_moves = sorted(moves, key=lambda m: m.value, reverse=False)[:number]
        return best_moves

    def simulate(self, last_expanded_node) -> int:
        """
        Simulate the execution of a game until reaching a final position by playing heuristic based moves

        :param last_expanded_node: Initial MCNode for the simulation.
        :return: Reward value (0 or 1)
        """
        simulation_child = MCNode(board=deepcopy(last_expanded_node.board),
                                  color=last_expanded_node.color,
                                  nb_king_moved=last_expanded_node.nb_king_moved,
                                  max_it=last_expanded_node.max_it)
        simulation_board: Board = simulation_child.board  # To avoid working on existing new_state
        possible_moves = simulation_child.remaining_moves

        while not len(possible_moves) == 0 and self.nb_king_moved < 20:
            # Use of the heuristic
            # best_moves = self.choose_best_moves(possible_moves)
            rand_move = random.choice(possible_moves)
            col, row = rand_move.get_loc()
            skip = rand_move.skip
            simulation_board = simulation_board.simulate_move(rand_move.piece, (col, row), skip)

            self.analyze_move(rand_move)
            new_color = RED if last_expanded_node.color == WHITE else WHITE
            simulation_child = MCNode(board=simulation_board,
                                      color=new_color,
                                      nb_king_moved=self.nb_king_moved,
                                      previous_move=rand_move,
                                      max_it=self.max_it)
            possible_moves = simulation_child.remaining_moves


        return self.winner(simulation_child)

    def backpropagate(self, reward, node):
        """
        Back-propagate the results from simulated game up to root by alterning the reward between 0 and 1.

        :param reward: The reward seen from the last node
        :param node: Current node to update
        """
        if node.parent is None:
            # We got to the root.
            return

        # +=1 visits pour tout et +reward aux nodes avec la couleur du node de départ, +(1-reward) aux autres.
        node.visits += 1  # Same for every node we visited
        if node.color == self.color:
            node.reward += reward
        else:
            node.reward += 1 - reward  # The reward is adapted according to the color of the node.

        self.backpropagate(reward, node.parent)

    def analyze_move(self, move: Move):
        """
        Updates the number of kings moved to see if this is the end of a game or not.

        :param move: Move that just has been made by the algorithm.
        """
        piece_moved = move.get_piece()
        if piece_moved.is_king():
            self.nb_king_moved += 1
            # If no capture, we do nothing. If capture, count is back to zero.
            if move.get_skip() is not None and len(move.get_skip()) != 0:
                self.nb_king_moved = 0
        else:
            self.nb_king_moved = 0

    def winner(self, final_node):
        """
        Function that returns the correct number of points based on the winner or if there is a tie.

        :param final_node: Child that we are working on at the moment.
        :return: Numeric value representing the score. 1 if the winner
        is new_child, 0 if the winner is the other player and 0.5 if it's a tie.
        """
        if self.nb_king_moved >= 20:
            # It's a tie
            return 0.5
        else:
            if final_node.board.winner() == final_node.color:
                return 1
            else:
                # Aussi quand on ne sait plus jouer
                return 0

    def as_string(self, level=0):
        ret = "\t" * level + str(self.reward) + "/" + str(self.visits) + "\n"
        for child in self.children:
            ret += child.as_string(level + 1)
        return ret
