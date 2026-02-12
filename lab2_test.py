import unittest
from lab2 import RomanNumeralChecker


class TestRomanNumeralChecker(unittest.TestCase):
    """Тесты для RomanNumeralChecker"""

    def setUp(self):
        self.checker = RomanNumeralChecker()

    def test1_basic_numerals(self):
        """Базовые римские числа"""
        text = "I II III IV V VI VII VIII IX X"
        results = self.checker.find_roman_numerals(text)
        self.assertEqual(len(results), 10)
        # Проверяем некоторые значения
        self.assertEqual(results[0], ("I", 1))
        self.assertEqual(results[3], ("IV", 4))
        self.assertEqual(results[4], ("V", 5))
        self.assertEqual(results[8], ("IX", 9))
        self.assertEqual(results[9], ("X", 10))

    def test2_complex_numerals(self):
        """Сложные римские числа"""
        text = "XLVIII MMXXIV MCMXCIV"
        results = self.checker.find_roman_numerals(text)
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0], ("XLVIII", 48))
        self.assertEqual(results[1], ("MMXXIV", 2024))
        self.assertEqual(results[2], ("MCMXCIV", 1994))

    def test3_invalid_numerals(self):
        """Некорректные римские числа"""
        text = "IIII VV LL DD IC XM VX VL"
        results = self.checker.find_roman_numerals(text)
        # Должны найти только корректные
        self.assertEqual(len(results), 0)

    def test4_empty_cases(self):
        """Пустые случаи"""
        self.assertEqual(self.checker.find_roman_numerals(""), [])
        self.assertEqual(self.checker.find_roman_numerals("Просто текст"), [])

    def test5_validation(self):
        """Валидация чисел"""
        # Корректные
        self.assertTrue(self.checker._is_valid_roman("I"))
        self.assertTrue(self.checker._is_valid_roman("IV"))
        self.assertTrue(self.checker._is_valid_roman("MCMXCIV"))

        # Некорректные
        self.assertFalse(self.checker._is_valid_roman("IIII"))
        self.assertFalse(self.checker._is_valid_roman("VV"))
        self.assertFalse(self.checker._is_valid_roman("IC"))
        self.assertFalse(self.checker._is_valid_roman("XM"))

    def test6_conversion(self):
        """Конвертация римских чисел"""
        self.assertEqual(self.checker._roman_to_int("I"), 1)
        self.assertEqual(self.checker._roman_to_int("IV"), 4)
        self.assertEqual(self.checker._roman_to_int("IX"), 9)
        self.assertEqual(self.checker._roman_to_int("XL"), 40)
        self.assertEqual(self.checker._roman_to_int("XC"), 90)
        self.assertEqual(self.checker._roman_to_int("CD"), 400)
        self.assertEqual(self.checker._roman_to_int("CM"), 900)
        self.assertEqual(self.checker._roman_to_int("MCMXCIV"), 1994)
        self.assertEqual(self.checker._roman_to_int("MMXXIV"), 2024)

    def test7_mixed_text(self):
        """Текст с римскими числами и другими словами"""
        text = "Глава II, Раздел IV, Статья XIX века"
        results = self.checker.find_roman_numerals(text)
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0], ("II", 2))
        self.assertEqual(results[1], ("IV", 4))
        self.assertEqual(results[2], ("XIX", 19))


if __name__ == '__main__':
    unittest.main()