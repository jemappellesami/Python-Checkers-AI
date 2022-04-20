import pygame
from .constants import RED, WHITE, BLUE, SQUARE_SIZE, ROWS, COLS
from checkers.board import Board
from .move import Move
import time



class Game:
    def __init__(self, win=None, benchmark=False, parameters=[8, 3, 1]):
        heuristic_weights, max_it = parameters[1:], parameters[0]
        self._parameters_init(max_it, heuristic_weights)
        self._init()
        self.display = win
        self.king_moved = 0

    def _parameters_init(self, max_it, heuristic_weights):
        # first, default weights (to make sure the attribute is instanciated)
        self.heuristic_weights = (1,1)
        self.max_it = max_it
        # Currently : 2 heuristics, so check that the heuristic_weights attribute is of length 2
        if len(heuristic_weights) != 2 :
            print("There is an error with the weights of the heuristics")
        else :
            self.heuristic_weights = heuristic_weights

    def update(self):
        self.board.draw(self.display)
        self.draw_valid_moves(self.valid_moves)
        pygame.display.update()

    def update_log(self, move, move_time, ai_type, count_red, count_white):
        color = 0 if self.turn == WHITE else 1
        log_file = open(self.log_file_name, "a")
        log_file.write(
            "{}; {}; {}; {}; {}; {}; {}; {}\n".format(int(self.num_turn), color, ai_type, move, len(move.skip), move_time, count_red, count_white)
        )
        log_file.close()

    def update_log_winner(self, winner):
        log_file = open(self.log_file_name, "a")
        log_file.write(
            "Winner : {}\n".format("White" if winner == WHITE else "Red")
        )
        log_file.close()

    def _init(self):
        self.selected = None
        self.board = Board(self.heuristic_weights)
        self.turn = WHITE
        self.num_turn = 1
        self.valid_moves = {}

        # Log file management
        self._init_log()

    def _init_log(self):
        self.log_file_name = "heuristic_stats/Fournée2/m{}_h1_{}_h2_{}_{}.csv".format(self.max_it, self.heuristic_weights[0], self.heuristic_weights[1], time.time())
        log_file = open(self.log_file_name, "w")
        log_file.write("Turn; Color; AI; Move; Skip; Time; Num. Reds; Num. Whites \n")
        log_file.close()

    def winner(self):
        if self.king_moved >= 20:
            return "BOTH"
        return self.board.winner()

    def reset(self):
        self._init()

    def select(self, row, col):
        if self.selected:
            # il faut que ça soit selected pour pouvoir faire move
            result = self._move(row, col)
            # il faut que le move soit accepté pour qu'il se passe quelque chose, sinon on annule le move et on recommence
            if not result:
                self.selected = None
                self.select(row, col)

        piece = self.board.get_piece(row, col)
        # Piece vaut 0 si la case n'est pas occupée, (255,0,0) si c'est rouge, et (255,255,255) si c'est blanc

        if piece != 0 and piece.color == self.turn:
            self.selected = piece
            self.valid_moves = self.board.get_valid_moves(piece)
            return True

        return False

    def _move(self, row, col):
        piece = self.board.get_piece(row, col)  # La place à occuper ensuite.
        if self.selected and piece == 0 and (row, col) in self.valid_moves:
            self.board.move(self.selected, row,
                            col)  # A ce moment là, on bouge une pièce, il faut regarder si c'est un king ou pas.
            if self.selected.king:
                # Il faut compter chaque fois qu'une dame bouge.
                print("Une dame a été jouée")
                self.king_moved += 1
            else:
                print("Ce n'est pas une dame qui a joué")
                self.king_moved = 0
            skipped = self.valid_moves[(row, col)]
            if skipped:
                self.board.remove(skipped)
            self.change_turn()
        else:
            return False

        return True

    def draw_valid_moves(self, moves):
        for move in moves:
            row, col = move
            pygame.draw.circle(self.display, BLUE,
                               (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2), 15)

    def change_turn(self):
        self.valid_moves = {}
        if self.turn == RED:
            self.turn = WHITE
        else:
            self.turn = RED

    def get_board(self) -> Board:
        return self.board

    def ai_move(self, board, parent_action: Move):
        # Change here the counting of king_moved
        self.analyze_move(parent_action)
        self.board = board
        self.change_turn()
        self.num_turn += 0.5

    def analyze_move(self, move: Move):
        # Need to check if this was a king move and if there was a capture.
        piece_moved = move.get_piece()
        if piece_moved.is_king():
            self.king_moved += 1
            # If no capture, we do nothing. If capture, count is back to zero.
            if move.get_skip() is not None and len(move.get_skip()) != 0:
                self.king_moved = 0
        else:
            self.king_moved = 0
