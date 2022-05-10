import pygame
import sqlite3 # for logging
from montecarlo.algorithm import MCNode
from .constants import RED, WHITE, BLUE, SQUARE_SIZE, ROWS, COLS
from checkers.board import Board
from .move import Move
from SQLite.dbmanagement import create_connection, create_game_table, close_connection, insert_move
import time



class Game:
    def __init__(self, win=None, parameters=(8, 2, 1), logging=False):
        max_it = parameters[0]
        safe_heuri_weight = parameters[1]
        exploit_param = parameters[2]
        self._parameters_init(max_it, safe_heuri_weight, exploit_param)
        self._init(logging)
        self.display = win
        self.king_moved = 0

    def _parameters_init(self, max_it, safe_heuri_weight, exploit_param):
        # first, default weights (to make sure the attribute is instanciated)
        Board.set_heuri_weights(safe_heuri_weight)
        self.max_it = max_it
        MCNode.set_exploit(exploit_param)


    def update(self):
        self.board.draw(self.display)
        # self.board.test_heuristics()  # todo : is this supposed to be here?
        pygame.display.update()


    def human_update(self):
        self.board.draw(self.display)
        self.draw_valid_moves(self.valid_moves)
        pygame.display.update()

    def update_log(self, move, move_time, ai_type, count_red, count_white):
        if move is not None :
            color = "WHITE" if self.turn == WHITE else "RED"
            conn = create_connection("SQLite/Games.db")
            insert_move(table=self.table_name,
                        turn=int(self.num_turn),
                        color=color,
                        ai_type=ai_type,
                        origin_x=move.piece.row,
                        origin_y=move.piece.col,
                        final_x=move.loc[0],
                        final_y=move.loc[1],
                        skip=len(move.skip),
                        time=move_time,
                        count_red=count_red,
                        count_white=count_white,
                        conn=conn)
            close_connection(conn)

            # TODO : delete, normally its safe
            # log_file = open(self.log_file_name, "a")
            # log_file.write(
            #     "{}; {}; {}; {}; {}; {}; {}; {}\n".format(int(self.num_turn), color, ai_type, move, len(move.skip), move_time, count_red, count_white)
            # )
            # log_file.close()

    def update_log_winner(self, winner):
        conn = create_connection("SQLite/Games.db")
        insert_move(table=self.table_name,
                    turn=int(self.num_turn),
                    color=winner,
                    ai_type="END",
                    origin_x=-1,
                    origin_y=-1,
                    final_x=-1,
                    final_y=-1,
                    skip=-1,
                    time=-1,
                    count_red=-1,
                    count_white=-1,
                    conn=conn)
        close_connection(conn)

        # TODO : delete, normally its safe
        # log_file = open(self.log_file_name, "a")
        # log_file.write(
        #     "Winner : {}\n".format("White" if winner == WHITE else "Red")
        # )
        # log_file.close()

    def _init(self, logging):
        self.selected = None
        self.board = Board()
        self.turn = WHITE
        self.num_turn = 1
        self.valid_moves = {}

        # Log file management
        if logging:
            self._init_log()

    def _init_log(self):
        self.table_name = "m{}_h{}_t{}".format(self.max_it, MCNode.exploit_param, int(time.time()))
        # self.table_name = "test"
        conn = create_connection("SQLite/Games.db")
        create_game_table(self.table_name, conn)
        close_connection(conn)

        # TODO : delete, normally its safe
        #self.log_file_name = "heuristic_stats/NoHeuristicsAcc/m{}_h{}_{}_NOHEURISTICS.csv".format(self.max_it, MCNode.exploit_param, time.time())
        #log_file = open(self.log_file_name, "w")
        #log_file.write("Turn; Color; AI; Move; Skip; Time; Num. Reds; Num. Whites \n")
        #log_file.close()

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
            # print("set the valid moves", self.valid_moves)
            return True

        return False

    def _move(self, row, col):
        piece = self.board.get_piece(row, col)  # La place à occuper ensuite.
        valid_moves = self.valid_moves[1]
        if self.selected and piece == 0 and (row, col) in valid_moves:
            self.board.move(self.selected, row,
                            col)  # A ce moment là, on bouge une pièce, il faut regarder si c'est un king ou pas.
            if self.selected.king:
                # Il faut compter chaque fois qu'une dame bouge.
                # print("Une dame a été jouée")
                self.king_moved += 1
            else:
                # print("Ce n'est pas une dame qui a joué")
                self.king_moved = 0
            skipped = valid_moves[(row, col)]
            if skipped:
                self.board.remove(skipped)
            self.change_turn()
            self.selected = None
        else:
            return False

        return True

    def draw_valid_moves(self, moves):
        moves = moves[1]
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
        if move is not None :
            piece_moved = move.get_piece()
            if piece_moved.is_king():
                # print("Dame jouée")  # DEBUG
                self.king_moved += 1
                # If no capture, we do nothing. If capture, count is back to zero.
                if move.get_skip() is not None and len(move.get_skip()) != 0:
                    # print("Capture!")  # DEBUG
                    self.king_moved = 0
            else:
                # print("Pion joué")  # DEBUG
                self.king_moved = 0
