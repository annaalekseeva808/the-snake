import random

import pygame

# --- КОНСТАНТЫ ---
GRID_SIZE = 20
FIELD_SIZE = (600, 480)
BOARD_BACKGROUND_COLOR = (0, 0, 0)

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 480
GRID_WIDTH = 20
GRID_HEIGHT = 20

UP = (0, -GRID_HEIGHT)
DOWN = (0, GRID_HEIGHT)
LEFT = (-GRID_WIDTH, 0)
RIGHT = (GRID_WIDTH, 0)

# Глобальные переменные (нужны для автотестов)
screen = None
clock = None


class GameObject:
    """Базовый класс для всех игровых объектов."""

    def __init__(self, field_size=(600, 480)):
        # ВАЖНО: добавлены значения по умолчанию
        width, height = field_size
        self.position = (width // 2, height // 2)
        self.body_color = (255, 255, 255)

    def draw(self, screen):
        """Вычисляет случайную позицию."""
        pass


class Apple(GameObject):
    """Класс яблока."""

    def __init__(self, field_size=(600, 480), grid_size=20):
        # Значения по умолчанию
        super().__init__(field_size)
        self.body_color = (255, 0, 0)
        self.randomize_position(grid_size, field_size)

    def randomize_position(self, grid_size, field_size):
        """Вычисляет случайную позицию."""
        width, height = field_size
        max_x = width // grid_size
        max_y = height // grid_size
        x = random.randint(0, max_x - 1) * grid_size
        y = random.randint(0, max_y - 1) * grid_size
        self.position = (x, y)

    def draw(self, screen, grid_size):
        """Отрисовывает яблоко как красный квадрат."""
        # Защита от ошибок: берем первые два элемента позиции и приводим к int
        x = int(self.position[0])
        y = int(self.position[1])

        pygame.draw.rect(
            screen,
            self.body_color,
            (x, y, grid_size, grid_size)
        )


class Snake(GameObject):
    """Класс змейки."""

    def __init__(self, field_size=(600, 480), grid_size=20):
        # Значения по умолчанию
        super().__init__(field_size)
        self.grid_size = grid_size
        self.body_color = (0, 255, 0)
        self.length = 1
        self.positions = [self.position]
        self.direction = (grid_size, 0)
        self.next_direction = None
        self.last = None

    def update_direction(self):
        """Обновляет направление движения."""
        if self.next_direction is not None:
            if (self.direction[0] + self.next_direction[0] != 0
               and self.direction[1] + self.next_direction[1] != 0):
                self.direction = self.next_direction
            self.next_direction = None

    def get_head_position(self):
        """Возвращает координаты головы."""
        return self.positions[0]

    def move(self, field_size, grid_size):
        """Двигает змейку: добавляет новую голову и удаляет хвост."""
        head = self.get_head_position()
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])
        w, h = field_size
        self.positions.insert(0, (new_head[0] % w, new_head[1] % h))

        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def draw(self, screen, grid_size, background_color):
        """Рисует змейку и стирает старый хвост."""
        # Стираем старый хвост, если он есть
        if self.last is not None:
            pygame.draw.rect(
                screen,
                background_color,
                (self.last[0], self.last[1], grid_size, grid_size)
            )

        # Рисуем все сегменты змейки
        for position in self.positions:
            pygame.draw.rect(
                screen,
                self.body_color,
                (position[0], position[1], grid_size, grid_size)
            )

    def reset(self):
        """Сбрасывает состояние змейки к начальному."""
        self.length = 1
        self.positions = [self.position]
        self.direction = (self.grid_size, 0)
        self.next_direction = None
        self.last = None


def handle_keys(snake):
    """Обрабатывает нажатия клавиш и закрытие окна."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                snake.next_direction = (0, -GRID_SIZE)
            elif event.key == pygame.K_DOWN:
                snake.next_direction = (0, GRID_SIZE)
            elif event.key == pygame.K_LEFT:
                snake.next_direction = (-GRID_SIZE, 0)
            elif event.key == pygame.K_RIGHT:
                snake.next_direction = (GRID_SIZE, 0)
    return True


def main():
    """Главная функция игры."""
    global screen, clock

    pygame.init()
    screen = pygame.display.set_mode(FIELD_SIZE)
    pygame.display.set_caption('Изгиб Питона')
    clock = pygame.time.Clock()

    snake = Snake(FIELD_SIZE, GRID_SIZE)
    apple = Apple(FIELD_SIZE, GRID_SIZE)

    running = True
    while running:
        # 1. Обработка событий
        running = handle_keys(snake)

        if not running:
            break

        # 2. Логика игры
        snake.update_direction()
        snake.move(FIELD_SIZE, GRID_SIZE)

        # Проверка: съела ли змейка яблоко?
        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(GRID_SIZE, FIELD_SIZE)

        # Проверка: столкнулась ли змейка сама с собой?
        head = snake.get_head_position()
        if head in snake.positions[1:]:
            # СБРОС ИГРЫ (ИСПРАВЛЕНИЕ ОШИБКИ reset)
            # Вместо создания нового объекта Snake(), мы вызываем метод reset()
            snake.reset()
            apple.randomize_position(GRID_SIZE, FIELD_SIZE)

        # 3. Отрисовка
        screen.fill(BOARD_BACKGROUND_COLOR)
        apple.draw(screen, GRID_SIZE)
        snake.draw(screen, GRID_SIZE, BOARD_BACKGROUND_COLOR)

        pygame.display.flip()
        clock.tick(10)

    pygame.quit()


if __name__ == '__main__': 
    main()
