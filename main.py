import os
import random
from kivy.app import App
from kivy.core.text import LabelBase
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle, Line
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout

COLS = 10
ROWS = 20

SHAPES = [
    [[1, 1, 1, 1]],
    [[1, 1], [1, 1]],
    [[0, 1, 0], [1, 1, 1]],
    [[1, 1, 0], [0, 1, 1]],
    [[0, 1, 1], [1, 1, 0]],
    [[1, 0, 0], [1, 1, 1]],
    [[0, 0, 1], [1, 1, 1]],
]

COLORS = [
    (0, 1, 1, 1),
    (1, 1, 0, 1),
    (0.5, 0, 0.5, 1),
    (0, 1, 0, 1),
    (1, 0, 0, 1),
    (0, 0, 1, 1),
    (1, 0.5, 0, 1),
]

SWIPE_THRESHOLD = 30

BEST_SCORE_FILE = 'best_score.txt'

FONT_PATHS = (
    'C:/Windows/Fonts/calibri.ttf',
)


def register_app_font():
    for path in FONT_PATHS:
        if os.path.isfile(path):
            LabelBase.register(name='AppFont', fn_regular=path)
            return 'AppFont'
    return None


APP_FONT = register_app_font()


def styled_button(text, **kwargs):
    btn = Button(text=text, **kwargs)
    if APP_FONT:
        btn.font_name = APP_FONT
    return btn


def styled_label(text, **kwargs):
    lbl = Label(text=text, **kwargs)
    if APP_FONT:
        lbl.font_name = APP_FONT
    return lbl


