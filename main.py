import pygame
import sys
import random
from datetime import datetime

# Инициализация PyGame
pygame.init()

# Начальные размеры окна
INIT_WIDTH, INIT_HEIGHT = 1000, 700
FPS = 60
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (255, 50, 50)
BLUE = (50, 100, 255)
GRAY = (150, 150, 150)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (50, 50, 50)

# Тексты для тренировки
TEXTS = [
    "Hello world! This is a typing trainer. Practice makes perfect.",
    "The quick brown fox jumps over the lazy dog. This sentence contains all letters of alphabet.",
    "Programming is the process of creating a set of instructions that tell a computer how to perform a task.",
    "Python is an interpreted, high-level, general-purpose programming language.",
    "To be or not to be, that is the question. Whether 'tis nobler in the mind to suffer.",
    "Success is not final, failure is not fatal: it is the courage to continue that counts.",
    "The only way to do great work is to love what you do. If you haven't found it yet, keep looking.",
    "The journey of a thousand miles begins with a single step. Always remember that persistence is key.",
    "Artificial intelligence is the simulation of human intelligence processes by machines, especially computer systems.",
    "Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed."
]


class TypingTrainer:
    def __init__(self):
        # Создаем окно с поддержкой изменения размера
        self.screen = pygame.display.set_mode((INIT_WIDTH, INIT_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Клавиатурный тренажер")
        self.clock = pygame.time.Clock()

        # Текущие размеры окна
        self.window_width = INIT_WIDTH
        self.window_height = INIT_HEIGHT

        # Параметры для прокрутки текста
        self.text_offset_y = 0
        self.max_offset = 0
        self.line_height = 35
        self.char_width = 18

        # Шрифты (будут пересоздаваться при изменении размера)
        self.title_font = None
        self.button_font = None
        self.text_font = None
        self.stats_font = None
        self.small_font = None

        # Инициализируем шрифты
        self.update_fonts()

        # Статистика
        self.stats = {
            'completed_texts': 0,
            'total_errors': 0,
            'total_chars': 0,
            'last_time': 0
        }

        # Состояния игры
        self.state = "main_menu"
        self.current_text = ""
        self.user_input = ""
        self.errors = 0
        self.start_time = 0
        self.end_time = 0
        self.current_char_index = 0

        # Добавляем переменные для хранения результатов
        self.final_time = 0
        self.final_chars = 0

        # Для правильного расчета позиций символов
        self.text_lines = []  # Разбитый на строки исходный текст
        self.text_line_lengths = []  # Длина каждой строки в символах

        # Кнопки (будут обновляться при изменении размера)
        self.start_button = None
        self.retry_button = None
        self.menu_button = None

        # Обновляем позиции кнопок
        self.update_ui_elements()

        # Загрузка статистики
        self.load_stats()

    def update_fonts(self):
        """Обновление шрифтов при изменении размера окна"""
        scale_factor = min(self.window_width / INIT_WIDTH, self.window_height / INIT_HEIGHT)

        # Динамическое изменение размеров шрифтов
        self.title_font = pygame.font.SysFont('arial', int(48 * scale_factor), bold=True)
        self.button_font = pygame.font.SysFont('arial', int(32 * scale_factor))
        self.text_font = pygame.font.SysFont('courier', int(28 * scale_factor))
        self.stats_font = pygame.font.SysFont('arial', int(24 * scale_factor))
        self.small_font = pygame.font.SysFont('arial', int(20 * scale_factor))

        # Обновляем размеры символов для правильного позиционирования
        self.line_height = int(35 * scale_factor)
        self.char_width = int(18 * scale_factor)

    def update_ui_elements(self):
        """Обновление позиций UI элементов при изменении размера окна"""
        # Кнопки
        self.start_button = pygame.Rect(
            self.window_width // 2 - 100 * (self.window_width / INIT_WIDTH),
            self.window_height // 2 + 50 * (self.window_height / INIT_HEIGHT),
            200 * (self.window_width / INIT_WIDTH),
            60 * (self.window_height / INIT_HEIGHT)
        )

        self.retry_button = pygame.Rect(
            self.window_width // 2 - 150 * (self.window_width / INIT_WIDTH),
            self.window_height // 2 + 100 * (self.window_height / INIT_HEIGHT),
            140 * (self.window_width / INIT_WIDTH),
            50 * (self.window_height / INIT_HEIGHT)
        )

        self.menu_button = pygame.Rect(
            self.window_width // 2 + 10 * (self.window_width / INIT_WIDTH),
            self.window_height // 2 + 100 * (self.window_height / INIT_HEIGHT),
            140 * (self.window_width / INIT_WIDTH),
            50 * (self.window_height / INIT_HEIGHT)
        )

        # Сбрасываем смещение текста при изменении размера
        self.text_offset_y = 0

    def load_stats(self):
        """Загрузка статистики из файла"""
        try:
            with open("typing_stats.txt", "r") as f:
                lines = f.readlines()
                if len(lines) >= 3:
                    self.stats['completed_texts'] = int(lines[0].strip())
                    self.stats['total_errors'] = int(lines[1].strip())
                    self.stats['total_chars'] = int(lines[2].strip())
        except FileNotFoundError:
            pass

    def save_stats(self):
        """Сохранение статистики в файл"""
        with open("typing_stats.txt", "w") as f:
            f.write(f"{self.stats['completed_texts']}\n")
            f.write(f"{self.stats['total_errors']}\n")
            f.write(f"{self.stats['total_chars']}\n")

    def get_new_text(self):
        """Выбор случайного текста для тренировки"""
        return random.choice(TEXTS)

    def start_typing(self):
        """Начало новой тренировки"""
        self.state = "typing"
        self.current_text = self.get_new_text()
        self.user_input = ""
        self.errors = 0
        self.start_time = pygame.time.get_ticks()
        self.end_time = 0
        self.current_char_index = 0
        self.text_offset_y = 0
        # Сбрасываем финальные результаты
        self.final_time = 0
        self.final_chars = 0
        # Сбрасываем разбивку текста
        self.text_lines = []
        self.text_line_lengths = []

    def calculate_stats(self):
        """Расчет статистики после завершения текста"""
        if self.end_time == 0:
            # Если текст еще не завершен, используем текущее время
            current_time = pygame.time.get_ticks()
        else:
            # Если текст завершен, используем зафиксированное время окончания
            current_time = self.end_time

        elapsed_time = (current_time - self.start_time) / 1000  # в секундах
        chars_typed = len(self.user_input)

        # Обновление общей статистики
        self.stats['completed_texts'] += 1
        self.stats['total_errors'] += self.errors
        self.stats['total_chars'] += chars_typed
        self.stats['last_time'] = elapsed_time

        # Сохранение в файл
        self.save_stats()

        return elapsed_time, chars_typed

    def draw_main_menu(self):
        """Отрисовка главного меню"""
        self.screen.fill(BLACK)

        # Заголовок
        title = self.title_font.render("Клавиатурный тренажер", True, BLUE)
        title_rect = title.get_rect(center=(self.window_width // 2, self.window_height // 4))
        self.screen.blit(title, title_rect)

        # Статистика
        stats_y = self.window_height // 3
        stats_texts = [
            f"Пройдено текстов: {self.stats['completed_texts']}",
            f"Всего символов: {self.stats['total_chars']}",
            f"Процент ошибок: {self.get_error_percentage():.1f}%"
        ]

        for i, text in enumerate(stats_texts):
            stat = self.stats_font.render(text, True, WHITE)
            stat_rect = stat.get_rect(center=(self.window_width // 2, stats_y + i * 40))
            self.screen.blit(stat, stat_rect)

        # Кнопка "Начать"
        pygame.draw.rect(self.screen, GREEN, self.start_button, border_radius=15)
        pygame.draw.rect(self.screen, WHITE, self.start_button, 3, border_radius=15)

        start_text = self.button_font.render("Начать", True, WHITE)
        start_rect = start_text.get_rect(center=self.start_button.center)
        self.screen.blit(start_text, start_rect)

        # Подсказки
        hint1 = self.small_font.render("Нажмите 'Начать' для начала тренировки", True, GRAY)
        hint2 = self.small_font.render("ESC - вернуться в меню", True, GRAY)

        self.screen.blit(hint1, (self.window_width // 2 - hint1.get_width() // 2, self.window_height - 100))
        self.screen.blit(hint2, (self.window_width // 2 - hint2.get_width() // 2, self.window_height - 70))

    def get_error_percentage(self):
        """Расчет процента ошибок"""
        if self.stats['total_chars'] == 0:
            return 0.0
        return (self.stats['total_errors'] / self.stats['total_chars']) * 100

    def wrap_text_preserve(self, text, max_chars_per_line):
        """Разбивает текст на строки, сохраняя структуру оригинального текста"""
        if not text:
            return [], []

        lines = []
        line_lengths = []
        current_line = ""
        current_length = 0

        words = text.split(' ')

        for i, word in enumerate(words):
            # Добавляем пробел перед словом, если это не первое слово в строке
            if current_length > 0:
                word_with_space = " " + word
            else:
                word_with_space = word

            word_length = len(word_with_space)

            # Если слово помещается в текущую строку
            if current_length + word_length <= max_chars_per_line:
                current_line += word_with_space
                current_length += word_length
            else:
                # Сохраняем текущую строку
                if current_line:
                    lines.append(current_line)
                    line_lengths.append(len(current_line))

                # Начинаем новую строку
                # Если слово само по себе длиннее максимальной строки, разбиваем его
                if len(word) > max_chars_per_line:
                    # Разбиваем длинное слово
                    for j in range(0, len(word), max_chars_per_line):
                        part = word[j:j + max_chars_per_line]
                        lines.append(part)
                        line_lengths.append(len(part))
                    current_line = ""
                    current_length = 0
                else:
                    current_line = word
                    current_length = len(word)

            # Добавляем последнюю строку
            if i == len(words) - 1 and current_line:
                lines.append(current_line)
                line_lengths.append(len(current_line))

        return lines, line_lengths

    def get_char_position(self, char_index):
        """Получает позицию символа в разбитом тексте (строка, позиция в строке)"""
        if not self.text_line_lengths:
            return 0, 0

        remaining_chars = char_index
        for line_idx, line_len in enumerate(self.text_line_lengths):
            if remaining_chars < line_len:
                return line_idx, remaining_chars
            remaining_chars -= line_len

        # Если символ за пределами текста, возвращаем последнюю позицию
        return len(self.text_lines) - 1, self.text_line_lengths[-1]

    def draw_typing_screen(self):
        """Отрисовка экрана с набором текста"""
        self.screen.fill(BLACK)

        # Определяем максимальную ширину строки в символах
        max_chars_per_line = (self.window_width - 100) // self.char_width

        # Разбиваем текст на строки один раз при изменении размера окна или начале тренировки
        if not self.text_lines:
            self.text_lines, self.text_line_lengths = self.wrap_text_preserve(self.current_text, max_chars_per_line)

        # Вычисляем максимальное смещение для прокрутки
        total_text_height = len(self.text_lines) * self.line_height + 200  # +200 для ввода пользователя и отступов
        visible_height = self.window_height - 200  # Высота видимой области (исключая панель статистики)

        self.max_offset = max(0, total_text_height - visible_height)

        # Прокрутка колесиком мыши
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.text_offset_y = max(0, self.text_offset_y - 10)
        if keys[pygame.K_DOWN]:
            self.text_offset_y = min(self.max_offset, self.text_offset_y + 10)

        # Отрисовка текста для набора (со смещением)
        text_y = 150 - self.text_offset_y

        for i, line in enumerate(self.text_lines):
            if text_y + i * self.line_height > -50 and text_y + i * self.line_height < self.window_height:
                rendered_line = self.text_font.render(line, True, GRAY)
                self.screen.blit(rendered_line, (50, text_y + i * self.line_height))

        # Отрисовка ввода пользователя
        # Для правильного отображения ввода, нам нужно разбить его так же, как исходный текст
        input_y = text_y + len(self.text_lines) * self.line_height + 50

        # Создаем строки ввода пользователя, соответствующие разбивке исходного текста
        input_lines = []
        char_pos = 0

        for line_len in self.text_line_lengths:
            if char_pos < len(self.user_input):
                # Берем часть ввода, соответствующую этой строке исходного текста
                input_line = self.user_input[char_pos:char_pos + line_len]
                input_lines.append(input_line)
                char_pos += line_len
            else:
                input_lines.append("")

        # Отрисовываем строки ввода пользователя
        for line_idx, input_line in enumerate(input_lines):
            line_y = input_y + line_idx * self.line_height

            # Пропускаем строки вне видимой области
            if line_y < -50 or line_y > self.window_height:
                continue

            # Отрисовываем каждый символ в строке
            for char_idx, char in enumerate(input_line):
                # Вычисляем глобальный индекс символа в исходном тексте
                global_char_idx = sum(self.text_line_lengths[:line_idx]) + char_idx

                color = GREEN
                if global_char_idx < len(self.current_text):
                    if char == self.current_text[global_char_idx]:
                        color = GREEN
                    else:
                        color = RED

                char_surface = self.text_font.render(char, True, color)
                self.screen.blit(char_surface, (50 + char_idx * self.char_width, line_y))

        # Курсор
        # Получаем позицию текущего символа в разбитом тексте
        cursor_line_idx, cursor_char_idx = self.get_char_position(len(self.user_input))
        cursor_x = 50 + cursor_char_idx * self.char_width
        cursor_y = input_y + cursor_line_idx * self.line_height

        # Проверяем, находится ли курсор в видимой области
        if -50 < cursor_y < self.window_height:
            pygame.draw.line(self.screen, WHITE,
                             (cursor_x, cursor_y),
                             (cursor_x, cursor_y + self.line_height * 0.8), 2)

        # Автопрокрутка к курсору
        cursor_screen_y = cursor_y - self.text_offset_y
        if cursor_screen_y < 100:  # Если курсор близко к верху
            self.text_offset_y = max(0, self.text_offset_y - 20)
        elif cursor_screen_y > self.window_height - 100:  # Если курсор близко к низу
            self.text_offset_y = min(self.max_offset, self.text_offset_y + 20)

        # Прогресс
        progress = 0
        if len(self.current_text) > 0:
            progress = min(100, len(self.user_input) / len(self.current_text) * 100)

        # Полоса прогресса
        progress_width = self.window_width - 100
        pygame.draw.rect(self.screen, GRAY, (50, self.window_height - 100, progress_width, 20), border_radius=10)
        pygame.draw.rect(self.screen, BLUE, (50, self.window_height - 100, progress_width * progress / 100, 20),
                         border_radius=10)

        # Исправляем расчет времени
        if self.end_time > 0:
            elapsed_time = (self.end_time - self.start_time) / 1000
        else:
            elapsed_time = (pygame.time.get_ticks() - self.start_time) / 1000

        timer_text = self.stats_font.render(f"Время: {elapsed_time:.1f} сек", True, WHITE)
        self.screen.blit(timer_text, (50, self.window_height - 70))

        # Ошибки
        errors_text = self.stats_font.render(f"Ошибки: {self.errors}", True, WHITE)
        self.screen.blit(errors_text, (self.window_width - 200, self.window_height - 70))

        # Подсказки
        hint = self.small_font.render("ESC - меню | Enter - перезапуск | Стрелки - прокрутка", True, GRAY)
        self.screen.blit(hint, (self.window_width // 2 - hint.get_width() // 2, self.window_height - 40))

        # Индикатор прокрутки
        if self.max_offset > 0:
            scroll_ratio = self.text_offset_y / self.max_offset
            scrollbar_height = 100
            scrollbar_y = 100 + (self.window_height - 300) * scroll_ratio
            pygame.draw.rect(self.screen, DARK_GRAY, (self.window_width - 20, 100, 10, self.window_height - 200),
                             border_radius=5)
            pygame.draw.rect(self.screen, BLUE, (self.window_width - 20, scrollbar_y, 10, scrollbar_height),
                             border_radius=5)

    def draw_finished_screen(self):
        """Отрисовка экрана завершения"""
        self.screen.fill(BLACK)

        # Заголовок
        title = self.title_font.render("Текст завершен!", True, GREEN)
        title_rect = title.get_rect(center=(self.window_width // 2, self.window_height // 4))
        self.screen.blit(title, title_rect)

        # Статистика - используем сохраненные значения
        stats_y = self.window_height // 3
        stats_data = [
            f"Время: {self.final_time:.1f} сек",  # Это фиксированное значение
            f"Символов: {self.final_chars}",
            f"Ошибки: {self.errors}",
            f"Скорость: {self.final_chars / self.final_time * 60:.0f} зн/мин" if self.final_time > 0 else "Скорость: 0 зн/мин"
        ]

        for i, text in enumerate(stats_data):
            stat = self.stats_font.render(text, True, WHITE)
            stat_rect = stat.get_rect(center=(self.window_width // 2, stats_y + i * 40))
            self.screen.blit(stat, stat_rect)

        # Кнопки
        pygame.draw.rect(self.screen, BLUE, self.retry_button, border_radius=10)
        pygame.draw.rect(self.screen, WHITE, self.retry_button, 2, border_radius=10)

        pygame.draw.rect(self.screen, GREEN, self.menu_button, border_radius=10)
        pygame.draw.rect(self.screen, WHITE, self.menu_button, 2, border_radius=10)

        retry_text = self.button_font.render("Еще раз", True, WHITE)
        menu_text = self.button_font.render("Меню", True, WHITE)

        self.screen.blit(retry_text, retry_text.get_rect(center=self.retry_button.center))
        self.screen.blit(menu_text, menu_text.get_rect(center=self.menu_button.center))

    def wrap_text(self, text, max_chars_per_line):
        """Совместимость со старой функцией"""
        lines, lengths = self.wrap_text_preserve(text, max_chars_per_line)
        return lines

    def handle_events(self):
        """Обработка событий"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.save_stats()
                pygame.quit()
                sys.exit()

            elif event.type == pygame.VIDEORESIZE:
                # Обработка изменения размера окна
                self.window_width = event.w
                self.window_height = event.h
                self.screen = pygame.display.set_mode((self.window_width, self.window_height), pygame.RESIZABLE)
                self.update_fonts()
                self.update_ui_elements()
                # При изменении размера окна пересчитываем разбивку текста
                if self.state == "typing" and self.current_text:
                    max_chars_per_line = (self.window_width - 100) // self.char_width
                    self.text_lines, self.text_line_lengths = self.wrap_text_preserve(self.current_text,
                                                                                      max_chars_per_line)

            elif event.type == pygame.MOUSEWHEEL:
                # Прокрутка колесиком мыши
                if self.state == "typing":
                    self.text_offset_y = max(0, min(self.max_offset, self.text_offset_y - event.y * 20))

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = "main_menu"
                    self.text_offset_y = 0

                elif self.state == "typing":
                    if event.key == pygame.K_RETURN:
                        self.start_typing()
                    elif event.key == pygame.K_BACKSPACE:
                        if self.user_input:
                            self.user_input = self.user_input[:-1]
                            self.current_char_index = max(0, self.current_char_index - 1)
                    else:
                        if event.unicode and event.unicode.isprintable():
                            self.user_input += event.unicode

                            if len(self.user_input) <= len(self.current_text):
                                if event.unicode != self.current_text[len(self.user_input) - 1]:
                                    self.errors += 1

                            self.current_char_index = len(self.user_input)

                            # Проверка завершения текста
                            if len(self.user_input) >= len(self.current_text):
                                # Фиксируем время окончания
                                self.end_time = pygame.time.get_ticks()
                                # Сохраняем результаты один раз
                                self.final_time, self.final_chars = self.calculate_stats()
                                self.state = "finished"
                                self.text_offset_y = 0

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                if self.state == "main_menu":
                    if self.start_button.collidepoint(mouse_pos):
                        self.start_typing()

                elif self.state == "finished":
                    if self.retry_button.collidepoint(mouse_pos):
                        self.start_typing()
                    elif self.menu_button.collidepoint(mouse_pos):
                        self.state = "main_menu"

    def run(self):
        """Главный цикл игры"""
        while True:
            self.handle_events()

            if self.state == "main_menu":
                self.draw_main_menu()
            elif self.state == "typing":
                self.draw_typing_screen()
            elif self.state == "finished":
                # Используем сохраненные результаты
                self.draw_finished_screen()

            pygame.display.flip()
            self.clock.tick(FPS)


# Запуск приложения
if __name__ == "__main__":
    game = TypingTrainer()
    game.run()