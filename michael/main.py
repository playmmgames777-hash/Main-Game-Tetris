import random
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout

# Размеры поля
COLS = 10
ROWS = 20
BLOCK_SIZE = 30  # базовый размер, будет пересчитан под экран

# Фигуры Тетриса
SHAPES = [
    [[1, 1, 1, 1]],                         # I
    [[1, 1], [1, 1]],                       # O
    [[0, 1, 0], [1, 1, 1]],                 # T
    [[1, 1, 0], [0, 1, 1]],                 # S
    [[0, 1, 1], [1, 1, 0]],                 # Z
    [[1, 0, 0], [1, 1, 1]],                 # J
    [[0, 0, 1], [1, 1, 1]],                 # L
]

COLORS = [
    (0, 1, 1, 1),    # cyan
    (1, 1, 0, 1),    # yellow
    (0.5, 0, 0.5, 1),# purple
    (0, 1, 0, 1),    # green
    (1, 0, 0, 1),    # red
    (0, 0, 1, 1),    # blue
    (1, 0.5, 0, 1),  # orange
]

class TetrisGame(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Инициализация поля
        self.board = [[0] * COLS for _ in range(ROWS)]
        self.current_piece = None
        self.current_color = None
        self.current_x = 0
        self.current_y = 0
        self.score = 0
        self.game_over = False
        self.speed = 1.0  # секунд на падение одной клетки
        self.paused = False

        # Привязка размера окна
        Window.bind(on_resize=self.on_window_resize)
        self.cell_size = BLOCK_SIZE
        self.update_cell_size()

        # Рисование игрового поля (будет обновляться)
        self.draw_board()

        # Таймер падения фигуры
        Clock.schedule_interval(self.fall, self.speed)

        # Новая фигура
        self.new_piece()

    def update_cell_size(self, *args):
        # Вычисляем размер клетки так, чтобы поле поместилось по высоте экрана
        # Оставляем место для кнопок (примерно 150 пикселей снизу)
        available_height = Window.height - 150
        self.cell_size = min(BLOCK_SIZE, available_height // ROWS)
        # Если ширина меньше, можно ещё подогнать, но обычно хватает
        self.cell_size = max(20, self.cell_size)

    def on_window_resize(self, instance, width, height):
        self.update_cell_size()
        self.draw_board()

    def draw_board(self):
        self.canvas.clear()
        with self.canvas:
            # Фон поля (тёмный)
            Color(0.1, 0.1, 0.1, 1)
            self.bg_rect = Rectangle(
                pos=(self.center_x - (COLS * self.cell_size) / 2,
                     self.center_y - (ROWS * self.cell_size) / 2 + 50),
                size=(COLS * self.cell_size, ROWS * self.cell_size)
            )
            # Сетка и блоки
            for y in range(ROWS):
                for x in range(COLS):
                    if self.board[y][x]:
                        color = self.board[y][x]
                        Color(*color)
                        Rectangle(
                            pos=(self.bg_rect.pos[0] + x * self.cell_size,
                                 self.bg_rect.pos[1] + y * self.cell_size),
                            size=(self.cell_size, self.cell_size)
                        )
            # Текущая фигура
            if self.current_piece and not self.game_over:
                Color(*self.current_color)
                for y, row in enumerate(self.current_piece):
                    for x, cell in enumerate(row):
                        if cell:
                            board_x = self.current_x + x
                            board_y = self.current_y + y
                            if 0 <= board_y < ROWS and 0 <= board_x < COLS:
                                Rectangle(
                                    pos=(self.bg_rect.pos[0] + board_x * self.cell_size,
                                         self.bg_rect.pos[1] + board_y * self.cell_size),
                                    size=(self.cell_size, self.cell_size)
                                )
            # Разделительные линии (по желанию)
            Color(0.3, 0.3, 0.3)
            for x in range(COLS + 1):
                x_pos = self.bg_rect.pos[0] + x * self.cell_size
                from kivy.graphics import Line
                self.canvas.add(Line(points=[x_pos, self.bg_rect.pos[1],
                                            x_pos, self.bg_rect.pos[1] + ROWS * self.cell_size],
                                     width=1))
            for y in range(ROWS + 1):
                y_pos = self.bg_rect.pos[1] + y * self.cell_size
                self.canvas.add(Line(points=[self.bg_rect.pos[0], y_pos,
                                            self.bg_rect.pos[0] + COLS * self.cell_size, y_pos],
                                     width=1))

    def new_piece(self):
        shape_idx = random.randint(0, len(SHAPES)-1)
        self.current_piece = SHAPES[shape_idx]
        self.current_color = COLORS[shape_idx]
        self.current_x = COLS // 2 - len(self.current_piece[0]) // 2
        self.current_y = ROWS - len(self.current_piece)  # появляется сверху
        if not self.valid_position(self.current_piece, self.current_x, self.current_y):
            self.game_over = True
            self.draw_board()
            # Показываем Game Over через метку (обновим позже)
            if hasattr(self, 'parent') and self.parent:
                self.parent.show_game_over()

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
                # Удалить линию
                for yy in range(y, 0, -1):
                    self.board[yy] = self.board[yy-1][:]
                self.board[0] = [0] * COLS
                lines_cleared += 1
                # не уменьшаем y, так как теперь на этой строке новая (сдвинутая)
            else:
                y -= 1
        if lines_cleared:
            self.score += lines_cleared * 100
            if hasattr(self, 'parent') and self.parent:
                self.parent.update_score(self.score)

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
        # Поворот по часовой стрелке
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
        if hasattr(self, 'parent') and self.parent:
            self.parent.update_score(0)
            self.parent.hide_game_over()
        self.new_piece()
        self.draw_board()

    def on_touch_down(self, touch):
        # Обрабатываем касания кнопок (если они есть в родительском лейауте)
        # Но мы разместим кнопки как отдельные виджеты поверх, поэтому здесь можно не обрабатывать,
        # но на всякий случай можно добавить жесты: swipe влево/вправо, тап для вращения.
        # Пропустим, управление через кнопки.
        pass


class TetrisApp(App):
    def build(self):
        # Основной вертикальный лейаут: игра + панель управления
        self.root_layout = BoxLayout(orientation='vertical')

        # Верхняя часть: счёт
        top_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1))
        self.score_label = Label(text='Score: 0', font_size='20sp', size_hint=(1, 1))
        top_layout.add_widget(self.score_label)

        # Кнопка паузы/рестарта
        self.pause_btn = Button(text='Pause', size_hint=(0.2, 1))
        self.pause_btn.bind(on_press=self.toggle_pause)
        top_layout.add_widget(self.pause_btn)

        self.root_layout.add_widget(top_layout)

        # Игровое поле
        self.game = TetrisGame()
        self.game.size_hint = (1, 0.7)
        self.root_layout.add_widget(self.game)

        # Нижняя панель с кнопками управления
        bottom_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.2), spacing=10, padding=10)

        btn_left = Button(text='←', font_size='24sp')
        btn_left.bind(on_press=lambda x: self.game.move_left())
        bottom_layout.add_widget(btn_left)

        btn_rotate = Button(text='↻', font_size='24sp')
        btn_rotate.bind(on_press=lambda x: self.game.rotate())
        bottom_layout.add_widget(btn_rotate)

        btn_drop = Button(text='▼', font_size='24sp')
        btn_drop.bind(on_press=lambda x: self.game.drop())
        bottom_layout.add_widget(btn_drop)

        btn_right = Button(text='→', font_size='24sp')
        btn_right.bind(on_press=lambda x: self.game.move_right())
        bottom_layout.add_widget(btn_right)

        self.root_layout.add_widget(bottom_layout)

        # Слой Game Over (изначально скрыт)
        self.game_over_layout = BoxLayout(orientation='vertical', size_hint=(0.6, 0.3),
                                          pos_hint={'center_x': 0.5, 'center_y': 0.5})
        self.game_over_layout.opacity = 0  # скрыт
        self.game_over_label = Label(text='Game Over', font_size='30sp', color=(1,0,0,1))
        self.game_over_layout.add_widget(self.game_over_label)
        restart_btn = Button(text='Restart', size_hint=(1, 0.4))
        restart_btn.bind(on_press=lambda x: self.game.restart())
        self.game_over_layout.add_widget(restart_btn)
        self.root_layout.add_widget(self.game_over_layout)

        return self.root_layout

    def update_score(self, score):
        self.score_label.text = f'Score: {score}'

    def show_game_over(self):
        self.game_over_layout.opacity = 1

    def hide_game_over(self):
        self.game_over_layout.opacity = 0

    def toggle_pause(self, instance):
        self.game.paused = not self.game.paused
        self.pause_btn.text = 'Resume' if self.game.paused else 'Pause'


if __name__ == '__main__':
    TetrisApp().run()