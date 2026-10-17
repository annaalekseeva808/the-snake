import pygame

import random

GRID_SIZE = 20
FIELD_SIZE = (600, 480)
BOARD_BACKGROUND_COLOR = (0, 0, 0)


class GameObject:
    """Базовый класс для всех игровых объектов."""

    def __init__(self, field_size):
        width, height = field_size
        self.position = (width // 2, height // 2)
        self.body_color = (255, 255, 255)

    def draw(self, screen):
        """Базовый метод отрисовки (заглушка)."""
        pass


class Apple(GameObject):
    """Класс яблока."""

    def __init__(self, field_size, grid_size):
        super().__init__(field_size)
        self.body_color = (255, 0, 0)
        self.randomize_position(grid_size, field_size)

    def randomize_position(self, grid_size, field_size):
        """Вычисляет случайные координаты для яблока."""
        width, height = field_size
        max_x_cells = width // grid_size
        max_y_cells = height // grid_size

        random_x_index = random.randint(0, max_x_cells - 1)
        random_y_index = random.randint(0, max_y_cells - 1)

        new_x = random_x_index * grid_size
        new_y = random_y_index * grid_size

        self.position = (new_x, new_y)

    def draw(self, screen, grid_size):
        """Отрисовывает яблоко как красный квадрат."""
        pygame.draw.rect(
            screen,
            self.body_color,
            (self.position[0], self.position[1], grid_size, grid_size)
        )


class Snake(GameObject):
    """Класс змейки. Наследуется от GameObject."""

    def __init__(self, field_size, grid_size):
        """Инициализирует змейку в центре поля."""
        super().__init__(field_size)

        self.body_color = (0, 255, 0)
        self.length = 1
        self.positions = [self.position]

        # Начальное направление: вправо
        self.direction = (grid_size, 0)

        self.next_direction = None
        self.last = None

    def update_direction(self):
        """Применяет новое направление, запрещая разворот на 180 градусов."""
        if self.next_direction is not None:
            # ИСПРАВЛЕНО: условие в скобках, 'and' в начале новой строки
            if (
                self.direction[0] + self.next_direction[0] != 0
                and self.direction[1] + self.next_direction[1] != 0
            ):
                self.direction = self.next_direction

            self.next_direction = None

    def get_head_position(self):
        """Возвращает координаты головы (первый элемент списка)."""
        return self.positions[0]

    def move(self, field_size, grid_size):
        """Обновляет позицию змейки: добавляет голову, удаляет хвост."""
        current_head = self.get_head_position()

        new_head = (
            current_head[0] + self.direction[0],
            current_head[1] + self.direction[1]
        )

        width, height = field_size
        new_head = (
            new_head[0] % width,
            new_head[1] % height
        )

        self.positions.insert(0, new_head)

        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def draw(self, screen, grid_size, background_color):
        """Отрисовывает змейку и стирает старый хвост."""
        if self.last is not None:
            pygame.draw.rect(
                screen,
                background_color,
                (self.last[0], self.last[1], grid_size, grid_size)
            )

        for position in self.positions:
            pygame.draw.rect(
                screen,
                self.body_color,
                (position[0], position[1], grid_size, grid_size)
            )


def handle_events(snake):
    """Обрабатывает события (закрытие окна и нажатия клавиш)."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False  # Возвращаем False, чтобы выйти из цикла игры

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                snake.next_direction = (0, -GRID_SIZE)
            elif event.key == pygame.K_DOWN:
                snake.next_direction = (0, GRID_SIZE)
            elif event.key == pygame.K_LEFT:
                snake.next_direction = (-GRID_SIZE, 0)
            elif event.key == pygame.K_RIGHT:
                snake.next_direction = (GRID_SIZE, 0)

    return True  # Если окно не закрыли, продолжаем игру


def main():
    """Основная функция игры."""
    # --- НАСТРОЙКИ ---
    GRID_SIZE = 20
    FIELD_SIZE = (600, 480)
    BOARD_BACKGROUND_COLOR = (0, 0, 0)

    # --- ЗАПУСК PYGAME ---
    pygame.init()
    screen = pygame.display.set_mode(FIELD_SIZE)
    pygame.display.set_caption('Изгиб Питона')
    clock = pygame.time.Clock()

    # --- СОЗДАНИЕ ОБЪЕКТОВ ---
    snake = Snake(FIELD_SIZE, GRID_SIZE)
    apple = Apple(FIELD_SIZE, GRID_SIZE)

    running = True
    while running:
        # 1. Обработка событий (ВЫНЕСЕНА В ОТДЕЛЬНУЮ ФУНКЦИЮ)
        # Если функция вернет False (нажали крестик), цикл остановится
        running = handle_events(snake)

        # Если игра остановлена (крестик), прерываем цикл сразу
        if not running:
            break

        # 2. Логика игры (движение, столкновения, еда)
        # Применяем направление
        snake.update_direction()

        # Двигаем змейку
        snake.move(FIELD_SIZE, GRID_SIZE)

        # Проверка: съела ли змейка яблоко?
        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(GRID_SIZE, FIELD_SIZE)

        # Проверка: столкнулась ли змейка сама с собой?
        head = snake.get_head_position()
        if head in snake.positions[1:]:
            # Сброс игры
            snake = Snake(FIELD_SIZE, GRID_SIZE)
            apple = Apple(FIELD_SIZE, GRID_SIZE)

        # 3. Отрисовка
        screen.fill(BOARD_BACKGROUND_COLOR)
        apple.draw(screen, GRID_SIZE)
        snake.draw(screen, GRID_SIZE, BOARD_BACKGROUND_COLOR)

        pygame.display.flip()
        clock.tick(10)

    pygame.quit()
