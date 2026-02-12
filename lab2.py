
import re
import requests
from bs4 import BeautifulSoup


class RomanNumeralChecker:
    def __init__(self):
        # Регулярное выражение для поиска римских чисел
        # Ограничиваем числа от I до MMMCMXCIX (1-3999)
        self.roman_pattern = re.compile(
            r'''
            \b                         # Граница слова
            (                          # Основная группа
                M{0,3}                 # Тысячи: 0-3 символа M
                (?:CM|CD|D?C{0,3})     # Сотни: 900, 400, 0-300, 500-800
                (?:XC|XL|L?X{0,3})     # Десятки: 90, 40, 0-30, 50-80
                (?:IX|IV|V?I{0,3})     # Единицы: 9, 4, 0-3, 5-8
            )
            \b                         # Граница слова
            ''',
            re.VERBOSE | re.IGNORECASE
        )

        # Таблица для конвертации римских чисел в арабские
        self.roman_to_arabic = {
            'I': 1, 'V': 5, 'X': 10, 'L': 50,
            'C': 100, 'D': 500, 'M': 1000
        }

        # Валидные комбинации вычитания
        self.valid_subtractions = {
            'IV', 'IX', 'XL', 'XC', 'CD', 'CM'
        }

    def find_roman_numerals(self, text):
        """Находит все римские числа в тексте"""
        matches = []
        for match in self.roman_pattern.finditer(text.upper()):
            roman_numeral = match.group(1).upper()
            # Проверяем, что найденная строка является корректным римским числом
            if self._is_valid_roman(roman_numeral):
                arabic_value = self._roman_to_int(roman_numeral)
                if arabic_value > 0:  # Игнорируем пустую строку
                    matches.append((roman_numeral, arabic_value))
        return matches

    def _is_valid_roman(self, roman):
        """Проверяет, является ли строка синтаксически корректным римским числом"""
        if not roman:
            return False

        roman = roman.upper()

        # Проверка на недопустимые символы
        if not all(char in self.roman_to_arabic for char in roman):
            return False

        # Проверка правил повторения символов
        # I, X, C, M могут повторяться до 3 раз подряд
        # V, L, D не могут повторяться
        for char in ['V', 'L', 'D']:
            if roman.count(char) > 1:
                # Проверяем, что они не рядом (VV недопустимо, но XV VX - ок)
                if char * 2 in roman:
                    return False

        # Проверка на более чем 3 повторения I, X, C, M подряд
        for char in ['I', 'X', 'C', 'M']:
            if char * 4 in roman:
                return False

        # Проверка правил вычитания
        i = 0
        while i < len(roman):
            if i + 1 < len(roman):
                pair = roman[i:i + 2]
                # Если это комбинация вычитания
                if pair in self.valid_subtractions:
                    # Проверяем, что меньшая цифра стоит перед большей
                    if self.roman_to_arabic[pair[0]] >= self.roman_to_arabic[pair[1]]:
                        return False
                    i += 2
                else:
                    # Проверяем обычный порядок (не должно быть меньшей перед большей, если это не вычитание)
                    if i + 1 < len(roman) and self.roman_to_arabic[roman[i]] < self.roman_to_arabic[roman[i + 1]]:
                        return False
                    i += 1
            else:
                i += 1

        return True

    def _roman_to_int(self, roman):
        """Конвертирует римское число в целое арабское"""
        if not roman:
            return 0

        roman = roman.upper()
        total = 0
        i = 0

        while i < len(roman):
            # Если есть следующая цифра и она больше текущей, то это вычитание
            if (i + 1 < len(roman) and
                    self.roman_to_arabic[roman[i]] < self.roman_to_arabic[roman[i + 1]]):
                total += (self.roman_to_arabic[roman[i + 1]] - self.roman_to_arabic[roman[i]])
                i += 2
            else:
                total += self.roman_to_arabic[roman[i]]
                i += 1

        return total

    def get_roman_from_url(self, url):
        """Загружает текст с веб-страницы и ищет римские числа"""
        print(f"🔄 Загружаю страницу: {url}")
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Удаляем скрипты и стили чтобы получить чистый текст
        for script in soup(["script", "style"]):
            script.decompose()

        # Получаем чистый текст страницы
        page_text = soup.get_text()

        print(f"📄 Размер текста: {len(page_text)} символов")

        return self.find_roman_numerals(page_text)

    def process_file(self, filename):
        """Читает файл и ищет римские числа"""
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                content = file.read()
            return self.find_roman_numerals(content)
        except FileNotFoundError:
            print(f"Файл {filename} не найден")
            return []
        except Exception as e:
            print(f"Ошибка при чтении файла: {e}")
            return []

    def validate_roman_number(self, roman_num):
        """Валидирует одно римское число"""
        roman_num = roman_num.upper().strip()
        if self._is_valid_roman(roman_num):
            arabic = self._roman_to_int(roman_num)
            return f"{roman_num} = {arabic} (корректно)"
        else:
            return f"{roman_num} = Некорректное римское число"


def main():
    checker = RomanNumeralChecker()

    print("=== Проверка и поиск римских чисел ===")
    print("Диапазон: от I до MMMCMXCIX (1-3999)")
    print("Правила римских чисел:")
    print("- I, X, C, M могут повторяться до 3 раз")
    print("- V, L, D не могут повторяться")
    print("- Вычитание возможно только для IV, IX, XL, XC, CD, CM")
    print("\nВыберите режим работы:")
    print("1 - Поиск в тексте")
    print("2 - Загрузить из файла")
    print("3 - Загрузить по URL")
    print("4 - Проверить одно число")

    choice = input("Ваш выбор (1-4): ").strip()

    if choice == '1':
        # Поиск в тексте
        text = input("Введите текст для поиска: ")
        numerals = checker.find_roman_numerals(text)
        if numerals:
            print("Найденные римские числа:")
            for roman, arabic in numerals:
                print(f"- {roman} = {arabic}")
            print(f"\nВсего найдено: {len(numerals)} чисел")
        else:
            print("Римские числа не найдены")

    elif choice == '2':
        # Загрузка из файла
        filename = input("Введите имя файла: ")
        numerals = checker.process_file(filename)
        if numerals:
            print("Найденные римские числа:")
            for roman, arabic in numerals:
                print(f"- {roman} = {arabic}")
            print(f"\nВсего найдено: {len(numerals)} чисел")
        else:
            print("Римские числа не найдены")

    elif choice == '3':
        # Загрузка по URL
        url = input("Введите URL: ")
        numerals = checker.get_roman_from_url(url)
        if numerals:
            print("Найденные римские числа:")
            for roman, arabic in numerals:
                print(f"- {roman} = {arabic}")
            print(f"\nВсего найдено: {len(numerals)} чисел")
        else:
            print("Римские числа не найдены")

    elif choice == '4':
        # Проверка одного числа
        roman_num = input("Введите римское число для проверки: ")
        result = checker.validate_roman_number(roman_num)
        print(f"Результат проверки: {result}")
    else:
        print("Неверный выбор")


if __name__ == "__main__":
    main()