class TetrisGame(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.board = [[0] * COLS for _ in range(ROWS)]
        self.current_piece = None
        self.current_color = None
        self.current_x = 0
        self.current_y = 0
        self.score = 0
        self.game_over = False
        self.speed = 1.0
        self.paused = False
        self._touch_start = None
        self.cell_size = 30
        self.next_piece = None
        self.next_color = None

        self.bind(size=self.on_size_change)
        self.draw_board()
        Clock.schedule_interval(self.fall, self.speed)
        self.new_piece()

    def _app(self):
        return App.get_running_app()

    def on_size_change(self, *args):
        self.update_cell_size()
        self.draw_board()

    def update_cell_size(self):
        side_margin = 4
        top_bottom_margin = 4
        available_w = self.width - side_margin * 2
        available_h = self.height - top_bottom_margin * 2
        self.cell_size = min(available_w // COLS, available_h // ROWS)
        self.cell_size = max(14, self.cell_size)

    def draw_board(self):
        self.canvas.clear()
        bx = self.x + (self.width - COLS * self.cell_size) / 2
        by = self.y + (self.height - ROWS * self.cell_size) / 2

        with self.canvas:
            Color(0.08, 0.08, 0.08, 1)
            Rectangle(pos=(bx - 2, by - 2), size=(COLS * self.cell_size + 4, ROWS * self.cell_size + 4))

            for y in range(ROWS):
                for x in range(COLS):
                    if self.board[y][x]:
                        Color(*self.board[y][x])
                        Rectangle(
                            pos=(bx + x * self.cell_size, by + y * self.cell_size),
                            size=(self.cell_size, self.cell_size)
                        )
                    else:
                        Color(0.15, 0.15, 0.15, 1)
                        Rectangle(
                            pos=(bx + x * self.cell_size, by + y * self.cell_size),
                            size=(self.cell_size - 1, self.cell_size - 1)
                        )

            if self.current_piece and not self.game_over:
                Color(*self.current_color)
                for y, row in enumerate(self.current_piece):
                    for x, cell in enumerate(row):
                        if cell:
                            board_x = self.current_x + x
                            board_y = self.current_y + y
                            if 0 <= board_y < ROWS and 0 <= board_x < COLS:
                                Rectangle(
                                    pos=(bx + board_x * self.cell_size, by + board_y * self.cell_size),
                                    size=(self.cell_size - 1, self.cell_size - 1)
                                )

            Color(0.25, 0.25, 0.25, 1)
            for x in range(COLS + 1):
                x_pos = bx + x * self.cell_size
                Line(points=[x_pos, by, x_pos, by + ROWS * self.cell_size], width=1)
            for y in range(ROWS + 1):
                y_pos = by + y * self.cell_size
                Line(points=[bx, y_pos, bx + COLS * self.cell_size, y_pos], width=1)

    def new_piece(self):
        if self.next_piece is not None:
            self.current_piece = self.next_piece
            self.current_color = self.next_color
        else:
            shape_idx = random.randint(0, len(SHAPES) - 1)
            self.current_piece = SHAPES[shape_idx]
            self.current_color = COLORS[shape_idx]
        shape_idx = random.randint(0, len(SHAPES) - 1)
        self.next_piece = SHAPES[shape_idx]
        self.next_color = COLORS[shape_idx]
        self.current_x = COLS // 2 - len(self.current_piece[0]) // 2
        self.current_y = ROWS - len(self.current_piece)
        if not self.valid_position(self.current_piece, self.current_x, self.current_y):
            self.game_over = True
            self.draw_board()
            app = self._app()
            if app:
                app.show_game_over()
        app = self._app()
        if app and hasattr(app, 'update_next_piece'):
            app.update_next_piece()

    def valid_position(self, piece, px, py):
        for y, row in enumerate(piece):
            for x, cell in enumerate(row):
                if cell:
                    board_x = px + x
                    board_y = py + y
                    if board_x < 0 or board_x >= COLS or board_y < 0 or board_y >= ROWS:
                        return False
                    if self.board[board_y][board_x]:
                        return False
        return True

    def fall(self, dt):
        if self.game_over or self.paused:
            return
        if self.valid_position(self.current_piece, self.current_x, self.current_y - 1):
            self.current_y -= 1
        else:
            self.lock_piece()
            self.clear_lines()
            self.new_piece()
        self.draw_board()

    def lock_piece(self):
        for y, row in enumerate(self.current_piece):
            for x, cell in enumerate(row):
                if cell:
                    board_x = self.current_x + x
                    board_y = self.current_y + y
                    if 0 <= board_y < ROWS and 0 <= board_x < COLS:
                        self.board[board_y][board_x] = self.current_color
        self.current_piece = None

    def clear_lines(self):
        lines_cleared = 0
        y = ROWS - 1
        while y >= 0:
            if all(self.board[y]):
                for yy in range(y, ROWS - 1):
                    self.board[yy] = self.board[yy + 1][:]
                self.board[ROWS - 1] = [0] * COLS
                lines_cleared += 1
            else:
                y -= 1
        if lines_cleared:
            self.score += lines_cleared * 100
            app = self._app()
            if app:
                app.update_score(self.score)

    def move_left(self):
        if self.game_over or self.paused:
            return
        if self.valid_position(self.current_piece, self.current_x - 1, self.current_y):
            self.current_x -= 1
            self.draw_board()

    def move_right(self):
        if self.game_over or self.paused:
            return
        if self.valid_position(self.current_piece, self.current_x + 1, self.current_y):
            self.current_x += 1
            self.draw_board()

    def rotate(self):
        if self.game_over or self.paused:
            return
        rotated = [list(row) for row in zip(*self.current_piece[::-1])]
        if self.valid_position(rotated, self.current_x, self.current_y):
            self.current_piece = rotated
            self.draw_board()

    def drop(self):
        if self.game_over or self.paused:
            return
        while self.valid_position(self.current_piece, self.current_x, self.current_y - 1):
            self.current_y -= 1
        self.lock_piece()
        self.clear_lines()
        self.new_piece()
        self.draw_board()

    def restart(self):
        self.board = [[0] * COLS for _ in range(ROWS)]
        self.score = 0
        self.game_over = False
        self.paused = False
        self.next_piece = None
        self.next_color = None
        app = self._app()
        if app:
            app.update_score(0)
            app.hide_game_over()
            app.pause_btn.set_paused(False)
        self.new_piece()
        self.draw_board()

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return super().on_touch_down(touch)
        self._touch_start = (touch.x, touch.y)
        return True

    def on_touch_up(self, touch):
        if self._touch_start is None:
            return super().on_touch_up(touch)
        dx = touch.x - self._touch_start[0]
        dy = touch.y - self._touch_start[1]
        self._touch_start = None

        if abs(dx) < SWIPE_THRESHOLD and abs(dy) < SWIPE_THRESHOLD:
            self.rotate()
        elif abs(dx) > abs(dy):
            if dx > SWIPE_THRESHOLD:
                self.move_right()
            elif dx < -SWIPE_THRESHOLD:
                self.move_left()
        elif dy < -SWIPE_THRESHOLD:
            self.drop()
        return True


class NextPiecePreview(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.piece = None
        self.piece_color = (1, 1, 1, 1)
        self.bind(size=self._redraw)

    def set_piece(self, piece, color):
        self.piece = piece
        self.piece_color = color
        self._redraw()

    def _redraw(self, *args):
        self.canvas.clear()
        if not self.piece:
            with self.canvas:
                Color(0.1, 0.1, 0.1, 1)
                Rectangle(pos=self.pos, size=self.size)
            return
        rows = len(self.piece)
        cols = len(self.piece[0])
        preview_cell = min(self.width / 6, self.height / 6)
        preview_cell = max(4, preview_cell)
        px = self.x + (self.width - cols * preview_cell) / 2
        py = self.y + (self.height - rows * preview_cell) / 2
        with self.canvas:
            Color(0.08, 0.08, 0.08, 1)
            Rectangle(pos=(px - 2, py - 2), size=(cols * preview_cell + 4, rows * preview_cell + 4))
            for y in range(rows):
                for x in range(cols):
                    if self.piece[y][x]:
                        Color(*self.piece_color)
                        Rectangle(pos=(px + x * preview_cell, py + y * preview_cell),
                                  size=(preview_cell, preview_cell))
                    else:
                        Color(0.15, 0.15, 0.15, 1)
                        Rectangle(pos=(px + x * preview_cell, py + y * preview_cell),
                                  size=(preview_cell - 1, preview_cell - 1))


class ImageTextButton(ButtonBehavior, BoxLayout):
    def __init__(self, text='', image_source=None, image_position='left', font_size=36, action=None, bg_color=(0.2, 0.4, 1, 1), color=(1, 1, 1, 1), **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.padding = [2, 2]
        self.spacing = 2

        with self.canvas.before:
            Color(*bg_color)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(pos=self._update_bg, size=self._update_bg)

        btn_font = APP_FONT

        self.img_size = int(font_size * 1.45)

        if image_source and image_position == 'left':
            img = Image(source=image_source, size_hint=(None, 1), width=self.img_size)
            self.add_widget(img)

        self.label = Label(text=text, font_size=font_size, color=color, bold=True)
        if btn_font:
            self.label.font_name = btn_font
        self.add_widget(self.label)

        if image_source and image_position == 'right':
            img = Image(source=image_source, size_hint=(None, 1), width=self.img_size)
            self.add_widget(img)

        if action:
            self.bind(on_press=lambda x: action())

    def _update_bg(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos


class PausePlayButton(ButtonBehavior, BoxLayout):
    def __init__(self, pause_source='img/pause.png', play_source='img/play.png', **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.pause_source = pause_source
        self.play_source = play_source
        self._is_paused = False

        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(pos=self._update_bg, size=self._update_bg)

        self.img = Image(source=self.pause_source, size_hint=(1, 1))
        self.add_widget(self.img)

    def _update_bg(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos

    def set_paused(self, paused):
        self._is_paused = paused
        self.img.source = self.play_source if paused else self.pause_source


class TetrisApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.best_score = self.load_best_score()

    def build(self):
        root = FloatLayout()

        content = BoxLayout(orientation='vertical', size_hint=(1, 1))

        top_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.06), spacing=2, padding=[3, 1])
        btn_pause = PausePlayButton(pause_source='img/pause.png', play_source='img/play.png',
                                    size_hint=(0.12, 1))
        btn_pause.bind(on_press=self.toggle_pause)
        top_layout.add_widget(btn_pause)
        self.pause_btn = btn_pause

        score_box = BoxLayout(orientation='vertical', size_hint=(0.73, 1), spacing=0)
        self.score_label = styled_label(text='Счёт: 0', font_size=14, halign='center', valign='middle')
        self.score_label.bind(size=self.score_label.setter('text_size'))
        score_box.add_widget(self.score_label)

        self.best_score_label = styled_label(text='Наилучний счёт: 0', font_size=14, halign='center', valign='middle', color=(1, 1, 0, 1))
        self.best_score_label.bind(size=self.best_score_label.setter('text_size'))
        score_box.add_widget(self.best_score_label)
        self.update_best_score_display()
        top_layout.add_widget(score_box)

        btn_exit = styled_button(text='Выход', font_size=38, size_hint=(0.15, 1),
                                 background_color=(1, 0.2, 0.2, 1), color=(1, 1, 1, 1))
        btn_exit.bind(on_press=self.exit_app)
        top_layout.add_widget(btn_exit)
        content.add_widget(top_layout)

        next_row = BoxLayout(orientation='horizontal', size_hint=(1, 0.10), spacing=2, padding=[3, 1])
        self.next_preview = NextPiecePreview(size_hint=(1, 1))
        next_row.add_widget(self.next_preview)
        content.add_widget(next_row)

        self.game = TetrisGame()
        self.game.size_hint = (1, 0.76)
        content.add_widget(self.game)

        bottom_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.08), spacing=6, padding=[6, 6])

        btn_left = ImageTextButton(text='Влево', image_source='img/left.png', image_position='left',
                                    font_size=36, action=self.game.move_left, bg_color=(0.2, 0.4, 1, 1))
        bottom_layout.add_widget(btn_left)

        btn_rotate = ImageTextButton(text='Поворот', image_source='img/rotate.png', image_position='left',
                                     font_size=36, action=self.game.rotate, bg_color=(1, 0.85, 0, 1), color=(0, 0, 0, 1))
        bottom_layout.add_widget(btn_rotate)

        btn_drop = ImageTextButton(text='Вниз', image_source='img/bottom.png', image_position='left',
                                   font_size=36, action=self.game.drop, bg_color=(0.6, 0.2, 0.8, 1))
        bottom_layout.add_widget(btn_drop)

        btn_right = ImageTextButton(text='Вправо', image_source='img/right.png', image_position='right',
                                     font_size=36, action=self.game.move_right, bg_color=(0.2, 0.4, 1, 1))
        bottom_layout.add_widget(btn_right)
        content.add_widget(bottom_layout)

        root.add_widget(content)

        self.game_over_layout = BoxLayout(
            orientation='vertical',
            size_hint=(0.7, 0.35),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            padding=20,
            spacing=10,
        )
        self.game_over_layout.opacity = 0
        self.game_over_layout.disabled = True
        with self.game_over_layout.canvas.before:
            Color(0, 0, 0, 0.8)
            self._overlay_bg = Rectangle(pos=self.game_over_layout.pos, size=self.game_over_layout.size)
        self.game_over_layout.bind(
            pos=lambda w, v: setattr(self._overlay_bg, 'pos', v),
            size=lambda w, v: setattr(self._overlay_bg, 'size', v),
        )
        self.game_over_label = styled_label(text='Игра окончена', font_size=28, color=(1, 0, 0, 1))
        self.game_over_layout.add_widget(self.game_over_label)

        restart_btn = styled_button(text='Заново', font_size=28, size_hint=(1, 0.4),
                                    background_color=(0.3, 0.7, 0.3, 1), color=(1, 1, 1, 1))
        restart_btn.bind(on_press=lambda x: self.game.restart())
        self.game_over_layout.add_widget(restart_btn)
        root.add_widget(self.game_over_layout)

        return root

    def load_best_score(self):
        try:
            if os.path.exists(BEST_SCORE_FILE):
                with open(BEST_SCORE_FILE, 'r') as f:
                    return int(f.read().strip())
        except:
            pass
        return 0

    def save_best_score(self):
        try:
            with open(BEST_SCORE_FILE, 'w') as f:
                f.write(str(self.best_score))
        except:
            pass

    def update_best_score_display(self):
        self.best_score_label.text = f'Наилучний счёт: {self.best_score}'

    def update_score(self, score):
        self.score_label.text = f'Счёт: {score}'

    def update_next_piece(self):
        if hasattr(self, 'next_preview') and hasattr(self, 'game'):
            self.next_preview.set_piece(self.game.next_piece, self.game.next_color)

    def show_game_over(self):
        self.game_over_layout.opacity = 1
        self.game_over_layout.disabled = False
        if self.game.score > self.best_score:
            self.best_score = self.game.score
            self.save_best_score()
            self.update_best_score_display()

    def hide_game_over(self):
        self.game_over_layout.opacity = 0
        self.game_over_layout.disabled = True

    def toggle_pause(self, instance):
        self.game.paused = not self.game.paused
        self.pause_btn.set_paused(self.game.paused)

    def exit_app(self, instance):
        App.get_running_app().stop()


if __name__ == '__main__':
    TetrisApp().run()
