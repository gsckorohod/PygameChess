import pygame

LMB = 1
RMB = 3


class Board:
    def __init__(self, width, height, cell_size=(30, 30), board_size=None):
        self.width = width
        self.height = height
        self.board = [[None] * width for _ in range(height)]
        self.left = 0
        self.top = 0

        self.cell_size = cell_size
        self.default_draw_func = None
        self.is_board_flipped = False

        if board_size is not None:
            b_w, b_h = board_size
            self.cell_size = ((b_h - self.top) // height), ((b_w - self.left) // width)

        self.row_size, self.col_size = self.cell_size

        self.selected_cells = []

    def get_selected_cells(self):
        return self.selected_cells

    def set_selected_cells(self, cells):
        self.selected_cells = cells

    def select_cell(self, cell):
        self.selected_cells.append(cell)

    def deselect_cell(self, cell):
        if cell in self.selected_cells:
            self.selected_cells.remove(cell)

    def is_cell_selected(self, cell):
        return cell in self.selected_cells

    def flip(self):
        self.is_board_flipped = not self.is_board_flipped

    def get_flipped(self):
        return self.is_board_flipped

    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def render(self, surface, draw_function=None):
        draw_func = self.default_draw_func

        if draw_function:
            draw_func = draw_function

        for y in range(self.width):
            for x in range(self.width):
                r_pos = (r_x, r_y, rw, rh) = (x * self.col_size + self.left, y * self.row_size + self.top,
                                              self.col_size, self.row_size)

                if self.is_board_flipped:
                    r_y = (self.height - 1) * self.row_size - r_y
                    r_x = (self.width - 1) * self.col_size - r_x

                if draw_func:
                    new_surface = draw_func(r_pos, (x, y), self)
                    surface.blit(new_surface, (r_x, r_y))
                else:
                    pygame.draw.rect(surface, pygame.Color("black"), r_pos)
                    pygame.draw.rect(surface, pygame.Color("white"), r_pos, 1)

    def get_surface(self, draw_function=None):
        surface = pygame.Surface((self.width * self.col_size + self.left, self.height * self.row_size + self.top))
        self.render(surface, draw_function)
        return surface

    def on_click(self, cell, button=LMB):
        print('clicked cell:', cell)

    def get_cell(self, mouse_pos):
        cell_x = (mouse_pos[0] - self.left) // self.col_size
        cell_y = (mouse_pos[1] - self.top) // self.row_size

        if cell_x < 0 or cell_x >= self.width or cell_y < 0 or cell_y >= self.height:
            return None

        if self.is_board_flipped:
            cell_y = self.height - cell_y - 1
            cell_x = self.width - cell_x - 1

        return cell_x, cell_y

    def get_click(self, mouse_pos, button=LMB):
        cell = self.get_cell(mouse_pos)
        if cell:
            self.on_click(cell, button)

    def get_neighbours(self, cell, diag=False):
        col, row = cell
        out = []

        if row > 0:
            out.append((col, row - 1))
            if diag:
                if col > 0:
                    out.append((col - 1, row - 1))
                if col < self.width - 1:
                    out.append((col + 1, row - 1))
        if row < self.height - 1:
            out.append((col, row + 1))
            if diag:
                if col > 0:
                    out.append((col - 1, row + 1))
                if col < self.width - 1:
                    out.append((col + 1, row + 1))
        if col > 0:
            out.append((col - 1, row))
        if col < self.width - 1:
            out.append((col + 1, row))

        return out

    def get_value(self, cell):
        col, row = cell
        return self.board[row][col]


def main():
    size = 500, 500
    pygame.init()

    screen = pygame.display.set_mode(size)
    board = Board(10, 10, board_size=(400, 400))
    board_surf = board.get_surface()

    screen.fill(pygame.Color('black'))
    screen.blit(board_surf, (0, 0))
    pygame.display.flip()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
    pygame.quit()


if __name__ == '__main__':
    main()
