from copy import deepcopy

import pygame

from board import Board, LMB, RMB

WHITE, BLACK = 0, 1
WHITE_CELL_COLOR, BLACK_CELL_COLOR = pygame.Color('#FAE0C7'), pygame.Color('#BF7E44')
PIECES_PATH = 'data/images/pieces/'
CHESS_HORIZONTAL_LETTERS = 'ABCDEFGH'


class HistoryObject:
    def __init__(self, old, new, color):
        self.old = old
        self.new = new
        self.color = color


def correct_coords(row, col):
    """Функция проверяет, что координаты (row, col) лежат
    внутри доски"""
    return 0 <= row < 8 and 0 <= col < 8


def get_row_letter(row, is_flipped=False):
    if is_flipped:
        return str(row + 1)

    return str(8 - row)


def get_col_letter(col, is_flipped=False):
    if is_flipped:
        col = 7 - col

    return CHESS_HORIZONTAL_LETTERS[col]


def to_chess_notation(pos, is_flipped=False):
    row, col = pos
    return get_row_letter(row, is_flipped) + get_col_letter(col, is_flipped)


def opponent(color):
    """Удобная функция для вычисления цвета противника"""
    if color == WHITE:
        return BLACK
    else:
        return WHITE


def is_free_cell(cell, board, color):
    c, r = cell
    fig = board.get_piece(r, c)
    if fig is not None:
        if fig.get_color() == color:
            return False
    return True


def get_piece_img(piece, color=None):
    if piece is None:
        return None

    path = PIECES_PATH

    if color is None:
        color = piece.get_color()

    if color == BLACK:
        path += 'black'
    else:
        path += 'white'

    img = None

    if isinstance(piece, Pawn):
        img = pygame.image.load(f'{path}/pawn.png')
    elif isinstance(piece, Rook):
        img = pygame.image.load(f'{path}/rook.png')
    elif isinstance(piece, Knight):
        img = pygame.image.load(f'{path}/knight.png')
    elif isinstance(piece, Bishop):
        img = pygame.image.load(f'{path}/bishop.png')
    elif isinstance(piece, Queen):
        img = pygame.image.load(f'{path}/queen.png')
    elif isinstance(piece, King):
        img = pygame.image.load(f'{path}/king.png')

    return img


