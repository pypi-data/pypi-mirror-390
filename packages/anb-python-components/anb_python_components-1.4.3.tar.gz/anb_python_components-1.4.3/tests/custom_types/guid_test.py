# tests/custom_types/guid_test.py

import unittest
from unittest.mock import patch

from anb_python_components import WrongTypeException
from anb_python_components.custom_types.guid import GUID

class GUIDTest(unittest.TestCase):
    """
    Тесты для класса GUID.
    """
    
    def test_empty_guid_constant (self):
        """
        Проверка константы EMPTY.
        """
        self.assertEqual(GUID.EMPTY, "00000000-0000-0000-0000-000000000000")
    
    def test_init_with_valid_string (self):
        """
        Инициализация с валидной строкой GUID.
        """
        guid = GUID("123e4567-e89b-12d3-a456-426614174000")
        self.assertEqual(str(guid), "123e4567-e89b-12d3-a456-426614174000")
    
    def test_init_with_empty_string (self):
        """
        Инициализация с пустой строкой (должна использовать EMPTY).
        """
        guid = GUID()
        self.assertEqual(str(guid), GUID.EMPTY)
    
    def test_init_with_guid_instance (self):
        """
        Инициализация с экземпляром GUID.
        """
        original = GUID("123e4567-e89b-12d3-a456-426614174000")
        copy = GUID(original)
        self.assertEqual(str(copy), str(original))
    
    def test_init_with_invalid_type (self):
        """
        Инициализация с неверным типом должна вызывать исключение.
        """
        with self.assertRaises(WrongTypeException) as context:
            # noinspection PyTypeChecker
            GUID(123)
        self.assertIn("Неверный тип аргумента!", str(context.exception))
    
    def test_init_with_invalid_guid_format (self):
        """
        Инициализация с невалидным форматом GUID должна вызывать исключение.
        """
        with self.assertRaises(WrongTypeException) as context:
            GUID("invalid-guid-format")
        self.assertIn("Неверный формат GUID!", str(context.exception))
    
    def test_str_method (self):
        """
        Метод __str__ должен возвращать текстовое представление GUID.
        """
        guid = GUID("123e4567-e89b-12d3-a456-426614174000")
        self.assertEqual(str(guid), "123e4567-e89b-12d3-a456-426614174000")
    
    def test_eq_method_equal_guids (self):
        """
        Сравнение двух одинаковых GUID должно возвращать True.
        """
        guid1 = GUID("123e4567-e89b-12d3-a456-426614174000")
        guid2 = GUID("123e4567-e89b-12d3-a456-426614174000")
        self.assertTrue(guid1 == guid2)
    
    def test_eq_method_different_guids (self):
        """
        Сравнение разных GUID должно возвращать False.
        """
        guid1 = GUID("123e4567-e89b-12d3-a456-426614174000")
        guid2 = GUID("00000000-0000-0000-0000-000000000000")
        self.assertFalse(guid1 == guid2)
    
    def test_eq_method_with_non_guid (self):
        """
        Сравнение с не-GUID должно вызывать исключение.
        """
        guid = GUID("123e4567-e89b-12d3-a456-426614174000")
        with self.assertRaises(WrongTypeException) as context:
            # noinspection PyStatementEffect
            guid == "not-a-guid"
        self.assertIn("Неверный тип аргумента!", str(context.exception))
    
    def test_generate_method (self):
        """
        Тест генерации GUID.
        """
        guid = GUID.generate()
        self.assertTrue(GUID.validate(guid))
    
    def test_is_equal_valid_guids (self):
        """
        is_equal должен возвращать True для одинаковых GUID.
        """
        result = GUID.is_equal("fc0ec9bd-7481-2944-a333-55640c4505be", "fc0ec9bd-7481-2944-a333-55640c4505be")
        self.assertTrue(result)
    
    def test_is_equal_different_guids (self):
        """
        is_equal должен возвращать False для разных GUID.
        """
        result = GUID.is_equal("fc0ec9bd-7481-2944-a333-55640c4505be", GUID.EMPTY)
        self.assertFalse(result)
    
    def test_is_equal_with_non_string_or_guid (self):
        """
        is_equal с неверным типом аргумента должен вызывать исключение.
        """
        with self.assertRaises(WrongTypeException) as context:
            # noinspection PyTypeChecker
            GUID.is_equal(123, "123e4567-e89b-12d3-a456-426614174000")
        self.assertIn("Неверный тип аргумента!", str(context.exception))
    
    def test_validate_valid_guid (self):
        """
        validate должен возвращать True для валидного GUID.
        """
        result = GUID.validate("123e4567-e89b-12d3-a456-426614174000")
        self.assertTrue(result)
    
    def test_validate_invalid_guid (self):
        """
        validate должен возвращать False для невалидного GUID.
        """
        result = GUID.validate("invalid-guid")
        self.assertFalse(result)
    
    def test_validate_guid_instance (self):
        """
        validate должен корректно обрабатывать экземпляр GUID.
        """
        guid = GUID("123e4567-e89b-12d3-a456-426614174000")
        result = GUID.validate(guid)
        self.assertTrue(result)
    
    def test_is_invalid_or_empty_valid_non_empty (self):
        """
        is_invalid_or_empty должен возвращать False для валидного непустого GUID.
        """
        result = GUID.is_invalid_or_empty("123e4567-e89b-12d3-a456-426614174000")
        self.assertFalse(result)
    
    def test_is_invalid_or_empty_invalid_guid (self):
        """
        is_invalid_or_empty должен возвращать True для невалидного GUID.
        """
        result = GUID.is_invalid_or_empty("invalid-guid")
        self.assertTrue(result)
    
    def test_is_invalid_or_empty_empty_guid (self):
        """
        is_invalid_or_empty должен возвращать True для пустого GUID.
        """
        result = GUID.is_invalid_or_empty(GUID.EMPTY)
        self.assertTrue(result)
    
    def test_parse_valid_guid (self):
        """
        parse должен возвращать экземпляр GUID для валидной строки.
        """
        guid = GUID.parse("123e4567-e89b-12d3-a456-426614174000")
        self.assertEqual(str(guid), "123e4567-e89b-12d3-a456-426614174000")
    
    def test_parse_invalid_guid_empty_if_not_valid (self):
        """
        parse с invalid guid и empty_if_not_valid=True должен возвращать пустой GUID.
        """
        guid = GUID.parse("invalid-guid", empty_if_not_valid = True)
        self.assertEqual(str(guid), GUID.EMPTY)
    
    def test_parse_invalid_guid_raise_exception (self):
        """
        parse с invalid guid и empty_if_not_valid=False должен вызывать исключение.
        """
        with self.assertRaises(WrongTypeException) as context:
            GUID.parse("invalid-guid", empty_if_not_valid = False)
        self.assertIn("Предан неверный GUID / Wrong GUID.", str(context.exception))
    
    def test_parse_empty_string (self):
        """
        parse с пустой строкой должен возвращать пустой GUID при empty_if_not_valid=True.
        """
        guid = GUID.parse("", empty_if_not_valid = True)
        self.assertEqual(str(guid), GUID.EMPTY)
    
    def test_validate_with_guid_instance (self):
        """
        validate должен корректно обрабатывать экземпляр GUID.
        """
        guid = GUID("123e4567-e89b-12d3-a456-426614174000")
        result = GUID.validate(guid)
        self.assertTrue(result)
    
    def test_is_equal_mixed_types (self):
        """
        is_equal должен корректно сравнивать строку и экземпляр GUID.
        """
        result = GUID.is_equal(
                "123e4567-e89b-12d3-a456-426614174000",
                GUID("123e4567-e89b-12d3-a456-426614174000")
                )
        self.assertTrue(result)
    
    def test_init_case_insensitive (self):
        """
        Инициализация должна корректно обрабатывать GUID в разных регистрах.
        """
        guid1 = GUID("123E4567-E89B-12D3-A456-426614174000")
        guid2 = GUID("123e4567-e89b-12d3-a456-426614174000")
        self.assertEqual(str(guid1).lower(), str(guid2).lower())
    
    def test_str_returns_empty_on_none_value (self):
        """
        Метод __str__ должен возвращать EMPTY, если __value равно None.
        """
        # Создаем экземпляр с пустым значением (искусственно для теста)
        guid = GUID()
        guid._GUID__value = None  # Прямой доступ к приватному атрибуту для теста
        self.assertEqual(str(guid), GUID.EMPTY)
    
    def test_eq_with_non_guid_type_raises_exception (self):
        """
        Сравнение с не-GUID объектом должно вызывать исключение.
        """
        guid = GUID("123e4567-e89b-12d3-a456-426614174000")
        with self.assertRaises(WrongTypeException):
            # noinspection PyStatementEffect
            guid == 123
    
    @patch('secrets.randbits')
    def test_generate_creates_unique_guids (self, mock_randbits):
        """
        generate должен создавать уникальные GUID при разных вызовах.
        """
        # Настраиваем mock для возврата разных значений при каждом вызове
        mock_randbits.side_effect = [
                0x11111111, 0x2222, 0x3333, 0x4444, 0x555555555555,
                0x66666666, 0x7777, 0x8888, 0x9999, 0xAAAAAAAAAAAA
                ]
        
        guid1 = GUID.generate()
        guid2 = GUID.generate()
        
        self.assertNotEqual(str(guid1), str(guid2))
    
    def test_is_invalid_or_empty_none_input (self):
        """
        is_invalid_or_empty должен корректно обрабатывать None.
        """
        # noinspection PyTypeChecker
        result = GUID.is_invalid_or_empty(None)
        self.assertTrue(result)
    
    def test_parse_none_input_with_empty_option (self):
        """
        parse должен обрабатывать None как пустую строку при empty_if_not_valid=True.
        """
        # noinspection PyTypeChecker
        guid = GUID.parse(None, empty_if_not_valid = True)
        self.assertEqual(str(guid), GUID.EMPTY)

if __name__ == '__main__':
    unittest.main()