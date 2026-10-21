from random import randint


import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 20

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


# Тут опишите все классы игры.
class GameObject:
    """Базовый класс для всех игровых объектов."""

    def __init__(self):
        # По умолчанию ставим объект в центр экрана
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.body_color = None  # Цвет зададим в наследниках

    def draw(self, surface):
        """Заглушка для отрисовки. Переопределяется в дочерних классах."""
        pass


class Apple(GameObject):
    """Класс яблока."""

    def __init__(self):
        super().__init__()
        self.body_color = APPLE_COLOR
        self.randomize_position()

    def randomize_position(self):
        """Генерирует случайную позицию на сетке."""
        # randint дает номер клетки от 0 до (кол-во клеток - 1)
        rand_x = randint(0, GRID_WIDTH - 1)
        rand_y = randint(0, GRID_HEIGHT - 1)

        # Переводим номер клетки в пиксели
        self.position = (rand_x * GRID_SIZE, rand_y * GRID_SIZE)

    def draw(self, surface):
        """Отрисовывает яблоко как красный квадрат."""
        rect = (*self.position, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(surface, self.body_color, rect)
        # Рисуем рамку (как в подсказке внизу прекода)
        pygame.draw.rect(surface, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Класс змейки."""

    def draw(self, surface):
        """Отрисовывает змейку и стирает старый след."""
        # 1. Стираем (последний сегмент, который мы потеряли при движении)
        if self.last is not None:
            last_rect = (*self.last, GRID_SIZE, GRID_SIZE)
            # Рисуем поверх старого сегмента цветом фона (черным)
            pygame.draw.rect(surface, BOARD_BACKGROUND_COLOR, last_rect)
            # Рисуем рамку поверх, чтобы гарантированно затереть старую клетку
            pygame.draw.rect(surface, BORDER_COLOR, last_rect, 1)

        # 2. Рисуем все текущие сегменты змейки
        for position in self.positions:
            rect = (*position, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(surface, self.body_color, rect)
            pygame.draw.rect(surface, BORDER_COLOR, rect, 1)

    def update_direction(self):
        """Обновляет направление, если игрок нажал кнопку."""
        if self.next_direction:
            # Проверка: нельзя развернуться на 180 градусов.
            # Если текущее направление (1, 0), то противоположное (-1, 0).
            opposite = (self.direction[0] * -1, self.direction[1] * -1)

            # Если новое направление НЕ противоположно текущему — меняем
            if self.next_direction != opposite:
                self.direction = self.next_direction

            # Сбрасываем next_direction, чтобы не применять его снова
            self.next_direction = None

    def reset(self):
        """Сбрасывает змейку в начальное состояние после столкновения."""
        self.length = 1
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.positions = [self.position]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None

    def __init__(self):
        # 1. Запускаем логику родителя (получаем позицию центра)
        super().__init__()

        # 2. Цвет змейки из твоего прекода
        self.body_color = SNAKE_COLOR

        # 3. Начальные параметры
        self.length = 1
        self.positions = [self.position]  # Тело - список координат

        # 4. Направление: начинаем движение вправо
        self.direction = RIGHT
        self.next_direction = None

        # 5. Атрибут для стирания хвоста (чтобы не оставалось шлейфа)
        self.last = None

    def get_head_position(self):
        """Возвращает координаты головы (первый элемент списка)."""
        return self.positions[0]

    def move(self):
        """Логика движения: находим новую голову, добавляем, удаляем хвост."""
        current_head = self.get_head_position()

        # Вычисляем новую позицию головы.
        # self.direction - это кортеж (dx, dy), например (1, 0).
        # Умножаем на GRID_SIZE, чтобы перейти от клеток к пикселям.
        new_head = (
            current_head[0] + self.direction[0] * GRID_SIZE,
            current_head[1] + self.direction[1] * GRID_SIZE
        )

        # Проход сквозь стены (телепортация)
        new_head = (
            new_head[0] % SCREEN_WIDTH,
            new_head[1] % SCREEN_HEIGHT
        )

        # Сохраняем последний сегмент (хвост) в атрибут last.
        # Это нужно, чтобы потом стереть его с экрана цветом фона.
        if self.positions:
            self.last = self.positions[-1]
        else:
            self.last = None

        # Добавляем новую голову в НАЧАЛО списка позиций
        self.positions.insert(0, new_head)

        # Удаляем хвост, если длина змейки не увеличилась
        # Если змейка съела яблоко, length стал больше, и хвост НЕ удаляется
        if len(self.positions) > self.length:
            self.positions.pop()


def handle_keys(snake):
    """Обрабатывает нажатия клавиш и задает next_direction для змейки."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                snake.next_direction = UP
            elif event.key == pygame.K_DOWN:
                snake.next_direction = DOWN
            elif event.key == pygame.K_LEFT:
                snake.next_direction = LEFT
            elif event.key == pygame.K_RIGHT:
                snake.next_direction = RIGHT


def main():
    """Основной игровой цикл."""
    # 1. Создаем объекты
    snake = Snake()
    apple = Apple()

    # 2. Запускаем бесконечный цикл игры
    while True:
        # --- Обработка событий ---
        handle_keys(snake)

        # Обновляем направление (проверяем, можно ли повернуть)
        snake.update_direction()

        # --- Логика игры ---
        # Двигаем змейку
        snake.move()

        # Проверка: съела ли змейка яблоко?
        # Сравниваем координаты головы змейки и яблока
        if snake.get_head_position() == apple.position:
            snake.length += 1            # Змейка становится длиннее
            apple.randomize_position()   # Яблоко появляется в новом месте

        # Проверка: врезалась ли змейка в себя?
        # Голова не должна совпадать ни с одним другим сегментом тела
        if snake.get_head_position() in snake.positions[1:]:
            snake.reset()  # Сброс игры (змейка возвращается в центр)
            apple.randomize_position()  # Яблоко перелетает в случайное место

        # --- Отрисовка ---
        # Очищаем экран черным цветом перед новой картинкой
        screen.fill(BOARD_BACKGROUND_COLOR)

        # Рисуем объекты
        apple.draw(screen)
        snake.draw(screen)

        # Обновляем экран (показываем всё, что нарисовали за этот кадр)
        pygame.display.flip()

        # Ограничиваем скорость игры (не чаще SPEED кадров в секунду)
        clock.tick(SPEED)


if __name__ == '__main__':
    main()