def draw_chess(rect, pos, sender):
    x, y, w, h = rect
    c, r = pos
    cell = sender.get_value(pos)

    out_surface = pygame.Surface((w, h))

    color = BLACK_CELL_COLOR if ((r + c) % 2) else WHITE_CELL_COLOR
    out_surface.fill(color)

    if cell is not None:
        img = get_piece_img(cell)
        if img is not None:
            img = img.convert_alpha()
            img = pygame.transform.smoothscale(img, (w, h))
            out_surface.blit(img, (0, 0))

    if sender.is_cell_selected((c, r)):
        pygame.draw.rect(out_surface, pygame.Color('red'), (1, 1, w - 2, h - 2), 3)

    selected = sender.get_selected_cells()
    if selected:
        selected_figure = sender.get_value(selected[0])
        if selected_figure is not None:
            fpos = frow, fcell = selected_figure.get_pos(sender)
            if not sender.move_will_cause_check(frow, fcell, r, c):
                if selected_figure.can_move(sender, r, c):
                    pygame.draw.circle(out_surface, pygame.Color('#1a508b'), (w // 2, h // 2), min(w, h) // 8)
                    pygame.draw.circle(out_surface, pygame.Color('#1a508b'), (w // 2, h // 2), min(w, h) // 4, 6)
                elif isinstance(selected_figure, (King, Rook)):
                    if selected_figure.can_castle(sender, r, c):
                        pygame.draw.circle(out_surface, pygame.Color('#1a508b'), (w // 2, h // 2), min(w, h) // 8)
                        pygame.draw.circle(out_surface, pygame.Color('#1a508b'), (w // 2, h // 2), min(w, h) // 4, 6)
                if selected_figure.can_attack(sender, r, c):
                    pygame.draw.circle(out_surface, pygame.Color('red'), (w // 2, h // 2), min(w, h) // 8)
                    pygame.draw.circle(out_surface, pygame.Color('red'), (w // 2, h // 2), min(w, h) // 4, 6)

    return out_surface


class Figure:
    def __init__(self, color):
        self.color = color

    def color_str(self):
        color = 'WHITE' if self.get_color() == WHITE else 'BLACK'
        return color

    def get_color(self):
        return self.color

    def get_pos(self, board):
        for r in range(8):
            for c in range(8):
                if board.get_value((c, r)) is self:
                    return r, c

    def can_move(self, board, row1, col1):
        return False

    def can_attack(self, board, row1, col1):
        fig = board.get_value((col1, row1))
        is_opponent = fig is not None and fig.get_color() == opponent(self.get_color())
        return self.can_move(board, row1, col1) and is_opponent


class Castleable(Figure):
    def __init__(self, color):
        super().__init__(color)
        self.has_moved = False

    def check_if_moved(self):
        return self.has_moved

    def set_has_moved(self):
        self.has_moved = True

    def can_castle(self, board, row1, col1):
        if board.is_check():
            return False

        if not self.check_if_moved():
            new_fig = board.get_piece(row1, col1)
            if isinstance(new_fig, (Rook, King)) and not isinstance(new_fig, self.__class__):
                if new_fig.get_color() == self.get_color() and not new_fig.check_if_moved():
                    return True

        return False


class Rook(Castleable):
    def __init__(self, color):
        super().__init__(color)

    def __str__(self):
        color = self.color_str()
        return f'Rook({color})'

    def char(self):
        out = 'R'
        out += 'W' if self.get_color() == WHITE else 'B'
        out += 'M' if self.check_if_moved() else 'N'
        return out

    def raw_char(self):
        return self.char()[0]

    def can_move(self, board, row1, col1):
        row, col = self.get_pos(board)

        # Невозможно сделать ход в клетку, которая не лежит в том же ряду
        # или столбце клеток.
        if row != row1 and col != col1:
            return False
        elif row != row1:
            step = 1 if (row1 >= row) else -1
            for r in range(row + step, row1, step):
                # Если на пути по вертикали есть фигура
                if not (board.get_piece(r, col) is None):
                    return False
        elif col != col1:
            step = 1 if (col1 >= col) else -1
            for c in range(col + step, col1, step):
                # Если на пути по горизонтали есть фигура
                if not (board.get_piece(row, c) is None):
                    return False
        else:
            return False

        return is_free_cell((col1, row1), board, self.get_color())


class Pawn(Figure):
    def __init__(self, color):
        super().__init__(color)
        self.direction = 1 if color == WHITE else -1
        self.start_row = 1 if color == WHITE else 6
        self.end_row = 7 if color == WHITE else 0
        # Пешка может сделать из начального положения ход на 2 клетки
        # вперёд, поэтому поместим индекс начального ряда в start_row.

    def __str__(self):
        color = self.color_str()
        return f'Pawn({color})'

    def char(self):
        out = 'P'
        out += 'W' if self.get_color() == WHITE else 'B'
        return out

    def raw_char(self):
        return self.char()[0]

    def can_move(self, board, row1, col1):
        row, col = self.get_pos(board)
        # Пешка может ходить только по вертикали
        # "взятие на проходе" не реализовано
        if col != col1:
            return False

        # ход на 1 клетку
        if row + self.direction == row1 and col == col1:
            return board.get_piece(row1, col1) is None

        # ход на 2 клетки из начального положения
        if (row == self.start_row
                and row + 2 * self.direction == row1
                and board.get_piece(row + 2 * self.direction, col) is None and col == col1):
            return True

        return False

    def can_promote(self, board):
        row, _ = self.get_pos(board)
        return row == self.end_row

    def can_attack(self, board, row1, col1):
        row, col = self.get_pos(board)

        direction = 1 if (self.color == WHITE) else -1
        if row + direction == row1 and (col + 1 == col1 or col - 1 == col1):
            piece = board.get_piece(row1, col1)
            if isinstance(piece, (Pawn, Knight, Bishop, Rook, Queen)):
                cl = piece.get_color()
                return self.color != cl
        return False


class Knight(Figure):
    def __init__(self, color):
        super().__init__(color)
        self.color = color

    def __str__(self):
        color = self.color_str()
        return f'Knight({color})'

    def char(self):
        out = 'N'
        out += 'W' if self.get_color() == WHITE else 'B'
        return out

    def raw_char(self):
        return self.char()[0]

    def can_move(self, board, row1, col1):
        row, col = self.get_pos(board)

        if (not correct_coords(row, col)) or (row1 == row or col1 == col):
            return False
        else:
            coords_ok = (abs(row - row1) + abs(col - col1)) == 3
            is_free = is_free_cell((col1, row1), board, self.get_color())
            return coords_ok and is_free


class King(Castleable):
    def __init__(self, color):
        super().__init__(color)
        self.has_moved = False

    def __str__(self):
        color = self.color_str()
        return f'King({color})'

    def char(self):
        out = 'K'
        out += 'W' if self.get_color() == WHITE else 'B'
        out += 'M' if self.check_if_moved() else 'N'
        return out

    def raw_char(self):
        return self.char()[0]

    def can_move(self, board, row1, col1):
        row, col = self.get_pos(board)

        neighbours = board.get_neighbours((col, row))
        check_list = []
        for n in neighbours:
            c, r = n
            fig = board.get_piece(r, c)
            if fig is None or fig.get_color() == opponent(self.get_color()):
                check_list.append(n)

        return (col1, row1) in check_list


class Queen(Figure):
    def __init__(self, color):
        super().__init__(color)

    def __str__(self):
        color = self.color_str()
        return f'Queen({color})'

    def char(self):
        out = 'Q'
        out += 'W' if self.get_color() == WHITE else 'B'
        return out

    def raw_char(self):
        return self.char()[0]

    def can_move(self, board, row1, col1):
        row, col = self.get_pos(board)

        is_diag = abs(col1 - col) == abs(row1 - row)

        if (row1 != row) and (col1 != col) and is_diag:
            stepy = 1 if (row1 >= row) else -1
            stepx = 1 if (col1 >= col) else -1
            c, r = col + stepx, row + stepy

            while (r != row1) or (c != col1):
                # Если на пути по диагонали есть фигура
                if not (board.get_piece(r, c) is None):
                    return False
                r, c = r + stepy, c + stepx
        elif (row1 != row) and (col1 == col):
            step = 1 if (row1 >= row) else -1
            for r in range(row + step, row1, step):
                # Если на пути по вертикали есть фигура
                if not (board.get_piece(r, col) is None):
                    return False
        elif (col1 != col) and (row1 == row):
            step = 1 if (col1 >= col) else -1
            for c in range(col + step, col1, step):
                # Если на пути по горизонтали есть фигура
                if not (board.get_piece(row, c) is None):
                    return False
        else:
            return False

        return is_free_cell((col1, row1), board, self.get_color())


class Bishop(Figure):
    def __init__(self, color):
        super().__init__(color)

    def __str__(self):
        color = self.color_str()
        return f'Bishop({color})'

    def char(self):
        out = 'B'
        out += 'W' if self.get_color() == WHITE else 'B'
        return out

    def raw_char(self):
        return self.char()[0]

    def can_move(self, board, row1, col1):
        row, col = self.get_pos(board)

        is_diag = abs(col1 - col) == abs(row1 - row)

        if (row1 != row) and (col1 != col) and is_diag:
            stepy = 1 if (row1 >= row) else -1
            stepx = 1 if (col1 >= col) else -1
            c, r = col + stepx, row + stepy

            while ((r != row1) or (c != col1)) and (correct_coords(r, c)):
                # Если на пути по диагонали есть фигура
                if not (board.get_piece(r, c) is None):
                    return False
                r, c = r + stepy, c + stepx
        else:
            return False

        return is_free_cell((col1, row1), board, self.get_color())


PIECES_CHARS = {
    'Q': Queen,
    'K': King,
    'N': Knight,
    'B': Bishop,
    'R': Rook,
    'P': Pawn
}

COLOR_CHARS = {
    'W': WHITE,
    'B': BLACK
}


def read_board_from_file(filename, pieces_chars=None, color_chars=None, empty_char='-'):
    if pieces_chars is None:
        pieces_chars = PIECES_CHARS
    if color_chars is None:
        color_chars = COLOR_CHARS

    file = open(filename, 'r')
    lines = file.readlines()
    out = []

    move_char = lines[0][0]
    if move_char == 'B':
        curr_move = BLACK
    else:
        curr_move = WHITE

    for line in lines[1:9]:
        out.append([])
        ln = [x for x in line.split() if x]

        for cell in ln[:8]:
            if cell == empty_char:
                out[-1].append(None)
            else:
                cell = cell.upper()

                fig_char = cell[0]
                color_char = cell[1]

                piece_class = pieces_chars[fig_char]
                color = color_chars[color_char]

                piece = piece_class(color)

                if piece_class in (Rook, King):
                    if len(cell) > 2 and cell[2] == 'M':
                        piece.set_has_moved()

                out[-1].append(piece)

        while len(out[-1]) < 8:
            out[-1].append(None)

    file.close()

    while len(out) < 8:
        out.append([None for _ in range(8)])

    return out, curr_move


def write_board_to_file(filename, board, curr_move=WHITE, pieces_chars=None, color_chars=None, empty_char='-'):
    if pieces_chars is None:
        pieces_chars = PIECES_CHARS
    if color_chars is None:
        color_chars = COLOR_CHARS

    lines = ['B\n' if curr_move == BLACK else 'W\n']
    for line in board:
        line = [x.char() if isinstance(x, (Pawn, Bishop, Knight, Rook, Queen, King)) else empty_char for x in line]
        lines.append(' '.join(line) + '\n')

    file = open(filename, 'w')
    file.writelines(lines)
    file.close()


class ChessBoard(Board):
    def __init__(self, size, promotion_func):
        super().__init__(8, 8, board_size=size)

        self.board[0] = [
            Rook(WHITE), Knight(WHITE), Bishop(WHITE), King(WHITE),
            Queen(WHITE), Bishop(WHITE), Knight(WHITE), Rook(WHITE)
        ]
        self.board[1] = [
            Pawn(WHITE), Pawn(WHITE), Pawn(WHITE), Pawn(WHITE),
            Pawn(WHITE), Pawn(WHITE), Pawn(WHITE), Pawn(WHITE)
        ]
        self.board[6] = [
            Pawn(BLACK), Pawn(BLACK), Pawn(BLACK), Pawn(BLACK),
            Pawn(BLACK), Pawn(BLACK), Pawn(BLACK), Pawn(BLACK)
        ]
        self.board[7] = [
            Rook(BLACK), Knight(BLACK), Bishop(BLACK), King(BLACK),
            Queen(BLACK), Bishop(BLACK), Knight(BLACK), Rook(BLACK)
        ]

        self.color = WHITE

        self.promotion_func = promotion_func

        self.pieces_chars = PIECES_CHARS
        self.colors_chars = COLOR_CHARS

        self.starting_board = deepcopy(self.board)
        self.history = []
        self.history_pos = -1

    def reset(self):
        self.board = self.starting_board
        self.color = WHITE
        self.history = []
        self.history_pos = -1

    def set_board(self, board):
        for r, current_row in enumerate(board):
            for c, fig in enumerate(current_row):
                if isinstance(fig, (King, Queen, Knight, Rook, Pawn, Bishop)) or fig is None:
                    self.board[r][c] = fig
        self.history = []
        self.history_pos = -1

    def get_board(self):
        return self.board

    def set_color(self, color):
        if color not in [WHITE, BLACK]:
            raise ValueError('Illegal color value')
        self.color = color

    def read_from_file(self, filename, empty_char='-'):
        new_board, curr_move = read_board_from_file(filename, self.pieces_chars, self.colors_chars, empty_char)
        self.set_board(new_board)
        self.set_color(curr_move)

    def write_to_file(self, filename, empty_char='-'):
        write_board_to_file(filename, self.board, self.color, self.pieces_chars, self.colors_chars, empty_char)

    def current_player_color(self):
        return self.color

    def get_piece(self, row, col):
        if correct_coords(row, col):
            return self.board[row][col]
        else:
            return None

    def can_move_piece(self, row, col, row1, col1):
        """Проверить возможность перемещения
         фигуры из точки (row, col) в точку (row1, col1)"""

        if not correct_coords(row, col) or not correct_coords(row1, col1):
            return False
        if row == row1 and col == col1:
            return False  # нельзя пойти в ту же клетку

        piece = self.board[row][col]

        if piece is None:
            return False
        if piece.get_color() != self.color:
            return False
        if self.board[row1][col1] is None:
            if not piece.can_move(self, row1, col1):
                return False
        elif self.board[row1][col1].get_color() == opponent(piece.get_color()):
            if not piece.can_attack(self, row1, col1):
                return False
        else:
            return False

        return True

    def get_figures(self, color=None):
        out = []

        for row in self.board:
            for fig in row:
                if fig is not None:
                    if color is None or fig.get_color() == color:
                        out.append(fig)

        return out

    def get_figure_positions(self, color=None):
        if color is None:
            color = self.color

        return [x.get_pos(self) for x in self.get_figures(color)]

    def get_possible_moves(self, color=None):
        if color is None:
            color = self.color

        out = []

        positions = self.get_figure_positions(color)
        for row, col in positions:
            for r in range(8):
                for c in range(8):
                    if self.can_move_piece(row, col, r, c):
                        out.append((row, col, r, c))

        return out

    def get_king(self, color=None):
        if color is None:
            color = self.color

        kings = [x.get_pos(self) for x in self.get_figures(color) if isinstance(x, King)]
        if kings:
            return kings[-1]
        else:
            return None

    def is_check(self):
        if not self.get_king(self.color):
            # print('Warning: no king found!')
            return False

        opponent_figures = self.get_figures(opponent(self.color))
        king = self.get_king()

        for fig in opponent_figures:
            if fig.can_attack(self, *king):
                return True

        return False

    def move_will_cause_check(self, row, col, row1, col1):
        if not self.can_move_piece(row, col, row1, col1):
            return False

        piece1, piece2 = self.board[row][col], self.board[row1][col1]
        self.board[row][col] = None
        self.board[row1][col1] = piece1

        ch = self.is_check()

        self.board[row][col] = piece1
        self.board[row1][col1] = piece2

        return ch

    def moves_without_check(self, color=None):
        if color is None:
            color = self.color

        return [x for x in self.get_possible_moves(color) if not self.move_will_cause_check(*x)]

    def is_checkmate(self):
        return not self.moves_without_check(self.color)

    def can_castle(self, row, col, row1, col1):
        piece1 = self.board[row][col]
        piece2 = self.board[row1][col1]

        if piece1 is None or piece2 is None:
            return False
        elif not isinstance(piece1, (Rook, King)):
            return False
        elif not isinstance(piece2, (Rook, King)):
            return False
        else:
            p1 = piece1.can_castle(self, row1, col1)
            p2 = piece2.can_castle(self, row, col)
            return p1 and p2

    def promote(self, row, col, char):
        piece = self.board[row][col]

        if piece is None:
            return False
        elif not isinstance(piece, Pawn):
            return False
        elif not piece.can_promote(self):
            return False
        elif self.pieces_chars[char.upper()] == King:
            return False

        new_piece = self.pieces_chars.get(char.upper()[0], Pawn)
        self.board[row][col] = new_piece(self.color)
        return True

    def move_piece(self, row, col, row1, col1, autopromote=False):
        """Переместить фигуру из точки (row, col) в точку (row1, col1).
        Если перемещение возможно, метод выполнит его и вернёт True.
        Если нет --- вернёт False"""

        if self.is_checkmate():
            return None
        elif self.can_move_piece(row, col, row1, col1):
            piece = self.board[row][col]

            old = {
                (row, col): piece,
                (row1, col1): self.board[row1][col1]
            }

            self.board[row][col] = None  # Снять фигуру.
            self.board[row1][col1] = piece  # Поставить на новое место.

            piece = self.get_piece(row1, col1)
            if isinstance(piece, (Rook, King)):
                piece.set_has_moved()
            elif isinstance(piece, Pawn):
                if piece.can_promote(self):
                    if autopromote:
                        promote_char = 'Q'
                    else:
                        promote_char = self.promotion_func()

                    self.promote(row1, col1, promote_char)

            new = {
                (row, col): None,
                (row1, col1): self.board[row1][col1]
            }

            history_obj = HistoryObject(old, new, self.color)
            self.color = opponent(self.color)
            return history_obj
        elif self.can_castle(row, col, row1, col1):
            piece1 = self.board[row][col]
            piece2 = self.board[row1][col1]

            old = {
                (row, col): piece1,
                (row1, col1): piece2
            }

            piece1.set_has_moved()
            piece2.set_has_moved()

            self.board[row][col] = piece2
            self.board[row1][col1] = piece1

            new = {
                (row, col): piece2,
                (row1, col1): piece1
            }

            history_obj = HistoryObject(old, new, self.color)
            self.color = opponent(self.color)
            return history_obj
        else:
            return None

    def make_move(self, row, col, row1, col1, autopromote=False):
        history_obj = self.move_piece(row, col, row1, col1, autopromote)
        if isinstance(history_obj, HistoryObject):
            if self.history_pos != len(self.history) - 1:
                self.history = []
                self.history_pos = -1

            self.history.append(history_obj)
            self.history_pos += 1
            return history_obj

    def on_click(self, cell, button=LMB):
        if button == LMB:
            self.set_selected_cells([cell])
        elif button == RMB:
            if self.get_selected_cells():
                selected_col, selected_row = self.get_selected_cells()[0]
                col, row = cell
                history_obj = self.make_move(selected_row, selected_col, row, col)
                return history_obj

        return None

    def get_click(self, mouse_pos, button=LMB):
        cell = self.get_cell(mouse_pos)
        if cell:
            move = self.on_click(cell, button)
            return move
        return None

    def get_from_history(self, is_old):
        history_obj = self.history[self.history_pos]
        obj = history_obj.old if is_old else history_obj.new
        self.color = history_obj.color
        for key in obj.keys():
            row, col = key
            val = obj[key]
            self.board[row][col] = val

    def undo(self, do_pop=False):
        if self.history:
            if do_pop:
                self.history_pos = len(self.history) - 1

            if self.history_pos >= 0:
                self.get_from_history(True)
            if self.history_pos > 0:
                self.history_pos -= 1

            if do_pop:
                self.history.pop()

    def redo(self):
        if self.history:
            if self.history_pos < len(self.history):
                self.get_from_history(False)
            if self.history_pos < len(self.history) - 1:
                self.history_pos += 1


def main():
    size = 800, 800
    pygame.init()

    screen = pygame.display.set_mode(size)
    board = ChessBoard((600, 600), promotion_func=input)

    screen.fill(pygame.Color('black'))
    board.is_board_flipped = True
    board_surf = board.get_surface(draw_function=draw_chess)
    screen.blit(board_surf, (0, 0))
    pygame.display.flip()

    clock = pygame.time.Clock()

    running = True
    while running:
        has_interacted = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                left, _, right = pygame.mouse.get_pressed(3)

                btn = LMB if left else RMB
                board.get_click(event.pos, btn)

                has_interacted = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z:
                    board.undo()
                    has_interacted = True
                elif event.key == pygame.K_x:
                    board.redo()
                    has_interacted = True

        if has_interacted:
            screen.fill(pygame.Color('black'))
            board_surf = board.get_surface(draw_function=draw_chess)
            screen.blit(board_surf, (0, 0))
            pygame.display.flip()

        clock.tick(30)
    pygame.quit()


if __name__ == '__main__':
    main()
