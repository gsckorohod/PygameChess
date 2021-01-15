from tkinter import Tk
from tkinter import filedialog as fd

import pygame

import ai
import chess
import gui
from chess import RMB, LMB

BOARD_IMG = 'data/images/board.jpg'
FRAME_COLOR = pygame.Color('#ead7c6')
LETTER_COLOR = pygame.Color('#663a0d')
FONT_TYPEWRITER_PATH = 'data/fonts/linowrite.ttf'
BUTTON_IMG_PATH = 'data/images/buttons/'

PLAY_IMG = pygame.image.load(BUTTON_IMG_PATH + 'play.png')
PAUSE_IMG = pygame.image.load(BUTTON_IMG_PATH + 'pause.png')
REDO_IMG = pygame.image.load(BUTTON_IMG_PATH + 'redo.png')
UNDO_IMG = pygame.image.load(BUTTON_IMG_PATH + 'undo.png')
FLIP_IMG = pygame.image.load(BUTTON_IMG_PATH + 'flip.png')
RESET_IMG = pygame.image.load(BUTTON_IMG_PATH + 'reset.png')
SAVE_IMG = pygame.image.load(BUTTON_IMG_PATH + 'save.png')
OPEN_IMG = pygame.image.load(BUTTON_IMG_PATH + 'open.png')
BOT_ON_IMG = pygame.image.load(BUTTON_IMG_PATH + 'bot_on.png')
BOT_OFF_IMG = pygame.image.load(BUTTON_IMG_PATH + 'bot_off.png')

AI_DEPTH = 2


class PromoteDialog:
    def __init__(self, rect, target, btn_space=10, title_h=20, color=chess.WHITE):
        self.x, self.y, self.w, self.h = self.rect = rect
        self.btn_space = btn_space
        self.title_h = title_h

        self.target = target

        figures = list(chess.PIECES_CHARS.keys())
        figures.remove('K')
        self.figures = figures
        self.output = 'Q'

        self.btn_w = (self.w - self.btn_space * (len(self.figures) + 1)) // len(self.figures)

        self.gui_group = gui.UIGroup(rect)

        self.title_lbl = gui.UILabel((0, 0, self.w, self.title_h), 'Выберите фигуру:')

        for i, fig in enumerate(self.figures):
            x = self.btn_space + (self.btn_w + self.btn_space) * i
            y = self.btn_space + self.title_h

            piece = chess.PIECES_CHARS[fig](color)
            img = chess.get_piece_img(piece)
            del piece

            pygame.draw.rect(img, pygame.Color('black'), (3, 3, img.get_width() - 6, img.get_height() - 6), 9)

            btn = gui.UIButton((x, y, self.btn_w, self.btn_w), None, img=img, text=fig,
                               font_size=1, text_align=(gui.ALIGN_LEFT, gui.ALIGN_TOP))
            self.gui_group.add_element(btn)

        self.gui_group.add_element(self.title_lbl)

    def __call__(self):
        clock = pygame.time.Clock()

        mpos = pygame.mouse.get_pos()

        running = True

        while running:
            has_interacted = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    btn = self.gui_group.get_click(event.pos)
                    if isinstance(btn, gui.UIButton):
                        self.output = btn.text[0].upper()
                        running = False
                    has_interacted = True
                if event.type == pygame.MOUSEMOTION:
                    mpos = pygame.mouse.get_pos()
                    self.gui_group.get_mouse_over(mpos)
                    has_interacted = True
                if event.type == pygame.MOUSEBUTTONUP:
                    self.gui_group.get_mouse_up(mpos)
                    has_interacted = True

            if has_interacted:
                self.render()
                pygame.display.update(self.rect)

            clock.tick(10)

        del clock
        return self.output

    def get_img(self):
        return self.gui_group.get_img()

    def render(self):
        x, y, w, h = self.rect
        self.target.blit(self.get_img(), (x, y))


