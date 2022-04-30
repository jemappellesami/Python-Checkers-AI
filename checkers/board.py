from copy import deepcopy

import pygame
from typing import List

from .constants import BLACK, ROWS, RED, SQUARE_SIZE, COLS, WHITE
from .piece import Piece


class Board:
    safe_heuri_weight = 1

    def __init__(self):
        self.board = []
        self.red_left = self.white_left = 12
        self.red_kings = self.white_kings = 0
        self.create_board()

    def set_heuri_weights(heuri_weights):
        Board.safe_heuri_weight = heuri_weights

    def draw_squares(self, win):
        win.fill(BLACK)
        for row in range(ROWS):
            for col in range(row % 2, COLS, 2):
                pygame.draw.rect(win, RED, (row * SQUARE_SIZE, col * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def evaluate(self):
        return self.white_left - self.red_left + (self.white_kings * 0.5 - self.red_kings * 0.5)

    def get_all_pieces(self, color) -> List[Piece]:
        """

        :param color:
        :return: All "piece" objects of the board.
        """
        pieces = []
        for row in self.board:
            for piece in row:
                if piece != 0 and piece.color == color:
                    pieces.append(piece)
        return pieces

    def move(self, piece, row, col):
        self.board[piece.row][piece.col], self.board[row][col] = self.board[row][col], self.board[piece.row][piece.col]
        piece.move(row, col)

        if row == ROWS - 1 or row == 0:
            piece.make_king()
            if piece.color == WHITE:
                self.white_kings += 1
            else:
                self.red_kings += 1

    def get_piece(self, row, col):
        return self.board[row][col]

    def create_board(self):
        for row in range(ROWS):
            self.board.append([])
            for col in range(COLS):
                if col % 2 == ((row + 1) % 2):
                    if row < 3:
                        self.board[row].append(Piece(row, col, WHITE))
                    elif row > 4:
                        self.board[row].append(Piece(row, col, RED))
                    else:
                        self.board[row].append(0)
                else:
                    self.board[row].append(0)

    def draw(self, win):
        self.draw_squares(win)
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece != 0:
                    piece.draw(win)

    def remove(self, pieces):
        for piece in pieces:
            self.board[piece.row][piece.col] = 0
            if piece != 0:
                if piece.color == RED:
                    self.red_left -= 1
                else:
                    self.white_left -= 1

    def winner(self):
        """
        Proposition de correction : la partie se termine quand l'un des deux n'a plus de pièce OU plus de moves possible
        :return:
        """
        self.red_left, self.white_left = self.get_num()
        if self.red_left <= 0:
            # Il n'y a plus de rouge sur le board.
            return WHITE
        elif self.white_left <= 0:
            # Il n'y a plus de blanc sur le board.
            return RED
        return None

    def eval_number(self, color, is_king):
        """
        Evaluates the current board for the given color by accounting for that color's number of pieces
        :param color: color on which we focus
        :param is_king: true if the type of the piece is king
        :return: the value of the board for the given color
        """
        res = list(map(lambda x: x.king == is_king, self.get_all_pieces(color))).count(True)

        return res

    def eval_edge(self, color, is_king):
        """
        Evaluates the current board for the given color by accounting for that color's edge pieces
        :param color: color on which we focus
        :param is_king: true if the type of the piece is king
        :return: the value of the board for the given color
        """
        res = list(map(lambda x: x.king == is_king
                                 and (x.row in [0, 7] or x.col in [0, 7]), self.get_all_pieces(color))).count(True)

        return res

    def eval_movable(self, color, is_king):
        """
        Evaluates the current board for the given color by accounting for that color's movable pawns
        (=pawns able to perform a move)
        :param color: color on which we focus
        :param is_king: true if the type of the piece is king
        :return: the value of the board for the given color
        """
        res = sum(list(map(lambda x: x.king == is_king
                                    and len(self.get_valid_moves(x)[1].keys()) > 0, self.get_all_pieces(color))))

        return res

    def eval_promotion_distance(self, color):
        """
        Evaluates the current board for the given color by accounting for that color's pawns' aggregate distance to the
        promotion line
        :param color: color on which we focus
        :return: the value of the board for the given color
        """
        res = 0

        if color == WHITE:
            res = sum(list(map(lambda x: 7 - x.row, [x for x in self.get_all_pieces(color) if not x.king])))
        else:
            res = sum(list(map(lambda x: x.row, [x for x in self.get_all_pieces(color) if not x.king])))

        # FIXME: should we use average or sum?
        # sum: gets lower as we promote pawns (but also gets lower as we *lose* pawns)
        # average: can get higher if we promote pawns to kings

        return res

    def eval_promotion_fields(self, color):
        """
        Evaluates the current board for the given color by accounting for that color's unoccupied promotion fields
        (= 4 fields at the end of a board opposite the color's initial position)
        :param color: color on which we focus
        :return: the value of the board for the given color
        """
        res = 0

        if color == WHITE:
            promotion_fields = [(7, 0), (7, 2), (7, 4), (7, 6)]
        else:
            promotion_fields = [(0, 1), (0, 3), (0, 5), (0, 7)]

        for x, y in promotion_fields:
            if self.get_piece(x, y) == 0:
                res += 1

        return res

    def eval_defender_pieces(self, color):
        """
        Evaluates the current board for the given color by accounting for that color's defender pieces
        (=pieces situated in two lowermost rows)
        :param color: color on which we focus
        :return: the value of the board for the given color
        """

        if color == WHITE:
            defender_rows = list(range(2))
        else:
            defender_rows = list(range(6, 8))

        res = sum(list(map(lambda x: x.row in defender_rows, self.get_all_pieces(color))))

        return res

    def eval_attacking_pawns(self, color):
        """
        Evaluates the current board for the given color by accounting for that color's attacking pawns
        (=pawns positioned in the three topmost rows)
        :param color: color on which we focus
        :return: the value of the board for the given color
        """

        if color == WHITE:
            attacking_rows = list(range(5, 8))
        else:
            attacking_rows = list(range(3))

        res = sum(list(map(lambda x: x.row in attacking_rows, [x for x in self.get_all_pieces(color) if not x.king])))

        return res

    def eval_central(self, color, is_king):
        """
        Evaluates the current board for the given color by accounting for that color's central pieces
        (=pawns positioned in the three topmost rows)
        :param color: color on which we focus
        :param is_king: true if the type of the piece is king
        :return: the value of the board for the given color
        """

        central_rows = list(range(3, 5))

        res = sum(list(map(lambda x: x.row in central_rows,
                           [x for x in self.get_all_pieces(color) if x.king == is_king])))

        return res

    def eval_piece_row_value(self, color):
        """
        Evaluates the current board for the given color following the "Piece & Row to value" method.
        Pawn’s value = 5 + row number
        King’s value = 5 + # of rows + 2
        :param color: color on which we focus
        :return: the value of the board for the given color
        """
        res = 0
        num_of_rows = 8
        row_no = 0

        for piece in self.get_all_pieces(color):
            if color == RED:
                row_no = (8 - piece.row)
            elif color == WHITE:
                row_no = piece.row

            res += 5 + row_no if not piece.king else 5 + num_of_rows + 2
        return res

    def test_heuristics(self):
        for color in [RED, WHITE]:
            color_string = "RED" if color == RED else "WHITE"
            print(color_string)
            for cond in [True, False]:
                type_string = "kings" if cond else "pawns"
                # print("eval_number_{}".format(type_string), self.eval_number(color, cond))
                # print("eval_edge_{}".format(type_string), self.eval_edge(color, cond))
                # print("eval_movable_{}".format(type_string), self.eval_movable(color, cond))
                # print("eval_central_{}".format(type_string), self.eval_central(color, cond))
            # print("eval_promotion_distance", self.eval_promotion_distance(color))
            # print("eval_promotion_fields", self.eval_promotion_fields(color))
            # print("eval_defender_pieces", self.eval_defender_pieces(color))
            # print("eval_attacking_pawns", self.eval_attacking_pawns(color))

    def eval(self, color):
        return self.eval_piece_row_value(color) \
               + (self.eval_edge(color, True) + self.eval_edge(color, False)) * self.safe_heuri_weight

    def get_valid_moves(self, piece):
        moves = {}
        left = piece.col - 1
        right = piece.col + 1
        row = piece.row

        if piece.color == RED or piece.king:
            moves.update(self._traverse_left(row - 1, max(row - 3, -1), -1, piece.color, left))
            moves.update(self._traverse_right(row - 1, max(row - 3, -1), -1, piece.color, right))
        if piece.color == WHITE or piece.king:
            moves.update(self._traverse_left(row + 1, min(row + 3, ROWS), 1, piece.color, left))
            moves.update(self._traverse_right(row + 1, min(row + 3, ROWS), 1, piece.color, right))

        # Modification : return the valid moves for the current piece, to keep track of this information
        return piece, moves

    def _traverse_left(self, start, stop, step, color, left, skipped=None):
        if skipped is None:
            skipped = []
        moves = {}
        last = []
        for r in range(start, stop, step):
            if left < 0:
                break

            current = self.board[r][left]
            if current == 0:
                if skipped and not last:
                    break
                elif skipped:
                    moves[(r, left)] = last + skipped
                else:
                    moves[(r, left)] = last

                if last:
                    if step == -1:
                        row = max(r - 3, 0)
                    else:
                        row = min(r + 3, ROWS)
                    moves.update(self._traverse_left(r + step, row, step, color, left - 1, skipped=last))
                    moves.update(self._traverse_right(r + step, row, step, color, left + 1, skipped=last))
                break
            elif current.color == color:
                break
            else:
                last = [current]

            left -= 1

        return moves

    def _traverse_right(self, start, stop, step, color, right, skipped=[]):
        moves = {}
        last = []
        for r in range(start, stop, step):
            if right >= COLS:
                break

            current = self.board[r][right]
            if current == 0:
                if skipped and not last:
                    break
                elif skipped:
                    moves[(r, right)] = last + skipped
                else:
                    moves[(r, right)] = last

                if last:
                    if step == -1:
                        row = max(r - 3, 0)
                    else:
                        row = min(r + 3, ROWS)
                    moves.update(self._traverse_left(r + step, row, step, color, right - 1, skipped=last))
                    moves.update(self._traverse_right(r + step, row, step, color, right + 1, skipped=last))
                break
            elif current.color == color:
                break
            else:
                last = [current]

            right += 1

        return moves

    def get_num(self):
        num_whites = len(self.get_all_pieces(WHITE))
        num_reds = len(self.get_all_pieces(RED))
        return num_reds, num_whites

    def get_all_moves(self, color):
        moves = []

        for piece in self.get_all_pieces(color):
            valid_moves = self.get_valid_moves(piece)[1]
            for move, skip in valid_moves.items():
                temp_board = deepcopy(self)
                temp_piece = temp_board.get_piece(piece.row, piece.col)
                new_board = temp_board.simulate_move(temp_piece, move, skip)
                moves.append(new_board)
        return moves

    def simulate_move(self, piece, move, skip):
        self.move(piece, move[0], move[1])
        if skip:
            self.remove(skip)

        return self
