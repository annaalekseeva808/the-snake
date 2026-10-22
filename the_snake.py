from random import randint

import pygame 

# Константы для размеров поля и сетки: 
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480 
GRID_SIZE = 20 
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE 
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE 

# Константа для начальной позиции (центр экрана)
START_POSITION = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

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

# Тут описаны все классы игры. 
class GameObject: 
    """Базовый класс для всех игровых объектов.""" 
    def __init__(self): 
        # Используем заранее посчитанную константу
        self.position = START_POSITION 
        self.body_color = None


    def draw(self, surface): 
        """Заглушка для отрисовки. Переопределяется в дочерних классах.""" 

 
class Apple(GameObject): 
    """Класс яблока.""" 
    def __init__(self): 
        super().__init__() 
        self.body_color = APPLE_COLOR 
        self.randomize_position() 

    def randomize_position(self, occupied_positions=None):
        """Генерирует случайную позицию, избегая занятых клеток."""
        attempts = 0
        max_attempts = 100  # Пробуем максимум 100 раз
        
        while attempts < max_attempts:
            rand_x = randint(0, GRID_WIDTH - 1)
            rand_y = randint(0, GRID_HEIGHT - 1)
            new_pos = (rand_x * GRID_SIZE, rand_y * GRID_SIZE)
            
            # ПРОВЕРКА: если клетка занята змейкой — пропускаем её
            if occupied_positions is not None and new_pos in occupied_positions:
                attempts += 1
                continue
            
            # Если клетка свободна — ставим яблоко и выходим
            self.position = new_pos
            return
        
        # РЕЗЕРВНЫЙ ВАРИАНТ: если за 100 попыток не нашли место (поле забито),
        # ставим яблоко в любую клетку, чтобы игра не зависла.
        # Game Over
        self.position = (0, 0) 

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
        
        # 1. Распаковываем координаты головы и направления в понятные переменные
        head_x, head_y = self.get_head_position()
        dir_x, dir_y = self.direction
        
        # 2. Вычисляем новую позицию
        new_head_x = head_x + dir_x * GRID_SIZE
        new_head_y = head_y + dir_y * GRID_SIZE
        
        # 3. Проход сквозь стены (телепортация)
        new_head_x = new_head_x % SCREEN_WIDTH
        new_head_y = new_head_y % SCREEN_HEIGHT
        
        new_head = (new_head_x, new_head_y)
        
        # 4. Запоминаем последний сегмент (хвост), чтобы потом стереть его
        if self.positions:
            self.last = self.positions[-1]
        else:
            self.last = None
        
        # 5. Добавляем новую голову в начало списка
        self.positions.insert(0, new_head)
        
        # 6. Удаляем хвост, если змейка не выросла (не съела яблоко)
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
                # Проверка: съела ли змейка яблоко?
        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(occupied_positions=snake.positions)
        
        # Проверка: врезалась ли змейка в себя? (если не съела яблоко)
        elif snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            apple.randomize_position(occupied_positions=snake.positions)

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