class Chess:
    def __init__(self, size, frame_size, pos=(0, 0), frame_image=None, frame_color=FRAME_COLOR, promote=input):
        self.size = self.w, self.h = size
        self.pos = self.x, self.y = pos
        self.offset = self.x_offset, self.y_offset = frame_size

        chess_side = min(self.size)
        self.chess_size = self.chess_w, self.chess_h = chess_side - 2 * self.x_offset, chess_side - 2 * self.y_offset
        self.chess_pos = self.chess_x, self.chess_y = self.w - (self.x_offset + self.chess_w), self.y_offset

        self.frame_color = frame_color

        self.chess_board = chess.ChessBoard(self.chess_size, promote)
        ui_x, ui_y = 20, 20
        ui_w, ui_h = self.w - chess_side - 40, self.h - 40

        self.lbl_status = gui.UILabel((10, 10, ui_w - 20, 50), bg_color=pygame.Color('white'), text='Ход белых')
        self.stopwatch = gui.UILcdDisplay((10, 10 + (self.lbl_status.y + self.lbl_status.h) + 10,
                                           ui_w - 20, 50))

        btn_w, btn_h = 50, 50
        self.play_btn = gui.UIButton((10, 10 + (self.stopwatch.y + self.stopwatch.h) + 10, btn_w, btn_h),
                                     self.unpause_stopwatch, img=PLAY_IMG)
        self.pause_btn = gui.UIButton((self.play_btn.x + self.play_btn.w + 20,
                                       10 + (self.stopwatch.y + self.stopwatch.h) + 10, btn_w, btn_h),
                                      self.pause_stopwatch, img=PAUSE_IMG)

        self.undo_btn = gui.UIButton((10, 10 + (self.play_btn.y + self.play_btn.h) + 30,
                                      btn_w, btn_h), self.undo, img=UNDO_IMG)

        self.redo_btn = gui.UIButton((self.undo_btn.x + self.undo_btn.w + 20,
                                      10 + (self.play_btn.y + self.play_btn.h) + 30,
                                      btn_w, btn_h), self.redo, img=REDO_IMG)

        self.flip_btn = gui.UIButton((self.redo_btn.x + self.redo_btn.w + 20,
                                      10 + (self.play_btn.y + self.play_btn.h) + 30,
                                      btn_w, btn_h), self.chess_board.flip, img=FLIP_IMG)

        self.reset_btn = gui.UIButton((10, 10 + (self.undo_btn.y + self.undo_btn.h) + 10,
                                       btn_w, btn_h), self.reset, img=RESET_IMG)

        self.save_btn = gui.UIButton((self.reset_btn.x + self.reset_btn.w + 20,
                                      10 + (self.undo_btn.y + self.undo_btn.h) + 10,
                                      btn_w, btn_h), self.write_to_file, img=SAVE_IMG)

        self.load_btn = gui.UIButton((self.save_btn.x + self.save_btn.w + 20,
                                      10 + (self.undo_btn.y + self.undo_btn.h) + 10,
                                      btn_w, btn_h), self.read_from_file, img=OPEN_IMG)

        self.ai_enabled_switch = gui.UISwitch((10, 10 + (self.reset_btn.y + self.reset_btn.h) + 30,
                                               btn_w, btn_h), action=self.switch_ai,
                                              on_img=BOT_ON_IMG, off_img=BOT_OFF_IMG)

        self.ai_enabled_lbl = gui.UILabel((self.ai_enabled_switch.x + self.ai_enabled_switch.w + 20,
                                           self.ai_enabled_switch.y,
                                           ui_w - self.ai_enabled_switch.w - 40,
                                           btn_h), 'ИИ выключен')

        self.turn_history_box = gui.UIListVertical((10,
                                                    10 + (self.ai_enabled_switch.y + self.ai_enabled_switch.h) + 30,
                                                    ui_w - 20,
                                                    ui_h - (self.ai_enabled_switch.y + self.ai_enabled_switch.h + 50)))

        self.gui_group = gui.UIGroup((ui_x, ui_y, ui_w, ui_h))

        self.gui_group.add_element(self.stopwatch)
        self.gui_group.add_element(self.lbl_status)
        self.gui_group.add_element(self.turn_history_box)
        self.gui_group.add_element(self.pause_btn)
        self.gui_group.add_element(self.play_btn)
        self.gui_group.add_element(self.undo_btn)
        self.gui_group.add_element(self.redo_btn)
        self.gui_group.add_element(self.flip_btn)
        self.gui_group.add_element(self.reset_btn)
        self.gui_group.add_element(self.save_btn)
        self.gui_group.add_element(self.load_btn)
        self.gui_group.add_element(self.ai_enabled_switch)
        self.gui_group.add_element(self.ai_enabled_lbl)

        if isinstance(frame_image, pygame.Surface):
            self.img = pygame.transform.smoothscale(frame_image, self.size)
        else:
            self.img = self.get_frame_img()

        self.is_ai_enabled = False

        self.turn_len = 120
        self.stopwatch_secs = self.turn_len
        self.is_stopwatch_running = True

        self.update_stopwatch_text()

    def switch_ai(self):
        self.is_ai_enabled = self.ai_enabled_switch.get_state()
        if self.is_ai_enabled:
            self.ai_enabled_lbl.set_text('ИИ включен')
        else:
            self.ai_enabled_lbl.set_text('ИИ выключен')

    def write_to_file(self):
        file_name = fd.asksaveasfilename(filetypes=[("Txt files", "*.txt")])

        if file_name:
            self.chess_board.write_to_file(file_name)

    def read_from_file(self):
        file_name = fd.askopenfilename(filetypes=[("Txt files", "*.txt")])

        if file_name:
            try:
                self.chess_board.read_from_file(file_name)
            except Exception as error:
                print('Error reading file:', error)
                self.reset()

        self.turn_history_box.clear()

    def undo(self):
        self.chess_board.undo()
        self.stopwatch_secs = self.turn_len
        self.update_stopwatch_text()

    def redo(self):
        self.chess_board.redo()
        self.stopwatch_secs = self.turn_len
        self.update_stopwatch_text()

    def reset(self):
        self.chess_board.reset()

        self.turn_history_box.clear()

        self.stopwatch_secs = self.turn_len
        self.is_stopwatch_running = True
        self.update_stopwatch_text()

    def pause_stopwatch(self):
        self.is_stopwatch_running = False

    def unpause_stopwatch(self):
        self.is_stopwatch_running = True

    def update_stopwatch_text(self):
        mins = self.stopwatch_secs // 60
        secs = self.stopwatch_secs % 60

        s_mins = ('0' if mins < 10 else '') + str(mins)
        s_secs = ('0' if secs < 10 else '') + str(secs)

        self.stopwatch.set_text(s_mins + ':' + s_secs)

    def tick_stopwatch(self):
        if self.is_stopwatch_running and not self.chess_board.is_checkmate():
            self.stopwatch_secs -= 1
            self.update_stopwatch_text()

            if self.stopwatch_secs == 0:
                self.stopwatch_secs = self.turn_len
                self.change_turn()

    def get_frame_img(self):
        img = pygame.Surface(self.size)

        img.fill(self.frame_color)

        size = min(self.chess_board.col_size // 2, self.chess_board.row_size // 2, self.y_offset - 4)
        font = pygame.font.Font(FONT_TYPEWRITER_PATH, size)

        flipped = self.chess_board.get_flipped()

        for i in range(8):
            row_letter_img = font.render(chess.get_row_letter(i, is_flipped=flipped), True, LETTER_COLOR)
            col_letter_img = font.render(chess.get_col_letter(i, is_flipped=flipped), True, LETTER_COLOR)

            x_off = (self.x_offset - row_letter_img.get_width()) // 2
            y_off = (self.y_offset - col_letter_img.get_height()) // 2

            col_offset = (self.chess_board.col_size - col_letter_img.get_width()) // 2
            row_offset = (self.chess_board.row_size - row_letter_img.get_height()) // 2

            x = self.chess_x + col_offset + (self.chess_board.col_size * i)
            y = self.chess_y + row_offset + (self.chess_board.row_size * i)

            img.blit(row_letter_img, (self.chess_x - self.x_offset + x_off, y))
            img.blit(row_letter_img, (self.w - self.x_offset + x_off, y))
            img.blit(col_letter_img, (x, y_off))
            img.blit(col_letter_img, (x, self.h - self.y_offset + y_off))

        chess_side = min(self.size)
        cx, cy = self.w - chess_side, self.h - chess_side
        offset = 4
        pygame.draw.rect(img, LETTER_COLOR, (cx + offset, cy + offset,
                                             chess_side - 2 * offset, chess_side - 2 * offset), 5)
        pygame.draw.rect(img, chess.BLACK_CELL_COLOR, (self.chess_x - 2, self.chess_y - 2,
                                                       self.chess_w, self.chess_h), 3)

        return img

    def get_surface(self):
        board_img = self.chess_board.get_surface(chess.draw_chess)

        frame = self.get_frame_img()

        frame.blit(board_img, self.chess_pos)
        self.gui_group.render(frame)

        return frame

    def render(self, target):
        img = self.get_surface()
        target.blit(img, self.pos)

    def get_mouse_over(self, mouse_pos):
        self.gui_group.get_mouse_over(mouse_pos)

    def get_mouse_up(self, mouse_pos):
        self.gui_group.get_mouse_up(mouse_pos)

    def make_ai_move(self):
        is_maximising = self.chess_board.color == chess.WHITE

        best_move = ai.minimax_root(AI_DEPTH, self.chess_board, is_maximising)

        history_obj = self.chess_board.make_move(*best_move, True)

        self.update_game(history_obj)

        self.stopwatch_secs = self.turn_len
        self.update_stopwatch_text()

    def change_turn(self):
        self.chess_board.color = chess.opponent(self.chess_board.color)
        if self.chess_board.color == chess.WHITE:
            self.lbl_status.set_text('Ход белых')
        else:
            self.lbl_status.set_text('Ход чёрных')

    def update_game(self, history_obj):
        if isinstance(history_obj, chess.HistoryObject):
            self.stopwatch_secs = self.turn_len
            self.update_stopwatch_text()

            c1, c2, *_ = history_obj.old.keys()
            f1, f2 = history_obj.old[c1], history_obj.old[c2]

            if isinstance(f1, (chess.King, chess.Queen, chess.Rook, chess.Pawn, chess.Knight, chess.Bishop)):
                char = f1.char()[0]

                s_pos1 = chess.to_chess_notation(c1).lower()
                s_pos2 = chess.to_chess_notation(c2).lower()

                s_color = 'Белые' if history_obj.color == chess.WHITE else 'Чёрные'

                text = s_color + ': ' + char + ' ' + s_pos1 + ' - ' + s_pos2

                new_lbl = gui.UILabel((0, 0, 100, 30))
                self.turn_history_box.add_element(new_lbl, True)
                new_lbl.set_text(text)

        if self.chess_board.color == chess.WHITE:
            self.lbl_status.set_text('Ход белых')
        else:
            self.lbl_status.set_text('Ход чёрных')

    def get_click(self, mouse_pos, button=LMB):
        self.gui_group.get_click(mouse_pos)

        mx, my = mouse_pos
        mpos = mx - self.chess_x, my - self.y - self.chess_y

        move = self.chess_board.get_click(mpos, button)

        self.update_game(move)
        return move


def main():
    size = screen_w, screen_h = 1000, 700

    pygame.init()

    screen = pygame.display.set_mode(size)
    screen.fill(pygame.Color('white'))

    dialog_w, dialog_h = screen_w // 2, screen_h // 4
    dialog_x, dialog_y = (screen_w - dialog_w) // 2, (screen_h - dialog_h) // 2

    dia = PromoteDialog((dialog_x, dialog_y, dialog_w, dialog_h), screen, 10, 40)

    chessb = Chess(size, (60, 60), (0, 0), promote=dia)

    game_over_lbl = gui.UILabel((0, 0, dialog_w, dialog_h // 2 - 10), text='Игра закончена',
                                bg_color=pygame.Color('white'))
    play_again_btn = gui.UIButton((20, dialog_h // 2, dialog_w - 40, dialog_h // 2 - 10), chessb.reset,
                                  text='Начать заново')
    game_over = gui.UIGroup((dialog_x, dialog_y, dialog_w, dialog_h), bg_color=pygame.Color('white'))
    game_over.add_element(game_over_lbl)
    game_over.add_element(play_again_btn)
    game_over.hide()

    chessb.render(screen)
    pygame.display.flip()

    clock = pygame.time.Clock()

    STOPWATCH_TICK = pygame.USEREVENT + 1
    pygame.time.set_timer(STOPWATCH_TICK, 1000)

    mpos = pygame.mouse.get_pos()

    running = True

    while running:
        has_interacted = False
        is_checkmate = chessb.chess_board.is_checkmate()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                left, _, right = pygame.mouse.get_pressed(3)

                btn = LMB if left else RMB

                if is_checkmate:
                    game_over.get_click(mpos)
                else:
                    if chessb.get_click(event.pos, btn) and chessb.is_ai_enabled:
                        chessb.render(screen)
                        pygame.display.update((chessb.x, chessb.y, chessb.w, chessb.h))

                        if not chessb.chess_board.is_checkmate():
                            chessb.make_ai_move()

                has_interacted = True
            if event.type == pygame.MOUSEMOTION:
                mpos = pygame.mouse.get_pos()

                chessb.get_mouse_over(mpos)
                game_over.get_mouse_over(mpos)

                has_interacted = True
            if event.type == pygame.MOUSEBUTTONUP:
                chessb.get_mouse_up(mpos)
                game_over.get_mouse_up(mpos)

                has_interacted = True
            if event.type == STOPWATCH_TICK:
                chessb.tick_stopwatch()
                has_interacted = True

        if has_interacted or is_checkmate:
            screen.fill(pygame.Color('white'))
            chessb.render(screen)

            if is_checkmate:
                game_over.show()

                text = 'Игра закончена! '
                if chessb.chess_board.color == chess.WHITE:
                    text += 'Победили чёрные'
                else:
                    text += 'Победили белые'

                game_over_lbl.set_text(text)
                game_over.render(screen)

            pygame.display.flip()

        if not is_checkmate:
            game_over.hide()

    clock.tick(10)


pygame.quit()

if __name__ == '__main__':
    Tk().withdraw()
    main()
